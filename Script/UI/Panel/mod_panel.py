# -*- coding: UTF-8 -*-
"""
Mod管理面板
在标题界面显示的mod管理界面
"""
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, py_cmd
from Script.Core.mod_manager import get_mod_manager, ModInfo
from Script.UI.Moudle import draw
from Script.Config import normal_config

_: FunctionType = get_text._
cache: game_type.Cache = cache_control.cache
config_normal = normal_config.config_normal


class ModManagePanel:
    """Mod管理面板"""
    
    def __init__(self, width: int):
        """
        初始化面板
        
        参数:
            width: 面板宽度
        """
        self.width = width
        self.mod_manager = get_mod_manager()
        self.current_page = 0
        self.page_size = 10
        self.selected_mod_id = None
    
    def draw(self):
        """绘制面板"""
        self.mod_manager.scan_mods()  # 刷新mod列表
        
        while True:
            py_cmd.clr_cmd()
            
            # 标题
            title_draw = draw.TitleLineDraw(_("模组管理"), self.width)
            title_draw.draw()

            # 提示用户安装mod的风险
            hint_draw = draw.NormalDraw()
            hint_draw.text = _("○模组中的代码会直接在游戏中执行，请只安装你信赖的模组，避免使用了带有病毒木马等有害代码的模组而出现损失\n○使用模组时需检查适用版本，避免与游戏版本不兼容，导致游戏崩溃或异常\n○启用或禁用模组后需要重启游戏才能生效\n")
            hint_draw.width = self.width
            hint_draw.draw()
            
            line_feed = draw.NormalDraw()
            line_feed.text = "\n"
            line_feed.width = 1
            line_feed.draw()
            
            # 显示mod列表
            return_list = []
            mods = list(self.mod_manager.mods.values())
            
            if not mods:
                info_draw = draw.CenterDraw()
                info_draw.text = _("未找到任何模组\n请将模组放入游戏目录下的mod文件夹中")
                info_draw.width = self.width
                info_draw.draw()
                line_feed.draw()
            else:
                # 分页显示
                start_idx = self.current_page * self.page_size
                end_idx = min(start_idx + self.page_size, len(mods))
                page_mods = mods[start_idx:end_idx]
                
                # 表头
                header_text = _("   状态   |  名称                       |  版本    |  作者")
                header_draw = draw.NormalDraw()
                header_draw.text = header_text + "\n"
                header_draw.width = self.width
                header_draw.draw()
                
                line = draw.LineDraw("-", self.width)
                line.draw()
                
                # mod列表
                for i, mod in enumerate(page_mods):
                    idx = start_idx + i
                    status = _("[启用]") if mod.enabled else _("[禁用]")
                    status_style = "gold_enrod" if mod.enabled else "standard"
                    
                    # 创建可点击的按钮
                    button_text = f"  {status}  |  {mod.name[: 20]: <20}  | {mod.version:<8} |  {mod.author[:10]}"
                    button = draw.LeftButton(
                        button_text,
                        str(idx),
                        self.width,
                        normal_style=status_style,
                        cmd_func=self._select_mod,
                        args=(mod.mod_id,)
                    )
                    button.draw()
                    line_feed.draw()
                    return_list.append(str(idx))
                
                # 分页信息
                total_pages = (len(mods) + self.page_size - 1) // self.page_size
                page_info = draw.CenterDraw()
                page_info.text = _("\n第 {0} / {1} 页").format(self.current_page + 1, total_pages)
                page_info.width = self.width
                page_info.draw()
                line_feed.draw()
            
            # 操作按钮
            line = draw.LineDraw("=", self.width)
            line.draw()
            
            button_list = []
            
            if len(mods) > self.page_size:
                if self.current_page > 0:
                    prev_btn = draw.CenterButton(_("[上一页]"), "prev", self.width // 6)
                    button_list.append(prev_btn)
                    return_list.append("prev")
                
                total_pages = (len(mods) + self.page_size - 1) // self.page_size
                if self.current_page < total_pages - 1:
                    next_btn = draw.CenterButton(_("[下一页]"), "next", self.width // 6)
                    button_list.append(next_btn)
                    return_list.append("next")
            
            refresh_btn = draw.CenterButton(_("[刷新列表]"), "refresh", self.width // 6)
            button_list.append(refresh_btn)
            return_list.append("refresh")
            
            back_btn = draw.CenterButton(_("[返回]"), "back", self.width // 6)
            button_list.append(back_btn)
            return_list.append("back")
            
            for btn in button_list:
                btn.draw()
            line_feed.draw()
            
            # 等待输入
            ans = flow_handle.askfor_all(return_list)
            
            if ans == "back":
                break
            elif ans == "prev":
                self.current_page = max(0, self.current_page - 1)
            elif ans == "next":
                total_pages = (len(mods) + self.page_size - 1) // self.page_size
                self.current_page = min(total_pages - 1, self.current_page + 1)
            elif ans == "refresh":
                self.mod_manager.scan_mods()
            elif ans.isdigit():
                idx = int(ans)
                if 0 <= idx < len(mods):
                    self._show_mod_detail(mods[idx])
    
    def _select_mod(self, mod_id: str):
        """选择mod"""
        self.selected_mod_id = mod_id
    
    def _show_mod_detail(self, mod: ModInfo):
        """显示mod详情"""
        while True:
            py_cmd.clr_cmd()
            
            # 标题
            title_draw = draw.TitleLineDraw(mod.name, self.width)
            title_draw.draw()
            
            line_feed = draw.NormalDraw()
            line_feed.text = "\n"
            line_feed.width = 1
            
            # mod信息
            info_lines = [
                _("ID: {0}").format(mod.mod_id),
                _("版本: {0}").format(mod.version),
                _("作者: {0}").format(mod.author),
                _("适用游戏版本: {0}").format(mod.game_version or _('未指定')),
                _("状态: {0}").format(_('已启用') if mod.enabled else _('已禁用')),
                _("加载状态: {0}").format(_('已加载') if mod.loaded else _('未加载')),
                "",
                _("描述:"),
                mod.description or _("无描述"),
            ]
            if mod.error_message:
                info_lines.extend(["", _("错误信息:"), mod.error_message[: 200]])
            
            for line in info_lines:
                info_draw = draw.NormalDraw()
                info_draw.text = line + "\n"
                info_draw.width = self.width
                info_draw.draw()
            
            line_feed.draw()
            
            # 操作按钮
            line = draw.LineDraw("=", self.width)
            line.draw()
            
            return_list = []
            
            if mod.enabled:
                disable_btn = draw.CenterButton(_("[禁用模组]"), "toggle", self.width // 5)
                disable_btn.draw()
            else:
                enable_btn = draw.CenterButton(_("[启用模组]"), "toggle", self.width // 5)
                enable_btn.draw()
            return_list.append("toggle")
            
            # 加载顺序调整
            up_btn = draw.CenterButton(_("[上移优先级]"), "up", self.width // 5)
            up_btn.draw()
            return_list.append("up")
            
            down_btn = draw.CenterButton(_("[下移优先级]"), "down", self.width // 5)
            down_btn.draw()
            return_list.append("down")
            
            back_btn = draw.CenterButton(_("[返回]"), "back", self.width // 5)
            back_btn.draw()
            return_list.append("back")
            
            ans = flow_handle.askfor_all(return_list)
            
            if ans == "back":
                break
            elif ans == "toggle":
                if mod.enabled:
                    self.mod_manager.disable_mod(mod.mod_id)
                    mod.enabled = False
                    info_text_str = _("\n\n已禁用模组【{0}】，将在重启游戏后生效。\n\n").format(mod.name)
                else:
                    self.mod_manager.enable_mod(mod.mod_id)
                    mod.enabled = True
                    info_text_str = _("\n\n已启用模组【{0}】，将在重启游戏后生效。\n\n").format(mod.name)
                # 输出提示提醒要重启游戏后生效
                info_draw = draw.WaitDraw()
                info_draw.text = info_text_str
                info_draw.width = self.width
                info_draw.draw()
            elif ans == "up":
                self.mod_manager.move_mod_up(mod.mod_id)
            elif ans == "down":
                self.mod_manager.move_mod_down(mod.mod_id)
