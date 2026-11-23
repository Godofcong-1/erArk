#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调用 OpenAI 图像模型（默认 gpt-image-2.5-sunburst）生成指定角色的立绘

用法示例：
    .conda\\python.exe tools/generate_character_portrait.py 阿米娅
    .conda\\python.exe tools/generate_character_portrait.py 阿米娅 凯尔希 --n 2
    .conda\\python.exe tools/generate_character_portrait.py 0001 --variant 半身 --extra "手持法杖"
    .conda\\python.exe tools/generate_character_portrait.py 阿米娅 --use-existing
    .conda\\python.exe tools/generate_character_portrait.py 阿米娅 --dry-run

角色参数可以是角色名，也可以是 data/character 下 CSV 的编号（如 0001）
角色外貌信息（种族、职业、身体素质、服装、介绍）自动从角色 CSV 读取并拼入提示词

儿童版模式（--child）：把一张立绘改画成该角色儿童时期的全身立绘
    .conda\\python.exe tools/generate_character_portrait.py --child image/美术风格参考图/阿达克利斯.png
    .conda\\python.exe tools/generate_character_portrait.py --child 阿达克利斯 --extra "鞋子是黑色防水短靴" --n 2
    .conda\\python.exe tools/generate_character_portrait.py --child 阿达克利斯 --dry-run
    - 参数是原图路径，或角色名/种族名（依次在 image/美术风格参考图、image/立绘 下找同名图）；裸体、内衣类差分不接受
    - 第1张输入是铺白底的原图，画风、外貌、服装、姿势、肤色都以它为准，只把年龄改小（默认约 8 岁，--age 可改）
    - 第2张输入是已拼好的比例对照表 tools/儿童立绘参考/儿童参考对照表.png（该目录下的儿童立绘裁出人物、统一身高后拼成），只用于理解儿童的年龄感与身体比例
    - 参考图有增删时加 --rebuild-child-ref-sheet，用目录中的参考图重新拼接并覆盖对照表
    - 提示词内置了从这些参考图总结出的儿童特征，--extra 只需写本角色的姿势、鞋子、肤色等细节
    - 结果保存为 <角色名>_小_全身_<时间>_<序号>.png，另存一张"原图 | 结果 | 标杆"的白底对比图

API 密钥读取顺序：环境变量 OPENAI_API_KEY > 仓库根目录 ai_chat_api_key.csv 的 OPENAI_API_KEY 行
接口地址读取顺序：--base-url > 环境变量 OPENAI_BASE_URL > ai_chat_api_key.csv 的 OPENAI_BASE_URL 行（都没有则用官方地址）
生成结果默认保存到 tools/output/立绘生成/<角色名>/，不会直接写入 image/立绘
"""

import argparse
import base64
import csv
import io
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import openai
from PIL import Image

# 仓库根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
# 角色 CSV 目录
CHARACTER_DIR = ROOT_DIR / "data" / "character"
# 配置表目录（性别/种族/职业/素质）
CSV_DIR = ROOT_DIR / "data" / "csv"
# 现有立绘根目录
PORTRAIT_DIR = ROOT_DIR / "image" / "立绘"
# API 密钥文件
API_KEY_CSV = ROOT_DIR / "ai_chat_api_key.csv"
# 默认输出目录
DEFAULT_OUTPUT_DIR = ROOT_DIR / "tools" / "output" / "立绘生成"
# 默认模型
DEFAULT_MODEL = "gpt-image-2.5-sunburst"

# 与外貌相关的身体素质编号范围（年龄段、兽耳兽角、胸臀腿足等）
BODY_TALENT_ID_RANGE = range(101, 133)

# 差分名对应的画面描述，未列出的差分名直接作为描述使用
VARIANT_PROMPTS = {
    "全身": "全身立绘，从头顶到脚底完整入画，自然站姿，人物居中，四周留少量空白",
    "半身": "半身立绘，腰部以上入画，人物居中，面向观者",
    "笑脸": "全身立绘，从头顶到脚底完整入画，自然站姿，表情是明朗的笑容",
    "愉快": "全身立绘，从头顶到脚底完整入画，自然站姿，表情愉快轻松",
    "不爽": "全身立绘，从头顶到脚底完整入画，自然站姿，表情不耐烦、有些不爽",
    "愤怒": "全身立绘，从头顶到脚底完整入画，自然站姿，表情愤怒",
}

# 儿童版模式：按名字查找原图时最先查找的目录（按种族命名的角色图）
STYLE_REF_DIR = ROOT_DIR / "image" / "美术风格参考图"
# 儿童立绘参考目录：存放儿童立绘参考图，以及由它们拼好的比例对照表（只供模型理解儿童的年龄感与身体比例）
DEFAULT_CHILD_REF_DIR = ROOT_DIR / "tools" / "儿童立绘参考"
# 参考目录中已拼好的比例对照表文件名；重新拼接时要把它排除在参考图之外
CHILD_REF_SHEET_NAME = "儿童参考对照表.png"
# 用户认可的儿童年龄感标杆（卡普里尼儿童版），生成后与原图、结果一起拼进对比图
CHILD_BENCHMARK_NAME = "女儿_埃拉菲亚_全身.png"
# 儿童版原图文件名中不允许出现的词：裸体、内衣类差分不能作为儿童版的原图
CHILD_FORBIDDEN_SOURCE_WORDS = ("裸", "内裤", "内衣", "胸衣", "袜子")
# 可读取的图片后缀
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")
# 儿童参考对照表的排版：每人统一缩放到的身高、每行最多人数、间距（像素）
REF_SHEET_FIGURE_HEIGHT = 640
REF_SHEET_COLUMNS = 5
REF_SHEET_GAP = 32
# 裁出人物范围时视为实心的最低 alpha，不高于它的多为抠图残留的淡光晕
FIGURE_ALPHA_THRESHOLD = 32
# 对比图中每张图统一缩放到的高度、图与图之间灰色细缝的宽度（像素）
COMPARE_HEIGHT = 1024
COMPARE_GAP = 8

# 儿童的共同特征：总结自 tools/儿童立绘参考 中的儿童立绘，参考图大改时需要同步更新
# {head_ratio} 由目标年龄决定；不要改写成"写实比例/5.5头身/不要大眼睛"，实测会显老
CHILD_FEATURE_LINES = [
    "{head_ratio}，头部相对身体明显偏大，身材矮小",
    "圆脸，脸颊饱满，额头宽，下巴短小圆润，下颌线柔和；眼睛较大、明亮且睁开，位置在头部高度一半附近；鼻子和嘴巴小巧",
    "脖子短而细，肩膀窄，躯干短而平直，没有腰线和成年人的身体曲线，胯部窄，小肚子微微圆起",
    "手臂和腿短而直，线条柔和，膝盖和肌肉不明显，手脚小巧",
    "站姿自然放松：双脚平放在地面、并拢或微微分开，重心居中，不交叉双腿，不扭胯，不摆成熟的模特姿势",
    "神情天真、带孩子气（安静、害羞或好奇都可以），不要成熟冷淡或妩媚的神情，不要垂眼",
    "衣服相对身体略显宽大（袖口、外套、斗篷都像大了一号），不贴身",
]


def load_name_table(csv_path, name_col):
    """
    读取配置表，建立编号到名字的映射
    参数：
        csv_path (Path): 配置表路径
        name_col (int): 名字所在列的下标
    返回值：dict[int, str] - 编号 -> 名字
    """
    table = {}
    if not csv_path.exists():
        return table
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        # 表头下方的类型提示行（如 0,1,0,0）也以数字开头，但真实数据在其后，同编号会被覆盖掉
        for row in csv.reader(f):
            if len(row) > name_col and row[0].isdigit() and row[name_col]:
                table[int(row[0])] = row[name_col]
    return table


def load_config_tables():
    """
    读取拼提示词要用到的各张配置表
    参数：无
    返回值：dict[str, dict[int, str]] - 表名 -> (编号 -> 名字)
    """
    return {
        "sex": load_name_table(CSV_DIR / "SexTem.csv", 1),
        "race": load_name_table(CSV_DIR / "Race.csv", 1),
        "profession": load_name_table(CSV_DIR / "Profession.csv", 1),
        "talent": load_name_table(CSV_DIR / "Talent.csv", 2),
    }


def find_character_csv(key):
    """
    根据角色名或编号查找角色 CSV 文件
    参数：
        key (str): 角色名（如 阿米娅）或编号（如 0001 / 1）
    返回值：Path | None - 找到的 CSV 路径，找不到返回 None
    """
    # 按编号匹配文件名前缀
    if key.isdigit():
        prefix = f"{int(key):04d}_"
        for path in CHARACTER_DIR.glob(f"{prefix}*.csv"):
            return path
        return None
    # 按文件名中的角色名精确匹配
    for path in CHARACTER_DIR.glob("*.csv"):
        parts = path.stem.split("_", 1)
        if len(parts) == 2 and parts[1] == key:
            return path
    return None


def lookup_name(table, value):
    """
    按编号在配置表里查名字
    参数：
        table (dict[int, str]): 编号 -> 名字
        value (str): CSV 中的编号字符串
    返回值：str - 查到的名字，查不到返回空字符串
    """
    return table.get(int(value), "") if value.isdigit() else ""


def load_character_info(csv_path, tables):
    """
    从角色 CSV 中提取生成立绘所需的外貌信息
    参数：
        csv_path (Path): 角色 CSV 路径
        tables (dict[str, dict[int, str]]): load_config_tables 返回的配置表
    返回值：dict - 包含 name / sex / race / profession / introduce / body_traits / clothes 的字典
    """
    info = {"name": "", "sex": "", "race": "", "profession": "", "introduce": "", "body_traits": [], "clothes": []}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))[2:]
    for row in rows:
        if not row:
            continue
        # 补齐列数，避免个别行缺列
        key, _, value, _, _ = (row + [""] * 5)[:5]
        if key == "Name":
            info["name"] = value
        # 性别/种族/职业：CSV 备注列写法不统一，一律按编号查配置表
        elif key == "Sex":
            info["sex"] = lookup_name(tables["sex"], value)
        elif key == "Race":
            info["race"] = lookup_name(tables["race"], value)
        elif key == "Profession":
            info["profession"] = lookup_name(tables["profession"], value)
        elif key == "Introduce_1":
            info["introduce"] = value
        # 身体素质：只取外貌相关的编号段
        elif key.startswith("T|"):
            talent_id = key[2:]
            talent_name = lookup_name(tables["talent"], talent_id)
            if talent_name and int(talent_id) in BODY_TALENT_ID_RANGE and value != "0":
                info["body_traits"].append(talent_name)
        # 服装：去掉"必带"等标记，同名衣物（如连衣裙同时占上下衣位）只保留一次
        elif key.startswith("C|") and value:
            cloth_name = value.replace("必带", "").strip()
            if cloth_name not in info["clothes"]:
                info["clothes"].append(cloth_name)
    if not info["name"]:
        info["name"] = csv_path.stem.split("_", 1)[-1]
    return info


def find_existing_portrait(name):
    """
    在 image/立绘 下查找该角色已有的立绘，用作参考图
    参数：
        name (str): 角色名
    返回值：Path | None - 优先返回全身图，其次半身图，再次同名图
    """
    for file_name in (f"{name}_全身.png", f"{name}_半身.png", f"{name}.png"):
        for path in PORTRAIT_DIR.rglob(file_name):
            return path
    return None


def build_prompt(info, variant, extra, transparent):
    """
    拼接图像生成提示词
    参数：
        info (dict): load_character_info 返回的角色信息
        variant (str): 差分名（全身/半身/笑脸...）
        extra (str): 用户追加的描述
        transparent (bool): 是否要求透明背景
    返回值：str - 完整提示词
    """
    lines = [
        f"为游戏《明日方舟》（Arknights）的角色「{info['name']}」绘制一张角色立绘。",
        "画风：明日方舟官方立绘风格的二次元插画，精细线稿，干净的赛璐璐上色配合柔和的明暗过渡，高完成度。",
        f"构图：{VARIANT_PROMPTS.get(variant, variant)}。",
    ]
    # 角色基础设定
    base_parts = []
    if info["sex"]:
        base_parts.append(f"性别{info['sex']}")
    if info["race"]:
        base_parts.append(f"种族为泰拉世界的{info['race']}")
    if info["profession"]:
        base_parts.append(f"职业定位是{info['profession']}")
    if base_parts:
        lines.append("角色设定：" + "，".join(base_parts) + "。")
    if info["body_traits"]:
        lines.append("外貌特征：" + "、".join(info["body_traits"]) + "。")
    if info["clothes"]:
        lines.append("服装：" + "、".join(info["clothes"]) + "。")
    if info["introduce"]:
        lines.append(f"人物介绍（用于把握气质）：{info['introduce']}")
    if extra:
        lines.append(f"额外要求：{extra}")
    # 背景与禁止项
    lines.append("背景：完全透明，只保留人物本身。" if transparent else "背景：纯白色，无任何场景元素。")
    lines.append("画面中不要出现任何文字、签名、水印、边框或分镜。")
    return "\n".join(lines)


def display_path(path):
    """
    把路径转成便于阅读的形式
    参数：
        path (Path): 文件或目录路径
    返回值：str - 在仓库内时返回相对仓库根目录的路径，否则返回原路径
    """
    try:
        return str(path.resolve().relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def resolve_child_source(key):
    """
    解析儿童版模式的原图
    参数：
        key (str): 原图路径，或角色名/种族名
    返回值：tuple[Path, str] | None - (原图路径, 角色名)，找不到返回 None；给路径时角色名取文件名第一个"_"之前的部分
    """
    # 直接给出的图片路径：相对路径先按当前目录解析，再按仓库根目录解析
    for path in (Path(key), ROOT_DIR / key):
        if path.is_file():
            return path.resolve(), path.stem.split("_")[0]
    # 按名字查找：先查美术风格参考图目录，再查 image/立绘 下的现有立绘
    for suffix in IMAGE_SUFFIXES:
        path = STYLE_REF_DIR / f"{key}{suffix}"
        if path.is_file():
            return path, key
    existing = find_existing_portrait(key)
    return (existing, key) if existing else None


def load_flat_image(path, crop=False):
    """
    读取图片并铺到白底上，去掉透明通道（部分 PNG 的透明像素里残留着杂色，接口若丢弃 alpha 通道就会被模型看到）
    参数：
        path (Path): 图片路径
        crop (bool): 是否先裁到人物范围（忽略 alpha 不高于 FIGURE_ALPHA_THRESHOLD 的淡光晕）
    返回值：PIL.Image.Image - RGB 图片
    """
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
    if crop:
        bbox = rgba.getchannel("A").point(lambda alpha: 255 if alpha > FIGURE_ALPHA_THRESHOLD else 0).getbbox()
        if bbox:
            rgba = rgba.crop(bbox)
    canvas = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    canvas.alpha_composite(rgba)
    return canvas.convert("RGB")


def resize_to_height(image, height):
    """
    按比例把图片缩放到指定高度
    参数：
        image (PIL.Image.Image): 图片
        height (int): 目标高度（像素）
    返回值：PIL.Image.Image - 缩放后的图片
    """
    width = max(1, round(image.width * height / image.height))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def image_to_png_bytes(image):
    """
    把图片编码为 PNG 二进制，用于直接上传
    参数：
        image (PIL.Image.Image): 图片
    返回值：bytes - PNG 数据
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def build_child_ref_sheet(paths):
    """
    把儿童参考图裁出人物、统一身高后拼成一张白底比例对照表
    参数：
        paths (list[Path]): 参考图路径
    返回值：PIL.Image.Image - 对照表图片
    """
    figures = [resize_to_height(load_flat_image(path, crop=True), REF_SHEET_FIGURE_HEIGHT) for path in paths]
    # 行数按每行最多 REF_SHEET_COLUMNS 人计算，再把人数平均分到各行
    row_count = math.ceil(len(figures) / REF_SHEET_COLUMNS)
    per_row = math.ceil(len(figures) / row_count)
    rows = [figures[i : i + per_row] for i in range(0, len(figures), per_row)]
    row_widths = [sum(figure.width for figure in row) + REF_SHEET_GAP * (len(row) - 1) for row in rows]
    sheet_size = (max(row_widths) + REF_SHEET_GAP * 2, len(rows) * (REF_SHEET_FIGURE_HEIGHT + REF_SHEET_GAP) + REF_SHEET_GAP)
    sheet = Image.new("RGB", sheet_size, (255, 255, 255))
    # 各行水平居中，所有人头顶和脚底对齐
    y = REF_SHEET_GAP
    for row, row_width in zip(rows, row_widths):
        x = (sheet.width - row_width) // 2
        for figure in row:
            sheet.paste(figure, (x, y))
            x += figure.width + REF_SHEET_GAP
        y += REF_SHEET_FIGURE_HEIGHT + REF_SHEET_GAP
    return sheet


def prepare_child_ref_sheet(args):
    """
    读取参考目录中已拼好的儿童参考对照表；指定 --rebuild-child-ref-sheet 时先用目录中的参考图重新拼接并覆盖保存
    参数：
        args (argparse.Namespace): 命令行参数
    返回值：tuple[Path, PIL.Image.Image | None] - (对照表路径, 对照表图片)，没有对照表时图片为 None
    """
    ref_dir = Path(args.child_ref_dir)
    sheet_path = ref_dir / CHILD_REF_SHEET_NAME
    # 重新拼接：对照表本身也放在参考目录里，必须排除，否则会把旧对照表当成一张参考图拼进去
    if args.rebuild_child_ref_sheet:
        ref_paths = [path for path in sorted(ref_dir.iterdir()) if path.suffix.lower() in IMAGE_SUFFIXES and path.name != CHILD_REF_SHEET_NAME] if ref_dir.is_dir() else []
        if ref_paths:
            sheet = build_child_ref_sheet(ref_paths)
            sheet.save(sheet_path)
            print(f"已用 {len(ref_paths)} 张参考图重新拼接对照表（{sheet.width}x{sheet.height}）：{display_path(sheet_path)}")
            return sheet_path, sheet
        print(f"未在 {ref_dir} 找到儿童参考图，无法重新拼接对照表")
    if not sheet_path.is_file():
        print(f"未找到儿童参考对照表 {sheet_path}，只用提示词里的儿童特征总结（可加 --rebuild-child-ref-sheet 用参考图重新拼接）")
        return sheet_path, None
    sheet = load_flat_image(sheet_path)
    print(f"儿童参考对照表（{sheet.width}x{sheet.height}）：{display_path(sheet_path)}")
    return sheet_path, sheet


def child_head_ratio(age):
    """
    按目标年龄给出头身比的写法
    参数：
        age (int): 目标年龄
    返回值：str - 头身比描述
    """
    if age <= 5:
        return "约4头身"
    if age <= 9:
        return "约4.5头身"
    return "约5头身"


def build_child_prompt(name, race, sex, age, has_sheet, extra, transparent):
    """
    拼接儿童版提示词：画风、外貌、服装、姿势以第1张原图为准，第2张对照表只用于理解儿童的年龄感与身体比例
    参数：
        name (str): 角色名（按种族命名的图则为种族名）
        race (str): 种族名，未知时为空字符串
        sex (str): 性别名，为"男"时按男孩描述，其余按女孩描述
        age (int): 目标年龄
        has_sheet (bool): 是否附带儿童参考对照表（第2张图）
        extra (str): 本角色的补充要求
        transparent (bool): 是否要求透明背景
    返回值：str - 完整提示词
    """
    pronoun, child_word = ("他", "小男孩") if sex == "男" else ("她", "小女孩")
    lines = [f"把第1张立绘中的角色「{name}」画成{pronoun}儿童时期（约{age}岁的{child_word}）的全身立绘：同一个人小时候的样子，只把年龄改小，其余一切照第1张。"]
    # 输入图片的分工：第1张决定一切，第2张只提供儿童的年龄感与比例
    if has_sheet:
        lines.append(f"共有两张输入图片。第1张是「{name}」的原版立绘，是本次作画的唯一依据：画风、外貌、服装和姿势都以它为准。")
        lines.append(
            f"第2张是同系列多位角色儿童时期立绘拼成的比例对照表（每个人都缩放到相同身高并排摆放），只用来理解约{age}岁儿童的年龄感和身体比例；"
            "不要借用其中任何人的画风、发型、发色、角、耳朵、服装、配饰、配色、姿势或构图，也不要画成多人并排，只画第1张里的这一个角色。"
        )
    else:
        lines.append(f"第1张是「{name}」的原版立绘，也是唯一的输入图片，是本次作画的唯一依据：画风、外貌、服装和姿势都以它为准。")
    # 画风完全沿用原图：不写任何通用画风描述，否则会被拉向光滑的动画风
    sheet_style_note = "，也不要照搬第2张的画风" if has_sheet else ""
    lines.append(
        "【画风——完全照第1张】线稿的笔触、粗细与虚实，上色与明暗画法，笔刷质感（第1张有速写感、笔触痕迹或排线就同样保留），"
        "色调、饱和度与明暗对比，整体完成度，都与第1张一致，像同一位画师为这个角色画的儿时立绘。"
        f"不要画得比第1张更干净、更光滑、更精致，不要改成通用的日系动画赛璐璐风格{sheet_style_note}。"
        "五官沿用第1张的画法，只按儿童比例调整大小和位置。"
    )
    # 与原图保持一致的部分
    race_note = f"（种族：泰拉世界的{race}）" if race else ""
    lines.append(
        f"【与第1张保持一致】发型、发色、瞳色；耳朵、角、尾巴、光环等种族特征{race_note}，按儿童身材相应缩小；肤色完全相同，不要变深也不要变浅；"
        "服装与配饰的款式、配色、花纹；手臂和手的动作、手里拿的东西、头部角度与视线方向；表情的情绪（在此基础上带着孩子气）。"
    )
    # 儿童特征，以及两种要避开的失败方向
    lines.append("【儿童特征（总结自同系列儿童立绘）】")
    head_ratio = child_head_ratio(age)
    lines.extend(f"- {line.format(head_ratio=head_ratio)}" for line in CHILD_FEATURE_LINES)
    lines.append(
        "【不要】Q版或大头娃娃（3头身左右、四肢短粗、手脚像肉团、五官简化）；"
        "缩小的成年人（修长的腿、细腰、成年人的身体曲线、长脖子、窄长脸、高颧骨、成熟的眼神或妆容）。"
    )
    # 服装、鞋子、构图与背景
    lines.append(
        "【服装】沿用第1张的款式与配色，按儿童身材重新裁剪、略宽松；领口、下摆、裤腰都把身体遮好，不露胸口、腹部和内衣；"
        "暴露或成熟的元素（低领、露脐、紧身、网袜、吊带袜等）改成同款式同配色、适合儿童的样子。"
    )
    # 鞋子：沿用原图款式，只要求平底；浅口鞋、乐福鞋露出脚背可以接受，只有赤脚和露趾凉鞋需要改
    lines.append(
        "【鞋子】平底儿童鞋，款式与颜色沿用第1张，按儿童的脚缩小；第1张有鞋跟就改成平底，浅口鞋、乐福鞋这类露出脚背的平底鞋可以保留；"
        "第1张若是赤脚或露出脚趾的凉鞋，改成同色系、包住脚趾的平底儿童鞋，并符合该角色种族的生活环境。"
    )
    lines.append("【构图】全身立绘，从头顶到脚底完整入画，单人，人物居中，四周留少量空白。")
    lines.append("【背景】完全透明，只保留人物本身。" if transparent else "【背景】纯白色，无任何场景元素。")
    lines.append("画面中不要出现任何文字、签名、水印、边框或分镜。")
    if extra:
        lines.append(f"【本角色的补充要求】{extra}")
    return "\n".join(lines)


def save_compare_image(images, save_path):
    """
    把若干张白底图等高横向拼接成对比图（图与图之间用灰色细缝隔开），便于并排验收
    参数：
        images (list[PIL.Image.Image]): 已铺白底的 RGB 图片，从左到右排列
        save_path (Path): 保存路径
    返回值：无
    """
    scaled = [resize_to_height(image, COMPARE_HEIGHT) for image in images]
    width = sum(image.width for image in scaled) + COMPARE_GAP * (len(scaled) - 1)
    canvas = Image.new("RGB", (width, COMPARE_HEIGHT), (160, 160, 160))
    x = 0
    for image in scaled:
        canvas.paste(image, (x, 0))
        x += image.width + COMPARE_GAP
    canvas.save(save_path)


def load_api_config(cli_base_url):
    """
    读取 API 密钥与接口地址
    参数：
        cli_base_url (str | None): 命令行传入的接口地址
    返回值：tuple[str, str | None] - (api_key, base_url)
    """
    csv_values = {}
    if API_KEY_CSV.exists():
        with open(API_KEY_CSV, "r", encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                if len(row) >= 2:
                    csv_values[row[0].strip()] = row[1].strip()
    # 密钥文件中 OPENAI_* 与 GPT_* 两种行名都认
    api_key = os.environ.get("OPENAI_API_KEY") or csv_values.get("OPENAI_API_KEY") or csv_values.get("GPT_API_KEY", "")
    base_url = cli_base_url or os.environ.get("OPENAI_BASE_URL") or csv_values.get("OPENAI_BASE_URL") or csv_values.get("GPT_BASE_URL") or None
    # 中转地址只写了域名时补上 /v1，SDK 会直接在 base_url 后拼接接口路径
    if base_url and not urllib.parse.urlparse(base_url).path.strip("/"):
        base_url = base_url.rstrip("/") + "/v1"
    return api_key, base_url


def request_images(client, args, prompt, inputs):
    """
    调用图像接口生成图片；有输入图片时走 images.edit，否则走 images.generate
    参数：
        client (openai.OpenAI): 客户端
        args (argparse.Namespace): 命令行参数
        prompt (str): 提示词
        inputs (list[Path | tuple[str, bytes, str]]): 输入图片，可以是文件路径，也可以是 (文件名, 二进制数据, MIME 类型) 元组
    返回值：list[bytes] - 生成的图片二进制数据
    """
    params = {
        "model": args.model,
        "prompt": prompt,
        "size": args.size,
        "quality": args.quality,
        "n": args.n,
        "background": args.background,
        "output_format": "png",
    }
    if inputs:
        # 输入保真度只有编辑接口支持；未指定时不传，中转服务不一定认这个参数
        if args.input_fidelity:
            params["input_fidelity"] = args.input_fidelity
        # SDK 会自行读取路径对应的文件，元组则原样上传
        response = client.images.edit(image=list(inputs), **params)
    else:
        response = client.images.generate(**params)

    # 兼容 b64 与 url 两种返回
    results = []
    for item in response.data:
        if getattr(item, "b64_json", None):
            results.append(base64.b64decode(item.b64_json))
        elif getattr(item, "url", None):
            with urllib.request.urlopen(item.url) as resp:
                results.append(resp.read())
    return results


def call_image_api(client, args, name, prompt, inputs):
    """
    调用图像接口并处理失败情况
    参数：
        client (openai.OpenAI): 客户端
        args (argparse.Namespace): 命令行参数
        name (str): 角色名（用于打印）
        prompt (str): 提示词
        inputs (list[Path | tuple[str, bytes, str]]): 输入图片，见 request_images
    返回值：list[bytes] - 生成的图片二进制数据，失败时为空列表
    """
    print(f"[{name}] 正在调用 {args.model} 生成，请稍候……")
    start = time.time()
    try:
        images = request_images(client, args, prompt, inputs)
    except openai.OpenAIError as e:
        print(f"[{name}] 生成失败：{e}")
        return []
    if not images:
        print(f"[{name}] 接口未返回图片")
        return []
    print(f"[{name}] 生成完成，用时 {time.time() - start:.1f} 秒")
    return images


def save_results(save_dir, base_name, prompt_text, images, name):
    """
    保存生成的图片与提示词
    参数：
        save_dir (Path): 保存目录
        base_name (str): 文件名前缀
        prompt_text (str): 写入 .prompt.txt 的内容
        images (list[bytes]): 生成的图片二进制数据
        name (str): 角色名（用于打印）
    返回值：list[Path] - 保存的图片路径
    """
    save_dir.mkdir(parents=True, exist_ok=True)
    (save_dir / f"{base_name}.prompt.txt").write_text(prompt_text, encoding="utf-8")
    saved_paths = []
    for index, data in enumerate(images, 1):
        save_path = save_dir / f"{base_name}_{index}.png"
        save_path.write_bytes(data)
        print(f"[{name}] 已保存：{save_path}")
        saved_paths.append(save_path)
    return saved_paths


def generate_for_character(client, args, key, tables):
    """
    为单个角色生成立绘并保存
    参数：
        client (openai.OpenAI | None): 客户端，dry-run 时为 None
        args (argparse.Namespace): 命令行参数
        key (str): 角色名或编号
        tables (dict[str, dict[int, str]]): load_config_tables 返回的配置表
    返回值：bool - 是否成功
    """
    # 读取角色信息，找不到 CSV 时仅用名字生成
    csv_path = find_character_csv(key)
    if csv_path:
        info = load_character_info(csv_path, tables)
        print(f"\n[{info['name']}] 角色数据：{csv_path.relative_to(ROOT_DIR)}")
    else:
        if key.isdigit():
            print(f"\n[{key}] 找不到该编号的角色 CSV，跳过")
            return False
        info = {"name": key, "sex": "", "race": "", "profession": "", "introduce": "", "body_traits": [], "clothes": []}
        print(f"\n[{key}] 未找到角色 CSV，仅按角色名生成")
    name = info["name"]

    # 收集参考图
    ref_paths = [Path(p) for p in args.ref]
    if args.use_existing:
        existing = find_existing_portrait(name)
        if existing:
            ref_paths.insert(0, existing)
        else:
            print(f"[{name}] 未找到现有立绘，不使用参考图")
    for path in ref_paths:
        if not path.exists():
            print(f"[{name}] 参考图不存在：{path}")
            return False

    prompt = build_prompt(info, args.variant, args.extra, args.background == "transparent")
    if ref_paths:
        prompt += "\n参考图：保持参考图中角色的发型、发色、瞳色、服装配色与标志性特征一致。"
        print(f"[{name}] 参考图：" + "，".join(str(p) for p in ref_paths))
    print(f"[{name}] 提示词：\n{prompt}")
    if args.dry_run:
        return True

    # 调用接口并保存
    images = call_image_api(client, args, name, prompt, ref_paths)
    if not images:
        return False
    stamp = time.strftime("%Y%m%d_%H%M%S")
    save_results(Path(args.out) / name, f"{name}_{args.variant}_{stamp}", prompt, images, name)
    return True


def generate_child_portrait(client, args, key, tables, sheet_path, ref_sheet):
    """
    把一张原图改画成该角色儿童时期的全身立绘，并保存结果、提示词与白底对比图
    参数：
        client (openai.OpenAI | None): 客户端，dry-run 时为 None
        args (argparse.Namespace): 命令行参数
        key (str): 原图路径，或角色名/种族名
        tables (dict[str, dict[int, str]]): load_config_tables 返回的配置表
        sheet_path (Path): 儿童参考对照表路径（用于记录）
        ref_sheet (PIL.Image.Image | None): 儿童参考对照表，没有对照表时为 None
    返回值：bool - 是否成功
    """
    resolved = resolve_child_source(key)
    if not resolved:
        print(f"\n[{key}] 找不到原图：请传入图片路径，或确认 image/美术风格参考图、image/立绘 下有同名图片")
        return False
    source, name = resolved
    # 儿童版只接受穿着完整服装的原图，裸体、内衣类差分一律拒绝
    if any(word in source.stem for word in CHILD_FORBIDDEN_SOURCE_WORDS):
        print(f"\n[{name}] 儿童版只接受穿着完整服装的原图，已跳过：{display_path(source)}")
        return False
    print(f"\n[{name}] 原图：{display_path(source)}")

    # 种族与性别：优先读角色 CSV；没有 CSV 而名字本身是种族名时（如 阿达克利斯），就以它为种族
    # 身体素质、服装、介绍不拼进提示词：素质里有成年人的身材条目，CSV 服装也未必与原图一致，一律以原图为准
    race, sex = "", ""
    csv_path = find_character_csv(name)
    if csv_path:
        info = load_character_info(csv_path, tables)
        race, sex = info["race"], info["sex"]
    elif name in tables["race"].values():
        race = name

    prompt = build_child_prompt(name, race, sex, args.age, ref_sheet is not None, args.extra, args.background == "transparent")
    # 输入图片与参数记录：打印出来，并附在 .prompt.txt 末尾方便复现
    record = ["[输入图片]", f"1. 原图：{display_path(source)}（铺白底后上传）"]
    if ref_sheet is not None:
        record.append(f"2. 儿童参考对照表：{display_path(sheet_path)}")
    record.append(f"[参数] model={args.model} size={args.size} quality={args.quality} background={args.background} n={args.n} age={args.age} input_fidelity={args.input_fidelity or '未指定'}")
    record_text = "\n".join(record)
    print(f"[{name}] 提示词：\n{prompt}\n{record_text}")
    if args.dry_run:
        return True

    # 原图和对照表都以内存中的白底 PNG 上传，文件名用 ASCII
    source_image = load_flat_image(source)
    inputs = [("source.png", image_to_png_bytes(source_image), "image/png")]
    if ref_sheet is not None:
        inputs.append(("child_refs.png", image_to_png_bytes(ref_sheet), "image/png"))
    images = call_image_api(client, args, name, prompt, inputs)
    if not images:
        return False

    # 保存结果，文件名带"_小"，与游戏萝莉差分的命名一致
    save_dir = Path(args.out) / name
    base_name = f"{name}_小_全身_{time.strftime('%Y%m%d_%H%M%S')}"
    result_paths = save_results(save_dir, base_name, f"{prompt}\n\n{record_text}", images, name)
    # 白底对比图：原图 | 各张结果 | 年龄感标杆（参考目录里有标杆图时才放）
    compare_images = [source_image] + [load_flat_image(path) for path in result_paths]
    benchmark = Path(args.child_ref_dir) / CHILD_BENCHMARK_NAME
    if benchmark.is_file():
        compare_images.append(load_flat_image(benchmark))
    compare_path = save_dir / f"{base_name}_对比.png"
    save_compare_image(compare_images, compare_path)
    print(f"[{name}] 对比图（原图 | 结果 | 标杆）：{compare_path}")
    return True


def parse_args():
    """
    解析命令行参数
    参数：无
    返回值：argparse.Namespace - 参数对象
    """
    parser = argparse.ArgumentParser(description="调用 GPT 图像模型生成 erArk 角色立绘")
    parser.add_argument("characters", nargs="+", help="角色名或角色编号，可传多个；儿童版模式下为原图路径或角色名/种族名")
    parser.add_argument("--variant", default="全身", help="差分名：全身/半身/笑脸/愉快/不爽/愤怒，或任意自定义描述（默认 全身；儿童版模式固定为全身）")
    parser.add_argument("--extra", default="", help="追加到提示词末尾的额外要求（儿童版模式下写本角色的姿势、鞋子、肤色等细节）")
    parser.add_argument("--ref", nargs="*", default=[], help="参考图路径，可传多个（有参考图时走图像编辑接口；儿童版模式不使用）")
    parser.add_argument("--use-existing", action="store_true", help="自动使用 image/立绘 下该角色已有的立绘作为参考图（儿童版模式不使用）")
    parser.add_argument("--child", action="store_true", help="儿童版模式：把原图改画成该角色儿童时期的全身立绘")
    parser.add_argument("--age", type=int, default=8, choices=range(4, 13), metavar="4-12", help="儿童版的目标年龄（默认 8）")
    parser.add_argument("--child-ref-dir", default=str(DEFAULT_CHILD_REF_DIR), help=f"儿童参考目录，存放参考图与拼好的 {CHILD_REF_SHEET_NAME}（默认 tools/儿童立绘参考）")
    parser.add_argument("--rebuild-child-ref-sheet", action="store_true", help="用儿童参考目录中的参考图重新拼接并覆盖对照表（参考图有增删时使用）")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"模型名（默认 {DEFAULT_MODEL}）")
    parser.add_argument("--size", default=None, help="图片尺寸（默认 1024x1536 竖版；儿童版模式默认 1024x1024，与游戏立绘一致）")
    parser.add_argument("--quality", default="high", help="画质：low/medium/high/auto（默认 high）")
    parser.add_argument("--background", default="transparent", help="背景：transparent/opaque/auto（默认 transparent）")
    parser.add_argument("--input-fidelity", default=None, choices=["high", "low"], help="输入图片保真度，只对图像编辑接口生效（默认不传，中转服务不一定支持）")
    parser.add_argument("--n", type=int, default=1, help="每个角色生成张数（默认 1）")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT_DIR), help="输出目录（默认 tools/output/立绘生成）")
    parser.add_argument("--base-url", default=None, help="自定义接口地址（兼容 OpenAI 的中转服务）")
    parser.add_argument("--timeout", type=float, default=600, help="单次请求超时秒数（默认 600）")
    parser.add_argument("--dry-run", action="store_true", help="只打印提示词，不调用接口")
    args = parser.parse_args()
    # 尺寸默认值随模式而定：游戏立绘是方图，儿童版直接出方图
    if args.size is None:
        args.size = "1024x1024" if args.child else "1024x1536"
    return args


def main():
    """
    主函数：逐个角色生成立绘
    参数：无
    返回值：int - 进程退出码，全部成功为 0
    """
    args = parse_args()
    tables = load_config_tables()

    # 初始化客户端（dry-run 不需要密钥）
    client = None
    if not args.dry_run:
        api_key, base_url = load_api_config(args.base_url)
        if not api_key:
            print("未找到 API 密钥：请设置环境变量 OPENAI_API_KEY，或在 ai_chat_api_key.csv 中添加 OPENAI_API_KEY 行")
            return 1
        client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=args.timeout)

    if args.child:
        if args.ref or args.use_existing:
            print("儿童版模式不使用 --ref / --use-existing，已忽略")
        # 对照表只拼一次，所有原图共用
        sheet_path, ref_sheet = prepare_child_ref_sheet(args)
        failed = [key for key in args.characters if not generate_child_portrait(client, args, key, tables, sheet_path, ref_sheet)]
    else:
        failed = [key for key in args.characters if not generate_for_character(client, args, key, tables)]
    if failed:
        print(f"\n以下角色未成功：{'，'.join(failed)}")
        return 1
    print("\n全部完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
