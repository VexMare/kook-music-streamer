#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API配置管理工具
用于查看和修改音乐API配置
"""

import os
import sys

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def read_config():
    """读取当前配置"""
    try:
        from config import music_api_base
        return music_api_base
    except ImportError as e:
        print(f"❌ 无法读取配置文件: {e}")
        return None

def write_config(new_api_base):
    """写入新配置"""
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.py')
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换API配置
        import re
        pattern = r'music_api_base\s*=\s*"[^"]*"'
        replacement = f'music_api_base = "{new_api_base}"'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
        else:
            # 如果没有找到配置，在文件末尾添加
            new_content = content.rstrip() + f'\n\n# 音乐API配置\nmusic_api_base = "{new_api_base}"\n'
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"❌ 写入配置文件失败: {e}")
        return False

def test_api(api_base):
    """测试API可用性"""
    import requests
    import json
    
    print(f"\n🔍 测试API: {api_base}")
    
    try:
        # 测试搜索API
        search_url = f"{api_base}/cloudsearch?keywords=测试"
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'result' in data and 'songs' in data['result']:
                    print(f"✅ API可用 - 搜索功能正常")
                    return True
                else:
                    print(f"❌ API响应格式异常")
                    return False
            except json.JSONDecodeError:
                print(f"❌ API返回非JSON数据")
                return False
        else:
            print(f"❌ API响应错误: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API连接失败: {e}")
        return False

def show_menu():
    """显示菜单"""
    print("\n" + "="*60)
    print("🎵 KOOK音乐机器人 - API配置管理")
    print("="*60)
    
    current_api = read_config()
    if current_api:
        print(f"📋 当前API: {current_api}")
    else:
        print("📋 当前API: 未配置")
    
    print("\n📝 可用选项:")
    print("1. 查看当前配置")
    print("2. 切换到新API (https://mapi.chixiaotao.cn)")
    print("3. 切换到备用API (https://api.music.liuzhijin.cn)")
    print("4. 测试当前API")
    print("5. 自定义API地址")
    print("6. 退出")
    print("="*60)

def main():
    """主函数"""
    while True:
        show_menu()
        
        try:
            choice = input("\n请选择操作 (1-6): ").strip()
            
            if choice == '1':
                # 查看当前配置
                current_api = read_config()
                if current_api:
                    print(f"\n📋 当前API配置: {current_api}")
                    test_api(current_api)
                else:
                    print("\n❌ 未找到API配置")
            
            elif choice == '2':
                # 切换到新API
                new_api = "https://mapi.chixiaotao.cn"
                print(f"\n🔄 切换到新API: {new_api}")
                
                if test_api(new_api):
                    if write_config(new_api):
                        print("✅ 配置更新成功!")
                    else:
                        print("❌ 配置更新失败!")
                else:
                    print("❌ API测试失败，未更新配置")
            
            elif choice == '3':
                # 切换到备用API
                backup_api = "https://api.music.liuzhijin.cn"
                print(f"\n🔄 切换到备用API: {backup_api}")
                
                if test_api(backup_api):
                    if write_config(backup_api):
                        print("✅ 配置更新成功!")
                    else:
                        print("❌ 配置更新失败!")
                else:
                    print("❌ API测试失败，未更新配置")
            
            elif choice == '4':
                # 测试当前API
                current_api = read_config()
                if current_api:
                    test_api(current_api)
                else:
                    print("\n❌ 未找到API配置")
            
            elif choice == '5':
                # 自定义API地址
                custom_api = input("\n请输入自定义API地址: ").strip()
                if custom_api:
                    if custom_api.startswith(('http://', 'https://')):
                        print(f"\n🔄 切换到自定义API: {custom_api}")
                        
                        if test_api(custom_api):
                            if write_config(custom_api):
                                print("✅ 配置更新成功!")
                            else:
                                print("❌ 配置更新失败!")
                        else:
                            print("❌ API测试失败，未更新配置")
                    else:
                        print("❌ 请输入有效的HTTP/HTTPS地址")
                else:
                    print("❌ 请输入有效的API地址")
            
            elif choice == '6':
                # 退出
                print("\n👋 再见!")
                break
            
            else:
                print("❌ 无效选择，请输入1-6")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作，再见!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    main()

