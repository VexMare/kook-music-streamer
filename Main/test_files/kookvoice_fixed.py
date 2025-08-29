#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOOK音乐播放器 - 修复版本
解决播放中断和自动跳转问题
"""

import asyncio
import threading
import time
import logging
import requests
from enum import Enum
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Status(Enum):
    WAIT = "wait"
    PLAYING = "playing"
    END = "end"
    SKIP = "skip"
    STOP = "stop"
    START = "start"

class PlayInfo:
    def __init__(self, guild_id: str, voice_channel_id: str, file: str, token: str, extra_data: Dict[str, Any] = None):
        self.guild_id = guild_id
        self.voice_channel_id = voice_channel_id
        self.file = file
        self.token = token
        self.extra_data = extra_data or {}

# 全局变量
play_list: Dict[str, Dict[str, Any]] = {}
guild_status: Dict[str, Status] = {}
playlist_handle_status: Dict[str, bool] = {}
events: Dict[Status, list] = {}
original_loop = None
log_enabled = True

# 播放配置
PLAYBACK_CONFIG = {
    'buffer_size': 1024 * 1024,  # 1MB缓冲区
    'retry_count': 3,  # 重试次数
    'retry_delay': 1.0,  # 重试延迟
    'timeout': 30.0,  # 超时时间
    'stream_check_interval': 0.5,  # 流检查间隔
    'empty_stream_tolerance': 3,  # 空流容忍次数
}

def set_ffmpeg(path: str):
    """设置FFmpeg路径"""
    global ffmpeg_bin
    ffmpeg_bin = path

def configure_logging(enable: bool = True):
    """配置日志"""
    global log_enabled
    log_enabled = enable

def on_event(event: Status):
    """事件装饰器"""
    def decorator(func):
        if event not in events:
            events[event] = []
        events[event].append(func)
        return func
    return decorator

async def trigger_event(event: Status, *args, **kwargs):
    """触发事件"""
    if event in events:
        for func in events[event]:
            try:
                await func(*args, **kwargs)
            except Exception as e:
                if log_enabled:
                    logger.error(f"事件处理错误: {e}")

class Player:
    def __init__(self, guild_id: str, voice_channel_id: Optional[str] = None, token: Optional[str] = None):
        self.guild_id = guild_id
        self.voice_channel_id = voice_channel_id
        self.token = token

    def join(self):
        """加入语音频道"""
        if not self.voice_channel_id or not self.token:
            raise ValueError("需要提供voice_channel_id和token")
        
        if self.guild_id in play_list:
            raise ValueError("该服务器已在播放中")
        
        play_list[self.guild_id] = {
            'voice_channel': self.voice_channel_id,
            'play_list': [],
            'now_playing': None
        }
        guild_status[self.guild_id] = Status.WAIT
        
        handler = PlayHandler(self.guild_id, self.token)
        handler.start()
        
        if log_enabled:
            logger.info(f"加入语音频道: {self.voice_channel_id}, 服务器: {self.guild_id}")

    def add_music(self, file: str, extra_data: Dict[str, Any] = None):
        """添加音乐到播放队列"""
        if self.guild_id not in play_list:
            raise ValueError("请先加入语音频道")
        
        music_info = {
            'file': file,
            'ss': 0,
            'extra': extra_data or {}
        }
        play_list[self.guild_id]['play_list'].append(music_info)
        
        if log_enabled:
            logger.info(f"添加音乐: {file}, 服务器: {self.guild_id}")

    def skip(self):
        """跳过当前歌曲"""
        if self.guild_id in guild_status:
            guild_status[self.guild_id] = Status.SKIP
            if log_enabled:
                logger.info(f"跳过歌曲, 服务器: {self.guild_id}")

    def stop(self):
        """停止播放"""
        if self.guild_id in guild_status:
            guild_status[self.guild_id] = Status.STOP
            if log_enabled:
                logger.info(f"停止播放, 服务器: {self.guild_id}")

    def seek(self, seconds: int):
        """跳转到指定时间"""
        if self.guild_id not in play_list:
            raise ValueError("该服务器没有正在播放的歌曲")
        
        now_play = play_list[self.guild_id]['now_playing']
        if now_play:
            now_play['ss'] = int(seconds)
            if 'start' in now_play:
                del now_play['start']
            play_list[self.guild_id]['play_list'].insert(0, now_play)
            guild_status[self.guild_id] = Status.SKIP
            
            if log_enabled:
                logger.info(f"跳转到 {seconds} 秒, 服务器: {self.guild_id}")

    def get_progress(self) -> int:
        """获取播放进度"""
        if self.guild_id not in play_list:
            return 0
        
        now_play = play_list[self.guild_id]['now_playing']
        if not now_play or 'start' not in now_play:
            return 0
        
        return int(time.time() - now_play['start'])

class PlayHandler(threading.Thread):
    def __init__(self, guild_id: str, token: str):
        threading.Thread.__init__(self)
        self.token = token
        self.guild = guild_id
        self.requestor = VoiceRequestor(token)
        self.channel_id = None

    def run(self):
        if log_enabled:
            logger.info(f"开始处理, 服务器: {self.guild}")
        
        loop_t = asyncio.new_event_loop()
        asyncio.set_event_loop(loop_t)
        loop_t.run_until_complete(self.main())
        
        if log_enabled:
            logger.info(f"处理完成, 服务器: {self.guild}")

    async def main(self):
        start_event = asyncio.Event()
        task1 = asyncio.create_task(self.push())
        task2 = asyncio.create_task(self.keepalive())
        task3 = asyncio.create_task(self.stop(start_event))

        done, pending = await asyncio.wait(
            [task1, task2],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        start_event.set()
        await task3

    async def stop(self, start_event):
        await start_event.wait()
        global playlist_handle_status
        
        if self.guild in play_list:
            del play_list[self.guild]
        if self.guild in playlist_handle_status and playlist_handle_status[self.guild]:
            playlist_handle_status[self.guild] = False
        
        try:
            await self.requestor.leave(self.channel_id)
        except:
            pass
        
        if log_enabled:
            logger.info(f"停止并清理, 服务器: {self.guild}")

    async def push(self):
        """改进的音频推送方法"""
        global playlist_handle_status
        playlist_handle_status[self.guild] = True
        
        try:
            await asyncio.sleep(1)
            new_channel = play_list[self.guild]['voice_channel']
            self.channel_id = new_channel

            # 加入语音频道
            try:
                await self.requestor.leave(self.channel_id)
            except:
                pass
            
            try:
                res = await self.requestor.join(self.channel_id)
            except Exception as e:
                if log_enabled:
                    logger.error(f'加入频道失败: {e}')
                raise RuntimeError(f'加入频道失败 {e}')

            rtp_url = f"rtp://{res['ip']}:{res['port']}?rtcpport={res['rtcp_port']}"
            bitrate = int(res['bitrate'] / 1000)
            bitrate *= 0.9 if bitrate > 100 else 1

            # 等待播放状态
            while self.guild in guild_status and guild_status[self.guild] == Status.WAIT:
                await asyncio.sleep(2)

            # 创建FFmpeg进程
            command = f'{ffmpeg_bin} -re -loglevel level+info -nostats -i - -map 0:a:0 -acodec libopus -ab {bitrate}k -ac 2 -ar 48000 -f tee [select=a:f=rtp:ssrc=1111:payload_type=111]{rtp_url}'
            
            if log_enabled:
                logger.info(f'运行 ffmpeg 命令: {command}')
            
            p = await asyncio.create_subprocess_shell(
                command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )

            # 播放循环
            while True:
                await asyncio.sleep(0.5)
                
                # 获取下一首歌曲
                if play_list[self.guild]['now_playing'] and not play_list[self.guild]['play_list']:
                    music_info = play_list[self.guild]['now_playing']
                else:
                    if not play_list[self.guild]['play_list']:
                        break
                    music_info = play_list[self.guild]['play_list'].pop(0)
                    music_info['start'] = time.time()
                    play_list[self.guild]['now_playing'] = music_info
                
                file = music_info['file']

                # 处理额外参数
                extra_command = ''
                if extra_data := music_info.get('extra'):
                    extra_command = extra_data.get('extra_command') or ''

                    def pack_command(full_command, name, value):
                        if value:
                            full_command += f' -{name} "{value}"'
                        return full_command

                    extra_command = pack_command(extra_command, 'headers', extra_data.get('header'))
                    extra_command = pack_command(extra_command, 'cookies', extra_data.get('cookies'))
                    extra_command = pack_command(extra_command, 'user_agent', extra_data.get('user_agent'))
                    extra_command = pack_command(extra_command, 'referer', extra_data.get('referer'))

                # 播放单首歌曲
                success = await self._play_single_song(p, file, extra_command, music_info)
                if not success:
                    if log_enabled:
                        logger.warning(f"播放失败: {file}, 服务器: {self.guild}")
                    continue

                # 检查播放列表状态
                guild_status[self.guild] = Status.END
                if len(play_list[self.guild]['play_list']) == 0:
                    try:
                        p.kill()
                    except:
                        pass
                    del play_list[self.guild]
                    playlist_handle_status[self.guild] = False
                    if log_enabled:
                        logger.info(f'播放结束, 服务器: {self.guild}')
                    break

        except Exception as e:
            if log_enabled:
                logger.error('推流过程中出现错误:', exc_info=True)

    async def _play_single_song(self, p, file: str, extra_command: str, music_info: Dict[str, Any]) -> bool:
        """播放单首歌曲的改进版本"""
        retry_count = 0
        empty_stream_count = 0
        
        # 检查是否是歌单歌曲标记
        if file.startswith("PLAYLIST_SONG:"):
            # 解析歌单歌曲标记
            parts = file.split(":")
            if len(parts) >= 4:
                song_id = parts[1]
                song_name = parts[2]
                artist_name = parts[3]
                
                # 实时获取歌曲URL
                try:
                    # 从config导入API配置
                    from config import music_api_base
                    url_api = f"{music_api_base}/song/url?id={song_id}"
                    url_res = requests.get(url_api, timeout=15)
                    
                    if url_res.status_code == 200:
                        url_data = url_res.json()
                        if url_data['data'][0]['url']:
                            file = url_data['data'][0]['url']
                            if log_enabled:
                                logger.info(f"实时获取到URL: {song_name} - {artist_name}")
                        else:
                            if log_enabled:
                                logger.warning(f"无法获取播放链接: {song_name} - {artist_name}")
                            return False
                    else:
                        if log_enabled:
                            logger.error(f"获取URL失败: {song_name} - {artist_name}")
                        return False
                except Exception as e:
                    if log_enabled:
                        logger.error(f"实时获取URL异常: {e}")
                    return False
        
        while retry_count < PLAYBACK_CONFIG['retry_count']:
            try:
                command2 = f'{ffmpeg_bin} -nostats -i "{file}" {extra_command} -filter:a volume=0.4 -ss {music_info["ss"]} -format pcm_s16le -ac 2 -ar 48000 -f wav -'
                
                if log_enabled:
                    logger.info(f'正在播放文件: {file}')
                
                p2 = await asyncio.create_subprocess_shell(
                    command2,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL
                )

                sleep_control = 1
                every_shard_bytes = 192000 * sleep_control
                sleep_control -= 0.004
                i = 0
                total_audio = b''
                need_break = False
                first_music_start_time = 0
                last_audio_time = time.time()

                while True:
                    start_time = time.time()
                    
                    # 改进的音频流读取
                    try:
                        new_audio = await asyncio.wait_for(p2.stdout.read(), timeout=PLAYBACK_CONFIG['timeout'])
                    except asyncio.TimeoutError:
                        if log_enabled:
                            logger.warning(f"音频流读取超时: {file}")
                        break
                    
                    total_audio = total_audio + new_audio
                    audio_slice = total_audio[i * every_shard_bytes:(i + 1) * every_shard_bytes]
                    
                    if need_break:
                        break
                    
                    # 改进的空流检测
                    if not new_audio:
                        empty_stream_count += 1
                        if empty_stream_count > PLAYBACK_CONFIG['empty_stream_tolerance']:
                            if not audio_slice:
                                break
                            if len(audio_slice) < every_shard_bytes:
                                need_break = True
                        else:
                            await asyncio.sleep(PLAYBACK_CONFIG['stream_check_interval'])
                            continue
                    else:
                        empty_stream_count = 0
                        last_audio_time = time.time()
                    
                    # 检查音频数据是否足够
                    if len(audio_slice) < every_shard_bytes:
                        await asyncio.sleep(0.01)
                        continue
                    
                    # 写入音频数据
                    try:
                        p.stdin.write(audio_slice)
                    except Exception as e:
                        if log_enabled:
                            logger.error(f"写入音频数据失败: {e}")
                        break
                    
                    if first_music_start_time == 0:
                        first_music_start_time = time.time()
                    
                    play_list[self.guild]['now_playing']['ss'] = first_music_start_time - time.time()
                    i += 1
                    flag = 0

                    # 状态检查循环
                    while True:
                        if self.guild not in guild_status:
                            guild_status[self.guild] = Status.END
                        
                        if guild_status[self.guild] != Status.PLAYING:
                            state = guild_status[self.guild]
                            if state == Status.END:
                                asyncio.run_coroutine_threadsafe(trigger_event(Status.START,
                                                                           PlayInfo(self.guild, self.channel_id, file, self.token,
                                                                                    music_info.get('extra'))), original_loop)
                                if log_enabled:
                                    logger.info(f'开始播放: {file}, 服务器: {self.guild}')
                                guild_status[self.guild] = Status.PLAYING
                            elif state == Status.SKIP:
                                flag = 1
                                break
                            elif state == Status.STOP:
                                flag = 1
                                play_list[self.guild]['play_list'] = []
                                break
                        elif time.time() - start_time > sleep_control:
                            break
                        else:
                            await asyncio.sleep(0.001)

                    if flag == 1:
                        break
                
                # 清理进程
                try:
                    p2.kill()
                except:
                    pass
                
                return True  # 播放成功
                
            except Exception as e:
                retry_count += 1
                if log_enabled:
                    logger.error(f"播放重试 {retry_count}/{PLAYBACK_CONFIG['retry_count']}: {e}")
                
                if retry_count < PLAYBACK_CONFIG['retry_count']:
                    await asyncio.sleep(PLAYBACK_CONFIG['retry_delay'])
                else:
                    if log_enabled:
                        logger.error(f"播放失败，已达到最大重试次数: {file}")
                    return False
        
        return False

    async def keepalive(self):
        """保活机制"""
        while True:
            await asyncio.sleep(45)
            try:
                await self.requestor.keep_alive(self.channel_id)
                if log_enabled:
                    logger.info(f'发送保活请求, 频道: {self.channel_id}')
            except Exception as e:
                if log_enabled:
                    logger.error(f'保活请求失败: {e}')

# 简化的VoiceRequestor类（实际使用时需要完整的实现）
class VoiceRequestor:
    def __init__(self, token: str):
        self.token = token
    
    async def join(self, channel_id: str):
        # 这里需要实际的实现
        pass
    
    async def leave(self, channel_id: str):
        # 这里需要实际的实现
        pass
    
    async def keep_alive(self, channel_id: str):
        # 这里需要实际的实现
        pass

async def start():
    """启动播放器"""
    global original_loop
    original_loop = asyncio.get_event_loop()
    while True:
        await asyncio.sleep(1000)

def run():
    """运行播放器"""
    asyncio.run(start())

# 导出主要类和函数
__all__ = ['Player', 'Status', 'PlayInfo', 'on_event', 'set_ffmpeg', 'configure_logging', 'start', 'run']
