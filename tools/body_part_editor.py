"""
身体部位数据编辑工具

功能说明：
用于手动修正角色图片的身体部位关键点数据。
支持读取单个JSON文件或整个文件夹，在图片上直接拖动修改部位点位置。

使用方法：
1. 运行本脚本启动GUI界面
2. 通过菜单读取单个JSON文件或文件夹
3. 在图片上拖动节点修改位置
4. 使用Ctrl+S保存，使用左右键切换文件

作者：AI Assistant
日期：2026-02-12
"""

import os
import sys
import json
import copy
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

# COCO 17 关键点名称
COCO_KEYPOINTS = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]

# 关键点中文名称映射
KEYPOINT_NAMES_CN = {
    "nose": "鼻子",
    "left_eye": "左眼",
    "right_eye": "右眼",
    "left_ear": "左耳",
    "right_ear": "右耳",
    "left_shoulder": "左肩",
    "right_shoulder": "右肩",
    "left_elbow": "左肘",
    "right_elbow": "右肘",
    "left_wrist": "左腕",
    "right_wrist": "右腕",
    "left_hip": "左髋",
    "right_hip": "右髋",
    "left_knee": "左膝",
    "right_knee": "右膝",
    "left_ankle": "左踝",
    "right_ankle": "右踝"
}

# 骨架连接定义 (起点ID, 终点ID, 颜色)
SKELETON_CONNECTIONS = [
    # 头部
    (0, 1, "#FF6B6B"),   # 鼻子-左眼
    (0, 2, "#FF6B6B"),   # 鼻子-右眼
    (1, 3, "#FFE66D"),   # 左眼-左耳
    (2, 4, "#FFE66D"),   # 右眼-右耳
    # 肩膀连接
    (5, 6, "#4ECDC4"),   # 左肩-右肩
    # 左臂
    (5, 7, "#95E1D3"),   # 左肩-左肘
    (7, 9, "#95E1D3"),   # 左肘-左腕
    # 右臂
    (6, 8, "#A8D8EA"),   # 右肩-右肘
    (8, 10, "#A8D8EA"),  # 右肘-右腕
    # 躯干
    (5, 11, "#DDA0DD"),  # 左肩-左髋
    (6, 12, "#DDA0DD"),  # 右肩-右髋
    # 髋部连接
    (11, 12, "#F8B500"), # 左髋-右髋
    # 左腿
    (11, 13, "#98D8C8"), # 左髋-左膝
    (13, 15, "#98D8C8"), # 左膝-左踝
    # 右腿
    (12, 14, "#B8E0D2"), # 右髋-右膝
    (14, 16, "#B8E0D2"), # 右膝-右踝
]

# 关键点颜色（根据部位分组）
KEYPOINT_COLORS = {
    0: "#FF4444",  # 鼻子 - 红色
    1: "#FF6666", 2: "#FF6666",  # 眼睛 - 浅红
    3: "#FFAA00", 4: "#FFAA00",  # 耳朵 - 橙色
    5: "#44FF44", 6: "#44FF44",  # 肩膀 - 绿色
    7: "#00FF88", 8: "#00FF88",  # 肘部 - 青绿
    9: "#00FFFF", 10: "#00FFFF", # 手腕 - 青色
    11: "#4444FF", 12: "#4444FF", # 髋部 - 蓝色
    13: "#8844FF", 14: "#8844FF", # 膝盖 - 紫色
    15: "#FF44FF", 16: "#FF44FF", # 脚踝 - 品红
}


class BodyPartEditor:
    """身体部位编辑器主类"""
    
    def __init__(self, root):
        """
        初始化编辑器
        
        输入：root: tk.Tk - 主窗口
        输出：无
        功能：设置窗口、菜单和画布
        """
        self.root = root
        self.root.title("身体部位数据编辑工具")
        
        # 最大化窗口
        self.root.state('zoomed')
        
        # 数据存储
        self.files = []  # [(json_path, png_path, data, modified), ...]
        self.current_index = 0
        self.current_image = None
        self.photo_image = None
        self.landmarks = []  # 当前文件的landmarks
        self.dragging_point = None  # 正在拖动的点的ID
        self.point_items = {}  # {landmark_id: (oval_id, text_id, source_id)}
        self.line_items = {}  # {(start_id, end_id): line_id} - 骨架线條字典
        self.scale_factor = 1.0  # 图片缩放比例
        self.offset_x = 0  # 图片在画布上的X偏移
        self.offset_y = 0  # 图片在画布上的Y偏移
        self.image_width = 0
        self.image_height = 0
        
        # 撤销历史记录
        self.undo_history = []  # [{file_index: landmarks_copy}, ...]
        self.max_undo_steps = 50  # 最大撤销步数
        self.drag_start_snapshot = None  # 拖动开始时的快照
        
        # 显示模式
        self.show_landmarks = True  # 是否显示关键点
        self.zoom_level = 1.0  # 缩放级别（0.25 - 4.0）
        self.min_zoom = 0.25
        self.max_zoom = 4.0

        # 性能优化相关缓存
        self._image_cache = {}  # {png_path: 解码后的PIL图片}
        self._image_cache_lock = threading.Lock()  # 图片缓存锁（后台预取线程会访问）
        self._photo_cache = {}  # {(png_path, w, h): ImageTk.PhotoImage} - 缩放结果缓存
        self._current_png_path = None  # 当前显示的图片路径（缓存key用）
        self._last_canvas_size = (0, 0)  # 上次画布尺寸（过滤无效Configure事件）
        self._resize_after_id = None  # 窗口变化防抖定时器
        self._hq_redraw_after_id = None  # 高质量重绘防抖定时器

        # 创建界面
        self._create_menu()
        self._create_main_ui()
        
        # 绑定快捷键
        self.root.bind('<Control-s>', self._save_current)
        self.root.bind('<Control-z>', self._undo)
        self.root.bind('<Control-Z>', self._undo)
        self.root.bind('<Left>', self._prev_file)
        self.root.bind('<Right>', self._next_file)
        self.root.bind('<Control-Left>', self._prev_file)
        self.root.bind('<Control-Right>', self._next_file)

    def _create_menu(self):
        """
        创建菜单栏
        
        输入：无
        输出：无
        功能：创建文件菜单（读取文件/文件夹）
        """
        # 菜单字体设置
        menu_font = ('微软雅黑', 12)
        
        menubar = tk.Menu(self.root, font=menu_font)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="读取JSON文件", command=self._open_file, accelerator="")
        file_menu.add_command(label="读取文件夹", command=self._open_folder, accelerator="")
        file_menu.add_separator()
        file_menu.add_command(label="保存", command=lambda: self._save_current(None), accelerator="Ctrl+S")
        file_menu.add_command(label="保存全部", command=self._save_all)
        file_menu.add_separator()
        file_menu.add_command(label="撤销", command=lambda: self._undo(None), accelerator="Ctrl+Z")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0, font=menu_font)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        
    def _create_main_ui(self):
        """
        创建主界面
        
        输入：无
        输出：无
        功能：创建标题、画布、左侧工具栏、底部状态栏
        """
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置按钮样式
        style = ttk.Style()
        style.configure('Large.TButton', font=('微软雅黑', 12))
        style.configure('Tool.TButton', font=('微软雅黑', 11), width=10)
        
        # 顶部标题栏
        self.title_frame = ttk.Frame(main_frame)
        self.title_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(
            self.title_frame, 
            text="请通过菜单读取JSON文件或文件夹", 
            font=('微软雅黑', 20, 'bold')
        )
        self.title_label.pack()
        
        # 修改状态标签
        self.modified_label = ttk.Label(
            self.title_frame,
            text="",
            font=('微软雅黑', 14),
            foreground='red'
        )
        self.modified_label.pack()
        
        # 中间内容区（左侧工具栏 + 右侧画布）
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧工具栏
        self.toolbar_frame = ttk.Frame(content_frame, width=120)
        self.toolbar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.toolbar_frame.pack_propagate(False)  # 保持固定宽度
        
        # 工具栏标题
        ttk.Label(self.toolbar_frame, text="工具栏", font=('微软雅黑', 12, 'bold')).pack(pady=(5, 10))
        
        # 1. 可视化按钮
        self.visibility_btn = ttk.Button(
            self.toolbar_frame, 
            text="👁 隐藏标记",
            command=self._toggle_visibility,
            style='Tool.TButton'
        )
        self.visibility_btn.pack(pady=5, padx=5, fill=tk.X)
        
        # 2. 左右互换按钮
        self.swap_lr_btn = ttk.Button(
            self.toolbar_frame,
            text="⇄ 左右互换",
            command=self._swap_left_right,
            style='Tool.TButton'
        )
        self.swap_lr_btn.pack(pady=5, padx=5, fill=tk.X)
        
        # 3. 缩放控制
        ttk.Separator(self.toolbar_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(self.toolbar_frame, text="缩放控制", font=('微软雅黑', 10)).pack(pady=(0, 5))
        
        self.zoom_in_btn = ttk.Button(
            self.toolbar_frame,
            text="🔍+ 放大",
            command=self._zoom_in,
            style='Tool.TButton'
        )
        self.zoom_in_btn.pack(pady=3, padx=5, fill=tk.X)
        
        self.zoom_out_btn = ttk.Button(
            self.toolbar_frame,
            text="🔍- 缩小",
            command=self._zoom_out,
            style='Tool.TButton'
        )
        self.zoom_out_btn.pack(pady=3, padx=5, fill=tk.X)
        
        self.zoom_reset_btn = ttk.Button(
            self.toolbar_frame,
            text="🔄 重置",
            command=self._zoom_reset,
            style='Tool.TButton'
        )
        self.zoom_reset_btn.pack(pady=3, padx=5, fill=tk.X)
        
        # 缩放级别显示
        self.zoom_label = ttk.Label(self.toolbar_frame, text="100%", font=('微软雅黑', 11))
        self.zoom_label.pack(pady=5)
        
        # 画布框架
        canvas_frame = ttk.Frame(content_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建画布
        self.canvas = tk.Canvas(
            canvas_frame, 
            bg='#2D2D2D',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定画布事件
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<B1-Motion>', self._on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_canvas_release)
        
        # 绑定Ctrl+滚轮缩放
        self.canvas.bind('<Control-MouseWheel>', self._on_mouse_wheel)

        # 只在画布自身尺寸变化时才触发重绘（绑定在root上会收到所有子控件的Configure事件，导致拖动时反复无谓重绘）
        self.canvas.bind('<Configure>', self._on_resize)

        # 底部状态栏
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="未加载文件",
            font=('微软雅黑', 14)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # 导航按钮
        nav_frame = ttk.Frame(self.status_frame)
        nav_frame.pack(side=tk.RIGHT)
        
        self.prev_btn = ttk.Button(nav_frame, text="◀ 上一个", command=lambda: self._prev_file(None), style='Large.TButton')
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.index_label = ttk.Label(nav_frame, text="0 / 0", font=('微软雅黑', 14))
        self.index_label.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = ttk.Button(nav_frame, text="下一个 ▶", command=lambda: self._next_file(None), style='Large.TButton')
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(nav_frame, text="💾 保存", command=lambda: self._save_current(None), style='Large.TButton')
        self.save_btn.pack(side=tk.LEFT, padx=20)
        
    def _open_file(self):
        """
        打开单个JSON文件
        
        输入：无
        输出：无
        功能：让用户选择JSON文件并加载
        """
        filepath = filedialog.askopenfilename(
            title="选择身体部位JSON文件",
            filetypes=[("JSON文件", "*_body.json"), ("所有JSON", "*.json")],
            initialdir="c:/code/erArk/image/立绘"
        )
        
        if filepath:
            self.files = []
            self._load_json_file(filepath)
            self.current_index = 0
            self._display_current()
            
    def _open_folder(self):
        """
        打开文件夹（递归搜索所有_body.json）
        
        输入：无
        输出：无
        功能：递归搜索文件夹内的所有身体数据JSON
        """
        folder = filedialog.askdirectory(
            title="选择包含身体数据的文件夹",
            initialdir="c:/code/erArk/image/立绘"
        )
        
        if folder:
            self.files = []
            self._scan_folder(folder)
            
            if self.files:
                self.current_index = 0
                self._display_current()
                messagebox.showinfo("加载完成", f"共找到 {len(self.files)} 个身体数据文件")
            else:
                messagebox.showwarning("未找到文件", "该文件夹中没有找到 *_body.json 文件")
                
    def _scan_folder(self, folder):
        """
        递归扫描文件夹查找body.json文件
        
        输入：folder: str - 文件夹路径
        输出：无
        功能：递归查找所有*_body.json文件
        """
        for root, dirs, files in os.walk(folder):
            for filename in files:
                if filename.endswith('_body.json'):
                    json_path = os.path.join(root, filename)
                    self._load_json_file(json_path)
                    
    def _load_json_file(self, json_path):
        """
        加载单个JSON文件
        
        输入：json_path: str - JSON文件路径
        输出：无
        功能：读取JSON数据并找到对应的PNG图片
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 查找对应的PNG文件
            folder = os.path.dirname(json_path)
            source_image = data.get('source_image', '')
            
            if source_image:
                png_path = os.path.join(folder, source_image)
            else:
                # 尝试根据JSON文件名推断
                base_name = os.path.basename(json_path).replace('_body.json', '')
                png_path = os.path.join(folder, f"{base_name}_全身.png")
            
            if os.path.exists(png_path):
                self.files.append([json_path, png_path, data, False])  # [json, png, data, modified]
            else:
                print(f"警告: 找不到图片文件 {png_path}")
                
        except Exception as e:
            print(f"加载失败 {json_path}: {e}")
            
    def _display_current(self):
        """
        显示当前文件
        
        输入：无
        输出：无
        功能：在画布上显示图片和部位点
        """
        if not self.files:
            return
            
        json_path, png_path, data, modified = self.files[self.current_index]
        
        # 更新标题
        character_name = data.get('character', os.path.basename(json_path))
        self.title_label.config(text=f"角色：{character_name}")
        
        # 更新修改状态
        if modified:
            self.modified_label.config(text="[已修改，未保存]")
        else:
            self.modified_label.config(text="")
        
        # 更新状态栏
        self.index_label.config(text=f"{self.current_index + 1} / {len(self.files)}")
        self.status_label.config(text=f"文件: {os.path.basename(json_path)}")
        
        # 加载图片（带解码缓存，切回已看过的文件时无需重新解码）
        try:
            self.current_image = self._get_image(png_path)
            self._current_png_path = png_path
            self.image_width = self.current_image.width
            self.image_height = self.current_image.height
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {e}")
            return

        # 获取landmarks（只保留COCO 17个关键点，id 0-16）
        all_landmarks = data.get('landmarks', [])
        self.landmarks = [lm for lm in all_landmarks if lm.get('id', 999) < 17]

        # 重新绘制（首帧用快速缩放保证切换流畅，随后自动补高质量重绘）
        self._redraw(fast=True)

        # 后台预取相邻文件的图片，加速左右切换
        self._prefetch_neighbors()

    def _get_image(self, png_path):
        """
        获取解码后的PIL图片（带缓存）

        输入：png_path: str - 图片路径
        输出：Image.Image - 解码完成的图片对象
        功能：命中缓存直接返回；否则立即解码并放入缓存（后台预取线程也会调用本函数）
        """
        with self._image_cache_lock:
            image = self._image_cache.get(png_path)
        if image is not None:
            return image
        image = Image.open(png_path)
        image.load()  # 立即解码，避免首次缩放时才触发耗时解码
        with self._image_cache_lock:
            self._image_cache[png_path] = image
            # 限制缓存数量，先进先出淘汰（避免大图占用过多内存）
            while len(self._image_cache) > 8:
                oldest = next(iter(self._image_cache))
                if oldest == png_path:
                    break
                self._image_cache.pop(oldest)
        return image

    def _prefetch_neighbors(self):
        """
        后台预取相邻文件的图片

        输入：无
        输出：无
        功能：在后台线程解码上一张/下一张图片，使左右键切换文件时几乎无延迟
        """
        paths = []
        for offset in (1, -1):
            idx = self.current_index + offset
            if 0 <= idx < len(self.files):
                paths.append(self.files[idx][1])
        if not paths:
            return

        def work():
            for path in paths:
                try:
                    self._get_image(path)
                except Exception:
                    pass

        threading.Thread(target=work, daemon=True).start()

    def _redraw(self, fast=False):
        """
        重新绘制画布内容

        输入：fast: bool - 是否使用快速缩放（低质量插值，空闲后自动补一次高质量重绘）
        输出：无
        功能：清空画布并重新绘制图片、骨架和关键点；缩放结果带缓存，避免重复的高开销缩放
        """
        if not self.current_image:
            return

        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 10 or canvas_height < 10:
            # 画布还没准备好
            self.root.after(100, self._redraw)
            return

        # 计算缩放比例（保持纵横比）
        scale_x = (canvas_width - 40) / self.image_width
        scale_y = (canvas_height - 40) / self.image_height
        base_scale = min(scale_x, scale_y, 1.0)  # 基础缩放（不放大，只缩小）

        # 应用用户缩放级别
        self.scale_factor = base_scale * self.zoom_level

        # 计算缩放后的尺寸
        scaled_width = max(1, int(self.image_width * self.scale_factor))
        scaled_height = max(1, int(self.image_height * self.scale_factor))

        # 计算居中偏移
        self.offset_x = (canvas_width - scaled_width) // 2
        self.offset_y = (canvas_height - scaled_height) // 2

        # 优先命中缩放结果缓存，避免每次重绘都做高开销的图片缩放
        cache_key = (self._current_png_path, scaled_width, scaled_height)
        photo = self._photo_cache.get(cache_key)
        if photo is None:
            # 快速模式用BILINEAR保证交互流畅，稍后再补一次高质量重绘；reducing_gap可显著加速大图缩小
            resample = Image.Resampling.BILINEAR if fast else Image.Resampling.LANCZOS
            scaled_image = self.current_image.resize((scaled_width, scaled_height), resample, reducing_gap=2.0)
            photo = ImageTk.PhotoImage(scaled_image)
            if fast:
                self._schedule_hq_redraw()
            else:
                self._photo_cache[cache_key] = photo
                # 限制缓存数量，先进先出淘汰
                while len(self._photo_cache) > 12:
                    self._photo_cache.pop(next(iter(self._photo_cache)))
        self.photo_image = photo

        # 清空画布并绘制图片
        self.canvas.delete('all')
        self.canvas.create_image(
            self.offset_x, self.offset_y,
            anchor=tk.NW,
            image=self.photo_image
        )

        # 绘制骨架线和关键点覆盖层
        self._redraw_overlay(clear=False)

    def _redraw_overlay(self, clear=True):
        """
        重新绘制关键点与骨架覆盖层（不重绘底图）

        输入：clear: bool - 是否先清除已有覆盖层元素
        输出：无
        功能：只删除并重建点/线/文字元素，跳过图片缩放，用于切换显示、撤销、左右互换等操作
        """
        if clear:
            self.canvas.delete('overlay')
        self.point_items = {}
        self.line_items = {}

        # 根据可视化模式决定是否绘制骨架线和关键点
        if self.show_landmarks:
            self._draw_skeleton()
            self._draw_keypoints()

    def _schedule_hq_redraw(self):
        """
        延迟调度一次高质量重绘（防抖）

        输入：无
        输出：无
        功能：连续缩放等快速交互结束约200ms后，用LANCZOS补绘一次清晰的底图
        """
        if self._hq_redraw_after_id is not None:
            self.root.after_cancel(self._hq_redraw_after_id)
        self._hq_redraw_after_id = self.root.after(200, self._do_hq_redraw)

    def _do_hq_redraw(self):
        """
        执行高质量重绘

        输入：无
        输出：无
        """
        self._hq_redraw_after_id = None
        self._redraw(fast=False)

    def _draw_skeleton(self):
        """
        绘制骨架连线
        
        输入：无
        输出：无
        功能：根据关键点位置绘制骨架
        """
        if not self.landmarks:
            return
            
        # 建立ID到landmark的映射
        landmark_map = {lm['id']: lm for lm in self.landmarks}
        
        for start_id, end_id, color in SKELETON_CONNECTIONS:
            if start_id in landmark_map and end_id in landmark_map:
                start = landmark_map[start_id]
                end = landmark_map[end_id]
                
                # 转换为画布坐标
                x1 = self.offset_x + start['x'] * self.image_width * self.scale_factor
                y1 = self.offset_y + start['y'] * self.image_height * self.scale_factor
                x2 = self.offset_x + end['x'] * self.image_width * self.scale_factor
                y2 = self.offset_y + end['y'] * self.image_height * self.scale_factor
                
                line_id = self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=color,
                    width=3,
                    tags=('overlay', f'skeleton_{start_id}_{end_id}')
                )
                self.line_items[(start_id, end_id)] = line_id
                
    def _draw_keypoints(self):
        """
        绘制关键点
        
        输入：无
        输出：无
        功能：绘制可拖动的关键点圆圈和标签
        """
        if not self.landmarks:
            return
            
        point_radius = 8
        
        for landmark in self.landmarks:
            lm_id = landmark['id']
            name = landmark.get('name', COCO_KEYPOINTS[lm_id] if lm_id < len(COCO_KEYPOINTS) else f'point_{lm_id}')
            cn_name = KEYPOINT_NAMES_CN.get(name, name)
            color = KEYPOINT_COLORS.get(lm_id, '#FFFFFF')
            
            # 转换为画布坐标
            x = self.offset_x + landmark['x'] * self.image_width * self.scale_factor
            y = self.offset_y + landmark['y'] * self.image_height * self.scale_factor
            
            # 绘制圆圈
            oval_id = self.canvas.create_oval(
                x - point_radius, y - point_radius,
                x + point_radius, y + point_radius,
                fill=color,
                outline='white',
                width=2,
                tags=('overlay', f'point_{lm_id}')
            )
            
            # 绘制标签
            # 根据位置决定标签方向
            text_offset_x = 15
            text_offset_y = -5
            anchor = tk.W
            
            # 如果点在右侧，标签放左边
            if landmark['x'] > 0.7:
                text_offset_x = -15
                anchor = tk.E
                
            text_id = self.canvas.create_text(
                x + text_offset_x, y + text_offset_y,
                text=cn_name,
                fill='white',
                font=('微软雅黑', 11),
                anchor=anchor,
                tags=('overlay', f'label_{lm_id}')
            )
            
            # 添加来源模型标记
            source = landmark.get('source_model', '?')
            source_id = self.canvas.create_text(
                x, y + point_radius + 10,
                text=f'[{source}]',
                fill='#888888',
                font=('Consolas', 10),
                tags=('overlay', f'source_{lm_id}')
            )
            
            self.point_items[lm_id] = (oval_id, text_id, source_id)
            
    def _on_canvas_click(self, event):
        """
        画布点击事件
        
        输入：event: tk.Event - 点击事件
        输出：无
        功能：检测是否点击了某个关键点
        """
        # 隐藏模式下不允许拖动
        if not self.show_landmarks:
            return
            
        # 检查是否点击了关键点
        for lm_id, (oval_id, text_id, source_id) in self.point_items.items():
            coords = self.canvas.coords(oval_id)
            if coords:
                x1, y1, x2, y2 = coords
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.dragging_point = lm_id
                    # 拖动开始时保存快照（用于撤销）
                    self.drag_start_snapshot = copy.deepcopy(self.landmarks)
                    return
                    
        self.dragging_point = None
        self.drag_start_snapshot = None
        
    def _on_canvas_drag(self, event):
        """
        画布拖动事件
        
        输入：event: tk.Event - 拖动事件
        输出：无
        功能：拖动选中的关键点（优化：只更新相关元素而非完全重绘）
        """
        if self.dragging_point is None:
            return
            
        # 限制在图片范围内
        img_x = (event.x - self.offset_x) / self.scale_factor
        img_y = (event.y - self.offset_y) / self.scale_factor
        
        img_x = max(0, min(self.image_width, img_x))
        img_y = max(0, min(self.image_height, img_y))
        
        # 计算画布坐标
        canvas_x = self.offset_x + img_x * self.scale_factor
        canvas_y = self.offset_y + img_y * self.scale_factor
        
        # 更新landmark数据
        for landmark in self.landmarks:
            if landmark['id'] == self.dragging_point:
                landmark['x'] = img_x / self.image_width
                landmark['y'] = img_y / self.image_height
                break
                
        # 标记为已修改
        if not self.files[self.current_index][3]:
            self.files[self.current_index][3] = True
            self.modified_label.config(text="[已修改，未保存]")
                
        # 优化：只更新被拖动的点和相关连线的位置，而非完全重绘
        self._update_point_position(self.dragging_point, canvas_x, canvas_y)
    
    def _update_point_position(self, lm_id, canvas_x, canvas_y):
        """
        更新单个关键点的位置（不重绘整个画布）
        
        输入：
            lm_id: int - 关键点ID
            canvas_x: float - 画布X坐标
            canvas_y: float - 画布Y坐标
        输出：无
        """
        point_radius = 8
        
        # 更新圆点和标签位置
        if lm_id in self.point_items:
            oval_id, text_id, source_id = self.point_items[lm_id]
            
            # 更新圆点
            self.canvas.coords(
                oval_id,
                canvas_x - point_radius, canvas_y - point_radius,
                canvas_x + point_radius, canvas_y + point_radius
            )
            
            # 获取landmark数据来决定标签位置
            landmark = None
            for lm in self.landmarks:
                if lm['id'] == lm_id:
                    landmark = lm
                    break
            
            if landmark:
                text_offset_x = 15 if landmark['x'] <= 0.7 else -15
                text_offset_y = -5
                anchor = tk.W if landmark['x'] <= 0.7 else tk.E
                
                # 更新标签位置
                self.canvas.coords(text_id, canvas_x + text_offset_x, canvas_y + text_offset_y)
                self.canvas.itemconfig(text_id, anchor=anchor)
                
                # 更新来源标记位置
                self.canvas.coords(source_id, canvas_x, canvas_y + point_radius + 10)
        
        # 更新相关的骨架线
        self._update_skeleton_lines(lm_id)
        
    def _update_skeleton_lines(self, lm_id):
        """
        更新与指定关键点相关的骨架线
        
        输入：lm_id: int - 关键点ID
        输出：无
        """
        # 建立ID到landmark的映射
        landmark_map = {lm['id']: lm for lm in self.landmarks}
        
        # 找到与该点相关的连线并更新
        for start_id, end_id, color in SKELETON_CONNECTIONS:
            if start_id == lm_id or end_id == lm_id:
                if start_id in landmark_map and end_id in landmark_map:
                    start = landmark_map[start_id]
                    end = landmark_map[end_id]
                    
                    x1 = self.offset_x + start['x'] * self.image_width * self.scale_factor
                    y1 = self.offset_y + start['y'] * self.image_height * self.scale_factor
                    x2 = self.offset_x + end['x'] * self.image_width * self.scale_factor
                    y2 = self.offset_y + end['y'] * self.image_height * self.scale_factor
                    
                    # 使用字典key查找对应的连线
                    line_key = (start_id, end_id)
                    if line_key in self.line_items:
                        self.canvas.coords(self.line_items[line_key], x1, y1, x2, y2)
    
    def _on_canvas_release(self, event):
        """
        画布释放事件
        
        输入：event: tk.Event - 释放事件
        输出：无
        功能：结束拖动，将拖动前的快照保存到历史记录
        """
        # 如果确实进行了拖动操作，保存快照到历史
        if self.dragging_point is not None and self.drag_start_snapshot is not None:
            # 检查是否真的有变化
            has_change = False
            for orig, curr in zip(self.drag_start_snapshot, self.landmarks):
                if orig['id'] == self.dragging_point:
                    if abs(orig['x'] - curr['x']) > 0.0001 or abs(orig['y'] - curr['y']) > 0.0001:
                        has_change = True
                        break
            
            if has_change:
                # 保存拖动前的状态到历史
                self.undo_history.append({
                    'file_index': self.current_index,
                    'landmarks': self.drag_start_snapshot
                })
                # 限制历史记录数量
                if len(self.undo_history) > self.max_undo_steps:
                    self.undo_history.pop(0)
        
        self.dragging_point = None
        self.drag_start_snapshot = None
        
    def _on_resize(self, event):
        """
        画布大小变化事件

        输入：event: tk.Event - 大小变化事件
        输出：无
        功能：画布尺寸真正变化时才延迟重绘，避免其他Configure事件引发无谓的全量重绘
        """
        new_size = (event.width, event.height)
        if new_size == self._last_canvas_size:
            return
        self._last_canvas_size = new_size
        if self.current_image:
            # 使用after防抖，避免拖动窗口边框时频繁重绘
            if self._resize_after_id is not None:
                self.root.after_cancel(self._resize_after_id)
            self._resize_after_id = self.root.after(100, self._do_resize_redraw)

    def _do_resize_redraw(self):
        """
        执行窗口大小变化后的重绘

        输入：无
        输出：无
        """
        self._resize_after_id = None
        self._redraw()
    
    def _undo(self, event):
        """
        撤销操作
        
        输入：event: tk.Event - 键盘事件（可为None）
        输出：无
        功能：恢复到上一步的状态
        """
        if not self.undo_history:
            return
            
        # 弹出最近的历史记录
        history = self.undo_history.pop()
        file_index = history['file_index']
        old_landmarks = history['landmarks']

        # 恢复数据（同时更新files列表中的data，保持内存数据一致）
        data = self.files[file_index][2]
        all_landmarks = data.get('landmarks', [])
        # 替换COCO 17点，保留其他点（如果有）
        other_landmarks = [lm for lm in all_landmarks if lm.get('id', 999) >= 17]
        restored = copy.deepcopy(old_landmarks)
        data['landmarks'] = restored + other_landmarks

        # 如果是当前文件的历史记录
        if file_index == self.current_index:
            # 直接恢复 landmarks，只重绘覆盖层（底图不变）
            self.landmarks = restored
            self._redraw_overlay()
        else:
            # 是其他文件的历史记录，切换到该文件并恢复
            self.current_index = file_index
            self._display_current()
        
        # 检查是否还有未保存的修改
        # （如果撤销后与原始数据一致，可以取消修改标记）
        # 这里简化处理，保持修改标记
    
    def _toggle_visibility(self):
        """
        切换关键点可视化模式
        
        输入：无
        输出：无
        功能：显示/隐藏身体部位标记点
        """
        self.show_landmarks = not self.show_landmarks
        
        # 更新按钮文本
        if self.show_landmarks:
            self.visibility_btn.config(text="👁 隐藏标记")
        else:
            self.visibility_btn.config(text="👁 显示标记")

        # 只重绘覆盖层，底图无需重新缩放
        if self.photo_image:
            self._redraw_overlay()
        else:
            self._redraw()
    
    def _swap_left_right(self):
        """
        左右互换
        
        输入：无
        输出：无
        功能：交换所有左右对称的部位点位置
        """
        if not self.landmarks:
            return
        
        # 保存撤销快照
        self.undo_history.append({
            'file_index': self.current_index,
            'landmarks': copy.deepcopy(self.landmarks)
        })
        if len(self.undo_history) > self.max_undo_steps:
            self.undo_history.pop(0)
        
        # 左右对应关系 (left_id, right_id)
        lr_pairs = [
            (1, 2),   # left_eye <-> right_eye
            (3, 4),   # left_ear <-> right_ear
            (5, 6),   # left_shoulder <-> right_shoulder
            (7, 8),   # left_elbow <-> right_elbow
            (9, 10),  # left_wrist <-> right_wrist
            (11, 12), # left_hip <-> right_hip
            (13, 14), # left_knee <-> right_knee
            (15, 16), # left_ankle <-> right_ankle
        ]
        
        # 建立ID到landmark的映射
        landmark_map = {lm['id']: lm for lm in self.landmarks}
        
        # 交换位置
        for left_id, right_id in lr_pairs:
            if left_id in landmark_map and right_id in landmark_map:
                left_lm = landmark_map[left_id]
                right_lm = landmark_map[right_id]
                
                # 交换x, y坐标
                left_lm['x'], right_lm['x'] = right_lm['x'], left_lm['x']
                left_lm['y'], right_lm['y'] = right_lm['y'], left_lm['y']
                
                # 标记为手动修改
                left_lm['source_model'] = 'Z'
                right_lm['source_model'] = 'Z'
        
        # 标记为已修改
        self.files[self.current_index][3] = True
        self.modified_label.config(text="[已修改，未保存]")

        # 只重绘覆盖层，底图无需重新缩放
        self._redraw_overlay()
    
    def _zoom_in(self):
        """
        放大
        
        输入：无
        输出：无
        """
        if self.zoom_level < self.max_zoom:
            self.zoom_level = min(self.zoom_level * 1.25, self.max_zoom)
            self._update_zoom_label()
            # 快速模式：连续缩放时保持流畅，停止后自动补高质量重绘
            self._redraw(fast=True)

    def _zoom_out(self):
        """
        缩小
        
        输入：无
        输出：无
        """
        if self.zoom_level > self.min_zoom:
            self.zoom_level = max(self.zoom_level / 1.25, self.min_zoom)
            self._update_zoom_label()
            # 快速模式：连续缩放时保持流畅，停止后自动补高质量重绘
            self._redraw(fast=True)
    
    def _zoom_reset(self):
        """
        重置缩放
        
        输入：无
        输出：无
        """
        self.zoom_level = 1.0
        self._update_zoom_label()
        self._redraw()
    
    def _update_zoom_label(self):
        """
        更新缩放级别显示
        
        输入：无
        输出：无
        """
        percent = int(self.zoom_level * 100)
        self.zoom_label.config(text=f"{percent}%")
    
    def _on_mouse_wheel(self, event):
        """
        鼠标滚轮缩放（Ctrl+滚轮）
        
        输入：event: tk.Event - 滚轮事件
        输出：无
        功能：放大或缩小显示
        """
        if event.delta > 0:
            self._zoom_in()
        else:
            self._zoom_out()
            
    def _prev_file(self, event):
        """
        切换到上一个文件
        
        输入：event: tk.Event - 键盘事件（可为None）
        输出：无
        """
        if self.files and self.current_index > 0:
            self.current_index -= 1
            self._display_current()
            
    def _next_file(self, event):
        """
        切换到下一个文件
        
        输入：event: tk.Event - 键盘事件（可为None）
        输出：无
        """
        if self.files and self.current_index < len(self.files) - 1:
            self.current_index += 1
            self._display_current()
            
    def _save_current(self, event):
        """
        保存当前文件
        
        输入：event: tk.Event - 键盘事件（可为None）
        输出：无
        功能：将修改后的数据写入JSON文件
        """
        if not self.files:
            return
            
        json_path, png_path, data, modified = self.files[self.current_index]
        
        # 更新landmarks数据
        # 将手动修改的点的source_model标记为"Z"
        for landmark in self.landmarks:
            # 检查是否有变化（与原数据对比）
            orig_landmarks = data.get('landmarks', [])
            for orig in orig_landmarks:
                if orig['id'] == landmark['id']:
                    if abs(orig['x'] - landmark['x']) > 0.0001 or abs(orig['y'] - landmark['y']) > 0.0001:
                        landmark['source_model'] = 'Z'  # 标记为手动修改
                    break
                    
        # 更新数据（保留id>=17的其他点）
        other_landmarks = [lm for lm in data.get('landmarks', []) if lm.get('id', 999) >= 17]
        data['landmarks'] = self.landmarks + other_landmarks

        # 写入文件
        if self._write_file(self.current_index):
            self.modified_label.config(text="[已保存]")
            # 2秒后清除保存提示
            self.root.after(2000, lambda: self.modified_label.config(text="") if not self.files[self.current_index][3] else None)

    def _write_file(self, index):
        """
        将指定文件的数据写入磁盘

        输入：index: int - 文件索引
        输出：bool - 是否写入成功
        功能：只做JSON写入与状态更新，不触发图片加载和重绘
        """
        entry = self.files[index]
        json_path = entry[0]
        data = entry[2]
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            entry[3] = False
            return True
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存文件 {os.path.basename(json_path)}: {e}")
            return False

    def _save_all(self):
        """
        保存所有已修改的文件

        输入：无
        输出：无
        功能：直接写入所有已修改文件，不逐个切换显示（避免每个文件都触发图片解码和重绘）
        """
        # 当前文件的编辑数据先同步回data
        if self.files and self.landmarks:
            data = self.files[self.current_index][2]
            other_landmarks = [lm for lm in data.get('landmarks', []) if lm.get('id', 999) >= 17]
            data['landmarks'] = self.landmarks + other_landmarks

        saved_count = 0
        for i in range(len(self.files)):
            if self.files[i][3]:
                if self._write_file(i):
                    saved_count += 1

        # 刷新当前文件的修改状态显示
        if self.files and not self.files[self.current_index][3]:
            self.modified_label.config(text="")
        messagebox.showinfo("保存完成", f"已保存 {saved_count} 个文件")
        
    def _show_help(self):
        """
        显示帮助信息
        
        输入：无
        输出：无
        """
        help_text = """身体部位数据编辑工具 - 使用说明

【基本操作】
• 文件 → 读取JSON文件：打开单个*_body.json文件
• 文件 → 读取文件夹：递归加载文件夹内所有*_body.json

【编辑操作】
• 点击并拖动圆点：修改该部位的位置
• 修改后的点在保存时会被标记为来源"Z"

【快捷键】
• Ctrl+S：保存当前文件
• ← / → 方向键：切换上一个/下一个文件

【显示说明】
• 彩色圆点：身体部位关键点
• 圆点下方[X]：该点的来源模型（A-G为自动识别，Z为手动修改）
• 彩色连线：骨架结构

【颜色含义】
• 红色系：头部（鼻子、眼睛、耳朵）
• 绿色系：上肢（肩膀、肘部、手腕）
• 蓝紫色系：下肢（髋部、膝盖、脚踝）
"""
        messagebox.showinfo("使用说明", help_text)


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置DPI感知（Windows高分屏支持）
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = BodyPartEditor(root)
    root.mainloop()


if __name__ == '__main__':
    main()
