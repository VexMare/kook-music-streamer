#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试原版播放方法
"""

import sys
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父目录（Main目录）
parent_dir = os.path.dirname(current_dir)

# 将父目录添加到Python路径
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # 导入原版kookvoice模块
    import kookvoice
    from config import ffmpeg_path, bot_token
    
    print("✅ 原版kookvoice模块导入成功!")
    
    # 设置FFmpeg路径
    kookvoice.set_ffmpeg(ffmpeg_path)
    print(f"🔧 FFmpeg路径: {ffmpeg_path}")
    
    # 配置日志
    kookvoice.configure_logging()
    print("🔧 日志配置完成")
    
    # 测试Player类初始化
    print("🔍 测试Player类初始化...")
    try:
        player = kookvoice.Player("test_guild_id", "test_channel_id", bot_token)
        print("✅ Player类初始化成功!")
        
        # 测试添加音乐
        print("🔍 测试添加音乐...")
        try:
            player.add_music("https://m7.music.126.net/20250830044048/8d2fa3e88a02265f0cff51d03864c9ba/ymusic/0e5a/010f/5159/9061428f616e5ba922adf39ae38f896c.flac")
            print("✅ 音乐添加成功!")
        except Exception as e:
            print(f"⚠️ 音乐添加失败（可能是测试环境）: {e}")
        
        # 测试播放列表
        print("🔍 测试播放列表...")
        try:
            from kookvoice.kookvoice import play_list
            print(f"✅ 播放列表状态: {play_list}")
        except Exception as e:
            print(f"⚠️ 播放列表获取失败: {e}")
        
    except Exception as e:
        print(f"❌ Player类初始化失败: {e}")
    
    print("\n🎉 原版播放方法测试完成!")
    
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
