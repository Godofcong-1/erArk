#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明日方舟活动剧情下载器 - 增强版
功能：支持多种活动剧情格式的自适应下载器
"""

import requests
import re
import os
import time
from urllib.parse import quote
from bs4 import BeautifulSoup


def get_activity_story_list_enhanced(activity_name):
    """
    获取活动的所有剧情列表（增强版，支持多种格式）
    参数:
        activity_name (str): 活动名称，如"将进酒"、"画中人"
    返回值:
        list: 剧情信息列表，每个元素为(display_name, full_url, story_code, story_name, story_type)元组
    功能描述:
        从剧情一览页面获取指定活动的所有剧情条目，支持多种不同的格式
    """
    # 构造剧情一览页面URL
    url = "https://prts.wiki/w/剧情一览"
    
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        print(f"正在获取活动 '{activity_name}' 的剧情列表...")
        
        # 发送HTTP请求获取页面内容
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含活动名称的文本
        page_text = soup.get_text()
        
        # 使用正则表达式查找活动相关的剧情条目
        pattern = rf"{re.escape(activity_name)}.*?支线\s+(.*?)(?=\n\n|\n[^I\s]|$)"
        
        match = re.search(pattern, page_text, re.DOTALL)
        
        if not match:
            print(f"✗ 未找到活动 '{activity_name}' 的剧情信息")
            return []
        
        # 提取剧情条目文本
        story_text = match.group(1)
        print(f"✓ 找到剧情文本块，长度: {len(story_text)} 字符")
        print(f"文本内容预览: {story_text[:100]}...")
        
        # 尝试多种解析方法
        stories = []
        
        # 方法1: 按·分隔符分割（适用于将进酒等活动）
        if '·' in story_text:
            print("✓ 使用·分隔符解析")
            story_items = [item.strip() for item in story_text.split('·') if item.strip()]
            
            for item in story_items:
                # 匹配剧情代码和名称
                item_match = re.match(r'([A-Z]{2,3}-[A-Z0-9-]+)\s+(.+)', item.strip())
                if item_match:
                    story_code = item_match.group(1)
                    full_name = item_match.group(2).strip()
                    
                    # 判断剧情类型和构造URL
                    story_info = parse_story_info(story_code, full_name)
                    if story_info:
                        stories.append(story_info)
                        print(f"  ✓ 解析: {story_info[0]}")
        
        # 方法2: 使用正则表达式直接匹配（适用于其他格式）
        if not stories:
            print("✓ 使用正则表达式匹配")
            
            # 尝试多种剧情代码格式
            code_patterns = [
                r'([A-Z]{2,3}-[A-Z0-9-]+)\s+([^\n·]+?)(?=\s+[A-Z]{2,3}-[A-Z0-9-]+|·|\n|$)',
                r'([A-Z]+-[A-Z0-9-]+)\s+([^·\n]+)',
                r'([A-Z]{2}-[A-Z0-9-]+)\s+([^·\n]+)',
            ]
            
            for pattern in code_patterns:
                matches = re.findall(pattern, story_text)
                if matches:
                    print(f"  使用模式匹配到 {len(matches)} 个剧情")
                    
                    for code, name in matches:
                        story_info = parse_story_info(code.strip(), name.strip())
                        if story_info:
                            stories.append(story_info)
                            print(f"    ✓ 解析: {story_info[0]}")
                    break
        
        # 方法3: 按行分割解析（备用方法）
        if not stories:
            print("✓ 使用行分割解析")
            lines = [line.strip() for line in story_text.split('\n') if line.strip()]
            
            for line in lines:
                # 查找包含剧情代码的行
                code_match = re.search(r'([A-Z]{2,3}-[A-Z0-9-]+)', line)
                if code_match:
                    story_code = code_match.group(1)
                    # 提取剧情名称（去掉代码部分）
                    story_name = re.sub(r'[A-Z]{2,3}-[A-Z0-9-]+\s*', '', line).strip()
                    
                    if story_name:
                        story_info = parse_story_info(story_code, story_name)
                        if story_info:
                            stories.append(story_info)
                            print(f"  ✓ 解析: {story_info[0]}")
        
        print(f"成功解析 {len(stories)} 个剧情")
        return stories
        
    except Exception as e:
        print(f"获取剧情列表失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return []


def parse_story_info(story_code, full_name):
    """
    解析剧情信息
    参数:
        story_code (str): 剧情代码，如IW-ST-1
        full_name (str): 完整名称，可能包含行动前/行动后标识
    返回值:
        tuple: (display_name, full_url, story_code, story_name, story_type)元组，失败返回None
    功能描述:
        解析剧情代码和名称，确定剧情类型并构造访问URL
    """
    try:
        # 判断剧情类型
        if '行动前' in full_name:
            story_type = "行动前"
            url_suffix = "BEG"
            story_name = re.sub(r'\s*行动前\s*', '', full_name).strip()
        elif '行动后' in full_name:
            story_type = "行动后"
            url_suffix = "END"
            story_name = re.sub(r'\s*行动后\s*', '', full_name).strip()
        else:
            story_type = "主线"
            url_suffix = "NBT"
            story_name = full_name
        
        # 清理剧情名称，移除多余的标点符号
        story_name = story_name.strip('·、，。；')
        
        if not story_name:
            return None
        
        # 构造URL
        page_name = f"{story_code}_{story_name}"
        full_url = f"https://prts.wiki/w/{quote(page_name)}/{url_suffix}"
        
        # 构造显示名称
        display_name = f"{story_code} {story_name} ({story_type})"
        
        return (display_name, full_url, story_code, story_name, story_type)
        
    except Exception as e:
        print(f"解析剧情信息失败: {story_code} {full_name} - {e}")
        return None


def extract_story_script_from_url(url, story_name):
    """
    从URL提取剧情脚本
    参数:
        url (str): 剧情页面URL
        story_name (str): 剧情名称，用于显示
    返回值:
        str: 提取的剧情脚本内容，失败返回None
    功能描述:
        从PRTS剧情页面的JavaScript中提取完整的剧情脚本内容
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # 获取页面内容
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"    ✗ 页面访问失败，状态码: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有script标签
        scripts = soup.find_all('script')
        
        # 查找包含剧情脚本的标签
        for i, script in enumerate(scripts):
            if not script.string:
                continue
            
            script_content = script.string.strip()
            
            # 检查脚本是否包含剧情标记
            story_markers = [
                '[HEADER', '[Dialog]', '[Character', '[Background', 
                '[playMusic', '[Subtitle', '[name=', '[Blocker'
            ]
            
            marker_count = sum(1 for marker in story_markers if marker in script_content)
            
            # 如果包含足够多的剧情标记（至少5个）
            if marker_count >= 5:
                print(f"    ✓ 找到剧情脚本 (标记数: {marker_count}，长度: {len(script_content)} 字符)")
                
                # 尝试提取纯剧情脚本部分
                cleaned_script = extract_pure_story_script(script_content)
                
                if cleaned_script:
                    return cleaned_script
                else:
                    return script_content
        
        print(f"    ✗ 未找到剧情脚本内容")
        return None
        
    except Exception as e:
        print(f"    ✗ 提取失败: {e}")
        return None


def extract_pure_story_script(script_content):
    """
    从JavaScript代码中提取纯剧情脚本
    参数:
        script_content (str): JavaScript脚本内容
    返回值:
        str: 纯剧情脚本内容，失败返回None
    功能描述:
        从包含JavaScript代码的脚本中提取出纯粹的剧情脚本部分
    """
    # 方法1: 如果脚本主要就是剧情内容（以剧情标记开头）
    if script_content.strip().startswith('[HEADER'):
        return script_content.strip()
    
    # 方法2: 查找被引号包围的剧情脚本
    quote_patterns = [
        r'["\']([^"\']*\[HEADER[^"\']*)["\']',  # 单/双引号包围的内容
        r'`([^`]*\[HEADER[^`]*)`',  # 反引号包围的内容
    ]
    
    for pattern in quote_patterns:
        matches = re.findall(pattern, script_content, re.DOTALL)
        for match in matches:
            if len(match) > 1000 and '[Dialog]' in match:  # 确保是完整的剧情
                # 处理转义字符
                cleaned = match.replace('\\n', '\n').replace('\\r', '\r').replace('\\"', '"').replace("\\'", "'")
                return cleaned
    
    # 方法3: 查找多行的剧情脚本块
    script_block_patterns = [
        r'(\[HEADER.*?)(?=function|\n\s*function|\n\s*var|\n\s*const|\n\s*let|$)',
        r'(\[HEADER.*?)(?=\n\s*\}|\n\s*\);|$)',
    ]
    
    for pattern in script_block_patterns:
        matches = re.findall(pattern, script_content, re.DOTALL)
        for match in matches:
            if len(match) > 1000:
                return match.strip()
    
    # 方法4: 如果脚本很短且主要是剧情内容，进行简单清理后返回
    if len(script_content) < 50000 and '[Dialog]' in script_content:
        # 移除明显的JavaScript代码行
        lines = script_content.split('\n')
        story_lines = []
        
        for line in lines:
            line = line.strip()
            # 跳过明显的JavaScript代码行
            if (line.startswith('var ') or line.startswith('function ') or 
                line.startswith('const ') or line.startswith('let ') or
                line.startswith('//') or line == '{' or line == '}' or
                line.startswith('if ') or line.startswith('for ') or
                line.startswith('while ') or not line):
                continue
            story_lines.append(line)
        
        if story_lines and len('\n'.join(story_lines)) > 1000:
            return '\n'.join(story_lines)
    
    return None


def save_story_script(story_code, story_name, story_type, script_content, output_dir):
    """
    保存剧情脚本到文件
    参数:
        story_code (str): 剧情代码，如IW-ST-1
        story_name (str): 剧情名称，如客将至
        story_type (str): 剧情类型，如主线、行动前、行动后
        script_content (str): 剧情脚本内容
        output_dir (str): 输出目录
    返回值:
        bool: 保存成功返回True，失败返回False
    功能描述:
        将剧情脚本保存为txt文件，文件名包含剧情代码、名称和类型
    """
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 构造安全的文件名
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', story_name)
        
        # 根据类型添加后缀
        type_suffix = {
            '主线': '',
            '行动前': '_行动前',
            '行动后': '_行动后',
            '其他': '_其他'
        }.get(story_type, f'_{story_type}')
        
        filename = f"{story_code}_{safe_name}{type_suffix}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"剧情: {story_code} {story_name} ({story_type})\n")
            f.write("=" * 70 + "\n\n")
            f.write(script_content)
        
        print(f"    ✓ 已保存: {filename}")
        return True
        
    except Exception as e:
        print(f"    ✗ 保存失败: {e}")
        return False


def download_activity_stories_enhanced(activity_name, output_dir=None):
    """
    下载指定活动的所有剧情（增强版）
    参数:
        activity_name (str): 活动名称
        output_dir (str): 输出目录，默认为活动名称
    返回值:
        tuple: (成功数量, 总数量)
    功能描述:
        下载指定活动的所有剧情脚本文件到本地，支持多种格式
    """
    # 设置默认输出目录
    if output_dir is None:
        output_dir = activity_name
    
    print(f"开始下载活动 '{activity_name}' 的剧情脚本...")
    
    # 获取剧情列表
    stories = get_activity_story_list_enhanced(activity_name)
    
    if not stories:
        print("未找到任何剧情，请检查活动名称是否正确")
        return 0, 0
    
    # 显示找到的剧情列表
    print(f"\n找到以下剧情:")
    print("-" * 80)
    for i, (display_name, _, _, _, _) in enumerate(stories, 1):
        print(f"{i:2d}. {display_name}")
    print("-" * 80)
    
    # 询问用户是否继续
    while True:
        confirm = input(f"\n是否开始下载这 {len(stories)} 个剧情？(y/n): ").strip().lower()
        if confirm in ['y', 'yes', '是', '']:
            break
        elif confirm in ['n', 'no', '否']:
            print("取消下载")
            return 0, 0
        else:
            print("请输入 y 或 n")
    
    # 下载每个剧情
    success_count = 0
    total_count = len(stories)
    
    for i, (display_name, url, story_code, story_name, story_type) in enumerate(stories, 1):
        print(f"\n[{i}/{total_count}] 正在下载: {display_name}")
        
        # 下载剧情脚本
        script_content = extract_story_script_from_url(url, display_name)
        
        if script_content:
            # 保存到文件
            if save_story_script(story_code, story_name, story_type, script_content, output_dir):
                success_count += 1
                
                # 显示内容预览
                preview_length = 150
                if len(script_content) > preview_length:
                    preview = script_content[:preview_length] + "..."
                else:
                    preview = script_content
                print(f"    内容预览: {preview}")
        
        # 添加延时避免请求过快
        if i < total_count:
            time.sleep(2)
    
    print(f"\n{'='*80}")
    print(f"下载完成！成功: {success_count}/{total_count}")
    
    if success_count > 0:
        print(f"所有文件已保存到目录: {output_dir}")
    
    return success_count, total_count


def main():
    """
    主函数
    功能描述:
        程序入口点，处理用户输入并执行下载任务
    """
    print("明日方舟活动剧情下载器")
    print("=" * 50)
    print("功能：支持多种活动剧情格式的自适应下载")
    print("=" * 50)
    
    # 获取用户输入
    while True:
        activity_name = input("\n请输入活动名称（如：将进酒、画中人）: ").strip()
        
        if activity_name:
            break
        else:
            print("活动名称不能为空，请重新输入")
    
    # 可选：自定义输出目录
    output_dir = input("请输入输出目录（留空使用活动名称）: ").strip()
    
    if not output_dir:
        output_dir = activity_name
    
    # 执行下载
    try:
        success, total = download_activity_stories_enhanced(activity_name, output_dir)
        
        if success > 0:
            print(f"\n✓ 下载成功！共下载了 {success} 个剧情脚本")
            print(f"文件保存位置: {os.path.abspath(output_dir)}")
            
            # 显示下载的文件列表
            if os.path.exists(output_dir):
                files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
                if files:
                    print(f"\n已下载的文件:")
                    for i, filename in enumerate(sorted(files), 1):
                        print(f"  {i}. {filename}")
        else:
            print(f"\n✗ 下载失败，请检查:")
            print("  1. 网络连接是否正常")
            print("  2. 活动名称是否正确")
            print("  3. PRTS网站是否可以正常访问")
        
    except KeyboardInterrupt:
        print("\n\n用户取消下载")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        print("请检查网络连接和输入参数")


if __name__ == "__main__":
    main()