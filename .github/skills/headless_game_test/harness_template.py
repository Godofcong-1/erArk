# -*- coding: UTF-8 -*-
"""
erArk 无头测试 harness 模板
==========================
用途：不启动界面，加载存档、复刻指令、带护栏运行行为循环、逐轮内窥、内存模拟修复。
用法：按 ==== 分段标记修改后，从仓库根目录运行：
    timeout 240 ./.conda/python.exe -u harness_template.py
    或以 heredoc 方式内联运行（<<'EOF' ... EOF）
注意：
  - 必须用 ./.conda/python.exe（裸 python 是商店空壳别名）
  - 外层必须加 timeout：游戏导入链的非守护线程会让进程跑完后不退出（EXIT=124 且结果已打印 = 正常）
  - 本脚本为只读诊断：只读存档入内存，不写任何文件；不要调用 establish_save / game_update_flow
"""
import os
import sys
import random

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows GBK 控制台防乱码
# 约定从仓库根目录运行本脚本；把当前工作目录加入 sys.path 以便 import 仓库根模块
sys.path.insert(0, os.getcwd())

# ==== 1. 初始化链（照抄 game.py 顺序，约3秒，顺序不能乱） ====
import auto_build_config  # noqa: F401  增量构建游戏数据
from Script.Config import normal_config
from Script.Core import game_type, cache_control

cache_control.cache = game_type.Cache()
normal_config.init_normal_config()
from Script.Config import game_config, character_config

game_config.init()
character_config.init_character_tem_data()
from Script.Config import map_config

map_config.init_map_data()
from Script.Design import (  # noqa: E402
    character_handle,
    game_time,
    character_behavior,
    handle_npc_ai,
    instuct_judege,
    map_handle,
    handle_premise,
)
import Script.Settle  # noqa: F401  注册全部结算器
import Script.StateMachine  # noqa: F401  注册全部状态机
from Script.Core import constant, save_handle, flow_handle
from Script.UI.Moudle import draw
from Script.System.Sex_System import drunk_sex_common

character_handle.init_character_tem()
game_time.init_time()

# ==== 2. 屏蔽UI：所有绘制无操作化 + 记录感兴趣的文本 ====
captured_messages = []
CAPTURE_KEYWORD = "吵醒"  # 改成要断言的文本关键词；不需要捕获则设为 None


def record_draw(self, *a, **k):
    if CAPTURE_KEYWORD and getattr(self, "text", None) and CAPTURE_KEYWORD in str(self.text):
        captured_messages.append(str(self.text).strip())


for _cls_name in dir(draw):
    _cls = getattr(draw, _cls_name)
    if isinstance(_cls, type) and hasattr(_cls, "draw"):
        try:
            _cls.draw = lambda self, *a, **k: None
        except Exception:
            pass
draw.WaitDraw.draw = record_draw  # WaitDraw 常用于关键提示，用记录型 stub
flow_handle.askfor_all = lambda *a, **k: ""
flow_handle.askfor_wait = lambda *a, **k: None

# ==== 3. 读档与状态体检 ====
SAVE_ID = "5"  # 要加载的存档号
save_handle.input_load_save(SAVE_ID)
cache = cache_control.cache
pl = cache.character_data[0]

WATCH_NAME = "阿米娅"  # 重点观察的角色名；None 则不按名找
watch_id = None
for _cid, _cd in cache.character_data.items():
    if WATCH_NAME and _cd.name == WATCH_NAME:
        watch_id = _cid
        break
WATCH = {watch_id} if watch_id is not None else set()

print("== 存档体检 ==")
print("game_time:", cache.game_time, "| 玩家位置:", pl.position, "| 玩家目标:", pl.target_character_id)
if watch_id is not None:
    _c = cache.character_data[watch_id]
    _lv, _ = drunk_sex_common.get_drunk_level(watch_id)
    print(
        f"{_c.name}(id{watch_id}): 位置={_c.position} bhv={_c.behavior.behavior_id} dur={_c.behavior.duration}"
        f" start={_c.behavior.start_time} state={_c.state}"
    )
    print(
        f"  tired={_c.tired_point} sleep={_c.sleep_point} hp={_c.hit_point}/{_c.hit_point_max}"
        f" mp={_c.mana_point}/{_c.mana_point_max} 醉酒lv={_lv} 安眠药={_c.h_state.body_item[9][1]}"
    )
    print(
        f"  sp_flag: sleep={_c.sp_flag.sleep} sleep_h_awake={_c.sp_flag.sleep_h_awake}"
        f" unconscious_h={_c.sp_flag.unconscious_h} is_h={_c.sp_flag.is_h} is_follow={_c.sp_flag.is_follow}"
    )

# （可选）把玩家搬到观察角色所在场景：
# map_handle.character_move_scene(pl.position, cache.character_data[watch_id].position, 0)
# （可选）修改角色状态制造前置条件，如压低熟睡度确保进入吵醒判定：
# cache.character_data[watch_id].sleep_point = 20

# ==== 4. 控制随机分支（可选） ====
random.seed(1)
FORCE_RANDINT_MIN = True  # True=所有 randint 返回下界（概率判定必中）
if FORCE_RANDINT_MIN:
    random.randint = lambda a, b: a

# ==== 5. 复刻玩家指令（不进真实主循环！） ====
BEHAVIOR = constant.Behavior.PLAY_INSTRUMENT  # 要模拟的行为常量
STATE = constant.CharacterStatus.STATUS_PLAY_INSTRUMENT

instuct_judege.init_character_behavior_start_time(0, cache.game_time)
pl.state = STATE
pl.behavior.behavior_id = BEHAVIOR
dur = max(game_config.config_behavior[BEHAVIOR].duration, 1)
pl.behavior.duration = dur
game_time.sub_time_now(dur)  # 真实流程也是先推进时间再进入行为循环
print(f"== 模拟指令 {BEHAVIOR} dur={dur} | 推进后 game_time: {cache.game_time} ==")

# ==== 6. 逐轮内窥插桩（可选，排查轮内"赋予→掐死"时打开） ====
ENABLE_PROBE = True
if ENABLE_PROBE and WATCH:
    _orig_find = handle_npc_ai.find_character_target

    def _wrap_find(cid, now_time):
        _orig_find(cid, now_time)
        if cid in WATCH:
            cd = cache.character_data[cid]
            print(f"    [find后] cid={cid} bhv={cd.behavior.behavior_id} dur={cd.behavior.duration} state={cd.state}")

    handle_npc_ai.find_character_target = _wrap_find
    character_behavior.handle_npc_ai.find_character_target = _wrap_find  # 双保险

    _orig_int = handle_npc_ai.judge_interrupt_character_behavior

    def _wrap_int(cid):
        pre = (cache.character_data[cid].behavior.behavior_id, cache.character_data[cid].behavior.duration)
        r = _orig_int(cid)
        if cid in WATCH:
            cd = cache.character_data[cid]
            print(f"    [中断判定] cid={cid} 前={pre} 返回={r} 后=({cd.behavior.behavior_id},{cd.behavior.duration})")
        return r

    handle_npc_ai.judge_interrupt_character_behavior = _wrap_int
    character_behavior.handle_npc_ai.judge_interrupt_character_behavior = _wrap_int

# ==== 7. 内存模拟候选修复（可选：改源码前先验证收敛） ====
# _orig_x = handle_npc_ai.judge_interrupt_character_behavior
# def _patched(cid):
#     cd = cache.character_data[cid]
#     if <候选修复条件>:
#         return 0
#     return _orig_x(cid)
# handle_npc_ai.judge_interrupt_character_behavior = _patched
# character_behavior.handle_npc_ai.judge_interrupt_character_behavior = _patched

# ==== 8. 带护栏的行为循环（复刻 init_character_behavior 主干） ====
PLAYER_PASS_LIMIT = 30
NPC_PASS_LIMIT = 25

cache.over_behavior_character = set()
g = 0
while 0 not in cache.over_behavior_character:
    g += 1
    if g > PLAYER_PASS_LIMIT:
        print("!! 玩家阶段卡死")
        break
    pl_start = pl.behavior.start_time
    character_behavior.character_behavior(0, cache.game_time, pl_start)
print("玩家阶段轮数:", g)

id_list = cache.npc_id_got.copy()
id_list.discard(0)
passes = 0
stuck = False
while len(cache.over_behavior_character) <= len(id_list):
    passes += 1
    if passes > NPC_PASS_LIMIT:
        stuck = True
        remain = [(c, cache.character_data[c].name) for c in id_list if c not in cache.over_behavior_character]
        print("!! NPC阶段死循环, 未完成(前8个):", remain[:8])
        break
    for cid in id_list:
        if cid in cache.over_behavior_character:
            continue
        if cid in WATCH:
            cd = cache.character_data[cid]
            print(
                f"[pass{passes}] 前: bhv={cd.behavior.behavior_id} dur={cd.behavior.duration}"
                f" start={cd.behavior.start_time} state={cd.state}"
            )
        character_behavior.character_behavior(cid, cache.game_time, pl_start)
        if cid in WATCH:
            cd = cache.character_data[cid]
            print(
                f"[pass{passes}] 后: bhv={cd.behavior.behavior_id} dur={cd.behavior.duration}"
                f" 完成={cid in cache.over_behavior_character}"
            )

# ==== 9. 结果判读 ====
print("NPC阶段轮数:", passes, "| 全部收敛:", not stuck)
print("捕获文本:", captured_messages if captured_messages else "无")
if watch_id is not None:
    _c = cache.character_data[watch_id]
    print(
        f"{_c.name}最终: bhv={_c.behavior.behavior_id} dur={_c.behavior.duration} state={_c.state}"
        f" 完成={watch_id in cache.over_behavior_character}"
    )
# 判读标准：玩家阶段通常1轮；NPC阶段个位数轮全部收敛；超限即活锁，"未完成"名单即卡死角色。
