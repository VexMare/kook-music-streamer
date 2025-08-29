#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试替代网易云音乐API
用于寻找可用的API服务
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
            elif 'text/html' in content_type:
                print(f"❌ 返回HTML页面")
                return False, "返回HTML页面"
            else:
                print(f"⚠️ 未知内容类型: {content_type}")
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

def test_search_apis():
    """测试搜索API"""
    print("🔍 测试搜索API")
    
    # 测试的API列表
    apis = [
        {
            "base": "https://api.music.liuzhijin.cn",
            "search_endpoint": "/search?keywords={keyword}",
            "name": "刘志进API"
        },
        {
            "base": "https://netease-cloud-music-api-tau-six.vercel.app",
            "search_endpoint": "/search?keywords={keyword}",
            "name": "Vercel部署API"
        },
        {
            "base": "https://music-api.vercel.app",
            "search_endpoint": "/search?keywords={keyword}",
            "name": "Vercel音乐API"
        },
        {
            "base": "https://music.liuzhijin.cn",
            "search_endpoint": "/search?keywords={keyword}",
            "name": "音乐API"
        }
    ]
    
    test_keyword = "晴天"
    
    working_apis = []
    
    for api in apis:
        endpoint = api["search_endpoint"].format(keyword=quote(test_keyword))
        success, result = test_api_endpoint(
            api["base"], 
            endpoint, 
            f"搜索API - {api['name']}"
        )
        
        if success:
            print(f"✅ {api['name']} 可用!")
            working_apis.append(api)
        else:
            print(f"❌ {api['name']} 不可用: {result}")
        
        time.sleep(1)  # 避免请求过快
    
    return working_apis

def test_song_url_apis(working_apis):
    """测试歌曲URL获取API"""
    print("\n🎵 测试歌曲URL获取API")
    
    test_song_id = "1901371647"  # 示例歌曲ID
    
    for api in working_apis:
        # 尝试不同的URL获取端点
        url_endpoints = [
            f"/song/url?id={test_song_id}",
            f"/song/url/v1?id={test_song_id}",
            f"/song/url/v2?id={test_song_id}"
        ]
        
        for endpoint in url_endpoints:
            success, result = test_api_endpoint(
                api["base"],
                endpoint,
                f"URL获取API - {api['name']} - {endpoint}"
            )
            
            if success:
                print(f"✅ {api['name']} URL获取成功!")
                break
            else:
                print(f"❌ {api['name']} URL获取失败: {result}")
        
        time.sleep(1)

def test_api_health():
    """测试API健康状态"""
    print("\n🏥 测试API健康状态")
    
    health_endpoints = [
        "/",
        "/health",
        "/status",
        "/ping"
    ]
    
    apis = [
        "https://api.music.liuzhijin.cn",
        "https://netease-cloud-music-api-tau-six.vercel.app",
        "https://music-api.vercel.app",
        "https://music.liuzhijin.cn"
    ]
    
    for api in apis:
        print(f"\n测试API: {api}")
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(f"{api}{endpoint}", timeout=5)
                print(f"  {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ {endpoint} 可用")
                    break
            except:
                print(f"  ❌ {endpoint} 不可用")

def main():
    """主函数"""
    print("🔍 替代API测试工具")
    print("=" * 60)
    
    # 测试API健康状态
    test_api_health()
    
    # 测试搜索API
    working_apis = test_search_apis()
    
    # 测试歌曲URL获取API
    if working_apis:
        test_song_url_apis(working_apis)
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    if working_apis:
        print(f"✅ 找到 {len(working_apis)} 个可用的API:")
        for api in working_apis:
            print(f"  - {api['name']}: {api['base']}")
    else:
        print("❌ 没有找到可用的API")
        print("建议:")
        print("  1. 检查网络连接")
        print("  2. 尝试搭建本地API服务")
        print("  3. 使用其他音乐服务")
    
    print("\n" + "=" * 60)
    print("🎯 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

