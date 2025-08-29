#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实时获取URL的歌单功能
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

def test_playlist_realtime():
    """测试实时获取URL的歌单功能"""
    try:
        from config import music_api_base
        
        # 测试歌单ID
        test_playlist_id = "947835566"  # 一个测试歌单
        NEW_API_BASE = music_api_base
        
        print(f"🧪 测试实时获取URL的歌单功能")
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
        
        print(f"🔄 开始获取歌曲信息，共 {len(track_ids)} 首歌曲")
        
        # 获取歌曲详细信息（只获取歌曲名，不获取URL）
        songs_info = []
        failed_songs = []
        
        for i in range(0, len(track_ids), 200):
            batch_ids = track_ids[i:i+200]
            batch_num = i // 200 + 1
            total_batches = (len(track_ids) + 199) // 200
            
            print(f"📦 处理第 {batch_num}/{total_batches} 批，包含 {len(batch_ids)} 首歌曲")
            
            # 获取歌曲详细信息
            song_detail_res = requests.get(f"{NEW_API_BASE}/song/detail?ids={','.join(batch_ids)}", timeout=15)
            is_valid, song_detail_data = validate_api_response(song_detail_res, "歌曲详情API")
            
            if is_valid:
                batch_success = 0
                batch_failed = 0
                
                for song in song_detail_data.get('songs', []):
                    song_id = str(song.get('id', ''))
                    song_name = song.get('name', '未知歌曲')
                    artist_name = song.get('ar', [{}])[0].get('name', '未知歌手') if song.get('ar') else '未知歌手'
                    
                    if song_id and song_name:
                        songs_info.append({
                            'id': song_id,
                            'name': song_name,
                            'artist': artist_name
                        })
                        batch_success += 1
                    else:
                        failed_songs.append(song_id)
                        batch_failed += 1
                
                print(f"✅ 第 {batch_num} 批完成: 成功 {batch_success} 首，失败 {batch_failed} 首")
            else:
                print(f"❌ 第 {batch_num} 批失败: {song_detail_data}")
                failed_songs.extend(batch_ids)
        
        print(f"📊 总体统计: 成功获取 {len(songs_info)} 首歌曲信息，失败 {len(failed_songs)} 首")
        
        success_rate = (len(songs_info) / len(track_ids)) * 100 if track_ids else 0
        print(f"📈 成功率: {success_rate:.1f}%")
        
        # 测试实时获取URL功能
        print(f"\n🔄 测试实时获取URL功能...")
        
        # 选择前3首歌进行测试
        test_songs = songs_info[:3]
        realtime_success = 0
        realtime_failed = 0
        
        for song_info in test_songs:
            song_id = song_info['id']
            song_name = song_info['name']
            artist_name = song_info['artist']
            
            print(f"🎵 测试歌曲: {song_name} - {artist_name}")
            
            # 模拟实时获取URL
            url_api = f"{NEW_API_BASE}/song/url?id={song_id}"
            url_res = requests.get(url_api, timeout=15)
            
            if url_res.status_code == 200:
                url_data = url_res.json()
                if url_data.get('data') and url_data['data'][0].get('url'):
                    print(f"✅ 实时获取URL成功: {song_name}")
                    realtime_success += 1
                else:
                    print(f"❌ 实时获取URL失败: {song_name} (无播放链接)")
                    realtime_failed += 1
            else:
                print(f"❌ 实时获取URL失败: {song_name} (API错误)")
                realtime_failed += 1
        
        print(f"\n📊 实时获取URL测试结果:")
        print(f"✅ 成功: {realtime_success} 首")
        print(f"❌ 失败: {realtime_failed} 首")
        
        # 显示歌曲标记格式
        print(f"\n📋 歌曲标记格式示例:")
        for song_info in test_songs[:2]:  # 只显示前2个
            song_marker = f"PLAYLIST_SONG:{song_info['id']}:{song_info['name']}:{song_info['artist']}"
            print(f"🎵 {song_marker}")
        
        print("🎉 实时获取URL的歌单功能测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_playlist_realtime()
