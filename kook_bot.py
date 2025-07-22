import kookvoice
from khl import *
import requests
import asyncio
import re
import traceback

# 配置 ffmpeg 路径
kookvoice.set_ffmpeg("F:/ffmpeg-master-latest-win64-gpl-shared/ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe")
kookvoice.configure_logging()

bot_token = "1/Mzg0MjE=/O02aee6F14ixnJfYns4AuA=="

bot = Bot(token=bot_token)

async def find_user_voice_channel(gid, aid):
    print(f"[DEBUG] 进入 find_user_voice_channel, gid={gid}, aid={aid}")
    print(f"[STEP] 获取用户 {aid} 在服务器 {gid} 的语音频道ID")
    voice_channel_ = await bot.client.gate.request('GET', 'channel-user/get-joined-channel',
                                                   params={'guild_id': gid, 'user_id': aid})
    voice_channel = voice_channel_["items"]
    if voice_channel:
        print(f"[STEP] 用户 {aid} 当前语音频道ID: {voice_channel[0]['id']}")
        return voice_channel[0]['id']
    print(f"[STEP][WARN] 用户 {aid} 不在任何语音频道")
    return None

@bot.command(name='music', prefixes=['.'])
async def play_song(msg: Message, *, song_name: str):
    print(f"[DEBUG] 进入 .music 指令, msg={msg}, song_name={song_name}")
    print(f"[CMD] .music triggered by {msg.author_id} in guild {msg.ctx.guild.id} with song_name: {song_name}")
    try:
        print("[STEP] 获取用户语音频道ID")
        try:
            voice_channel_id = await find_user_voice_channel(msg.ctx.guild.id, msg.author_id)
        except Exception as e:
            print("[ERROR] 获取语音频道ID异常:", e)
            traceback.print_exc()
            await msg.ctx.channel.send(f"获取语音频道ID失败: {e}")
            return
        if not voice_channel_id:
            await msg.ctx.channel.send('请先加入语音频道')
            print("[STEP][ERROR] 用户未在语音频道")
            return
        print(f"[STEP] 正在搜索网易云: {song_name}")
        try:
            res = requests.get(f"https://music-api.focalors.ltd/cloudsearch?keywords={song_name}")
            data = res.json()
        except Exception as e:
            print("[ERROR] 网易云搜索异常:", e)
            traceback.print_exc()
            await msg.ctx.channel.send(f"网易云搜索失败: {e}")
            return
        songs = data.get('result', {}).get('songs', [])
        print(f"[STEP] 搜索结果: {songs[:1]}")
        if not songs:
            await msg.ctx.channel.send('未搜索到歌曲')
            print("[STEP][WARN] 未搜索到歌曲")
            return
        song = songs[0]
        song_id = song['id']
        print(f"[STEP] 正在获取直链 for song_id: {song_id}")
        try:
            url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={song_id}")
            url_data = url_res.json()
        except Exception as e:
            print("[ERROR] 获取直链API异常:", e)
            traceback.print_exc()
            await msg.ctx.channel.send(f"获取直链API失败: {e}")
            return
        url = url_data['data'][0]['url']
        print(f"[STEP] 直链: {url}")
        if not url:
            await msg.ctx.channel.send('获取直链失败')
            print("[STEP][ERROR] 获取直链失败")
            return
        try:
            with open("active_list.txt", "a", encoding="utf-8") as f:
                f.write(url + "\n")
            print(f"[STEP] 已写入活动文件: {url}")
        except Exception as e:
            print("[ERROR] 写入活动文件异常:", e)
            traceback.print_exc()
            await msg.ctx.channel.send(f"写入活动文件失败: {e}")
            return
        print(f"[STEP] 实例化 Player 并准备推流")
        try:
            player = kookvoice.Player(str(msg.ctx.guild.id), voice_channel_id, bot_token)
            print(f"[STEP] join频道: {voice_channel_id}")
            player.join()
            print(f"[STEP] add_music: {url}")
            player.add_music(url, {"音乐名字": song['name'], "点歌人": msg.author_id})
        except Exception as e:
            print("[ERROR] Player推流异常:", e)
            traceback.print_exc()
            await msg.ctx.channel.send(f"Player推流失败: {e}")
            return
        await msg.ctx.channel.send(f"已添加到播放队列：{song['name']}")
        print(f"[STEP][SUCCESS] 已添加到播放队列：{song['name']}\n")
    except Exception as e:
        await msg.ctx.channel.send(f"点歌失败: {e}")
        print("[STEP][ERROR][music] 点歌异常:", e)
        traceback.print_exc()

@bot.command(name='album', prefixes=['.'])
async def play_playlist(msg: Message, *, playlist_input: str):
    print(f"[CMD] .album triggered by {msg.author_id} in guild {msg.ctx.guild.id} with input: {playlist_input}")
    try:
        print("[STEP] 获取用户语音频道ID")
        voice_channel_id = await find_user_voice_channel(msg.ctx.guild.id, msg.author_id)
        if not voice_channel_id:
            await msg.ctx.channel.send('请先加入语音频道')
            print("[STEP][ERROR] 用户未在语音频道")
            return
        match = re.search(r'id=(\d+)', playlist_input) or re.search(r'playlist/(\d+)', playlist_input) or re.search(r'(\d{6,})', playlist_input)
        playlist_id = match.group(1) if match else playlist_input
        print(f"[STEP] 正在获取歌单所有歌曲 for playlist_id: {playlist_id}")
        res = requests.get(f"https://music-api.focalors.ltd/playlist/track/all?id={playlist_id}")
        data = res.json()
        ids = [song['id'] for song in data.get('songs', [])]
        print(f"[STEP] 歌单歌曲ID: {ids}")
        if not ids:
            await msg.ctx.channel.send('未获取到歌单歌曲')
            print("[STEP][WARN] 未获取到歌单歌曲")
            return
        print(f"[STEP] 正在批量获取直链 for 歌单歌曲ID")
        url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={','.join(map(str, ids))}")
        url_data = url_res.json()
        urls = [item['url'] for item in url_data['data'] if item['url']]
        print(f"[STEP] 歌单直链: {urls}")
        if not urls:
            await msg.ctx.channel.send('未获取到任何可用直链')
            print("[STEP][ERROR] 未获取到任何可用直链")
            return
        # 批量写入活动文件
        with open("active_list.txt", "a", encoding="utf-8") as f:
            for url in urls:
                f.write(url + "\n")
        print(f"[STEP] 已批量写入活动文件，共{len(urls)}首")
        print(f"[STEP] 实例化 Player 并准备推流")
        player = kookvoice.Player(str(msg.ctx.guild.id), voice_channel_id, bot_token)
        print(f"[STEP] join频道: {voice_channel_id}")
        player.join()
        for url in urls:
            print(f"[STEP] add_music: {url}")
            player.add_music(url, {"音乐名字": "歌单曲目", "点歌人": msg.author_id})
        await msg.ctx.channel.send(f"歌单已全部加入播放队列！共{len(urls)}首")
        print(f"[STEP][SUCCESS] 歌单已全部加入播放队列！共{len(urls)}首")
    except Exception as e:
        await msg.ctx.channel.send(f"点歌单失败: {e}")
        print("[STEP][ERROR][album] 点歌单异常:", e)
        traceback.print_exc()

@bot.command(name='list', prefixes=['.'])
async def show_list(msg: Message):
    print(f"[CMD] .list triggered by {msg.author_id} in guild {msg.ctx.guild.id}")
    try:
        print("[STEP] 实例化 Player 并获取队列")
        player = kookvoice.Player(str(msg.ctx.guild.id))
        music_list = player.list()
        print(f"[STEP] 当前播放队列: {music_list}")
        if not music_list or not isinstance(music_list, list):
            await msg.ctx.channel.send('当前播放队列为空')
            print("[STEP][INFO] 当前播放队列为空")
            return
        music_list = [item for item in music_list if item]
        if not music_list:
            await msg.ctx.channel.send('当前播放队列为空')
            print("[STEP][INFO] 当前播放队列为空")
            return
        text = '\n'.join([f'{idx+1}. {item.get("file", "-")}' for idx, item in enumerate(music_list) if item and isinstance(item, dict)])
        await msg.ctx.channel.send(f'当前播放队列：\n{text}')
        print(f"[STEP][SUCCESS] 队列已发送")
    except Exception as e:
        await msg.ctx.channel.send(f'获取播放队列失败: {e}')
        print("[STEP][ERROR][list] 获取播放队列异常:", e)
        traceback.print_exc()

@bot.command(name='join', prefixes=['.'])
async def join_channel(msg: Message):
    print(f"[CMD] .join triggered by {msg.author_id} in guild {msg.ctx.guild.id}")
    try:
        print("[STEP] 获取用户语音频道ID")
        voice_channel_id = await find_user_voice_channel(msg.ctx.guild.id, msg.author_id)
        if not voice_channel_id:
            await msg.ctx.channel.send('请先加入语音频道')
            print("[STEP][ERROR] 用户未在语音频道")
            return
        print(f"[STEP] 实例化 Player 并 join 频道")
        player = kookvoice.Player(str(msg.ctx.guild.id), voice_channel_id, bot_token)
        player.join()
        await msg.ctx.channel.send('已加入你的语音频道')
        print(f"[STEP][SUCCESS] 已加入频道 {voice_channel_id}")
    except Exception as e:
        await msg.ctx.channel.send(f'加入频道失败: {e}')
        print("[STEP][ERROR][join] 加入频道异常:", e)
        traceback.print_exc()

@bot.command(name='exit', prefixes=['.'])
async def exit_channel(msg: Message):
    print(f"[CMD] .exit triggered by {msg.author_id} in guild {msg.ctx.guild.id}")
    try:
        print("[STEP] 实例化 Player 并 stop")
        player = kookvoice.Player(str(msg.ctx.guild.id))
        player.stop()
        await msg.ctx.channel.send('已退出频道并停止播放')
        print(f"[STEP][SUCCESS] 已退出频道")
    except Exception as e:
        await msg.ctx.channel.send(f'退出频道失败: {e}')
        print("[STEP][ERROR][exit] 退出频道异常:", e)
        traceback.print_exc()

if __name__ == '__main__':
    print("[INFO] KOOK 机器人启动中...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.start()) 