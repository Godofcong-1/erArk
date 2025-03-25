from types import FunctionType
from Script.Core import cache_control, game_type, get_text, constant
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.Design import handle_premise, attr_calculation, game_time, attr_text
import openai
import google.generativeai as genai
import os
import httpx
import re

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """

def get_key_type() -> str:
    """
    获取当前使用的api密钥类型\n
    Return arguments:
    key_type -- 当前使用的api密钥类型
    """
    model = cache.ai_setting.ai_chat_setting[5]
    # 如果没有输入模型名，则返回空字符串
    if not model:
        return ''
    if 'gpt' in model:
        return 'OPENAI_API_KEY'
    elif 'gemini' in model:
        return 'GEMINI_API_KEY'
    elif 'deepseek' in model:
        return 'DEEPSEEK_API_KEY'
    else:
        return 'OPENAI_API_KEY'


def save_ai_talk_record(character_id: int, behavior_id: int, ai_generated_text: str) -> None:
    """
    将AI生成的对话记录保存到CSV文件中
    参数:
        character_id: int 角色ID
        behavior_id: int 行为ID
        ai_generated_text: str AI生成的文本
    返回:
        None
    """
    # 保存路径
    save_path = "data/talk/ai/ai_talk.csv"
    # 如果文件不存在，则创建文件并写入表头
    if not os.path.exists(save_path):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("cid,behavior_id,adv_id,premise,context\n")
            f.write("口上id,触发口上的行为id,口上限定的剧情npcid,前提id,口上内容\n")
            f.write("str,int,int,str,str\n")
            f.write("0,0,0,0,1\n")
            f.write("口上配置数据,,,,\n")
    # 读取save_path文件的最后一行，获取其cid，然后加1
    with open(save_path, "r", encoding='utf-8') as f:
        lines = f.readlines()
        last_line = lines[-1]
        last_cid = last_line.split(",")[0]
        if last_cid == "口上配置数据":
            new_cid = 0
        else:
            new_cid = int(last_cid) + 1
    # 开始数据处理
    character_data = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    # 处理名字，将角色名替换为{Name}，交互对象名替换为{TargetName}
    Name = character_data.name
    TargetNickName = target_character_data.name
    if Name in ai_generated_text:
        ai_generated_text = ai_generated_text.replace(Name, '{Name}')
    if character_id != 0 or character_data.target_character_id != 0:
        if TargetNickName in ai_generated_text:
            ai_generated_text = ai_generated_text.replace(TargetNickName, '{TargetName}')
    # 前提文本
    premise_text = "generate_by_ai"
    # 触发者
    if character_id == 0:
        premise_text += "&sys_0"
    else:
        premise_text += "&sys_1"
    # 交互对象
    if character_data.target_character_id == 0:
        premise_text += "&sys_4"
    else:
        premise_text += "&sys_5"
    # 写入新数据
    with open(save_path, "a", encoding='utf-8') as f:
        f.write(f"{new_cid},{behavior_id},0,{premise_text},{ai_generated_text}\n")


def judge_use_text_ai(character_id: int, behavior_id: int, original_text: str, translator: bool = False, direct_mode: bool = False) -> str:
    """
    判断是否使用文本生成AI
    参数:
        character_id: int 角色ID
        behavior_id: int 行为ID
        original_text: str 原始文本
        translator: bool 是否为翻译模式
        direct_mode: bool 是否为直接对话模式
    返回:
        fanal_text: str 最终文本
    """
    # 如果AI设置未开启，则直接返回原文本
    if 1 not in cache.ai_setting.ai_chat_setting or cache.ai_setting.ai_chat_setting[1] == 0:
        return original_text

    # 判断在调用哪个api
    now_key_type = get_key_type()
    # 如果没有输入模型名，则返回原文本
    if now_key_type == "":
        return original_text
    # 如果没有设置api密钥，则直接返回原文本
    if now_key_type not in cache.ai_setting.ai_chat_api_key:
        return original_text

    # 直接对话模式跳过安全检查
    if not direct_mode:
        # 判断是否设置了指令类型
        if cache.ai_setting.ai_chat_setting[2] == 0:
            safe_flag = False
            status_data = game_config.config_status[behavior_id]
            # 判断是否是安全标签
            for safe_tag in ["日常", "娱乐", "工作"]:
                if safe_tag in status_data.tag:
                    safe_flag = True
                    break
            if not safe_flag:
                return original_text

        # 判断是什么类型的地文
        if cache.ai_setting.ai_chat_setting[3] == 0 and not translator:
            if "地文" not in original_text:
                return original_text

    # 没有交互对象则返回
    if handle_premise.handle_have_no_target(0):
        return original_text
    # 自己和交互对象都不是玩家则返回
    if handle_premise.handle_no_player(character_id) and handle_premise.handle_target_no_player(character_id):
        return original_text

    # 输出文本生成提示
    if cache.ai_setting.ai_chat_setting[8] == 0:
        model = cache.ai_setting.ai_chat_setting[5]
        info_draw = draw.NormalDraw()
        info_text = _("\n（正在调用{0}）\n").format(model)
        info_draw.text = info_text
        info_draw.width = window_width
        info_draw.draw()

    # 获取ai返回文本
    ai_result = text_ai(character_id, behavior_id, original_text, translator=translator, direct_mode=direct_mode)
    print(f"ai_text_result = {ai_result}")
    
    # 处理直接对话模式的返回值
    if direct_mode:
        ai_gererate_text = ai_result["text"]
        settle_direct_instruct(ai_result)
    else:
        ai_gererate_text = ai_result

    # 检测是否显示原文本
    if cache.ai_setting.ai_chat_setting[4] == 1:
        fanal_text = ai_gererate_text
    else:
        fanal_text = "(原文本)" + original_text + "\n" + ai_gererate_text

    # 是否保存
    if cache.ai_setting.ai_chat_setting[7] == 1 and not translator:
        save_ai_talk_record(character_id, behavior_id, ai_gererate_text)

    return fanal_text


def build_user_prompt(character_id: int, behavior_id: int, original_text: str, translator: bool = False, direct_mode: bool = False) -> str:
    """
    构造用户提示词
    参数:
        character_id: int 角色ID
        behavior_id: int 行为ID
        original_text: str 原始文本
        translator: bool 是否为翻译模式
        direct_mode: bool 是否为直接对话模式
    返回:
        user_prompt: str 构造好的用户提示词
    功能描述:
        根据角色数据、行为数据及外部CSV（game_config.config_ai_chat_send_data）中预置的提示词模板生成用户提示词。
        只有当 cache.ai_setting.send_data_flags 中对应的 cid 为 True 时才会将该提示词加入到输出中。
        模板中的花括号{}内为变量，需要替换为对应的实际值。
    """

    # 翻译模式分支，沿用原有逻辑
    if translator:
        user_prompt = _('你需要将一段文本翻译为') + normal_config.config_normal.language + _('语言。如果文本中有有{ }括起来的字符，请原样保留。请原样保留文本中的换行符。以下是需要翻译的文本：')
        user_prompt += original_text
        return user_prompt

    # 获取角色和场景相关数据
    character_data = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    Name = character_data.name
    TargetName = target_character_data.name
    Location = character_data.position[-1]
    Season = game_time.get_month_text()
    time_str = game_time.get_day_and_time_text()
    Behavior_Name = game_config.config_status[behavior_id].name

    # 玩家与NPC的区分
    pl_name = Name
    npc_name = TargetName
    npc_character_id = character_data.target_character_id
    npc_character_data = target_character_data
    # 如果交互对象是玩家
    if character_data.target_character_id == 0:
        pl_name = TargetName
        npc_name = Name
        npc_character_id = character_id
        npc_character_data = character_data

    # 初始定义各数据是否处理
    tem_send_data_flags = create_tem_sned_data_flags(npc_character_id,)

    # 心情、年龄、种族、出身地、势力
    angry_text = attr_calculation.get_angry_text(npc_character_data.angry_point)
    age_text = attr_text.get_age_talent_text(npc_character_id)
    race_name = game_config.config_race[npc_character_data.race].name
    birthplace_name = game_config.config_birthplace[npc_character_data.relationship.birthplace].name
    nation_name = game_config.config_nation[npc_character_data.relationship.nation].name

    # 关系
    ave_text = 0
    if tem_send_data_flags[11]:
        favorability = npc_character_data.favorability[0]
        favorability_lv, tem = attr_calculation.get_favorability_level(favorability)
        trust = npc_character_data.trust
        trust_lv, tem = attr_calculation.get_trust_level(trust)
        ave_lv = int((favorability_lv + trust_lv) / 2)
        ave_text = str(ave_lv)

    # 陷落
    fall_prompt = ""
    if tem_send_data_flags[12]:
        fall_lv = attr_calculation.get_character_fall_level(character_data.target_character_id if character_id == 0 else character_id, minus_flag=True)
        if fall_lv > 0:
            fall_prompt = _(' 双方是正常的爱情关系。如果用数字等级来表示爱情的程度，1表示有些懵懂的好感，4表示至死不渝的爱人，那么{0}和{1}的关系大概是{2}。').format(npc_name, pl_name, str(fall_lv))
        elif fall_lv < 0:
            fall_prompt = _(' 双方是扭曲的服从和支配关系。如果用数字等级来表示服从的程度，1代表有些讨好，4代表无比尊敬，那么{0}对{1}的服从程度大概是{2}。').format(npc_name, pl_name, str(fall_lv))

    sleep_text, tired_text = "", ""
    # 睡眠
    if tem_send_data_flags[35]:
        tem,sleep_text = attr_calculation.get_sleep_level(npc_character_data.sleep_point)
    # 疲劳
    if tem_send_data_flags[33]:
        tired_lv = attr_calculation.get_tired_level(npc_character_data.tired_point)
        if tired_lv > 0:
            tired_text = constant.tired_text_list[tired_lv]
    # 工作
    work_name, work_description = "", ""
    if tem_send_data_flags[53]:
        work_type = npc_character_data.work.work_type
        work_data = game_config.config_work_type[work_type]
        work_name = work_data.name
        work_description = work_data.describe
    # 称呼
    nick_name, nick_name_to_pl = "", ""
    if handle_premise.handle_self_have_nick_name_to_self(npc_character_id):
        nick_name = npc_character_data.nick_name
    if handle_premise.handle_self_have_nick_name_to_pl(npc_character_id):
        nick_name_to_pl = npc_character_data.nick_name_to_pl
    # 催眠
    hypnosis_name, hypnosis_effect = "", ""
    if tem_send_data_flags[61]:
        hypnosis_id = npc_character_data.sp_flag.unconscious_h
        hypnosis_data = game_config.config_hypnosis_type[hypnosis_id]
        hypnosis_name = hypnosis_data.name
        hypnosis_effect = hypnosis_data.introduce

    # 服装
    cloth_text = ""
    if tem_send_data_flags[101]:
        for clothing_type in game_config.config_clothing_type:
            if len(npc_character_data.cloth.cloth_wear[clothing_type]):
                for cloth_id in npc_character_data.cloth.cloth_wear[clothing_type]:
                    cloth_data = game_config.config_clothing_tem[cloth_id]
                    cloth_name = cloth_data.name
                    cloth_text += _("{0}、").format(cloth_name)
        if len(cloth_text) > 0:
            cloth_text = cloth_text[:-1] + "。"
    # 全素质数据
    talent_text = ""
    if tem_send_data_flags[102]:
        for talent_id in game_config.config_talent:
            if npc_character_data.talent[talent_id]:
                talent_name = game_config.config_talent[talent_id].name
                talent_text += _("{0}、").format(talent_name)
        if len(talent_text) > 0:
            talent_text = talent_text[:-1] + "。"

    # 初始提示词构造（根据是否有交互对象以及直接对话模式分支）
    user_prompt = _('请根据以下条件，描写两个角色的互动场景：')
    # 有交互对象
    if character_id != 0 or character_data.target_character_id != 0:
        # 生成模式
        if not direct_mode:
            user_prompt += _(' 在当前的场景里，{0}是医药公司的领导人，被称为博士，{1}是一家医药公司的员工。').format(pl_name, npc_name)
            user_prompt += _(' {0}正在对{1}进行的动作是{2}。你要弄清楚是谁对谁做了什么，{0}是做这个动作的人，{1}是被做了这个动作的人。你需要仅描述这个动作的过程。').format(pl_name, npc_name, Behavior_Name)
        # 直接对话模式
        else:
            user_prompt += _(' 互动文本里的“我”都是指{0}，你都是指“{1}”。').format(pl_name, npc_name)
            user_prompt += _(' 互动的文本的全文是：{0}。互动文本到这里结束了。').format(original_text)
            user_prompt += _(' 你要将该互动的内容补充完善，并进一步续写对该互动的反应。')
    # 无交互对象的情况
    else:
        user_prompt += _(' 在当前的场景里，{0}是医药公司的领导人之一，被称为博士，正在进行的动作是{1}。').format(pl_name, Behavior_Name)

    # 遍历 CSV 数据（game_config.config_ai_chat_send_data）按标识决定是否加入提示词
    # 假定每项数据为字典，键包括 'cid' 和 'prompt'
    for cid in game_config.config_ai_chat_send_data:
        # 如果没有选择该数据，则跳过
        if tem_send_data_flags[cid] == False:
            continue
        ai_chat_send_data = game_config.config_ai_chat_send_data[cid]

        # 获取提示词
        prompt_template = ai_chat_send_data.prompt
        # 定义模板变量
        variables = {
            'name': npc_name,
            'pl_name': pl_name,
            'Season': Season,
            'time': time_str,
            'Location': Location,
            'ave_text': ave_text,
            'fall_prompt': fall_prompt,
            'tired_text': tired_text,
            'sleep_text': sleep_text,
            'angry_text': angry_text,
            'age_text': age_text,
            'race_name': race_name,
            'birthplace_name': birthplace_name,
            'nation_name': nation_name,
            'work_name': work_name,
            'work_description': work_description,
            'nick_name': nick_name,
            'nick_name_to_pl': nick_name_to_pl,
            'hypnosis_name': hypnosis_name,
            'hypnosis_effect': hypnosis_effect,
            'cloth_text': cloth_text,
            'talent_text': talent_text,
        }
        try:
            prompt_filled = prompt_template.format(**variables)
        except Exception:
            prompt_filled = prompt_template
        user_prompt += prompt_filled
    return user_prompt

def create_tem_sned_data_flags(npc_character_id: int) -> list:
    """
    创建临时发送数据标志列表
    参数:
        npc_character_id: int 角色ID
    返回:
        tem_send_data_flags: list -- 临时发送数据标志列表
    功能描述:
        根据角色ID和游戏配置中的预设数据，创建一个包含各个数据项是否需要处理的布尔值的列表。
        该列表用于在生成用户提示词时判断哪些数据需要被包含在内。
    """
    tem_send_data_flags = cache.ai_setting.send_data_flags.copy()
    for cid in game_config.config_ai_chat_send_data:
        ai_chat_send_data = game_config.config_ai_chat_send_data[cid]
        # 初始化不存在的数据选择状态
        if cid not in tem_send_data_flags:
            # 如果是默认选择的，设为True，否则设为False
            if ai_chat_send_data.default == 1:
                tem_send_data_flags[cid] = True
            else:
                tem_send_data_flags[cid] = False
        # 跳过已经是false的
        if tem_send_data_flags[cid] == False:
            continue
        # 饥饿
        if cid == 31:
            if handle_premise.handle_hunger_le_79(npc_character_id):
                tem_send_data_flags[cid] = False
        # 尿意
        elif cid == 32:
            if handle_premise.handle_urinate_le_79(npc_character_id):
                tem_send_data_flags[cid] = False
        # 疲劳
        elif cid == 33:
            if handle_premise.handle_tired_le_74(npc_character_id):
                tem_send_data_flags[cid] = False
        # 睡眠
        elif cid == 35:
            if not (handle_premise.handle_action_sleep(npc_character_id) or handle_premise.handle_unconscious_flag_1(npc_character_id)):
                tem_send_data_flags[cid] = False
        # 女儿
        elif cid == 45:
            if handle_premise.handle_self_not_player_daughter(npc_character_id):
                tem_send_data_flags[cid] = False
        # 助理
        elif cid == 51:
            if handle_premise.handle_not_assistant(npc_character_id):
                tem_send_data_flags[cid] = False
        # 跟随
        elif cid == 52:
            if handle_premise.handle_not_follow(npc_character_id):
                tem_send_data_flags[cid] = False
        # 工作
        elif cid == 53:
            if not handle_premise.handle_have_work(npc_character_id):
                tem_send_data_flags[cid] = False
        # 访客
        elif cid == 54:
            if not handle_premise.handle_self_visitor_flag_1(npc_character_id):
                tem_send_data_flags[cid] = False
        # 催眠
        elif cid == 61:
            if not handle_premise.handle_unconscious_hypnosis_flag(npc_character_id):
                tem_send_data_flags[cid] = False
        # 监禁
        elif cid == 62:
            if handle_premise.handle_imprisonment_0(npc_character_id):
                tem_send_data_flags[cid] = False
        # 时停
        elif cid == 63:
            if handle_premise.handle_time_stop_off(npc_character_id):
                tem_send_data_flags[cid] = False

    return tem_send_data_flags

def text_ai(character_id: int, behavior_id: int, original_text: str, translator: bool = False, direct_mode: bool = False) -> dict:
    """
    文本生成AI\n\n
    Keyword arguments:
    character_id: int 角色id\n
    behavior_id: int 行为id\n
    original_text: str 原始文本\n
    translator -- 翻译模式\n
    direct_mode -- 直接对话模式\n
    Return arguments:
    直接对话模式: dict -- {"time": int, "tired": int, "relationship": int, "text": str}
    非直接对话模式: str -- AI生成的文本\n
    """

    # 基础数据
    talk_num = cache.ai_setting.ai_chat_setting[9] + 1

    # 模型与密钥
    model = cache.ai_setting.ai_chat_setting[5]
    now_key_type = get_key_type()
    API_KEY = cache.ai_setting.ai_chat_api_key[now_key_type]

    # 系统提示词
    system_promote = ''
    for system_promote_cid in game_config.ui_text_data['text_ai_system_promote']:
        system_promote_text = game_config.ui_text_data['text_ai_system_promote'][system_promote_cid]
        # 对生成数量的替换处理
        if "{talk_num}" in system_promote_text:
            system_promote_text = system_promote_text.replace("{talk_num}", str(talk_num))
        system_promote += _(system_promote_text)
    # print(system_promote)
    # 用户提示词
    user_prompt = build_user_prompt(character_id, behavior_id, original_text, translator, direct_mode)
    # print(f'user_prompt = {user_prompt}')

    # 直接对话模式
    if direct_mode:
        system_promote += _("你要根据以下格式返回文本，并且不需要任何其他的解释：\n")
        system_promote += _("第一行：time:int，用于表示互动行为持续的时间，单位为分钟，如 time:5 代表互动持续了5分钟\n")
        system_promote += _("第二行：tired:int，用于表示本次行为对体力的消耗程度，分为三个等级：\n")
        system_promote += _("  1 - 接近静止状态下的很少消耗，如坐着看书\n")
        system_promote += _("  2 - 正常消耗，如肢体动作、进行非体力劳动的工作\n")
        system_promote += _("  3 - 非常严重的消耗，如高强度健身、搬运重物\n")
        system_promote += _("第三行：relationship:int，用于表示本次行为对关系的影响程度，分为四个等级：\n")
        system_promote += _("  1 - 关系变差，如吵架、争执等负面行为\n")
        system_promote += _("  2 - 关系不变，如没有营养的对话、无聊的行为等\n")
        system_promote += _("  3 - 关系稍微变好，如共同工作、共同娱乐、轻度肢体交流等行为\n")
        system_promote += _("  4 - 关系快速变好，如约会、亲密行为等正面行为\n")
        system_promote += _("第四行及以后：text:str，用于返回你生成的场景描述文本，只在该行出现一次text:。\n")

    # 开始调用AI

    # 调用OpenAI
    if now_key_type == "OPENAI_API_KEY" or now_key_type == "DEEPSEEK_API_KEY":
        # 创建client
        client = openai.OpenAI(api_key=API_KEY)
        # deepseek则调整base_url
        if now_key_type == "DEEPSEEK_API_KEY":
            client = client.with_options(base_url="https://api.deepseek.com")
        # 自定义base_url
        if cache.ai_setting.ai_chat_setting[10] == 1:
            client = client.with_options(base_url=cache.ai_setting.now_ai_chat_base_url)
        # 自定义代理
        if cache.ai_setting.ai_chat_setting[11] == 1:
            if len(cache.ai_setting.now_ai_chat_proxy[1]) == 0:
                client = client.with_options(http_client=openai.DefaultHttpxClient(proxies=cache.ai_setting.now_ai_chat_proxy[0]))
            else:
                client = client.with_options(http_client=openai.DefaultHttpxClient(proxies=cache.ai_setting.now_ai_chat_proxy[0], transport=httpx.HTTPTransport(local_address=cache.ai_setting.now_ai_chat_proxy[1])))
        try:
            # 发送请求
            # 流式输出
            if cache.ai_setting.ai_chat_setting[14] == 1:
                completion = client.chat.completions.create(
                    model=cache.ai_setting.ai_chat_setting[5],
                    messages=[
                        {"role": "system", "content": system_promote},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True
                )
                # 调用流式处理函数获取返回的文本
                ai_gererate_text = process_stream_response(
                    stream=completion,         # 流式返回数据的迭代器，类型为object
                    direct_mode=direct_mode,   # 是否为直接对话模式，类型为bool
                    extractor=lambda chunk: chunk.choices[0].delta.content  # 提取chunk中的文本，返回值为str
                )
           # 非流式输出
            else:
                completion = client.chat.completions.create(
                    model=cache.ai_setting.ai_chat_setting[5],
                    messages=[
                        {"role": "system", "content": system_promote},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                # 获取返回的文本
                ai_gererate_text = completion.choices[0].message.content
        except Exception as e:
            # 如果发生异常，将返回的文本设为空
            ai_gererate_text = ""
    # 调用Gemini
    elif now_key_type == "GEMINI_API_KEY":
        # 创建client
        genai.configure(api_key=API_KEY)
        # gemini的传输协议改为rest
        if cache.ai_setting.ai_chat_setting[12] == 1:
            genai.configure(api_key=API_KEY, transport='rest')
        client = genai.GenerativeModel(model, system_instruction = system_promote)
        try:
            # 发送请求
            # 流式输出
            if cache.ai_setting.ai_chat_setting[14] == 1:
                completion = client.generate_content(user_prompt, stream=True)
                # 调用流式处理函数获取返回的文本
                ai_gererate_text = process_stream_response(
                    stream=completion,         # 流式返回数据的迭代器，类型为object
                    direct_mode=direct_mode,   # 是否为直接对话模式，类型为bool
                    extractor=lambda chunk: chunk.text  # 提取chunk中的文本，返回值为str
                )
            # 非流式输出
            else:
                completion = client.generate_content(user_prompt)
                # 获取返回的文本
                ai_gererate_text = completion.text
        except Exception as e:
            # 如果发生异常，将返回的文本设为空
            ai_gererate_text = ""

    # 如果没有返回文本，则返回原文本
    if ai_gererate_text == None or not len(ai_gererate_text):
        ai_gererate_text = _("(生成失败，使用原文本)") + original_text

    # 处理直接对话模式下的返回格式
    if direct_mode:
        # 解析AI返回的格式化文本
        lines = ai_gererate_text.split('\n')
        result = {
            "time": 5,  # 默认值
            "tired": 2,  # 默认值
            "relationship": 2,  # 默认值
            "text": ""  # 默认值
        }
        
        text_content = []
        for line in lines:
            if line.startswith("time:"):
                try:
                    result["time"] = int(line.replace("time:", "").strip())
                except ValueError:
                    pass
            elif line.startswith("tired:"):
                try:
                    result["tired"] = int(line.replace("tired:", "").strip())
                except ValueError:
                    pass
            elif line.startswith("relationship:"):
                try:
                    result["relationship"] = int(line.replace("relationship:", "").strip())
                except ValueError:
                    pass
            elif line.startswith("text:"):
                text_content.append(line.replace("text:", "", 1))
            else:
                text_content.append(line)
        
        # 合并所有文本内容
        result["text"] = "\n".join(text_content)
        
        # 在不影响\\n的情况下，将\n删去
        result["text"] = result["text"].replace("\n", "")
        # 删除思考过程
        if cache.ai_setting.ai_chat_setting[13] == 1:
            # 使用正则删除<think>到</think>之间的内容
            result["text"] = re.sub(r'<think>.*?</think>', '', result["text"])
        
        return result
    else:
        # 在不影响\\n的情况下，将\n删去
        ai_gererate_text = ai_gererate_text.replace("\n", "")
        # 非翻译模式下删去空格
        if not translator:
            ai_gererate_text = ai_gererate_text.replace(" ", "")
        # 删除思考过程
        if cache.ai_setting.ai_chat_setting[13] == 1:
            # 使用正则删除<think>到</think>之间的内容
            ai_gererate_text = re.sub(r'<think>.*?</think>', '', ai_gererate_text)
            
        return ai_gererate_text


def process_stream_response(stream: object, direct_mode: bool, extractor: object) -> str:
    """
    处理流式输出的返回数据，并绘制返回结果
    参数:
        stream: object - 流式返回数据的迭代器，每个元素代表部分返回内容
        direct_mode: bool - 是否为直接对话模式，直接对话模式下需要等待"text:"标记再开始输出
        extractor: function - 一个函数，输入chunk对象，返回对应的文本字符串
    返回:
        str - 拼接后的完整返回文本
    """

    ai_generate_text: str = ""
    now_draw = draw.NormalDraw()
    # 非直接对话模式时默认直接开始输出文本
    text_started: bool = not direct_mode

    for chunk in stream:
        # 提取当前chunk中的文本
        chunk_text: str = extractor(chunk)
        if not chunk_text:
            continue

        # 如果chunk仅为单独换行，则绘制换行并跳过当前循环
        if chunk_text.strip() == "\n":
            line_feed = draw.LineFeedWaitDraw()
            line_feed.text = " \n"
            line_feed.draw()
            continue

        # 在直接对话模式下，等待遇到"text:"标记后再开始绘制和存储
        if direct_mode:
            # 直接对话模式下等待遇到"text:"标记后再开始绘制和存储
            if "text:" in chunk_text and not text_started:
                text_started = True
                parts = chunk_text.split("text:", 1)
                if len(parts) > 1:
                    display_text = parts[1]
                    # 替换掉换行符
                    display_text = display_text.replace("\\n", "\n")
                    now_draw.text = display_text
                    now_draw.width = 1
                    now_draw.draw()
                    ai_generate_text += display_text
            # 如果已经开始text部分，直接显示文本
            elif text_started:
                # 替换掉换行符
                chunk_text = chunk_text.replace("\\n", "\n")
                # 替换掉text:
                now_draw.text = chunk_text.replace("text:", "")
                now_draw.width = 1
                now_draw.draw()
                ai_generate_text += chunk_text
            # 如果未开始text部分，只存储不显示
            else:
                ai_generate_text += chunk_text
        # 非直接对话模式下直接显示文本
        else:
            now_draw.text = chunk_text
            now_draw.width = 1
            now_draw.draw()
            ai_generate_text += chunk_text

    # 绘制一个空白的等待
    wait_draw = draw.LineFeedWaitDraw()
    wait_draw.text = " \n"
    wait_draw.draw()

    return ai_generate_text


def direct_chat_with_ai() -> str:
    """
    与AI进行直接对话\n
    用户输入动作文本，AI生成回复\n
    Return arguments:
    reply_text -- AI回复文本
    """
    # 提示信息
    ask_text = _("\n请描述你想要进行的动作(输入空白文本退出)：\n")

    # 获取玩家输入
    ask_panel = panel.AskForOneMessage()
    ask_panel.set(ask_text, 999)
    user_input = ask_panel.draw()
    line_feed.draw()
    
    # 如果输入为空，则退出
    if not user_input:
        return ""
        
    # 获取当前玩家角色ID和目标角色ID
    character_id = 0  # 假设0是玩家角色
    behavior_id = 0   # 默认行为ID，可以根据实际情况调整
    
    # 调用判断函数，启用直接对话模式
    reply_text = judge_use_text_ai(character_id, behavior_id, user_input, direct_mode=True)
    
    # 非流式传输下再绘制回复
    if cache.ai_setting.ai_chat_setting[14] != 1:
        # 处理换行符
        reply_text = reply_text.replace("\\n", "\n")
        # 替换掉text:
        reply_text = reply_text.replace("text:", "")
        # 绘制AI回复
        reply_draw = draw.NormalDraw()
        reply_draw.text = _("\nAI回复：\n") + reply_text + _("\n")
        reply_draw.width = window_width
        reply_draw.draw()

    return reply_text

def settle_direct_instruct(ai_result: dict) -> None:
    """
    处理直接对话模式下的AI返回结果\n
    参数:
        ai_result: dict -- AI返回的结果，包含时间、体力消耗、关系变化等信息
    返回:
        None
    """
    from Script.Design.handle_instruct import chara_handle_instruct_common_settle
    tem_state_id = constant.CharacterStatus.STATUS_AI_CHAT_INSTRUCT
    # 指令持续时间
    new_duration = ai_result["time"]
    # 构建该临时指令的结算
    game_config.config_behavior_effect_data[tem_state_id] = set()
    # 体力气力消耗
    game_config.config_behavior_effect_data[tem_state_id].add(10 + ai_result["tired"])
    game_config.config_behavior_effect_data[tem_state_id].add(11 + ai_result["tired"])
    # 关系变化
    if ai_result["relationship"] == 1:
        game_config.config_behavior_effect_data[tem_state_id].add(23)
    elif ai_result["relationship"] == 3:
        game_config.config_behavior_effect_data[tem_state_id].add(21)
    elif ai_result["relationship"] == 4:
        game_config.config_behavior_effect_data[tem_state_id].add(21)
        game_config.config_behavior_effect_data[tem_state_id].add(22)
    # 执行结算
    chara_handle_instruct_common_settle(tem_state_id, duration=new_duration)
