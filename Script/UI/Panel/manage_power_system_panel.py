from typing import Dict, List, Tuple, Callable
from types import FunctionType

# 依赖模块，与生产线面板保持一致的导入方式
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
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

数据结构(动态附加，不修改 game_type 源文件)：
  cache.rhodes_island.power_supply_strategy: Dict[int,int]
      供电策略：设施大类cid -> 策略id
  cache.rhodes_island.power_storage: int 当前已储存能量 (单位：度)
  cache.rhodes_island.power_storage_max: int 当前最大可储能量 (根据蓄电池数量与等级计算)
  cache.rhodes_island.last_power_settle_hour: int 上次结算发生的小时

策略定义：
 0 标准(100%)  1 节能(80%)  2 超额(120%)  3 断电(0%)  4 备用(40%)
 影响：仅影响该区块的“有效耗电需求”，用于未来可扩展的优先级/宕机事件。

发电设定(可调公式)：
  火力(源石反应炉)：
      主反应炉等级 L = orundum_reactor_list[0]
      副反应炉数量 A = orundum_reactor_list[1]
      基础每日燃料可燃量 base_fuel = 20 + 10*(L-1)
      实际可燃 = base_fuel * (1 + 0.5*A)
      燃料资源id = 15  (若不足则按库存部分燃烧)
      每单位燃料产能 eff = 5 + 2*(L-1)  (受效率加成 adjust)
      调控员效率加成 op_bonus = sum(单人制造能力系数) / 100 (安全下限0)
      基地全局效率：cache.rhodes_island.effectiveness / 100
      总产能 = fuel_used * eff * (1 + op_bonus) * global_eff
  清洁能源(水/风/太阳能)：other_power_facility_list = [hydro, wind, solar]
      设基础单台产能：hydro=60, wind=40, solar=30
      动力区设施等级(设施cid=1) lv1 = cache.rhodes_island.facility_level.get(1,1)
      清洁能源效率 = 1 + (lv1-1)*0.1
      总产能 = Σ(数量 * 基础 * 效率 * global_eff)
  蓄电池 battery_list = [lv1, lv2, lv3]
      容量: lv1=500, lv2=1500, lv3=4000
      自放电率: lv1=2%, lv2=1%, lv3=0.5% 每日

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
    cap_table = [500, 1500, 4000]
    ri.power_storage_max = 0
    for idx, num in enumerate(getattr(ri, "battery_list", [])):
        if idx < len(cap_table):
            ri.power_storage_max += cap_table[idx] * num
    # 储能不超过上限
    if ri.power_storage > ri.power_storage_max:
        ri.power_storage = ri.power_storage_max


def get_theoretical_power_generation() -> float:
    """计算当前配置下24小时理论可发电量(不考虑燃料库存、自放电)"""
    _init_power_runtime_fields()
    ri = cache.rhodes_island
    global_eff = max(ri.effectiveness, 50) / 100 # 全局效率
    # 主炉等级当前版本直接等于动力区的区块等级
    now_facility_lv = ri.facility_level.get(1, 1)  # 动力区cid=1
    ri.orundum_reactor_list[0] = now_facility_lv
    # 火电部分
    main_level = ri.orundum_reactor_list[0] # 主炉等级
    aux_count = ri.orundum_reactor_list[1] # 副炉数量
    base_fuel = 20 + 10 * max(main_level - 1, 0) # 每日基础燃料消耗
    fuel_can_burn_daily = base_fuel * (1 + 0.5 * aux_count) # 理论每日可燃料
    eff_per_fuel = 5 + 2 * max(main_level - 1, 0) # 每单位燃料产能
    op_bonus = _get_operator_power_bonus(0) + 1 # 调控员效率加成
    fire_power = fuel_can_burn_daily * eff_per_fuel * op_bonus * global_eff
    # 清洁能源
    hydro, wind, solar = ri.other_power_facility_list
    facility_lv = ri.facility_level.get(1, 1)  # 动力区cid=1
    clean_eff = 1 + 0.1 * (facility_lv - 1)
    base_clean = [60, 40, 30]
    hydro_bonus = _get_operator_power_bonus(1) + 1
    wind_bonus = _get_operator_power_bonus(2) + 1
    solar_bonus = _get_operator_power_bonus(3) + 1
    clean_power = (hydro * base_clean[0] * hydro_bonus + wind * base_clean[1] * wind_bonus + solar * base_clean[2] * solar_bonus) * clean_eff * global_eff
    return round(fire_power + clean_power, 2)


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
    base_fuel = 20 + 10 * max(main_level - 1, 0)
    fuel_can_burn_daily = base_fuel * (1 + 0.5 * aux_count)
    # 按小时比例(若小时不足24则按比例消耗)
    fuel_can_burn = fuel_can_burn_daily * (hours / 24)
    fuel_have = ri.materials_resouce.get(15, 0)
    fuel_use = min(fuel_can_burn, fuel_have)
    if fuel_use < fuel_can_burn - 0.1:
        un_normal = True
        text += _(" - 燃料不足：计划消耗 {0:.1f}，实际仅 {1:.1f}\n").format(fuel_can_burn, fuel_use)
    ri.materials_resouce[15] = fuel_have - int(fuel_use)
    # 燃料转化效率
    eff_per_fuel = 5 + 2 * max(main_level - 1, 0)
    op_bonus = _get_operator_power_bonus()  # 例如 0.1234
    fire_power = fuel_use * eff_per_fuel * (1 + op_bonus) * global_eff
    text += _(" - 火力发电：消耗燃料 {0:.1f} 单位，产出 {1:.1f} 度 (调控员加成 {2:.2%})\n").format(fuel_use, fire_power, op_bonus)

    # ------------ 清洁能源 ------------ #
    hydro, wind, solar = ri.other_power_facility_list
    # 设施等级: 动力区 cid=1 (Facility.csv 中 001, 读取为 int 1)
    facility_lv = ri.facility_level.get(1, 1)
    clean_eff = 1 + 0.1 * (facility_lv - 1)
    # 基础产能(每日)，按小时比例
    base_clean = [60, 40, 30]  # hydro, wind, solar/day/台
    # 分项清洁能源
    hydro_power_daily = hydro * base_clean[0] * clean_eff * global_eff
    wind_power_daily = wind * base_clean[1] * clean_eff * global_eff
    solar_power_daily = solar * base_clean[2] * clean_eff * global_eff
    clean_power_daily = hydro_power_daily + wind_power_daily + solar_power_daily
    hydro_power = hydro_power_daily * (hours / 24)
    wind_power = wind_power_daily * (hours / 24)
    solar_power = solar_power_daily * (hours / 24)
    clean_power = hydro_power + wind_power + solar_power
    text += _(" - 清洁能源：水{0}({3:.1f}) 风{1}({4:.1f}) 太阳能{2}({5:.1f}) 台，总产出 {6:.1f} 度 (效率x{7:.2f})\n").format(
        hydro, wind, solar, hydro_power, wind_power, solar_power, clean_power, clean_eff * global_eff
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
    discharge_rates = [0.02, 0.01, 0.005]
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
            # 显示分项发电潜力(按24h理论值)
            main_level = ri.orundum_reactor_list[0]
            aux_count = ri.orundum_reactor_list[1]
            base_fuel = 20 + 10 * max(main_level - 1, 0)
            fuel_can_burn_daily = base_fuel * (1 + 0.5 * aux_count)
            eff_per_fuel = 5 + 2 * max(main_level - 1, 0)
            op_bonus = _get_operator_power_bonus()
            global_eff = max(ri.effectiveness, 50) / 100
            fire_theory = fuel_can_burn_daily * eff_per_fuel * (1 + op_bonus) * global_eff
            hydro, wind, solar = ri.other_power_facility_list
            facility_lv = ri.facility_level.get(1, 1)
            clean_eff = 1 + 0.1 * (facility_lv - 1)
            base_clean = [60, 40, 30]
            hydro_t = hydro * base_clean[0] * clean_eff * global_eff
            wind_t = wind * base_clean[1] * clean_eff * global_eff
            solar_t = solar * base_clean[2] * clean_eff * global_eff
            overview.append(_("  源石反应炉 主:{0} 副:{1} 理论产出:{2:.1f}" ).format(main_level, aux_count, fire_theory))
            overview.append(_("  清洁能源 水力:{0}({3:.1f}) 风能:{1}({4:.1f}) 光伏:{2}({5:.1f}) 总:{6:.1f}" ).format(
                hydro, wind, solar, hydro_t, wind_t, solar_t, hydro_t+wind_t+solar_t))
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
            info.text = _("当前调控员数量：{0}  总效率加成：{1:.2%}\n" ).format(len(ri.power_operator_ids_list), op_bonus)
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
            for idx, cid in enumerate(main_ops):
                name = self._get_chara_name(cid)
                type_name = [_("源石反应炉"), _("水力发电　"), _("风能发电　"), _("光伏发电　")]
                # 显示文本
                chara_name = name if name else _("(空缺)")
                chara_name = attr_calculation.pad_display_width(chara_name, 12)
                main_text = _("{0}主调控员: {1}").format(type_name[idx], chara_name)
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
        while 1:
            title = draw.TitleLineDraw(_("发电设施管理"), self.width)
            title.draw()
            lv = ri.facility_level.get(1,1)
            return_list = []
            head = draw.NormalDraw(); head.width = self.width
            facility_text = attr_calculation.pad_display_width(_("设施"), 12, "center")
            info_text = attr_calculation.pad_display_width(_("信息"), 60, "center")
            head.text = _(" {0} | 当前 | {1} | 操作\n").format(facility_text, info_text)
            head.draw()
            # 主反应炉
            main_lv = ri.orundum_reactor_list[0]
            main_lv = str(main_lv).rjust(2, ' ')
            main_info = attr_calculation.pad_display_width(_("主炉等级决定单位燃料的发电效率"), 60)
            row = draw.NormalDraw(); row.width = self.width
            row.text = _(" 主源石反应炉 | {0}级 | {1} | ").format(main_lv, main_info)
            row.draw()
            def up_main():
                ri.orundum_reactor_list[0] = min(ri.orundum_reactor_list[0] + 1, 10)
            btn = draw.CenterButton(_("[升级]"), _("升级主源石反应炉"), 10, cmd_func=up_main); btn.draw(); return_list.append(btn.return_text)
            line_feed.draw()
            # 副反应炉
            aux = ri.orundum_reactor_list[1]
            aux = str(aux).rjust(2, ' ')
            aux_info = attr_calculation.pad_display_width(_("副炉数量影响每日燃料的燃烧数量，启用台数越多燃料消耗越多"), 60)
            row = draw.NormalDraw(); row.width = self.width
            row.text = _(" 副源石反应炉 | {0}台 | {1} | ").format(aux, aux_info)
            row.draw()
            def add_aux():
                ri.orundum_reactor_list[1] = min(ri.orundum_reactor_list[1] + 1, lv * 3)
            def sub_aux():
                if ri.orundum_reactor_list[1] > 0: ri.orundum_reactor_list[1] -= 1
            btn_add = draw.CenterButton(_("[+]"), _("增加副源石反应炉"), 8, cmd_func=add_aux); btn_add.draw(); return_list.append(btn_add.return_text)
            btn_sub = draw.CenterButton(_("[-]"), _("减少副源石反应炉"), 8, cmd_func=sub_aux); btn_sub.draw(); return_list.append(btn_sub.return_text)
            line_feed.draw()
            # 清洁能源
            names = [_("水力发电轮组"), _("风力发电机组"), _("光伏发电板组")]
            descs = [_("发电量小但稳定，仅在停靠时可用，行驶中无法使用"), _("发电量受风速影响大，仅在停靠时可用，行驶中无法使用"), _("发电量受日照影响大，停靠或行驶中均可使用")]
            limits = [lv * 5, lv * 8, lv * 8]
            for idx in range(3):
                num = ri.other_power_facility_list[idx]
                num = str(num).rjust(2, ' ')
                row = draw.NormalDraw(); row.width = self.width
                descs_now = attr_calculation.pad_display_width(descs[idx], 60)
                row.text = f" {names[idx]} | {num}组 | {descs_now} | "
                row.draw()
                def _make_add(i):
                    return lambda : self._inc_clean(i, +1, limits)
                def _make_sub(i):
                    return lambda : self._inc_clean(i, -1, limits)
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

    def _inc_clean(self, idx: int, delta: int, limits: List[int]):
        """增加或减少某类清洁能源设施"""
        ri = cache.rhodes_island
        ri.other_power_facility_list[idx] = max(0, min(ri.other_power_facility_list[idx] + delta, limits[idx]))

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
            cap_table = [500,1500,4000]
            rate_table = [0.02,0.01,0.005]
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
        if delta > 0:
            ri.battery_list[level] += 1
        else:
            if ri.battery_list[level] > 0:
                ri.battery_list[level] -= 1
        _recalc_battery_capacity()

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

