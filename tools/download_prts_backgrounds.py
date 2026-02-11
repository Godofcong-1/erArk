"""
PRTS Wiki 场景背景图片下载脚本
从 https://prts.wiki/w/剧情资源概览/背景 下载所有场景图片到 image/全场景 目录
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from pathlib import Path


def download_prts_backgrounds():
    """
    从 PRTS Wiki 下载所有场景背景图片
    
    Keyword arguments:
    无
    
    Return arguments:
    无
    """
    # 目标 URL
    url = "https://prts.wiki/w/剧情资源概览/背景"
    
    # 输出目录
    output_dir = Path("image/全场景")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 请求头，模拟浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"正在访问: {url}")
    
    try:
        # 获取网页内容
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有图片标签
        # PRTS Wiki 通常使用 <img> 标签或 <a> 标签链接到图片
        image_urls = set()
        
        # 方法1: 查找所有 img 标签
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                # 转换为完整 URL
                full_url = urljoin(url, src)
                # 过滤出背景图片（通常包含特定路径或尺寸）
                if any(keyword in full_url.lower() for keyword in ['bg_', 'background', '背景', '/thumb/']):
                    # 尝试获取原图链接（去除缩略图尺寸）
                    original_url = re.sub(r'/thumb(/.*?)/\d+px-.*?$', r'\1', full_url)
                    image_urls.add(original_url if original_url != full_url else full_url)
        
        # 方法2: 查找链接到图片文件的 a 标签
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(ext in href.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                full_url = urljoin(url, href)
                image_urls.add(full_url)
        
        # 方法3: 查找 gallery 类或特定的容器
        galleries = soup.find_all(['div', 'ul'], class_=re.compile(r'gallery|mw-gallery'))
        for gallery in galleries:
            for img in gallery.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(url, src)
                    original_url = re.sub(r'/thumb(/.*?)/\d+px-.*?$', r'\1', full_url)
                    image_urls.add(original_url if original_url != full_url else full_url)
        
        print(f"找到 {len(image_urls)} 个图片链接")
        
        # 下载所有图片
        success_count = 0
        fail_count = 0
        
        for idx, img_url in enumerate(image_urls, 1):
            try:
                # 从 URL 中提取文件名
                filename = unquote(img_url.split('/')[-1])
                # 清理文件名中的非法字符
                filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                
                # 如果没有扩展名，尝试从 URL 推断
                if '.' not in filename:
                    filename += '.png'
                
                filepath = output_dir / filename
                
                # 如果文件已存在，跳过
                if filepath.exists():
                    print(f"[{idx}/{len(image_urls)}] 跳过已存在: {filename}")
                    success_count += 1
                    continue
                
                print(f"[{idx}/{len(image_urls)}] 下载: {filename}")
                
                # 下载图片
                img_response = requests.get(img_url, headers=headers, timeout=30)
                img_response.raise_for_status()
                
                # 保存图片
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"  ✓ 保存成功: {filepath}")
                success_count += 1
                
                # 礼貌性延迟，避免请求过快
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ✗ 下载失败: {img_url}")
                print(f"    错误: {e}")
                fail_count += 1
                continue
        
        print("\n" + "="*60)
        print(f"下载完成！")
        print(f"成功: {success_count} 个")
        print(f"失败: {fail_count} 个")
        print(f"保存位置: {output_dir.absolute()}")
        print("="*60)
        
    except Exception as e:
        print(f"错误: 无法访问网页")
        print(f"详细信息: {e}")
        return


if __name__ == "__main__":
    download_prts_backgrounds()
