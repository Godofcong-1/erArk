import os

# 立绘分类文件夹的优先顺序，web 模式遍历立绘子目录时也按这个顺序
PRIOR_PORTRAIT_SUB_DIRS = ["干员", "特殊NPC", "路人", "女儿"]


def image_path_priority(image_path: str) -> tuple:
    """
    同名图片的取舍顺序，值小的优先
    目录层级浅的优先，使角色主文件夹里的文件胜过草稿、差分等子文件夹里的同名文件；
    层级相同时，所在文件夹按 PRIOR_PORTRAIT_SUB_DIRS 的顺序优先，不在其中的排在后面；
    再相同时按路径各段排序，使结果与文件系统的遍历顺序无关

    Keyword arguments:
    image_path -- str，图片文件路径

    Return arguments:
    tuple -- (路径段数, 各级文件夹的分类序号, 路径各段)
    """
    parts = tuple(os.path.normpath(image_path).split(os.sep))
    folder_ranks = tuple(PRIOR_PORTRAIT_SUB_DIRS.index(part) if part in PRIOR_PORTRAIT_SUB_DIRS else len(PRIOR_PORTRAIT_SUB_DIRS) for part in parts[:-1])
    return (len(parts), folder_ranks, parts)


def build_image_path_index(directory: str) -> tuple:
    """
    遍历目录下的全部 png，为每个图片名（文件名去掉 .png）取一个文件
    tk 模式的图片加载与 web 模式的立绘查找都用这里的结果，同名图片在两边取同一个文件

    Keyword arguments:
    directory -- str，图片根目录

    Return arguments:
    dict -- 图片名 -> 取中的文件路径
    dict -- 重名的图片名 -> 按取舍顺序排好的全部文件路径，第一个即取中的文件
    """
    # 按图片名收集全部同名文件
    candidates = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".png"):
                candidates.setdefault(file[:-4], []).append(os.path.join(root, file))

    # 每个图片名按取舍顺序取第一个文件，重名的另外记下
    index = {}
    duplicates = {}
    for image_name, paths in candidates.items():
        paths.sort(key=image_path_priority)
        index[image_name] = paths[0]
        if len(paths) > 1:
            duplicates[image_name] = paths
    return index, duplicates
