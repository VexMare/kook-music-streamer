#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试异步修复
"""

import sys
import os
import asyncio

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父目录（Main目录）
parent_dir = os.path.dirname(current_dir)

# 将父目录添加到Python路径
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

async def test_async_join():
    try:
        # 导入修复后的kookvoice模块
        import kookvoice_real_fixed as kookvoice
        
        print("✅ 模块导入成功!")
        
        # 测试Player类初始化
        print("🔍 测试Player类初始化...")
        try:
            player = kookvoice.Player("test_guild_id", "test_channel_id", "test_token")
            print("✅ Player类初始化成功!")
            print(f"Player状态: {player.status}")
            
            # 测试异步join方法
            print("\n🔍 测试异步join方法...")
            try:
                # 注意：这里使用测试token，实际会失败，但可以测试异步调用
                result = await player.join()
                print(f"✅ join方法调用成功，结果: {result}")
            except Exception as e:
                print(f"⚠️ join方法调用失败（预期行为）: {e}")
            
        except Exception as e:
            print(f"❌ Player类初始化失败: {e}")
        
        print("\n🎉 异步修复测试完成!")
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_async_join())
