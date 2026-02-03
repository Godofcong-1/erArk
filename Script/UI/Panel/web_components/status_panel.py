# -*- coding: utf-8 -*-
"""
状态面板组件
负责处理Web模式下的角色状态信息显示
"""

from typing import Dict, List, Optional
from Script.Core import cache_control, game_type, get_text
from Script.Design import attr_text, handle_premise, attr_calculation
from Script.Config import game_config
from Script.UI.Panel import character_info_head

cache: game_type.Cache = cache_control.cache
_: callable = get_text._


class StatusPanel:
    """
    状态面板管理器
    负责获取和格式化角色状态信息
    """

    def __init__(self):
        """初始化状态面板管理器"""
        pass

    def get_player_info(self) -> dict:
        """
        获取玩家信息
        
        Returns:
        dict -- 玩家信息数据
        """
        pl_data: game_type.Character = cache.character_data.get(0)
        if not pl_data:
            return self._get_empty_player_info()
        
        # 检查是否有理智药和精力剂
        has_sanity_drug = False
        for item_id in [0, 1, 2, 3]:  # 理智药剂ID
            if pl_data.item.get(item_id, 0) > 0:
                has_sanity_drug = True
                break
        
        has_semen_drug = pl_data.item.get(11, 0) > 0  # 精力剂ID为11
        
        return {
            "name": pl_data.name,
            "nick_name": pl_data.nick_name if hasattr(pl_data, 'nick_name') else "",
            "hp": pl_data.hit_point,
            "hp_max": pl_data.hit_point_max,
            "mp": pl_data.mana_point,
            "mp_max": pl_data.mana_point_max,
            "sanity": getattr(pl_data, 'sanity_point', 0),
            "sanity_max": getattr(pl_data, 'sanity_point_max', 100),
            "semen": self._get_semen_value(pl_data),
            "semen_max": self._get_semen_max_value(pl_data),
            "special_states": self._get_special_states(0),
            "has_sanity_drug": has_sanity_drug,
            "has_semen_drug": has_semen_drug
        }

    def _get_empty_player_info(self) -> dict:
        """获取空的玩家信息结构"""
        return {
            "name": "",
            "nick_name": "",
            "hp": 0,
            "hp_max": 100,
            "mp": 0,
            "mp_max": 100,
            "sanity": 0,
            "sanity_max": 100,
            "semen": 0,
            "semen_max": 100,
            "special_states": [],
            "has_sanity_drug": False,
            "has_semen_drug": False
        }

    def get_target_info(self, character_id: int) -> dict:
        """
        获取交互对象信息
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        dict -- 交互对象信息数据
        """
        char_data: game_type.Character = cache.character_data.get(character_id)
        if not char_data:
            return self._get_empty_target_info()
        
        return {
            "id": character_id,
            "name": char_data.name,
            "favorability": self._get_favorability(char_data),
            "trust": self._get_trust(char_data),
            "hp": char_data.hit_point,
            "hp_max": char_data.hit_point_max,
            "mp": char_data.mana_point,
            "mp_max": char_data.mana_point_max,
            "special_states": self._get_special_states(character_id),
            "pleasure_states": self._get_pleasure_states(character_id),
            "other_states": self._get_other_states(character_id),
            "value_changes": self._get_value_changes(character_id)
        }

    def _get_empty_target_info(self) -> dict:
        """获取空的交互对象信息结构"""
        return {
            "id": -1,
            "name": "",
            "favorability": {"value": 0, "level": ""},
            "trust": {"value": 0, "level": ""},
            "hp": 0,
            "hp_max": 100,
            "mp": 0,
            "mp_max": 100,
            "special_states": [],
            "pleasure_states": [],
            "other_states": [],
            "value_changes": []
        }

    def _get_semen_value(self, char_data: game_type.Character) -> int:
        """获取精液值"""
        try:
            return char_data.semen_point
        except AttributeError:
            return 0

    def _get_semen_max_value(self, char_data: game_type.Character) -> int:
        """获取精液最大值"""
        try:
            return char_data.semen_point_max
        except AttributeError:
            return 100

    def _get_favorability(self, char_data: game_type.Character) -> dict:
        """
        获取好感度信息
        
        Returns:
        dict -- 包含数值和等级的好感度信息
        """
        try:
            favorability_value = char_data.favorability.get(0, 0)
            # 计算好感度等级
            level = self._calculate_favorability_level(favorability_value)
            return {"value": favorability_value, "level": level}
        except (AttributeError, KeyError):
            return {"value": 0, "level": ""}

    def _get_trust(self, char_data: game_type.Character) -> dict:
        """
        获取信赖度信息
        
        Returns:
        dict -- 包含数值和等级的信赖度信息
        """
        try:
            trust_value = char_data.trust
            # 计算信赖度等级
            level = self._calculate_trust_level(trust_value)
            return {"value": trust_value, "level": level}
        except AttributeError:
            return {"value": 0, "level": ""}

    def _calculate_favorability_level(self, value: int) -> str:
        """计算好感度等级"""
        if value >= 10000:
            return "S"
        elif value >= 5000:
            return "A"
        elif value >= 2000:
            return "B"
        elif value >= 500:
            return "C"
        elif value >= 0:
            return "D"
        else:
            return "E"

    def _calculate_trust_level(self, value: float) -> str:
        """计算信赖度等级"""
        if value >= 200:
            return "S"
        elif value >= 150:
            return "A"
        elif value >= 100:
            return "B"
        elif value >= 50:
            return "C"
        elif value >= 0:
            return "D"
        else:
            return "E"

    def _get_special_states(self, character_id: int) -> List[dict]:
        """
        获取角色特殊状态标记
        使用 character_info_head.py 中的 get_character_status_list 函数
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        List[dict] -- 特殊状态标记列表，每个元素包含 text 和 style
        """
        states = []
        char_data: game_type.Character = cache.character_data.get(character_id)
        if not char_data:
            return states
        
        # 使用已实现的函数获取状态列表
        status_list, status_text_list = character_info_head.get_character_status_list(character_id)
        
        # 转换为Web可用的格式
        for draw_obj, text in zip(status_list, status_text_list):
            if text:  # 只添加非空的状态
                state_info = {
                    "text": text,
                    "style": getattr(draw_obj, 'style', 'standard'),
                    "tooltip": getattr(draw_obj, 'tooltip', '')
                }
                states.append(state_info)
        
        return states

    def _get_pleasure_states(self, character_id: int) -> List[dict]:
        """
        获取角色快感状态（状态类型0）
        参考 see_character_info_panel.py 的 SeeCharacterStatusPanel 类
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        List[dict] -- 快感状态列表，每个元素包含 name, value, max_value, level
        """
        states = []
        char_data: game_type.Character = cache.character_data.get(character_id)
        if not char_data:
            return states
        
        # 获取状态类型0（快感状态）的所有状态ID
        pleasure_type_id = 0
        if pleasure_type_id not in game_config.config_character_state_type_data:
            return states
        
        status_ids = game_config.config_character_state_type_data[pleasure_type_id]
        
        # 润滑状态也归到快感里（ID=8）
        additional_ids = [8]
        
        for status_id in status_ids:
            state_info = self._get_status_info(char_data, status_id)
            if state_info:
                states.append(state_info)
        
        # 添加润滑状态
        for status_id in additional_ids:
            state_info = self._get_status_info(char_data, status_id)
            if state_info:
                states.append(state_info)
        
        return states
    
    def _get_status_info(self, char_data: game_type.Character, status_id: int) -> Optional[dict]:
        """
        获取单个状态的信息
        
        Keyword arguments:
        char_data -- 角色数据
        status_id -- 状态ID
        
        Returns:
        Optional[dict] -- 状态信息，如果应跳过则返回 None
        """
        # 性别过滤
        if status_id in {2, 4, 7} and char_data.sex == 0:  # 阴蒂、阴道、子宫 - 男性跳过
            return None
        if status_id == 3 and char_data.sex == 1:  # 阴茎 - 女性跳过
            return None
        
        # 获取状态配置
        if status_id not in game_config.config_character_state:
            return None
        
        state_config = game_config.config_character_state[status_id]
        status_text = state_config.name
        
        # 计算状态数值和等级
        status_value = 0
        if hasattr(char_data, 'status_data') and status_id in char_data.status_data:
            status_value = char_data.status_data[status_id]
        status_value = round(status_value)
        status_level = attr_calculation.get_status_level(status_value)
        
        # 计算当前等级的最大值
        if status_level in game_config.config_character_state_level:
            max_value = game_config.config_character_state_level[status_level].max_value
        else:
            max_value = 100
        
        return {
            "id": status_id,
            "name": status_text,
            "value": status_value,
            "max_value": max_value,
            "level": status_level,
            "tooltip": state_config.info if hasattr(state_config, 'info') else ""
        }

    def _get_other_states(self, character_id: int) -> List[dict]:
        """
        获取角色其他状态（状态类型1，排除润滑）
        参考 see_character_info_panel.py 的 SeeCharacterStatusPanel 类
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        List[dict] -- 其他状态列表，每个元素包含 name, value, max_value, level
        """
        states = []
        char_data: game_type.Character = cache.character_data.get(character_id)
        if not char_data:
            return states
        
        # 获取状态类型1（其他状态）的所有状态ID
        other_type_id = 1
        if other_type_id not in game_config.config_character_state_type_data:
            return states
        
        status_ids = game_config.config_character_state_type_data[other_type_id]
        
        # 排除润滑（已归到快感里）
        excluded_ids = {8}
        
        for status_id in status_ids:
            if status_id in excluded_ids:
                continue
            state_info = self._get_status_info(char_data, status_id)
            if state_info:
                states.append(state_info)
        
        return states

    def get_target_extra_info(self, character_id: int) -> dict:
        """
        获取交互对象的附加信息（服装、身体、群交、隐奸）
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        dict -- 附加信息数据，包含各栏位的可见性和展开状态
        """
        from Script.Design import handle_premise
        
        # 获取各栏位的展开状态（用于控制内容是否显示）
        clothing_expanded = cache.scene_panel_show[1] if hasattr(cache, 'scene_panel_show') else True
        body_expanded = cache.scene_panel_show[2] if hasattr(cache, 'scene_panel_show') else True
        show_detailed_dirty = cache.all_system_setting.draw_setting[10] if hasattr(cache, 'all_system_setting') else False
        show_all_body_parts = cache.all_system_setting.draw_setting.get(18, 0) if hasattr(cache, 'all_system_setting') else False
        
        # 群交模式判定
        group_sex_visible = cache.group_sex_mode if hasattr(cache, 'group_sex_mode') else False
        
        # 隐奸模式判定
        hidden_sex_visible = handle_premise.handle_hidden_sex_mode_ge_1(0) if character_id else False
        
        # 是否在H中
        is_h_mode = handle_premise.handle_is_h(0)
        
        # 服装和身体栏位始终显示按钮（visible=True），仅用expanded控制内容是否展开
        # 群交和隐奸栏位根据模式判定是否显示
        return {
            "clothing": {
                "visible": True,  # 按钮始终显示
                "expanded": clothing_expanded,  # 内容是否展开
                "data": self._get_clothing_info(character_id) if clothing_expanded and character_id else {}
            },
            "body": {
                "visible": True,  # 按钮始终显示
                "expanded": body_expanded,  # 内容是否展开
                "data": self._get_body_info(character_id) if body_expanded and character_id else {}
            },
            "group_sex": {
                "visible": group_sex_visible,
                "expanded": group_sex_visible,
                "data": self._get_group_sex_info() if group_sex_visible else {}
            },
            "hidden_sex": {
                "visible": hidden_sex_visible,
                "expanded": hidden_sex_visible,
                "data": self._get_hidden_sex_info() if hidden_sex_visible else {}
            },
            "show_detailed_dirty": show_detailed_dirty,
            "show_all_body_parts": show_all_body_parts,
            "is_h_mode": is_h_mode
        }

    def _get_clothing_info(self, character_id: int) -> dict:
        """
        获取服装信息
        参考 Script/UI/Panel/cloth_panel.py 的 SeeCharacterClothPanel 逻辑
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        dict -- 服装信息数据
        """
        from Script.Design import attr_calculation
        
        if not character_id or character_id not in cache.character_data:
            return {"items": [], "naked": True, "off_items": []}
        
        pl_data = cache.character_data.get(0)
        target_data = cache.character_data.get(character_id)
        if not pl_data or not target_data:
            return {"items": [], "naked": True, "off_items": []}
        
        items = []
        off_items = []
        show_detailed = cache.all_system_setting.draw_setting[10] if hasattr(cache, 'all_system_setting') else False
        
        # 遍历全部衣服类型
        for clothing_type in game_config.config_clothing_type:
            type_name = game_config.config_clothing_type[clothing_type].name
            
            # 当该类型里有衣服存在的时候才显示
            if len(target_data.cloth.cloth_wear[clothing_type]):
                # 胸部和内裤的特殊显示逻辑
                if clothing_type in {6, 9} and not cache.debug_mode:
                    # 透视能力或没穿外层衣服时可见
                    if (
                        (pl_data.pl_ability.visual and pl_data.talent[307])
                        or len(target_data.cloth.cloth_wear[clothing_type - 1]) == 0
                    ):
                        target_data.cloth.cloth_see[clothing_type] = True
                    else:
                        target_data.cloth.cloth_see[clothing_type] = False
                    if not target_data.cloth.cloth_see[clothing_type]:
                        continue
                
                # 获取该类型下的所有衣服
                for cloth_id in target_data.cloth.cloth_wear[clothing_type]:
                    cloth_name = game_config.config_clothing_tem[cloth_id].name
                    cloth_item = {
                        "id": cloth_id,
                        "type": clothing_type,
                        "type_name": type_name,
                        "name": cloth_name,
                        "is_worn": True,
                        "dirty_text": ""
                    }
                    
                    # 精液污浊显示
                    if len(target_data.dirty.cloth_semen) == 0:
                        empty_dirty_data = attr_calculation.get_dirty_reset(target_data.dirty)
                        target_data.dirty.cloth_semen = empty_dirty_data.cloth_semen
                    
                    if target_data.dirty.cloth_semen[clothing_type][1] != 0:
                        semen_level = target_data.dirty.cloth_semen[clothing_type][2]
                        dirty_text_cid = f"{_(type_name, revert_translation=True)}精液污浊{str(semen_level)}"
                        if show_detailed:
                            dirty_text = game_config.ui_text_data.get('dirty_full', {}).get(dirty_text_cid, "")
                        else:
                            dirty_text = game_config.ui_text_data.get('dirty', {}).get(dirty_text_cid, "")
                        cloth_item["dirty_text"] = dirty_text
                    
                    items.append(cloth_item)
            
            # 真空显示
            if clothing_type in {6, 9} and not len(target_data.cloth.cloth_wear[clothing_type]):
                if not cache.debug_mode:
                    if not target_data.cloth.cloth_see.get(clothing_type, False):
                        continue
                items.append({
                    "id": -1,
                    "type": clothing_type,
                    "type_name": type_name,
                    "name": _("真空"),
                    "is_worn": True,
                    "is_vacuum": True,
                    "dirty_text": ""
                })
        
        # 检查是否全裸
        naked = True
        for clothing_type in game_config.config_clothing_type:
            if len(target_data.cloth.cloth_wear[clothing_type]):
                naked = False
                break
        
        # 获取脱下的衣服（仅在H中显示）
        from Script.Design import handle_premise
        if handle_premise.handle_is_h(0):
            for cloth_type in target_data.cloth.cloth_off:
                for cloth_id in target_data.cloth.cloth_off[cloth_type]:
                    cloth_name = game_config.config_clothing_tem[cloth_id].name
                    type_name = game_config.config_clothing_type[cloth_type].name
                    off_items.append({
                        "id": cloth_id,
                        "type": cloth_type,
                        "type_name": type_name,
                        "name": cloth_name,
                        "is_worn": False
                    })
        
        return {
            "items": items,
            "naked": naked,
            "off_items": off_items
        }

    def _get_body_info(self, character_id: int) -> dict:
        """
        获取身体信息
        参考 Script/UI/Panel/dirty_panel.py 的 SeeCharacterBodyPanel 逻辑
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        dict -- 身体信息数据
        """
        from Script.Design import clothing, handle_premise
        
        if not character_id or character_id not in cache.character_data:
            return {"parts": []}
        
        pl_data = cache.character_data.get(0)
        target_data = cache.character_data.get(character_id)
        if not pl_data or not target_data:
            return {"parts": []}
        
        parts = []
        show_detailed = cache.all_system_setting.draw_setting[10] if hasattr(cache, 'all_system_setting') else False
        
        # 获取没有穿服装的部位列表
        no_cloth_body_list = clothing.get_exposed_body_parts(character_id)
        
        # 是否透视中
        visual_flag = 0
        if pl_data.pl_ability.visual:
            if pl_data.talent[309]:
                visual_flag = 3  # 生理透视
            elif pl_data.talent[308]:
                visual_flag = 2  # 腔内透视
            else:
                visual_flag = 1  # 服装透视
        
        # 腹部整体精液量统计
        abdomen_all_semen = 0
        
        # 遍历全部位
        for i in range(len(game_config.config_body_part)):
            body_part_data = game_config.config_body_part[i]
            part_name = body_part_data.name
            
            # 检查脏污数据
            if len(target_data.dirty.body_semen) <= i:
                target_data.dirty.body_semen[i] = [part_name, 0, 0, 0]
            
            # 累计腹部精液量
            if i in [5, 7, 8, 15]:
                abdomen_all_semen += target_data.dirty.body_semen[i][1]
            
            # 判定部位是否被衣服遮挡
            if i not in no_cloth_body_list and visual_flag == 0:
                continue
            
            # 腔内透视判定
            if visual_flag <= 1 and i in {7, 9, 15}:
                continue
            
            part_info = {
                "id": i,
                "name": part_name,
                "texts": []
            }
            
            # 爱液文本
            if i == 6 and target_data.status_data[8]:
                level = attr_calculation.get_status_level(target_data.status_data[8])
                if level <= 2:
                    text_index = "爱液1"
                elif level <= 4:
                    text_index = "爱液2"
                elif level <= 6:
                    text_index = "爱液3"
                else:
                    text_index = "爱液4"
                if show_detailed:
                    text = game_config.ui_text_data.get('dirty_full', {}).get(text_index, "")
                else:
                    text = game_config.ui_text_data.get('dirty', {}).get(text_index, "")
                if text:
                    part_info["texts"].append({"type": "love_juice", "text": text})
            
            # 处子血判定
            if i == 6 and visual_flag >= 2:
                if not target_data.talent[0] and handle_premise.handle_first_sex_in_today(character_id):
                    dirty_text_cid = "破处血1"
                    if show_detailed:
                        text = game_config.ui_text_data.get('dirty_full', {}).get(dirty_text_cid, "")
                    else:
                        text = game_config.ui_text_data.get('dirty', {}).get(dirty_text_cid, "")
                    if text:
                        part_info["texts"].append({"type": "virgin_blood", "text": text})
            
            # 精液污浊判定
            if target_data.dirty.body_semen[i][2]:
                semen_level = target_data.dirty.body_semen[i][2]
                dirty_text_cid = f"{_(part_name, revert_translation=True)}精液污浊{str(semen_level)}"
                if show_detailed:
                    text = game_config.ui_text_data.get('dirty_full', {}).get(dirty_text_cid, "")
                else:
                    text = game_config.ui_text_data.get('dirty', {}).get(dirty_text_cid, "")
                if text:
                    part_info["texts"].append({"type": "semen", "text": text})
            
            if part_info["texts"]:
                parts.append(part_info)
        
        # 其他信息
        extra_info = []
        
        # 腹部整体精液
        if abdomen_all_semen:
            now_level = attr_calculation.get_semen_now_level(abdomen_all_semen, 20, 0)
            if now_level >= 2:
                dirty_text_cid = f"腹部整体精液污浊{str(now_level)}"
                if show_detailed:
                    text = game_config.ui_text_data.get('dirty_full', {}).get(dirty_text_cid, "")
                else:
                    text = game_config.ui_text_data.get('dirty', {}).get(dirty_text_cid, "")
                if text:
                    extra_info.append({"type": "abdomen_semen", "text": text})
        
        # 阴茎位置文本
        if target_data.h_state.insert_position != -1:
            now_position_index = target_data.h_state.insert_position
            position_text_cid = f"阴茎位置{str(now_position_index)}"
            insert_position_text = game_config.ui_text_data.get('h_state', {}).get(position_text_cid, "")
            
            sex_position_index = pl_data.h_state.current_sex_position
            if now_position_index in {6, 7, 8, 9} and sex_position_index != -1:
                sex_position_text_cid = f"体位{str(sex_position_index)}"
                sex_position_text = game_config.ui_text_data.get('h_state', {}).get(sex_position_text_cid, "")
                insert_text = _("以{0}").format(sex_position_text) + insert_position_text
            else:
                insert_text = insert_position_text
            if insert_text:
                extra_info.append({"type": "insert_position", "text": insert_text})
        
        # 绳子捆绑
        if target_data.h_state.bondage:
            bondage_id = target_data.h_state.bondage
            bondage_name = game_config.config_bondage[bondage_id].name
            bondage_text = _("被绳子捆成了{0}").format(bondage_name)
            extra_info.append({"type": "bondage", "text": bondage_text})
        
        # H道具
        body_item_dict = target_data.h_state.body_item
        sex_toy_level = target_data.sp_flag.sex_toy_level
        if sex_toy_level == 0:
            sex_toy_lv_text = _("(关)")
        elif sex_toy_level == 1:
            sex_toy_lv_text = _("(弱)")
        elif sex_toy_level == 2:
            sex_toy_lv_text = _("(中)")
        else:
            sex_toy_lv_text = _("(强)")
        
        h_items = []
        for i in range(len(body_item_dict)):
            if body_item_dict[i][1]:
                body_item_data = game_config.config_body_item[i]
                status_text = body_item_dict[i][0]
                if body_item_data.type == 2:
                    status_text += sex_toy_lv_text
                h_items.append(status_text)
        if h_items:
            extra_info.append({"type": "h_items", "items": h_items})
        
        return {
            "parts": parts,
            "extra_info": extra_info
        }

    def _get_group_sex_info(self) -> dict:
        """
        获取群交信息
        参考 Script/System/Sex_System/group_sex_panel.py 的 SeeGroupSexInfoPanel 逻辑
        
        Returns:
        dict -- 群交信息数据
        """
        if not cache.group_sex_mode:
            return {"active": False, "body_parts": []}
        
        pl_data = cache.character_data.get(0)
        if not pl_data:
            return {"active": False, "body_parts": []}
        
        now_template_data = pl_data.h_state.group_sex_body_template_dict.get("A", {})
        if not now_template_data:
            return {"active": False, "body_parts": []}
        
        body_parts = []
        body_part_name_dict = {
            "mouth": _("嘴"),
            "L_hand": _("左手"),
            "R_hand": _("右手"),
            "penis": _("阴茎"),
            "anal": _("肛门"),
        }
        
        # 对单遍历各部位
        if isinstance(now_template_data, list) and len(now_template_data) > 0:
            for body_part, (target_chara_id, state_id) in now_template_data[0].items():
                if state_id != -1:
                    target_chara_name = cache.character_data.get(target_chara_id, {})
                    if hasattr(target_chara_name, 'name'):
                        target_chara_name = target_chara_name.name
                    else:
                        target_chara_name = ""
                    state_name = game_config.config_behavior.get(state_id, {})
                    if hasattr(state_name, 'name'):
                        state_name = state_name.name
                    else:
                        state_name = ""
                    body_part_name = body_part_name_dict.get(body_part, body_part)
                    body_parts.append({
                        "part": body_part,
                        "part_name": body_part_name,
                        "target_name": target_chara_name,
                        "action_name": state_name
                    })
            
            # 对多（侍奉）
            if len(now_template_data) > 1:
                target_chara_id_list, state_id = now_template_data[1]
                if state_id != -1 and -1 not in target_chara_id_list:
                    target_names = []
                    for tid in target_chara_id_list:
                        tc = cache.character_data.get(tid, {})
                        if hasattr(tc, 'name'):
                            target_names.append(tc.name)
                    state_name = game_config.config_behavior.get(state_id, {})
                    if hasattr(state_name, 'name'):
                        state_name = state_name.name
                    else:
                        state_name = ""
                    body_parts.append({
                        "part": "wait_upon",
                        "part_name": _("侍奉"),
                        "target_names": target_names,
                        "action_name": state_name
                    })
        
        return {
            "active": True,
            "player_name": pl_data.name,
            "body_parts": body_parts
        }

    def _get_hidden_sex_info(self) -> dict:
        """
        获取隐奸信息
        参考 Script/System/Sex_System/hidden_sex_panel.py 的 See_Hidden_Sex_InfoPanel 逻辑
        
        Returns:
        dict -- 隐奸信息数据
        """
        from Script.Design import handle_premise
        from Script.UI.Panel import dirty_panel
        
        if not handle_premise.handle_hidden_sex_mode_ge_1(0):
            return {"active": False}
        
        pl_data = cache.character_data.get(0)
        if not pl_data:
            return {"active": False}
        
        # 隐蔽程度
        now_degree = pl_data.h_state.hidden_sex_discovery_dregree
        
        # 获取隐蔽等级
        hidden_level = 0
        hidden_text = ""
        for now_cid in game_config.config_hidden_level:
            now_data = game_config.config_hidden_level[now_cid]
            if now_degree > now_data.hidden_point:
                continue
            else:
                hidden_level = now_cid
                hidden_text = now_data.name
                break
        if not hidden_text:
            hidden_level = 3
            hidden_text = game_config.config_hidden_level.get(3, {})
            if hasattr(hidden_text, 'name'):
                hidden_text = hidden_text.name
            else:
                hidden_text = ""
        
        result = {
            "active": True,
            "hidden_level": hidden_level,
            "hidden_text": hidden_text,
            "hidden_degree": now_degree
        }
        
        # 阴茎位置文本
        insert_chara_id = dirty_panel.get_inserted_character_id()
        if insert_chara_id != 0:
            insert_character_data = cache.character_data.get(insert_chara_id)
            if insert_character_data:
                chara_name = insert_character_data.name
                now_position_index = insert_character_data.h_state.insert_position
                position_text_cid = f"阴茎位置{str(now_position_index)}"
                insert_position_text = game_config.ui_text_data.get('h_state', {}).get(position_text_cid, "")
                
                sex_position_index = pl_data.h_state.current_sex_position
                if now_position_index in {6, 7, 8, 9} and sex_position_index != -1:
                    sex_position_text_cid = f"体位{str(sex_position_index)}"
                    sex_position_text = game_config.ui_text_data.get('h_state', {}).get(sex_position_text_cid, "")
                    insert_text = _("悄悄地以{0}对{1}").format(sex_position_text, chara_name) + insert_position_text
                else:
                    insert_text = _("{0}正在偷偷给你").format(chara_name) + insert_position_text
                result["insert_text"] = insert_text
        
        return result

    def _get_value_changes(self, character_id: int) -> list:
        """
        获取数值变化列表，用于浮动文本显示
        获取后会清空该角色的变化数据，确保每次变化只显示一次
        只返回最近2秒内的变化，避免显示过时数据
        
        Keyword arguments:
        character_id -- 角色ID
        
        Returns:
        list -- 该角色相关的数值变化列表
        """
        import time
        
        if not hasattr(cache, 'web_value_changes') or not cache.web_value_changes:
            return []
        
        current_time = time.time()
        
        # 筛选与当前角色相关的变化，且只取最近2秒内的
        changes = [
            change for change in cache.web_value_changes
            if change.get('character_id') == character_id 
            and (current_time - change.get('timestamp', 0)) < 2.0
        ]
        
        # 从缓存中移除已获取的变化，避免重复显示
        if changes:
            cache.web_value_changes = [
                change for change in cache.web_value_changes
                if change.get('character_id') != character_id
            ]
        
        # 清理超过5秒的旧数据
        cache.web_value_changes = [
            change for change in cache.web_value_changes
            if (current_time - change.get('timestamp', 0)) < 5.0
        ]
        
        return changes
