# -*- coding: UTF-8 -*-
"""H 指令纸娃娃地文的生成与校验：A / B1 / B2 / C1 / C2 五段 x（攻略程度五档 + 通用 + 8 种无意识差分）

用法（在仓库根目录运行）:
    .conda\\python.exe tools/AI/纸娃娃指令地文/gen_paperdoll.py . <行为id>... [--check]
    --check  只校验文本源，不写 CSV（子代理写作时只用这个）
    --all    处理 spec.json 里全部已写好文本源的行为
    --show-spec  只打印所列行为的 spec 块（不读整份 spec.json，省得把全部指令的规则都读进上下文）
    --add-extra=部位1,部位2 / --add-forbidden=词1,词2
             只对这一次运行，给所列的单个行为追加部位短词 / 禁用词（只增不删，不写回 spec.json）。
             子代理不改 spec.json，需要追加时用这两个参数校验，并把追加项写进返回结果；
             主代理在工作流结束后用 make_specs.py --merge=<文件> 合并进 spec.json

文件:
    spec.json                 全部指令的规则，以行为id为键：部位短词、服装占位符、豁免词、额外禁用词，见 写作指南.md
    src/<行为id>.txt          五档与通用：`## 0 A` ... `## 4 C2`、`## 通用 A` ... `## 通用 C2`
    src/<行为id>_无意识.txt   无意识差分：`## 睡奸 A` ... `## 逆推 C2`
    每组 10 行，一行一条；空行忽略
输出:
    data/talk_common/action_<段>/<spec.dir>/<行为id>_<段>.csv；类型名 action_part_<行为id>_<A|B|C>（B1/B2 同属 B，C1/C2 同属 C）
cid（游戏会在前面拼上文件名，B1 与 B2 不冲突）:
    五档 1000 + 档*100 + 序号；通用 1500 + 序号；无意识差分 2000 + 差分序号*100 + 序号
前提:
    五档 = 档前提 & t_unconscious_flag_0；通用 = t_unconscious_flag_0；无意识差分 = 各自前提
    t_unconscious_flag_0（对方没有任何无意识状态）让清醒文本与各无意识差分互斥：平然状态下普通文本本来也能通过无意识判定，不加会混着抽
"""
import json
import os
import re
import sys

ROOT = sys.argv[1]
CHECK_ONLY = "--check" in sys.argv
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(HERE, "spec.json")
SRC_DIR = os.path.join(HERE, "src")


def cli_list(flag: str) -> list:
    """读命令行里 `<flag>=a,b` 形式的参数（可出现多次），返回去掉空项后的值列表

    参数:
        flag (str): 参数名，如 --add-extra
    返回:
        list: 值列表
    """
    values = []
    for arg in sys.argv:
        if arg.startswith(flag + "="):
            values += [value for value in arg[len(flag) + 1 :].split(",") if value]
    # 去掉重复项，保留先后顺序
    return list(dict.fromkeys(values))


# 子代理提议追加的规则：只在这次运行里叠加到 spec 上，不写回 spec.json（子代理并行写作时不共用一个可写文件）
ADD_EXTRA = cli_list("--add-extra")
ADD_FORBIDDEN = cli_list("--add-forbidden")

HEADER = "cid,type_id,adv_id,premise,context\r\n组件id,组件类型名,组件限定的剧情npcid,前提id,组件内容\r\nstr,str,int,str,str\r\n0,0,0,0,1\r\n组件配置数据,,,,\r\n"

# 攻略程度五档：未陷落 / 思慕·恋慕 / 恋人·爱侣 / 屈从·驯服 / 宠物·奴隶
TIER_PREMISE = [
    "CVP_A2_G_E_0",
    "CVP_A2_G_GE_1&CVP_A2_G_LE_2",
    "CVP_A2_G_GE_3",
    "CVP_A2_G_GE_-2&CVP_A2_G_LE_-1",
    "CVP_A2_G_LE_-3",
]
GENERAL_GROUP = "通用"
# 无意识差分（.github/skills/text_generation_for_instruction_code_generation/无意识H前提）；时停解放只在高潮时触发，指令文本不做
VARIANT_PREMISE = {
    "睡奸": "t_unconscious_flag_1&target_not_sleep_h_awake_but_pretend_sleep",
    "装睡": "t_unconscious_flag_1&target_sleep_h_awake_but_pretend_sleep",
    "醉酒": "t_unconscious_flag_2",
    "时停": "t_unconscious_flag_3",
    "平然": "t_unconscious_flag_4",
    "空气": "t_unconscious_flag_5",
    "木头人": "t_unconscious_flag_6&t_hypnosis_blockhead",
    "逆推": "t_unconscious_flag_6&t_hypnosis_active_h",
}
VARIANT_LIST = list(VARIANT_PREMISE)
GROUP_LIST = list(range(5)) + [GENERAL_GROUP] + VARIANT_LIST
SEGMENT_LIST = ["A", "B1", "B2", "C1", "C2"]
TEXTS_PER_GROUP = 10
LINE_MAX = 90

# 默认禁用词（spec.allow_words 可豁免其中的词，spec.forbidden 可追加）：
#   H 不预设地点、家具、时段与光线；不写破处与初次（另有专门文本）；不写避孕套与否；不写射精与内射那一下（射精文本由射精流程另外输出）
#   不写脚、鞋、袜（用户不要这类描写；足交、袜子交、鞋子交在 spec 里豁免）；不预设她穿裙子
DEFAULT_FORBIDDEN = [
    "床", "墙", "桌", "椅", "沙发", "办公", "早安", "晚安", "清晨", "深夜", "夜晚", "夜色", "晨光", "月光", "阳光",
    # 枕头与天花板同样预设了床与室内（2026-11-28 去重改写时混进来过 8 句）；「枕着他的手臂」这类不含下列词的写法不受影响
    "枕头", "枕上", "软枕", "天花板",
    "初吻", "处女", "落红", "破瓜", "第一次", "初次",
    "避孕套", "套子", "无套", "生插", "内射",
    "射了", "射满", "灌满", "喷射", "射出来了", "射进了", "射在了", "射到了", "精液溅", "精液喷",
    "脚", "鞋", "袜", "裙",
]


def load_all_specs() -> dict:
    """读入 spec.json，返回 {行为id: spec 字典}

    返回:
        dict: 全部指令的 spec
    """
    with open(SPEC_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_spec(behavior: str) -> dict:
    """读入某指令的 spec（spec.json 里该行为id的那一块），并叠加命令行 --add-extra / --add-forbidden 临时追加的项

    参数:
        behavior (str): 行为id
    返回:
        dict: 该指令生效的 spec；spec.json 里没有这个行为id时抛 KeyError
    """
    spec = load_all_specs()[behavior]
    # 只增不删：已在 spec 里的项不重复追加
    for key, values in (("extra", ADD_EXTRA), ("forbidden", ADD_FORBIDDEN)):
        spec[key] = spec.get(key, []) + [value for value in values if value not in spec.get(key, [])]
    return spec


def parse_text_file(path: str) -> dict:
    """解析文本源：`## <组> <段>` 开组，其后每行一条；返回 {(组, 段): [文本]}，组为档序号（int）或组名（str）"""
    groups = {}
    now_key = None
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("## "):
                head = line[3:].split()
                assert len(head) == 2, (path, line)
                group_str, segment = head
                now_key = (int(group_str) if group_str.isdigit() else group_str, segment)
                assert now_key not in groups, (path, "组重复", now_key)
                groups[now_key] = []
                continue
            assert now_key is not None, (path, "组头之前有文本", line)
            groups[now_key].append(line)
    return groups


def placeholder_form(part: str, segment: str) -> str:
    """部位短词在某段的写法：A 段用长短词 {x}，B/C 段用短词 {x_s}"""
    return "{" + part + "}" if segment == "A" else "{" + part + "_s}"


def check_text(text: str, spec: dict, group, segment: str) -> list:
    """校验单条文本，返回问题列表；group 为档序号（int）或组名（str）"""
    errors = []
    penis = placeholder_form("penis", segment)
    main_list = [placeholder_form(part, segment) for part in spec.get("main", [])]
    extra_list = [placeholder_form(part, segment) for part in spec.get("extra", [])]
    item_list = list(spec.get("items", []))
    literal_list = list(spec.get("literals", []))
    if "," in text:
        errors.append("半角逗号")
    if len(text) > LINE_MAX:
        errors.append(f"过长{len(text)}")
    allowed = {"{Name}", "{TargetName}", penis} | set(main_list) | set(extra_list) | set(item_list)
    for placeholder in re.findall(r"\{[^{}]*\}", text):
        if placeholder not in allowed:
            errors.append(f"占位符{placeholder}不在本段允许范围")
    stripped = re.sub(r"\{[^{}]*\}", "", text)
    if "{" in stripped or "}" in stripped:
        errors.append("括号不配对")
    # 各段的主语：B1 博士主导、C1 博士的感受要有 {Name}；其余段要有 {TargetName}
    subject = "{Name}" if segment in ("B1", "C1") else "{TargetName}"
    if subject not in text:
        errors.append(f"缺{subject}")
    # 本指令的部位：主部位短词、服装占位符或字面部位词，至少出现其一
    part_flag = any(p in text for p in main_list + item_list) or any(word in stripped for word in literal_list)
    penis_flag = penis in text
    if segment.startswith("C"):
        if not part_flag and not penis_flag:
            errors.append(f"缺{penis}与本指令部位")
    else:
        if not part_flag:
            errors.append(f"缺本指令部位（{'、'.join(main_list + item_list + literal_list)}）")
        if spec.get("penis_required", True) and not penis_flag:
            errors.append(f"缺{penis}")
    # 只有宠物·奴隶档称主人
    if group != 4 and "主人" in text:
        errors.append("非宠物·奴隶档称主人")
    allow_words = set(spec.get("allow_words", []))
    for word in [w for w in DEFAULT_FORBIDDEN if w not in allow_words] + list(spec.get("forbidden", [])):
        if word in stripped:
            errors.append(f"禁用词{word}")
    return errors


# 范例（帽子交）只供学结构与语气，不许照搬句子：去掉占位符后与范例任一句的相似度达到该值即判为照搬
REFERENCE_BEHAVIOR = "hat_job"
SIMILARITY_LIMIT = 0.75
_reference_cache = []


def strip_placeholders(text: str) -> str:
    """去掉占位符，只留正文用于比较相似度"""
    return re.sub(r"\{[^{}]*\}", "", text)


def reference_lines() -> list:
    """读入范例的全部文本（去掉占位符），只读一次"""
    if not _reference_cache:
        for file_name in (f"{REFERENCE_BEHAVIOR}.txt", f"{REFERENCE_BEHAVIOR}_无意识.txt"):
            path = os.path.join(SRC_DIR, file_name)
            if os.path.exists(path):
                for texts in parse_text_file(path).values():
                    _reference_cache.extend(strip_placeholders(text) for text in texts)
    return _reference_cache


def copied_from_reference(text: str) -> str:
    """返回与之过于相似的范例句（去掉占位符后的正文），没有则为空串"""
    import difflib

    body = strip_placeholders(text)
    matcher = difflib.SequenceMatcher(autojunk=False)
    matcher.set_seq2(body)
    for reference in reference_lines():
        matcher.set_seq1(reference)
        if matcher.real_quick_ratio() >= SIMILARITY_LIMIT and matcher.quick_ratio() >= SIMILARITY_LIMIT and matcher.ratio() >= SIMILARITY_LIMIT:
            return reference
    return ""


def load_behavior(behavior: str) -> tuple:
    """读入并校验某指令的全部文本源；返回 (spec, {(组, 段): [文本]}, 问题列表)"""
    spec = load_spec(behavior)
    errors = []
    groups = {}
    for file_name in (f"{behavior}.txt", f"{behavior}_无意识.txt"):
        path = os.path.join(SRC_DIR, file_name)
        if not os.path.exists(path):
            errors.append((behavior, "缺文本源", file_name))
            continue
        for key, texts in parse_text_file(path).items():
            if key in groups:
                errors.append((behavior, "两个文本源里组重复", key))
            groups[key] = texts
    expect_keys = {(group, segment) for group in GROUP_LIST for segment in SEGMENT_LIST}
    missing = sorted(expect_keys - set(groups), key=str)
    extra = sorted(set(groups) - expect_keys, key=str)
    if missing:
        errors.append((behavior, "缺组", missing))
    if extra:
        errors.append((behavior, "多出不认识的组", extra))
    # 通用组与五档在清醒时同池抽取：同一段里通用句与任一档的句子不能骨架雷同
    import difflib

    for segment in SEGMENT_LIST:
        tier_bodies = [(tier, strip_placeholders(text)) for tier in range(5) for text in groups.get((tier, segment), [])]
        for text in groups.get((GENERAL_GROUP, segment), []):
            matcher = difflib.SequenceMatcher(autojunk=False)
            matcher.set_seq2(strip_placeholders(text))
            for tier, body in tier_bodies:
                matcher.set_seq1(body)
                if matcher.real_quick_ratio() >= SIMILARITY_LIMIT and matcher.quick_ratio() >= SIMILARITY_LIMIT and matcher.ratio() >= SIMILARITY_LIMIT:
                    errors.append((behavior, (GENERAL_GROUP, segment), [f"通用句与第 {tier} 档的句子过于相似（{body}），两者清醒时同池抽取，请换一种写法"], text))
                    break
    seen = set()
    for key, texts in groups.items():
        if len(texts) != TEXTS_PER_GROUP:
            errors.append((behavior, key, f"条数{len(texts)}，应为{TEXTS_PER_GROUP}"))
        for text in texts:
            problem = check_text(text, spec, key[0], key[1]) if key in expect_keys else []
            if text in seen:
                problem.append("与本指令其他条重复")
            if behavior != REFERENCE_BEHAVIOR:
                reference = copied_from_reference(text)
                if reference:
                    problem.append(f"与范例帽子交的句子过于相似（{reference}），照搬了句子骨架，请换一种写法")
            seen.add(text)
            if problem:
                errors.append((behavior, key, problem, text))
    return spec, groups, errors


def group_cid_premise(group, index: int) -> tuple:
    """取某组某条的 cid 数值与前提"""
    if isinstance(group, int):
        return 1000 + group * 100 + index, f"{TIER_PREMISE[group]}&t_unconscious_flag_0"
    if group == GENERAL_GROUP:
        return 1500 + index, f"t_unconscious_flag_0"
    return 2000 + VARIANT_LIST.index(group) * 100 + index, f"{VARIANT_PREMISE[group]}"


def build_csv(type_id: str, rows: list) -> str:
    """拼出整份 CSV 文本；rows 为 [(组, 序号, 文本)]，各组之间空一行"""
    out = HEADER
    last_group = None
    for group, index, text in rows:
        if group != last_group:
            out += "\r\n"
            last_group = group
        cid, premise = group_cid_premise(group, index)
        out += f"{cid},{type_id},0,{premise},{text}\r\n"
    return out


if __name__ == "__main__":
    behavior_list = [arg for arg in sys.argv[2:] if not arg.startswith("--")]
    if "--all" in sys.argv:
        behavior_list = sorted(behavior for behavior in load_all_specs() if os.path.exists(os.path.join(SRC_DIR, behavior + ".txt")))
    # 临时追加的规则只对单个行为有意义，混在多个行为或 --all 里容易把一个指令的豁免带给别的指令
    if (ADD_EXTRA or ADD_FORBIDDEN) and len(behavior_list) != 1:
        print("--add-extra / --add-forbidden 只能配合单个行为id使用")
        sys.exit(1)
    # 只看规则：打印所列行为生效的 spec 块（含临时追加项）后退出
    if "--show-spec" in sys.argv:
        for behavior in behavior_list:
            print(json.dumps({behavior: load_spec(behavior)}, ensure_ascii=False, indent=2))
        sys.exit(0)
    all_errors = []
    outputs = {}
    for behavior in behavior_list:
        spec, groups, errors = load_behavior(behavior)
        all_errors += errors
        counts = {segment: sum(len(groups.get((group, segment), [])) for group in GROUP_LIST) for segment in SEGMENT_LIST}
        print(behavior, counts, f"问题 {len(errors)} 处")
        # 先算好全部内容，全部校验通过后再写文件
        for segment in SEGMENT_LIST:
            rows = [(group, i, text) for group in GROUP_LIST for i, text in enumerate(groups.get((group, segment), []))]
            rel_path = f"action_{segment}/{spec['dir']}/{behavior}_{segment}.csv"
            outputs[rel_path] = build_csv(f"action_part_{behavior}_{segment[0]}", rows)
    for error in all_errors[:200]:
        print(error)
    if len(all_errors) > 200:
        print(f"……另有 {len(all_errors) - 200} 处未列出")
    print(f"问题 {len(all_errors)} 处")
    if all_errors:
        sys.exit(1)
    if CHECK_ONLY:
        sys.exit(0)
    for rel_path, content in outputs.items():
        path = os.path.join(ROOT, "data", "talk_common", rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        print(rel_path)
