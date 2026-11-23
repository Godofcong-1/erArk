# -*- coding: UTF-8 -*-
"""Web 模式的文字输入与完整游戏状态：游戏等文字输入时有页面连上或刷新，各页面收到的完整状态仍带输入请求与子面板数据；输入被读走后请求随即撤掉，没人等输入时提交的文字不会留给下一次输入"""
from _bootstrap import *  # noqa: F401,F403
from Script.Core import web_server

http = web_server.app.test_client()
""" 页面的 HTTP 接口（提交输入、取状态） """


def state_list(page) -> list:
    """
    取出一个页面自上次读取以来收到的全部游戏状态推送
    Keyword arguments:
    page -- Socket.IO 测试客户端
    Return arguments:
    list -- 各条 game_state_update 的内容
    """
    return [packet["args"][0] for packet in page.get_received() if packet["name"] == "game_state_update"]


def reset_state() -> None:
    """
    把服务器里的输入相关状态清回初始（各节之间互不影响）
    Keyword arguments:
    无
    Return arguments:
    无
    """
    with web_server.state_lock:
        web_server.game_state.pop("input_request", None)
        web_server.game_state.pop("sub_panel_data", None)
        web_server.game_state["sub_panel_mode"] = False
        web_server.input_response = None


section("1. 游戏等文字输入时，另一个页面连上")
reset_state()
player_page = web_server.socketio.test_client(web_server.app)
state_list(player_page)
name_request = {"type": "string", "message": "请输入姓名", "default": ""}
web_server.update_input_request(name_request)
pushed = state_list(player_page)
check("游戏开始等文字输入时，页面收到带输入请求的状态", len(pushed) == 1 and pushed[0].get("input_request") == name_request, pushed[0].get("input_request") if pushed else None)
other_page = web_server.socketio.test_client(web_server.app)
full_list = state_list(player_page)
check("另一个页面连上时发出的是完整游戏状态（带玩家信息，下面两条才有意义）", len(full_list) == 1 and "player_info" in full_list[0], [sorted(state) for state in full_list])
check("原来的页面收到的完整状态仍带着输入请求（输入框不失效）", bool(full_list) and full_list[0].get("input_request") == name_request, full_list[0].get("input_request") if full_list else None)
new_page_list = state_list(other_page)
check("新连上的页面也收到带输入请求的状态", bool(new_page_list) and new_page_list[-1].get("input_request") == name_request, [state.get("input_request") for state in new_page_list])
player_page.emit("refresh_state")
refresh_list = state_list(player_page)
check("页面请求刷新状态时，发回的完整状态同样带着输入请求", bool(refresh_list) and refresh_list[-1].get("input_request") == name_request, [state.get("input_request") for state in refresh_list])

section("2. 子面板里有页面连上")
reset_state()
sub_panel_data = {"scene_info_bar": {"scene_name": "当前位置:测试", "game_time": "测试时间"}, "panel_tabs": [{"id": "__main_panel__", "name": "主面板"}]}
with web_server.state_lock:
    web_server.game_state["sub_panel_mode"] = True
    web_server.game_state["sub_panel_data"] = sub_panel_data
state_list(player_page)
third_page = web_server.socketio.test_client(web_server.app)
full_list = state_list(player_page)
check("子面板模式下有页面连上时，完整状态带着子面板模式与场景信息栏、选项卡数据",
      bool(full_list) and full_list[0].get("sub_panel_mode") is True and full_list[0].get("sub_panel_data") == sub_panel_data and "player_info" in full_list[0],
      (full_list[0].get("sub_panel_mode"), full_list[0].get("sub_panel_data")) if full_list else None)
third_page.disconnect()

section("3. 输入被读走后撤掉输入请求")
reset_state()
web_server.update_input_request(name_request)
reply = http.post("/api/string_input", json={"value": "Testdoc"}).get_json()
answer = web_server.get_input_response()
check("游戏在等输入时，提交的文字被收下并被游戏读到", reply == {"success": True} and answer == "Testdoc", (reply, answer))
check("游戏读走输入后，状态里不再带输入请求", "input_request" not in http.get("/api/get_state").get_json(), http.get("/api/get_state").get_json().get("input_request"))
state_list(player_page)
web_server.update_game_state([], None)
pushed = state_list(player_page)
check("之后的常规状态推送不带输入请求", len(pushed) == 1 and "input_request" not in pushed[0], [state.get("input_request") for state in pushed])
check("还没有输入时去读，读到的是空、也不会撤掉请求", (web_server.update_input_request(name_request), web_server.get_input_response(), "input_request" in http.get("/api/get_state").get_json())[1:] == (None, True))

section("4. 没人等输入时提交的文字")
reset_state()
reply = http.post("/api/string_input", json={"value": "Stray"}).get_json()
check("游戏没有在等输入时，提交的文字被拒收", reply.get("success") is False and bool(reply.get("error")), reply)
reply_int = http.post("/api/integer_input", json={"value": "7"}).get_json()
check("游戏没有在等输入时，提交的数字被拒收", reply_int.get("success") is False and bool(reply_int.get("error")), reply_int)
web_server.update_input_request({"type": "integer", "message": "请输入小时", "default": 0})
check("之前被拒收的内容不会留给下一次输入", web_server.get_input_response() is None)
reply_int = http.post("/api/integer_input", json={"value": "7"}).get_json()
answer = web_server.get_input_response()
check("游戏在等数字时，提交的数字被收下并读到（转成整数）", reply_int == {"success": True} and answer == 7, (reply_int, answer))
web_server.update_input_request({"type": "integer", "message": "请输入小时", "default": 0})
reply_int = http.post("/api/integer_input", json={"value": "不是数字"}).get_json()
answer = web_server.get_input_response()
check("提交的数字转不成整数时按 0 收下", reply_int == {"success": True} and answer == 0, (reply_int, answer))

reset_state()
player_page.disconnect()
other_page.disconnect()
finish()
