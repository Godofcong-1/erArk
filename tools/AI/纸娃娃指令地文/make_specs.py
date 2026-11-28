# -*- coding: UTF-8 -*-
"""生成 spec.json：以行为id为键，每个指令一块，记录部位短词、服装占位符、豁免词、额外禁用词与语义说明

用法: .conda\\python.exe tools/AI/纸娃娃指令地文/make_specs.py [--force]
已存在的 spec 块默认不覆盖（里面可能已合并过子代理提议的 extra / forbidden），--force 时覆盖

合并子代理提议的追加项（子代理自己不改 spec.json）:
    .conda\\python.exe tools/AI/纸娃娃指令地文/make_specs.py --merge=<文件>
    文件是工作流返回的 spec_add 列表：[{"behavior": 行为id, "extra": [...], "forbidden": [...], "reason": "理由"}]
    只增不删，已有的项跳过；每块记一条 changes。只做合并，不补 TABLE 里缺的块
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(HERE, "spec.json")
FORCE = "--force" in sys.argv

# 帽子这一格有发卡、发箍、发绳、头花、头盔、护目镜、兜帽、面罩等，只写戴在头上时的磨蹭
HAT_FORBIDDEN = ["帽", "檐", "内衬", "布料", "织物", "金属", "毛绒", "皮质", "摘下", "取下", "戴回", "装饰", "发卡", "发箍", "头盔", "罩进", "塞进", "套住", "裹住", "罩住"]
WEAPON_FORBIDDEN = ["刀刃", "剑刃", "刀身", "剑身", "刀鞘", "剑鞘", "枪管", "枪口", "枪身", "扳机", "弓弦", "箭", "弹匣", "刀锋", "剑锋"]
CLOTH_NOTE = "服装交：阴茎与她此刻穿戴着的这件衣物摩擦。动笔前按写作指南 5.3 调查这一格实际有哪些衣物，只写各种衣物都说得通的动作，把只属于某类衣物的形制、材质、部件补进 forbidden。"

# 行为id: (显示名, 目录, 主部位, 额外部位, 服装占位符, 字面部位词, 是否必须写阴茎, 豁免词, 额外禁用词, 说明)
TABLE = {
    "handjob": ("手交", "wait_upon", ["hands"], [], [], [], True, [], [], "她用手套弄、揉搓、撸动阴茎。"),
    "blowjob": ("口交", "wait_upon", ["mouth"], [], [], [], True, [], [], "她用嘴含住阴茎吞吐、舔舐、吮吸；不是深喉，不顶进喉咙深处。"),
    "paizuri": ("乳交", "wait_upon", ["breast"], [], [], [], True, [], [], "阴茎夹在她的双乳之间摩擦；不预设胸的大小，交给 {breast} 占位符。"),
    "footjob": ("足交", "wait_upon", ["feet"], ["legs"], [], [], True, ["脚"], [], "她用双脚夹住、踩踏、揉搓阴茎。可以写脚；不预设她穿没穿袜子、鞋子（袜、鞋仍禁用）。"),
    "hairjob": ("发交", "wait_upon", ["hair"], [], [], [], True, [], [], "用她的头发缠绕、包裹阴茎摩擦；不预设头发长短与发色。"),
    "axillajob": ("腋交", "wait_upon", ["armpit"], [], [], [], True, [], [], "阴茎夹在她的腋下抽送摩擦。"),
    "rub_buttock": ("素股", "wait_upon", ["vagina", "legs"], ["clitoris"], [], ["臀"], True, [], ["插进", "插入"], "素股：阴茎夹在她的大腿根或臀缝之间，贴着阴唇来回摩擦，不插入。"),
    "hand_blowjob": ("手交口交", "wait_upon", ["hands", "mouth"], [], [], [], True, [], [], "一边用手撸动茎身，一边用嘴含住龟头吮吸舔舐，手口并用。"),
    "tits_blowjob": ("乳交口交", "wait_upon", ["breast", "mouth"], [], [], [], True, [], [], "阴茎夹在她的双乳之间摩擦，同时她低头含住从乳间露出的龟头。"),
    "focus_blowjob": ("真空口交", "wait_upon", ["mouth"], ["throat"], [], [], True, [], [], "真空口交：她双颊凹陷，用力把口腔吸成真空，紧紧吸住阴茎强力吮吸吞吐。"),
    "deep_throat": ("深喉插入", "wait_upon", ["throat", "mouth"], [], [], [], True, [], [], "阴茎深深顶进她的喉咙，整根没入，喉咙被撑开。"),
    "sixty_nine": ("六九式", "wait_upon", ["mouth", "vagina"], ["clitoris"], [], [], False, [], [], "六九式：两人头尾相对互相口交，她含着阴茎吞吐，博士同时舔弄她的小穴与阴蒂。B1 写博士舔她（可以不写阴茎），B2 写她口交。"),
    "legjob": ("腿交", "wait_upon", ["legs"], [], [], [], True, [], [], "阴茎夹在她并拢的大腿之间抽送摩擦（不是素股，不贴着阴唇）。"),
    "tailjob": ("尾交", "wait_upon", [], [], [], ["尾"], True, [], [], "用她的尾巴缠绕、包裹阴茎摩擦。尾巴的种类与形状因干员而异（毛茸茸、鳞片、细长等），只写各种尾巴都说得通的动作，不写毛色与材质。"),
    "face_rub": ("阴茎蹭脸", "wait_upon", ["face"], [], [], [], True, [], [], "阴茎在她的脸上磨蹭、拍打、滑过脸颊与唇边，不插进嘴里。"),
    "horn_rub": ("阴茎蹭角", "wait_upon", [], [], [], ["角"], True, [], [], "阴茎在她头上的角上磨蹭。角的形状因干员而异（龙角、羊角、鹿角、独角等），只写各种角都说得通的动作。注意「角」字也出现在嘴角、角度等词里，每条都要真的写到她的角。"),
    "ears_rub": ("阴茎蹭耳朵", "wait_upon", [], [], [], ["耳"], True, [], [], "阴茎在她的兽耳上磨蹭（她有兽耳）。兽耳形状因干员而异，只写各种兽耳都说得通的动作。"),
    "clean_blowjob": ("清洁口交", "wait_upon", ["mouth"], [], [], [], True, [], [], "清洁口交：射精之后，博士的阴茎沾满精液与两人的体液，她用嘴把它舔舐、含吮干净。是事后清理，不是为了让他射；可以写他被舔得又硬起来。"),
    "hat_job": ("帽子交", "wait_upon", [], [], ["{TargetHatName}"], [], True, [], HAT_FORBIDDEN, CLOTH_NOTE + "头部这一格一半不是帽子，一律写戴在头上时的磨蹭，不摘下。"),
    "glasses_job": ("眼镜交", "wait_upon", [], ["face"], ["{TargetGlassesName}"], [], True, [], [], CLOTH_NOTE),
    "ear_ornament_job": ("耳饰交", "wait_upon", [], [], ["{TargetEarDecoName}"], [], True, [], [], CLOTH_NOTE),
    "neck_ornament_job": ("脖饰交", "wait_upon", [], [], ["{TargetNeckDecoName}"], [], True, [], [], CLOTH_NOTE),
    "mouth_ornament_job": ("口罩交", "wait_upon", [], ["mouth", "face"], ["{TargetMouthDecoName}"], [], True, [], [], CLOTH_NOTE),
    "top_job": ("上衣交", "wait_upon", [], ["breast"], ["{TargetUpClothName}"], [], True, [], [], CLOTH_NOTE),
    "corset_job": ("胸衣交", "wait_upon", [], ["breast"], ["{TargetBraName}"], [], True, [], [], CLOTH_NOTE),
    "gloves_job": ("手套交", "wait_upon", [], ["hands"], ["{TargetGloveName}"], [], True, [], [], CLOTH_NOTE),
    "skirt_job": ("裙子交", "wait_upon", [], ["legs"], ["{TargetSkiName}"], [], True, ["裙"], [], CLOTH_NOTE),
    "underwear_job": ("内裤交", "wait_upon", [], ["vagina"], ["{TargetPanName}"], [], True, [], [], CLOTH_NOTE),
    "socks_job": ("袜子交", "wait_upon", [], ["legs", "feet"], ["{TargetSocName}"], [], True, ["脚", "袜"], [], CLOTH_NOTE),
    "shoes_job": ("鞋子交", "wait_upon", [], ["feet"], ["{TargetShoeName}"], [], True, ["脚", "鞋"], [], CLOTH_NOTE),
    "weapons_job": ("武器交", "wait_upon", [], ["hands"], ["{TargetWeaponName}"], [], True, [], WEAPON_FORBIDDEN, CLOTH_NOTE + "武器种类各异（刀剑、枪械、弩、法杖、盾、锤等），不写任何具体形制。"),
    "trousers_job": ("裤子交", "wait_upon", [], ["legs"], ["{TargetDownClothName}"], [], True, [], [], CLOTH_NOTE),
}

# 插入类：体位 x 插入部位
POSITION_LIST = [
    ("normal", "正常位"), ("back", "背后位"), ("riding", "对面骑乘位"), ("back_riding", "背面骑乘位"),
    ("face_seat", "对面座位"), ("back_seat", "背面座位"), ("face_stand", "对面立位"), ("back_stand", "背面立位"),
    ("face_hug", "对面抱位"), ("back_hug", "背面抱位"), ("face_lay", "对面卧位"), ("back_lay", "背面卧位"),
]
INSERT_KIND = {
    # 后缀: (行为id后缀, 名称后缀, 目录, 主部位, 额外部位, 说明)
    "sex": ("_sex", "", "insert_v", ["vagina"], ["clitoris", "womb", "breast", "legs"], "阴茎插入她的小穴抽插。"),
    "anal_sex": ("_anal_sex", "肛交", "insert_a", ["anal"], ["breast", "legs"], "阴茎插入她的后穴抽插。"),
    "cervix_sex": ("_cervix_sex", "子宫口姦", "insert_w", ["womb", "vagina"], ["breast", "legs"], "阴茎插进小穴最深处，龟头挤进子宫口（宫颈）抽插研磨，没有整根进入子宫。"),
    "womb_sex": ("_womb_sex", "子宫姦", "insert_w", ["womb"], ["vagina", "breast", "legs"], "阴茎贯穿子宫口，整根插进子宫里抽插。"),
    "urethral_sex": ("_urethral_sex", "尿道姦", "insert_u", ["urethra"], ["vagina", "clitoris", "breast", "legs"], "阴茎插进她的尿道抽插（游戏设定中可行），尿道被撑开。"),
}
for kind, (suffix, name_suffix, folder, main, extra, kind_note) in INSERT_KIND.items():
    for position, position_name in POSITION_LIST:
        behavior = position + suffix
        # 背后位在后穴、子宫口、子宫、尿道里叫后背位
        display = position_name if kind == "sex" else position_name.replace("背后位", "后背位") + name_suffix
        TABLE[behavior] = (display, folder, main, extra, [], [], True, [], [], f"{kind_note}体位为{position_name.replace('后背位', '背后位')}，见写作指南 5.1。")
TABLE["stimulate_g_point"] = ("刺激G点", "insert_v", ["vagina"], ["clitoris", "breast"], [], [], True, [], [], "阴茎插在她的小穴里，专门调整角度反复顶弄、碾磨小穴前壁的G点。体位不限，不要写死。")
TABLE["womb_os_caress"] = ("玩弄子宫口", "insert_w", ["womb", "vagina"], ["breast"], [], [], True, [], [], "阴茎插到小穴最深处，龟头抵着子宫口研磨、顶弄、画圈玩弄，不插进子宫。体位不限，不要写死。")
TABLE["stimulate_sigmoid_colon"] = ("玩弄s状结肠", "insert_a", ["anal"], ["breast"], [], [], True, [], [], "阴茎深深插进她的后穴，越过直肠顶到S状结肠的弯折处反复顶弄。体位不限，不要写死。")
TABLE["stimulate_vagina"] = ("隔着刺激阴道", "insert_a", ["anal", "vagina"], ["clitoris", "breast"], [], [], True, [], [], "阴茎插在她的后穴里，隔着一层肉壁顶弄、刺激小穴；插的是后穴，不是小穴。体位不限，不要写死。")



def dump_specs(spec_map: dict) -> str:
    """把全部 spec 序列化成文本：按行为id排序，每个指令一块，块内一个字段一行（便于用 Edit 只改自己那一块，diff 也好读）

    参数:
        spec_map (dict): {行为id: spec 字典}
    返回:
        str: 可直接写入 spec.json 的文本
    """
    block_list = []
    for behavior in sorted(spec_map):
        # 一个字段一行：值用单行 JSON，列表也不换行
        field_list = [f"    {json.dumps(key, ensure_ascii=False)}: {json.dumps(value, ensure_ascii=False)}" for key, value in spec_map[behavior].items()]
        block_list.append(f"  {json.dumps(behavior, ensure_ascii=False)}: {{\n" + ",\n".join(field_list) + "\n  }")
    return "{\n" + ",\n".join(block_list) + "\n}\n"


def merge_spec_add(spec_map: dict, add_list: list) -> list:
    """把子代理提议的追加项合并进 spec_map（原地修改，只增不删），返回每块的合并说明

    参数:
        spec_map (dict): {行为id: spec 字典}
        add_list (list): [{"behavior", "extra", "forbidden", "reason"}]
    返回:
        list: 实际有新增的块的说明文字；行为id不存在时抛 KeyError（调用方此时还没写文件）
    """
    report_list = []
    for add in add_list:
        spec = spec_map[add["behavior"]]
        part_list = []
        for key in ("extra", "forbidden"):
            # dict.fromkeys 去掉输入里自身的重复，保留先后顺序
            new_values = [value for value in dict.fromkeys(add.get(key, [])) if value not in spec[key]]
            if new_values:
                spec[key] += new_values
                part_list.append(f"{key} 增加{'、'.join(f'「{value}」' for value in new_values)}")
        if not part_list:
            continue
        change = "；".join(part_list) + f"：{add.get('reason', '')}"
        spec["changes"].append(change)
        report_list.append(f"{add['behavior']}  {change}")
    return report_list


if __name__ == "__main__":
    # 读入已有的 spec.json（合并过子代理提议的块要保留）
    spec_map = {}
    if os.path.exists(SPEC_FILE):
        with open(SPEC_FILE, encoding="utf-8") as f:
            spec_map = json.load(f)
    # 合并模式：只合并追加项，算好全部内容后再写文件
    merge_path = next((arg[len("--merge=") :] for arg in sys.argv if arg.startswith("--merge=")), "")
    if merge_path:
        with open(merge_path, encoding="utf-8") as f:
            report_list = merge_spec_add(spec_map, json.load(f))
        content = dump_specs(spec_map)
        with open(SPEC_FILE, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        for report in report_list:
            print(report)
        print(f"合并了 {len(report_list)} 块")
        sys.exit(0)
    written = 0
    for behavior, (name, folder, main, extra, items, literals, penis_required, allow_words, forbidden, notes) in TABLE.items():
        if behavior in spec_map and not FORCE:
            continue
        spec_map[behavior] = {
            "name": name,
            "dir": folder,
            "main": main,
            "extra": extra,
            "items": items,
            "literals": literals,
            "penis_required": penis_required,
            "allow_words": allow_words,
            "forbidden": forbidden,
            "notes": notes,
            "changes": [],
        }
        written += 1
    # 先算好全部内容再打开文件（open(w) 会先清空，算错就会截空）
    content = dump_specs(spec_map)
    with open(SPEC_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"共 {len(TABLE)} 个指令，本次写入 {written} 块 spec，spec.json 现有 {len(spec_map)} 块")
