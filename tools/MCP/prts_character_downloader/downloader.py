#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PRTS角色立绘下载器核心功能模块

从原始脚本重构而来，提供角色立绘下载的核心功能
"""

import os
import urllib.request
import urllib.parse
import json
import time
import re
from typing import Optional, Dict, List

class PRTSCharacterDownloader:
    """PRTS角色立绘下载器"""
    def __init__(self):
        """
        初始化下载器
        
        功能描述：设置下载器的基本配置和用户代理
        """
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # 特殊角色的预定义映射
        self.special_characters = {
            "塔露拉": "https://media.prts.wiki/2/22/Avg_char_011_talula_1.png",
            # 可以在这里添加更多特殊角色的映射
        }
          # 自动检测工作区根目录
        self.workspace_root = self._find_workspace_root()
    
    def _find_workspace_root(self) -> str:
        """
        查找工作区根目录
        
        返回值类型：str
        功能描述：从当前目录向上查找包含特定标识文件的工作区根目录
        """
        # 首先尝试使用MCP服务器的已知位置推断工作区根目录
        current_file = os.path.abspath(__file__)  # 当前downloader.py文件的路径
        print(f"[DEBUG] 当前文件路径: {current_file}")
        
        # 从当前文件路径推断工作区根目录
        # 当前文件在: workspaceroot/tools/MCP/prts_character_downloader/downloader.py
        # 所以工作区根目录是: 向上4级目录
        current_dir = os.path.dirname(current_file)  # .../prts_character_downloader/
        current_dir = os.path.dirname(current_dir)   # .../MCP/
        current_dir = os.path.dirname(current_dir)   # .../tools/
        workspace_root = os.path.dirname(current_dir)  # .../workspaceroot/
        
        print(f"[DEBUG] 通过文件路径推断的工作区根目录: {workspace_root}")
        
        # 验证推断的路径是否包含工作区标识文件
        workspace_markers = [
            'game.py',
            'config.ini', 
            'data',
            'Script',
            '.git'
        ]
        
        found_markers = []
        for marker in workspace_markers:
            marker_path = os.path.join(workspace_root, marker)
            if os.path.exists(marker_path):
                found_markers.append(marker)
        
        if found_markers:
            print(f"[DEBUG] 验证成功，在 {workspace_root} 找到标识文件: {found_markers}")
            return workspace_root
        
        # 如果推断失败，回退到原来的逻辑
        print(f"[DEBUG] 推断失败，回退到目录遍历方式")
        current_dir = os.path.abspath(os.getcwd())
        print(f"[DEBUG] 开始查找工作区根目录，当前目录: {current_dir}")
        
        # 向上查找工作区根目录
        search_dir = current_dir
        while search_dir != os.path.dirname(search_dir):  # 直到根目录
            print(f"[DEBUG] 检查目录: {search_dir}")
            # 检查是否包含工作区标识文件
            found_markers = []
            for marker in workspace_markers:
                marker_path = os.path.join(search_dir, marker)
                if os.path.exists(marker_path):
                    found_markers.append(marker)
            
            if found_markers:
                print(f"[DEBUG] 在 {search_dir} 找到标识文件: {found_markers}")
                return search_dir
            
            search_dir = os.path.dirname(search_dir)
        
        # 如果没找到，返回当前目录
        print(f"[DEBUG] 未找到工作区根目录，返回当前目录: {current_dir}")
        return current_dir
    
    def _resolve_save_path(self, save_dir: str) -> str:
        """
        解析保存路径
        
        参数：
            save_dir (str): 原始保存目录路径
            
        返回值类型：str
        功能描述：将相对路径转换为基于工作区根目录的绝对路径
        """
        # 如果已经是绝对路径，直接返回
        if os.path.isabs(save_dir):
            return save_dir
        
        # 如果是相对路径，基于工作区根目录解析
        resolved_path = os.path.join(self.workspace_root, save_dir)
        return os.path.abspath(resolved_path)
    
    def get_image_url_from_api(self, character_name: str) -> Optional[str]:
        """
        通过MediaWiki API查询图片的实际URL
        
        参数：
            character_name (str): 角色名称
            
        返回值类型：Optional[str]
        功能描述：使用MediaWiki API搜索角色立绘图片URL
        """
        # 构建API查询URL
        api_url = "https://prts.wiki/api.php"
        
        # 查询包含"立绘_角色名"的图片
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'allimages',
            'aifrom': f'立绘_{character_name}_1',
            'ailimit': '10',
            'aiprop': 'url'
        }
        
        try:
            # 构建完整URL
            query_url = api_url + '?' + urllib.parse.urlencode(params)
            print(f"查询API: {query_url}")
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            request = urllib.request.Request(query_url, headers=headers)
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            # 查找匹配的图片
            if 'query' in data and 'allimages' in data['query']:
                for image in data['query']['allimages']:
                    name = image.get('name', '')
                    # 检查是否是我们要找的立绘图片
                    if f'立绘_{character_name}_1' in name or f'立绘_{character_name}_skin' in name:
                        return image.get('url')
                        
        except Exception as e:
            print(f"API查询出错: {e}")
        
        return None
    
    def get_image_from_story_page(self, character_name: str) -> Optional[str]:
        """
        从剧情角色一览页面查找图片
        
        参数：
            character_name (str): 角色名称（可能是部分名称）
            
        返回值类型：Optional[str]
        功能描述：从PRTS网站的剧情角色一览页面爬取角色立绘图片URL
        """
        try:
            url = "https://prts.wiki/w/%E5%89%A7%E6%83%85%E8%A7%92%E8%89%B2%E4%B8%80%E8%A7%88"
            print(f"正在从剧情角色一览页面查找 {character_name}...")
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request) as response:
                html_content = response.read().decode('utf-8')
            
            # 查找所有表格行
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(row_pattern, html_content, re.DOTALL)
            
            print(f"找到 {len(rows)} 个表格行")
            
            # 遍历行查找匹配的角色
            for i, row_content in enumerate(rows):
                # 检查这一行是否包含角色名
                if character_name in row_content:
                    # 提取所有的td
                    td_pattern = r'<td[^>]*>(.*?)</td>'
                    tds = re.findall(td_pattern, row_content, re.DOTALL)
                    
                    # 检查第一个td是否包含角色名
                    first_td_text = re.sub(r'<[^>]+>', '', tds[0]).strip() if len(tds) > 0 else ""
                    
                    # 如果第一个td包含角色名（部分匹配）
                    if character_name in first_td_text:
                        print(f"找到匹配的角色: {first_td_text}")
                        
                        # 搜索范围：当前行和下一行
                        search_content = row_content
                        if i + 1 < len(rows):
                            search_content += rows[i + 1]
                        
                        # 在搜索范围中查找图片
                        img_pattern = r'<img[^>]+(?:data-src|src)=["\']([^"\']+)["\'][^>]*>'
                        img_urls = re.findall(img_pattern, search_content)
                        
                        print(f"在搜索范围找到 {len(img_urls)} 个图片")
                        
                        for img_url in img_urls:
                            if ('Avg_avg_npc' in img_url or 'Avg_char' in img_url) and \
                               'base64' not in img_url and '1px' not in img_url:
                                
                                # 处理相对URL
                                if img_url.startswith('//'):
                                    img_url = 'https:' + img_url
                                elif img_url.startswith('/'):
                                    img_url = 'https://prts.wiki' + img_url
                                
                                # 如果是缩略图，获取原图
                                if '/thumb/' in img_url:
                                    orig_pattern = r'/thumb(/[^/]+/[^/]+/[^/]+\.\w+)/\d+px-'
                                    orig_match = re.search(orig_pattern, img_url)
                                    if orig_match:
                                        img_url = 'https://media.prts.wiki' + orig_match.group(1)
                                
                                print(f"找到匹配的图片URL: {img_url}")
                                return img_url
            
            print(f"未能在表格中找到包含 '{character_name}' 的角色")
                    
        except Exception as e:
            print(f"从剧情角色一览页面查找时出错: {e}")
        
        return None
    
    def get_special_character_url(self, character_name: str) -> Optional[str]:
        """
        获取特殊角色的图片URL
        
        参数：
            character_name (str): 角色名称
            
        返回值类型：Optional[str]
        功能描述：从预定义的特殊角色映射表中获取图片URL
        """
        return self.special_characters.get(character_name, None)
    
    def try_construct_direct_url(self, character_name: str) -> Optional[str]:
        """
        尝试直接构建图片URL
        
        参数：
            character_name (str): 角色名称
            
        返回值类型：Optional[str]
        功能描述：通过尝试常见的hash前缀来直接构建图片URL
        """
        # 对中文进行URL编码
        encoded_name = urllib.parse.quote(f"立绘_{character_name}_1.png")
        
        # 尝试一些常见的hash前缀
        prefixes = [
            "0/01", "0/02", "0/03", "0/04", "0/05", "0/06", "0/07", "0/08", "0/09", "0/0a",
            "0/0b", "0/0c", "0/0d", "0/0e", "0/0f", "1/10", "1/11", "1/12", "1/13", "1/14",
            "1/15", "1/16", "1/17", "1/18", "1/19", "1/1a", "1/1b", "1/1c", "1/1d", "1/1e"
        ]
        
        for prefix in prefixes:
            url = f"https://media.prts.wiki/{prefix}/{encoded_name}"
            
            try:
                headers = {
                    'User-Agent': self.user_agent
                }
                
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request) as response:
                    if response.getcode() == 200:
                        print(f"找到立绘图片: {url}")
                        return url
                        
            except urllib.error.HTTPError:
                continue
            except Exception as e:
                print(f"尝试URL {url} 时出错: {e}")
                break
        
        return None
    
    def search_character_image_url(self, character_name: str) -> Optional[str]:
        """
        搜索角色立绘图片的URL（不下载）
        
        参数：
            character_name (str): 角色名称
            
        返回值类型：Optional[str]
        功能描述：使用多种方法搜索角色立绘图片的URL
        """
        print(f"正在搜索 {character_name} 的立绘图片URL...")
        
        # 方法1：检查是否是特殊角色
        image_url = self.get_special_character_url(character_name)
        if image_url:
            print(f"使用预定义的特殊角色图片URL")
            return image_url
        
        # 方法2：从API获取图片URL
        image_url = self.get_image_url_from_api(character_name)
        if image_url:
            return image_url
        
        # 方法3：从剧情角色一览页面查找
        print("API查询未找到图片，尝试从剧情角色一览页面查找...")
        image_url = self.get_image_from_story_page(character_name)
        if image_url:
            return image_url
        
        # 方法4：尝试直接构建URL
        print("剧情角色页面也未找到，尝试直接构建URL...")
        image_url = self.try_construct_direct_url(character_name)
        if image_url:
            return image_url
        
        print(f"未能找到 {character_name} 的立绘图片URL")
        return None
    
    def download_image_from_url(self, image_url: str, save_path: str) -> bool:
        """
        从URL下载图片到指定路径
        
        参数：
            image_url (str): 图片URL
            save_path (str): 保存路径
            
        返回值类型：bool
        功能描述：下载图片并保存到指定路径
        """
        try:
            # 确保保存路径的目录存在
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
                print(f"创建目录: {save_dir}")
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            request = urllib.request.Request(image_url, headers=headers)
            with urllib.request.urlopen(request) as response:
                image_data = response.read()
            
            with open(save_path, 'wb') as f:
                f.write(image_data)
            
            print(f"图片已保存到: {save_path}")
            return True
            
        except Exception as e:
            print(f"下载图片时出错: {e}")
            return False
    def download_character_image(self, character_name: str, save_dir: str = "downloaded_images") -> bool:
        """
        下载角色立绘图片
        
        参数：
            character_name (str): 角色名称（中文）
            save_dir (str): 保存图片的目录
            
        返回值类型：bool
        功能描述：搜索并下载指定角色的立绘图片
        """
        # 解析保存路径（处理相对路径）
        resolved_save_dir = self._resolve_save_path(save_dir)
        
        # 创建保存目录
        if not os.path.exists(resolved_save_dir):
            os.makedirs(resolved_save_dir)
            print(f"创建下载目录: {resolved_save_dir}")
        
        print(f"正在查询 {character_name} 的立绘图片...")
        print(f"保存目录: {resolved_save_dir}")
        
        # 搜索图片URL
        image_url = self.search_character_image_url(character_name)
        
        if image_url:
            print(f"找到立绘图片: {image_url}")
            
            # 从URL获取文件扩展名
            file_ext = '.png'  # 默认扩展名
            if '.' in image_url:
                ext = image_url.split('.')[-1].split('?')[0].lower()
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    file_ext = '.' + ext
            
            # 生成保存路径
            filename = f"{character_name}_立绘{file_ext}"
            save_path = os.path.join(resolved_save_dir, filename)
            
            # 下载图片
            return self.download_image_from_url(image_url, save_path)
        else:
            print(f"未能找到 {character_name} 的立绘图片")
            return False
    def batch_download_characters(self, character_names: List[str], save_dir: str = "downloaded_images", delay_seconds: float = 1) -> Dict[str, bool]:
        """
        批量下载多个角色的立绘图片
        
        参数：
            character_names (List[str]): 角色名称列表
            save_dir (str): 保存图片的目录
            delay_seconds (float): 每次下载之间的延迟秒数
            
        返回值类型：Dict[str, bool]
        功能描述：批量下载多个角色的立绘，返回每个角色的下载结果
        """
        # 解析保存路径（处理相对路径）
        resolved_save_dir = self._resolve_save_path(save_dir)
        
        # 确保保存目录存在
        if not os.path.exists(resolved_save_dir):
            os.makedirs(resolved_save_dir)
            print(f"创建下载目录: {resolved_save_dir}")
        
        print(f"批量下载目标目录: {resolved_save_dir}")
        
        results = {}
        
        for i, character_name in enumerate(character_names):
            print(f"\n[{i+1}/{len(character_names)}] 开始处理: {character_name}")
            
            # 使用已解析的目录路径
            success = self.download_character_image(character_name, resolved_save_dir)
            results[character_name] = success
            
            # 如果不是最后一个角色，添加延迟
            if i < len(character_names) - 1:
                time.sleep(delay_seconds)
        
        return results
