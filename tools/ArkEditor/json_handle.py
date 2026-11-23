import json


def is_utf8bom(file_path: str) -> bool:
    """
    判断文件编码是否为utf-8
    Keyword arguments:
    filepath -- 文件路径
    """
    with open(file_path, mode="rb") as now_file:
        return now_file.read(3) == b"\xef\xbb\xbf"


def load_json(file_path: str) -> dict:
    """
    载入json文件
    文件不是合法的 JSON 时抛出 json.JSONDecodeError，由调用方提示用户——
    不能在这里吞掉错误返回空数据：调用方会把「空」当成文件内容显示出来，之后一按保存就把原文件覆盖成空的
    Keyword arguments:
    file_path -- 文件路径
    Return arguments:
    dict -- 文件里的数据
    """
    if is_utf8bom(file_path):
        ec = "utf-8-sig"
    else:
        ec = "utf-8"
    with open(file_path, "r", encoding=ec) as f:
        return json.loads(f.read())
