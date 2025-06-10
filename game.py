#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
import logging
import time
from types import FunctionType

if __name__ == "__main__":

    import auto_build_config
    from Script.Config import normal_config
    from Script.Core import game_type, cache_control

    # log输出等级
    # logging.basicConfig(format='等级：%(levelname)s，函数名：%(funcName)s，信息为：%(message)s', level = logging.DEBUG)
    logging.basicConfig(format='等级：%(levelname)s，函数名：%(funcName)s，信息为：%(message)s', level = logging.INFO)

    # 初始化游戏缓存数据
    cache_control.cache = game_type.Cache()
    # 初始化游戏基础配置数据
    normal_config.init_normal_config()

    from Script.Core import get_text
    from Script.Config import game_config, name_config, character_config

    _: FunctionType = get_text._
    """ 翻译api """

    # 载入游戏配置
    game_config.init()
    # 读取Web模式标志
    now_web_mode = normal_config.config_normal.web_draw
    cache_control.cache.web_mode = now_web_mode
    # 载入姓名配置，暂时去掉
    # name_config.init_name_data()
    # 初始化角色人物卡数据
    character_config.init_character_tem_data()

    # 载入地图数据
    from Script.Config import map_config
    map_config.init_map_data()

    from Script.Design import start_flow, character_handle, game_time
    import Script.Settle
    import Script.StateMachine
    from Script.Core import flow_handle, game_init, io_init
    import Script.UI.Flow

    # 载入角色人物卡数据
    character_handle.init_character_tem()

    # 初始化游戏时间
    game_time.init_time()
    

    # 判定是否需要使用Web模式
    if now_web_mode:
        import Script.UI.Flow
        
        print("正在初始化Web服务器...")
        
        # 导入Web服务器模块和Web版IO适配器
        # 注意：web_server模块中的eventlet已经在导入时根据需要执行了monkey_patch
        from Script.Core.web_server import start_server, stop_server, server_port
        import Script.Core.io_web as io
        
        # 导入Web绘制适配器并应用到所有绘制类
        from Script.UI import web_draw_adapter
        
        # 应用Web绘制适配器到所有绘制类
        web_draw_adapter.apply_web_adapters()
        
        # 替换game_init中的io_init引用
        game_init.io_init = io
        # 初始化当前绘制元素列表
        cache_control.cache.current_draw_elements = []
        
        print("正在启动游戏Web服务器...")
        
        # 启动Web服务器（现在会返回实际使用的端口）
        try:
            active_port = start_server()
            print(f"游戏运行中，请在浏览器中访问 http://localhost:{active_port}")
            # 获取本机IP地址
            try:
                import socket
                # 获取本机计算机名称
                hostname = socket.gethostname()
                # 获取本机IP
                ip_address = socket.gethostbyname(hostname)
                print(f"同一局域网内的设备也可以访问 http://{ip_address}:{active_port}")
            except Exception as e:
                print(f"无法获取本机IP地址: {e}")
        except Exception as e:
            print(f"Web服务器启动失败: {e}")
            sys.exit(1)
    
        # 添加退出处理函数
        import atexit
        def cleanup():
            """
            退出前清理函数
            
            参数：无
            
            返回值类型：无
            功能描述：确保程序退出时关闭Web服务器
            """
            print("正在关闭Web服务器...")
            stop_server()
        
        # 注册退出处理函数
        atexit.register(cleanup)
    
    # 初始化游戏（使用Web模式，不启动tkinter窗口）
    # 由于设置了Web模式标志，所有的输入输出和流程控制都会使用Web版本的函数
    try:
        game_init.run(start_flow.start_frame)
    except Exception as e:
        print(f"游戏初始化失败: {e}")
        logging.error(f"游戏初始化失败: {str(e)}", exc_info=True)
        # 当游戏初始化失败时，也应该尝试清理服务器
        if now_web_mode:
            cleanup()
        sys.exit(1)
    
    # 保持主线程运行
    try:
        while True:
            # 主循环保持程序运行，减少CPU使用率
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n游戏已被用户中断")
        # 明确调用清理函数
        if now_web_mode:
            cleanup()
        sys.exit(0)
