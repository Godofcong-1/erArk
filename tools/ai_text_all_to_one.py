from pathlib import Path
import csv

def collect_and_cut_rows(source_dir: Path, target_file: Path) -> None:
    """输入类型: Path, Path / 输出类型: None / 功能: 将源目录下各 CSV 的第 5 行起数据剪切到目标文件并清理第 5 列首尾双引号"""
    target_file.parent.mkdir(parents=True, exist_ok=True)

    with target_file.open("a", encoding="utf-8-sig", newline="") as target_fp:
        target_writer = csv.writer(target_fp)
        for csv_path in sorted(source_dir.glob("*.csv")):
            with csv_path.open("r", encoding="utf-8-sig", newline="") as src_fp:
                rows = list(csv.reader(src_fp))

            if len(rows) <= 4:
                continue

            keep_rows = rows[:4]
            move_rows = rows[4:]
            for row in move_rows:
                if len(row) > 4 and row[4]:
                    col = row[4]
                    if col.startswith('\"'):
                        print("Found leading quote")
                        col = col[1:]
                    if col.endswith('\"'):
                        print("Found trailing quote")
                        col = col[:-1]
                    row[4] = col
                target_writer.writerow(row)

            with csv_path.open("w", encoding="utf-8-sig", newline="") as dst_fp:
                csv.writer(dst_fp).writerows(keep_rows)


def main() -> None:
    """输入类型: None / 输出类型: None / 功能: 执行剪切与合并流程"""
    base_dir = Path(__file__).resolve().parent
    source_dir = base_dir / ".github" / "prompts" / "AI文本生成工作流" / "生成目标文件"
    target_file = base_dir / ".github" / "prompts" / "AI文本生成工作流" / "生成完待处理数据.csv"
    collect_and_cut_rows(source_dir, target_file)


if __name__ == "__main__":
    main()