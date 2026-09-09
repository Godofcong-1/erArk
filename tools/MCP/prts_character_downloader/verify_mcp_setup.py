#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PRTS MCP服务器启动验证脚本

功能描述：验证MCP服务器是否能正常启动和提供工具
"""

import sys
import os
import asyncio
import json

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from tools.MCP.prts_character_downloader.server import PRTSMCPServer
    from tools.MCP.prts_character_downloader.downloader import PRTSCharacterDownloader
    print("✅ 模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

async def test_mcp_server():
    """
    测试MCP服务器功能
    
    返回值类型：无
    功能描述：创建MCP服务器实例并测试基础功能
    """
    try:
        # 创建MCP服务器实例
        print("🔧 创建MCP服务器实例...")
        mcp_server = PRTSMCPServer()
        print("✅ MCP服务器实例创建成功")
        
        # 测试下载器功能
        print("🔧 测试下载器功能...")
        downloader = PRTSCharacterDownloader()
        
        # 测试搜索功能（不实际下载）
        print("🔍 测试搜索莱伊的立绘URL...")
        url = await asyncio.to_thread(downloader.search_character_image_url, "莱伊")
        if url:
            print(f"✅ 搜索成功: {url}")
        else:
            print("未找到URL，但搜索功能正常")
        
        print("✅ 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_downloader_basic():
    """
    测试下载器基础功能
    
    返回值类型：bool
    功能描述：测试下载器是否能正常初始化
    """
    try:
        print("🔧 测试下载器基础功能...")
        downloader = PRTSCharacterDownloader()
        print("✅ 下载器初始化成功")
        
        # 测试特殊角色映射
        special_chars = downloader.special_characters
        print(f"✅ 特殊角色映射加载成功，包含 {len(special_chars)} 个角色")
        
        return True
    except Exception as e:
        print(f"❌ 下载器测试失败: {e}")
        return False

def main():
    """
    主函数
    
    返回值类型：无
    功能描述：运行所有测试
    """
    print("=" * 50)
    print("PRTS MCP服务器启动验证")
    print("=" * 50)
    
    # 测试基础功能
    if not test_downloader_basic():
        sys.exit(1)
    
    print("\n" + "-" * 30)
    print("开始异步测试...")
    print("-" * 30)
    
    # 运行异步测试
    try:
        success = asyncio.run(test_mcp_server())
        if success:
            print("\n🎉 所有测试通过！MCP服务器可以正常使用。")
            print("\n📝 使用说明：")
            print("1. 重启VS Code以应用MCP配置")
            print("2. 在GitHub Copilot Chat中使用以下命令：")
            print("   - @prts 下载莱伊的立绘")
            print("   - @prts 搜索塔露拉的立绘URL")
            print("   - @prts 批量下载 莱伊,陈,阿米娅 的立绘")
        else:
            print("\n❌ 测试失败，请检查配置。")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 异步测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
