#!/usr/bin/env python3
"""
在 CSV 文件的指定列（默认 `context`）中按字符计数插入换行符。

用法示例：
    python tools/wrap_context_linebreaks.py --file data/talk/daily/chat/assistant_chat.csv

主要行为：
1. 逐行读取 CSV（保留表头和其他列不变）。
2. 对指定的列从左到右计数字符，达到阈值（默认 100）后，寻找下一个句号（中文句号 '。' 或英文句号 '.'），在该句号后插入换行符（"\n"），计数归零并继续。
3. 覆盖写回原文件（脚本会先根据 --no-backup 禁用备份，默认会创建一个 .bak 备份）。

限制与说明：
- 如果在达到阈值后再也找不到句号，则在该点不插入换行（保留原文）。
- 句号包括中文和英文句号；脚本不会改变除插入换行外的文本。
"""
import argparse
import csv
import os
import shutil
import sys


def wrap_text_by_sentences(text: str, threshold: int = 100) -> str:
    """按要求在句号后插入换行符。

    算法：从左到右遍历字符，累加长度；当计数>=threshold后，寻找下一个句号（'。' 或 '.'），在该句号后插入"\n"并将计数清零，继续处理剩余部分。
    如果找不到句号则不做插入。
    """
    if not text:
        return text

    out_parts = []
    i = 0
    n = len(text)
    count = 0

    while i < n:
        ch = text[i]
        out_parts.append(ch)
        count += 1

        if count >= threshold:
            # 从当前位置向后搜索句号
            j = i + 1
            found = -1
            while j < n:
                if text[j] == '。' or text[j] == '.':
                    found = j
                    break
                j += 1

            if found != -1:
                # 把中间的内容也追加
                # 已经将 [i] 加入 out_parts，因此只需把 text[i+1:found+1]
                # 但是因为我们在循环中会继续追加，这里把剩余一次性处理更方便
                # 将剩余部分从 i+1 到 found 加入
                out_parts.extend(list(text[i+1:found+1]))
                out_parts.append('\\n')
                # 更新指针到 found+1
                i = found
                count = 0
            else:
                # 没有找到句号，直接走到结尾并结束
                # 之后的字符会在自然循环中被加入
                pass

        i += 1

    return ''.join(out_parts)


def process_csv(file_path: str, column_name: str = 'context', threshold: int = 100, backup: bool = True):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)

    # 备份
    if backup:
        bak_path = file_path + '.bak'
        shutil.copy2(file_path, bak_path)

    # 读取所有内容
    with open(file_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise ValueError('CSV 没有表头')

        rows = list(reader)

    if column_name not in fieldnames:
        raise ValueError(f'列 "{column_name}" 在 CSV 中未找到')

    # 处理每一行
    for idx, row in enumerate(rows):
        original = row.get(column_name, '')
        new = wrap_text_by_sentences(original, threshold=threshold)
        # print(new)
        if new != original:
            rows[idx][column_name] = new

    # 覆盖写回（保持原有列顺序）
    tmp_path = file_path + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    shutil.move(tmp_path, file_path)

    # 将文件里的部分文本进行替换以修改错误的格式
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 将,"替换为,
    content = content.replace(',"', ',')
    content = content.replace('""', '"')
    content = content.replace('"\n', '\n')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description='在 CSV 的指定列达到字符数阈值后，于下一句号后插入换行。')
    parser.add_argument('--file', '-f', required=True, help='要处理的 CSV 文件路径')
    parser.add_argument('--column', '-c', default='context', help='要处理的列名，默认 "context"')
    parser.add_argument('--threshold', '-t', type=int, default=60, help='字符阈值，默认 60')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份（默认会创建 .bak）')

    args = parser.parse_args()

    try:
        process_csv(args.file, column_name=args.column, threshold=args.threshold, backup=not args.no_backup)
    except Exception as e:
        print('处理失败：', e, file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
