from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QLabel, QPushButton, QMenu, QHBoxLayout
from PySide6.QtGui import QFont, QAction
from PySide6.QtCore import Qt
import cache_control

font = QFont()
font.setPointSize(cache_control.now_font_size)
font.setFamily(cache_control.now_font_name)

class ItemTextEdit(QWidget):
    """文本编辑框主体"""

    def __init__(self):
        """初始化文本编辑框主体"""
        super(ItemTextEdit, self).__init__()
        self.font = font
        self.setFont(self.font)
        label_layout = QVBoxLayout()
        # 加入标题
        self.info_label = QLabel()
        self.info_label.setText("文本编辑")
        label_layout.addWidget(self.info_label)

        # 加入保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save)
        # 加入文本触发者名字按钮
        self.insert_name_button = QPushButton("插入文本触发者名字")
        self.insert_name_button.clicked.connect(lambda: self.insert_text('{Name}'))
        # 加入文本触发者的交互对象名字按钮
        self.insert_target_name_button = QPushButton("插入文本触发者的交互对象名字")
        self.insert_target_name_button.clicked.connect(lambda: self.insert_text('{TargetName}'))
        # 加入玩家名字按钮
        self.insert_player_name_button = QPushButton("插入玩家名字")
        self.insert_player_name_button.clicked.connect(lambda: self.insert_text('{PlayerName}'))
        # 格式按钮：加粗/斜体/下划线
        self.bold_button = QPushButton("加粗")
        self.bold_button.clicked.connect(lambda: self.apply_inline_tag('bold'))
        self.italic_button = QPushButton("斜体")
        self.italic_button.clicked.connect(lambda: self.apply_inline_tag('italic'))
        self.underline_button = QPushButton("下划线")
        self.underline_button.clicked.connect(lambda: self.apply_inline_tag('underline'))
        # 预览按钮（切换编辑/预览）
        self.preview_button = QPushButton("预览")
        self.preview_button.setCheckable(True)
        self.preview_button.clicked.connect(self.toggle_preview)
        # 加入一行文本提示
        self.max_length = 0
        self.info_label = QLabel()
        self.info_label.setText(f"右键可浏览全部代码文本进行插入，当前最长行字符总长度为{self.max_length}，建议不要超过100")
        # 上述按钮的布局变成横向（包含预览切换）
        insert_button_layout = QHBoxLayout()
        insert_button_layout.addWidget(self.save_button)
        insert_button_layout.addWidget(self.insert_name_button)
        insert_button_layout.addWidget(self.insert_target_name_button)
        insert_button_layout.addWidget(self.insert_player_name_button)
        style_button_layout = QHBoxLayout()
        style_button_layout.addWidget(self.bold_button)
        style_button_layout.addWidget(self.italic_button)
        style_button_layout.addWidget(self.underline_button)
        style_button_layout.addWidget(self.preview_button)
        label_layout.addLayout(insert_button_layout)
        label_layout.addLayout(style_button_layout)
        label_layout.addWidget(self.info_label)
        # 加入文本编辑框
        self.now_text = ""
        self.label_text = QTextEdit(self.now_text)
        label_layout.addWidget(self.label_text)

        # 预览区域（只读，用于展示渲染后的 HTML）
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setVisible(False)
        label_layout.addWidget(self.preview_edit)

        # 事件模式下的注释编辑栏（默认高度3行）
        self.comment_label = QLabel("事件注释（仅事件模式可编辑）：")
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("可填写事件注释，支持多行")
        self.comment_edit.setFont(self.font)
        self.comment_edit.setVisible(False)  # 默认隐藏，事件模式下显示
        self.comment_label.setVisible(False)
        self.comment_edit.setFixedHeight(self.comment_edit.fontMetrics().height() * 3 + 16)  # 3行高度，略加padding
        label_layout.addWidget(self.comment_label)
        label_layout.addWidget(self.comment_edit)

        # 设置布局
        self.setLayout(label_layout)

        # 创建右键菜单
        self.right_click_menu = QMenu(self)
        self.right_click_menu.setFont(self.font)
        # 创建菜单项
        self.create_right_click_menu()
        # 将右键菜单绑定到文本编辑框上
        self.label_text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label_text.customContextMenuRequested.connect(self.show_right_click_menu)

    def create_right_click_menu(self):
        """创建右键菜单"""
        # 创建四个一级菜单
        # 将子菜单和其项的显示字体统一为编辑器当前字体，避免系统默认样式导致不一致
        chara_menu = self.right_click_menu.addMenu("角色名")
        chara_menu.setFont(self.font)
        chara_nick_menu = self.right_click_menu.addMenu("角色称呼")
        chara_nick_menu.setFont(self.font)
        common_text_menu = self.right_click_menu.addMenu("纸娃娃文本")
        common_text_menu.setFont(self.font)
        clothing_menu = self.right_click_menu.addMenu("服装名")
        clothing_menu.setFont(self.font)
        scene_menu = self.right_click_menu.addMenu("场景名")
        scene_menu.setFont(self.font)
        food_menu = self.right_click_menu.addMenu("食物名")
        food_menu.setFont(self.font)
        other_menu = self.right_click_menu.addMenu("其他")
        other_menu.setFont(self.font)
        draw_menu = self.right_click_menu.addMenu("绘制")
        draw_menu.setFont(self.font)

        # 角色名菜单项
        chara_items = [
            {"text": "文本触发者名字", "slot": lambda: self.insert_text('{Name}')},
            {"text": "文本触发者的交互对象名字", "slot": lambda: self.insert_text('{TargetName}')},
            {"text": "玩家名字", "slot": lambda: self.insert_text('{PlayerName}')},
            {"text": "玩家的交互对象的名字", "slot": lambda: self.insert_text('{PlayerTargetName}')},
            {"text": "当前场景中随机一名角色名字", "slot": lambda: self.insert_text('{SceneOneCharaName}')},
            {"text": "移动目标场景中随机一名角色名字", "slot": lambda: self.insert_text('{TargetOneCharaName}')},
            {"text": "移动出发场景中随机一名角色名字", "slot": lambda: self.insert_text('{SrcOneCharaName}')},
            {"text": "H行为被打断时的闯入者的名字", "slot": lambda: self.insert_text('{HInterruptCharaName}')},
        ]

        # 角色称呼菜单项
        chara_nick_items = [
            {"text": "玩家对触发者的称呼", "slot": lambda: self.insert_text('{NickName}')},
            {"text": "触发者对玩家的称呼", "slot": lambda: self.insert_text('{NickNameToPl}')},
            {"text": "玩家对交互对象的称呼", "slot": lambda: self.insert_text('{TargetNickName}')},
            {"text": "交互对象对玩家的称呼", "slot": lambda: self.insert_text('{TargetNickNameToPl}')},
            {"text": "触发者与交互对象中非玩家的那个对玩家的称呼", "slot": lambda: self.insert_text('{PlayerNickName}')},
        ]

        # 纸娃娃文本菜单项
        common_text_items = [
            {"text": "玩家阴茎描述_长句", "slot": lambda: self.insert_text('{penis}')},
            {"text": "玩家阴茎描述_短词", "slot": lambda: self.insert_text('{penis_s}')},
            {"text": "玩家交互对象口腔描述_长句", "slot": lambda: self.insert_text('{mouth}')},
            {"text": "玩家交互对象口腔描述_短词", "slot": lambda: self.insert_text('{mouth_s}')},
            {"text": "玩家交互对象头发描述_长句", "slot": lambda: self.insert_text('{hair}')},
            {"text": "玩家交互对象头发描述_短词", "slot": lambda: self.insert_text('{hair_s}')},
            {"text": "玩家交互对象脸部描述_长句", "slot": lambda: self.insert_text('{face}')},
            {"text": "玩家交互对象脸部描述_短词", "slot": lambda: self.insert_text('{face_s}')},
            {"text": "玩家交互对象胸部描述_长句", "slot": lambda: self.insert_text('{breast}')},
            {"text": "玩家交互对象胸部描述_短词", "slot": lambda: self.insert_text('{breast_s}')},
            {"text": "玩家交互对象腋部描述_长句", "slot": lambda: self.insert_text('{armpit}')},
            {"text": "玩家交互对象腋部描述_短词", "slot": lambda: self.insert_text('{armpit_s}')},
            {"text": "玩家交互对象手部描述_长句", "slot": lambda: self.insert_text('{hands}')},
            {"text": "玩家交互对象手部描述_短词", "slot": lambda: self.insert_text('{hands_s}')},
            {"text": "玩家交互对象阴道描述_长句", "slot": lambda: self.insert_text('{vagina}')},
            {"text": "玩家交互对象阴道描述_短词", "slot": lambda: self.insert_text('{vagina_s}')},
            {"text": "玩家交互对象子宫描述_长句", "slot": lambda: self.insert_text('{womb}')},
            {"text": "玩家交互对象子宫描述_短词", "slot": lambda: self.insert_text('{womb_s}')},
            {"text": "玩家交互对象后穴描述_短词", "slot": lambda: self.insert_text('{anal_s}')},
            {"text": "玩家交互对象尿道描述_短词", "slot": lambda: self.insert_text('{urethra_s}')},
            {"text": "玩家交互对象腿部描述_短词", "slot": lambda: self.insert_text('{legs_s}')},
            {"text": "玩家交互对象脚部描述_短词", "slot": lambda: self.insert_text('{feet_s}')},
        ]

        # 服装名菜单项
        clothing_items = [
            {"text": "自己的上衣名字", "slot": lambda: self.insert_text('{SelfUpClothName}')},
            {"text": "自己的下衣名字", "slot": lambda: self.insert_text('{SelfDownClothName}')},
            {"text": "交互对象的上衣名字", "slot": lambda: self.insert_text('{TargetUpClothName}')},
            {"text": "交互对象的下衣名字", "slot": lambda: self.insert_text('{TargetDownClothName}')},
            {"text": "交互对象的胸衣名字", "slot": lambda: self.insert_text('{TargetBraName}')},
            {"text": "交互对象的裙子名字", "slot": lambda: self.insert_text('{TargetSkiName}')},
            {"text": "交互对象的内裤名字", "slot": lambda: self.insert_text('{TargetPanName}')},
            {"text": "交互对象的袜子名字", "slot": lambda: self.insert_text('{TargetSocName}')},
            {"text": "自己穿着的上衣名字", "slot": lambda: self.insert_text('{UpClothName}')},
            {"text": "自己穿着的下衣名字", "slot": lambda: self.insert_text('{DownClothName}')},
            {"text": "自己穿着的内裤名字", "slot": lambda: self.insert_text('{PanName}')},
            {"text": "自己穿着的袜子名字", "slot": lambda: self.insert_text('{SocName}')},
        ]

        # 场景名菜单项
        scene_items = [
            {"text": "当前场景名字", "slot": lambda: self.insert_text('{SceneName}')},
            {"text": "移动目标场景名字", "slot": lambda: self.insert_text('{TargetSceneName}')},
            {"text": "移动出发场景名字", "slot": lambda: self.insert_text('{SrcSceneName}')},
        ]

        # 食物名菜单项
        food_items = [
            {"text": "当前行为中食物名字", "slot": lambda: self.insert_text('{FoodName}')},
            {"text": "食物制作时间", "slot": lambda: self.insert_text('{MakeFoodTime}')},
            {"text": "当前背包里所有食物名字", "slot": lambda: self.insert_text('{AllFoodName}')},
        ]

        # 其他名菜单项
        other_items = [
            {"text": "当前书籍名字", "slot": lambda: self.insert_text('{BookName}')},
            {"text": "当前行为榨出母乳的毫升数", "slot": lambda: self.insert_text('{MilkMl}')},
            {"text": "跳过每行确认，直接显示到最后一行", "slot": lambda: self.insert_text('{Jump}')},
        ]

        # 绘制菜单项
        draw_items = [
            {"text": "加粗", "slot": lambda: self.insert_text('<bold></bold>')},
            {"text": "斜体", "slot": lambda: self.insert_text('<italic></italic>')},
            {"text": "下划线", "slot": lambda: self.insert_text('<underline></underline>')},
            {"text": "红色", "slot": lambda: self.insert_text('<red></red>')},
            {"text": "绿色", "slot": lambda: self.insert_text('<green></green>')},
            {"text": "蓝色", "slot": lambda: self.insert_text('<blue></blue>')},
            {"text": "黄色", "slot": lambda: self.insert_text('<yellow></yellow>')},
            {"text": "粉色", "slot": lambda: self.insert_text('<pink></pink>')},
            {"text": "紫色", "slot": lambda: self.insert_text('<purple></purple>')},
            {"text": "橙色", "slot": lambda: self.insert_text('<orange></orange>')},
            {"text": "金黄色", "slot": lambda: self.insert_text('<gold_enrod></gold_enrod>')},
            {"text": "体力颜色", "slot": lambda: self.insert_text('<hp_point></hp_point>')},
            {"text": "气力颜色", "slot": lambda: self.insert_text('<mp_point></mp_point>')},
            {"text": "理智颜色", "slot": lambda: self.insert_text('<sanity></sanity>')},
            {"text": "精液颜色", "slot": lambda: self.insert_text('<semen></semen>')},
            {"text": "尿液颜色", "slot": lambda: self.insert_text('<khaki></khaki>')},
        ]

        # 将菜单项添加到对应的一级菜单中
        menu_items = [
            (chara_menu, chara_items),
            (chara_nick_menu, chara_nick_items),
            (common_text_menu, common_text_items),
            (clothing_menu, clothing_items),
            (scene_menu, scene_items),
            (food_menu, food_items),
            (other_menu, other_items),
            (draw_menu, draw_items),
        ]

        # 遍历菜单项，添加到对应的菜单中
        for menu, items in menu_items:
            for item in items:
                action = QAction(item["text"], self)
                action.triggered.connect(item["slot"])
                menu.addAction(action)

    def show_right_click_menu_event(self, pos):
        """显示右键菜单（修正方法名避免遮盖）"""
        self.right_click_menu.exec_(self.label_text.mapToGlobal(pos))

    def toggle_preview(self, checked: bool):
        """切换编辑/预览模式；预览时把当前文本渲染为 HTML 显示在 preview_edit 中"""
        if checked:
            # 切换到预览模式
            raw = self.label_text.toPlainText()
            raw = raw.replace('\\n', '\n')
            html = render_text_for_display(raw)
            self.preview_edit.setHtml(html)
            self.preview_edit.setVisible(True)
            self.label_text.setVisible(False)
            # 禁用其他控件以防误编辑
            self.save_button.setEnabled(False)
            self.insert_name_button.setEnabled(False)
            self.insert_target_name_button.setEnabled(False)
            self.insert_player_name_button.setEnabled(False)
            self.bold_button.setEnabled(False)
            self.italic_button.setEnabled(False)
            self.underline_button.setEnabled(False)
        else:
            # 返回编辑模式
            self.preview_edit.setVisible(False)
            self.label_text.setVisible(True)
            self.save_button.setEnabled(True)
            self.insert_name_button.setEnabled(True)
            self.insert_target_name_button.setEnabled(True)
            self.insert_player_name_button.setEnabled(True)
            self.bold_button.setEnabled(True)
            self.italic_button.setEnabled(True)
            self.underline_button.setEnabled(True)

    def apply_inline_tag(self, tag_name: str):
        """在选中文本两侧插入左右标签；若无选区则插入完整标签并把光标移到中间。

        示例:
            apply_inline_tag('bold') -> 若有选中文本：在选区前插入 '<bold>'，在选区后插入 '</bold>'
                                    -> 若无选区：插入 '<bold></bold>' 并将光标放到标签中间
        """
        te = self.label_text
        cursor = te.textCursor()
        selected_text = cursor.selectedText()
        left_tag = f'<{tag_name}>'
        right_tag = f'</{tag_name}>'

        if selected_text:
            # 包裹选区：用左标签 + 选中文本 + 右标签替换选区
            cursor.insertText(f'{left_tag}{selected_text}{right_tag}')
            # 插入后光标默认在插入内容末端，无需额外调整
        else:
            # 无选区：插入完整标签并将光标移动到两标签之间
            insert_pos = cursor.position()
            cursor.insertText(f'{left_tag}{right_tag}')
            # 将光标移动到左标签之后的位置以便用户继续输入
            cursor.setPosition(insert_pos + len(left_tag))
            te.setTextCursor(cursor)

    def insert_text(self, text):
        """右键菜单插入文本"""
        self.label_text.insertPlainText(text)

    def update(self):
        """更新文本内容"""
        if cache_control.now_edit_type_flag == 1:
            # 事件模式，显示注释栏
            self.comment_label.setVisible(True)
            self.comment_edit.setVisible(True)
            event_obj = cache_control.now_event_data.get(cache_control.now_select_id)
            self.now_text = event_obj.text if event_obj else ""
            # 注释属性（comment）
            comment = getattr(event_obj, "comment", "") if event_obj else ""
            self.comment_edit.setText(comment.replace("\\n", "\n"))
        else:
            # 非事件模式，隐藏注释栏
            self.comment_label.setVisible(False)
            self.comment_edit.setVisible(False)
            if cache_control.now_edit_type_flag == 0:
                self.now_text = cache_control.now_talk_data[cache_control.now_select_id].text
            else:
                self.now_text = ""
        # 将换行符"\n"换成真正的换行
        self.now_text = self.now_text.replace("\\n", "\n")
        self.label_text.setText(self.now_text)
        # 计算最长行长度
        max_length = 0
        for line in self.now_text.split("\n"):
            if len(line) > max_length:
                max_length = len(line)
        self.max_length = max_length
        # 更新提示文本
        self.info_label.setText(f"右键菜单可插入更多文本，当前最长行字符总长度为{self.max_length}，建议不要超过100")

    def save(self):
        """保存文本内容"""
        now_text = self.label_text.toPlainText()
        # 检测里面的","，换成"，"，防止csv文件解析出错
        now_text = now_text.replace(",", "，")
        # 检测换行符，换成"\n"，防止csv文件解析出错
        now_text = now_text.replace("\n", "\\n")
        # 保存注释内容（仅事件模式）
        if cache_control.now_edit_type_flag == 1 and cache_control.now_select_id in cache_control.now_event_data:
            cache_control.now_event_data[cache_control.now_select_id].text = now_text
            comment_text = self.comment_edit.toPlainText().replace("\n", "\\n")
            cache_control.now_event_data[cache_control.now_select_id].comment = comment_text
        elif cache_control.now_edit_type_flag == 0 and cache_control.now_select_id in cache_control.now_talk_data:
            cache_control.now_talk_data[cache_control.now_select_id].text = now_text
        # 检测英文双引号，直接删除，防止csv文件解析出错
        now_text = now_text.replace("\"", "")

    def show_right_click_menu(self, pos):
        """显示右键菜单"""
        self.right_click_menu.exec_(self.label_text.mapToGlobal(pos))


def render_text_for_display(raw_text: str) -> str:
    """把自定义标签转换为 HTML 并返回完整的 HTML 字符串。

    支持标签：bold/italic/underline -> b/i/u
            颜色标签 (red, green, blue, yellow, pink, purple, orange, gold_enrod)
            特殊颜色标签 (hp_point, mp_point, sanity, semen, khaki) 映射为样式颜色名或 hex
    """
    tag_map = {
        'bold': ('b', None),
        'italic': ('i', None),
        'underline': ('u', None),
        'red': ('span', 'color:red'),
        'green': ('span', 'color:green'),
        'blue': ('span', 'color:blue'),
        'yellow': ('span', 'color:yellow'),
        'pink': ('span', 'color:pink'),
        'purple': ('span', 'color:purple'),
        'orange': ('span', 'color:orange'),
        'gold_enrod': ('span', 'color:goldenrod'),
        'hp_point': ('span', 'color:#ff5a5a'),
        'mp_point': ('span', 'color:#70c070'),
        'sanity': ('span', 'color:#7272bc'),
        'semen': ('span', 'color:#fffacd'),
        'khaki': ('span', 'color:#f0e68c'),
    }

    html = raw_text
    for custom_tag, (html_tag, style) in tag_map.items():
        open_tag = f'<{custom_tag}>'
        close_tag = f'</{custom_tag}>'
        if style:
            replacement_open = f'<{html_tag} style="{style}">'
        else:
            replacement_open = f'<{html_tag}>'
        replacement_close = f'</{html_tag}>'
        html = html.replace(open_tag, replacement_open).replace(close_tag, replacement_close)

    # 将换行转换为 <br>
    html = html.replace('\n', '<br>')

    # 使用当前字体和大小包裹
    font_name = getattr(cache_control, 'now_font_name', 'sans-serif')
    font_size = getattr(cache_control, 'now_font_size', 12)
    safe_html = f"<div style='font-family:{font_name}; font-size:{font_size}pt;'>{html}</div>"
    return safe_html
