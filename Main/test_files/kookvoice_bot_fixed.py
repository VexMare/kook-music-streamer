#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOOK音乐机器人 - 修复版本
包含更好的错误处理和API响应验证
"""

import asyncio
import kookvoice
from khl import *
from config import ffmpeg_path, bot_token
import requests, re, time
import json

bot = Bot(token=bot_token)

kookvoice.set_ffmpeg(ffmpeg_path)
kookvoice.configure_logging()

async def find_user(gid, aid):
    voice_channel_ = await bot.client.gate.request('GET', 'channel-user/get-joined-channel',
                                                   params={'guild_id': gid, 'user_id': aid})
    voice_channel = voice_channel_["items"]
    if voice_channel:
        return voice_channel[0]['id']

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
        try:
            # 搜索歌曲
            search_url = f"https://music-api.focalors.ltd/cloudsearch?keywords={music_input}"
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
            
            # 获取歌曲URL
            url_api = f"https://music-api.focalors.ltd/song/url?id={song_id}"
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
    
    # 添加到播放队列
    try:
        player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
        extra_data = {"音乐名字": music_input, "点歌人": msg.author_id, "文字频道": msg.ctx.channel.id}
        player.add_music(music_url, extra_data)
        
        c = Card()
        c.append(Module.Header('✅ 添加音乐成功'))
        c.append(Module.Context(f'{music_input} 已加入播放队列'))
        await msg.ctx.channel.send(CardMessage(c))
        
    except Exception as e:
        c = Card()
        c.append(Module.Header('❗ 播放失败'))
        c.append(Module.Context(f'添加到播放队列失败: {str(e)}'))
        await msg.ctx.channel.send(CardMessage(c))

@bot.command(name='wygd')
async def playlist_play(msg: Message, playlist_input: str):
    # 清空临时文件
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
    
    try:
        # 获取歌单详情
        cookie = "_iuqxldmzr_=32; _ntes_nnid=f8d17ff9e05eeabfb8c72fe67ad97c16,1751683757404; _ntes_nuid=f8d17ff9e05eeabfb8c72fe67ad97c16; NMTID=00Oizgk-WYcmXqiDUmNm5Rtpyrf5kMAAAGX2H0B3A; WEVNSM=1.0.0; WNMCID=udswoz.1751683758155.01.0; WM_TID=HCqXgqTIIQNFBEQABRaSb7OBKqYFM%2BEq; sDeviceId=YD-oVtKGUmBDkdAAxEVQRbTe6KUerYUO4mm; ntes_utid=tid._.FIXa1T4qo25AEhQUQFPDaqPBa6YUf9ni._.0; __snaker__id=cQV1B7woOE1YivlC; __remember_me=true; _ns=NS1.2.460637847.1752213999; timing_user_id=time_bxhYvDdYla; ntes_kaola_ad=1; gdxidpyhxdE=xLinAr2KQACRbE6dMJbuW9QHVUy4%2F7EdTxW0OxNNZmLcZC1gYUnT6oEQJDur5ATAiBKne3epmAamVcl5CZXZobploHbM%2B%5CsTfWQPX4OXQR6VGf7nUJs%2FRD2a%5C3Z4uWnB%2F4duBVlvRco%2B%2B%2F7LCcxDMkAm4q8b9mk7yw%5CjexIlE%5C%5CYhpa7%3A1752995592949; MUSIC_U=002371E7668FBD67FCE25C294FB8E0EA024932A8812D854E56DBE11FF5693F2C236EF3C290D8367EA82922470229347DFF3EF32EEAD0B2135900F60923C9A27D2CF508C2883D16BB477CABE04883B3195059B483F0472E8D8676B1756658C0BD3B38F52BAF43FB61BA5F48E8696D4936AE51F2DB9A84398BDA0937008A642323BFED0BAE292D581E6A273CF0ABDE9F7C9ED74F79A5E5D334878482277B23E1C71978122714DDCB04FE08F4C7CDBCD32A58A0802DC22B1C1DD40E114F58DC9F5DBE177D1077EFC5AB9CCA72FF8A073970A1F92640723BDC516337EF18ED884ED048EC0F272C146D654525D55A9A18112C6CEA76F972DE126B1E4FAF018B65F2FA9C6302E06830BAD9FFB8C8F4BA2D5E3413EB6DD6DA1A062EAB26337AB07C7C3855115AF6D6133A3C084A4E5C3392BDC8AC459200014988C553E9C8A8BA928A3AA7C6CD4F62AB9D047DE1DAEA15B8FF5F1020C5FC954183C0A670D6E86129711623BB9B86442E18C1488744E2B9FABC1DF746D048CE521AB607D89546F9A4BE2BC40BF86E4954F03C285C44E380F942DC1D8A8FA8FED69B52F27572960814110C44; __csrf=31df74b574317b691b1961de39798404; JSESSIONID-WYYY=XJChzC28SNq2HItYknBNsc9goMm77mpui%2FXSRPq%2FHZ2WEqdncxhd65ToKoQo%2F%2FRGhbvCpd28WT8frn%5C6jnnCwsZ19aO%2FxGwOw0dxbjI8w7Blxv854W%2BKfmqBAP1aqTVRIunVdAorMqjnEmmD5qVFp7m8WF4XhACXPZl7Mplty2l%2B%2FGcU%3A1753265767321; WM_NI=86y44SGto%2FVEZLbiLygPy5dl8AZvRxlayeuYdM%2FKoVXZiT7uV44T4C6EJqZB7wkKcBIF2nVcS4IWLBg7Hdl3YANEpOCIH34TTZw1MIcx7hCWZBdRDx9ylYbpolDJiWisR0c%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee86f56af692ac97c754aa8a8ea2d44a979e8faccb3c86e7c09ae543a8b5bf8bf82af0fea7c3b92afceab7d5b75985aca1d0d54f9a94ae8acf73a590b7d6e768fc9f9697d174b0bfb786f853a893e1acee5e9c86a7b5b67f96ecfcb5b749f69b8692d94af5a9a5ace24a8b9afe8fd56991ec87b8cf4aa5e98885ef399b9f82a6f345819788d4b7609886b9d2d043a1a8f989c25d9a9eacb3c774fba7a4bae17cadb48cabec5dabad9ed1e237e2a3"
        
        playlist_url = f"https://music-api.focalors.ltd/playlist/detail?id={playlist_id}"
        res = requests.get(playlist_url, params={"cookie": cookie}, timeout=20)
        
        is_valid, playlist_data = validate_api_response(res, "歌单详情API")
        if not is_valid:
            c = Card()
            c.append(Module.Header('❗ 歌单获取失败'))
            c.append(Module.Context(f'歌单详情API错误: {playlist_data}'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        
        track_ids = [str(track['id']) for track in playlist_data.get('playlist', {}).get('trackIds', [])]
        if not track_ids:
            c = Card()
            c.append(Module.Header('❗ 歌单失败'))
            c.append(Module.Context('歌单为空或获取失败'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        
        print(f"📀 歌单包含 {len(track_ids)} 首歌曲")
        
        # 批量获取歌曲URL
        urls = []
        id2url = {}
        
        for i in range(0, len(track_ids), 200):
            batch_ids = track_ids[i:i+200]
            url_api = f"https://music-api.focalors.ltd/song/url?id={','.join(batch_ids)}"
            
            url_res = requests.get(url_api, params={"cookie": cookie}, timeout=20)
            is_valid, url_data = validate_api_response(url_res, "批量URL获取API")
            
            if is_valid:
                for item in url_data['data']:
                    if item['url']:
                        urls.append(item['url'])
                        id2url[str(item['id'])] = item['url']
            else:
                print(f"⚠️ 批量获取URL失败: {url_data}")
        
        # 记录无法获取URL的歌曲
        no_url_ids = [tid for tid in track_ids if tid not in id2url]
        with open('NoList.txt', 'w', encoding='utf-8') as f:
            for tid in no_url_ids:
                f.write(tid + '\n')
        
        with open('list.txt', 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(url + '\n')
        
        print(f"✅ 成功获取 {len(urls)} 首歌曲的URL")
        
        # 检查用户是否在语音频道
        voice_channel_id = await find_user(msg.ctx.guild.id, msg.author_id)
        if voice_channel_id is None:
            c = Card()
            c.append(Module.Header('❗ 歌单失败'))
            c.append(Module.Context('请先加入语音频道'))
            await msg.ctx.channel.send(CardMessage(c))
            return
        
        # 添加到播放队列
        player = kookvoice.Player(msg.ctx.guild.id, voice_channel_id, bot_token)
        for url in urls:
            player.add_music(url)
            time.sleep(0.5)
        
        c = Card()
        c.append(Module.Header('✅ 歌单已加入播放队列'))
        c.append(Module.Context(f'共{len(urls)}首可用歌曲已加入播放队列'))
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
    asyncio.run(asyncio.gather(bot.start(), kookvoice.start()))

