import os
import json
import cv2
import numpy as np
from rtmlib import Wholebody

# COCO 17 关键点名称（索引 0-16 对应身体部位）
# 这些是标准的 COCO 姿态估计数据集中定义的人体关键点
COCO_KEYPOINTS = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]

def main():
    """
    主函数：使用 RTMlib Wholebody 模型分析角色立绘图像中的人体关键点
    
    功能说明：
    1. 初始化 RTM Wholebody 姿态估计模型（包含 RTMDet 检测 + RTMPose 姿态估计）
    2. 遍历 image/立绘/干员/差分 目录下所有角色文件夹
    3. 对每个角色的 _全身.png 图像进行关键点检测
    4. 将检测结果保存为 _body.json 文件（版本 2.0 格式）
    5. 跳过已处理过的 v2.0 版本文件，避免重复计算
    
    输入：无（从文件系统读取图像）
    输出：为每个角色生成 JSON 格式的关键点数据文件
    """
    
    # 默认使用 CPU 设备以确保在所有环境下的稳定性
    # 虽然已安装 onnxruntime-gpu，但在某些环境下 CUDA 可能无法正常工作
    # RTMlib 会尝试使用指定的设备进行推理
    # 优先尝试使用 GPU（若不可用则回退到 CPU）
    device = 'cuda'
    print(f"正在初始化 RTM Wholebody 模型（优先设备: {device}）...")
    try:
        wholebody = Wholebody(device=device)
    except Exception as e:
        print(f"GPU 初始化失败: {e}，尝试回退到 CPU...")
        try:
            device = 'cpu'
            wholebody = Wholebody(device=device)
        except Exception as e2:
            print(f"模型初始化失败: {e2}")
            return

    # 构建目标目录路径
    # 当前脚本在 tools/ 目录下，需要回退到工作区根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(current_dir)
    base_dir = os.path.join(workspace_root, 'image', '立绘', '特殊NPC')

    # 检查目标目录是否存在
    if not os.path.exists(base_dir):
        print(f"目录 {base_dir} 不存在。")
        return

    # 获取所有角色文件夹列表
    characters = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    print(f"在 {base_dir} 中找到 {len(characters)} 个角色文件夹。")

    # 统计变量
    count = 0  # 总处理数（预留）
    updated_count = 0  # 实际更新的文件数
    
    # 遍历每个角色文件夹
    for i, char_name in enumerate(characters):
        char_dir = os.path.join(base_dir, char_name)
        # 构建全身图像和 JSON 输出文件的路径
        full_body_path = os.path.join(char_dir, f"{char_name}_全身.png")
        json_path = os.path.join(char_dir, f"{char_name}_body.json")

        # 如果全身图像不存在，跳过该角色
        if not os.path.exists(full_body_path):
            continue

        # 检查是否已经处理过（版本 2.0 且使用 rtmlib_wholebody 模型）
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 如果已是 v2.0 版本且使用相同模型，则跳过
                    if data.get('version') == '2.0' and data.get('model') == 'rtmlib_wholebody':
                         continue
            except:
                # 如果 JSON 文件损坏或格式错误，则重新处理
                pass
        
        # 显示当前处理进度
        print(f"[{i+1}/{len(characters)}] 正在分析 {char_name}...", end='', flush=True)
        
        try:
            # 使用 numpy 读取图像以支持包含 Unicode 字符的路径
            # 这是处理中文路径的标准方法
            img_array = np.fromfile(full_body_path, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            # 检查图像是否成功加载
            if image is None:
                print(f" 错误：无法读取图像。")
                continue

            # 获取图像尺寸（用于归一化坐标）
            height, width = image.shape[:2]

            # 运行姿态估计推理
            # 返回值说明：
            # keypoints: (N, K, 2) - N 个检测到的人体，每个有 K 个关键点，每个点 (x, y) 坐标
            # scores: (N, K) - 每个关键点的置信度分数
            keypoints, scores = wholebody(image)

            # 用于存储所有关键点数据的列表
            landmarks_data = []
            
            # 如果没有检测到任何人体
            if keypoints is None or len(keypoints) == 0:
                print(f" 未检测到人体。", end='')
                # 即使未检测到人体，也创建 JSON 文件标记为已处理
                # 这样不会在下次运行时重复尝试
                output_data = {
                    "version": "2.0",
                    "model": "rtmlib_wholebody",
                    "character": char_name,
                    "source_image": f"{char_name}_全身.png",
                    "image_width": width,
                    "image_height": height,
                    "landmarks": [],
                    "note": "RTMPose 未检测到人体"
                }
            else:
                # 处理检测到的人体关键点
                # 如果检测到多个人体，选择第一个（通常角色立绘只有一个主体）
                # 也可以选择平均置信度最高的，但对于单人立绘，第一个通常就是目标
                kps = keypoints[0]  # (K, 2) - K 个关键点的 (x, y) 坐标
                scs = scores[0]     # (K,) - K 个关键点的置信度分数
                
                # 遍历每个关键点，提取并归一化坐标
                for idx, (kp, score) in enumerate(zip(kps, scs)):
                    # kp 是像素坐标 [x, y]
                    # RTMlib 输出的是有效的像素坐标
                    # 归一化到 [0, 1] 范围，便于不同分辨率图像间的比较
                    norm_x = float(kp[0]) / width
                    norm_y = float(kp[1]) / height
                    
                    # 获取关键点名称
                    kp_name = f"KP_{idx}"  # 默认名称
                    if idx < len(COCO_KEYPOINTS):
                        kp_name = COCO_KEYPOINTS[idx]  # 使用标准 COCO 关键点名称
                    
                    # 构建关键点数据结构
                    landmarks_data.append({
                        "id": idx,                    # 关键点索引
                        "name": kp_name,              # 关键点名称
                        "x": norm_x,                  # 归一化 x 坐标
                        "y": norm_y,                  # 归一化 y 坐标
                        "score": float(score),        # 置信度分数
                        "visibility": float(score)    # 可见性（映射为置信度分数）
                    })

                print(f" 检测到 {len(landmarks_data)} 个关键点。", end='')
                
                # 构建完整的输出数据结构
                output_data = {
                    "version": "2.0",                           # 数据格式版本
                    "model": "rtmlib_wholebody",                # 使用的模型名称
                    "character": char_name,                     # 角色名称
                    "source_image": f"{char_name}_全身.png",    # 源图像文件名
                    "image_width": width,                       # 图像宽度
                    "image_height": height,                     # 图像高度
                    "landmarks": landmarks_data                 # 关键点数据列表
                }

            # 将结果写入 JSON 文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(" 已保存。")
            updated_count += 1

        except Exception as e:
            # 捕获并打印处理过程中的任何异常
            print(f" 处理失败: {e}")
    
    # 打印最终统计信息
    print(f"分析完成。已更新 {updated_count} 个角色的数据。")

if __name__ == "__main__":
    main()

