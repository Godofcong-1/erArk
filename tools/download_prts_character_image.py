#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从PRTS网站下载指定角色的立绘图片（最终优化版）
整合原有的API方法和优化后的批量下载功能
"""

import os
import sys
import urllib.request
import urllib.parse
import json
import time
import re
from html.parser import HTMLParser

def get_image_url_from_api(character_name):
    """
    通过MediaWiki API查询图片的实际URL
    
    Args:
        character_name: 角色名称
        
    Returns:
        图片URL或None
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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

def get_image_from_story_page(character_name):
    """
    从剧情角色一览页面查找图片（改进版）
    
    Args:
        character_name: 角色名称（可能是部分名称）
        
    Returns:
        图片URL或None
    """
    try:
        url = "https://prts.wiki/w/%E5%89%A7%E6%83%85%E8%A7%92%E8%89%B2%E4%B8%80%E8%A7%88"
        print(f"正在从剧情角色一览页面查找 {character_name}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            html_content = response.read().decode('utf-8')
        
        # 查找所有表格行
        # 使用更通用的模式来匹配表格行
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, html_content, re.DOTALL)
        
        print(f"找到 {len(rows)} 个表格行")
        
        # 使用索引来遍历行，这样可以访问下一行
        for i, row_content in enumerate(rows):
            # 检查这一行是否包含角色名（作为部分匹配）
            if character_name in row_content:
                # 提取所有的td（注意：可能有嵌套的表格）
                # 先尝试简单的td提取
                td_pattern = r'<td[^>]*>(.*?)</td>'
                tds = re.findall(td_pattern, row_content, re.DOTALL)
                
                # 检查第一个td是否包含角色名
                first_td_text = re.sub(r'<[^>]+>', '', tds[0]).strip() if len(tds) > 0 else ""
                
                # 如果第一个td包含角色名（部分匹配）
                if character_name in first_td_text:
                    print(f"找到匹配的角色: {first_td_text}")
                    
                    # 搜索范围：当前行和下一行（有些角色的图片在下一行）
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
                                # 从缩略图URL提取原图URL
                                # 例如: /thumb/c/c9/Avg_avg_npc_893_1-1$1.png/380px-Avg_avg_npc_893_1-1$1.png
                                # 转换为: /c/c9/Avg_avg_npc_893_1-1$1.png
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

def get_special_character_url(character_name):
    """
    获取特殊角色的图片URL
    """
    # 已知的特殊角色图片映射
    special_characters = {
        "塔露拉": "https://media.prts.wiki/2/22/Avg_char_011_talula_1.png",
        # 可以在这里添加更多特殊角色的映射
    }
    
    return special_characters.get(character_name, None)

def download_character_image_api(character_name, save_dir="downloaded_images"):
    """
    通过多种方式下载角色立绘
    
    Args:
        character_name: 角色名称（中文）
        save_dir: 保存图片的目录
        
    Returns:
        bool: 是否成功下载
    """
    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    print(f"正在查询{character_name}的立绘图片...")
    
    # 方法1：检查是否是特殊角色
    image_url = get_special_character_url(character_name)
    if image_url:
        print(f"使用预定义的特殊角色图片URL")
    
    # 方法2：从API获取图片URL
    if not image_url:
        image_url = get_image_url_from_api(character_name)
    
    # 方法3：如果API查询失败，尝试从剧情角色一览页面查找
    if not image_url:
        print("API查询未找到图片，尝试从剧情角色一览页面查找...")
        image_url = get_image_from_story_page(character_name)
    
    # 方法3：如果还是没找到，尝试直接构建URL
    if not image_url:
        print("剧情角色页面也未找到，尝试直接构建URL...")
        
        # 对中文进行URL编码
        encoded_name = urllib.parse.quote(f"立绘_{character_name}_1.png")
        
        # 尝试一些常见的hash前缀（只尝试前20个）
        prefixes = [
            "0/01", "0/02", "0/03", "0/04", "0/05", "0/06", "0/07", "0/08", "0/09", "0/0a",
            "0/0b", "0/0c", "0/0d", "0/0e", "0/0f", "1/10", "1/11", "1/12", "1/13", "1/14",
            "1/15", "1/16", "1/17", "1/18", "1/19", "1/1a", "1/1b", "1/1c", "1/1d", "1/1e"
        ]
        
        for prefix in prefixes:
            url = f"https://media.prts.wiki/{prefix}/{encoded_name}"
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request) as response:
                    if response.getcode() == 200:
                        image_url = url
                        print(f"找到立绘图片: {url}")
                        break
                        
            except urllib.error.HTTPError:
                continue
            except Exception as e:
                print(f"尝试URL {url} 时出错: {e}")
                break
    
    # 如果找到了图片URL，下载它
    if image_url:
        print(f"找到立绘图片: {image_url}")
        
        try:
            # 下载图片
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            request = urllib.request.Request(image_url, headers=headers)
            with urllib.request.urlopen(request) as response:
                image_data = response.read()
            
            # 从URL获取文件扩展名
            file_ext = '.png'  # 默认扩展名
            if '.' in image_url:
                ext = image_url.split('.')[-1].split('?')[0].lower()
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    file_ext = '.' + ext
            
            # 保存图片
            filename = f"{character_name}_立绘{file_ext}"
            save_path = os.path.join(save_dir, filename)
            
            with open(save_path, 'wb') as f:
                f.write(image_data)
            
            print(f"图片已保存到: {save_path}")
            return True
            
        except Exception as e:
            print(f"下载图片时出错: {e}")
    else:
        print(f"未能找到{character_name}的立绘图片")
    
    return False

def main():
    """主函数"""
    # 设置要下载的角色名称列表
    characters = [
        "莱伊",  # 测试剧情角色
        # 可以在这里添加更多角色名
    ]
    
    # 也可以从命令行参数获取角色名
    if len(sys.argv) > 1:
        characters = sys.argv[1:]
    
    # 逐个下载角色立绘
    for character in characters:
        print(f"\n开始处理: {character}")
        download_character_image_api(character)
        # 避免请求过快
        time.sleep(1)
    
    print("\n所有任务完成！")

if __name__ == "__main__":
    main()