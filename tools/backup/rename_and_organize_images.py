# -*- coding: utf-8 -*-
"""
重命名和整理图片脚本
1. 将原始半身图重命名为 {角色名}_半身.png
2. 下载全身图并命名为 {角色名}_全身.png
3. 生成头部图片（待扩展）

用法：python rename_and_organize_images.py
"""

import os
import sys
import time
from pathlib import Path


# 路径配置
DIFF_DIR = "image/立绘/干员/差分"


def rename_half_body_images():
    """
    重命名半身图
    在每个角色文件夹中找到不含下划线的png文件，重命名为 {角色名}_半身.png
    """
    print("=" * 50)
    print("开始重命名半身图...")
    print("=" * 50)
    
    diff_path = Path(DIFF_DIR)
    if not diff_path.exists():
        print(f"差分目录 {DIFF_DIR} 不存在")
        return
    
    folders = [f for f in diff_path.iterdir() if f.is_dir()]
    print(f"找到 {len(folders)} 个角色文件夹")
    
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    for folder in folders:
        character_name = folder.name
        
        # 跳过特殊文件夹
        if character_name.startswith('.') or character_name == '__pycache__':
            continue
        
        # 检查是否已有半身图
        half_body_path = folder / f"{character_name}_半身.png"
        if half_body_path.exists():
            skipped_count += 1
            continue
        
        # 查找不含下划线的png文件（原始半身图）
        original_files = [f for f in folder.glob("*.png") if '_' not in f.stem]
        
        if not original_files:
            # 可能原始文件已经被重命名过
            continue
        
        if len(original_files) > 1:
            print(f"  [警告] {character_name} - 发现多个原始文件: {[f.name for f in original_files]}")
        
        original_file = original_files[0]
        
        try:
            # 重命名
            original_file.rename(half_body_path)
            print(f"  [完成] {character_name}: {original_file.name} -> {half_body_path.name}")
            renamed_count += 1
        except Exception as e:
            print(f"  [错误] {character_name} - {str(e)}")
            error_count += 1
    
    print("=" * 50)
    print(f"重命名完成！")
    print(f"  重命名文件: {renamed_count}")
    print(f"  跳过文件: {skipped_count}")
    print(f"  错误数量: {error_count}")
    print("=" * 50)


def download_full_body_images():
    """
    下载全身图
    使用 download_prts_character_image.py 脚本下载
    """
    print("=" * 50)
    print("开始下载全身图...")
    print("=" * 50)
    
    diff_path = Path(DIFF_DIR)
    if not diff_path.exists():
        print(f"差分目录 {DIFF_DIR} 不存在")
        return
    
    folders = [f for f in diff_path.iterdir() if f.is_dir()]
    
    need_download = []
    for folder in folders:
        character_name = folder.name
        
        # 跳过特殊文件夹
        if character_name.startswith('.') or character_name == '__pycache__':
            continue
        
        # 检查是否已有全身图
        full_body_path = folder / f"{character_name}_全身.png"
        if not full_body_path.exists():
            need_download.append(character_name)
    
    print(f"需要下载全身图的角色: {len(need_download)}")
    
    if not need_download:
        print("所有角色都已有全身图")
        return
    
    # 尝试导入下载脚本
    try:
        # 添加tools目录到路径
        tools_dir = Path(__file__).parent
        sys.path.insert(0, str(tools_dir))
        
        from download_prts_character_image import download_character_image_api
        
        downloaded_count = 0
        error_count = 0
        skipped_count = 0
        
        for character_name in need_download:
            print(f"  正在下载: {character_name}")
            try:
                # 下载全身图到临时目录
                temp_dir = "temp_download"
                result = download_character_image_api(character_name, temp_dir)
                if result:
                    # 查找下载的图片
                    temp_path = Path(temp_dir)
                    downloaded_files = list(temp_path.glob(f"*{character_name}*.png"))
                    if downloaded_files:
                        source_file = downloaded_files[0]
                        target_path = Path(DIFF_DIR) / character_name / f"{character_name}_全身.png"
                        # 确保目标目录存在
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        import shutil
                        shutil.move(str(source_file), str(target_path))
                        print(f"    [完成] 已保存到 {target_path}")
                        downloaded_count += 1
                    else:
                        print(f"    [警告] 下载成功但未找到图片文件")
                        skipped_count += 1
                else:
                    print(f"    [跳过] 未能下载")
                    skipped_count += 1
            except Exception as e:
                print(f"    [错误] {str(e)}")
                error_count += 1
            
            # 添加延迟避免被限流
            time.sleep(0.5)
        
        print(f"下载完成: {downloaded_count} 成功, {skipped_count} 跳过, {error_count} 失败")
        
    except ImportError as e:
        print(f"无法导入下载脚本: {e}")
        print("请确保 download_prts_character_image.py 存在于 tools 目录中")


def check_image_status():
    """
    检查图片状态
    """
    print("=" * 50)
    print("检查图片状态...")
    print("=" * 50)
    
    diff_path = Path(DIFF_DIR)
    if not diff_path.exists():
        print(f"差分目录 {DIFF_DIR} 不存在")
        return
    
    folders = [f for f in diff_path.iterdir() if f.is_dir()]
    
    stats = {
        "total": 0,
        "has_half_body": 0,
        "has_full_body": 0,
        "has_head": 0,
        "has_body_parts_json": 0
    }
    
    for folder in folders:
        character_name = folder.name
        
        # 跳过特殊文件夹
        if character_name.startswith('.') or character_name == '__pycache__':
            continue
        
        stats["total"] += 1
        
        if (folder / f"{character_name}_半身.png").exists():
            stats["has_half_body"] += 1
        
        if (folder / f"{character_name}_全身.png").exists():
            stats["has_full_body"] += 1
        
        if (folder / f"{character_name}_头部.png").exists():
            stats["has_head"] += 1
        
        if (folder / "body_parts.json").exists():
            stats["has_body_parts_json"] += 1
    
    print(f"角色总数: {stats['total']}")
    print(f"有半身图: {stats['has_half_body']} ({stats['has_half_body']*100//stats['total'] if stats['total'] else 0}%)")
    print(f"有全身图: {stats['has_full_body']} ({stats['has_full_body']*100//stats['total'] if stats['total'] else 0}%)")
    print(f"有头部图: {stats['has_head']} ({stats['has_head']*100//stats['total'] if stats['total'] else 0}%)")
    print(f"有部位JSON: {stats['has_body_parts_json']} ({stats['has_body_parts_json']*100//stats['total'] if stats['total'] else 0}%)")


if __name__ == "__main__":
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"工作目录: {os.getcwd()}")
    print()
    
    # 检查状态
    check_image_status()
    print()
    
    # 重命名半身图
    rename_half_body_images()
    print()
    
    # 下载全身图（可选，取消注释以启用）
    # download_full_body_images()
