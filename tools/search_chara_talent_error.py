import os
import csv

character_dir = r'data\character'
problem_files = []

for filename in os.listdir(character_dir):
    if filename.endswith('.csv'):
        file_path = os.path.join(character_dir, filename)
        count = 0
        with open(file_path, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # 跳过表头
            for row in reader:
                if not row or not row[0].startswith('T|'):
                    continue
                try:
                    num = int(row[0][2:].split('|')[0])
                    if 121 <= num <= 132:
                        count += 1
                except Exception:
                    continue
        if count != 4:
            print(file_path)