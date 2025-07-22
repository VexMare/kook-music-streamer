import requests
import re

# 输入歌单链接或ID
def extract_playlist_id(playlist_input):
    match = re.search(r'id=(\d+)', playlist_input) or re.search(r'playlist/(\d+)', playlist_input) or re.search(r'(\d{6,})', playlist_input)
    return match.group(1) if match else playlist_input

playlist_input = input('请输入网易云歌单链接或ID: ')
playlist_id = extract_playlist_id(playlist_input)

# 获取歌单所有歌曲ID
res = requests.get(f"https://music-api.focalors.ltd/playlist/track/all?id={playlist_id}")
data = res.json()
ids = [str(song['id']) for song in data.get('songs', [])]
if not ids:
    print('未获取到歌单歌曲')
    exit(1)

# 获取所有歌曲的直链
url_res = requests.get(f"https://music-api.focalors.ltd/song/url?id={','.join(ids)}")
url_data = url_res.json()
urls = [item['url'] for item in url_data['data'] if item['url']]

if not urls:
    print('未获取到任何可用直链')
    exit(1)

# 保存到list.txt
with open('list.txt', 'w', encoding='utf-8') as f:
    for url in urls:
        f.write(url + '\n')
print(f'已保存{len(urls)}首歌曲直链到list.txt') 