from typing import List
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, constant
from Script.UI.Moudle import draw, panel
from Script.Config import game_config, normal_config
import openai
import concurrent.futures

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

    def draw(self):
        """绘制对象"""

        title_text = _("文本生成AI设置")
        title_draw = draw.TitleLineDraw(title_text, self.width)
        if 1 not in cache.ai_chat_setting or cache.ai_chat_setting[1] == 0:
            while 1:
                return_list = []
                title_draw.draw()

                # 输出提示信息
                now_draw = draw.NormalDraw()
                info_text = _(" \n ○文本生成AI是一个试验性的功能，存在相当多的风险，所以需要您确认以下所有免责事项才可以使用\n\n\n 1.该功能需要您自行准备好一个OpenAI的API密钥，并保证电脑环境可以正常访问OpenAI的API，游戏本身不会为您提供相关的获取方法，请自行准备\n\n\n   2.文本生成AI以及网络环境的使用会产生一定的费用，该费用需自己承担，与开发者没有任何关系\n\n\n 3.文本生成AI的使用可能会产生一定的风险，包括但不限于：聊天内容不当、聊天内容不符合社会规范等，开发者不对生成的内容负责，也不代表开发者同意或反对其中的任何观点\n\n\n 4.不恰当的使用过程或生成内容有可能会导致OpenAI对您的api和相关账号提出警告或进一步的停止服务等举措，请牢记该风险，相关的直接或间接损失均需您自己承担，与开发者无关\n\n\n 5.本声明的解释权归开发者所有，且在版本更新中声明内容可能有所变更，请以最新版本为准。\n\n\n 6.基于以上又叠了这么多层buff，明确知道自己在做什么，并且愿意承担费用和风险的人再来点击下一步吧\n\n\n")
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
            now_draw.text = info_text
            now_draw.width = self.width
            now_draw.draw()

            # 遍历全部设置
            for cid in game_config.config_ai_chat_setting:
                # 如果当前不是第1个设置，且第1个设置没有开启，则不显示后面的设置
                if cid != 1 and (1 not in cache.ai_chat_setting or cache.ai_chat_setting[1] == 0):
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
                if cid not in cache.ai_chat_setting:
                    cache.ai_chat_setting[cid] = 0
                now_setting_flag = cache.ai_chat_setting[cid] # 当前设置的值
                option_len = len(game_config.config_ai_chat_setting_option[cid]) # 选项的长度

                # 当前选择的选项的名字
                button_text = f" [{game_config.config_ai_chat_setting_option[cid][now_setting_flag]}] "
                button_len = max(len(button_text) * 2, 20)

                button_draw = draw.LeftButton(button_text, str(cid) + button_text, button_len, cmd_func=self.change_setting, args=(cid, option_len))
                button_draw.draw()
                return_list.append(button_draw.return_text)

            # api密钥
            if cache.ai_chat_setting[1] == 1:
                line_feed.draw()
                line_feed.draw()
                # 查看当前目录下是否有api密钥文件
                try:
                    with open("ai_chat_api_key.txt", "r") as f:
                        api_key = f.read()
                        # 去掉换行符
                        api_key = api_key.replace("\n", "")
                        cache.ai_chat_api_key["OPENAI_API_KEY"] = api_key
                except FileNotFoundError:
                    pass
                # 显示当前api的密钥
                OPENAI_API_KEY = cache.ai_chat_api_key.get("OPENAI_API_KEY", "")
                if OPENAI_API_KEY == "":
                    OPENAI_API_KEY = _("未设置")
                else:
                    OPENAI_API_KEY = _("已设置")
                key_info_text = f"  OpenAI API密钥： {OPENAI_API_KEY}\n"
                key_info_draw = draw.NormalDraw()
                key_info_draw.text = key_info_text
                key_info_draw.width = self.width
                key_info_draw.draw()

                # 更改api密钥
                button_text = _("  [更改OpenAI API密钥] ")
                button_len = max(len(button_text) * 2, 20)
                button_draw = draw.LeftButton(button_text, _("更改OpenAI API密钥"), button_len, cmd_func=self.change_api_key)
                button_draw.draw()
                return_list.append(button_draw.return_text)

            # 测试按钮
            if cache.ai_chat_setting[1] == 1:
                line_feed.draw()
                line_feed.draw()
                button_text = _("  [测试] ")
                button_len = max(len(button_text) * 2, 20)
                button_draw = draw.LeftButton(button_text, _("测试"), button_len, cmd_func=self.test_ai)
                button_draw.draw()
                return_list.append(button_draw.return_text)
                if self.test_flag == 0:
                    pass
                elif self.test_flag == 1:
                    info_text = _(" \n  测试通过，当前调用的模型为：") + constant.open_ai_model_list[cache.ai_chat_setting[5]] + "\n"
                    info_draw = draw.NormalDraw()
                    info_draw.text = info_text
                    info_draw.width = self.width
                    info_draw.draw()
                elif self.test_flag == 2:
                    info_text = _(" \n  测试不通过\n")
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
        ai_chat_setting_data = game_config.config_ai_chat_setting[cid]
        info_text = f"\n {ai_chat_setting_data.info}\n"
        now_draw.text = info_text
        now_draw.width = self.width
        now_draw.draw()
        line = draw.LineDraw("-", self.width)
        line.draw()

    def change_setting(self, cid, option_len):
        """修改设置"""
        if cache.ai_chat_setting[cid] < option_len - 1:
            cache.ai_chat_setting[cid] += 1
        else:
            cache.ai_chat_setting[cid] = 0

    def change_api_key(self):
        """修改api密钥"""
        while 1:
            return_list = []
            title_draw = draw.TitleLineDraw(_("更改OpenAI API密钥"), self.width)
            title_draw.draw()

            # 输出提示信息
            now_draw = draw.NormalDraw()
            info_text = _(" \n ○请在下方输入您的OpenAI API密钥，输入完成后点击[确定]即可保存，保存后会在当前目录下创建一个文件，请注意保管密钥文件，谨防泄露\n\n\n")
            now_draw.text = info_text
            now_draw.width = self.width
            now_draw.draw()

            # 输入框
            ask_text = _("请输入您的OpenAI API密钥，应当是以 sk- 开头的一长段字符串\n")
            ask_name_panel = panel.AskForOneMessage()
            ask_name_panel.set(ask_text, 10)
            OPENAI_API_KEY = ask_name_panel.draw()
            line_feed.draw()
            line_feed.draw()

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
                cache.ai_chat_api_key["OPENAI_API_KEY"] = ask_text
                # 在当前目录下创建一个文件，保存api密钥
                with open("ai_chat_api_key.txt", "w") as f:
                    f.write(OPENAI_API_KEY)
                break
            elif yrn == back_draw.return_text:
                break

    def test_ai(self):
        """测试AI"""
        if "OPENAI_API_KEY" not in cache.ai_chat_api_key:
            line_feed.text = _(" \n  请先设置OpenAI API密钥\n")
            line_feed.width = self.width
            line_feed.draw()
            return
        OPENAI_API_KEY = cache.ai_chat_api_key["OPENAI_API_KEY"]
        # print(OPENAI_API_KEY)

        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        # 测试AI，在30秒内如果没有返回结果，则认为测试不通过
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.get_completion, client)
            try:
                # 等待30秒以获取结果
                result = future.result(timeout=30)
                info_text = _(" \n  测试通过\n")
                self.test_flag = 1
            except concurrent.futures.TimeoutError:
                info_text = _(" \n  测试不通过\n")
                self.test_flag = 2
            except Exception as e:
                info_text = _(" \n  测试不通过\n")
                self.test_flag = 2
        info_draw = draw.NormalDraw()
        info_draw.text = info_text
        info_draw.width = self.width
        info_draw.draw()

    def get_completion(self, client):
        return client.chat.completions.create(
            model=constant.open_ai_model_list[cache.ai_chat_setting[5]],
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
