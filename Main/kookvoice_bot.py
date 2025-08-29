import asyncio
import kookvoice
from khl import *
from config import ffmpeg_path, bot_token, music_api_base
import requests, re, time
import json

bot = Bot(token=bot_token)

kookvoice.set_ffmpeg(ffmpeg_path)
kookvoice.configure_logging()

# 从配置文件读取API配置
NEW_API_BASE = music_api_base

def validate_api_response(response, api_name):
    """验证API响应是否有效"""
    try:
        # 检查状态码
        if response.status_code != 200:
            return False, f"API {api_name} 返回错误状态码: {response.status_code}"
        
        # 检查响应内容是否为空
        if not response.text.strip():
            return False, f"API {api_name} 返回空响应"
        
        # 尝试解析JSON
        data = response.json()
        return True, data
        
    except json.JSONDecodeError as e:
        return False, f"API {api_name} JSON解析失败: {str(e)}"
    except Exception as e:
        return False, f"API {api_name} 验证失败: {str(e)}"

async def find_user(gid, aid):
    voice_channel_ = await bot.client.gate.request('GET', 'channel-user/get-joined-channel',
                                                   params={'guild_id': gid, 'user_id': aid})
    voice_channel = voice_channel_["items"]
    if voice_channel:
        return voice_channel[0]['id']

@bot.command(name='加入')
async def join_vc(msg: Message):
    voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
    if voice_channel_id is None:
        c = Card()
        c.append(Module.Header('❗ 加入失败'))
        c.append(Module.Context('请先加入语音频道'))
        await msg.ctx.channel.send(CardMessage(c))
        return
    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
    player.join()
    voice_channel = await bot.client.fetch_public_channel(voice_channel_id)
    c = Card()
    c.append(Module.Header('✅ 已加入语音频道'))
    c.append(Module.Context(f'已加入语音频道 #{voice_channel.name}'))
    await msg.ctx.channel.send(CardMessage(c))

@bot.command(name='wy')
async def play(msg: Message, music_input: str):
    voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
    if voice_channel_id is None:
        c = Card()
        c.append(Module.Header('❗ 点歌失败'))
        c.append(Module.Context('请先加入语音频道'))
        await msg.ctx.channel.send(CardMessage(c))
        return
    # 判断是否为直链
    if music_input.startswith("http"):
        music_url = music_input
        song_name = "直链音乐"
    else:
        try:
            # 搜索歌曲 - 使用新API
            search_url = f"{NEW_API_BASE}/cloudsearch?keywords={music_input}"
            print(f"🔍 搜索歌曲: {search_url}")
            
            res = requests.get(search_url, timeout=15)
            is_valid, search_result = validate_api_response(res, "搜索API")
            
            if not is_valid:
                c = Card()
                c.append(Module.Header('❗ 搜索失败'))
                c.append(Module.Context(f'搜索API错误: {search_result}'))
                await msg.ctx.channel.send(CardMessage(c))
                return
            
            songs = search_result.get('result', {}).get('songs', [])
            if not songs:
                c = Card()
                c.append(Module.Header('❗ 点歌失败'))
                c.append(Module.Context('未搜索到歌曲'))
                await msg.ctx.channel.send(CardMessage(c))
                return
            
            song = songs[0]
            song_id = song['id']
            song_name = song.get('name', music_input)
            artist_name = song.get('ar', [{}])[0].get('name', '未知')
            
            print(f"🎵 找到歌曲: {song_name} - {artist_name} (ID: {song_id})")
            
            # 获取歌曲URL - 使用新API
            url_api = f"{NEW_API_BASE}/song/url?id={song_id}"
            print(f"🔗 获取URL: {url_api}")
            
            url_res = requests.get(url_api, timeout=15)
            is_valid, url_result = validate_api_response(url_res, "URL获取API")
            
            if not is_valid:
                c = Card()
                c.append(Module.Header('❗ 获取URL失败'))
                c.append(Module.Context(f'URL获取API错误: {url_result}'))
                await msg.ctx.channel.send(CardMessage(c))
                return
            
            music_url = url_result['data'][0]['url']
            if not music_url:
                c = Card()
                c.append(Module.Header('❗ 点歌失败'))
                c.append(Module.Context('获取直链失败，可能是VIP歌曲'))
                await msg.ctx.channel.send(CardMessage(c))
                return
            
            print(f"✅ 获取到音乐URL: {music_url[:50]}...")
            
        except requests.exceptions.Timeout:
            c = Card()
            c.append(Module.Header('❗ 网络超时'))
            c.append(Module.Context('API请求超时，请稍后重试'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        except requests.exceptions.ConnectionError:
            c = Card()
            c.append(Module.Header('❗ 网络连接失败'))
            c.append(Module.Context('无法连接到音乐API服务器'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        except Exception as e:
            c = Card()
            c.append(Module.Header('❗ 未知错误'))
            c.append(Module.Context(f'发生未知错误: {str(e)}'))
            await msg.ctx.channel.send(CardMessage(c))
            return
    
    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
    extra_data = {"音乐名字": song_name, "点歌人": msg.author_id, "文字频道": msg.ctx.channel.id}
    player.add_music(music_url, extra_data)
    c = Card()
    c.append(Module.Header('✅ 添加音乐成功'))
    c.append(Module.Context(f'{song_name} 已加入播放队列'))
    await msg.ctx.channel.send(CardMessage(c))

@bot.command(name='wygd')
async def playlist_play(msg: Message, playlist_input: str):
    def extract_playlist_id(playlist_input):
        match = re.search(r'id=(\d+)', playlist_input) or re.search(r'playlist/(\d+)', playlist_input) or re.search(r'(\d{6,})', playlist_input)
        return match.group(1) if match else playlist_input
    
    playlist_id = extract_playlist_id(playlist_input)
    
    c = Card()
    c.append(Module.Header('🎶 歌单处理中'))
    c.append(Module.Context(f'正在获取歌单[{playlist_id}]的所有直链...'))
    await msg.ctx.channel.send(CardMessage(c))
    
    try:
        # 获取歌单详情
        playlist_url = f"{NEW_API_BASE}/playlist/detail?id={playlist_id}"
        res = requests.get(playlist_url, timeout=20)
        
        is_valid, playlist_data = validate_api_response(res, "歌单详情API")
        if not is_valid:
            c = Card()
            c.append(Module.Header('❗ 歌单获取失败'))
            c.append(Module.Context(f'歌单详情API错误: {playlist_data}'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        
        playlist_info = playlist_data.get('playlist', {})
        
        # 获取歌单统计信息
        playlist_name = playlist_info.get('name', '未知歌单')
        track_count = playlist_info.get('trackCount', 0)
        
        print(f"🎵 歌单信息: {playlist_name}, 总歌曲数: {track_count}")
        
        # 优先使用 trackIds，如果没有则使用 tracks
        track_ids = []
        if 'trackIds' in playlist_info and playlist_info['trackIds']:
            track_ids = [str(track['id']) for track in playlist_info['trackIds']]
            print(f"📋 从 trackIds 获取到 {len(track_ids)} 首歌曲")
        elif 'tracks' in playlist_info and playlist_info['tracks']:
            track_ids = [str(track['id']) for track in playlist_info['tracks']]
            print(f"📋 从 tracks 获取到 {len(track_ids)} 首歌曲")
        
        if not track_ids:
            c = Card()
            c.append(Module.Header('❗ 歌单失败'))
            c.append(Module.Context('歌单为空或获取失败'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        
        # 获取歌曲详细信息（只获取歌曲名，不获取URL）
        songs_info = []
        failed_songs = []
        
        print(f"🔄 开始获取歌曲信息，共 {len(track_ids)} 首歌曲")
        
        for i in range(0, len(track_ids), 200):
            batch_ids = track_ids[i:i+200]
            batch_num = i // 200 + 1
            total_batches = (len(track_ids) + 199) // 200
            
            print(f"📦 处理第 {batch_num}/{total_batches} 批，包含 {len(batch_ids)} 首歌曲")
            
            # 获取歌曲详细信息
            song_detail_res = requests.get(f"{NEW_API_BASE}/song/detail?ids={','.join(batch_ids)}", timeout=15)
            is_valid, song_detail_data = validate_api_response(song_detail_res, "歌曲详情API")
            
            if is_valid:
                batch_success = 0
                batch_failed = 0
                
                for song in song_detail_data.get('songs', []):
                    song_id = str(song.get('id', ''))
                    song_name = song.get('name', '未知歌曲')
                    artist_name = song.get('ar', [{}])[0].get('name', '未知歌手') if song.get('ar') else '未知歌手'
                    
                    if song_id and song_name:
                        songs_info.append({
                            'id': song_id,
                            'name': song_name,
                            'artist': artist_name
                        })
                        batch_success += 1
                    else:
                        failed_songs.append(song_id)
                        batch_failed += 1
                
                print(f"✅ 第 {batch_num} 批完成: 成功 {batch_success} 首，失败 {batch_failed} 首")
            else:
                print(f"❌ 第 {batch_num} 批失败: {song_detail_data}")
                failed_songs.extend(batch_ids)
        
        print(f"📊 总体统计: 成功获取 {len(songs_info)} 首歌曲信息，失败 {len(failed_songs)} 首")
        
        if not songs_info:
            c = Card()
            c.append(Module.Header('❗ 歌单失败'))
            c.append(Module.Context('歌单中没有可播放的歌曲'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        
        # 检查用户是否在语音频道
        voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
        if voice_channel_id is None:
            c = Card()
            c.append(Module.Header('❗ 歌单失败'))
            c.append(Module.Context('请先加入语音频道'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        
        # 添加到播放队列（使用歌曲信息标记，播放时实时获取URL）
        player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
        for song_info in songs_info:
            # 创建歌曲标记，格式：PLAYLIST_SONG:歌曲ID:歌曲名:歌手名
            song_marker = f"PLAYLIST_SONG:{song_info['id']}:{song_info['name']}:{song_info['artist']}"
            player.add_music(song_marker)
            time.sleep(0.1)  # 避免过快添加
        
        # 构建详细的结果信息
        success_rate = (len(songs_info) / len(track_ids)) * 100 if track_ids else 0
        
        c = Card()
        c.append(Module.Header('✅ 歌单已加入播放队列'))
        c.append(Module.Context(f'🎵 歌单: {playlist_name}'))
        c.append(Module.Context(f'📊 总歌曲数: {len(track_ids)} 首'))
        c.append(Module.Context(f'✅ 成功获取: {len(songs_info)} 首歌曲信息'))
        c.append(Module.Context(f'❌ 获取失败: {len(failed_songs)} 首'))
        c.append(Module.Context(f'📈 成功率: {success_rate:.1f}%'))
        c.append(Module.Context('🔄 播放时将实时获取最新链接'))
        
        if failed_songs:
            c.append(Module.Context('💡 失败原因可能是歌曲信息获取失败'))
        
        await msg.ctx.channel.send(CardMessage(c))
        
    except Exception as e:
        c = Card()
        c.append(Module.Header('❗ 歌单处理失败'))
        c.append(Module.Context(f'处理歌单时发生错误: {str(e)}'))
        await msg.ctx.channel.send(CardMessage(c))

@bot.command(name='跳过')
async def skip(msg: Message):
    player = kookvoice.Player(msg.ctx.guild.id)
    player.skip()
    c = Card()
    c.append(Module.Header('⏭️ 已跳过'))
    c.append(Module.Context('已跳过当前歌曲'))
    await msg.ctx.channel.send(CardMessage(c))

@bot.command(name='停止')
async def stop(msg: Message):
    player = kookvoice.Player(msg.ctx.guild.id)
    player.stop()
    c = Card()
    c.append(Module.Header('⏹️ 已停止'))
    c.append(Module.Context('播放已停止'))
    await msg.ctx.channel.send(CardMessage(c))

from khl.card import Module, Card, CardMessage

# 删除@bot.command(name="列表")及其下方的list函数实现

@bot.command(name="进度")
async def progress_cmd(msg: Message):
    try:
        player = kookvoice.Player(msg.ctx.guild.id)
        progress = int(player.get_progress())
        await msg.ctx.channel.send(f"当前已播放：{progress} 秒")
    except Exception as e:
        await msg.ctx.channel.send(f"查询进度失败：{e}")

@bot.command(name="跳转")
async def seek(msg: Message, time: int):
    player = kookvoice.Player(msg.ctx.guild.id)
    player.seek(time)
    await msg.ctx.channel.send(f'已跳转到 {time} 秒')

from kookvoice import run_async

@kookvoice.on_event(kookvoice.Status.START)
async def on_music_start(play_info: kookvoice.PlayInfo):
    guild_id = play_info.guild_id
    voice_channel_id = play_info.voice_channel_id
    music_bot_token = play_info.token
    extra_data = play_info.extra_data
    text_channel_id = extra_data['文字频道']
    text_channel = await bot.client.fetch_public_channel(text_channel_id)
    await text_channel.send(f"正在播放 {extra_data.get('音乐名字', play_info.file)}")

    # 自动推送进度
    async def push_progress():
        player = kookvoice.Player(guild_id)
        for _ in range(18*3):  # 约3分钟，18次/分钟
            try:
                progress = int(player.get_progress())
                await text_channel.send(f"当前已播放：{progress} 秒")
                await asyncio.sleep(10)
            except Exception:
                break
    asyncio.create_task(push_progress())

@bot.command(name='清空列表')
async def clear_list(msg: Message):
    try:
        open('list.txt', 'w', encoding='utf-8').close()
        open('NoList.txt', 'w', encoding='utf-8').close()
        player = kookvoice.Player(msg.ctx.guild.id)
        from kookvoice.kookvoice import play_list
        if str(msg.ctx.guild.id) in play_list:
            play_list[str(msg.ctx.guild.id)]['play_list'] = []
            c = Card()
            c.append(Module.Header('🗑️ 播放队列已清空'))
            c.append(Module.Context('仅保留当前正在播放的音乐'))
            await msg.ctx.channel.send(CardMessage(c))
        else:
            c = Card()
            c.append(Module.Header('🗑️ 无队列'))
            c.append(Module.Context('当前没有播放队列'))
            await msg.ctx.channel.send(CardMessage(c))
    except Exception as e:
        c = Card()
        c.append(Module.Header('❗ 清空失败'))
        c.append(Module.Context(f'清空队列失败: {e}'))
        await msg.ctx.channel.send(CardMessage(c))

@bot.command(name='帮助')
async def help_cmd(msg: Message):
    from khl.card import Module, Card, CardMessage
    c = Card()
    c.append(Module.Header('恶小梦Bot网易接口'))
    c.append(Module.Context('🎵 /加入  让机器人进入你的语音频道'))
    c.append(Module.Context('🎶 /wy 歌名  网易云点歌（如 /wy 晴天）'))
    c.append(Module.Context('📀 /wygd 歌单链接  播放网易云歌单（如 /wygd https://music.163.com/playlist?id=947835566）'))
    c.append(Module.Context('⏭️ /跳过  跳过当前歌曲'))
    c.append(Module.Context('⏹️ /停止  停止播放'))
    c.append(Module.Context('🗑️ /清空列表  清空播放队列'))
    c.append(Module.Context('❓ /帮助  查看本说明'))
    c.append(Module.Context('🌟项目开源地址🌟 https://github.com/NightmaresNightmares/kook-music-streamer'))
    c.append(Module.Context('🎵抖音🎵 https://www.douyin.com/user/MS4wLjABAAAADKa8egW-VGLmOg0sqjN-9Vf8wFZRfJwPpzVerdVKzlQ4WK_NvSLjSj3tzdUXfq-k?from_tab_name=main'))
    c.append(Module.Context('🎬哔哩哔哩🎬 https://space.bilibili.com/365374856'))
    c.append(Module.Context('恶小梦Bot等你一起来搞事情'))
    await msg.ctx.channel.send(CardMessage(c))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(bot.start(), kookvoice.start())) 