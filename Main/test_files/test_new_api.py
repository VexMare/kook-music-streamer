#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的网易云音乐API
https://mapi.chixiaotao.cn/docs/#/
"""

import requests
import json
import time
from urllib.parse import quote

def test_api_endpoint(base_url, endpoint, description=""):
    """测试API端点"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"API: {base_url}")
    print(f"端点: {endpoint}")
    print(f"{'='*60}")
    
    try:
        url = f"{base_url}{endpoint}"
        print(f"完整URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', '未知')}")
        
        # 检查响应内容
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type or 'text/json' in content_type:
                try:
                    data = response.json()
                    print(f"✅ JSON解析成功!")
                    print(f"响应键: {list(data.keys()) if isinstance(data, dict) else '非字典'}")
                    return True, data
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    return False, f"JSON解析失败: {e}"
            else:
                print(f"⚠️ 内容类型: {content_type}")
                # 尝试解析为JSON
                try:
                    data = response.json()
                    print(f"✅ 成功解析为JSON!")
                    return True, data
                except:
                    print(f"❌ 无法解析为JSON")
                    return False, "无法解析为JSON"
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False, f"HTTP错误: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False, str(e)

def test_search_api():
    """测试搜索API"""
    print("🔍 测试搜索API")
    
    base_url = "https://mapi.chixiaotao.cn"
    test_keyword = "晴天"
    
    # 测试不同的搜索端点
    search_endpoints = [
        f"/search?keywords={quote(test_keyword)}",
        f"/cloudsearch?keywords={quote(test_keyword)}",
        f"/search?keywords={quote(test_keyword)}&type=1",
        f"/search?keywords={quote(test_keyword)}&limit=10"
    ]
    
    working_endpoints = []
    
    for i, endpoint in enumerate(search_endpoints, 1):
        success, result = test_api_endpoint(
            base_url, 
            endpoint, 
            f"搜索API #{i}"
        )
        
        if success:
            print(f"✅ 搜索端点 #{i} 可用!")
            working_endpoints.append(endpoint)
            
            # 如果是搜索API，显示歌曲信息
            if isinstance(result, dict) and 'result' in result and 'songs' in result['result']:
                songs = result['result']['songs']
                print(f"找到 {len(songs)} 首歌曲:")
                for j, song in enumerate(songs[:3]):  # 只显示前3首
                    print(f"  {j+1}. {song.get('name', '未知')} - {song.get('ar', [{}])[0].get('name', '未知')}")
        else:
            print(f"❌ 搜索端点 #{i} 不可用: {result}")
        
        time.sleep(1)  # 避免请求过快
    
    return working_endpoints

def test_song_url_api():
    """测试歌曲URL获取API"""
    print("\n🎵 测试歌曲URL获取API")
    
    base_url = "https://mapi.chixiaotao.cn"
    test_song_ids = ["1901371647", "1824045033"]  # 示例歌曲ID
    
    working_url_endpoints = []
    
    for song_id in test_song_ids:
        # 尝试不同的URL获取端点
        url_endpoints = [
            f"/song/url?id={song_id}",
            f"/song/url/v1?id={song_id}",
            f"/song/url/v2?id={song_id}"
        ]
        
        for i, endpoint in enumerate(url_endpoints, 1):
            success, result = test_api_endpoint(
                base_url,
                endpoint,
                f"URL获取API - ID={song_id} - #{i}"
            )
            
            if success:
                print(f"✅ URL获取端点 #{i} 可用!")
                working_url_endpoints.append(endpoint)
                
                # 显示URL信息
                if isinstance(result, dict) and 'data' in result:
                    song_data = result['data'][0] if result['data'] else {}
                    print(f"   歌曲URL: {song_data.get('url', '无URL')}")
                break
            else:
                print(f"❌ URL获取端点 #{i} 不可用: {result}")
        
        time.sleep(1)
    
    return working_url_endpoints

def test_playlist_api():
    """测试歌单API"""
    print("\n📀 测试歌单API")
    
    base_url = "https://mapi.chixiaotao.cn"
    test_playlist_id = "947835566"  # 示例歌单ID
    
    playlist_endpoints = [
        f"/playlist/detail?id={test_playlist_id}",
        f"/playlist/track/all?id={test_playlist_id}",
        f"/playlist/detail?id={test_playlist_id}&limit=10"
    ]
    
    working_playlist_endpoints = []
    
    for i, endpoint in enumerate(playlist_endpoints, 1):
        success, result = test_api_endpoint(
            base_url,
            endpoint,
            f"歌单API #{i}"
        )
        
        if success:
            print(f"✅ 歌单端点 #{i} 可用!")
            working_playlist_endpoints.append(endpoint)
            
            # 显示歌单信息
            if isinstance(result, dict) and 'playlist' in result:
                playlist = result['playlist']
                print(f"   歌单名称: {playlist.get('name', '未知')}")
                print(f"   歌曲数量: {len(playlist.get('trackIds', []))}")
        else:
            print(f"❌ 歌单端点 #{i} 不可用: {result}")
        
        time.sleep(1)
    
    return working_playlist_endpoints

def test_api_health():
    """测试API健康状态"""
    print("\n🏥 测试API健康状态")
    
    base_url = "https://mapi.chixiaotao.cn"
    health_endpoints = [
        "/",
        "/health",
        "/status",
        "/ping",
        "/api/status"
    ]
    
    for endpoint in health_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"  {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ {endpoint} 可用")
                break
        except Exception as e:
            print(f"  ❌ {endpoint} 不可用: {e}")

def main():
    """主函数"""
    print("🔍 新API测试工具")
    print("API: https://mapi.chixiaotao.cn")
    print("=" * 60)
    
    # 测试API健康状态
    test_api_health()
    
    # 测试搜索API
    working_search_endpoints = test_search_api()
    
    # 测试歌曲URL获取API
    working_url_endpoints = test_song_url_api()
    
    # 测试歌单API
    working_playlist_endpoints = test_playlist_api()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    print(f"✅ 可用的搜索端点: {len(working_search_endpoints)}")
    for endpoint in working_search_endpoints:
        print(f"  - {endpoint}")
    
    print(f"✅ 可用的URL获取端点: {len(working_url_endpoints)}")
    for endpoint in working_url_endpoints:
        print(f"  - {endpoint}")
    
    print(f"✅ 可用的歌单端点: {len(working_playlist_endpoints)}")
    for endpoint in working_playlist_endpoints:
        print(f"  - {endpoint}")
    
    if working_search_endpoints and working_url_endpoints:
        print("\n🎉 API测试成功! 可以用于机器人!")
    else:
        print("\n❌ API测试失败，需要进一步检查")
    
    print("\n" + "=" * 60)
    print("🎯 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

