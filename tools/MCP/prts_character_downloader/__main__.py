#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PRTS角色立绘下载器 MCP服务器

用法：
    python server.py

本MCP服务器提供以下工具：
1. download_character_image - 下载单个角色的立绘图片
2. batch_download_characters - 批量下载多个角色的立绘图片  
3. search_character_image_url - 仅搜索角色立绘图片的URL，不下载

支持多种下载方式：
- MediaWiki API查询
- 剧情角色页面抓取
- 直接URL构建
- 特殊角色预定义映射
"""

from .server import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
