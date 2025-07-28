import subprocess
import time
import os

# 网易云音乐直链
music_url = "http://m801.music.126.net/20250724000052/cfa2e5b949d31190d5cd15547512b18a/jdymusic/obj/wo3DlMOGwrbDjj7DisKw/36433243748/4e0f/6d75/1fc4/8d0d2b4eb9bc897f1b7a847963b9df15.mp3?vuutv=Yc6mclsPzjIyJ5jTgixfNdCRTHhIUFaQEqTmry0swXQoteYXFxgRRiMqlNV/4K1rQMl8bF2jc4DpxyBX5cmqsaqO4ZDBMJCUtyWp1Sf4tolNdZ4gtZGJoKz6O2RelGvlyOl3AZ8+lVDIDlauq+b/cnX45FfTSkCK9NpsgguERfU="

# ffmpeg和ffplay的路径（根据实际情况修改）
ffmpeg_path = r"./ffmpeg/bin/ffmpeg.exe"
ffplay_path = r"./ffmpeg/bin/ffplay.exe"

# 推流端口
rtp_port = 12345
sdp_file = "test.sdp"

# 先删除旧的SDP文件
if os.path.exists(sdp_file):
    os.remove(sdp_file)

# 1. 启动ffmpeg推流并生成SDP
ffmpeg_cmd = [
    ffmpeg_path,
    "-re",  # 新增，实时推流
    "-i", music_url,
    "-ac", "2",
    "-ar", "48000",
    "-c:a", "libopus",
    "-b:a", "64k",
    "-f", "rtp",
    f"rtp://127.0.0.1:{rtp_port}",
    "-sdp_file", sdp_file
]
print("启动ffmpeg推流...\n命令:", ' '.join(ffmpeg_cmd))
ffmpeg_proc = subprocess.Popen(ffmpeg_cmd)

# 2. 等待SDP文件生成
for _ in range(10):
    if os.path.exists(sdp_file):
        break
    time.sleep(0.5)
else:
    print("SDP文件生成失败，退出。")
    ffmpeg_proc.terminate()
    exit(1)

# 3. 启动ffplay接收
ffplay_cmd = [ffplay_path, "-protocol_whitelist", "file,rtp,udp,crypto,data", sdp_file]
print("启动ffplay接收...\n命令:", ' '.join(ffplay_cmd))
ffplay_proc = subprocess.Popen(ffplay_cmd)

# 4. 等待推流结束
try:
    ffmpeg_proc.wait()
except KeyboardInterrupt:
    pass
finally:
    ffplay_proc.terminate()
    print("测试结束。") 