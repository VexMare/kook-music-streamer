import os
import importlib.util
import asyncio
import kookvoice
from khl import *
import requests, re, time

# 始终读取当前工作目录下的 config.py
config_path = os.path.join(os.getcwd(), 'config.py')
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
ffmpeg_path = config.ffmpeg_path
bot_token = config.bot_token

bot = Bot(token=bot_token)

kookvoice.set_ffmpeg(ffmpeg_path)
kookvoice.configure_logging()

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
    else:
        res = requests.get(f"https://music-api.focalors.ltd/cloudsearch?keywords={music_input}")
        data = res.json()
        songs = data.get('result', {}).get('songs', [])
        if not songs:
            c = Card()
            c.append(Module.Header('❗ 点歌失败'))
            c.append(Module.Context('未搜索到歌曲'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        song = songs[0]
        song_id = song['id']
        url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={song_id}")
        url_data = url_res.json()
        music_url = url_data['data'][0]['url']
        if not music_url:
            c = Card()
            c.append(Module.Header('❗ 点歌失败'))
            c.append(Module.Context('获取直链失败'))
            await msg.ctx.channel.send(CardMessage(c))
            return
    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
    extra_data = {"音乐名字": music_input, "点歌人": msg.author_id, "文字频道": msg.ctx.channel.id}
    player.add_music(music_url, extra_data)
    c = Card()
    c.append(Module.Header('✅ 添加音乐成功'))
    c.append(Module.Context(f'{music_input} 已加入播放队列'))
    await msg.ctx.channel.send(CardMessage(c))

@bot.command(name='wygd')
async def playlist_play(msg: Message, playlist_input: str):
    open('list.txt', 'w', encoding='utf-8').close()
    open('NoList.txt', 'w', encoding='utf-8').close()
    def extract_playlist_id(playlist_input):
        match = re.search(r'id=(\d+)', playlist_input) or re.search(r'playlist/(\d+)', playlist_input) or re.search(r'(\d{6,})', playlist_input)
        return match.group(1) if match else playlist_input
    playlist_id = extract_playlist_id(playlist_input)
    c = Card()
    c.append(Module.Header('🎶 歌单处理中'))
    c.append(Module.Context(f'正在获取歌单[{playlist_id}]的所有直链...'))
    await msg.ctx.channel.send(CardMessage(c))
    cookie = "_iuqxldmzr_=32; ..."  # 省略长cookie
    res = requests.get(f"https://music-api.focalors.ltd/playlist/detail?id={playlist_id}", params={"cookie": cookie})
    data = res.json()
    track_ids = [str(track['id']) for track in data.get('playlist', {}).get('trackIds', [])]
    if not track_ids:
        c = Card()
        c.append(Module.Header('❗ 歌单失败'))
        c.append(Module.Context('请再重新获取一次若还是失败请联系管理员'))
        await msg.ctx.channel.send(CardMessage(c))
        return
    urls = []
    id2url = {}
    for i in range(0, len(track_ids), 200):
        batch_ids = track_ids[i:i+200]
        url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={','.join(batch_ids)}", params={"cookie": cookie})
        url_data = url_res.json()
        for item in url_data['data']:
            if item['url']:
                urls.append(item['url'])
                id2url[str(item['id'])] = item['url']
    no_url_ids = [tid for tid in track_ids if tid not in id2url]
    with open('NoList.txt', 'w', encoding='utf-8') as f:
        for tid in no_url_ids:
            f.write(tid + '\n')
    with open('list.txt', 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')
    voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
    if voice_channel_id is None:
        c = Card()
        c.append(Module.Header('❗ 歌单失败'))
        c.append(Module.Context('请先加入语音频道'))
        await msg.ctx.channel.send(CardMessage(c))
        return
    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
    for url in urls:
        player.add_music(url)
        time.sleep(0.5)
    c = Card()
    c.append(Module.Header('✅ 歌单已加入播放队列'))
    c.append(Module.Context(f'共{len(urls)}首可用歌曲已加入播放队列'))
    await msg.ctx.channel.send(CardMessage(c))
    kookvoice.run()

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
    c.append(Module.Context('📄 /wygd 歌单链接  播放网易云歌单（如 /wygd https://music.163.com/playlist?id=947835566）'))
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