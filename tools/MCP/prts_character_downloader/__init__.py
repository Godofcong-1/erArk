# PRTS角色立绘下载器 MCP服务器

"""
PRTS角色立绘下载器 MCP服务器

提供从PRTS网站下载明日方舟角色立绘图片的功能
支持多种下载方式：MediaWiki API、剧情角色页面抓取、直接URL构建
"""

__version__ = "1.0.0"
__author__ = "erArk Team"

from .downloader import PRTSCharacterDownloader
from .server import PRTSMCPServer

__all__ = ["PRTSCharacterDownloader", "PRTSMCPServer"]
