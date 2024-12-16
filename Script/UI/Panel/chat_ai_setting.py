from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
from Script.Design import attr_text, attr_calculation
import openai
import google.generativeai as genai
import concurrent.futures
import os
import csv
import httpx

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


def judge_use_text_ai(character_id: int, behavior_id: int, original_text: str, translator: bool = False) -> str:
    """
    判断是否使用文本生成AI\n
    Keyword arguments:\n
    character_id -- 角色id\n
    behavior_id -- 行为id\n
    original_text -- 原始文本\n
    translator -- 翻译模式\n
    Return arguments:
    fanal_text -- 最终文本
    """
    # 如果AI设置未开启，则直接返回原文本
    if 1 not in cache.ai_setting.ai_chat_setting or cache.ai_setting.ai_chat_setting[1] == 0:
        return original_text
    # 如果api密钥未设置，则直接返回原文本

    # 判断在调用哪个api
    model = cache.ai_setting.ai_chat_setting[5]
    # 如果没有输入模型名，则返回原文本
    if not model:
        return original_text
    if 'gpt' in model:
        now_key_type = 'OPENAI_API_KEY'
    elif 'gemini' in model:
        now_key_type = 'GEMINI_API_KEY'
    else:
        now_key_type = 'OPENAI_API_KEY'
    if now_key_type not in cache.ai_setting.ai_chat_api_key:
        return original_text
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

    # 输出文本生成提示
    if cache.ai_setting.ai_chat_setting[8] == 0:
        model = cache.ai_setting.ai_chat_setting[5]
        info_draw = draw.NormalDraw()
        info_text = _("\n（正在调用{0}）\n").format(model)
        info_draw.text = info_text
        info_draw.width = window_width
        info_draw.draw()

    ai_gererate_text = text_ai(character_id, behavior_id, original_text, translator=translator)
    # 检测是否显示原文本
    if cache.ai_setting.ai_chat_setting[4] == 1:
        fanal_text = ai_gererate_text
    else:
        fanal_text = original_text + "*\n" + ai_gererate_text

    # 是否保存
    if cache.ai_setting.ai_chat_setting[7] == 1 and not translator:
        save_path = "data/talk/ai/ai_talk.csv"
        # 检测是否存在文件，如果不存在的话，创建文件
        # 检查文件是否存在
        if not os.path.exists(save_path):
            # 如果文件不存在，创建文件夹和文件
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

        # 保存数据
        with open(save_path, "a", encoding='utf-8') as f:
            f.write(f"{new_cid},{behavior_id},0,generate_by_ai,{ai_gererate_text}\n")

    return fanal_text

def text_ai(character_id: int, behavior_id: int, original_text: str, translator: bool = False) -> str:
    """
    文本生成AI\n\n
    Keyword arguments:
    character_id: int 角色id\n
    behavior_id: int 行为id\n
    original_text: str 原始文本\n
    translator -- 翻译模式\n
    """
    from Script.Design import handle_premise

    # 基础数据
    character_data = cache.character_data[character_id]
    target_character_data = cache.character_data[character_data.target_character_id]
    Name = character_data.name
    TargetNickName = target_character_data.name
    Location = attr_text.get_scene_path_text(character_data.position)
    talk_num = cache.ai_setting.ai_chat_setting[9] + 1
    Behavior_Name = game_config.config_status[behavior_id].name

    # 模型与密钥
    model = cache.ai_setting.ai_chat_setting[5]
    if 'gpt' in model:
        now_key_type = 'OPENAI_API_KEY'
    elif 'gemini' in model:
        now_key_type = 'GEMINI_API_KEY'
    else:
        now_key_type = 'OPENAI_API_KEY'
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
    # 生成模式
    if not translator:
        user_prompt = _('请根据以下条件，描写两个角色的互动场景：')
        # 地点
        user_prompt += _("场景发生的地点是{0}。").format(Location)
        # 有交互对象时
        if character_id != 0 or character_data.target_character_id != 0:
            if character_id == 0:
                pl_name = Name
                npc_name = TargetNickName
                npc_character_id = character_data.target_character_id
                npc_character_data = target_character_data
            elif character_data.target_character_id == 0:
                pl_name = TargetNickName
                npc_name = Name
                npc_character_id = character_id
                npc_character_data = character_data
            else:
                return original_text
            # 名字
            user_prompt += _("在当前的场景里，{0}是医药公司的领导人，被称为博士，{1}是一家医药公司的员工。").format(pl_name, npc_name)
            # 动作
            user_prompt += _("{0}正在对{1}进行的动作是{2}。").format(Name, TargetNickName, Behavior_Name)
            # 关系
            favorability = npc_character_data.favorability[0]
            favorability_lv, tem = attr_calculation.get_favorability_level(favorability)
            trust = npc_character_data.trust
            trust_lv, tem = attr_calculation.get_trust_level(trust)
            ave_lv = int((favorability_lv + trust_lv) / 2)
            user_prompt += _("如果用数字等级来表示关系好坏，0是第一次见面的陌生人，8是托付人生的亲密伴侣，那{0}和{1}的关系大概是{2}。").format(Name, TargetNickName, ave_lv)
            # 陷落
            fall_lv = attr_calculation.get_character_fall_level(npc_character_id, minus_flag = True)
            if fall_lv > 0:
                user_prompt += _("{0}和{1}是正常的爱情关系。如果用数字等级来表示爱情的程度，1是有些懵懂的好感，4是至死不渝的爱人，那{0}和{1}的关系大概是{4}。").format(Name, TargetNickName, Name, TargetNickName, fall_lv)
            elif fall_lv < 0:
                user_prompt += _("{0}和{1}是扭曲的服从和支配的关系。如果用数字等级来表示服从的程度，1是有些讨好和有些卑微，4是无比的尊敬和彻底的服从，那{2}对{3}的服从的等级大概是{4}。").format(Name, TargetNickName, npc_name, pl_name, fall_lv)

            # 基础状态
            # 年龄素质
            age_text = attr_text.get_age_talent_text(npc_character_id)
            user_prompt += _("{0}的年龄是{1}。").format(npc_name, age_text)
            # 睡眠、疲劳、困倦
            if handle_premise.handle_action_sleep(npc_character_id) or handle_premise.handle_unconscious_flag_1(npc_character_id):
                tem,sleep_name = attr_calculation.get_sleep_level(npc_character_data.sleep_point)
                user_prompt += _("{0}正在睡觉，睡眠的深度是{1}。").format(npc_name, sleep_name)
            else:
                # 疲劳与困倦
                sleep_lv = attr_calculation.get_tired_level(npc_character_data.tired_point)
                if sleep_lv > 0:
                    sleep_text = constant.sleep_text_list[sleep_lv]
                    user_prompt += _("{0}有些困了，困的程度为{1}。").format(npc_name, sleep_text)
            # 心情
            angry_text = attr_calculation.get_angry_text(npc_character_data.angry_point)
            if angry_text != "普通":
                user_prompt += _("{0}的心情状态是{1}。").format(npc_name, angry_text)
            # 跟随
            if handle_premise.handle_is_follow_1(npc_character_id):
                user_prompt += _("{0}正在跟随{1}一起行动。").format(npc_name, pl_name)
            # 尿意
            if handle_premise.handle_urinate_ge_80(npc_character_id):
                user_prompt += _("{0}有点想上厕所尿尿。").format(npc_name)
            # 饥饿
            if handle_premise.handle_hunger_ge_80(npc_character_id):
                user_prompt += _("{0}有点饿了，想吃东西。").format(npc_name)
            # 催眠
            if handle_premise.handle_unconscious_hypnosis_flag(npc_character_id):
                user_prompt += _("{0}被{1}催眠了。").format(npc_name, pl_name)
            # 监禁
            if handle_premise.handle_imprisonment_1(npc_character_id):
                user_prompt += _("{0}被{1}监禁在监狱里了。").format(npc_name, pl_name)
            # 访客
            if npc_character_data.sp_flag.vistor == 1:
                user_prompt += _("{0}不是公司的员工，是前来拜访的访客。").format(npc_name)
            # 时停
            if handle_premise.handle_unconscious_flag_3(npc_character_id):
                user_prompt += _("{0}正处在停止的时间中，无法做出任何反应。").format(npc_name)
            # 中量数据才有的分支
            if cache.ai_setting.ai_chat_setting[6] >= 1:
                # 职业
                profession_name = game_config.config_profession[npc_character_data.profession].name
                user_prompt += _("{0}的职业是{1}。").format(npc_name, profession_name)
                # 种族
                race_name = game_config.config_race[npc_character_data.race].name
                user_prompt += _("{0}是一种虚构的奇幻种族，种族名是{1}。").format(npc_name, race_name)
                # 出身地
                birthplace_name = game_config.config_birthplace[npc_character_data.relationship.birthplace].name
                user_prompt += _("{0}的出生地是{1}。").format(npc_name, birthplace_name)
                # 势力
                nation_name = game_config.config_nation[npc_character_data.relationship.nation].name
                user_prompt += _("{0}所属的具体势力是{1}。").format(npc_name, nation_name)
                # 全素质数据
                user_prompt += _("{0}有以下素质特性：").format(npc_name)
                for talent_id in game_config.config_talent:
                    if npc_character_data.talent[talent_id]:
                        talent_name = game_config.config_talent[talent_id].name
                        user_prompt += _("{0}、").format(talent_name)
                user_prompt = user_prompt[:-1] + "。"
            # 大量数据才有的分支
            if cache.ai_setting.ai_chat_setting[6] >= 2:
                # 服装
                user_prompt += _("{0}穿着的衣服有：").format(npc_name)
                for clothing_type in game_config.config_clothing_type:
                    if len(npc_character_data.cloth.cloth_wear[clothing_type]):
                        for cloth_id in npc_character_data.cloth.cloth_wear[clothing_type]:
                            cloth_name = game_config.config_clothing_tem[cloth_id].name
                            user_prompt += _("{0}、").format(cloth_name)
                user_prompt = user_prompt[:-1] + "。"
                # 工作
                if handle_premise.handle_have_work(npc_character_id):
                    work_name = game_config.config_work_type[npc_character_data.work.work_type].name
                    user_prompt += _("{0}的工作是{1}。").format(npc_name, work_name)
                # 称呼
                if handle_premise.handle_self_have_nick_name_to_pl(npc_character_id):
                    nick_name = npc_character_data.nick_name_to_pl
                    user_prompt += _("{0}称呼{1}为{2}。").format(npc_name, pl_name, nick_name)
                if handle_premise.handle_self_have_nick_name_to_self(npc_character_id):
                    nick_name = npc_character_data.nick_name
                    user_prompt += _("{0}称呼{1}为{2}。").format(pl_name, npc_name, nick_name)

        else:
            user_prompt += _("在当前的场景里，{0}是医药公司的领导人之一，被称为博士。").format(Name)
            user_prompt += _("{0}正在进行的动作是{1}。").format(Name, Behavior_Name)
    # 翻译模式
    else:
        user_prompt = _('你需要将一段文本翻译为')
        user_prompt += normal_config.config_normal.language
        user_prompt += _('语言。如果文本中有有\{\}括起来的字符，请原样保留。请原样保留文本中的换行符。以下是需要翻译的文本：')
        user_prompt += original_text
    # 开始调用AI

    # 调用OpenAI
    if now_key_type == "OPENAI_API_KEY":
        # 创建client
        client = openai.OpenAI(api_key=API_KEY)
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
            completion = client.generate_content(user_prompt)
            # 获取返回的文本
            ai_gererate_text = completion.text
        except Exception as e:
            # 如果发生异常，将返回的文本设为空
            ai_gererate_text = ""

    # 如果没有返回文本，则返回原文本
    if ai_gererate_text == None or not len(ai_gererate_text):
        ai_gererate_text = original_text

    # 在不影响\\n的情况下，将\n删去
    ai_gererate_text = ai_gererate_text.replace("\n", "")
    # 非翻译模式下删去空格
    if not translator:
        ai_gererate_text = ai_gererate_text.replace(" ", "")
    # print(ai_gererate_text)

    return ai_gererate_text


class Chat_Ai_Setting_Panel:
    """
    用于文本生成AI设置的面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        # self.now_panel = _("文本生成AI设置")
        # """ 当前绘制的页面 """
        self.draw_list: List[draw.NormalDraw] = []
        """ 绘制的文本列表 """
        self.pl_character_data = cache.character_data[0]
        """ 玩家的属性 """
        self.test_flag = 0
        """ 测试标志，0为未测试，1为测试通过，2为测试不通过 """
        self.error_message = ""
        """ 错误信息 """

    def draw(self):
        """绘制对象"""

        title_text = _("文本生成AI设置")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        if 1 not in cache.ai_setting.ai_chat_setting or cache.ai_setting.ai_chat_setting[1] == 0:
            while 1:
                return_list = []
                title_draw.draw()

                # 输出提示信息
                now_draw = draw.NormalDraw()
                info_text = _(" \n ○文本生成AI是一个试验性的功能，存在相当多的风险，所以需要您确认以下所有免责事项才可以使用\n\n\n 1.该功能需要您自行准备好OpenAI/Gemini的API密钥，并保证电脑的网络环境可以正常访问该API，本游戏不会为您提供相关的获取方法，请自行准备\n\n\n   2.文本生成AI以及网络环境的使用会产生一定的费用，该费用需自己承担，与开发者没有任何关系\n\n\n 3.文本生成AI的使用可能会产生一定的风险，包括但不限于：聊天内容不当、聊天内容不符合社会规范等，开发者不对生成的内容负责，也不代表开发者同意或反对其中的任何观点\n\n\n 4.不恰当的使用过程或生成内容有可能会导致模型提供商对您的api和相关账号提出警告或进一步的停止服务等举措，请牢记该风险，相关的直接或间接损失均需您自己承担，与开发者无关\n\n\n 5.本声明的解释权归开发者所有，且在版本更新中声明内容可能有所变更，请以最新版本为准。\n\n\n 6.基于以上又叠了这么多层buff，明确知道自己在做什么，并且愿意承担费用和风险的人再来点击下一步吧\n\n\n")
                now_draw.text = info_text
                now_draw.width = self.width
                now_draw.draw()

                no_draw = draw.LeftButton(_("[0]我不太确定，再考虑一下"), _("返回"), self.width)
                no_draw.draw()
                return_list.append(no_draw.return_text)
                line_feed.draw()
                line_feed.draw()

                yes_draw = draw.LeftButton(_("[1]我已阅读并同意以上所有免责事项，理解并愿意承担对应的费用和风险"), _("下一步"), self.width)
                yes_draw.draw()
                return_list.append(yes_draw.return_text)
                line_feed.draw()

                yrn = flow_handle.askfor_all(return_list)
                if yrn == no_draw.return_text:
                    cache.now_panel_id = constant.Panel.IN_SCENE
                    return
                elif yrn == yes_draw.return_text:
                    break

        while 1:
            return_list = []
            line_feed.draw()
            title_draw.draw()

            # 输出提示信息
            now_draw = draw.NormalDraw()
            info_text = _(" \n ○点击[选项标题]显示[选项介绍]，点击[选项本身]即可[改变该选项]\n")
            info_text += _("   开启本功能后，受网络连接速度和模型的文本生成速度影响，在生成文本时会有明显的延迟\n")
            info_text += _('   系统提示词文件路径为 data/ui_text/text_ai_system_promote.csv ，可以根据自己的需要进行调整，调整后需重启游戏\n')
            info_text += _('   包含调用、输送数据在内的完整代码，见游戏源码文件路径 Script/UI/Panel/chat_ai_setting.py ，可以根据自己的需要进行调整，调整后需自行打包\n')
            now_draw.text = info_text
            now_draw.width = self.width
            now_draw.draw()

            # 遍历全部设置
            for cid in game_config.config_ai_chat_setting:
                # 如果当前不是第1个设置，且第1个设置没有开启，则不显示后面的设置
                if cid != 1 and (1 not in cache.ai_setting.ai_chat_setting or cache.ai_setting.ai_chat_setting[1] == 0):
                    break
                line_feed.draw()
                ai_chat_setting_data = game_config.config_ai_chat_setting[cid]
                # 选项名
                button_text = f"  [{ai_chat_setting_data.name}]： "
                button_len = max(len(button_text) * 2, 60)
                button_draw = draw.LeftButton(button_text, button_text, button_len, cmd_func=self.draw_info, args=(cid))
                button_draw.draw()
                return_list.append(button_draw.return_text)

                # 如果没有该键，则创建一个，并置为0
                if cid not in cache.ai_setting.ai_chat_setting:
                    cache.ai_setting.ai_chat_setting[cid] = 0
                now_setting_flag = cache.ai_setting.ai_chat_setting[cid] # 当前设置的值
                option_len = len(game_config.config_ai_chat_setting_option[cid]) # 选项的长度

                # 当前选择的选项的名字
                # 自定义模型的名字
                if cid == 5:
                    button_text = f" [{cache.ai_setting.ai_chat_setting[cid]}] "
                elif cid == 10 and cache.ai_setting.ai_chat_setting[cid] == 1:
                    button_text = f" [{game_config.config_ai_chat_setting_option[cid][now_setting_flag]}] " + cache.ai_setting.now_ai_chat_base_url
                elif cid == 11 and cache.ai_setting.ai_chat_setting[cid] == 1:
                    button_text = f" [{game_config.config_ai_chat_setting_option[cid][now_setting_flag]}] " + "ip：" + cache.ai_setting.now_ai_chat_proxy[0]
                    if len(cache.ai_setting.now_ai_chat_proxy[1]) > 0:
                        button_text += " port：" + cache.ai_setting.now_ai_chat_proxy[1]
                else:
                    button_text = f" [{game_config.config_ai_chat_setting_option[cid][now_setting_flag]}] "
                button_len = max(len(button_text) * 2, 20)

                # 绘制选项
                button_draw = draw.LeftButton(button_text, str(cid) + button_text, button_len, cmd_func=self.change_setting, args=(cid, option_len))
                button_draw.draw()
                return_list.append(button_draw.return_text)

            # 非中文语言下，显示翻译选项
            if normal_config.config_normal.language != "zh_CN":
                line_feed.draw()
                # 选项名
                button_text = _("  [语言翻译]： ")
                button_len = max(len(button_text) * 2, 60)
                button_draw = draw.LeftButton(button_text, button_text, button_len, cmd_func=self.draw_info, args=(31))
                button_draw.draw()
                return_list.append(button_draw.return_text)
                # 绘制选项
                if cache.ai_setting.ai_chat_translator_setting == 0:
                    button_text = _(" [未开启] ")
                elif cache.ai_setting.ai_chat_translator_setting == 1:
                    button_text = _(" [仅翻译地文] ")
                elif cache.ai_setting.ai_chat_translator_setting == 2:
                    button_text = _(" [翻译地文和口上] ")
                button_draw = draw.LeftButton(button_text, str(cid) + button_text, button_len, cmd_func=self.change_translator)
                button_draw.draw()
                return_list.append(button_draw.return_text)

            # api密钥
            if cache.ai_setting.ai_chat_setting[1] == 1:
                line_feed.draw()
                line_feed.draw()

                # 查看当前目录下是否有api密钥文件
                try:
                    with open("ai_chat_api_key.csv", "r", encoding='utf-8') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if row[0] == "OPENAI_API_KEY":
                                api_key = row[1]
                                cache.ai_setting.ai_chat_api_key["OPENAI_API_KEY"] = api_key
                            elif row[0] == "GEMINI_API_KEY":
                                api_key = row[1]
                                cache.ai_setting.ai_chat_api_key["GEMINI_API_KEY"] = api_key
                except FileNotFoundError:
                    pass
                # 显示当前api的密钥
                OPENAI_API_KEY = cache.ai_setting.ai_chat_api_key.get("OPENAI_API_KEY", "")
                if OPENAI_API_KEY == "":
                    OPENAI_API_KEY = _("未设置")
                else:
                    OPENAI_API_KEY = _("已设置")
                key_info_text = _("  OpenAI API密钥： {0}\n").format(OPENAI_API_KEY)
                GEMINI_API_KEY = cache.ai_setting.ai_chat_api_key.get("GEMINI_API_KEY", "")
                if GEMINI_API_KEY == "":
                    GEMINI_API_KEY = _("未设置")
                else:
                    GEMINI_API_KEY = _("已设置")
                key_info_text += _("  Gemini API密钥： {0}\n").format(GEMINI_API_KEY)
                key_info_draw = draw.NormalDraw()
                key_info_draw.text = key_info_text
                key_info_draw.width = self.width
                key_info_draw.draw()

                # 更改api密钥
                button_text = _("  [更改OpenAI API密钥] ")
                button_len = max(len(button_text) * 2, 20)
                button_draw = draw.CenterButton(button_text, _("更改OpenAI API密钥"), button_len, cmd_func=self.change_api_key, args=("OPENAI_API_KEY"))
                button_draw.draw()
                return_list.append(button_draw.return_text)
                button_text = _("  [更改Gemini API密钥] ")
                button_len = max(len(button_text) * 2, 20)
                button_draw = draw.CenterButton(button_text, _("更改Gemini API密钥"), button_len, cmd_func=self.change_api_key, args=("GEMINI_API_KEY"))
                button_draw.draw()
                return_list.append(button_draw.return_text)

            # 测试按钮
            if cache.ai_setting.ai_chat_setting[1] == 1:
                line_feed.draw()
                line_feed.draw()
                button_text = _("  [测试] ")
                button_len = max(len(button_text) * 2, 20)
                button_draw = draw.CenterButton(button_text, _("测试"), button_len, cmd_func=self.test_ai)
                button_draw.draw()
                return_list.append(button_draw.return_text)
                if self.test_flag == 0:
                    pass
                elif self.test_flag == 1:
                    info_text = _(" \n  测试通过，当前调用的模型为：") + cache.ai_setting.ai_chat_setting[5] + "\n"
                    info_draw = draw.NormalDraw()
                    info_draw.text = info_text
                    info_draw.width = self.width
                    info_draw.draw()
                elif self.test_flag == 2:
                    info_text = _(" \n  测试不通过，错误信息为：\n  ") + self.error_message + "\n"
                    info_draw = draw.NormalDraw()
                    info_draw.text = info_text
                    info_draw.width = self.width
                    info_draw.draw()

            line_feed.draw()
            line_feed.draw()
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width)
            back_draw.draw()
            line_feed.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def draw_info(self, cid):
        """绘制选项介绍信息"""
        line = draw.LineDraw("-", self.width)
        line.draw()
        now_draw = draw.WaitDraw()
        # 常规选项
        if cid <= 30:
            ai_chat_setting_data = game_config.config_ai_chat_setting[cid]
            info_text = f"\n {ai_chat_setting_data.info}\n"
        elif cid == 31:
            info_text = _(" \n  本选项用于设置是否开启语言翻译功能\n")
            info_text += _("  开启后，游戏中的文本将会被翻译成您设置的语言-[{0}]\n").format(normal_config.config_normal.language)
        now_draw.text = info_text
        now_draw.width = self.width
        now_draw.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()

    def change_setting(self, cid, option_len):
        """修改设置"""
        # 自定义模型的名字
        if cid == 5:
            line_feed.draw()
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()
            line_feed.draw()
            ask_text = _("请输入您要使用的模型名（不含引号、逗号或空格）：\n")
            ask_text += _("  *目前仅支持gpt和gemini模型，未包含在示例中的更多模型名请在官方文档中查阅\n")
            ask_text += _("  gpt模型示例：gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini\n")
            ask_text += _("  gemini模型示例：gemini-1.5-pro, gemini-1.5-flash\n")
            ask_panel = panel.AskForOneMessage()
            ask_panel.set(ask_text, 99)
            new_model = ask_panel.draw()
            cache.ai_setting.ai_chat_setting[cid] = new_model
            self.test_flag = 0 # 重置测试标志
        # 调整生成文本数量的选项单独处理
        elif cid == 9:
            line_feed.draw()
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()
            line_feed.draw()
            ask_text = _("请输入1~10的数字\n")
            ask_panel = panel.AskForOneMessage()
            ask_panel.set(ask_text, 99)
            new_num = int(ask_panel.draw()) - 1
            if new_num < 0:
                new_num = 0
            elif new_num > 9:
                new_num = 9
            cache.ai_setting.ai_chat_setting[cid] = new_num
        # 调整api的base_url的选项单独处理
        elif cid == 10:
            if cache.ai_setting.ai_chat_setting[cid] == 0:
                line_feed.draw()
                line_draw = draw.LineDraw("-", self.width)
                line_draw.draw()
                line_feed.draw()
                ask_text = _("请输入您要使用的api的base_url（不含引号、逗号或空格）：\n")
                ask_text += _("  目前仅支持openAI\n")
                ask_text += _("  示例：http://my.test.server.example.com:8083/v1\n")
                ask_panel = panel.AskForOneMessage()
                ask_panel.set(ask_text, 999)
                new_base_url = ask_panel.draw()
                cache.ai_setting.now_ai_chat_base_url = new_base_url
                cache.ai_setting.ai_chat_setting[cid] = 1
            else:
                cache.ai_setting.ai_chat_setting[cid] = 0
        # 调整api的代理的选项单独处理
        elif cid == 11:
            if cache.ai_setting.ai_chat_setting[cid] == 0:
                line_feed.draw()
                line_draw = draw.LineDraw("-", self.width)
                line_draw.draw()
                line_feed.draw()
                ask_text = _("请输入您要使用的代理ip（不含引号、逗号或空格）：\n")
                ask_text += _("  目前仅支持openAI\n")
                ask_text += _("  示例：http://my.test.proxy.example.com\n")
                ask_panel = panel.AskForOneMessage()
                ask_panel.set(ask_text, 999)
                new_ip = ask_panel.draw()
                cache.ai_setting.now_ai_chat_proxy[0] = new_ip
                line_feed.draw()
                ask_text = _("请输入您要使用的代理端口，不使用端口则随便输入数字后回车即可：\n")
                ask_text += _("  示例：0.0.0.0\n")
                ask_panel = panel.AskForOneMessage()
                ask_panel.set(ask_text, 999)
                new_port = ask_panel.draw()
                # 检测输入的端口是否符合规范，需要有三个点
                if new_port.count(".") == 3:
                    cache.ai_setting.now_ai_chat_proxy[1] = new_port
                else:
                    cache.ai_setting.now_ai_chat_proxy[1] = ""
                cache.ai_setting.ai_chat_setting[cid] = 1
            else:
                cache.ai_setting.ai_chat_setting[cid] = 0
        else:
            if cache.ai_setting.ai_chat_setting[cid] < option_len - 1:
                cache.ai_setting.ai_chat_setting[cid] += 1
            else:
                cache.ai_setting.ai_chat_setting[cid] = 0

    def change_translator(self):
        """修改翻译设置"""
        cache.ai_setting.ai_chat_translator_setting += 1
        if cache.ai_setting.ai_chat_translator_setting > 2:
            cache.ai_setting.ai_chat_translator_setting = 0

    def change_api_key(self, key_type: str):
        """修改api密钥"""
        while 1:
            return_list = []
            title_draw = draw.TitleLineDraw(_("更改API密钥"), self.width)
            title_draw.draw()

            # 输出提示信息
            now_draw = draw.NormalDraw()
            info_text = _(" \n ○请在下方输入您的{0}，输入完成后点击[确定]即可保存，保存后会在当前目录下创建一个文件，请注意保管密钥文件，谨防泄露\n\n\n").format(key_type)
            now_draw.text = info_text
            now_draw.width = self.width
            now_draw.draw()

            # 输入框
            if key_type == "OPENAI_API_KEY":
                ask_text = _("请输入您的OpenAI API密钥，应当是以 sk- 开头的一长段字符串\n")
            elif key_type == "GEMINI_API_KEY":
                ask_text = _("请输入您的Gemini API密钥，应当是一个长段字符串\n")
            ask_name_panel = panel.AskForOneMessage()
            ask_name_panel.set(ask_text, 999)
            API_KEY = ask_name_panel.draw()
            line_feed.draw()
            line_feed.draw()

            # 检测输入的api密钥是否符合规范
            if key_type == "OPENAI_API_KEY" and not API_KEY.startswith("sk-"):
                info_text = _(" \n  输入的API密钥不符合规范，请重新输入\n")
                info_draw = draw.NormalDraw()
                info_draw.text = info_text
                info_draw.width = self.width
                info_draw.draw()
                continue

            # 确定按钮
            yes_draw = draw.CenterButton(_("[确定]"), _("确定"), self.width / 2)
            yes_draw.draw()
            return_list.append(yes_draw.return_text)

            # 返回按钮
            back_draw = draw.CenterButton(_("[返回]"), _("返回"), self.width / 2)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn == yes_draw.return_text:
                cache.ai_setting.ai_chat_api_key[key_type] = ask_text
                self.test_flag = 0 # 重置测试标志
                # 调用保存函数
                self.update_or_add_key("ai_chat_api_key.csv", key_type, API_KEY)
                break
            elif yrn == back_draw.return_text:
                break

    def update_or_add_key(self, file_path, key_type, new_api_key):
        """更新或添加键值对"""
        rows = []
        key_found = False

        # 检查文件是否存在，如果不存在则创建文件
        if not os.path.exists(file_path):
            with open(file_path, "w", newline='', encoding='utf-8') as f:
                pass  # 创建一个空文件

        # 读取文件内容
        with open(file_path, "r", newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == key_type:
                    row[1] = new_api_key
                    key_found = True
                rows.append(row)

        # 如果没有找到键，则添加新的键值对
        if not key_found:
            rows.append([key_type, new_api_key])

        # 写回文件
        with open(file_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    def test_ai(self):
        """测试AI"""

        # 判断在调用哪个api
        model = cache.ai_setting.ai_chat_setting[5]
        if 'gpt' in model:
            now_key_type = 'OPENAI_API_KEY'
        elif 'gemini' in model:
            now_key_type = 'GEMINI_API_KEY'
        else:
            now_key_type = 'OPENAI_API_KEY'
            info_draw = draw.NormalDraw()
            info_draw.text = _(" \n  未识别到gpt或gemini字符，将默认为openAI格式的模型\n")
            info_draw.width = self.width
            info_draw.draw()

        # 判断是否设置了api密钥
        if now_key_type not in cache.ai_setting.ai_chat_api_key:
            info_draw = draw.NormalDraw()
            info_draw.text = _(" \n  请先设置该模型的API密钥\n")
            info_draw.width = self.width
            info_draw.draw()
            return

        API_KEY = cache.ai_setting.ai_chat_api_key[now_key_type]
        # CUSTOM_ENDPOINT = cache.ai_setting.now_ai_chat_api_endpoint[now_key_type]

        if now_key_type == "OPENAI_API_KEY":
            client = openai.OpenAI(api_key=API_KEY)
            # 自定义base_url
            if cache.ai_setting.ai_chat_setting[10] == 1:
                client = client.with_options(base_url=cache.ai_setting.now_ai_chat_base_url)
            # 自定义代理
            if cache.ai_setting.ai_chat_setting[11] == 1:
                if len(cache.ai_setting.now_ai_chat_proxy[1]) == 0:
                    client = client.with_options(http_client=openai.DefaultHttpxClient(proxies=cache.ai_setting.now_ai_chat_proxy[0]))
                else:
                    client = client.with_options(http_client=openai.DefaultHttpxClient(proxies=cache.ai_setting.now_ai_chat_proxy[0], transport=httpx.HTTPTransport(local_address=cache.ai_setting.now_ai_chat_proxy[1])))
        elif now_key_type == "GEMINI_API_KEY":
            genai.configure(api_key=API_KEY)
            # gemini的传输协议改为rest
            if cache.ai_setting.ai_chat_setting[12] == 1:
                genai.configure(api_key=API_KEY, transport='rest')
            client = genai.GenerativeModel(model)

        # 测试AI，在30秒内如果没有返回结果，则认为测试不通过
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.get_completion, client, now_key_type)
            try:
                # 等待30秒以获取结果
                result = future.result(timeout=30)
                info_text = _(" \n  测试通过\n")
                self.test_flag = 1
            except concurrent.futures.TimeoutError:
                info_text = _(" \n  测试不通过，原因：连接超时\n")
                self.test_flag = 2
                self.error_message = _("连接超时")
            except Exception as e:
                info_text = _(" \n  测试不通过，原因：{0}\n").format(e)
                self.test_flag = 2
                self.error_message = str(e)
        info_draw = draw.NormalDraw()
        info_draw.text = info_text
        info_draw.width = self.width
        info_draw.draw()

    def get_completion(self, client, key_type):

        if key_type == "OPENAI_API_KEY":
            return client.chat.completions.create(
                model=cache.ai_setting.ai_chat_setting[5],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "测试消息"
                            }
                        ]
                    }
                ]
            )
        elif key_type == "GEMINI_API_KEY":
            return client.generate_content("测试消息")
