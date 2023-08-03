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
    Keyword arguments:
    file_path -- 文件路径
    """
    if is_utf8bom(file_path):
        ec = "utf-8-sig"
    else:
        ec = "utf-8"
    with open(file_path, "r", encoding=ec) as f:
        try:
            json_data = json.loads(f.read())
            f.close()
        except json.decoder.JSONDecodeError:
            json_data = []
    return json_data
