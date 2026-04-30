#!/usr/bin/env python3
"""
将“角色能力修改表”文本解析为 CSV，并可按能力数据批量回写角色文件。

输入文本格式：
- 以空行分隔不同角色块。
- 每个角色块通常有 2~3 行：
  1) 角色名
  2) 新的角色能力
  3) 可选修改理由（会被忽略）

输出 CSV 格式：
- 每行一个角色。
- 第 1 列：角色名
- 第 2 列：角色文件名（从 data/character 反查 Name 行）
- 第 3 列：角色能力
- 第 4 列：角色能力数据（能力id:能力等级）
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re


ABILITY_NAME_ALIASES = {
    "医疗": "医术",
    "治疗": "医术",
}


def parse_blocks(text: str) -> list[list[str]]:
    """按空行分块并清理每行两端空白。"""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks: list[list[str]] = []
    current: list[str] = []

    for raw_line in normalized.split("\n"):
        line = raw_line.strip()
        if not line:
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(line)

    if current:
        blocks.append(current)

    return blocks


def extract_rows(blocks: list[list[str]]) -> tuple[list[list[str]], list[tuple[int, str]]]:
    """从每个角色块提取 [角色名, 角色能力]，并返回被跳过块的序号与角色名。"""
    rows: list[list[str]] = []
    skipped_blocks: list[tuple[int, str]] = []

    for index, block in enumerate(blocks, start=1):
        if len(block) < 2:
            skipped_name = block[0].strip() if block and block[0].strip() else "<空角色名>"
            skipped_blocks.append((index, skipped_name))
            continue

        name = block[0]
        ability = block[1]
        rows.append([name, ability])

    return rows, skipped_blocks


def build_name_to_filename_map(character_dir: Path) -> dict[str, str]:
    """扫描角色目录，构建 角色名 -> 文件名 的映射。"""
    mapping: dict[str, str] = {}

    if not character_dir.exists() or not character_dir.is_dir():
        return mapping

    for file_path in sorted(character_dir.glob("*.csv")):
        try:
            with file_path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 3:
                        continue
                    if row[0].strip() == "Name":
                        name = row[2].strip()
                        if name and name not in mapping:
                            mapping[name] = file_path.name
                        break
        except Exception:
            continue

    return mapping


def build_skill_maps(ability_csv_path: Path) -> tuple[dict[str, str], dict[int, str]]:
    """从 Ability.csv 读取技能能力，构建 名称映射与ID映射。"""
    name_to_id: dict[str, str] = {}
    id_to_base_name: dict[int, str] = {}

    if not ability_csv_path.exists() or not ability_csv_path.is_file():
        return name_to_id, id_to_base_name

    with ability_csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 3:
                continue

            ability_id_text = row[0].strip()
            ability_type = row[1].strip()
            ability_name = row[2].strip()
            if not ability_id_text.isdigit() or ability_type != "4" or not ability_name:
                continue

            ability_id = int(ability_id_text)
            base_name = ability_name.removesuffix("技能")
            id_to_base_name[ability_id] = base_name
            name_to_id[ability_name] = ability_id_text
            name_to_id[base_name] = ability_id_text

    for alias, target in ABILITY_NAME_ALIASES.items():
        if target in name_to_id:
            name_to_id[alias] = name_to_id[target]

    return name_to_id, id_to_base_name


def parse_ability_text_to_data(ability_text: str, skill_name_to_id: dict[str, str]) -> tuple[str, bool]:
    """将角色能力文本解析为 能力ID:等级 列表字符串。"""
    compact_text = re.sub(r"\s+", "", ability_text)
    if not compact_text or not skill_name_to_id:
        return "", False

    skill_names = sorted(skill_name_to_id.keys(), key=len, reverse=True)
    result: list[str] = []
    index = 0
    has_unresolved_part = False

    while index < len(compact_text):
        matched_name = next((name for name in skill_names if compact_text.startswith(name, index)), None)
        if not matched_name:
            has_unresolved_part = True
            index += 1
            continue

        level_start = index + len(matched_name)
        level_end = level_start
        while level_end < len(compact_text) and compact_text[level_end].isdigit():
            level_end += 1

        if level_end == level_start:
            has_unresolved_part = True
            index = level_start
            continue

        ability_id = skill_name_to_id[matched_name]
        level = compact_text[level_start:level_end]
        result.append(f"{ability_id}:{level}")
        index = level_end

    return ",".join(result), has_unresolved_part


def attach_character_metadata(rows: list[list[str]], name_to_filename: dict[str, str], skill_name_to_id: dict[str, str]) -> tuple[list[list[str]], int, int]:
    """补充角色文件名与角色能力数据列。"""
    new_rows: list[list[str]] = []
    unmatched_count = 0
    unresolved_ability_count = 0

    for row in rows:
        name = row[0]
        ability = row[1]
        filename = name_to_filename.get(name, "")
        ability_data, has_unresolved_part = parse_ability_text_to_data(ability, skill_name_to_id)
        if not filename:
            unmatched_count += 1
        if has_unresolved_part:
            unresolved_ability_count += 1
        new_rows.append([name, filename, ability, ability_data])

    return new_rows, unmatched_count, unresolved_ability_count


def parse_ability_data_pairs(ability_data_text: str) -> list[tuple[int, int]]:
    """将“40:1,41:2”解析为[(40,1),(41,2)]。"""
    pairs: list[tuple[int, int]] = []
    for segment in ability_data_text.split(","):
        item = segment.strip()
        if not item or ":" not in item:
            continue
        ability_id_text, level_text = item.split(":", 1)
        if not ability_id_text.isdigit() or not level_text.isdigit():
            continue
        ability_id = int(ability_id_text)
        level = int(level_text)
        pairs.append((ability_id, level))
    return pairs


def build_skill_row(ability_id: int, level: int, id_to_base_name: dict[int, str]) -> list[str]:
    """根据能力ID和等级构造角色技能行。"""
    base_name = id_to_base_name.get(ability_id, str(ability_id))
    info_text = f"角色{base_name}技能为{level}"
    return [f"A|{ability_id}", "int", str(level), "0", info_text]


def is_skill_a_row(row: list[str]) -> bool:
    """判断是否为 A|40~49 的技能能力行。"""
    if not row:
        return False
    key = row[0].strip()
    match = re.fullmatch(r"A\|(\d+)", key)
    if not match:
        return False
    ability_id = int(match.group(1))
    return 40 <= ability_id <= 49


def rewrite_character_skill_rows(character_file: Path, ability_pairs: list[tuple[int, int]], id_to_base_name: dict[int, str]) -> bool:
    """重写单个角色文件中的技能能力行。"""
    if not character_file.exists() or not character_file.is_file():
        return False

    with character_file.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file))

    filtered_rows: list[list[str]] = [row for row in rows if not is_skill_a_row(row)]

    insert_pos = len(filtered_rows)
    has_a_section = False
    has_e_section = False
    for index, row in enumerate(filtered_rows):
        if row and row[0].strip().startswith("A|"):
            has_a_section = True
            insert_pos = index + 1

    # 若不存在 A 段，则将技能能力插入到首个 E 段之前。
    if not has_a_section:
        for index, row in enumerate(filtered_rows):
            if row and row[0].strip().startswith("E|"):
                has_e_section = True
                insert_pos = index
                break
    
    # 若既没有 A 段也没有 E 段，则将技能能力插入到首个 T 段之前。
    if not has_a_section and not has_e_section:
        for index, row in enumerate(filtered_rows):
            if row and row[0].strip().startswith("T|"):
                insert_pos = index
                break

    new_skill_rows = [build_skill_row(ability_id, level, id_to_base_name) for ability_id, level in ability_pairs]
    new_rows = filtered_rows[:insert_pos] + new_skill_rows + filtered_rows[insert_pos:]

    with character_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(new_rows)

    return True


def update_character_files_from_table(table_csv_path: Path, character_dir: Path, id_to_base_name: dict[int, str], max_update: int) -> tuple[int, int, int]:
    """按角色能力修改表批量更新角色CSV。"""
    if not table_csv_path.exists() or not table_csv_path.is_file():
        return 0, 0, 0

    total_rows = 0
    updated_files = 0
    skipped_rows = 0

    with table_csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_rows += 1
            filename = (row.get("角色文件名") or "").strip()
            ability_data_text = (row.get("角色能力数据") or "").strip()
            if not filename or not ability_data_text:
                skipped_rows += 1
                continue

            ability_pairs = parse_ability_data_pairs(ability_data_text)
            if not ability_pairs:
                skipped_rows += 1
                continue

            character_file = character_dir / filename
            changed = rewrite_character_skill_rows(character_file, ability_pairs, id_to_base_name)
            if changed:
                updated_files += 1
            else:
                skipped_rows += 1

            if max_update > 0 and updated_files >= max_update:
                break

    return total_rows, updated_files, skipped_rows


def write_csv(rows: list[list[str]], output_path: Path, with_header: bool) -> None:
    """将提取结果写入 CSV 文件。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        if with_header:
            writer.writerow(["角色名", "角色文件名", "角色能力", "角色能力数据"])
        writer.writerows(rows)


def main() -> None:
    """脚本入口：解析参数并执行转换。"""
    parser = argparse.ArgumentParser(description="解析角色能力修改表文本，导出角色名、文件名、能力和能力数据 CSV")
    parser.add_argument("input", help="输入文本文件路径")
    parser.add_argument("output", help="输出 CSV 文件路径")
    parser.add_argument("--with-header", action="store_true", help="在 CSV 首行写入表头")
    parser.add_argument("--character-dir", default="data/character", help="角色 CSV 目录（用于按角色名反查文件名和回写角色能力）")
    parser.add_argument("--ability-csv", default="data/csv/Ability.csv", help="能力定义 CSV（用于按能力名反查能力ID）")
    parser.add_argument("--update-character-files", action="store_true", help="根据输出CSV中的角色能力数据，回写角色文件中的A|40~49能力")
    parser.add_argument("--max-update", type=int, default=0, help="最多更新多少个角色文件，0表示不限制")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    character_dir = Path(args.character_dir)
    ability_csv_path = Path(args.ability_csv)

    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"输入文件不存在：{input_path}")

    content = input_path.read_text(encoding="utf-8")
    blocks = parse_blocks(content)
    rows, skipped_blocks = extract_rows(blocks)
    name_to_filename = build_name_to_filename_map(character_dir)
    skill_name_to_id, id_to_base_name = build_skill_maps(ability_csv_path)
    final_rows, unmatched_count, unresolved_ability_count = attach_character_metadata(rows, name_to_filename, skill_name_to_id)
    write_csv(final_rows, output_path, args.with_header)

    print(f"共识别角色块：{len(blocks)}")
    print(f"成功导出行数：{len(rows)}")
    print(f"角色目录映射数量：{len(name_to_filename)}")
    print(f"能力映射数量：{len(skill_name_to_id)}")
    print(f"未匹配角色数量：{unmatched_count}")
    print(f"能力文本存在未解析内容的行数：{unresolved_ability_count}")
    if skipped_blocks:
        print("跳过块（行数不足 2）：")
        for block_index, block_name in skipped_blocks:
            print(f" - 序号 {block_index}，角色名：{block_name}")
    print(f"输出文件：{output_path}")

    if args.update_character_files:
        total_rows, updated_files, skipped_rows = update_character_files_from_table(output_path, character_dir, id_to_base_name, args.max_update)
        print(f"已按能力表遍历行数：{total_rows}")
        print(f"实际更新角色文件数：{updated_files}")
        print(f"跳过行数：{skipped_rows}")


if __name__ == "__main__":
    main()
