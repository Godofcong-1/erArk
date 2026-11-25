# -*- coding: UTF-8 -*-
"""存档系统：只写临时目录的存读档往返与 save_info、旧存档读档时的跨版本补全、温室生产线与阿玛雅编号两处旧档修复、旧档缺国家、读档归一化（路径分隔符 / 履历平铺字段 / 无壳卵生孕程）、2025.5.20 以前的整数行为 id"""
from _bootstrap import *  # noqa: F401,F403
import builtins
import io
import pickle
import shutil
import tempfile
import traceback

from Script.Core import old_chara_to_new
from Script.Design import basement, character_handle
from Script.System.Pregnancy_System import pregnancy_constant
from Script.UI.Flow import creator_character_flow
from Script.UI.Panel import agriculture_production_panel, collection_panel

# ==== 0. 写盘守卫与存档目录重定向 ====
# 存档只许写进本测试新建的临时目录：
#    ① get_save_dir_path / _get_save_info_path 换成指向临时目录的版本（原版会在仓库根目录建 save 目录）；
#    ② 在 builtins.open / io.open / os.open / os.makedirs / os.mkdir / 删除与改名类函数上装守卫，写的目标不在临时目录里就记一笔并抛 PermissionError
#       （装好后先自检一次：往仓库里一个不存在的子目录写文件必须被拦下）；
#    ③ 收尾时比对仓库 save 目录（文件名、大小、修改时间），前后必须一致；临时目录删干净。
#    establish_save 就是同步地 pickle 写两个文件（establish_save_linux 只是名字带 linux，没有子进程 / 线程），上面三道足以证明只写了临时目录
TMP_ROOT = os.path.abspath(tempfile.mkdtemp(prefix="erArk_save_test_"))
""" 本测试唯一允许写入的目录 """
_SAVE_DIR = os.path.join(ROOT, "save")
""" 仓库里的真实存档目录 """


def snapshot_dir(path: str) -> list:
    """
    记录一个目录下全部条目的相对路径、大小与修改时间
    Keyword arguments:
    path -- 目录路径
    Return arguments:
    list -- [(相对路径, 大小, 修改时间), ...]；目录不存在时为 None
    """
    if not os.path.isdir(path):
        return None
    result = []
    for dir_path, dir_name_list, file_name_list in os.walk(path):
        for name in sorted(dir_name_list + file_name_list):
            full_path = os.path.join(dir_path, name)
            stat = os.stat(full_path)
            result.append((os.path.relpath(full_path, path), stat.st_size, stat.st_mtime_ns))
    return sorted(result)


SAVE_DIR_BEFORE = snapshot_dir(_SAVE_DIR)
""" 跑测试前仓库 save 目录的快照 """


def inside_tmp(path) -> bool:
    """
    判断路径是否在临时目录之内
    Keyword arguments:
    path -- 文件路径（str / bytes / PathLike）
    Return arguments:
    bool -- 是否在临时目录之内
    """
    path = os.fsdecode(os.fspath(path))
    try:
        return os.path.commonpath([os.path.normcase(os.path.abspath(path)), os.path.normcase(TMP_ROOT)]) == os.path.normcase(TMP_ROOT)
    except ValueError:
        # 不同盘符
        return False


write_violation_list = []
""" 守卫拦下的越界写操作 """
_real_func = {
    "open": builtins.open,
    "os.open": os.open,
    "makedirs": os.makedirs,
    "mkdir": os.mkdir,
    "remove": os.remove,
    "unlink": os.unlink,
    "rmdir": os.rmdir,
    "rename": os.rename,
    "replace": os.replace,
    "rmtree": shutil.rmtree,
}
""" 被守卫替换前的原函数 """


def _deny(operation: str, path):
    """
    记录并拒绝一次越界写操作
    Keyword arguments:
    operation -- 操作名
    path -- 目标路径
    Return arguments:
    无（总是抛出 PermissionError）
    """
    write_violation_list.append((operation, str(path)))
    raise PermissionError(f"测试守卫：禁止在临时目录之外{operation} {path}")


def guarded_open(file, mode="r", *args, **kwargs):
    """
    带守卫的 open：写模式只许打开临时目录里的文件
    Keyword arguments:
    file -- 文件路径或文件描述符
    mode -- 打开模式
    Return arguments:
    file object -- 原 open 的返回值
    """
    if isinstance(file, (str, bytes, os.PathLike)) and any(flag in mode for flag in "wax+") and not inside_tmp(file):
        _deny("写文件", file)
    return _real_func["open"](file, mode, *args, **kwargs)


def guarded_os_open(path, flags, *args, **kwargs):
    """
    带守卫的 os.open：带写入 / 创建标志时只许打开临时目录里的文件
    Keyword arguments:
    path -- 文件路径
    flags -- 打开标志
    Return arguments:
    int -- 文件描述符
    """
    write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
    if flags & write_flags and not inside_tmp(path):
        _deny("写文件", path)
    return _real_func["os.open"](path, flags, *args, **kwargs)


def _make_path_guard(name: str, operation: str):
    """
    生成「第一个参数必须在临时目录里」的守卫函数
    Keyword arguments:
    name -- _real_func 里的原函数键
    operation -- 操作名
    Return arguments:
    function -- 守卫函数
    """

    def guard(path, *args, **kwargs):
        """
        守卫：目标不在临时目录里就拒绝
        Keyword arguments:
        path -- 目标路径
        Return arguments:
        原函数的返回值
        """
        if not inside_tmp(path):
            _deny(operation, path)
        return _real_func[name](path, *args, **kwargs)

    return guard


def _make_rename_guard(name: str):
    """
    生成改名类守卫：源与目标都必须在临时目录里
    Keyword arguments:
    name -- _real_func 里的原函数键
    Return arguments:
    function -- 守卫函数
    """

    def guard(src, dst, *args, **kwargs):
        """
        守卫：源或目标不在临时目录里就拒绝
        Keyword arguments:
        src -- 源路径
        dst -- 目标路径
        Return arguments:
        原函数的返回值
        """
        if not inside_tmp(src) or not inside_tmp(dst):
            _deny("改名", f"{src} -> {dst}")
        return _real_func[name](src, dst, *args, **kwargs)

    return guard


def install_write_guard():
    """
    装上写盘守卫
    Keyword arguments:
    无
    Return arguments:
    无
    """
    builtins.open = guarded_open
    io.open = guarded_open
    os.open = guarded_os_open
    os.makedirs = _make_path_guard("makedirs", "建目录")
    os.mkdir = _make_path_guard("mkdir", "建目录")
    os.remove = _make_path_guard("remove", "删文件")
    os.unlink = _make_path_guard("unlink", "删文件")
    os.rmdir = _make_path_guard("rmdir", "删目录")
    os.rename = _make_rename_guard("rename")
    os.replace = _make_rename_guard("replace")
    shutil.rmtree = _make_path_guard("rmtree", "删目录树")


def remove_write_guard():
    """
    拆掉写盘守卫，还原全部原函数
    Keyword arguments:
    无
    Return arguments:
    无
    """
    builtins.open = _real_func["open"]
    io.open = _real_func["open"]
    os.open = _real_func["os.open"]
    os.makedirs = _real_func["makedirs"]
    os.mkdir = _real_func["mkdir"]
    os.remove = _real_func["remove"]
    os.unlink = _real_func["unlink"]
    os.rmdir = _real_func["rmdir"]
    os.rename = _real_func["rename"]
    os.replace = _real_func["replace"]
    shutil.rmtree = _real_func["rmtree"]


def cleanup_tmp():
    """
    拆守卫并删掉临时目录
    Keyword arguments:
    无
    Return arguments:
    无
    """
    remove_write_guard()
    shutil.rmtree(TMP_ROOT, ignore_errors=True)


_base_excepthook = sys.excepthook


def _cleanup_then_exit(exc_type, exc_value, exc_traceback):
    """
    未捕获异常时先清理临时目录，再交给公共的崩溃处理
    Keyword arguments:
    exc_type -- 异常类型
    exc_value -- 异常对象
    exc_traceback -- 回溯对象
    Return arguments:
    无
    """
    cleanup_tmp()
    _base_excepthook(exc_type, exc_value, exc_traceback)


sys.excepthook = _cleanup_then_exit


def tmp_save_dir_path(save_id: str) -> str:
    """
    存档目录重定向：存档 id → 临时目录下的子目录（不在仓库里建 save 目录）
    Keyword arguments:
    save_id -- 存档id
    Return arguments:
    str -- 存档目录路径
    """
    return os.path.join(TMP_ROOT, str(save_id))


def tmp_save_info_path() -> str:
    """
    save_info.json 重定向到临时目录
    Keyword arguments:
    无
    Return arguments:
    str -- save_info.json 路径
    """
    return os.path.join(TMP_ROOT, "save_info.json")


save_handle.get_save_dir_path = tmp_save_dir_path
save_handle._get_save_info_path = tmp_save_info_path
install_write_guard()
section("写盘守卫自检")
# 探针路径的父目录不存在：万一守卫没生效，open 也只会因找不到目录而失败，不会真在仓库里留下文件
_GUARD_PROBE_PATH = os.path.join(ROOT, "erArk_save_test_guard_probe_dir", "probe.tmp")
""" 守卫自检用的仓库内路径 """
_guard_result = []
for _probe_name, _probe_func in (("open", lambda: open(_GUARD_PROBE_PATH, "wb")), ("io.open", lambda: io.open(_GUARD_PROBE_PATH, "w")),
                                 ("os.open", lambda: os.open(_GUARD_PROBE_PATH, os.O_WRONLY | os.O_CREAT))):
    try:
        _probe_func()
        _guard_result.append((_probe_name, "未拦截"))
    except PermissionError:
        _guard_result.append((_probe_name, "拦截"))
    except OSError as error:
        _guard_result.append((_probe_name, repr(error)))
check("往临时目录之外写文件被守卫拦下（open / io.open / os.open）", all(result == "拦截" for _name, result in _guard_result) and len(write_violation_list) == 3,
      _guard_result)
write_violation_list.clear()

# ==== 1. 存档 fixture ====
section("存档 fixture：新开局基地 + 模板角色")
cache.rhodes_island = basement.get_base_zero()
creator_character_flow.first_bonus_and_setting_updata()
cache.country = attr_calculation.get_country_reset(cache.country)
basement.get_base_updata()
ADV_SMITH = game_config.config_facility_open[13].NPC_id
""" 铁匠铺（开放房间 13）绑定的干员 adv：她在编时，读档会把这间房开放 """
# 与开新游戏一样按模板实例化全部角色：读档时存档里缺的模板角色会被补建（update_new_character），只建几个的话往返比对就不成立了
character_handle.init_character_list()
for adv in (1, 448, 450, ADV_SMITH):
    cache.npc_id_got.add(adv)
    move_to(adv, SCENE_DORM)
character_handle.init_character_facility_open()
check("fixture：阿米娅 / 阿玛雅 / 死芒 / 铁匠铺干员都按模板建好",
      [cache.character_data[cid].name for cid in (1, 448, 450)] == [_("阿米娅"), _("阿玛雅"), _("死芒")] and cache.character_data[ADV_SMITH].adv == ADV_SMITH,
      [(cid, cache.character_data[cid].name) for cid in (1, 448, 450, ADV_SMITH)])
pl.name = "测试博士"
set_time(datetime.datetime(2026, 9, 20, 15, 30))
ri = cache.rhodes_island
ri.materials_resouce[1] = 12345
ri.materials_resouce[31] = 77
ri.facility_level[16] = 3
ri.assembly_line[0] = [5, 0, 87.5, 0, 9]
amiya = cache.character_data[1]
amiya.favorability[0] = 321
amiya.ability[30] = 4
amiya.hit_point = 55
amiya.work.work_type = 111


def snapshot_cache() -> dict:
    """
    提取缓存里存读档往返要比对的关键字段
    Keyword arguments:
    无
    Return arguments:
    dict -- 字段名 → 值（素质 / 能力 / 经验只取非零项：读档会给角色补齐配置里新增的键；
            尿道 / 子宫处女素质（2 / 3）读档时按经验重算，由「新开局的角色素质与读档时的补素质规则一致」一段单独断言）
    """
    chara = {}
    for cid, cd in cache.character_data.items():
        chara[cid] = (cd.cid, cd.name, cd.adv, list(cd.position), cd.hit_point, cd.mana_point, dict(cd.favorability), cd.work.work_type, cd.dormitory,
                      {k: v for k, v in cd.ability.items() if v}, {k: v for k, v in cd.talent.items() if v and k not in (2, 3)}, {k: v for k, v in cd.experience.items() if v})
    now_ri = cache.rhodes_island
    return {
        "game_time": cache.game_time,
        "npc_id_got": set(cache.npc_id_got),
        "character": chara,
        "materials": dict(now_ri.materials_resouce),
        "facility_level": dict(now_ri.facility_level),
        "facility_open": dict(now_ri.facility_open),
        "assembly_line": {k: list(v) for k, v in now_ri.assembly_line.items()},
        "herb_garden_line": {k: list(v) for k, v in now_ri.herb_garden_line.items()},
        "green_house_line": {k: list(v) for k, v in now_ri.green_house_line.items()},
        "warehouse_capacity": now_ri.warehouse_capacity,
    }


CHARACTER_FIELD_NAME = ("cid", "name", "adv", "position", "hit_point", "mana_point", "favorability", "work_type", "dormitory", "ability", "talent", "experience")
""" snapshot_cache 里每个角色元组的字段名 """


def describe_snapshot_diff(old_snapshot: dict, new_snapshot: dict) -> list:
    """
    列出两份快照的差异，角色逐字段列出
    Keyword arguments:
    old_snapshot -- 旧快照
    new_snapshot -- 新快照
    Return arguments:
    list -- [(字段, 旧值, 新值), ...]，最多 8 条
    """
    result = []
    for key in old_snapshot:
        if old_snapshot[key] == new_snapshot[key]:
            continue
        if key != "character":
            result.append((key, old_snapshot[key], new_snapshot[key]))
            continue
        for cid in sorted(set(old_snapshot[key]) | set(new_snapshot[key])):
            old_one = old_snapshot[key].get(cid)
            new_one = new_snapshot[key].get(cid)
            if old_one == new_one:
                continue
            if old_one is None or new_one is None:
                result.append((f"character[{cid}]", old_one, new_one))
                continue
            for index, field_name in enumerate(CHARACTER_FIELD_NAME):
                if old_one[index] != new_one[index]:
                    result.append((f"character[{cid}].{field_name}", old_one[index], new_one[index]))
    return result[:8]


# ==== 2. 存读档往返 ====
section("新开局的角色素质与读档时的补素质规则一致")
# 读档时 old_chara_to_new.update_character_config_data 对每个 NPC 执行「没有 U / W 插入经验就有尿道 / 子宫处女素质」；
#    新开局的角色若不满足这条，第一次存读档后素质就会凭空变化。下面的往返比对因此不比这两个素质，由本条单独断言
virgin_missing = sorted(cid for cid, cd in cache.character_data.items()
                        if cid and ((cd.experience.get(63, 0) == 0 and not cd.talent.get(2, 0)) or (cd.experience.get(64, 0) == 0 and not cd.talent.get(3, 0))))
check("新开局：没有 U / W 插入经验的 NPC 都带尿道 / 子宫处女素质", not virgin_missing,
      [(cid, cache.character_data[cid].name) for cid in virgin_missing])

section("存读档往返（只写临时目录）")
before = snapshot_cache()
save_handle.establish_save("1")
check("establish_save 在临时目录写出头部 0 与数据 1 两个文件",
      os.path.isfile(os.path.join(TMP_ROOT, "1", "0")) and os.path.isfile(os.path.join(TMP_ROOT, "1", "1")), os.listdir(TMP_ROOT))
check("judge_save_file_exist：写过的存档在、没写过的不在", save_handle.judge_save_file_exist("1") and not save_handle.judge_save_file_exist("2"))
head = save_handle.load_save_info_head("1")
check("存档头部：版本号、游戏时间、玩家名", head["game_verson"] == normal_config.config_normal.verson and head["game_time"] == before["game_time"] and head["character_name"] == "测试博士",
      head)
loaded_only = save_handle.load_save("1")
check("load_save 只读出缓存对象、不覆盖当前内存", isinstance(loaded_only, game_type.Cache) and set(loaded_only.character_data) == set(cache.character_data) and loaded_only is not cache)
# 改掉内存里的值，读档后能恢复才说明数据真是从文件里来的
set_time(DEFAULT_TIME)
ri.materials_resouce[1] = 0
amiya.favorability[0] = 0
remove_character(450)
save_handle.input_load_save("1")
after = snapshot_cache()
check("读档后关键字段与存档前完全一致（角色、时间、已有干员、资源、设施、生产线）", before == after, describe_snapshot_diff(before, after))
check("读档换掉了角色对象（玩家 fixture 已不是存档里的玩家）", cache.character_data[0] is not pl and cache.character_data[0].name == "测试博士")
check("读档重置临时界面状态：鼠标状态为新对象、更新流程嵌套深度为 0", isinstance(cache.wframe_mouse, game_type.WFrameMouse) and cache.game_update_flow_running == 0)
pl = cache.character_data[0]
ri = cache.rhodes_island

section("save_info.json（上次存档页码与 id）")
save_handle.set_last_save_id("1")
save_handle.set_last_save_page(3)
check("上次存档 id 与页码写进临时目录的 save_info.json 并读得回来",
      save_handle.get_last_save_id() == "1" and save_handle.get_last_save_page() == 3 and os.path.isfile(os.path.join(TMP_ROOT, "save_info.json")))
save_handle.remove_save("1")
check("remove_save 删掉存档目录", not os.path.exists(os.path.join(TMP_ROOT, "1")) and not save_handle.judge_save_file_exist("1"))


def make_old_save(save_id: str, mutate_func):
    """
    用当前缓存写一个存档，再把它读成独立的对象、按旧版本的样子改坏后原样写回，造出一个「旧存档」
    Keyword arguments:
    save_id -- 存档id
    mutate_func -- 接收反序列化出来的 Cache 对象并就地修改的函数（改的是存档里的副本，不碰当前内存）
    Return arguments:
    无
    """
    save_handle.establish_save(save_id)
    with open(os.path.join(save_handle.get_save_dir_path(save_id), "1"), "rb") as save_file:
        old_cache = pickle.load(save_file)
    mutate_func(old_cache)
    save_handle.write_save_data(save_id, "1", old_cache)


# ==== 3. 旧存档：读档时的跨版本补全 ====
section("旧存档读档：缺字段、类型不符、设置、地图、资源与设施的补全")
DROP_RESOURCE_ID = 36
""" 旧档里没有的资源 """
DROP_FACILITY_ID = 41
""" 旧档里没有的设施 """
DROP_OPEN_ID = next(cid for cid in game_config.config_facility_open if game_config.config_facility_open[cid].NPC_id == 0)
""" 旧档里没有的、不绑定干员的开放房间 """
DROP_BOOK_ID = sorted(game_config.config_book)[0]
""" 旧档里没有借阅记录的书 """
MISSING_SCENE = sorted(cache.scene_data)[-1]
""" 旧档里还没有的场景 """
NEW_CHARACTER_ADV = max(adv for adv in cache.npc_tem_data if adv not in cache.npc_id_got and adv not in (448, 450))
""" 旧档里还没有的模板角色（后来才实装） """
DEAD_ROOM = ["教", "不存在的教室"]
""" 地图改建后已删除的房间（所属区块还在） """
DEAD_BLOCK = ["不存在的区块", "不存在的房间"]
""" 整个区块都已删除 """
pl.pl_collection.npc_panties_tem.clear()
pl.pl_collection.npc_socks_tem.clear()
PAN_ID = sorted(game_config.config_clothing_tem)[0]
""" 待摆放的内裤藏品 """
SOCK_ID = sorted(game_config.config_clothing_tem)[1]
""" 待摆放的袜子藏品 """


def mutate_old_save(old: game_type.Cache):
    """
    把存档副本改成旧版本的样子
    Keyword arguments:
    old -- 反序列化出来的存档缓存
    Return arguments:
    无
    """
    old_ri = old.rhodes_island
    # Cache 级：旧版本还没有的字段；Rhodes_Island 里类型对不上的字段；int 默认值的字段存成了 float
    del old.__dict__["today_taiggered_event_record"]
    old_ri.milk_in_fridge = []
    old_ri.effectiveness = 87.5
    # 资源、设施等级、开放房间、书籍借阅：配置里新增的条目旧档里没有
    del old_ri.materials_resouce[DROP_RESOURCE_ID]
    del old_ri.facility_level[DROP_FACILITY_ID]
    del old_ri.facility_open[DROP_OPEN_ID]
    old_ri.facility_open[13] = False
    del old_ri.book_borrow_dict[DROP_BOOK_ID]
    # 设置：基础设置缺一项、另一项被玩家改过；生殖方式设置整个不存在；AI 设置、体检设置、调教设置都是空的
    del old.all_system_setting.base_setting[10]
    old.all_system_setting.base_setting[2] = 0
    del old.all_system_setting.__dict__["birth_type_setting"]
    old.ai_setting.ai_chat_setting = {}
    old_ri.physical_examination_setting = {}
    old_ri.confinement_training_setting = {}
    # 地图：缺一个场景；死芒站在已删除的房间里，铁匠铺干员站在整个已删除的区块里
    del old.scene_data[MISSING_SCENE]
    old.character_data[450].position = list(DEAD_ROOM)
    old.character_data[ADV_SMITH].position = list(DEAD_BLOCK)
    # 后来才实装的角色：旧档里还没有她
    del old.character_data[NEW_CHARACTER_ADV]
    for dict_name in ("token_list", "first_panties", "npc_panties", "npc_socks"):
        getattr(old.character_data[0].pl_collection, dict_name).pop(NEW_CHARACTER_ADV, None)
    # 监禁：被监禁却不在囚犯名单里
    old.character_data[1].sp_flag.imprisonment = True
    old.character_data[1].sp_flag.escaping = False
    old_ri.current_prisoners = {}
    # 角色结构体里后来新增的字段
    del old.character_data[0].pl_collection.used_condoms
    del old.character_data[1].dirty.condom_decoration
    del old.character_data[1].pregnancy.eggs
    del old.character_data[1].action_info.sleep_disturbed_end_time
    # 临时界面状态：旧版把「正在按任意键继续」的 0 值存了进来；更新流程嵌套深度残留
    old.wframe_mouse.w_frame_up = 0
    old.game_update_flow_running = 3
    # 温室（9890fac79）：有温室字段、但还没有任何温室生产线
    old_ri.green_house_line = {}
    # 阿玛雅（acc54a85f）：旧版的编号修正只改了 adv 没改 cid，留下键与 adv 为 448、cid 却仍是死芒 450 的阿玛雅；
    #    她在收藏品的四个字典里都没有条目。阿米娅只有信物条目，内裤 / 袜子两个字典单独缺键，已有的收藏不能被覆盖
    old.character_data[448].cid = 450
    old_collection = old.character_data[0].pl_collection
    for dict_name in ("token_list", "first_panties", "npc_panties", "npc_socks"):
        getattr(old_collection, dict_name).pop(448, None)
    old_collection.token_list[1] = True
    old_collection.first_panties[1] = "阿米娅的内裤"
    old_collection.npc_panties.pop(1, None)
    old_collection.npc_socks.pop(1, None)
    # 待摆放的藏品：阿玛雅的内裤、阿米娅的袜子，以及一个已不存在的角色（如被移除的异常女儿）的内裤
    old_collection.npc_panties_tem = {448: [PAN_ID], 99999: [PAN_ID]}
    old_collection.npc_socks_tem = {1: [SOCK_ID]}


make_old_save("2", mutate_old_save)
cache.today_taiggered_event_record = {"当前内存里的值"}
try:
    save_handle.input_load_save("2")
    check("旧存档 input_load_save 不抛异常", True)
except Exception as error:
    traceback.print_exc()
    check("旧存档 input_load_save 不抛异常", False, repr(error))
pl = cache.character_data[0]
ri = cache.rhodes_island
zero_setting = attr_calculation.get_system_setting_zero()
check("Cache 缺的字段补成默认值（不是沿用当前内存里的值）", cache.today_taiggered_event_record == set(), cache.today_taiggered_event_record)
check("类型对不上的字段重置为默认值（list → dict）", ri.milk_in_fridge == {}, ri.milk_in_fridge)
check("int 默认值的字段存成 float 时保留原值（不当作类型不符）", ri.effectiveness == 87.5, ri.effectiveness)
check("配置里新增的资源补 0、设施等级补 1、开放房间补关闭、书籍补未借出",
      ri.materials_resouce.get(DROP_RESOURCE_ID) == 0 and ri.facility_level.get(DROP_FACILITY_ID) == 1 and ri.facility_open.get(DROP_OPEN_ID) is False and ri.book_borrow_dict.get(DROP_BOOK_ID) == -1,
      (ri.materials_resouce.get(DROP_RESOURCE_ID), ri.facility_level.get(DROP_FACILITY_ID), ri.facility_open.get(DROP_OPEN_ID), ri.book_borrow_dict.get(DROP_BOOK_ID)))
check("绑定干员的房间：该干员已在编时读档自动开放", ri.facility_open[13] is True)
check("基础设置：缺的项补默认值，玩家改过的项保留", cache.all_system_setting.base_setting[10] == zero_setting.base_setting[10] and cache.all_system_setting.base_setting[2] == 0,
      (cache.all_system_setting.base_setting.get(10), cache.all_system_setting.base_setting.get(2)))
check("生殖方式设置整个缺失时按默认值重建", cache.all_system_setting.birth_type_setting == zero_setting.birth_type_setting, cache.all_system_setting.birth_type_setting)
check("AI 设置、体检设置、调教设置补齐全部键",
      set(cache.ai_setting.ai_chat_setting) == set(game_config.config_ai_chat_setting)
      and set(ri.physical_examination_setting) == set(attr_calculation.get_physical_exam_setting_zero())
      and set(ri.confinement_training_setting) == set(game_config.config_confinement_training_setting))
check("地图：旧档缺的场景补回", MISSING_SCENE in cache.scene_data)
dead_room_entry = [DEAD_ROOM[0], "0"]
check("站在已删除房间里的角色挪到所属区块的入口，并登记进入口的角色名单",
      cache.character_data[450].position == dead_room_entry and 450 in cache.scene_data[scene_str(dead_room_entry)].character_list, cache.character_data[450].position)
check("整个区块都已删除时挪到地图原点", cache.character_data[ADV_SMITH].position == ["0", "0"], cache.character_data[ADV_SMITH].position)
check("被监禁却不在囚犯名单里的角色补进名单", 1 in ri.current_prisoners, ri.current_prisoners)
new_character = cache.character_data.get(NEW_CHARACTER_ADV)
check("旧档里没有的模板角色按模板补建（cid 即 adv），收藏品里也有她的条目",
      new_character is not None and new_character.cid == NEW_CHARACTER_ADV and new_character.name == cache.npc_tem_data[NEW_CHARACTER_ADV].Name
      and NEW_CHARACTER_ADV in pl.pl_collection.token_list and NEW_CHARACTER_ADV in pl.pl_collection.npc_panties,
      (NEW_CHARACTER_ADV, new_character.name if new_character else None))
check("角色结构体后来新增的字段补默认值（避孕套、污浊装饰、卵、被吵醒结束时间）",
      pl.pl_collection.used_condoms == [] and cache.character_data[1].dirty.condom_decoration == {} and cache.character_data[1].pregnancy.eggs == {}
      and cache.character_data[1].action_info.sleep_disturbed_end_time == datetime.datetime(1, 1, 1))
check("鼠标状态不随存档带入（旧档残留的 w_frame_up=0 会让之后的输入卡死）", cache.wframe_mouse.w_frame_up == game_type.WFrameMouse.w_frame_up, vars(cache.wframe_mouse))
check("更新流程嵌套深度重置为 0", cache.game_update_flow_running == 0, cache.game_update_flow_running)
cache.character_data[1].sp_flag.imprisonment = False
ri.current_prisoners = {}

# ==== 4. 温室生产线 ====
section("没有温室字段的更旧存档：按开局默认值补出温室生产线 0")
old_rhodes = basement.get_base_zero()
del old_rhodes.green_house_line
save_handle.update_dict_with_default(old_rhodes.__dict__, basement.get_base_zero().__dict__)
check("update_dict_with_default 补出带生产线 0 的温室字段", old_rhodes.green_house_line == {0: [0, 0, 0, 0, 0]}, old_rhodes.green_house_line)

section("锁定修复 9890fac79：没有温室生产线数据的旧存档，读档后刷新基地数值不报错")
# 旧档读进来温室字段仍是空字典（update_dict_with_default 不动已有的键）；
#    之后任何一次 get_base_updata（打开农业 / 宿舍管理 / 课表面板都会调）走「温室生产线初始化」分支时，
#    修复前那里残留了一行引用药田循环变量的代码，疗养庭院排在药田之前，变量尚未赋值，直接 UnboundLocalError
check("读档后温室字段仍是旧档里的空字典", ri.green_house_line == {}, ri.green_house_line)
try:
    basement.get_base_updata()
    check("get_base_updata 不抛异常", True)
except Exception as error:
    traceback.print_exc()
    check("get_base_updata 不抛异常", False, repr(error))
check("补出温室生产线 0，效率按温室口径计算", 0 in ri.green_house_line
      and ri.green_house_line[0][2] == agriculture_production_panel.calculate_agriculture_line_efficiency(0, agriculture_type=1)[1], ri.green_house_line)
check("药田生产线的效率按药田口径计算（不被温室的值改写）",
      ri.herb_garden_line[0][2] == agriculture_production_panel.calculate_agriculture_line_efficiency(0, agriculture_type=0)[1], ri.herb_garden_line)

# ==== 5. 锁定修复：阿玛雅的角色编号 ====
section("锁定修复 acc54a85f：旧存档中阿玛雅的角色编号修正不完整，读档时自动修复，摆放藏品不报错")
amaya = cache.character_data[448]
check("读档把键与 adv 为 448、cid 却是 450 的阿玛雅的 cid 改回 448", amaya.cid == 448 and amaya.adv == 448 and amaya.name == _("阿玛雅"), (amaya.cid, amaya.adv, amaya.name))
check("死芒不受影响", cache.character_data[450].cid == 450 and cache.character_data[450].name == _("死芒"))
collection = pl.pl_collection
check("阿玛雅在收藏品四个字典里都补上了条目", collection.token_list.get(448) is False and collection.first_panties.get(448) == ""
      and collection.npc_panties.get(448) == [] and collection.npc_socks.get(448) == [],
      (collection.token_list.get(448), collection.first_panties.get(448), collection.npc_panties.get(448), collection.npc_socks.get(448)))
check("只缺内裤 / 袜子字典的阿米娅也补上了，已有的信物与初次内裤不被覆盖",
      collection.npc_panties.get(1) == [] and collection.npc_socks.get(1) == [] and collection.token_list[1] is True and collection.first_panties[1] == "阿米娅的内裤",
      (collection.npc_panties.get(1), collection.npc_socks.get(1), collection.token_list.get(1), collection.first_panties.get(1)))
try:
    collection_panel.collapse_collection()
    check("摆放藏品（collapse_collection）不抛异常", True)
except Exception as error:
    traceback.print_exc()
    check("摆放藏品（collapse_collection）不抛异常", False, repr(error))
pan_name = game_config.config_clothing_tem[PAN_ID].name
sock_name = game_config.config_clothing_tem[SOCK_ID].name
check("阿玛雅的内裤、阿米娅的袜子摆进收藏，已不存在的角色被跳过，待摆放列表清空",
      collection.npc_panties.get(448) == [pan_name] and collection.npc_socks.get(1) == [sock_name] and 99999 not in collection.npc_panties
      and not collection.npc_panties_tem and not collection.npc_socks_tem,
      (collection.npc_panties.get(448), collection.npc_socks.get(1), collection.npc_panties_tem, collection.npc_socks_tem))

section("阿玛雅编号修正的主分支（fix_wrong_character）：阿玛雅占着死芒的 450 号")
fake_dead_mango = game_type.Character()
fake_dead_mango.cid = 448
fake_dead_mango.adv = 448
fake_dead_mango.name = _("死芒")
old_amaya = game_type.Character()
old_amaya.cid = 450
old_amaya.adv = 450
old_amaya.name = _("阿玛雅")
fake_loaded_dict = {"character_data": {0: pl, 448: fake_dead_mango, 450: old_amaya}, "npc_tem_data": dict(cache.npc_tem_data)}
fix_count = old_chara_to_new.fix_wrong_character(fake_loaded_dict)
fixed_data = fake_loaded_dict["character_data"]
check("阿玛雅挪到 448 号，cid 与 adv 一起改成 448", fixed_data[448] is old_amaya and old_amaya.cid == 448 and old_amaya.adv == 448, (old_amaya.cid, old_amaya.adv))
check("450 号按模板重建为死芒", fixed_data[450].name == _("死芒") and fixed_data[450].cid == 450 and fixed_data[450].adv == 450 and fix_count >= 1,
      (fixed_data[450].name, fixed_data[450].cid, fixed_data[450].adv, fix_count))

# ==== 6. 旧存档缺少后来新增的国家 ====
section("旧存档缺少后来新增的国家（大地图数据）")
# 出身地 / 国家（Birthplace.csv）新增一行之后，旧档的国家数据里没有它；早于势力外交系统（2024-08）的存档则整个没有国家数据。
#    读档时 get_country_reset 给存档里的国家数据补这个国家的感染率与病人数量系数
DROP_COUNTRY_ID = cache.rhodes_island.current_location[0]
""" 旧档里没有的国家：取罗德岛当前所在国，医疗部每天按它的病人数量系数刷新病人 """


def mutate_drop_country(old: game_type.Cache):
    """
    把存档副本的国家数据改成还没有 DROP_COUNTRY_ID 这个国家的样子
    Keyword arguments:
    old -- 反序列化出来的存档缓存
    Return arguments:
    无
    """
    old.country.country_infection_rate.pop(DROP_COUNTRY_ID, None)
    old.country.country_infection_patient_ratio.pop(DROP_COUNTRY_ID, None)


make_old_save("3", mutate_drop_country)
live_country = cache.country
# 从标题画面读档：进程里还没开过任何一局，缓存是 game_type.Cache() 的初值，国家数据为空
cache.country = game_type.Country()
try:
    save_handle.input_load_save("3")
    check("从标题画面读这个旧档（内存里还没有国家数据）不抛异常", True)
except Exception as error:
    traceback.print_exc()
    check("从标题画面读这个旧档（内存里还没有国家数据）不抛异常", False, repr(error))
# 游戏中读档：内存里是一局完整的游戏
cache.country = live_country
save_handle.input_load_save("3")
check("游戏中读这个旧档：读进来的国家数据补出了该国的感染率与病人数量系数",
      DROP_COUNTRY_ID in cache.country.country_infection_rate and DROP_COUNTRY_ID in cache.country.country_infection_patient_ratio,
      (cache.country.country_infection_rate.get(DROP_COUNTRY_ID), cache.country.country_infection_patient_ratio.get(DROP_COUNTRY_ID)))
pl = cache.character_data[0]
ri = cache.rhodes_island

# ==== 7. 读档归一化 ====
section("读档归一化：存档里外系统的路径分隔符")
FOREIGN_SEP = "/" if os.sep == "\\" else "\\"
""" 另一种系统的路径分隔符（Linux / macOS 存的档在 Windows 上读，或反过来） """
path_cache = game_type.Cache()
path_cache.scene_data = {f"宿舍{FOREIGN_SEP}1区": game_type.Scene()}
path_cache.scene_data[f"宿舍{FOREIGN_SEP}1区"].scene_path = f"宿舍{FOREIGN_SEP}1区"
path_cache.map_data = {}
path_chara = game_type.Character()
path_chara.dormitory = f"宿舍{FOREIGN_SEP}1区{FOREIGN_SEP}101"
path_chara.work.dormitory_admin_target_room = f"宿舍{FOREIGN_SEP}1区{FOREIGN_SEP}102"
path_cache.character_data = {101: path_chara}
path_cache.rhodes_island = game_type.Rhodes_Island()
path_cache.rhodes_island.facility_damage_data = {f"制造加工{FOREIGN_SEP}车间": 2}
path_cache.rhodes_island.maintenance_place = {101: f"动力{FOREIGN_SEP}0"}
save_handle._normalize_loaded_save_paths(path_cache)
check("场景键与场景路径换成本系统分隔符", list(path_cache.scene_data) == [f"宿舍{os.sep}1区"] and path_cache.scene_data[f"宿舍{os.sep}1区"].scene_path == f"宿舍{os.sep}1区",
      list(path_cache.scene_data))
check("角色的宿舍与宿管目标房间换成本系统分隔符",
      path_chara.dormitory == f"宿舍{os.sep}1区{os.sep}101" and path_chara.work.dormitory_admin_target_room == f"宿舍{os.sep}1区{os.sep}102",
      (path_chara.dormitory, path_chara.work.dormitory_admin_target_room))
check("设施损坏记录的键与检修地点换成本系统分隔符",
      list(path_cache.rhodes_island.facility_damage_data) == [f"制造加工{os.sep}车间"] and path_cache.rhodes_island.maintenance_place[101] == f"动力{os.sep}0",
      (path_cache.rhodes_island.facility_damage_data, path_cache.rhodes_island.maintenance_place))

section("读档归一化：性行为履历的旧版平铺处女字段并进 first_part_sex_dict")
OLD_TIME = datetime.datetime(2026, 5, 1, 20, 0)
""" 旧档里记下的初体验时间 """
NEW_RECORD_DICT_LIST = ("first_part_sex_dict", "first_shoot_body_dict", "first_strong_orgasm_dict", "first_super_orgasm_dict", "first_plural_orgasm_dict",
                        "fall_talent_time_dict", "first_mark_dict", "first_h_mode_dict", "first_special_record_dict")
""" 性行为履历系统新增的九个字典 """


def make_old_record_character(cid: int) -> game_type.Character:
    """
    造一个带旧版平铺处女字段的角色（没有新版的九个字典）
    Keyword arguments:
    cid -- 角色id（0 为玩家）
    Return arguments:
    game_type.Character -- 角色对象
    """
    character_data = game_type.Character()
    character_data.cid = cid
    record = character_data.first_record
    for dict_name in NEW_RECORD_DICT_LIST:
        if hasattr(record, dict_name):
            delattr(record, dict_name)
    record.first_sex_id = 0
    record.first_sex_time = OLD_TIME
    record.first_sex_place = ["宿舍", "1区", "101"]
    record.first_sex_posture = "正常位"
    record.first_sex_item = -1
    record.first_a_sex_id = 0
    record.first_a_sex_time = OLD_TIME
    record.first_a_sex_place = ["宿舍", "1区", "101"]
    record.first_a_sex_posture = "后背位"
    record.first_a_sex_item = -1
    record.first_u_sex_id = 0
    record.first_u_sex_time = OLD_TIME
    record.first_u_sex_place = ["宿舍", "1区", "101"]
    record.first_u_sex_posture = ""
    record.first_u_sex_item = 1
    record.first_w_sex_id = -1
    record.first_w_sex_time = datetime.datetime(1, 1, 1)
    record.first_w_sex_place = ["0"]
    record.first_w_sex_posture = ""
    record.first_m_sex_time = OLD_TIME
    return character_data


npc_old = make_old_record_character(101)
player_old = make_old_record_character(0)
save_handle._migrate_first_record_flat_fields(npc_old)
save_handle._migrate_first_record_flat_fields(player_old)
npc_record = npc_old.first_record
check("九个新字典都补上了", all(isinstance(getattr(npc_record, name, None), dict) for name in NEW_RECORD_DICT_LIST))
check("NPC：V 处女转入键 6、A 处女转入键 8、U 处女转入键 9（旧道具编号 1 采尿器改记为 2）、M 处女时间转入键 2，W 没有记录不建条目",
      sorted(npc_record.first_part_sex_dict) == [2, 6, 8, 9] and npc_record.first_part_sex_dict[6]["posture"] == "正常位"
      and npc_record.first_part_sex_dict[8]["posture"] == "后背位" and npc_record.first_part_sex_dict[9]["item"] == 2 and npc_record.first_part_sex_dict[2]["time"] == OLD_TIME,
      npc_record.first_part_sex_dict)
check("NPC：V 处女的平铺字段转走后重置为默认值，A / U / W / M 的平铺字段删除",
      npc_record.first_sex_id == -1 and npc_record.first_sex_time == datetime.datetime(1, 1, 1)
      and not any(hasattr(npc_record, name) for name in ("first_a_sex_id", "first_u_sex_item", "first_w_sex_time", "first_m_sex_time")))
check("玩家：V 平铺字段保留给童贞记录用，不转入键 6", 6 not in player_old.first_record.first_part_sex_dict and player_old.first_record.first_sex_time == OLD_TIME,
      player_old.first_record.first_part_sex_dict)
_migrated = dict(npc_record.first_part_sex_dict)
save_handle._migrate_first_record_flat_fields(npc_old)
check("再迁移一次是幂等的", npc_record.first_part_sex_dict == _migrated)

section("读档归一化：无壳卵生种族在实装前按单胎胎生怀上的孕程，读档时清除")
SOFT_EGG_RACE = next(cid for cid, race in game_config.config_race.items() if getattr(race, "birth_type", 1) == pregnancy_constant.BIRTH_TYPE_EGG_SOFT)
""" 一个无壳卵生种族 """


def make_pregnant_character(race_id: int) -> game_type.Character:
    """
    造一个处于妊娠期、刚生过一胎还在育儿的角色
    Keyword arguments:
    race_id -- 种族id
    Return arguments:
    game_type.Character -- 角色对象
    """
    character_data = game_type.Character()
    character_data.race = race_id
    character_data.talent = {20: 0, 21: 1, 22: 0, 23: 1, 24: 1, 26: 1, 27: 1, 35: 0}
    character_data.pregnancy.fetus_count = 2
    return character_data


soft_on = make_pregnant_character(SOFT_EGG_RACE)
soft_off = make_pregnant_character(SOFT_EGG_RACE)
viviparous = make_pregnant_character(0)
egg_cache = game_type.Cache()
egg_cache.character_data = {1: soft_on, 2: viviparous}
egg_cache.all_system_setting = attr_calculation.get_system_setting_zero()
egg_cache.all_system_setting.birth_type_setting[pregnancy_constant.BIRTH_TYPE_EGG_SOFT] = 1
save_handle._normalize_loaded_save_paths(egg_cache)
check("开关开启：无壳卵生角色的妊娠与孕肚清除、胎数归零，产后 / 育儿 / 泌乳保留",
      soft_on.talent[21] == 0 and soft_on.talent[26] == 0 and soft_on.pregnancy.fetus_count == 0 and soft_on.talent[23] == 1 and soft_on.talent[24] == 1 and soft_on.talent[27] == 1,
      (soft_on.talent, soft_on.pregnancy.fetus_count))
check("胎生种族的孕程不受影响", viviparous.talent[21] == 1 and viviparous.pregnancy.fetus_count == 2)
egg_cache.character_data = {1: soft_off}
egg_cache.all_system_setting.birth_type_setting[pregnancy_constant.BIRTH_TYPE_EGG_SOFT] = 0
save_handle._normalize_loaded_save_paths(egg_cache)
check("开关关闭：该种族按单胎胎生运行，孕程是正常妊娠，每次读档都不能清（plan_21）", soft_off.talent[21] == 1 and soft_off.pregnancy.fetus_count == 2,
      (soft_off.talent, soft_off.pregnancy.fetus_count))

# ==== 8. 2025.5.20 以前的存档：整数形式的行为 id ====
section("锁定修复：2025.5.20 以前的存档里整数形式的行为 id 回到发呆，二段行为的整数键删除")
# 行为 id 在 2025.5.20 由整数改为字符串。原先按 Behavior_Int / SecondBehavior_Int 两张编号表逐个换算，
#    但这两张表后来被当成活的编号表维护：137 原是买食物，后来让给了拒绝饮酒，旧档里买食物的角色读进来就成了拒绝饮酒；
#    编号表里没有的整数则原样留在存档里，之后按 en_name 查行为配置时 KeyError
KEEP_SECOND_BEHAVIOR = next(bid for bid, behavior_data in game_config.config_behavior.items() if "二段结算" in behavior_data.tag)
""" 旧档里已是字符串键、待触发标记为 1 的二段行为 """
ALL_SECOND_BEHAVIOR = {bid for bid, behavior_data in game_config.config_behavior.items() if "二段结算" in behavior_data.tag}
""" 二段行为数据库里的全部二段行为 """
old_int_chara = cache.character_data[1]
for old_behavior_int in (137, 99999):
    old_int_chara.behavior.behavior_id = old_behavior_int
    old_int_chara.behavior.duration = 30
    old_int_chara.second_behavior[1418] = 1
    old_int_chara.second_behavior[99999] = 1
    old_int_chara.second_behavior[KEEP_SECOND_BEHAVIOR] = 1
    old_chara_to_new.update_character_config_data(old_int_chara)
    check(f"整数行为 id {old_behavior_int} 回到发呆，持续 1 分钟",
          old_int_chara.behavior.behavior_id == constant.Behavior.SHARE_BLANKLY and old_int_chara.behavior.duration == 1,
          (old_int_chara.behavior.behavior_id, old_int_chara.behavior.duration))
    check(f"（{old_behavior_int}）二段行为：整数键全部删除，字符串键的标记保留，全部二段行为都有键",
          not [key for key in old_int_chara.second_behavior if isinstance(key, int)]
          and old_int_chara.second_behavior[KEEP_SECOND_BEHAVIOR] == 1 and ALL_SECOND_BEHAVIOR <= set(old_int_chara.second_behavior),
          [key for key in old_int_chara.second_behavior if isinstance(key, int)])
old_int_chara.second_behavior[KEEP_SECOND_BEHAVIOR] = 0

# ==== 9. 收尾 ====
section("收尾：只写了临时目录")
check("写盘守卫没有拦到任何越界写", not write_violation_list, write_violation_list[:5])
check("临时目录里只有本测试写的东西", set(os.listdir(TMP_ROOT)) <= {"2", "3", "save_info.json"}, os.listdir(TMP_ROOT))
cleanup_tmp()
check("临时目录已删除", not os.path.exists(TMP_ROOT), TMP_ROOT)
check("仓库 save 目录前后一致（不存在的仍不存在；存在的话文件名、大小、修改时间都没变）", snapshot_dir(_SAVE_DIR) == SAVE_DIR_BEFORE)

finish()
