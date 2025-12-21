# -*- coding: UTF-8 -*-
"""
Mod管理器模块
负责mod的加载、管理和函数替换
"""
import os
import sys
import json
import importlib
import traceback
from typing import Dict, List, Any, Callable, Optional
from Script.Core import cache_control, game_type

# mod相关的全局变量
_mod_folder = "mod"
_mod_config_file = "mod_config.json"
_loaded_mods: Dict[str, 'ModInfo'] = {}
_original_functions: Dict[str, Callable] = {}  # 保存被替换的原函数
_mod_functions: Dict[str, Callable] = {}  # mod注册的新函数
_mod_assets: Dict[str, str] = {}  # mod素材路径映射


class ModInfo: 
    """Mod信息类"""
    def __init__(self, mod_id: str, info_dict: dict, mod_path: str):
        self.mod_id = mod_id
        self.name = info_dict. get("name", mod_id)
        self.version = info_dict.get("version", "1.0.0")
        self.author = info_dict.get("author", "未知")
        self.description = info_dict.get("description", "")
        self.game_version = info_dict. get("game_version", "")
        self.dependencies = info_dict. get("dependencies", [])
        self.incompatible = info_dict.get("incompatible", [])
        self.load_priority = info_dict.get("load_priority", 100)
        self.scripts = info_dict.get("scripts", [])
        self.assets = info_dict.get("assets", {})
        self.mod_path = mod_path
        self. enabled = False
        self.loaded = False
        self.error_message = ""


class ModManager: 
    """Mod管理器单例类"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self. mod_folder = _mod_folder
        self.mods: Dict[str, ModInfo] = {}
        self. enabled_mods: List[str] = []
        self.load_order: List[str] = []
        
    def get_mod_folder_path(self) -> str:
        """获取mod文件夹的绝对路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的exe环境
            base_path = os. path.dirname(sys.executable)
        else:
            # 开发环境
            base_path = os.path. dirname(os.path.dirname(os.path. dirname(os.path. abspath(__file__))))
        return os.path.join(base_path, self.mod_folder)
    
    def scan_mods(self) -> List[ModInfo]: 
        """扫描mod文件夹，获取所有mod信息"""
        mod_path = self.get_mod_folder_path()
        if not os.path.exists(mod_path):
            os.makedirs(mod_path)
            return []
        
        self.mods. clear()
        
        for item in os.listdir(mod_path):
            item_path = os.path. join(mod_path, item)
            if not os.path.isdir(item_path):
                continue
            
            info_file = os. path.join(item_path, "mod_info.json")
            if not os.path.exists(info_file):
                continue
            
            try:
                with open(info_file, "r", encoding="utf-8") as f:
                    info_dict = json. load(f)
                mod_id = info_dict.get("mod_id", item)
                mod_info = ModInfo(mod_id, info_dict, item_path)
                self. mods[mod_id] = mod_info
            except Exception as e:
                print(f"[Mod] 读取mod信息失败: {item}, 错误: {e}")
        
        # 加载配置文件中的启用状态和顺序
        self._load_mod_config()
        
        return list(self.mods.values())
    
    def _load_mod_config(self):
        """加载mod配置文件"""
        config_path = os.path.join(self.get_mod_folder_path(), _mod_config_file)
        if not os.path. exists(config_path):
            return
        
        try: 
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            self.enabled_mods = config.get("enabled_mods", [])
            self.load_order = config.get("load_order", [])
            
            # 更新mod的启用状态
            for mod_id in self.enabled_mods:
                if mod_id in self.mods:
                    self.mods[mod_id].enabled = True
        except Exception as e: 
            print(f"[Mod] 加载mod配置失败:  {e}")
    
    def save_mod_config(self):
        """保存mod配置文件"""
        config_path = os.path.join(self.get_mod_folder_path(), _mod_config_file)
        config = {
            "enabled_mods":  self.enabled_mods,
            "load_order": self.load_order
        }
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e: 
            print(f"[Mod] 保存mod配置失败: {e}")
    
    def enable_mod(self, mod_id: str) -> bool:
        """启用mod"""
        if mod_id not in self.mods:
            return False
        if mod_id in self. enabled_mods: 
            return True
        
        self.enabled_mods.append(mod_id)
        self.mods[mod_id].enabled = True
        
        if mod_id not in self. load_order: 
            self.load_order.append(mod_id)
        
        self.save_mod_config()
        return True
    
    def disable_mod(self, mod_id: str) -> bool:
        """禁用mod"""
        if mod_id not in self.mods:
            return False
        if mod_id not in self.enabled_mods:
            return True
        
        self.enabled_mods.remove(mod_id)
        self.mods[mod_id].enabled = False
        self.save_mod_config()
        return True
    
    def set_load_order(self, order: List[str]):
        """设置mod加载顺序"""
        self.load_order = order
        self.save_mod_config()
    
    def move_mod_up(self, mod_id: str) -> bool:
        """将mod在加载顺序中上移"""
        if mod_id not in self. load_order:
            return False
        index = self.load_order.index(mod_id)
        if index == 0:
            return False
        self.load_order[index], self.load_order[index - 1] = self.load_order[index - 1], self.load_order[index]
        self.save_mod_config()
        return True
    
    def move_mod_down(self, mod_id: str) -> bool:
        """将mod在加载顺序中下移"""
        if mod_id not in self.load_order:
            return False
        index = self.load_order.index(mod_id)
        if index == len(self.load_order) - 1:
            return False
        self.load_order[index], self.load_order[index + 1] = self.load_order[index + 1], self.load_order[index]
        self.save_mod_config()
        return True
    
    def get_sorted_enabled_mods(self) -> List[ModInfo]:
        """获取按加载顺序排序的已启用mod列表"""
        result = []
        # 先按load_order排序
        for mod_id in self.load_order:
            if mod_id in self.enabled_mods and mod_id in self.mods:
                result.append(self.mods[mod_id])
        # 再添加不在load_order中但已启用的mod
        for mod_id in self.enabled_mods:
            if mod_id not in self.load_order and mod_id in self.mods:
                result. append(self.mods[mod_id])
        return result
    
    def load_all_enabled_mods(self) -> Dict[str, str]:
        """
        加载所有已启用的mod
        返回:  {mod_id:  error_message} 加载失败的mod及错误信息
        """
        errors = {}
        sorted_mods = self.get_sorted_enabled_mods()
        
        for mod_info in sorted_mods:
            try: 
                self._load_single_mod(mod_info)
                mod_info.loaded = True
                print(f"[Mod] 成功加载: {mod_info.name} v{mod_info. version}")
            except Exception as e: 
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                mod_info.error_message = error_msg
                errors[mod_info.mod_id] = error_msg
                print(f"[Mod] 加载失败: {mod_info.name}, 错误: {e}")
        
        return errors
    
    def _load_single_mod(self, mod_info:  ModInfo):
        """加载单个mod"""
        # 1. 加载素材
        self._load_mod_assets(mod_info)
        
        # 2. 加载脚本
        for script_config in mod_info. scripts:
            self._load_mod_script(mod_info, script_config)
    
    def _load_mod_assets(self, mod_info: ModInfo):
        """加载mod素材"""
        global _mod_assets
        
        assets = mod_info.assets
        
        # 加载数据文件
        data_assets = assets.get("data", [])
        for data_config in data_assets: 
            file_path = os.path.join(mod_info.mod_path, data_config["file"])
            if os.path.exists(file_path):
                alias = f"mod:{mod_info.mod_id}/{data_config['file']}"
                _mod_assets[alias] = file_path
                # 根据merge_mode处理数据合并
                self._merge_data_file(data_config, file_path)
        
        # 加载图片素材
        image_assets = assets.get("image", [])
        for image_config in image_assets:
            file_path = os.path.join(mod_info.mod_path, image_config["file"])
            if os.path.exists(file_path):
                alias = image_config. get("alias", f"mod:{mod_info.mod_id}/{image_config['file']}")
                _mod_assets[alias] = file_path
    
    def _merge_data_file(self, data_config: dict, file_path: str):
        """合并数据文件到游戏配置"""
        import csv
        from Script.Config import game_config
        
        merge_mode = data_config.get("merge_mode", "append")
        target_config = data_config.get("target_config", "")
        
        if not target_config: 
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # 根据target_config找到对应的配置数据
            if hasattr(game_config, f"config_{target_config}"):
                config_dict = getattr(game_config, f"config_{target_config}")
                for row in rows:
                    if "cid" in row: 
                        cid = row["cid"]
                        if merge_mode == "append":
                            config_dict[cid] = row
                        elif merge_mode == "replace": 
                            config_dict[cid] = row
                        elif merge_mode == "merge":
                            if cid in config_dict:
                                config_dict[cid].update(row)
                            else:
                                config_dict[cid] = row
        except Exception as e: 
            print(f"[Mod] 合并数据文件失败:  {file_path}, 错误: {e}")
    
    def _load_mod_script(self, mod_info: ModInfo, script_config:  dict):
        """加载mod脚本文件"""
        script_file = script_config. get("file", "")
        script_path = os. path.join(mod_info.mod_path, script_file)
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"脚本文件不存在: {script_path}")
        
        # 读取脚本内容
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f. read()
        
        # 创建mod的执行命名空间
        mod_namespace = self._create_mod_namespace(mod_info)
        
        # 执行脚本
        try: 
            exec(compile(script_content, script_path, 'exec'), mod_namespace)
        except Exception as e: 
            raise RuntimeError(f"执行脚本失败: {script_file}, 错误:  {e}")
        
        # 处理函数定义
        functions = script_config. get("functions", [])
        for func_config in functions: 
            self._register_function(mod_info, mod_namespace, func_config)
    
    def _create_mod_namespace(self, mod_info:  ModInfo) -> dict:
        """创建mod脚本的执行命名空间"""
        import random  # 导入random供mod使用
        
        namespace = {
            "__builtins__": __builtins__,
            "__name__": f"mod_{mod_info.mod_id}",
            "__file__": mod_info.mod_path,
            # 提供常用的游戏模块引用
            "cache": cache_control. cache,
            "game_type": game_type,
            "random": random,  # 新增：提供random模块
            # 提供mod专用的工具函数
            "get_mod_asset":  lambda alias: get_mod_asset_path(mod_info. mod_id, alias),
            "get_original_function": lambda module, func: get_original_function(module, func),
            "call_original": lambda module, func, *args, **kwargs: call_original_function(module, func, *args, **kwargs),
        }
        
        # 动态导入常用模块
        try:
            from Script.Config import game_config, normal_config
            from Script.Core import constant, get_text
            namespace["game_config"] = game_config
            namespace["normal_config"] = normal_config
            namespace["constant"] = constant
            namespace["_"] = get_text._
        except Exception:
            pass
        
        return namespace
    
    def _register_function(self, mod_info: ModInfo, namespace: dict, func_config: dict):
        """注册mod函数"""
        global _original_functions, _mod_functions
        
        func_name = func_config.get("name", "")
        func_type = func_config.get("type", "new")
        
        if func_name not in namespace:
            raise ValueError(f"函数未在脚本中定义: {func_name}")
        
        mod_func = namespace[func_name]
        
        if func_type == "replace":
            # 替换现有函数
            target_module = func_config.get("target_module", "").strip().replace(" ", "")
            target_function = func_config.get("target_function", func_name).strip()
            
            try:
                module = self._import_module(target_module)
                if hasattr(module, target_function):
                    # 保存原函数（只有第一次替换时保存）
                    key = f"{target_module}.{target_function}"
                    if key not in _original_functions:
                        _original_functions[key] = getattr(module, target_function)
                    
                    # 替换为mod函数
                    setattr(module, target_function, mod_func)
                    print(f"[Mod] 替换函数: {key}")
                else:
                    raise AttributeError(f"目标函数不存在: {target_module}.{target_function}")
            except Exception as e:
                raise RuntimeError(f"替换函数失败: {target_module}.{target_function}, 错误: {e}")
        
        elif func_type == "new":
            # 注册新函数
            register_to = func_config.get("register_to", "").strip().replace(" ", "")
            key = f"{register_to}.{func_name}" if register_to else func_name
            _mod_functions[key] = mod_func
            
            # 如果指定了注册模块，则将函数添加到该模块
            if register_to:
                try:
                    module = self._import_module(register_to)
                    setattr(module, func_name, mod_func)
                    print(f"[Mod] 注册新函数: {key}")
                except Exception as e:
                    print(f"[Mod] 注册函数到模块失败: {key}, 错误: {e}")
    
    def _import_module(self, module_path: str):
        """动态导入模块"""
        # 清理模块路径中可能的空格
        clean_path = module_path.strip().replace(" ", "")
        return importlib.import_module(clean_path)


# 便捷函数
def get_mod_manager() -> ModManager: 
    """获取Mod管理器实例"""
    return ModManager()


def get_mod_asset_path(mod_id: str, alias: str) -> Optional[str]:
    """
    获取mod素材的实际路径
    
    参数: 
        mod_id: 当前mod的ID
        alias: 素材别名，格式为 "mod:mod_id/path/to/file"
    
    返回:
        素材的实际文件路径
    """
    if alias.startswith("mod:"):
        # 解析别名，去掉 "mod:" 前缀并处理可能的空格
        path_part = alias[4:].strip()
        parts = path_part.split("/", 1)
        if len(parts) == 2:
            target_mod_id = parts[0].strip()
            relative_path = parts[1]
            
            manager = get_mod_manager()
            if target_mod_id in manager.mods:
                mod_path = manager.mods[target_mod_id].mod_path
                full_path = os.path.join(mod_path, relative_path)
                if os.path.exists(full_path):
                    return full_path
    
    return None


def get_original_function(module_path: str, function_name: str) -> Optional[Callable]: 
    """
    获取被替换的原函数
    
    参数:
        module_path: 模块路径
        function_name:  函数名
    
    返回:
        原函数，如果未被替换则返回None
    """
    key = f"{module_path}.{function_name}"
    return _original_functions. get(key, None)


def call_original_function(module_path: str, function_name: str, *args, **kwargs):
    """
    调用被替换的原函数
    
    参数:
        module_path: 模块路径
        function_name:  函数名
        *args, **kwargs: 传递给原函数的参数
    
    返回: 
        原函数的返回值
    """
    original = get_original_function(module_path, function_name)
    if original is None:
        raise ValueError(f"原函数未找到: {module_path}.{function_name}")
    return original(*args, **kwargs)


def get_mod_function(key: str) -> Optional[Callable]: 
    """获取mod注册的函数"""
    return _mod_functions.get(key, None)


def init_mod_system():
    """初始化mod系统"""
    manager = get_mod_manager()
    manager.scan_mods()
    errors = manager.load_all_enabled_mods()
    
    if errors: 
        print("[Mod] 以下mod加载失败:")
        for mod_id, error in errors.items():
            print(f"  - {mod_id}: {error}")
    
    return len(errors) == 0