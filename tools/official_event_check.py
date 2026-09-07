# -*- coding: UTF-8 -*-
"""公务事件表（data/official_event/*.csv）的校验工具（Plan 23）

事件表有一堆**静默失败**的坑：`department` 写成非数字会让事件永远抽不中且不报错、
空着的选项列在构建时会被删掉、正文里的裸 `{}` 会在绘制时抛异常、
所有选项都带前提的事件会反复弹出……手写两百多条时这些错误几乎必然发生，
所以每写完一批就跑一次本工具。

用法（仓库根目录）：
    .conda\\python.exe tools/official_event_check.py            # 校验 + 统计报告
    .conda\\python.exe tools/official_event_check.py --full     # 额外校验条数下限（内容写完后用）
    .conda\\python.exe tools/official_event_check.py --quiet    # 只报错，不打统计

⚠️ 本工具**不启动游戏**：前提名与结算id直接从 `Script/Core/constant_promise.py`、
   `Script/Core/constant_effect.py`、`data/csv/*.csv` 里解析，跑一次不到一秒。
"""
import csv
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EVENT_DIR = os.path.join("data", "official_event")
""" 事件表所在目录 """

FIELD_COUNT = 28
""" 每行必须有的字段数（8个基本字段 + 4组×5个选项字段） """

BASE_FIELD = ["cid", "department", "subject", "sub_key", "once", "weight", "premise", "text"]
""" 基本字段的列名与顺序 """

OPTION_SUFFIX = ["", "_premise", "_reason", "_tip", "_effect"]
""" 每个选项块的五个字段后缀 """

INT_FIELD = ["department", "subject", "sub_key", "once", "weight"]
""" 必须是纯数字的字段 """

PARTNER_PREMISE = ("self_have_sibling_child", "self_have_classmate")
""" 会挑出互动对象的两个前提：写了 CVE_A2 的事件必须带其中之一，否则 A2 会落到博士身上 """

GROWTH_DEPARTMENT = 15
""" 教育区（养成事件） """

CHILD_SUB_KEY = {0, 101, 102, 103}
""" 未成年阶段的子桶键：这些事件不允许改能力与素质（选错不该掉能力） """

DORM_SUB_KEY = {102, 103, 104}
""" 幼女期起孩子住自己的宿舍，正文不该再出现育儿室 """

DORM_TEXT_ALLOW = {"幼女": {"5"}}
""" 上一条的例外：文件名 -> cid集合。
    ⚠️ 只放「搬离育儿室」这类**本身就在讲这件事**的里程碑事件，别拿它当报错的消音器 """

MIN_COUNT = {"婴儿": 50, "幼女": 70, "萝莉": 70, "通用": 56}
""" --full 模式下的条数下限（通用只数跨阶段的那部分，成年后事件不计入） """

TEXT_DUP_LEN = 15
""" 查重时比对的正文前缀长度 """


def load_premise_name_set() -> set:
    """
    从 constant_promise.py 里解析出全部合法的前提名
    Keyword arguments:
    无
    Return arguments:
    set -- 前提名集合
    """
    path = os.path.join("Script", "Core", "constant_promise.py")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return set(re.findall(r'^\s*[A-Z0-9_]+\s*=\s*"([a-z0-9_]+)"', text, re.M))


def load_effect_id_set() -> set:
    """
    从 constant_effect.py 里解析出全部合法的结算函数id
    Keyword arguments:
    无
    Return arguments:
    set -- 结算id集合（str形式，便于与CSV里的文本直接比对）
    """
    path = os.path.join("Script", "Core", "constant_effect.py")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return set(re.findall(r"^\s*[A-Z0-9_]+\s*=\s*(\d+)", text, re.M))


def load_department_set() -> set:
    """
    从 Facility.csv 里解析出全部部门id（type 为 -1 的区块行）
    Keyword arguments:
    无
    Return arguments:
    set -- 部门id集合（int）
    """
    result = set()
    path = os.path.join("data", "csv", "Facility.csv")
    with open(path, encoding="utf-8", newline="") as f:
        for index, row in enumerate(csv.reader(f)):
            if index < 5 or len(row) < 3:
                continue
            try:
                if int(row[2]) == -1:
                    result.add(int(row[0]))
            except ValueError:
                continue
    return result


class Checker:
    """
    公务事件表的校验器
    Keyword arguments:
    full -- 是否校验条数下限
    Return arguments:
    无
    """

    def __init__(self, full: bool = False):
        """初始化校验器"""
        self.full: bool = full
        """ 是否校验条数下限 """
        self.error_list: list = []
        """ 错误列表，每项为一行说明 """
        self.premise_name_set: set = load_premise_name_set()
        """ 合法前提名 """
        self.effect_id_set: set = load_effect_id_set()
        """ 合法结算函数id """
        self.department_set: set = load_department_set()
        """ 合法部门id """
        self.stat: dict = {}
        """ 统计报告数据 文件名:各项统计 """

    def error(self, path: str, line: int, text: str):
        """
        记一条错误
        Keyword arguments:
        path -- 文件路径
        line -- 行号（1起）
        text -- 错误说明
        Return arguments:
        无
        """
        self.error_list.append(f"{os.path.basename(path)}:{line} {text}")

    def check_file_format(self, path: str) -> list:
        """
        校验文件级格式（BOM/换行/表头），并返回全部行
        Keyword arguments:
        path -- 文件路径
        Return arguments:
        list -- csv 解析出的全部行
        """
        with open(path, "rb") as f:
            raw = f.read()
        if raw.startswith(b"\xef\xbb\xbf"):
            self.error(path, 1, "文件带BOM，构建时 cid 列名会变成 \\ufeffcid 并在载入配置时 KeyError")
        if b"\r\n" not in raw:
            self.error(path, 1, "文件不是CRLF换行")
        elif raw.replace(b"\r\n", b"").count(b"\n"):
            self.error(path, 1, "文件里混了裸LF换行")
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        if len(rows) < 5:
            self.error(path, 1, "表头不足5行")
            return []
        if rows[0][:8] != BASE_FIELD:
            self.error(path, 1, f"表头列名与约定不符：{rows[0][:8]}")
        return rows

    def check_option_block(self, path: str, line: int, row: dict, index: int, department: int, sub_key: int) -> bool:
        """
        校验一个选项块
        Keyword arguments:
        path -- 文件路径
        line -- 行号
        row -- 该行的字段dict
        index -- 选项序号1~4
        department -- 部门id
        sub_key -- 子桶键
        Return arguments:
        bool -- 该选项是否存在且没有前提（用于「至少一个无前提选项」的判定）
        """
        option_text = row.get(f"option_{index}", "").strip()
        premise_text = row.get(f"option_{index}_premise", "").strip()
        reason_text = row.get(f"option_{index}_reason", "").strip()
        tip_text = row.get(f"option_{index}_tip", "").strip()
        effect_text = row.get(f"option_{index}_effect", "").strip()
        if not option_text:
            for suffix in OPTION_SUFFIX[1:]:
                if row.get(f"option_{index}{suffix}", "").strip():
                    self.error(path, line, f"选项{index}的文本为空，但 option_{index}{suffix} 有内容（空选项的附属列必须一起留空）")
            return False
        self.check_text(path, line, f"选项{index}文本", option_text)
        if not tip_text:
            self.error(path, line, f"选项{index}缺后果提示（option_{index}_tip）")
        if premise_text and not reason_text:
            self.error(path, line, f"选项{index}带前提却没写置灰原因（option_{index}_reason）")
        self.check_premise_text(path, line, f"选项{index}前提", premise_text)
        self.check_effect_text(path, line, f"选项{index}结算", effect_text, row, department, sub_key)
        return not premise_text

    def check_text(self, path: str, line: int, name: str, text: str):
        """
        校验一段展示文本：不能有裸花括号与英文标点
        Keyword arguments:
        path -- 文件路径
        line -- 行号
        name -- 字段名（报错用）
        text -- 文本
        Return arguments:
        无
        """
        if "{" in text or "}" in text:
            self.error(path, line, f"{name}里有花括号，绘制时会走 .format() 并抛异常")
        if '"' in text:
            self.error(path, line, f"{name}里有英文双引号，构建时会被转义成 \\\" 并原样显示")
        if "," in text:
            self.error(path, line, f"{name}里有英文逗号，请改用中文全角逗号")

    def check_premise_text(self, path: str, line: int, name: str, premise_text: str):
        """
        校验一串 & 连接的前提
        Keyword arguments:
        path -- 文件路径
        line -- 行号
        name -- 字段名（报错用）
        premise_text -- 前提串
        Return arguments:
        无
        """
        if not premise_text:
            return
        for one in premise_text.split("&"):
            one = one.strip()
            if not one:
                continue
            if one.startswith("CVP_"):
                part = one.split("_")
                if len(part) < 4:
                    self.error(path, line, f"{name}的 {one} 段数不足（CVP_主体_类型_运算_值）")
                    continue
                if part[1] not in ("A1", "A2", "RI") and not part[1].startswith("A3"):
                    self.error(path, line, f"{name}的 {one} 主体 {part[1]} 不支持")
                if not re.fullmatch(r"-?\d+", part[-1]):
                    self.error(path, line, f"{name}的 {one} 判定值不是整数（前提侧的值走 int()，不能写小数）")
                continue
            if one not in self.premise_name_set:
                self.error(path, line, f"{name}的 {one} 不是已注册的前提")

    def check_effect_text(self, path: str, line: int, name: str, effect_text: str, row: dict, department: int, sub_key: int):
        """
        校验一串 & 连接的结算
        Keyword arguments:
        path -- 文件路径
        line -- 行号
        name -- 字段名（报错用）
        effect_text -- 结算串
        row -- 该行的字段dict（判 A2 与主体用）
        department -- 部门id
        sub_key -- 子桶键
        Return arguments:
        无
        """
        if not effect_text:
            return
        subject = row.get("subject", "1").strip()
        premise_text = row.get("premise", "")
        for one in effect_text.split("&"):
            one = one.strip()
            if not one:
                continue
            if one.isdigit():
                if one not in self.effect_id_set:
                    self.error(path, line, f"{name}的结算id {one} 不在 constant_effect.py 里")
                continue
            if not one.startswith("CVE_"):
                self.error(path, line, f"{name}的 {one} 既不是 CVE token 也不是纯数字结算id")
                continue
            part = one.split("_")
            if len(part) < 4:
                self.error(path, line, f"{name}的 {one} 段数不足（CVE_主体_类型_运算_值）")
                continue
            if part[1] not in ("A1", "A2", "RI") and not part[1].startswith("A3"):
                self.error(path, line, f"{name}的 {one} 主体 {part[1]} 不支持")
            if part[-2] not in ("G", "L", "E"):
                self.error(path, line, f"{name}的 {one} 运算符只能是 G/L/E")
            if part[1] == "RI":
                if not re.fullmatch(r"-?\d+(\.\d+)?", part[-1]):
                    self.error(path, line, f"{name}的 {one} 数值不合法")
            elif "Growth" not in one:
                if not re.fullmatch(r"-?\d+", part[-1]):
                    self.error(path, line, f"{name}的 {one} 数值必须是整数（只有 Growth 与 RI 允许小数）")
            if part[1] == "A2" and not any(k in premise_text for k in PARTNER_PREMISE):
                self.error(path, line, f"{name}用了 A2，但事件前提里没有 {PARTNER_PREMISE[0]} 或 {PARTNER_PREMISE[1]}，A2 会落到博士身上")
            if subject == "0" and part[1] in ("A1", "A2"):
                self.error(path, line, f"{name}用了 {part[1]}，但这条事件是无主体的部门事务（subject=0）")
            if department == GROWTH_DEPARTMENT and sub_key in CHILD_SUB_KEY and re.search(r"CVE_A[12]_(A|T)\|", one):
                self.error(path, line, f"{name}改了能力或素质，未成年阶段的事件选错不该掉能力")

    def check_row(self, path: str, line: int, row: dict, cid_set: set, text_set: set):
        """
        校验一条事件
        Keyword arguments:
        path -- 文件路径
        line -- 行号
        row -- 该行的字段dict
        cid_set -- 本文件已出现过的cid集合
        text_set -- 本文件已出现过的正文前缀集合
        Return arguments:
        无
        """
        cid = row.get("cid", "").strip()
        if not cid:
            self.error(path, line, "cid 为空")
            return
        if cid in cid_set:
            self.error(path, line, f"cid {cid} 在本文件内重复，后者会静默覆盖前者")
        cid_set.add(cid)
        for field in INT_FIELD:
            value = row.get(field, "").strip()
            if not re.fullmatch(r"-?\d+", value):
                self.error(path, line, f"{field} 的值「{value}」不是整数（写成非数字会让事件永远抽不中且不报错）")
        department = int(row["department"]) if re.fullmatch(r"-?\d+", row.get("department", "").strip()) else -1
        sub_key = int(row["sub_key"]) if re.fullmatch(r"-?\d+", row.get("sub_key", "").strip()) else -1
        if department not in self.department_set:
            self.error(path, line, f"department {department} 不是 Facility.csv 里的部门（type为-1的区块）")
        if row.get("subject", "").strip() not in ("0", "1"):
            self.error(path, line, "subject 只能是 0（无主体）或 1（角色）")
        if re.fullmatch(r"-?\d+", row.get("weight", "").strip()) and int(row["weight"]) <= 0:
            self.error(path, line, "weight 必须为正整数")
        text = row.get("text", "").strip()
        if not text:
            self.error(path, line, "事件正文为空")
        self.check_text(path, line, "事件正文", text)
        prefix = text[:TEXT_DUP_LEN]
        if prefix and prefix in text_set:
            self.error(path, line, f"事件正文的前{TEXT_DUP_LEN}字与本文件另一条重复：{prefix}")
        text_set.add(prefix)
        file_name = os.path.splitext(os.path.basename(path))[0]
        if department == GROWTH_DEPARTMENT and sub_key in DORM_SUB_KEY and "育儿室" in text and cid not in DORM_TEXT_ALLOW.get(file_name, set()):
            self.error(path, line, "幼女期起孩子住自己的宿舍，正文不该再出现育儿室（确实在写搬离育儿室的话，把 cid 加进 DORM_TEXT_ALLOW）")
        self.check_premise_text(path, line, "事件前提", row.get("premise", "").strip())
        have_free_option = False
        option_count = 0
        for index in range(1, 5):
            if row.get(f"option_{index}", "").strip():
                option_count += 1
            if self.check_option_block(path, line, row, index, department, sub_key):
                have_free_option = True
        if option_count < 2:
            self.error(path, line, f"只有 {option_count} 个选项，至少要有2个")
        if not have_free_option:
            self.error(path, line, "所有选项都带前提，全被挡住时事件会跳过且不写履历，于是第二天再被抽中反复弹出")

    def check_dir(self):
        """
        校验整个事件目录
        Keyword arguments:
        无
        Return arguments:
        无
        """
        path_list = sorted(glob.glob(os.path.join(EVENT_DIR, "*.csv")))
        if not path_list:
            self.error(EVENT_DIR, 0, "目录下没有任何事件表")
            return
        for path in path_list:
            rows = self.check_file_format(path)
            if not rows:
                continue
            head = rows[0]
            cid_set = set()
            text_set = set()
            file_stat = {"count": 0, "weight": [], "once": 0, "partner": 0, "personality": {}, "favorability": 0, "sub_key": {}}
            for index, raw_row in enumerate(rows[5:], start=6):
                if not raw_row or not raw_row[0].strip():
                    continue
                if len(raw_row) != FIELD_COUNT:
                    self.error(path, index, f"字段数为 {len(raw_row)}，应为 {FIELD_COUNT}")
                    continue
                row = dict(zip(head, raw_row))
                self.check_row(path, index, row, cid_set, text_set)
                self.collect_stat(file_stat, row)
            self.stat[os.path.basename(path)] = file_stat
            if self.full:
                self.check_count(path, file_stat)

    def collect_stat(self, file_stat: dict, row: dict):
        """
        累计一条事件的统计数据
        Keyword arguments:
        file_stat -- 该文件的统计dict
        row -- 该行的字段dict
        Return arguments:
        无
        """
        file_stat["count"] += 1
        if re.fullmatch(r"-?\d+", row.get("weight", "").strip()):
            file_stat["weight"].append(int(row["weight"]))
        if row.get("once", "0").strip() == "1":
            file_stat["once"] += 1
        if any(k in row.get("premise", "") for k in PARTNER_PREMISE):
            file_stat["partner"] += 1
        sub_key = row.get("sub_key", "").strip()
        file_stat["sub_key"][sub_key] = file_stat["sub_key"].get(sub_key, 0) + 1
        for index in range(1, 5):
            effect_text = row.get(f"option_{index}_effect", "")
            for one in re.findall(r"CVE_A1_Growth\|(1[0-3])_([GL])_([\d.]+)", effect_text):
                pair_id, operator_text, value = one
                now_stat = file_stat["personality"].setdefault(pair_id, [0, 0])
                now_stat[0 if operator_text == "G" else 1] += 1
            for one in re.findall(r"CVE_A1_F_([GL])_(\d+)", effect_text):
                file_stat["favorability"] += int(one[1]) * (1 if one[0] == "G" else -1)

    def check_count(self, path: str, file_stat: dict):
        """
        校验条数下限（--full 模式）
        Keyword arguments:
        path -- 文件路径
        file_stat -- 该文件的统计dict
        Return arguments:
        无
        """
        name = os.path.splitext(os.path.basename(path))[0]
        if name not in MIN_COUNT:
            return
        count = file_stat["count"]
        if name == "通用":
            # 通用文件里成年后（104）的事件不参与跨阶段池的供需，单独排除
            count -= file_stat["sub_key"].get("104", 0)
        if count < MIN_COUNT[name]:
            self.error(path, 0, f"条数 {count} 少于下限 {MIN_COUNT[name]}（供需推导见 plan_23 方案 §3.5）")

    def print_stat(self):
        """
        打印统计报告（只提示，不判失败）
        Keyword arguments:
        无
        Return arguments:
        无
        """
        pair_name = {"10": "勤劳/懒散", "11": "坚强/脆弱", "12": "热情/孤僻", "13": "开放/羞耻"}
        print()
        print("========== 统计报告 ==========")
        for name in self.stat:
            one = self.stat[name]
            weight_list = one["weight"]
            weight_text = f"{min(weight_list)}~{max(weight_list)}" if weight_list else "-"
            print(f"[{name}] 事件 {one['count']} 条｜权重 {weight_text}｜里程碑标注 {one['once']} 条｜带互动对象 {one['partner']} 条｜净好感 {one['favorability']:+d}")
            print(f"    子桶分布：{one['sub_key']}")
            if one["personality"]:
                text_list = []
                for pair_id in sorted(one["personality"]):
                    plus, minus = one["personality"][pair_id]
                    text_list.append(f"{pair_name.get(pair_id, pair_id)} +{plus}/-{minus}")
                print(f"    性格倾向：{'｜'.join(text_list)}")


def main():
    """
    入口：校验并按结果设置退出码
    Keyword arguments:
    无
    Return arguments:
    int -- 退出码，0为全部通过
    """
    full = "--full" in sys.argv
    quiet = "--quiet" in sys.argv
    checker = Checker(full)
    checker.check_dir()
    if checker.error_list:
        print(f"========== 发现 {len(checker.error_list)} 个问题 ==========")
        for one in checker.error_list:
            print("  " + one)
    else:
        total = sum(one["count"] for one in checker.stat.values())
        print(f"校验通过：{len(checker.stat)} 个文件，共 {total} 条事件")
    if not quiet:
        checker.print_stat()
    return 1 if checker.error_list else 0


if __name__ == "__main__":
    sys.exit(main())
