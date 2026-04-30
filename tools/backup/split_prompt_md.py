"""
MD提示词文件拆分工具

功能：将包含多个分支内容的MD提示词文件拆分成若干个单文件
输入：
    - 提示词md文件路径
    - 输出目录（可选，默认为md文件同目录）
输出：
    - 在输出目录下创建新文件夹
    - 文件夹里包含若干个md文件，每个文件对应一个分支

使用示例：
    python split_prompt_md.py .github/prompts/角色素质/指令前提分支_全陷落(带陌生).md
    python split_prompt_md.py .github/prompts/角色素质/指令前提分支_全陷落(带陌生).md --output ./output
"""

import argparse
import re
from pathlib import Path


def get_header_level(line):
    """
    获取标题的层级（#的数量）
    
    输入：
        line: 一行文本
    输出：
        int: 标题层级（如## 返回2），非标题返回0
    """
    if not line.startswith('#'):
        return 0
    match = re.match(r'^(#{1,6})\s', line)
    if match:
        return len(match.group(1))
    return 0


def parse_md_file(file_path):
    """
    解析MD文件，提取文件头和各个分支内容
    
    输入：
        file_path: MD文件路径
    输出：
        dict: {
            'header': 文件头内容（包括一级标题和总体说明）,
            'split_level': 最次级标题层级,
            'sections': [
                {
                    'name': 分支名,
                    'content': 完整内容
                }
            ]
        }
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # 找到所有标题及其层级（排除一级标题）
    header_levels = []
    for line in lines:
        level = get_header_level(line)
        if level > 1:  # 忽略一级标题
            header_levels.append(level)
    
    if not header_levels:
        print("警告：未找到二级及以下标题，无法拆分")
        return None
    
    # 确定最次级标题层级（最大的层级数）
    split_level = max(header_levels)
    print(f"识别到最次级标题层级: {split_level} 级")
    
    result = {
        'header': '',
        'split_level': split_level,
        'sections': []
    }
    
    # 找到第一个非一级标题之前的部分作为header
    header_lines = []
    content_start = 0
    
    for i, line in enumerate(lines):
        level = get_header_level(line)
        if level > 1:  # 遇到第一个非一级标题
            content_start = i
            break
        header_lines.append(line)
    
    result['header'] = '\n'.join(header_lines).strip()
    
    # 解析各个section（以最次级标题为分割）
    current_section = None
    current_section_lines = []
    
    for i in range(content_start, len(lines)):
        line = lines[i]
        level = get_header_level(line)
        
        # 遇到最次级标题，开始新section
        if level == split_level:
            # 保存之前的section
            if current_section:
                current_section['content'] = '\n'.join(current_section_lines).strip()
                result['sections'].append(current_section)
            
            # 创建新section
            section_name = line.lstrip('#').strip()
            current_section = {
                'name': section_name,
                'content': ''
            }
            current_section_lines = [line]
        
        # 收集section内容
        elif current_section:
            current_section_lines.append(line)
    
    # 保存最后一个section
    if current_section:
        current_section['content'] = '\n'.join(current_section_lines).strip()
        result['sections'].append(current_section)
    
    return result


def sanitize_filename(name):
    """
    清理文件名，移除不合法字符
    
    输入：
        name: 原始名称
    输出：
        str: 清理后的文件名
    """
    # 移除或替换不合法字符
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 移除首尾空格
    name = name.strip()
    # 如果文件名过长，截断
    if len(name) > 100:
        name = name[:100]
    return name


def split_md_file(input_file, output_dir=None):
    """
    拆分MD文件到多个单文件
    
    输入：
        input_file: 输入MD文件路径
        output_dir: 输出目录（可选）
    输出：
        None（在文件系统中创建文件）
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"错误：文件不存在 - {input_file}")
        return
    
    # 确定输出目录
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
    
    # 创建输出子目录（以原文件名命名，去掉.md扩展名）
    base_name = input_path.stem
    output_folder = output_dir / base_name
    output_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"解析文件: {input_file}")
    parsed = parse_md_file(input_file)
    
    if not parsed:
        return
    
    print(f"输出目录: {output_folder}")
    
    total_files = 0
    
    # 为每个section创建单独的文件
    for section in parsed['sections']:
        section_name = section['name']
        
        # 构造文件内容：header + section content
        file_content = parsed['header'] + '\n\n' + section['content']
        
        # 生成文件名
        filename = sanitize_filename(section_name) + '.md'
        file_path = output_folder / filename
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"  创建文件: {filename}")
        total_files += 1
    
    print(f"\n完成！共生成 {total_files} 个文件")
    print(f"输出位置: {output_folder.absolute()}")


def main():
    """
    主函数，处理命令行参数
    """
    parser = argparse.ArgumentParser(
        description='将MD提示词文件拆分成多个单文件（自动识别最次级标题层级）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python split_prompt_md.py .github/prompts/角色素质/指令前提分支_全陷落(带陌生).md
  python split_prompt_md.py input.md --output ./output
        """
    )
    
    parser.add_argument(
        'input_file',
        help='输入的MD提示词文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出目录（可选，默认为输入文件同目录）',
        default=None
    )
    
    args = parser.parse_args()
    
    split_md_file(args.input_file, args.output)


if __name__ == '__main__':
    main()
