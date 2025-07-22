import kookvoice
import requests
import re

# 配置 ffmpeg 路径
kookvoice.set_ffmpeg("F:/ffmpeg-master-latest-win64-gpl-shared/ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe")
kookvoice.configure_logging()

guild_id = "96420929"
voice_channel_id = "3846068906150173"
bot_token = "1/Mzg0MjE=/O02aee6F14ixnJfYns4AuA=="

player = kookvoice.Player(guild_id, voice_channel_id, bot_token)

def add_song_by_name(song_name):
    res = requests.get(f"https://music-api.focalors.ltd/cloudsearch?keywords={song_name}")
    data = res.json()
    songs = data.get('result', {}).get('songs', [])
    if not songs:
        print(f"未搜索到歌曲: {song_name}")
        return
    song = songs[0]
    song_id = song['id']
    url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={song_id}")
    url_data = url_res.json()
    url = url_data['data'][0]['url']
    if not url:
        print(f"获取直链失败: {song_name}")
        return
    player.add_music(url, {"音乐名字": song['name']})
    print(f"已添加到播放队列：{song['name']}")

def add_playlist_by_input(playlist_input):
    match = re.search(r'id=(\d+)', playlist_input) or re.search(r'playlist/(\d+)', playlist_input) or re.search(r'(\d{6,})', playlist_input)
    playlist_id = match.group(1) if match else playlist_input
    res = requests.get(f"https://music-api.focalors.ltd/playlist/track/all?id={playlist_id}")
    data = res.json()
    ids = [song['id'] for song in data.get('songs', [])]
    if not ids:
        print('未获取到歌单歌曲')
        return
    url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={','.join(map(str, ids))}")
    url_data = url_res.json()
    urls = [item['url'] for item in url_data['data'] if item['url']]
    if not urls:
        print('未获取到任何可用直链')
        return
    for url in urls:
        player.add_music(url, {"音乐名字": "歌单曲目"})
    print(f"歌单已全部加入播放队列！共{len(urls)}首")

# ====== 你可以在这里输入歌名或歌单链接 ======
# 示例：添加单曲
add_song_by_name("两难")

# 示例：添加歌单
# add_playlist_by_input("https://music.163.com/#/playlist?id=123456")
# add_playlist_by_input("123456")
# ======================================

# 启动推流，但不自动退出频道
try:
    kookvoice.run()
except KeyboardInterrupt:
    print("手动终止播放，机器人仍留在频道") 