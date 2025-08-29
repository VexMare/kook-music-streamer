#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的歌单功能（包括实时获取URL）
"""

import sys
import os
import time

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父目录（Main目录）
parent_dir = os.path.dirname(current_dir)

# 将父目录添加到Python路径
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_playlist_final():
    """测试完整的歌单功能"""
    try:
        from config import bot_token, ffmpeg_path
        import kookvoice
        
        # 设置FFmpeg路径
        kookvoice.set_ffmpeg(ffmpeg_path)
        
        print(f"🧪 测试完整的歌单功能")
        print(f"🎵 测试歌单ID: 947835566")
        print(f"🌐 FFmpeg路径: {ffmpeg_path}")
        
        # 创建播放器实例
        test_guild_id = "test_guild_123"
        test_channel_id = "test_channel_456"
        
        player = kookvoice.Player(test_guild_id, test_channel_id, bot_token)
        
        print(f"✅ 播放器创建成功")
        
        # 测试添加歌单歌曲标记
        test_song_markers = [
            "PLAYLIST_SONG:2692390754:第57次取消发送:菲菲公主（陆绮菲）",
            "PLAYLIST_SONG:1335942780:九万字:黄诗扶",
            "PLAYLIST_SONG:1413863166:冬眠:阿YueYue"
        ]
        
        print(f"🔄 测试添加歌单歌曲标记...")
        
        for i, song_marker in enumerate(test_song_markers, 1):
            try:
                player.add_music(song_marker)
                print(f"✅ 第 {i} 首歌曲标记添加成功: {song_marker}")
            except Exception as e:
                print(f"❌ 第 {i} 首歌曲标记添加失败: {e}")
        
        # 检查播放列表
        try:
            playlist = player.list()
            print(f"📋 播放列表长度: {len(playlist)}")
            for i, item in enumerate(playlist):
                print(f"  {i+1}. {item.get('file', '未知')}")
        except Exception as e:
            print(f"❌ 获取播放列表失败: {e}")
        
        print("🎉 歌单功能测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_playlist_final()
