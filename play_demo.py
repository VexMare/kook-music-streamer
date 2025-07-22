import kookvoice

# 指定 ffmpeg 路径
kookvoice.set_ffmpeg("F:/ffmpeg-master-latest-win64-gpl-shared/ffmpeg-master-latest-win64-gpl-shared/bin/ffmpeg.exe")

kookvoice.configure_logging()

music_path_or_link = "https://m801.music.126.net/20250721022350/72ec15baf5350750d1019465ff1940f6/jdymusic/obj/wo3DlMOGwrbDjj7DisKw/36433247255/635b/cba7/22ef/06f69f218d877d6c65b5c5483a433d7d.mp3?vuutv=ni3/DEFfp18k9yZdAIlBAJkOvqF7B0IyHjccJJTb97haNAJSgtsp8HLjPS2Azu3ByY4i5S8LPlENkBG9RSUgf8nwvA4PPEkxYTdO1d819Fw="  # 示例音频

# 下面三项请替换成你自己的
guild_id = "96420929"
voice_channel_id = "3846068906150173"
bot_token = "1/Mzg0MjE=/O02aee6F14ixnJfYns4AuA=="

player = kookvoice.Player(guild_id, voice_channel_id, bot_token)
player.add_music(music_path_or_link)

kookvoice.run()