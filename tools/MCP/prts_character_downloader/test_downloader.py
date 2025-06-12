#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PRTS角色立绘下载器测试脚本

用于测试下载器的核心功能，不依赖MCP框架
"""

import os
import sys
import time

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from downloader import PRTSCharacterDownloader

def test_single_download():
    """
    测试单个角色下载
    
    功能描述：测试下载单个角色立绘的功能
    """
    print("=== 测试单个角色下载 ===")
    downloader = PRTSCharacterDownloader()
    
    # 测试角色（选择一个存在的角色）
    test_character = "莱伊"
    
    print(f"测试下载角色: {test_character}")
    success = downloader.download_character_image(test_character, "test_images")
    
    if success:
        print(f"✓ 成功下载 {test_character} 的立绘")
    else:
        print(f"✗ 下载 {test_character} 的立绘失败")
    
    return success

def test_url_search():
    """
    测试URL搜索功能
    
    功能描述：测试仅搜索角色立绘URL的功能
    """
    print("\n=== 测试URL搜索功能 ===")
    downloader = PRTSCharacterDownloader()
    
    # 测试角色
    test_character = "莱伊"
    
    print(f"测试搜索角色URL: {test_character}")
    url = downloader.search_character_image_url(test_character)
    
    if url:
        print(f"✓ 找到 {test_character} 的立绘URL: {url}")
        return True
    else:
        print(f"✗ 未找到 {test_character} 的立绘URL")
        return False

def test_batch_download():
    """
    测试批量下载功能
    
    功能描述：测试批量下载多个角色立绘的功能
    """
    print("\n=== 测试批量下载功能 ===")
    downloader = PRTSCharacterDownloader()
    
    # 测试角色列表（选择存在的角色）
    test_characters = ["莱伊", "塔露拉"]
    
    print(f"测试批量下载角色: {test_characters}")
    results = downloader.batch_download_characters(test_characters, "test_images", 1)
    
    # 统计结果
    success_count = sum(1 for success in results.values() if success)
    total_count = len(test_characters)
    
    print(f"\n批量下载结果: {success_count}/{total_count}")
    for char_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {char_name}")
    
    return success_count > 0

def main():
    """
    主测试函数
    
    功能描述：运行所有测试用例
    """
    print("PRTS角色立绘下载器功能测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("URL搜索功能", test_url_search),
        ("单个角色下载", test_single_download),
        ("批量下载功能", test_batch_download),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} 测试出错: {e}")
            results.append((test_name, False))
        
        # 在测试之间添加延迟
        time.sleep(2)
    
    # 总结测试结果
    print("\n" + "=" * 50)
    print("测试结果总结:")
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {status}: {test_name}")
    
    passed_count = sum(1 for _, success in results if success)
    total_count = len(results)
    print(f"\n总计: {passed_count}/{total_count} 测试通过")

if __name__ == "__main__":
    main()
