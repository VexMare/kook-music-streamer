import kookvoice
import time
from config import ffmpeg_path, bot_token

kookvoice.set_ffmpeg(ffmpeg_path)
kookvoice.configure_logging()

player = kookvoice.Player(None, None, bot_token)

with open('list.txt', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

for url in urls:
    print(f"添加到播放队列: {url}")
    player.add_music(url)
    time.sleep(0.5)

kookvoice.run() 