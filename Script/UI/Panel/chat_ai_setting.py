from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
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
                    # 将部分选项默认设为1
                    if cid in {7, 12, 14}:
                        cache.ai_setting.ai_chat_setting[cid] = 1
                now_setting_flag = cache.ai_setting.ai_chat_setting[cid] # 当前设置的值
                option_len = len(game_config.config_ai_chat_setting_option[cid]) # 选项的长度

                # 当前选择的选项的名字
                # 自定义模型的名字
                if cid == 5:
                    button_text = f" [{cache.ai_setting.ai_chat_setting[cid]}] "
                # 自定义发送的数据
                elif cid == 6:
                    button_text = _(" [调整发送的数据] ")
                # 自定义base_url
                elif cid == 10 and cache.ai_setting.ai_chat_setting[cid] == 1:
                    button_text = f" [{game_config.config_ai_chat_setting_option[cid][now_setting_flag]}] " + cache.ai_setting.now_ai_chat_base_url
                # 自定义代理
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
                            elif row[0] == "DEEPSEEK_API_KEY":
                                api_key = row[1]
                                cache.ai_setting.ai_chat_api_key["DEEPSEEK_API_KEY"] = api_key
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
                DEEPSEEK_API_KEY = cache.ai_setting.ai_chat_api_key.get("DEEPSEEK_API_KEY", "")
                if DEEPSEEK_API_KEY == "":
                    DEEPSEEK_API_KEY = _("未设置")
                else:
                    DEEPSEEK_API_KEY = _("已设置")
                key_info_text += _("  DeepSeek API密钥： {0}\n").format(DEEPSEEK_API_KEY)
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
                button_text = _("  [更改DeepSeek API密钥] ")
                button_len = max(len(button_text) * 2, 20)
                button_draw = draw.CenterButton(button_text, _("更改DeepSeek API密钥"), button_len, cmd_func=self.change_api_key, args=("DEEPSEEK_API_KEY"))
                button_draw.draw()
                return_list.append(button_draw.return_text)

            # 测试按钮
            if cache.ai_setting.ai_chat_setting[1] == 1:
                line_feed.draw()
                line_feed.draw()
                button_text = _("  [测试](最大延迟上限10秒) ")
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
            ask_text += _("  *此处使用的模型会默认使用官方api地址，如果是第三方或本地部署，请更改[base_url]\n")
            ask_text += _("  *更多模型名请在官方文档中查阅，非该三类的模型将自动使用OpenAI格式来处理\n")
            ask_text += _("  gpt模型示例：gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini\n")
            ask_text += _("  deepseek模型示例：deepseek-chat,deepseek-reasoner\n")
            ask_text += _("  gemini模型示例：gemini-1.5-pro, gemini-1.5-flash，gemini-2.0-flash-exp\n")
            ask_panel = panel.AskForOneMessage()
            ask_panel.set(ask_text, 99)
            new_model = ask_panel.draw()
            cache.ai_setting.ai_chat_setting[cid] = new_model
            self.test_flag = 0 # 重置测试标志
        # 自定义发送的数据
        elif cid == 6:
            self.select_send_data()
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
                ask_text += _("  调用gpt、deepseek、gemini的官方api时url会自动填充，非官方api调用或本地api调用可在此手动输入\n")
                ask_text += _("  在线调用示例：http://my.test.server.example.com:8083/v1\n")
                ask_text += _("  本地调用示例：http://localhost:1234/v1\n")
                ask_panel = panel.AskForOneMessage()
                ask_panel.set(ask_text, 999)
                new_base_url = ask_panel.draw()
                # 如果最后的字符是换行符，则删去
                if new_base_url[-1] == "\n":
                    new_base_url = new_base_url[:-1]
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
                ask_text += _("  示例：http://my.test.proxy.example.com\n")
                ask_panel = panel.AskForOneMessage()
                ask_panel.set(ask_text, 999)
                new_ip = ask_panel.draw()
                # 如果最后的字符是换行符，则删去
                if new_ip[-1] == "\n":
                    new_ip = new_ip[:-1]
                cache.ai_setting.now_ai_chat_proxy[0] = new_ip
                line_feed.draw()
                ask_text = _("请输入您要使用的代理端口，不使用端口则随便输入数字后回车即可：\n")
                ask_text += _("  示例：0.0.0.0\n")
                ask_panel = panel.AskForOneMessage()
                ask_panel.set(ask_text, 999)
                new_port = ask_panel.draw()
                # 如果最后的字符是换行符，则删去
                if new_port[-1] == "\n":
                    new_port = new_port[:-1]
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

    def select_send_data(self):
        """选择发送的数据"""
        while True:
            send_data_all_flags = cache.ai_setting.send_data_flags
            return_list = []
            title_draw = draw.TitleLineDraw(_("选择发送给AI的数据"), self.width)
            title_draw.draw()
            
            # 显示提示信息
            info_draw = draw.NormalDraw()
            info_text = _(" \n ○发送的数据越多，AI可以利用的信息就越多，理论效果会越好\n")
            info_text += _("  但同时消耗的tokens和响应时间也越多，也可能因为信息太多而抓不住重点或超出上下文长度\n")
            info_text += _("  每项的数据量有小、中、大三级区分\n")
            info_text += _("  发送数据的文件路径为：data\csv\Ai_Chat_Send_Data.csv，可根据需要自行修改提示词\n")
            info_draw.text = info_text
            info_draw.width = self.width
            info_draw.draw()
            
            # 遍历所有数据
            for send_data_cid in game_config.config_ai_chat_send_data:
                ai_chat_send_data = game_config.config_ai_chat_send_data[send_data_cid]
                
                # 跳过ID为0的表头
                if send_data_cid == 0:
                    continue
                    
                # 初始化不存在的数据选择状态
                if send_data_cid not in send_data_all_flags:
                    # 如果是默认选择的，设为True，否则设为False
                    if ai_chat_send_data.default == 1:
                        send_data_all_flags[send_data_cid] = True
                    else:
                        send_data_all_flags[send_data_cid] = False

                # 如果当前cid的余数是1，则换行
                if send_data_cid % 10 == 1:
                    line_feed.draw()

                # 获取数据信息
                send_data_name = ai_chat_send_data.name
                send_data_required = ai_chat_send_data.required
                send_data_size = ai_chat_send_data.data_size
                
                # 数据量显示
                if send_data_size == 1:
                    size_text = _("小")
                elif send_data_size == 2:
                    size_text = _("中")
                elif send_data_size == 3:
                    size_text = _("大")
                else:
                    size_text = _("未知")
                    
                # 构建显示文本
                line_text = f"  {send_data_name}({size_text})  "
                button_len = max(len(line_text) * 2, 40)
                
                # 绘制数据名称和数据量，点击后将打印该send_data的提示信息
                name_draw = draw.LeftButton(line_text, send_data_name + '_prompt', button_len, cmd_func=self.print_send_data_prompt, args=(send_data_cid,))
                name_draw.draw()
                return_list.append(name_draw.return_text)
                
                # 绘制选择按钮（必选数据没有按钮）
                if send_data_required == 1:
                    button_text = _("【必选】")
                    required_draw = draw.LeftDraw()
                    required_draw.text = button_text
                    required_draw.draw()
                else:
                    if send_data_all_flags[send_data_cid]:
                        button_text = _("[√]")
                    else:
                        button_text = _("[×]")
                    button_draw = draw.CenterButton(button_text, send_data_name, 10, cmd_func=self.toggle_send_data, args=(send_data_cid))
                    button_draw.draw()
                    return_list.append(button_draw.return_text)

                line_feed.draw()
            
            # 添加返回按钮
            line_feed.draw()
            save_draw = draw.CenterButton(_("[返回]"), _("返回"), window_width // 2)
            save_draw.draw()
            return_list.append(save_draw.return_text)
            
            line_feed.draw()
            
            # 等待用户选择
            yrn = flow_handle.askfor_all(return_list)
            
            # 处理用户选择
            if yrn == save_draw.return_text:
                break

    def print_send_data_prompt(self, send_data_cid):
        """打印数据的提示信息"""
        line_draw = draw.LineDraw("-", self.width)
        line_draw.draw()
        line_feed.draw()
        ai_chat_send_data = game_config.config_ai_chat_send_data[send_data_cid]
        now_draw = draw.WaitDraw()
        now_draw.text = ai_chat_send_data.prompt
        now_draw.width = self.width
        now_draw.draw()
        line_feed.draw()
        line_feed.draw()

    def toggle_send_data(self, send_data_cid):
        """切换数据是否被选择"""
        cache.ai_setting.send_data_flags[send_data_cid] = not cache.ai_setting.send_data_flags[send_data_cid]

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
                ask_text = _("请输入您的OpenAI API密钥，应当是以 sk- 开头的一长段字符串（第三方或本地部署没有格式需求）\n")
            elif key_type == "DEEPSEEK_API_KEY":
                ask_text = _("请输入您的DeepSeek API密钥，应当是以 sk- 开头的一长段字符串（第三方或本地部署没有格式需求）\n")
            elif key_type == "GEMINI_API_KEY":
                ask_text = _("请输入您的Gemini API密钥，应当是一个长段字符串\n")
            ask_name_panel = panel.AskForOneMessage()
            ask_name_panel.set(ask_text, 999)
            API_KEY = ask_name_panel.draw()
            line_feed.draw()
            line_feed.draw()

            # 检测输入的api密钥是否符合规范
            if (key_type == "OPENAI_API_KEY" or key_type == "DEEPSEEK_API_KEY") and not API_KEY.startswith("sk-"):
                info_text = _(" \n  输入的API密钥不符合规范，请确认是否输入正确（第三方或本地部署没有格式需求）\n\n")
                info_draw = draw.NormalDraw()
                info_draw.text = info_text
                info_draw.width = self.width
                info_draw.draw()

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
        if model == 0 or model == "0":
            info_draw = draw.WaitDraw()
            info_draw.style = "warning"
            info_draw.text = _(" \n  未设置模型，请先选择模型\n")
            info_draw.width = self.width
            info_draw.draw()
            return
        if 'gpt' in model:
            now_key_type = 'OPENAI_API_KEY'
        elif 'deepseek' in model:
            now_key_type = 'DEEPSEEK_API_KEY'
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

        if now_key_type == "OPENAI_API_KEY" or now_key_type == "DEEPSEEK_API_KEY":
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
        elif now_key_type == "GEMINI_API_KEY":
            genai.configure(api_key=API_KEY)
            # gemini的传输协议改为rest
            if cache.ai_setting.ai_chat_setting[12] == 1:
                genai.configure(api_key=API_KEY, transport='rest')
            client = genai.GenerativeModel(model)

        info_draw = draw.NormalDraw()
        info_draw.width = self.width

        # 测试AI，在10秒内如果没有返回结果，则认为测试不通过
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.get_completion, client, now_key_type)
            try:
                # 等待10秒以获取结果
                result = future.result(timeout=10)
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
            finally:
                info_draw.text = info_text
                info_draw.draw()
                # TODO 不知道为什么取消没有生效，十分奇怪
                # 取消任务
                future.cancel()
                # 关闭线程池
                executor.shutdown(wait=False, cancel_futures=True)
                return

    def get_completion(self, client, key_type):
        """获取AI的返回结果"""
        if key_type == "OPENAI_API_KEY":
            return client.chat.completions.create(
                model=cache.ai_setting.ai_chat_setting[5],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "这是一条测试消息，如果收到请指直接回复1即可，不需要思考，不要回复其他内容"
                            }
                        ]
                    }
                ]
            )
        elif key_type == "GEMINI_API_KEY":
            return client.generate_content("这是一条测试消息，如果收到请指直接回复1即可，不需要思考，不需要回复其他内容")
