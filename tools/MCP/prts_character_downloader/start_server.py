#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PRTS角色立绘下载器 MCP服务器启动脚本

用法：
    python start_server.py

该脚本将启动MCP服务器，如果MCP库不可用，则提供独立的命令行界面
"""

import sys
import os
import asyncio

def check_mcp_available():
    """
    检查MCP库是否可用
    
    返回值类型：bool
    功能描述：检查是否安装了MCP库
    """
    try:
        import mcp
        return True
    except ImportError:
        return False

def run_standalone_cli():
    """
    运行独立的命令行界面
    
    功能描述：当MCP库不可用时，提供简单的命令行交互界面
    """
    from downloader import PRTSCharacterDownloader
    
    print("PRTS角色立绘下载器 - 独立模式")
    print("=" * 50)
    print("注意：MCP库未安装，运行在独立模式")
    print("要使用完整的MCP功能，请运行: pip install mcp")
    print("=" * 50)
    
    downloader = PRTSCharacterDownloader()
    
    while True:
        print("\n请选择操作：")
        print("1. 下载单个角色立绘")
        print("2. 批量下载角色立绘")
        print("3. 搜索角色立绘URL")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            # 单个角色下载
            character_name = input("请输入角色名称: ").strip()
            if character_name:
                save_dir = input("请输入保存目录 (默认: downloaded_images): ").strip()
                if not save_dir:
                    save_dir = "downloaded_images"
                
                print(f"\n开始下载 {character_name} 的立绘...")
                success = downloader.download_character_image(character_name, save_dir)
                
                if success:
                    print(f"✓ 成功下载 {character_name} 的立绘")
                else:
                    print(f"✗ 下载 {character_name} 的立绘失败")
        
        elif choice == "2":
            # 批量下载
            characters_input = input("请输入角色名称列表，用逗号分隔: ").strip()
            if characters_input:
                character_names = [name.strip() for name in characters_input.split(",") if name.strip()]
                
                if character_names:
                    save_dir = input("请输入保存目录 (默认: downloaded_images): ").strip()
                    if not save_dir:
                        save_dir = "downloaded_images"
                    
                    delay_input = input("请输入下载间隔秒数 (默认: 1): ").strip()
                    try:
                        delay_seconds = float(delay_input) if delay_input else 1.0
                    except ValueError:
                        delay_seconds = 1.0
                    
                    print(f"\n开始批量下载 {len(character_names)} 个角色的立绘...")
                    results = downloader.batch_download_characters(character_names, save_dir, delay_seconds)
                    
                    # 显示结果
                    success_count = sum(1 for success in results.values() if success)
                    total_count = len(character_names)
                    
                    print(f"\n批量下载完成: {success_count}/{total_count}")
                    for char_name, success in results.items():
                        status = "✓" if success else "✗"
                        print(f"  {status} {char_name}")
                else:
                    print("✗ 请输入有效的角色名称")
        
        elif choice == "3":
            # 搜索URL
            character_name = input("请输入角色名称: ").strip()
            if character_name:
                print(f"\n搜索 {character_name} 的立绘URL...")
                url = downloader.search_character_image_url(character_name)
                
                if url:
                    print(f"✓ 找到立绘URL: {url}")
                else:
                    print(f"✗ 未找到 {character_name} 的立绘URL")
        
        elif choice == "4":
            print("\n再见！")
            break
        
        else:
            print("✗ 无效选择，请输入 1-4")

async def run_mcp_server():
    """
    运行MCP服务器
    
    功能描述：启动完整的MCP服务器
    """
    from server import main
    await main()

def main():
    """
    主函数
    
    功能描述：根据MCP库可用性选择运行模式
    """
    if check_mcp_available():
        print("启动 PRTS角色立绘下载器 MCP服务器...")
        asyncio.run(run_mcp_server())
    else:
        print("MCP库未安装，启动独立命令行界面...")
        run_standalone_cli()

if __name__ == "__main__":
    main()
