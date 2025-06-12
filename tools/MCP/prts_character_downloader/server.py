#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PRTS角色立绘下载器 MCP服务器

提供从PRTS网站下载明日方舟角色立绘图片的功能
支持多种下载方式：MediaWiki API、剧情角色页面抓取、直接URL构建
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .downloader import PRTSCharacterDownloader

# 配置日志记录 - 针对Windows中文编码优化
import sys
import os

# 在Windows系统上设置控制台编码避免中文乱码
if os.name == 'nt':  # Windows系统
    try:
        # 设置环境变量
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        # 重新配置标准输出编码
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):  
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        # 设置控制台代码页为utf-8
        os.system('chcp 65001 >nul 2>&1')
    except Exception:
        pass  # 忽略编码设置错误

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class PRTSMCPServer:
    """PRTS角色立绘下载器MCP服务器"""
    
    def __init__(self):
        """
        初始化MCP服务器
        
        功能描述：创建服务器实例并初始化下载器
        """
        self.server = Server("prts-character-downloader")
        self.downloader = PRTSCharacterDownloader()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """
        设置MCP服务器的处理器
        
        功能描述：注册工具和请求处理器
        """
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """
            列出可用的工具
            
            返回值类型：List[types.Tool]
            功能描述：返回所有可用的PRTS下载工具
            """
            return [
                types.Tool(
                    name="download_character_image",
                    description="从PRTS网站下载指定角色的立绘图片",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "character_name": {
                                "type": "string",
                                "description": "要下载立绘的角色名称（中文）"
                            },
                            "save_dir": {
                                "type": "string",
                                "description": "保存图片的目录路径（可选，默认为'downloaded_images'）",
                                "default": "downloaded_images"
                            }
                        },
                        "required": ["character_name"]
                    }
                ),
                types.Tool(
                    name="batch_download_characters",
                    description="批量下载多个角色的立绘图片",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "character_names": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "要下载立绘的角色名称列表（中文）"
                            },
                            "save_dir": {
                                "type": "string",
                                "description": "保存图片的目录路径（可选，默认为'downloaded_images'）",
                                "default": "downloaded_images"
                            },
                            "delay_seconds": {
                                "type": "number",
                                "description": "每次下载之间的延迟秒数（可选，默认为1秒）",
                                "default": 1
                            }
                        },
                        "required": ["character_names"]
                    }
                ),
                types.Tool(
                    name="search_character_image_url",
                    description="仅搜索角色立绘图片的URL，不下载",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "character_name": {
                                "type": "string",
                                "description": "要搜索立绘的角色名称（中文）"
                            }
                        },
                        "required": ["character_name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """
            处理工具调用
            
            参数：
                name: 工具名称
                arguments: 工具参数
                
            返回值类型：List[types.TextContent]
            功能描述：根据工具名称执行相应的下载或搜索操作
            """
            try:
                if name == "download_character_image":
                    # 单个角色下载
                    character_name = arguments["character_name"]
                    save_dir = arguments.get("save_dir", "downloaded_images")
                    
                    logger.info(f"开始下载角色立绘: {character_name}")
                    
                    # 先获取解析后的保存路径用于调试
                    resolved_save_dir = self.downloader._resolve_save_path(save_dir)
                    logger.info(f"解析后的保存路径: {resolved_save_dir}")
                    
                    success = await asyncio.to_thread(
                        self.downloader.download_character_image, 
                        character_name, 
                        save_dir
                    )
                    
                    if success:
                        return [types.TextContent(
                            type="text",
                            text=f"成功下载 {character_name} 的立绘图片到 {resolved_save_dir} 目录"
                        )]
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"下载 {character_name} 的立绘图片失败"
                        )]
                
                elif name == "batch_download_characters":
                    # 批量下载
                    character_names = arguments["character_names"]
                    save_dir = arguments.get("save_dir", "downloaded_images")
                    delay_seconds = arguments.get("delay_seconds", 1)
                    
                    logger.info(f"开始批量下载 {len(character_names)} 个角色的立绘")
                    results = await asyncio.to_thread(
                        self.downloader.batch_download_characters,
                        character_names,
                        save_dir,
                        delay_seconds
                    )
                    
                    # 统计结果
                    success_count = sum(1 for success in results.values() if success)
                    total_count = len(character_names)
                    
                    result_text = f"批量下载完成：成功 {success_count}/{total_count}\n\n"
                    for char_name, success in results.items():
                        status = "✓ 成功" if success else "✗ 失败"
                        result_text += f"{status}: {char_name}\n"
                    
                    return [types.TextContent(
                        type="text",
                        text=result_text
                    )]
                
                elif name == "search_character_image_url":
                    # 仅搜索URL
                    character_name = arguments["character_name"]
                    
                    logger.info(f"搜索角色立绘URL: {character_name}")
                    image_url = await asyncio.to_thread(
                        self.downloader.search_character_image_url,
                        character_name
                    )
                    
                    if image_url:
                        return [types.TextContent(
                            type="text",
                            text=f"找到 {character_name} 的立绘图片URL：\n{image_url}"
                        )]
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"未能找到 {character_name} 的立绘图片URL"
                        )]
                
                else:
                    return [types.TextContent(
                        type="text", 
                        text=f"未知工具: {name}"
                    )]
            
            except Exception as e:
                logger.error(f"工具调用出错: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"执行工具时出错: {str(e)}"
                )]

async def main():
    """
    主函数
    
    功能描述：启动MCP服务器
    """
    # 创建服务器实例
    mcp_server = PRTSMCPServer()
    
    # 使用标准输入输出运行服务器
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("PRTS角色立绘下载器 MCP服务器已启动")
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="prts-character-downloader",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
