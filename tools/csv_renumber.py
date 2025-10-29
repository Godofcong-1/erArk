# -*- coding: utf-8 -*-
"""
输入类型 / 输出类型 / 功能：
- 输入类型：命令行参数（CSV 文件路径: str，起始编号: int，起始行: int=6，列号: int=1 等）
- 输出类型：无返回值；直接覆盖写回 CSV 原文件（默认先生成 .bak 备份）
- 功能：从指定起始行开始，将 CSV 第一列（或指定列）的值依次改写为给定起始编号并逐行 +1。

注意：
- 默认从第 6 行开始修改（包含标题/类型/示例等行的 CSV 场景）
- 默认目标列为第 1 列（人类友好 1-based；内部转换为 0-based）
- 默认使用 utf-8-sig 编码读写，以兼容带 BOM 的 UTF-8 文件
- 默认会在同目录生成一个 .bak 备份文件；可通过 --no-backup 禁用
"""
from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path
from typing import List


def renumber_csv(
    file_path: Path,
    start_value: int,
    start_line: int = 6,
    column_index: int = 0,
    encoding: str = "utf-8",
    backup: bool = True,
    backup_suffix: str = ".bak",
) -> None:
    """对 CSV 从给定起始行起重写指定列为递增编号，并写回原文件。

    参数:
    - file_path: CSV 文件路径
    - start_value: 起始编号（写入起始行的值）
    - start_line: 起始行（1-based，含该行）默认 6
    - column_index: 目标列（0-based），默认 0 即第一列
    - encoding: 文件编码，默认 utf-8-sig
    - backup: 是否写回前生成 .bak 备份
    - backup_suffix: 备份后缀名，默认 ".bak"
    """

    if start_line < 1:
        raise ValueError("start_line 必须 >= 1")
    if column_index < 0:
        raise ValueError("column_index 必须 >= 0")

    if not file_path.exists():
        raise FileNotFoundError(f"找不到文件: {file_path}")

    # 读取所有行
    rows: List[List[str]] = []
    with file_path.open("r", encoding=encoding, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(list(row))

    total = len(rows)
    if total == 0:
        print("文件为空，无需修改。")
        return

    # 计算从哪一行开始（将 1-based 转成列表索引 0-based）
    start_idx = start_line - 1
    if start_idx >= total:
        print(f"总行数 {total} 小于起始行 {start_line}，无修改。")
        return

    # 写入前备份
    if backup:
        backup_path = file_path.with_name(file_path.name + backup_suffix)
        shutil.copy2(file_path, backup_path)
        print(f"已备份到: {backup_path}")

    # 从起始行起逐行赋值/递增
    current_value = start_value
    target_count = 0
    for idx in range(start_idx, total):
        row = rows[idx]
        # 跳过空白行（所有单元格为空或仅含空白），不改变编号
        if not any((cell and cell.strip()) for cell in row):
            continue
        # 确保行长度足够
        if column_index >= len(row):
            # 若异常短行，扩展到需要的列数
            row.extend([""] * (column_index - len(row) + 1))
        row[column_index] = str(current_value)
        current_value += 1
        target_count += 1

    # 写回原文件
    with file_path.open("w", encoding=encoding, newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # 将文件里的部分文本进行替换以修改错误的格式
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
    # 将,"替换为,
    content = content.replace(',"', ',')
    content = content.replace('""', '"')
    content = content.replace('"\n', '\n')
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)

    print(
        f"已完成：文件={file_path}，总行数={total}，从第{start_line}行起共修改={target_count}行，列(0-based)={column_index}。"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从指定行开始将 CSV 指定列重编号（写回原文件，默认生成 .bak 备份）",
    )
    parser.add_argument("csv", type=str, help="CSV 文件路径")
    parser.add_argument("start", type=int, help="起始编号（起始行写入该值，后续行逐行+1）")

    parser.add_argument(
        "--start-line",
        type=int,
        default=6,
        help="起始行(1-based，含该行)，默认 6",
    )
    parser.add_argument(
        "--column",
        type=int,
        default=1,
        help="目标列(1-based)，默认 1 表示第一列",
    )
    parser.add_argument(
        "--encoding",
        type=str,
        default="utf-8",
        help="文件编码，默认 utf-8",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="不生成 .bak 备份文件（默认会生成）",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    file_path = Path(args.csv)
    # CLI 中列号为 1-based，内部转 0-based
    column_index = max(1, args.column) - 1
    start_line = max(1, args.start_line)
    backup = not args.no_backup

    renumber_csv(
        file_path=file_path,
        start_value=args.start,
        start_line=start_line,
        column_index=column_index,
        encoding=args.encoding,
        backup=backup,
    )


if __name__ == "__main__":
    main()
