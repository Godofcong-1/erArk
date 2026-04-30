#!/usr/bin/env python3
"""
处理 data/character 目录下的角色 CSV 文件：

功能概要：
- 遍历指定目录下所有以 .csv 结尾的文件。
- 对于每个非空 CSV 文件，检查是否已经包含字段标识 'T|2,int'：
  - 若已包含则跳过该文件（认为已存在需要的条目）。
  - 若未包含，则查找文件中第一处包含 'T|1,int' 的行，
    在该行之后插入两行新的字段定义：
      T|2,int,1,0,角色有尿道处女素质
      T|3,int,1,0,角色有子宫处女素质

命令行用法：
  python tools/process_character_csvs.py          # 仅预览（dry-run），在控制台打印将被修改的文件及 diff
  python tools/process_character_csvs.py --apply  # 真正写入修改，并为每个被修改的文件创建 .bak 备份

实现注意事项与约束：
- 脚本跳过空文件和非 .csv 文件。
- 修改时会先创建备份文件（在源文件名后追加 .bak）。

代码结构说明（高层次）:
- INSERT_LINES: 要插入的行列表（常量）
- process_file(path, apply): 处理单个文件的函数，返回该文件是否会/已被修改（bool）
- main(): 解析命令行参数并遍历目录，统计并打印处理结果

所有打印输出和错误提示均使用中文，方便本地化维护。
"""

import argparse
from pathlib import Path
import difflib
import shutil
import sys


# 要插入到 CSV 中的行（常量）
INSERT_LINES = [
    'T|2,int,1,0,角色有尿道处女素质',
    'T|3,int,1,0,角色有子宫处女素质',
]


def process_file(path: Path, apply: bool = False) -> bool:
    """
    处理单个 CSV 文件。

    参数:
      path: 要处理的文件路径（Path 对象），应为以 .csv 结尾的文件。
      apply: 布尔值，False 时仅进行预览（不写入），True 时写入修改并创建备份（.bak）。

    返回值:
      True - 文件将被或已经被修改（包括 dry-run 显示修改）。
      False - 文件无需修改（例如已包含 T|2,int，或没有找到 T|1,int，或文件为空）。

    实现细节:
    - 以 utf-8 编码读取文件内容，按行拆分为列表进行查找与插入操作。
    - 若文件最后一行以换行符结束，会在写回时保留末尾换行符，否则不添加额外换行。
    - dry-run 模式下会打印 unified diff，便于人工审阅。
    """

    # 以 utf-8 读取文件内容
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()

    # 空文件直接跳过
    if not lines:
        return False

    # 如果任意行包含 'T|2,int'，认为文件已包含目标字段，跳过
    if any('T|2,int' in ln for ln in lines):
        return False

    # 查找第一处包含 'T|1,int' 的行，并在其下一行处插入
    insert_idx = None
    for i, ln in enumerate(lines):
        if 'T|1,int' in ln:
            insert_idx = i + 1
            break

    # 如果没有找到 'T|1,int'，则不做修改
    if insert_idx is None:
        return False

    # 生成新的行列表并构建新的文本内容，注意保留原文件末尾是否有换行符的语义
    new_lines = lines[:insert_idx] + INSERT_LINES + lines[insert_idx:]
    new_text = '\n'.join(new_lines) + ('\n' if text.endswith('\n') else '')

    # 生成 diff，便于 dry-run 时输出查看改动
    diff = ''.join(difflib.unified_diff(lines, new_lines, fromfile=str(path), tofile=str(path) + ' (new)', lineterm=''))

    if apply:
        # 备份原文件（在原后追加 .bak）并写入新内容
        bak = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, bak)
        path.write_text(new_text, encoding='utf-8')
        print(f'已应用更改: {path} (备份文件: {bak})')
    else:
        # dry-run：打印将被修改的文件路径与 diff
        print(f'将会修改: {path}')
        print(diff)

    return True


def main():
    """
    脚本入口：解析命令行参数并遍历目标目录进行批量处理。

    命令行参数：
      --apply: 实际写入更改并创建备份；不加该参数时为 dry-run，仅打印会做的改动。
      --dir: 目标目录（默认为 'data/character'），可指定为其他路径以便测试。
    """

    parser = argparse.ArgumentParser(description='处理角色 CSV，向缺失的文件插入指定字段（支持 dry-run 与 apply 模式）')
    parser.add_argument('--apply', action='store_true', help='实际写入更改（并创建 .bak 备份）。')
    parser.add_argument('--dir', default='data/character', help="要处理的目录（默认：data/character）")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.exists() or not root.is_dir():
        # 使用中文错误提示并返回错误码
        print(f'目录未找到：{root}', file=sys.stderr)
        sys.exit(2)

    changed = []
    # 遍历目录下所有 .csv 文件（按字母序），并处理
    for p in sorted(root.glob('*.csv')):
        try:
            modified = process_file(p, apply=args.apply)
            if modified:
                changed.append(p)
        except Exception as e:
            # 捕获并以中文打印处理单个文件时的异常，继续下一个文件
            print(f'处理文件 {p} 时发生错误：{e}', file=sys.stderr)

    # 汇总输出处理结果（中文）
    print('\n处理摘要：')
    if changed:
        print(f'已修改或将要修改的文件数量：{len(changed)}')
        for p in changed:
            print(' -', p)
    else:
        print('无需修改的文件数量：0（未发现需要插入字段的 CSV）')


if __name__ == '__main__':
    main()
