#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Status枚举修复
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
    # 导入修复后的kookvoice模块
    import kookvoice_real_fixed as kookvoice
    
    print("✅ 模块导入成功!")
    
    # 测试Status枚举
    print("🔍 测试Status枚举...")
    print(f"Status.WAIT: {kookvoice.Status.WAIT}")
    print(f"Status.PLAYING: {kookvoice.Status.PLAYING}")
    print(f"Status.END: {kookvoice.Status.END}")
    print(f"Status.SKIP: {kookvoice.Status.SKIP}")
    print(f"Status.STOP: {kookvoice.Status.STOP}")
    print(f"Status.STOPPED: {kookvoice.Status.STOPPED}")
    print(f"Status.START: {kookvoice.Status.START}")
    
    # 测试Player类初始化
    print("\n🔍 测试Player类初始化...")
    try:
        player = kookvoice.Player("test_guild_id", "test_channel_id", "test_token")
        print("✅ Player类初始化成功!")
        print(f"Player状态: {player.status}")
    except Exception as e:
        print(f"❌ Player类初始化失败: {e}")
    
    print("\n🎉 Status枚举修复测试完成!")
    
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
