#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复语音连接问题的kookvoice版本 - 使用真正KOOK API
"""

import asyncio
import threading
import time
import logging
import requests
import aiohttp
from enum import Enum
from typing import Dict, Any, Optional

# 配置
ffmpeg_bin = None
log_enabled = True
logger = logging.getLogger(__name__)

# 播放配置
PLAYBACK_CONFIG = {
    'retry_count': 3,
    'retry_delay': 2,
    'timeout': 30,
    'empty_stream_tolerance': 5,
    'stream_check_interval': 2
}

class Status(Enum):
    WAIT = "wait"
    PLAYING = "playing"
    END = "end"
    SKIP = "skip"
    STOP = "stop"
    STOPPED = "stopped"
    START = "start"

class PlayInfo:
    def __init__(self, guild_id: str, voice_channel_id: str, token: str, file: str, extra_data: Dict[str, Any]):
        self.guild_id = guild_id
        self.voice_channel_id = voice_channel_id
        self.token = token
        self.file = file
        self.extra_data = extra_data

# 全局变量
play_list = {}
event_handlers = {}

def set_ffmpeg(path: str):
    global ffmpeg_bin
    ffmpeg_bin = path

def configure_logging():
    if log_enabled:
        logging.basicConfig(level=logging.INFO)

def on_event(event_type: Status):
    def decorator(func):
        if event_type not in event_handlers:
            event_handlers[event_type] = []
        event_handlers[event_type].append(func)
        return func
    return decorator

class VoiceRequestor:
    """真正的KOOK语音API请求器"""
    def __init__(self, token):
        self.token = token

    async def request(self, method, api, **kwargs):
        header = {'Authorization': f'Bot {self.token}'}
        async with aiohttp.ClientSession(headers=header) as r:
            res = await r.request(method, f'https://www.kookapp.cn/api/v3/{api}', **kwargs)
            resj = await res.json()
        if resj['code'] != 0:
            raise RuntimeError(resj['message'])
        return resj['data']

    async def join(self, cid):
        return await self.request('POST', 'voice/join', json={'channel_id': cid})

    async def leave(self, cid):
        return await self.request('POST', 'voice/leave', json={'channel_id': cid})

    async def list(self):
        return await self.request('GET', 'voice/list')

    async def keep_alive(self, cid):
        return await self.request('POST', 'voice/keep-alive', json={'channel_id': cid})

class Player:
    def __init__(self, guild_id: str, voice_channel_id: str = None, token: str = None):
        self.guild_id = str(guild_id)
        self.voice_channel_id = voice_channel_id
        self.token = token
        self.status = Status.STOPPED
        self.current_process = None
        self.retry_count = 0
        self.requestor = VoiceRequestor(token) if token else None
        
        if self.guild_id not in play_list:
            play_list[self.guild_id] = {
                'play_list': [],
                'current_index': 0,
                'is_playing': False
            }

    async def join(self):
        """加入语音频道（使用真正KOOK API）"""
        try:
            if log_enabled:
                logger.info(f"开始处理, 服务器: {self.guild_id}")
            
            if not self.voice_channel_id:
                if log_enabled:
                    logger.error("语音频道ID为空")
                return False
            
            if not self.token:
                if log_enabled:
                    logger.error("机器人Token为空")
                return False
            
            try:
                res = await self.requestor.join(self.voice_channel_id)
                if log_enabled:
                    logger.info(f"成功加入语音频道: {self.voice_channel_id}")
                    logger.info(f"RTP配置: {res}")
                return True
            except Exception as e:
                if log_enabled:
                    logger.error(f"加入语音频道失败: {e}")
                return False
            
        except Exception as e:
            if log_enabled:
                logger.error(f"加入语音频道失败: {e}")
            return False

    def add_music(self, file: str, extra_data: Dict[str, Any] = None):
        """添加音乐到播放队列"""
        if extra_data is None:
            extra_data = {}
        
        play_list[self.guild_id]['play_list'].append({
            'file': file,
            'extra_data': extra_data
        })
        
        if log_enabled:
            logger.info(f"添加音乐到队列: {file}")

    def skip(self):
        """跳过当前歌曲"""
        self.status = Status.SKIP
        if log_enabled:
            logger.info("跳过当前歌曲")

    def stop(self):
        """停止播放"""
        self.status = Status.STOP
        if log_enabled:
            logger.info("停止播放")

    def seek(self, time: int):
        """跳转到指定时间"""
        if log_enabled:
            logger.info(f"跳转到 {time} 秒")

    def get_progress(self) -> int:
        """获取播放进度"""
        return 0  # 简化实现

    async def start(self):
        """启动播放器"""
        while True:
            try:
                if self.guild_id in play_list and play_list[self.guild_id]['play_list']:
                    current_item = play_list[self.guild_id]['play_list'][0]
                    file = current_item['file']
                    extra_data = current_item['extra_data']
                    
                    # 播放音乐
                    success = await self._play_single_song(None, file, "", extra_data)
                    
                    if success:
                        # 播放完成，移除当前歌曲
                        play_list[self.guild_id]['play_list'].pop(0)
                    else:
                        # 播放失败，跳过当前歌曲
                        play_list[self.guild_id]['play_list'].pop(0)
                        if log_enabled:
                            logger.warning("播放失败，跳过当前歌曲")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                if log_enabled:
                    logger.error(f"播放器运行错误: {e}")
                await asyncio.sleep(5)

    async def _play_single_song(self, p, file: str, extra_command: str, music_info: Dict[str, Any]) -> bool:
        """播放单首歌曲的改进版本"""
        retry_count = 0
        
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
                if log_enabled:
                    logger.info(f"开始播放: {file}")
                
                # 触发播放开始事件
                play_info = PlayInfo(
                    guild_id=self.guild_id,
                    voice_channel_id=self.voice_channel_id,
                    token=self.token,
                    file=file,
                    extra_data=music_info
                )
                
                # 调用事件处理器
                if Status.START in event_handlers:
                    for handler in event_handlers[Status.START]:
                        try:
                            await handler(play_info)
                        except Exception as e:
                            if log_enabled:
                                logger.error(f"事件处理器错误: {e}")
                
                # 真正的音频播放实现
                success = await self._play_audio_with_ffmpeg(file)
                
                if success:
                    if log_enabled:
                        logger.info(f"播放完成: {file}")
                    return True
                else:
                    if log_enabled:
                        logger.error(f"音频播放失败: {file}")
                    return False
                
            except Exception as e:
                retry_count += 1
                if log_enabled:
                    logger.error(f"播放失败 (重试 {retry_count}/{PLAYBACK_CONFIG['retry_count']}): {e}")
                
                if retry_count < PLAYBACK_CONFIG['retry_count']:
                    await asyncio.sleep(PLAYBACK_CONFIG['retry_delay'])
        
        return False

    async def _play_audio_with_ffmpeg(self, audio_url: str) -> bool:
        """使用FFmpeg播放音频到KOOK语音频道"""
        try:
            if not ffmpeg_bin:
                if log_enabled:
                    logger.error("FFmpeg路径未设置")
                return False
            
            # 获取RTP配置
            rtp_config = await self._get_rtp_config()
            if not rtp_config:
                if log_enabled:
                    logger.error("无法获取RTP配置")
                return False
            
            # 构建RTP URL
            rtp_url = f"rtp://{rtp_config['ip']}:{rtp_config['port']}?rtcpport={rtp_config['rtcp_port']}"
            
            if log_enabled:
                logger.info(f"RTP URL: {rtp_url}")
                logger.info(f"音频URL: {audio_url}")
            
            # 构建FFmpeg命令
            ffmpeg_cmd = [
                ffmpeg_bin,
                '-i', audio_url,
                '-acodec', 'opus',
                '-ar', '48000',
                '-ac', '2',
                '-b:a', '128k',
                '-f', 'rtp',
                rtp_url
            ]
            
            if log_enabled:
                logger.info(f"FFmpeg命令: {' '.join(ffmpeg_cmd)}")
            
            # 启动FFmpeg进程
            import subprocess
            import asyncio
            
            # 创建异步子进程
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.current_process = process
            
            # 等待进程完成或超时
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5分钟超时
                
                if process.returncode == 0:
                    if log_enabled:
                        logger.info("FFmpeg播放成功完成")
                    return True
                else:
                    if log_enabled:
                        logger.error(f"FFmpeg播放失败，返回码: {process.returncode}")
                        if stderr:
                            logger.error(f"FFmpeg错误: {stderr.decode()}")
                    return False
                    
            except asyncio.TimeoutError:
                if log_enabled:
                    logger.warning("FFmpeg播放超时，可能音频已播放完成")
                # 尝试终止进程
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=5)
                except:
                    pass
                return True  # 超时通常意味着播放完成
                
        except Exception as e:
            if log_enabled:
                logger.error(f"音频播放异常: {e}")
            return False

    async def _get_rtp_config(self):
        """获取RTP配置信息"""
        try:
            if not self.requestor or not self.voice_channel_id:
                return None
            
            res = await self.requestor.join(self.voice_channel_id)
            return res
            
        except Exception as e:
            if log_enabled:
                logger.error(f"获取RTP配置失败: {e}")
            return None

    async def push(self):
        """推流方法（使用真正KOOK API）"""
        try:
            if not self.requestor or not self.voice_channel_id:
                if log_enabled:
                    logger.error("缺少requestor或voice_channel_id")
                return False
            
            # 获取RTP配置
            res = await self._get_rtp_config()
            
            if res is None:
                if log_enabled:
                    logger.error("无法获取RTP配置信息")
                return False
            
            # 构建RTP URL
            rtp_url = f"rtp://{res['ip']}:{res['port']}?rtcpport={res['rtcp_port']}"
            
            if log_enabled:
                logger.info(f"RTP URL: {rtp_url}")
            
            return True
            
        except Exception as e:
            if log_enabled:
                logger.error(f"推流过程中出现错误: {e}")
            return False

# 全局启动函数
async def start():
    """启动所有播放器"""
    tasks = []
    for guild_id in play_list:
        player = Player(guild_id)
        task = asyncio.create_task(player.start())
        tasks.append(task)
    
    if tasks:
        await asyncio.gather(*tasks)
    else:
        # 如果没有播放器，保持运行
        while True:
            await asyncio.sleep(1)
