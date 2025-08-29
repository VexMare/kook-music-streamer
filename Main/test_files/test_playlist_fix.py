#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试歌单获取功能改进
"""

import sys
import os
import requests
import json

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父目录（Main目录）
parent_dir = os.path.dirname(current_dir)

# 将父目录添加到Python路径
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

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

def test_playlist_extraction():
    """测试歌单信息提取"""
    try:
        from config import music_api_base
        
        # 测试歌单ID
        test_playlist_id = "947835566"  # 一个测试歌单
        NEW_API_BASE = music_api_base
        
        print(f"🧪 测试歌单获取功能")
        print(f"🎵 测试歌单ID: {test_playlist_id}")
        print(f"🌐 API地址: {NEW_API_BASE}")
        
        # 获取歌单详情
        playlist_url = f"{NEW_API_BASE}/playlist/detail?id={test_playlist_id}"
        print(f"🔗 请求URL: {playlist_url}")
        
        res = requests.get(playlist_url, timeout=20)
        is_valid, playlist_data = validate_api_response(res, "歌单详情API")
        
        if not is_valid:
            print(f"❌ 歌单详情API错误: {playlist_data}")
            return
        
        playlist_info = playlist_data.get('playlist', {})
        
        # 获取歌单统计信息
        playlist_name = playlist_info.get('name', '未知歌单')
        track_count = playlist_info.get('trackCount', 0)
        
        print(f"🎵 歌单信息: {playlist_name}")
        print(f"📊 总歌曲数: {track_count}")
        
        # 检查 trackIds 和 tracks
        track_ids = []
        if 'trackIds' in playlist_info and playlist_info['trackIds']:
            track_ids = [str(track['id']) for track in playlist_info['trackIds']]
            print(f"📋 从 trackIds 获取到 {len(track_ids)} 首歌曲")
        elif 'tracks' in playlist_info and playlist_info['tracks']:
            track_ids = [str(track['id']) for track in playlist_info['tracks']]
            print(f"📋 从 tracks 获取到 {len(track_ids)} 首歌曲")
        
        if not track_ids:
            print("❌ 没有获取到歌曲ID")
            return
        
        print(f"🔄 开始批量获取URL，共 {len(track_ids)} 首歌曲")
        
        # 批量获取URL
        urls = []
        failed_songs = []
        successful_songs = []
        
        for i in range(0, len(track_ids), 200):
            batch_ids = track_ids[i:i+200]
            batch_num = i // 200 + 1
            total_batches = (len(track_ids) + 199) // 200
            
            print(f"📦 处理第 {batch_num}/{total_batches} 批，包含 {len(batch_ids)} 首歌曲")
            
            url_res = requests.get(f"{NEW_API_BASE}/song/url?id={','.join(batch_ids)}", timeout=15)
            is_valid, url_data = validate_api_response(url_res, "批量URL获取API")
            
            if is_valid:
                batch_success = 0
                batch_failed = 0
                
                for item in url_data['data']:
                    if item['url']:
                        urls.append(item['url'])
                        successful_songs.append(str(item['id']))
                        batch_success += 1
                    else:
                        failed_songs.append(str(item['id']))
                        batch_failed += 1
                
                print(f"✅ 第 {batch_num} 批完成: 成功 {batch_success} 首，失败 {batch_failed} 首")
            else:
                print(f"❌ 第 {batch_num} 批失败: {url_data}")
                failed_songs.extend(batch_ids)
        
        print(f"📊 总体统计: 成功获取 {len(urls)} 首，失败 {len(failed_songs)} 首")
        
        success_rate = (len(urls) / len(track_ids)) * 100 if track_ids else 0
        print(f"📈 成功率: {success_rate:.1f}%")
        
        if failed_songs:
            print(f"💡 失败原因可能是VIP歌曲或版权限制")
            print(f"❌ 失败的歌曲ID: {failed_songs[:10]}...")  # 只显示前10个
        
        print("🎉 歌单获取测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_playlist_extraction()
