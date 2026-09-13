# -*- coding: UTF-8 -*-
"""
复现脚本骨架（system-review-round skill，P3）

用法：
    1. 复制到 scratchpad 的 pNN/repro_planNN.py（不入库），改下面的 SUITE_DIR 与「==== 复现检查 ====」段
    2. 在仓库根目录运行（改前）：
       timeout 300 ./.conda/python.exe -u <脚本> > <scratchpad>/pNN/repro.log 2>&1
    3. 实施完再跑一次（改后），按每项登记的 after 核对：
       REPRO_PHASE=after timeout 300 ./.conda/python.exe -u <脚本> > <scratchpad>/pNN/repro_after.log 2>&1

登记规则（Plan 30 实施文档 §2.0 的体例）：
    - 每项检查的「成立」都表示「问题现在确实存在」或「这条事实 / 前提确实如此」
    - category 四类：问题命中 / 前提对照（证明夹具真的走到了那条路径）/ 数据事实 / 随口径（结论取决于用户拍板）
    - after 三种：不再成立 / 照旧 / 随口径
    - 立项要求：改前全部成立；改后「问题命中」全部不再成立，其余照旧
"""
import os
import sys

ROOT = os.environ.get("ERARK_ROOT") or os.getcwd()
""" 仓库根目录：默认当前工作目录，也可用环境变量 ERARK_ROOT 指定 """
if not os.path.isfile(os.path.join(ROOT, "game.py")):
    print(f"找不到仓库根目录（{ROOT} 下没有 game.py），请在仓库根目录运行或设置 ERARK_ROOT")
    sys.exit(2)
SUITE_DIR = os.path.join(ROOT, "tools", "tests", "education")
""" 回归套件目录：复用它的 _bootstrap.py 做初始化；别的系统换成自己的套件目录 """
sys.path.insert(0, SUITE_DIR)

from _bootstrap import *  # noqa: F401,F403,E402  初始化游戏配置与缓存，并 chdir 到仓库根目录

CATEGORIES = ("问题命中", "前提对照", "数据事实", "随口径")
""" 检查项的四种类别 """
AFTER_VALUES = ("不再成立", "照旧", "随口径")
""" 改后预期的三种取值 """
PHASE = os.environ.get("REPRO_PHASE", "before")
""" before：改前立项；after：改后按 after 核对 """
RESULTS = []
""" 全部检查项的登记结果 """


def R(group: str, idx: int, desc: str, cond, after: str, category: str = "问题命中", extra="") -> bool:
    """
    登记一项复现检查
    Keyword arguments:
    group -- 组名（R1、R2……，一组对应一条发现）
    idx -- 组内序号
    desc -- 检查内容
    cond -- 本项是否成立
    after -- 修好之后的预期：不再成立 / 照旧 / 随口径
    category -- 类别：问题命中 / 前提对照 / 数据事实 / 随口径
    extra -- 附带打印的实际值
    Return arguments:
    bool -- 本项是否成立
    """
    assert category in CATEGORIES, f"未知类别 {category}"
    assert after in AFTER_VALUES, f"未知改后预期 {after}"
    holds = bool(cond)
    RESULTS.append({"group": group, "idx": idx, "desc": desc, "holds": holds, "after": after, "category": category})
    print(f"  [{'成立' if holds else '不成立'}] {group}-{idx} {desc} {extra}")
    return holds


def summary():
    """
    打印汇总并强制退出（导入链里的非守护线程会让进程不自行结束）
    Keyword arguments:
    无
    Return arguments:
    无
    """
    print()
    print("=" * 50)
    holds = [r for r in RESULTS if r["holds"]]
    print(f"阶段 {PHASE}：共 {len(RESULTS)} 项，成立 {len(holds)}、不成立 {len(RESULTS) - len(holds)}")
    for category in CATEGORIES:
        items = [r for r in RESULTS if r["category"] == category]
        if items:
            print(f"  {category}：{len(items)} 项，成立 {sum(r['holds'] for r in items)}")
    if PHASE == "before":
        bad = [r for r in RESULTS if not r["holds"]]
        print("改前全部成立，可以立项" if not bad else "改前有不成立的项（夹具没走到，或发现不成立）：")
    else:
        # 改后：不再成立的项应为 False，照旧的项应为 True，随口径的项不核对
        bad = [r for r in RESULTS if (r["after"] == "不再成立" and r["holds"]) or (r["after"] == "照旧" and not r["holds"])]
        print("改后全部符合预期" if not bad else "改后与预期不符：")
    for r in bad:
        print(f"  - {r['group']}-{r['idx']} {r['desc']}（{r['category']}，改后预期 {r['after']}）")
    sys.stdout.flush()
    os._exit(0 if not bad else 1)


# ==== 复现检查（示例：复制后删掉，换成本轮每条发现一组） ====
section("R0 示例：夹具与数据事实")
student = make_character(901, "示例学生", 152, daughter=True, stage=103)
R("R0", 0, "夹具：学生岗、萝莉期", student.work.work_type == 152 and student.talent[103] == 1, "照旧", "前提对照")
R("R0", 1, "数据事实：默认游戏时间是周一第一节", DEFAULT_TIME.weekday() == 0 and DEFAULT_TIME.hour == 9, "照旧", "数据事实")

summary()
