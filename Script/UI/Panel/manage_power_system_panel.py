from typing import Dict, List, Tuple
from types import FunctionType

# 依赖模块，与生产线面板保持一致的导入方式
from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.Config import game_config, normal_config
from Script.Design import attr_calculation
from Script.UI.Moudle import draw, panel

cache: game_type.Cache = cache_control.cache
_: FunctionType = get_text._
window_width: int = normal_config.config_normal.text_width
line_feed = draw.NormalDraw()
line_feed.text = "\n"
line_feed.width = 1

"""
能源系统管理面板 (Rhodes Power Management Panel)
====================================================================
设计目标：
 以《明日方舟》中罗德岛为背景，对基地动力区的能源生产、调配、储能进行可视化管理。

涵盖功能：
 1. 查看各区块(大类设施)耗电与供电策略；调整策略（标准/节能/超额/断电/备用）。
 2. 管理供能调控员：增减岗位人员，显示其制造能力对动力区效率(发电/燃料转化)的加成。
 3. 管理发电设施：火力(源石反应炉主/副)、水力/风力/太阳能；显示建造上限与产能/燃料消耗。
 4. 管理蓄电：建造/拆除不同等级蓄电池，显示当前与最大储能，以及自放电情况。
 5. 结算每日发电：燃料燃烧→电力、清洁能源产出、蓄电池充放电与自放电。

UI 说明：
  为保持与现有面板风格一致，使用相似的 draw.Button / flow_handle.askfor_all 结构；
  若上层仍未加载本面板新增字段，会在运行期自动初始化。

可扩展点：
  - 区块断电影响实际行为
  - 不足供电时随机事件
  - 蓄电优先级调度策略
  - 天气对风/太阳能修正
"""


# ---------------------------- 数据初始化辅助 ---------------------------- #
def _init_power_runtime_fields():
    """确保动力系统运行期字段存在"""
    ri = cache.rhodes_island
    if not hasattr(ri, "power_supply_strategy"):
        cache.rhodes_island.power_supply_strategy = {}
    if not hasattr(ri, "power_storage"):
        cache.rhodes_island.power_storage = 0
    if not hasattr(ri, "power_storage_max"):
        cache.rhodes_island.power_storage_max = 0
    if not hasattr(ri, "last_power_settle_hour"):
        cache.rhodes_island.last_power_settle_hour = cache.game_time.hour

    # 初始化所有大区块的策略(参考 Facility.csv 中 -1 标记的主区块 cid 0~?)
    for facility_cid, facility_data in game_config.config_facility.items():
        # type = -1 为区块
        try:
            if facility_data.type == -1 and facility_cid not in ri.power_supply_strategy:
                cache.rhodes_island.power_supply_strategy[facility_cid] = 0  # 标准
        except Exception:
            continue


# ---------------------------- 工具函数 ---------------------------- #
def _get_operator_power_bonus(type: int = -1) -> float:
    """
    计算调控员的效率加成 -> 返回一个倍率增量
    type: 发电类型，-1=全部，0=火力，1=水力，2=风力，3=太阳能
    """
    ri = cache.rhodes_island
    total = 0
    for chara_id in ri.power_operator_ids_list:
        try:
            # 获取角色数据
            character = cache.character_data[chara_id]
            ability_value = attr_calculation.get_ability_adjust(character.ability[7]) / 2
        except Exception:
            # 兜底，视为0级能力
            ability_value = attr_calculation.get_ability_adjust(0) / 2
        # 如果该角色不是主调控员，则效率减少
        if chara_id not in ri.main_power_facility_operator_ids:
            ability_value = ability_value / 5
        # 如果说是主调控员，且指定了类型
        elif type != -1:
            # 非当前类型的主调控员对其他类型的发电也减少效率
            if chara_id != ri.main_power_facility_operator_ids[type]:
                ability_value = ability_value / 3
        total += ability_value
    # 不为负数
    total = max(total, 0)
    return round(total, 1)


def _recalc_battery_capacity():
    """根据电池数量重算最大储能"""
    ri = cache.rhodes_island
    # 动态从配置读取电池容量
    cap_table = []
    for lv in (1,2,3):
        try:
            cid = game_config.config_power_storage_level_index.get("电池容量", {}).get(lv)
            if cid:
                cap_table.append(int(game_config.config_power_storage[cid].value))
            else:
                cap_table.append(0)
        except Exception:
            cap_table.append(0)
    ri.power_storage_max = 0
    for idx, num in enumerate(getattr(ri, "battery_list", [])):
        if idx < len(cap_table):
            ri.power_storage_max += cap_table[idx] * num
    # 储能不超过上限
    if ri.power_storage > ri.power_storage_max:
        ri.power_storage = ri.power_storage_max


def get_theoretical_fire_generation(detail: bool = False) -> float:
    """计算24h火力理论发电量(不考虑燃料库存)
    detail: 是否返回更精细的结果(当前仅保留接口, 未来可扩展返回 dict)
    """
    _init_power_runtime_fields()
    ri = cache.rhodes_island
    global_eff = max(ri.effectiveness, 50) / 100
    # 主炉等级与动力区等级同步
    now_facility_lv = ri.facility_level.get(1, 1)
    ri.orundum_reactor_list[0] = now_facility_lv
    main_level = ri.orundum_reactor_list[0] # 主炉等级
    aux_count = ri.orundum_reactor_list[1] # 副炉数量
    op_bonus = _get_operator_power_bonus(0) + 1 # 火力调控员加成
    def _pg(cat:str, lv:int, default:float=0.0):
        try:
            cid = game_config.config_power_generation_level_index.get(cat, {}).get(lv)
            if cid:
                return float(game_config.config_power_generation[cid].value)
        except Exception:
            pass
        return default
    eff_per_fuel = _pg("主反应炉", main_level, 5 + 2 * max(main_level - 1,0))
    aux_fuel_per = _pg("副反应炉", 1, 10) # 副炉燃料消耗
    # 燃料消耗等于副炉数量*副炉燃料消耗
    fuel_can_burn_daily = aux_count * aux_fuel_per
    # 总火电=燃料消耗量*燃烧效率*调控员加成*全局效率
    fire_power = fuel_can_burn_daily * eff_per_fuel * op_bonus * global_eff
    return round(fire_power, 2)


def get_theoretical_clean_generation(kind: int = -1) -> float:
    """计算24h清洁能源理论发电量
    kind: -1=全部 0=水力 1=风力 2=光伏
    """
    _init_power_runtime_fields()
    ri = cache.rhodes_island
    global_eff = max(ri.effectiveness, 50) / 100
    hydro, wind, solar = ri.other_power_facility_list
    # facility_lv = ri.facility_level.get(1, 1)  # 动力区等级，cid=1
    # TODO 未实装天气功能，暂用等级对应不同环境强度:取 level=3 代表标准发电
    base_clean = []
    for cat, fallback in ((_("水力"),60),(_("风力"),40),(_("光伏"),30)):
        cid_candidate = game_config.config_power_generation_level_index.get(cat, {}).get(3)
        try:
            if cid_candidate is not None and cid_candidate in game_config.config_power_generation:
                base_clean.append(float(game_config.config_power_generation[cid_candidate].value))
            else:
                base_clean.append(fallback)
        except Exception:
            base_clean.append(fallback)
    hydro_bonus = _get_operator_power_bonus(1) + 1
    wind_bonus = _get_operator_power_bonus(2) + 1
    solar_bonus = _get_operator_power_bonus(3) + 1
    hydro_val = hydro * base_clean[0] * hydro_bonus * global_eff
    wind_val = wind * base_clean[1] * wind_bonus * global_eff
    solar_val = solar * base_clean[2] * solar_bonus * global_eff
    if kind == 0:
        return round(hydro_val, 2)
    if kind == 1:
        return round(wind_val, 2)
    if kind == 2:
        return round(solar_val, 2)
    return round(hydro_val + wind_val + solar_val, 2)


def get_theoretical_power_generation() -> float:
    """兼容旧接口: 返回火力+清洁能源总理论产能"""
    return round(get_theoretical_fire_generation() + get_theoretical_clean_generation(), 1)


def _get_zone_adjust(zone_cid: int) -> float:
    """获取某区块当前策略调整系数"""
    ri = cache.rhodes_island
    strategy_id = ri.power_supply_strategy.get(zone_cid, 0)
    strategy_obj = game_config.config_supply_strategy.get(strategy_id)
    if strategy_obj:
        try:
            return float(strategy_obj.adjust)
        except Exception:
            return 1.0
    return 1.0


def get_zone_power_consumption(zone_cid: int) -> float:
    """计算指定区块当前策略下理论耗电量(按照当前设施等级, 24h基准)"""
    ri = cache.rhodes_island
    adjust = _get_zone_adjust(zone_cid)
    total = 0.0
    _zone_obj = game_config.config_facility.get(zone_cid)
    zone_name = getattr(_zone_obj, "name", "") if _zone_obj else ""
    for facility_cid, fac_data in game_config.config_facility.items():
        try:
            # 区块自身
            if fac_data.type == -1 and facility_cid != zone_cid:
                continue
        except Exception:
            continue
        belong = False
        # 自己的id等于区块id，或名称包含区块名，或类型等于区块id
        if facility_cid == zone_cid:
            belong = True
        elif zone_name and zone_name in fac_data.name:
            belong = True
        elif fac_data.type == zone_cid:
            belong = True
        if not belong:
            continue
        # 获取设施等级与基础耗电
        level = ri.facility_level.get(facility_cid, 1)
        try:
            effect_cid = game_config.config_facility_effect_data[fac_data.name][level]
            base_use = game_config.config_facility_effect[effect_cid].power_use
        except Exception:
            continue
        # 计算并累加
        total += base_use * adjust
    return round(total, 2)


def get_theoretical_power_consumption() -> float:
    """计算当前所有区块在策略加权后的总理论耗电量"""
    total = 0.0
    for facility_cid, facility_data in game_config.config_facility.items():
        try:
            if facility_data.type == -1:  # 区块
                total += get_zone_power_consumption(facility_cid)
        except Exception:
            continue
    return round(total, 2)


# ---------------------------- 结算逻辑 ---------------------------- #
def settle_power_system(newdayflag: bool = False, draw_flag: bool = True) -> Tuple[bool, str]:
    """结算动力系统每日发电与储能
    参数:
        newdayflag: 是否跨天结算
        draw_flag: 是否即时绘制信息
    返回:
        (un_normal, text) -> 是否存在异常(燃料不足/供电赤字) 与 文本
    """
    _init_power_runtime_fields()
    ri = cache.rhodes_island
    text = _("\n[动力系统结算]\n")
    un_normal = False

    # 计算经过的小时(跨天则补24)
    if newdayflag:
        hours = 24 + cache.game_time.hour - getattr(ri, "last_power_settle_hour", cache.game_time.hour)
    else:
        hours = cache.game_time.hour - getattr(ri, "last_power_settle_hour", cache.game_time.hour)
    hours = max(hours, 0)

    # 若未过时间则无需结算
    if hours == 0:
        return False, ""

    # 全局效率
    global_eff = max(ri.effectiveness, 50) / 100

    # ------------ 火力发电 ------------ #
    main_level = ri.orundum_reactor_list[0]
    aux_count = ri.orundum_reactor_list[1]
    # 仍按原逻辑计算燃料规划，以便与理论值对比
    base_fuel = 20 + 10 * max(main_level - 1, 0)
    fuel_can_burn_daily = base_fuel * (1 + 0.5 * aux_count)
    fuel_can_burn = fuel_can_burn_daily * (hours / 24)
    fuel_have = ri.materials_resouce.get(15, 0)
    fuel_use = min(fuel_can_burn, fuel_have)
    if fuel_use < fuel_can_burn - 0.1:
        un_normal = True
        text += _(" - 燃料不足：计划消耗 {0:.1f}，实际仅 {1:.1f}\n").format(fuel_can_burn, fuel_use)
    ri.materials_resouce[15] = fuel_have - int(fuel_use)
    # 复用理论火力获取效率参数: 需再计算瞬时效率以得到 fire_power 按实际燃料
    # 获取单位燃料效率
    try:
        power_generation_cid = game_config.config_power_generation_level_index[_("主反应炉")][main_level]
        eff_per_fuel = float(game_config.config_power_generation[power_generation_cid].value)
    except Exception:
        eff_per_fuel = 5 + 2 * max(main_level - 1, 0)
    op_bonus = _get_operator_power_bonus()
    fire_power = fuel_use * eff_per_fuel * (1 + op_bonus) * global_eff
    text += _(" - 火力发电：消耗燃料 {0:.1f} 单位，产出 {1:.1f} 度 (调控员加成 {2:.2%})\n").format(fuel_use, fire_power, op_bonus)

    # ------------ 清洁能源 ------------ #
    # 分项(按24h)
    hydro_full = get_theoretical_clean_generation(0)
    wind_full = get_theoretical_clean_generation(1)
    solar_full = get_theoretical_clean_generation(2)
    # 按小时比例
    ratio = hours / 24
    hydro_power = hydro_full * ratio
    wind_power = wind_full * ratio
    solar_power = solar_full * ratio
    clean_power = hydro_power + wind_power + solar_power
    text += _(" - 清洁能源(每小时)：水{0}({3:.1f}) 风{1}({4:.1f}) 太阳能{2}({5:.1f}) 台，总产出 {6:.1f} 度\n").format(
        ri.other_power_facility_list[0], ri.other_power_facility_list[1], ri.other_power_facility_list[2],
        hydro_power, wind_power, solar_power, clean_power
    )

    # ------------ 总产能 & 储能 ------------ #
    total_generated = fire_power + clean_power
    _recalc_battery_capacity()
    before_storage = ri.power_storage
    free_capacity = ri.power_storage_max - ri.power_storage
    charge = min(total_generated, free_capacity)
    ri.power_storage += charge
    surplus = total_generated - charge
    text += _(" - 储能：产能 {0:.1f} 度，充入 {1:.1f} 度，当前储能 {2}/{3}，剩余溢出 {4:.1f} 度\n").format(
        total_generated, charge, ri.power_storage, ri.power_storage_max, surplus
    )

    # ------------ 自放电 ------------ #
    # 按每日自放电率，比例缩放小时
    battery_nums = ri.battery_list
    # 自放电率从配置读取
    discharge_rates = []
    for lv in (1,2,3):
        try:
            cid = game_config.config_power_storage_level_index.get(_("自放电率"), {}).get(lv)
            if cid:
                discharge_rates.append(float(game_config.config_power_storage[cid].value))
            else:
                discharge_rates.append(0.0)
        except Exception:
            discharge_rates.append(0.0)
    # 加权平均自放电率
    total_cells = sum(battery_nums) or 1
    avg_rate = 0
    for idx, num in enumerate(battery_nums):
        avg_rate += discharge_rates[idx] * num
    avg_rate /= total_cells
    real_discharge_rate = avg_rate * (hours / 24)
    discharge_amount = ri.power_storage * real_discharge_rate
    ri.power_storage -= discharge_amount
    ri.power_storage = max(ri.power_storage, 0)
    text += _(" - 自放电：损失 {0:.1f} 度 (rate {1:.2%})，储能剩余 {2:.1f}\n").format(
        discharge_amount, real_discharge_rate, ri.power_storage
    )

    # ------------ 供电策略与耗电检查 ------------ #
    # 目前仅检测供电总量是否小于需求(简单模型：储能 + 产能 >= 需求)，需求使用 ri.power_use
    demand = ri.power_use * (hours / 24)
    # 简单判定：若产能+起始储能 < 需求 => 异常
    if before_storage + total_generated < demand - 0.1:
        un_normal = True
        text += _(" - 警告：本周期供电不足，需求 {0:.1f} 实际 {1:.1f}\n").format(
            demand, before_storage + total_generated
        )
    else:
        text += _(" - 供电正常：需求 {0:.1f} 覆盖率 {1:.1%}\n").format(
            demand, (before_storage + total_generated) / demand if demand else 1
        )

    ri.last_power_settle_hour = cache.game_time.hour

    if draw_flag:
        draw_text = draw.WaitDraw()
        draw_text.width = window_width
        draw_text.text = text
        draw_text.draw()

    return un_normal, text


# ---------------------------- 面板类 ---------------------------- #
class Manage_Power_System_Panel:
    """动力系统管理面板"""

    def __init__(self, width: int):
        self.width = width
        _init_power_runtime_fields()

    # ---------- 主绘制 ---------- #
    def draw(self):
        while 1:
            _init_power_runtime_fields()
            ri = cache.rhodes_island
            title = draw.TitleLineDraw(_("动力系统管理"), self.width)
            title.draw()

            # 自动结算（按小时）
            settle_power_system(draw_flag=False)

            info = draw.NormalDraw()
            info.width = self.width
            # 概览文本
            overview = []
            overview.append(_("--概览--"))
            overview.append(_("  当前用电量: {0} / 最大供电:{1}" ).format(ri.power_use, ri.power_max))
            _recalc_battery_capacity()
            overview.append(_("  储能: {0}/{1}" ).format(ri.power_storage, ri.power_storage_max))
            overview.append(_("  调控员人数: {0}" ).format(len(ri.power_operator_ids_list)))
            # 显示分项发电潜力(按24h理论值) 使用新函数
            main_level = ri.orundum_reactor_list[0]
            aux_count = ri.orundum_reactor_list[1]
            fire_theory = get_theoretical_fire_generation()
            hydro, wind, solar = ri.other_power_facility_list
            hydro_t = get_theoretical_clean_generation(0)
            wind_t = get_theoretical_clean_generation(1)
            solar_t = get_theoretical_clean_generation(2)
            overview.append(_("  源石反应炉(每小时) 主:{0} 副:{1} 理论产出:{2:.1f}" ).format(main_level, aux_count, fire_theory))
            overview.append(_("  清洁能源(每小时) 水力:{0}({3:.1f}) 风能:{1}({4:.1f}) 光伏:{2}({5:.1f})" ).format(
                hydro, wind, solar, hydro_t, wind_t, solar_t))
            overview.append(_("  蓄电池(L1/L2/L3): {0}/{1}/{2}" ).format(*ri.battery_list))
            overview.append(_("  上次结算小时:{0}" ).format(getattr(ri, "last_power_settle_hour", 0)))
            info.text = "\n".join(overview) + "\n"
            info.draw()

            line_feed.draw()
            return_list = []

            # 按钮 1 供电策略
            btn = draw.LeftButton(_("[001]供电策略调整"), _("供电策略调整"), self.width, cmd_func=self._panel_supply_strategy)
            btn.draw()
            line_feed.draw()
            return_list.append(btn.return_text)
            # 按钮 2 调控员
            btn = draw.LeftButton(_("[002]调控员管理"), _("调控员管理"), self.width, cmd_func=self._panel_operator)
            btn.draw()
            line_feed.draw()
            return_list.append(btn.return_text)
            # 按钮 3 发电设施
            btn = draw.LeftButton(_("[003]发电设施管理"), _("发电设施管理"), self.width, cmd_func=self._panel_facilities)
            btn.draw()
            line_feed.draw()
            return_list.append(btn.return_text)
            # 按钮 4 蓄电池管理
            btn = draw.LeftButton(_("[004]蓄电池管理"), _("蓄电池管理"), self.width, cmd_func=self._panel_battery)
            btn.draw()
            line_feed.draw()
            return_list.append(btn.return_text)
            # 按钮 5 强制结算
            btn = draw.LeftButton(_("[005]结算本时段"), _("结算本时段"), self.width, cmd_func=settle_power_system)
            btn.draw()
            return_list.append(btn.return_text)

            line_feed.draw()
            line_feed.draw()
            back = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back.draw()
            return_list.append(back.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == back.return_text:
                break

    # ---------- 供电策略子界面 ---------- #
    def _panel_supply_strategy(self):
        """供电策略调整子界面"""
        _init_power_runtime_fields()
        ri = cache.rhodes_island
        # 获取供电策略数据
        supply_strategy = game_config.config_supply_strategy
        while 1:
            title = draw.TitleLineDraw(_("供电策略"), self.width)
            title.draw()
            return_list = []
            # 汇总
            summary = draw.NormalDraw(); summary.width = self.width
            summary.text = _("\n  理论总发电:{0}  理论总耗电:{1}\n").format(
                get_theoretical_power_generation(), get_theoretical_power_consumption()
            )
            summary.draw()
            line_feed.draw()
            # 表头
            head = draw.NormalDraw(); head.width = self.width
            head.text = _("　区块　　　 | 当前策略　　　　　  | [-]降级   [+]升级\n")
            head.draw()
            # 列表
            for cid, fac_data in game_config.config_facility.items():
                try:
                    if fac_data.type != -1:
                        continue
                except Exception:
                    continue
                # 跳过动力区本身
                if cid == 1:
                    continue
                st = ri.power_supply_strategy.get(cid, 0)
                # 设施名称
                fac_name = attr_calculation.pad_display_width("　" + fac_data.name, 12)
                # 当前策略
                now_strategy_text = f"{supply_strategy[st].name}({int(supply_strategy[st].adjust*100)}%)"
                now_strategy_text = attr_calculation.pad_display_width(now_strategy_text, 10)
                # 当前耗电
                zone_use = str(get_zone_power_consumption(cid)).ljust(6)
                # 行文本
                row_draw = draw.NormalDraw(); row_draw.width = self.width
                row_draw.text = f"{fac_name} | {now_strategy_text} = {zone_use} | "
                row_draw.draw()

                # 按钮
                def make_dec(cid_inner):
                    return lambda : self._set_strategy(cid_inner, (ri.power_supply_strategy.get(cid_inner,0)-1)%5)
                def make_inc(cid_inner):
                    return lambda : self._set_strategy(cid_inner, (ri.power_supply_strategy.get(cid_inner,0)+1)%5)
                btn_dec = draw.CenterButton(_("[-]"), _("降低") + fac_data.name, 6, cmd_func=make_dec(cid)); btn_dec.draw(); return_list.append(btn_dec.return_text)
                btn_inc = draw.CenterButton(_("[+]"), _("提升") + fac_data.name, 6, cmd_func=make_inc(cid)); btn_inc.draw(); return_list.append(btn_inc.return_text)
                line_feed.draw()

            line_feed.draw()
            back = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back.draw(); return_list.append(back.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back.return_text:
                break

    def _cycle_strategy(self, cid: int):
        """循环切换某区块的供电策略"""
        ri = cache.rhodes_island
        now = ri.power_supply_strategy.get(cid, 0)
        ri.power_supply_strategy[cid] = (now + 1) % 5
    def _set_strategy(self, cid:int, value:int):
        ri = cache.rhodes_island
        ri.power_supply_strategy[cid] = value

    # ---------- 调控员管理 ---------- #
    def _panel_operator(self):
        """调控员管理子界面"""
        ri = cache.rhodes_island
        from Script.UI.Panel import manage_basement_panel
        while 1:
            title = draw.TitleLineDraw(_("调控员管理"), self.width)
            title.draw()
            return_list = []
            info = draw.NormalDraw(); info.width = self.width
            op_bonus = _get_operator_power_bonus()
            info.text = _("当前调控员数量：{0}  总效率加成：{1:.2%}" ).format(len(ri.power_operator_ids_list), op_bonus)
            info.text += " " * 4
            info.draw()

            button_text = _("[调控员增减]")
            button_draw = draw.CenterButton(
                _(button_text),
                _(button_text),
                len(button_text) * 2 + 2,
                cmd_func=manage_basement_panel.change_npc_work_out,
                args=self.width
                )
            return_list.append(button_draw.return_text)
            button_draw.draw()
            line_feed.draw()
            line_feed.draw()

            # 遍历显示各主调控员
            main_ops = ri.main_power_facility_operator_ids
            type_name = [_("源石反应炉"), _("水力发电"), _("风力发电"), _("光伏发电")]
            for idx, cid in enumerate(main_ops):
                name = self._get_chara_name(cid)
                # 显示文本
                chara_name = name if name else _("(空缺)")
                chara_name = attr_calculation.pad_display_width(chara_name, 12)
                now_type_name = attr_calculation.pad_display_width(type_name[idx], 12)
                main_text = _("{0}主调控员: {1}").format(now_type_name, chara_name)
                main_draw = draw.NormalDraw(); main_draw.width = self.width
                main_draw.text = main_text
                main_draw.draw()
                # 任命按钮
                def _make_appoint(i):
                    return lambda : self._appoint_main_operator(i)
                btn = draw.CenterButton(_("[任命]"), _("任命") + type_name[idx], 12, cmd_func=_make_appoint(idx))
                btn.draw(); return_list.append(btn.return_text)
                line_feed.draw()
            line_feed.draw()

            # 遍历显示其他调控员
            other_ops = [cid for cid in ri.power_operator_ids_list if cid not in main_ops]
            other_text = _("辅助调控员: ")
            if other_ops:
                names = [self._get_chara_name(cid) or _("(未知)") for cid in other_ops]
                other_text += "、".join(names)
            else:
                other_text += _("暂无")
            other_draw = draw.NormalDraw(); other_draw.width = self.width
            other_draw.text = other_text
            other_draw.draw()

            line_feed.draw()
            line_feed.draw()
            back = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back.draw(); return_list.append(back.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back.return_text:
                break

    def _appoint_main_operator(self, type_idx: int):
        """
        任命某类型主调控员
        Keyword arguments:
        commision_id -- 委托编号
        """

        ri = cache.rhodes_island
        type_name = [_("源石反应炉"), _("水力"), _("风能"), _("光伏")]
        return_list = []
        def _make_appoint(c_id):
            self._do_appoint_main_operator(type_idx, c_id)

        from Script.UI.Panel import common_select_NPC
        now_draw_panel : panel.PageHandlePanel = panel.PageHandlePanel([], common_select_NPC.CommonSelectNPCButtonList, 50, 5, window_width, True, False, 0)
        select_state = {}

        while 1:
            info_text = _("请选择一名调控员担任{0}主调控员:\n").format(type_name[type_idx])

            # 已选择的角色id列表
            final_list = []
            # 遍历角色id
            for npc_id in ri.power_operator_ids_list:
                if npc_id == 0:
                    continue
                now_list = [npc_id, _make_appoint, [ri.main_power_facility_operator_ids[type_idx]]]
                final_list.append(now_list)
            now_draw_panel.text_list = final_list

            # 调用通用选择按钮列表函数
            return_list, other_return_list, select_state = common_select_NPC.common_select_npc_button_list_func(now_draw_panel, _("任命主调控员"), info_text, select_state)

            yrn = flow_handle.askfor_all(return_list)
            if yrn == _("返回"):
                break

    def _do_appoint_main_operator(self, type_idx: int, chara_id: int):
        """执行任命某类型主调控员"""
        ri = cache.rhodes_island
        if chara_id not in ri.power_operator_ids_list:
            # 兜底
            return
        # 替换
        if type_idx < 0 or type_idx >= len(ri.main_power_facility_operator_ids):
            return
        # 如果该角色担任了其他主调控员，则清除
        for idx, cid in enumerate(ri.main_power_facility_operator_ids):
            if idx != type_idx and cid == chara_id:
                ri.main_power_facility_operator_ids[idx] = 0
        # 如果该角色正在担任该类型主调控员，则撤职
        if ri.main_power_facility_operator_ids[type_idx] == chara_id:
            ri.main_power_facility_operator_ids[type_idx] = 0
        else:
            ri.main_power_facility_operator_ids[type_idx] = chara_id

    # ---------- 发电设施管理 ---------- #
    def _panel_facilities(self):
        """发电设施管理子界面"""
        ri = cache.rhodes_island
        lv = ri.facility_level.get(1,1)
        while 1:
            return_list = []
            title = draw.TitleLineDraw(_("发电设施管理"), self.width)
            title.draw()
            # 汇总
            summary = draw.NormalDraw(); summary.width = self.width
            summary.text = _("\n  理论总发电:{0}  理论总耗电:{1}\n").format(
                get_theoretical_power_generation(), get_theoretical_power_consumption()
            )
            # 如果当前罗德岛在行驶中
            move_flag = False
            if ri.move_target_and_time[0] != 0:
                summary.text += _("！当前罗德岛处于行驶中，水力与风力发电设施无法工作！\n")
                move_flag = True
            summary.draw()
            # 显示文本
            extra_module = draw.NormalDraw(); extra_module.width = self.width
            extra_module.text = _("  副源石反应炉扩展模块 ：已用 {0} / 总 {1} （含区块等级提供的{2}）\n").format(
                ri.orundum_reactor_list[1], ri.materials_resouce[51] + lv * 3, lv * 3
            )
            extra_module.text += _("  清洁能源通用扩展模块 ：已用 {0} / 总 {1} （含区块等级提供的{2}）\n").format(
                sum(ri.other_power_facility_list), ri.materials_resouce[53] + lv, lv
            )
            extra_module.draw()
            line_feed.draw()
            # 提示信息
            info = draw.NormalDraw(); info.width = self.width
            info.text = _("○ 如果每日发电量+已储存蓄电量不够覆盖当日总用电量，将会影响罗德岛整体运营效率\n")
            info.text += _("○ 每日过剩的电量将优先充入蓄电池，溢出部分将被浪费\n")
            info.text += _("○ 扩展模块可以在生产制造区的流水线上消耗资源进行制造\n")
            info.text += _("○ 清洁能源设施的发电量受环境与天气影响较大，当前未实装地区环境与天气系统，暂为固定值乘以随机量\n")
            info.draw()
            line_feed.draw()
            head = draw.NormalDraw(); head.width = self.width
            facility_text = attr_calculation.pad_display_width(_("设施"), 12, "center")
            value_text = attr_calculation.pad_display_width(_("数值"), 9, "center")
            info_text = attr_calculation.pad_display_width(_("信息"), 60, "center")
            change_text = attr_calculation.pad_display_width(_("操作"), 14, "center")
            head.text = _(" {0} | 当前 | {1} | {2} | {3}\n").format(facility_text, value_text, info_text, change_text)
            head.draw()
            # 主反应炉
            main_lv = ri.orundum_reactor_list[0]
            main_lv = str(main_lv).rjust(2, ' ')
            # 读取当前等级单位燃料效率
            try:
                cid_eff = game_config.config_power_generation_level_index[_("主反应炉")][int(main_lv)]
                eff_value = float(game_config.config_power_generation[cid_eff].value)
            except Exception:
                eff_value = 5 + 2 * max(int(main_lv) - 1, 0)
            eff_value_str = str(round(eff_value,1)).rjust(4)
            main_info = attr_calculation.pad_display_width(_("主炉等级等于动力区等级，决定单位燃料的发电效率"), 60)
            row = draw.NormalDraw(); row.width = self.width
            row.text = _(" 主源石反应炉 | {0}级 | {1}/燃料 | {2} | ").format(main_lv, eff_value_str, main_info)
            row.draw()
            # 主反应炉升级按钮(与动力区等级同步，故取消)
            # def up_main():
            #     ri.orundum_reactor_list[0] = min(ri.orundum_reactor_list[0] + 1, 10)
            # btn = draw.CenterButton(_("[升级]"), _("升级主源石反应炉"), 10, cmd_func=up_main); btn.draw(); return_list.append(btn.return_text)
            line_feed.draw()
            # 副反应炉
            aux = ri.orundum_reactor_list[1]
            aux = str(aux).rjust(2, ' ')
            # 副反应炉燃料增量(统一使用等级1配置数值作为单台每日燃料)
            try:
                cid_aux = game_config.config_power_generation_level_index[_("副反应炉")][1]
                aux_fuel = float(game_config.config_power_generation[cid_aux].value)
            except Exception:
                aux_fuel = 10.0
            aux_info = attr_calculation.pad_display_width(_("副炉数量影响每日燃料的燃烧数量，启用台数越多燃料消耗越多"), 60)
            row = draw.NormalDraw(); row.width = self.width
            row.text = _(" 副源石反应炉 | {0}台 | {1:.1f}/台日 | {2} | ").format(aux, aux_fuel, aux_info)
            row.draw()
            def add_aux():
                ri.orundum_reactor_list[1] = min(ri.orundum_reactor_list[1] + 1, lv * 3 + ri.materials_resouce[51])
            def sub_aux():
                if ri.orundum_reactor_list[1] > 0: ri.orundum_reactor_list[1] -= 1
            btn_add = draw.CenterButton(_("[+]"), _("增加副源石反应炉"), 8, cmd_func=add_aux); btn_add.draw(); return_list.append(btn_add.return_text)
            btn_sub = draw.CenterButton(_("[-]"), _("减少副源石反应炉"), 8, cmd_func=sub_aux); btn_sub.draw(); return_list.append(btn_sub.return_text)
            line_feed.draw()
            # 清洁能源
            names = [_("水力发电轮组"), _("风力发电机组"), _("光伏发电板组")]
            descs = [_("发电量受水流速影响大，仅在停靠时可用，行驶中无法使用"), _("发电量受风速影响大，仅在停靠时可用，行驶中无法使用"), _("发电量受日照影响大，停靠或行驶中均可使用")]
            for idx in range(3):
                num = ri.other_power_facility_list[idx]
                num = str(num).rjust(2, ' ')
                # 对应类别名称与fallback
                cat_map = {0:_("水力"), 1:_("风力"), 2:_("光伏")}
                fallback_map = {0:60,1:40,2:30}
                try:
                    cid_lv3 = game_config.config_power_generation_level_index.get(cat_map[idx], {}).get(3)
                    if cid_lv3 is not None and cid_lv3 in game_config.config_power_generation:
                        base_val = float(game_config.config_power_generation[cid_lv3].value)
                    else:
                        base_val = fallback_map[idx]
                except Exception:
                    base_val = fallback_map[idx]
                # 如果是在行驶中，则水力与风力发电设施无效
                if move_flag and idx in (0,1):
                    base_val = 0.0
                base_val_str = str(round(base_val,1)).rjust(4)
                row = draw.NormalDraw(); row.width = self.width
                descs_now = attr_calculation.pad_display_width(descs[idx], 60)
                row.text = " {0} | {1}组 | {2}/组日 | {3} | ".format(names[idx], num, base_val_str, descs_now)
                row.draw()
                def _make_add(i):
                    return lambda : self._inc_clean(i, +1)
                def _make_sub(i):
                    return lambda : self._inc_clean(i, -1)
                btn_add = draw.CenterButton(_("[+]"), _("增加") + names[idx], 8, cmd_func=_make_add(idx)); btn_add.draw(); return_list.append(btn_add.return_text)
                btn_sub = draw.CenterButton(_("[-]"), _("减少") + names[idx], 8, cmd_func=_make_sub(idx)); btn_sub.draw(); return_list.append(btn_sub.return_text)
                line_feed.draw()

            line_feed.draw()
            back = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back.draw(); return_list.append(back.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back.return_text:
                break

    def _inc_clean(self, idx: int, delta: int):
        """增加或减少某类清洁能源设施"""
        ri = cache.rhodes_island
        lv = ri.facility_level.get(1, 1)
        # 按类型上限先校验
        new_val = max(0, ri.other_power_facility_list[idx] + delta)
        # 全局三类总量上限：区块等级 + 额外模块总数
        total_now = sum(ri.other_power_facility_list)
        if delta > 0:
            clean_total_limit = lv + ri.materials_resouce[53]
            if total_now >= clean_total_limit:
                self._hint(_("三种清洁能源设施总数已达上限({0})，可通过生产清洁能源模块扩展上限").format(clean_total_limit))
                return
            # 若未达上限，允许+1（在类型上限内）
            ri.other_power_facility_list[idx] = new_val
        else:
            ri.other_power_facility_list[idx] = new_val
        total_after = sum(ri.other_power_facility_list)
        ri.now_used_extra_clean_energy_module_count = max(0, total_after - lv)

    # ---------- 蓄电池管理 ---------- #
    def _panel_battery(self):
        """蓄电池管理子界面"""
        ri = cache.rhodes_island
        while 1:
            title = draw.TitleLineDraw(_("蓄电池管理"), self.width)
            title.draw()
            _recalc_battery_capacity()
            return_list = []
            head = draw.NormalDraw(); head.width = self.width
            head.text = _("类型 | 数量 | 容量/台 | 自放电 | 操作\n")
            head.draw()
            # 动态容量与自放电率显示
            cap_table = []
            for lv in (1,2,3):
                try:
                    cid = game_config.config_power_storage_level_index.get(_("电池容量"), {}).get(lv)
                    if cid:
                        cap_table.append(int(game_config.config_power_storage[cid].value))
                    else:
                        cap_table.append(0)
                except Exception:
                    cap_table.append(0)
            rate_table = []
            for lv in (1,2,3):
                try:
                    cid = game_config.config_power_storage_level_index.get(_("自放电率"), {}).get(lv)
                    if cid:
                        rate_table.append(float(game_config.config_power_storage[cid].value))
                    else:
                        rate_table.append(0.0)
                except Exception:
                    rate_table.append(0.0)
            names = [_("L1"),_("L2"),_("L3")]
            for idx in range(3):
                num = ri.battery_list[idx]
                row = draw.NormalDraw(); row.width = self.width
                row.text = f"{names[idx]} | {num} | {cap_table[idx]} | {int(rate_table[idx]*1000)/10}% | "
                row.draw()
                def make_add(i):
                    return lambda : self._change_battery(i, +1)
                def make_sub(i):
                    return lambda : self._change_battery(i, -1)
                btn_add = draw.CenterButton(_("[+]"), _("增加") + names[idx], 8, cmd_func=make_add(idx)); btn_add.draw(); return_list.append(btn_add.return_text)
                btn_sub = draw.CenterButton(_("[-]"), _("减少") + names[idx], 8, cmd_func=make_sub(idx)); btn_sub.draw(); return_list.append(btn_sub.return_text)
                line_feed.draw()
            line_feed.draw()
            # 蓄电池总量限制与生产入口
            lv = ri.facility_level.get(1, 1)
            total_batt = sum(ri.battery_list)
            used_extra_batt = max(0, total_batt - lv)
            used_extra_batt = min(used_extra_batt, ri.materials_resouce[52])
            tip = draw.NormalDraw(); tip.width = self.width
            tip.text = _("蓄电池扩展位：已用 {0} / 总 {1} （基础额度：{2}；总数上限=基础+扩展）\n").format(
                used_extra_batt, ri.materials_resouce[52], lv
            )
            tip.draw()
            line_feed.draw()
            total_draw = draw.NormalDraw(); total_draw.width = self.width
            total_draw.text = _("当前储能: {0}/{1}\n").format(ri.power_storage, ri.power_storage_max)
            total_draw.draw()
            back = draw.CenterButton(_("[返回]"), _("返回"), self.width)
            back.draw(); return_list.append(back.return_text)
            line_feed.draw()
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back.return_text:
                break

    def _change_battery(self, level: int, delta: int):
        ri = cache.rhodes_island
        lv = ri.facility_level.get(1, 1)
        if delta > 0:
            total_now = sum(ri.battery_list)
            total_limit = lv + ri.materials_resouce[52]
            if total_now >= total_limit:
                self._hint(_("蓄电池总数已达上限({0})，可通过生产蓄电池扩展上限").format(total_limit))
                return
            ri.battery_list[level] += 1
        else:
            if ri.battery_list[level] > 0:
                ri.battery_list[level] -= 1
        _recalc_battery_capacity()
        # 更新已使用扩展位
        total_after = sum(ri.battery_list)
        used_extra_batt = max(0, total_after - lv)
        ri.now_used_extra_battery_count = min(used_extra_batt, ri.materials_resouce[52])

    # ---------- 小提示 ---------- #
    def _hint(self, text: str):
        msg = draw.WaitDraw()
        msg.width = self.width
        msg.text = "\n" + str(text) + "\n"
        msg.draw()

    # ---------- 角色名工具 ---------- #
    def _get_chara_name(self, chara_id: int) -> str:
        """获取角色名称，失败则返回默认"""
        # 如果为id为0则为玩家，返回空字符串
        if chara_id == 0:
            return ""
        try:
            chara = cache.character_data.get(chara_id)
            if chara and hasattr(chara, "name"):
                return str(chara.name)
        except Exception:
            pass
        return _("干员") + str(chara_id)

