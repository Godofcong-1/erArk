"""将 CSV 行中从第 5 个逗号起的英文逗号替换为中文逗号。

每行的前四个逗号保持英文逗号，从第五个逗号开始替换为中文逗号字符。
"""
from __future__ import annotations

import argparse
from pathlib import Path


def replace_commas(line: str) -> str:
    """返回将第 5 次及以后的英文逗号替换后的行。

    参数:
        line: 要处理的单行字符串。

    返回:
        替换后的行字符串，前四个逗号保留为英文逗号，第五个及之后的逗号替换为中文逗号。
    """
    result: list[str] = []
    comma_count = 0

    # 遍历每个字符，遇到英文逗号时计数，若计数 >= 5 则替换为中文逗号
    for char in line:
        if char == ",":
            comma_count += 1
            if comma_count >= 5:
                result.append("，")
                continue
        result.append(char)

    return "".join(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="替换 CSV 文件中的逗号（从第五个开始替换为中文逗号）")
    parser.add_argument("path", type=Path, help="要更新的 CSV 文件路径")
    args = parser.parse_args()

    file_path = args.path
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 读取文件、逐行处理并写回
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    processed_lines = [replace_commas(line) for line in lines]
    file_path.write_text("".join(processed_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
