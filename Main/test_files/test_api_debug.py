#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易云音乐API调试工具
用于分析和解决API响应解析问题
"""

import requests
import json
import time
from urllib.parse import quote

def test_api_response(url, description=""):
    """测试API响应并详细分析"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        # 发送请求
        print("正在发送请求...")
        response = requests.get(url, timeout=10)
        
        # 显示响应状态
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应大小: {len(response.content)} 字节")
        
        # 显示原始响应内容
        print(f"\n原始响应内容 (前500字符):")
        print("-" * 40)
        content_preview = response.text[:500]
        print(content_preview)
        if len(response.text) > 500:
            print("... (内容被截断)")
        print("-" * 40)
        
        # 尝试解析JSON
        try:
            data = response.json()
            print(f"\n✅ JSON解析成功!")
            print(f"数据类型: {type(data)}")
            print(f"数据键: {list(data.keys()) if isinstance(data, dict) else '非字典类型'}")
            
            # 如果是搜索API，显示歌曲信息
            if 'result' in data and 'songs' in data['result']:
                songs = data['result']['songs']
                print(f"\n找到 {len(songs)} 首歌曲:")
                for i, song in enumerate(songs[:3]):  # 只显示前3首
                    print(f"  {i+1}. {song.get('name', '未知')} - {song.get('ar', [{}])[0].get('name', '未知')}")
            
            return True, data
            
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON解析失败: {e}")
            print(f"错误位置: 第{e.lineno}行，第{e.colno}列")
            print(f"错误信息: {e.msg}")
            
            # 尝试分析响应内容
            if response.text.strip() == "":
                print("⚠️  响应内容为空")
            elif "html" in response.text.lower():
                print("⚠️  响应内容可能是HTML页面")
            elif "error" in response.text.lower():
                print("⚠️  响应内容包含错误信息")
            
            return False, response.text
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")
        return False, str(e)

def test_music_search_api():
    """测试音乐搜索API"""
    print("🎵 测试网易云音乐搜索API")
    
    # 测试不同的搜索关键词
    test_keywords = ["晴天", "周杰伦", "test"]
    
    for keyword in test_keywords:
        url = f"https://music-api.focalors.ltd/cloudsearch?keywords={quote(keyword)}"
        success, data = test_api_response(url, f"搜索关键词: {keyword}")
        
        if success:
            print(f"✅ 搜索 '{keyword}' 成功")
        else:
            print(f"❌ 搜索 '{keyword}' 失败")
        
        time.sleep(1)  # 避免请求过快

def test_song_url_api():
    """测试歌曲URL获取API"""
    print("\n🎵 测试歌曲URL获取API")
    
    # 使用一个已知的歌曲ID进行测试
    test_song_ids = ["1901371647", "1824045033"]  # 一些示例歌曲ID
    
    for song_id in test_song_ids:
        url = f"https://music-api.focalors.ltd/song/url?id={song_id}"
        success, data = test_api_response(url, f"获取歌曲URL: ID={song_id}")
        
        if success:
            print(f"✅ 获取歌曲URL成功")
            if isinstance(data, dict) and 'data' in data:
                song_data = data['data'][0] if data['data'] else {}
                print(f"   歌曲URL: {song_data.get('url', '无URL')}")
        else:
            print(f"❌ 获取歌曲URL失败")
        
        time.sleep(1)

def test_alternative_apis():
    """测试备用API"""
    print("\n🔄 测试备用API")
    
    # 测试其他可能的API端点
    alternative_apis = [
        "https://music-api.focalors.ltd/search?keywords=晴天",
        "https://music-api.focalors.ltd/cloudsearch?keywords=晴天&limit=10",
        "https://music-api.focalors.ltd/cloudsearch?keywords=晴天&type=1"
    ]
    
    for i, api_url in enumerate(alternative_apis, 1):
        success, data = test_api_response(api_url, f"备用API #{i}")
        if success:
            print(f"✅ 备用API #{i} 可用")
        else:
            print(f"❌ 备用API #{i} 不可用")
        time.sleep(1)

def test_network_connectivity():
    """测试网络连接"""
    print("\n🌐 测试网络连接")
    
    test_urls = [
        "https://www.baidu.com",
        "https://music.163.com",
        "https://music-api.focalors.ltd"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - 连接失败: {e}")

def main():
    """主函数"""
    print("🔍 网易云音乐API调试工具")
    print("=" * 60)
    
    # 测试网络连接
    test_network_connectivity()
    
    # 测试音乐搜索API
    test_music_search_api()
    
    # 测试歌曲URL获取API
    test_song_url_api()
    
    # 测试备用API
    test_alternative_apis()
    
    print("\n" + "=" * 60)
    print("🎯 调试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

