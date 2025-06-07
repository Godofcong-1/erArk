#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
遍历data/character目录下的CSV文件，找出包含"通用上衣"的角色并下载其立绘
支持断点续传和批量控制
"""

import os
import sys
import csv
import re
import json
from download_prts_character_image import download_character_image_api
import time

def check_csv_for_keyword(csv_path, keyword="通用上衣"):
    """
    检查CSV文件是否包含指定关键词
    
    Args:
        csv_path: CSV文件路径
        keyword: 要查找的关键词
        
    Returns:
        bool: 是否包含关键词
    """
    try:
        # 尝试不同的编码方式读取CSV
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                with open(csv_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    if keyword in content:
                        return True
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
                
    except Exception as e:
        print(f"读取文件 {csv_path} 时出错: {e}")
    
    return False

def extract_character_name(filename):
    """
    从文件名提取角色名
    
    Args:
        filename: 文件名，如 "0001_阿米娅.csv"
        
    Returns:
        str: 角色名，如 "阿米娅"
    """
    # 移除.csv扩展名
    name = filename.replace('.csv', '')
    
    # 使用正则表达式匹配格式：数字_角色名
    match = re.match(r'^\d+_(.+)$', name)
    if match:
        return match.group(1)
    
    # 如果不匹配标准格式，返回整个名称（去掉数字部分）
    # 处理可能的其他格式
    parts = name.split('_', 1)
    if len(parts) > 1:
        return parts[1]
    
    return name

def load_progress():
    """加载进度文件"""
    progress_file = "download_progress.json"
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "characters_to_download": [],
        "downloaded": [],
        "failed": []
    }

def save_progress(progress):
    """保存进度文件"""
    progress_file = "download_progress.json"
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def retry_failed_downloads(progress, save_dir):
    """重试下载失败的文件"""
    failed_characters = progress["failed"].copy()  # 复制失败列表
    progress["failed"] = []  # 清空失败列表
    
    print(f"\n准备重试 {len(failed_characters)} 个失败的角色...")
    
    # 批量控制
    batch_size = 10  # 每批重试10个
    total_retried = 0
    total_success = 0
    
    for batch_start in range(0, len(failed_characters), batch_size):
        batch_end = min(batch_start + batch_size, len(failed_characters))
        batch = failed_characters[batch_start:batch_end]
        
        print(f"\n处理第 {batch_start+1}-{batch_end} 个（共 {len(failed_characters)} 个）")
        
        for i, character in enumerate(batch):
            current_index = batch_start + i + 1
            print(f"\n[{current_index}/{len(failed_characters)}] 重试: {character}")
            
            # 检查文件是否已存在
            existing_file = os.path.join(save_dir, f"{character}_立绘.png")
            if os.path.exists(existing_file):
                print(f"{character} 文件已存在，标记为已下载")
                progress["downloaded"].append(character)
                total_success += 1
                save_progress(progress)
                continue
            
            try:
                success = False
                # 首先检查是否有新版本的下载脚本
                if os.path.exists("download_prts_character_image_final_v2.py"):
                    try:
                        # 动态导入新版本
                        import importlib.util
                        spec = importlib.util.spec_from_file_location("download_v2", "download_prts_character_image_final_v2.py")
                        if spec and spec.loader:
                            download_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(download_module)
                            success = download_module.download_character_image_api(character, save_dir)
                            print("使用新版本下载函数")
                    except Exception as e:
                        print(f"新版本下载失败: {e}")
                        success = False
                
                # 如果没有新版本或新版本失败，使用旧版本
                if not success:
                    print("使用旧版本下载函数")
                    success = download_character_image_api(character, save_dir)
                
                if success:
                    progress["downloaded"].append(character)
                    total_success += 1
                    print(f"✓ {character} 下载成功！")
                else:
                    progress["failed"].append(character)
                    print(f"✗ {character} 再次失败")
                    
                save_progress(progress)
                total_retried += 1
                
            except Exception as e:
                print(f"下载 {character} 时出错: {e}")
                progress["failed"].append(character)
                save_progress(progress)
                total_retried += 1
            
            # 避免请求过快
            if i < len(batch) - 1:
                time.sleep(2)
        
        # 批次间休息
        if batch_end < len(failed_characters):
            print(f"\n批次完成，休息5秒...")
            time.sleep(5)
    
    # 汇总结果
    print("\n" + "="*50)
    print("重试完成！")
    print(f"重试了 {total_retried} 个角色")
    print(f"成功: {total_success}")
    print(f"仍然失败: {len(progress['failed'])}")
    
    if progress["failed"]:
        print(f"\n仍然失败的角色:")
        for char in progress["failed"]:
            print(f"  - {char}")
        
        # 更新失败文件
        with open('failed_characters.txt', 'w', encoding='utf-8') as f:
            for char in progress["failed"]:
                f.write(char + '\n')
        print("\n失败的角色名已更新到 failed_characters.txt")

def main():
    """主函数"""
    # 设置路径
    character_dir = os.path.join("data", "character")
    save_dir = "downloaded_images_common_clothes"
    
    # 检查目录是否存在
    if not os.path.exists(character_dir):
        print(f"错误：找不到目录 {character_dir}")
        return
    
    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 加载进度
    progress = load_progress()
    
    # 询问是否重试失败的文件
    if progress["failed"] and len(sys.argv) == 1:  # 只在没有命令行参数时询问
        print(f"\n发现 {len(progress['failed'])} 个之前下载失败的角色:")
        for char in progress["failed"][:10]:  # 只显示前10个
            print(f"  - {char}")
        if len(progress["failed"]) > 10:
            print(f"  ... 以及其他 {len(progress['failed']) - 10} 个")
        
        response = input("\n是否要重试下载这些失败的文件？(y/n): ").lower().strip()
        if response == 'y':
            print("\n开始重试失败的文件...")
            retry_failed_downloads(progress, save_dir)
            return
    
    # 如果没有角色列表，则重新扫描
    if not progress["characters_to_download"]:
        # 获取所有CSV文件
        csv_files = [f for f in os.listdir(character_dir) if f.endswith('.csv')]
        print(f"找到 {len(csv_files)} 个CSV文件")
        
        # 找出包含"通用上衣"的角色
        characters_to_download = []
        
        for csv_file in csv_files:
            csv_path = os.path.join(character_dir, csv_file)
            
            if check_csv_for_keyword(csv_path):
                character_name = extract_character_name(csv_file)
                characters_to_download.append(character_name)
                print(f"发现角色 {character_name} 包含'通用上衣'")
        
        progress["characters_to_download"] = characters_to_download
        save_progress(progress)
        print(f"\n总共找到 {len(characters_to_download)} 个包含'通用上衣'的角色")
    else:
        characters_to_download = progress["characters_to_download"]
        print(f"从进度文件加载，总共 {len(characters_to_download)} 个角色")
        print(f"已下载: {len(progress['downloaded'])}")
        print(f"失败: {len(progress['failed'])}")
    
    if not characters_to_download:
        print("没有找到包含'通用上衣'的角色")
        return
    
    # 批量控制
    batch_size = 20  # 每批下载20个
    start_index = len(progress["downloaded"]) + len(progress["failed"])
    
    if start_index >= len(characters_to_download):
        print("所有角色已处理完毕")
        return
    
    end_index = min(start_index + batch_size, len(characters_to_download))
    batch_characters = characters_to_download[start_index:end_index]
    
    # 下载立绘
    print(f"\n开始下载立绘图片... (第 {start_index+1}-{end_index} 个，共 {len(characters_to_download)} 个)")
    
    for i, character in enumerate(batch_characters):
        current_index = start_index + i + 1
        print(f"\n[{current_index}/{len(characters_to_download)}] 正在处理: {character}")
        
        # 跳过已下载的
        if character in progress["downloaded"]:
            print(f"{character} 已下载，跳过")
            continue
        
        # 检查文件是否已存在
        existing_file = os.path.join(save_dir, f"{character}_立绘.png")
        if os.path.exists(existing_file):
            print(f"{character} 文件已存在，标记为已下载")
            progress["downloaded"].append(character)
            save_progress(progress)
            continue
        
        try:
            if download_character_image_api(character, save_dir):
                progress["downloaded"].append(character)
            else:
                progress["failed"].append(character)
            save_progress(progress)
        except Exception as e:
            print(f"下载 {character} 时出错: {e}")
            progress["failed"].append(character)
            save_progress(progress)
        
        # 避免请求过快
        if i < len(batch_characters) - 1:
            time.sleep(2)
    
    # 汇总当前批次结果
    print("\n" + "="*50)
    print(f"当前批次完成！")
    print(f"总进度: {len(progress['downloaded'])}/{len(characters_to_download)} 成功")
    print(f"失败: {len(progress['failed'])}")
    
    remaining = len(characters_to_download) - len(progress["downloaded"]) - len(progress["failed"])
    if remaining > 0:
        print(f"\n还剩 {remaining} 个角色待下载")
        print("请再次运行脚本继续下载下一批")
    else:
        print("\n所有角色处理完毕！")
        
        if progress["failed"]:
            print(f"\n下载失败的角色 ({len(progress['failed'])}个):")
            for char in progress["failed"]:
                print(f"  - {char}")
            
            # 将失败的角色名保存到文件
            with open('failed_characters.txt', 'w', encoding='utf-8') as f:
                for char in progress["failed"]:
                    f.write(char + '\n')
            print("\n失败的角色名已保存到 failed_characters.txt")

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--retry":
        # 直接执行重试
        progress = load_progress()
        if progress["failed"]:
            save_dir = "downloaded_images_common_clothes"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            print(f"准备重试 {len(progress['failed'])} 个失败的文件...")
            retry_failed_downloads(progress, save_dir)
        else:
            print("没有失败的文件需要重试")
    else:
        main()