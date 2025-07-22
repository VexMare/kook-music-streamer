import asyncio
import kookvoice
from khl import *
from config import ffmpeg_path, bot_token
import requests, re, time

bot = Bot(token=bot_token)

kookvoice.set_ffmpeg(ffmpeg_path)
kookvoice.configure_logging()

async def find_user(gid, aid):
    voice_channel_ = await bot.client.gate.request('GET', 'channel-user/get-joined-channel',
                                                   params={'guild_id': gid, 'user_id': aid})
    voice_channel = voice_channel_["items"]
    if voice_channel:
        return voice_channel[0]['id']

@bot.command(name='join')
async def join_vc(msg: Message):
    voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
    if voice_channel_id is None:
        await msg.ctx.channel.send('请先加入语音频道')
        return
    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
    player.join()
    voice_channel = await bot.client.fetch_public_channel(voice_channel_id)
    await msg.ctx.channel.send(f'已加入语音频道 #{voice_channel.name}')

@bot.command(name='播放')
async def play(msg: Message, music_input: str):
    voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
    if voice_channel_id is None:
        await msg.ctx.channel.send('请先加入语音频道')
        return

    # 判断是否为直链
    if music_input.startswith("http"):
        music_url = music_input
    else:
        # 自动用网易云API搜索
        res = requests.get(f"https://music-api.focalors.ltd/cloudsearch?keywords={music_input}")
        data = res.json()
        songs = data.get('result', {}).get('songs', [])
        if not songs:
            await msg.ctx.channel.send('未搜索到歌曲')
            return
        song = songs[0]
        song_id = song['id']
        url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={song_id}")
        url_data = url_res.json()
        music_url = url_data['data'][0]['url']
        if not music_url:
            await msg.ctx.channel.send('获取直链失败')
            return

    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
    extra_data = {"音乐名字": music_input, "点歌人": msg.author_id, "文字频道": msg.ctx.channel.id}
    player.add_music(music_url, extra_data)
    await msg.ctx.channel.send(f'添加音乐成功 {music_input}')

@bot.command(name='歌单')
async def playlist_play(msg: Message, playlist_input: str):
    # 1. 解析歌单ID
    def extract_playlist_id(playlist_input):
        match = re.search(r'id=(\d+)', playlist_input) or re.search(r'playlist/(\d+)', playlist_input) or re.search(r'(\d{6,})', playlist_input)
        return match.group(1) if match else playlist_input

    playlist_id = extract_playlist_id(playlist_input)
    await msg.ctx.channel.send(f'正在获取歌单[{playlist_id}]的所有直链...')

    # 2. 获取所有歌曲直链
    res = requests.get(f"https://music-api.focalors.ltd/playlist/track/all?id={playlist_id}")
    data = res.json()
    ids = [str(song['id']) for song in data.get('songs', [])]
    if not ids:
        await msg.ctx.channel.send('未获取到歌单歌曲')
        return

    url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={','.join(ids)}")
    url_data = url_res.json()
    urls = [item['url'] for item in url_data['data'] if item['url']]
    if not urls:
        await msg.ctx.channel.send('未获取到任何可用直链')
        return

    # 3. 获取用户语音频道
    voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
    if voice_channel_id is None:
        await msg.ctx.channel.send('请先加入语音频道')
        return

    # 4. 播放所有直链
    player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
    for url in urls:
        player.add_music(url)
        time.sleep(0.5)
    await msg.ctx.channel.send(f'歌单已全部加入播放队列，共{len(urls)}首！')
    kookvoice.run()

@bot.command(name='跳过')
async def skip(msg: Message):
    player = kookvoice.Player(msg.ctx.guild.id)
    player.skip()
    await msg.ctx.channel.send(f'已跳过当前歌曲')

@bot.command(name='停止')
async def stop(msg: Message):
    player = kookvoice.Player(msg.ctx.guild.id)
    player.stop()
    await msg.ctx.channel.send(f'播放已停止')

from khl.card import Module, Card, CardMessage

@bot.command(name="列表")
async def list(msg: Message):
    try:
        player = kookvoice.Player(msg.ctx.guild.id)
        music_list = player.list()
        print(f"[DEBUG] /列表 music_list: {music_list}")
        if not music_list:
            await msg.ctx.channel.send('当前播放队列为空')
            return
        c = Card(color='#FFA4A4')
        c.append(Module.Context('正在播放'))
        now_playing = music_list.pop(0)
        now_playing_file = now_playing.get('file') if now_playing and isinstance(now_playing, dict) else None
        c.append(Module.Header(now_playing_file or "无"))
        c.append(Module.Divider())
        for index, i in enumerate(music_list):
            if i and isinstance(i, dict) and i.get('file'):
                extra = i.get('extra', {})
                user = extra.get('点歌人', '-') if isinstance(extra, dict) else '-'
                c.append(Module.Context(f"{index + 1}. {i.get('file', '-') } 点歌人：(met){user}(met)"))
        await msg.ctx.channel.send(CardMessage(c))
    except Exception as e:
        print("[ERROR] /列表 指令异常:", e)
        import traceback
        traceback.print_exc()
        await msg.ctx.channel.send(f"获取播放队列失败: {e}")

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
    await text_channel.send(f"正在播放 {play_info.file}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(bot.start(), kookvoice.start())) 