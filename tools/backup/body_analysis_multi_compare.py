"""
多模型+集成 身体部位识别对比测试工具

功能说明：
对比7个姿态估计模型 + 1个集成方案在动漫角色立绘上的识别效果。
不考虑速度，追求最大检测精度。

模型列表：
A. Wholebody balanced  = YOLOX-m + RTMW-dw-x-l@256x192 (133→17) [基线]
B. Body performance    = YOLOX-x + RTMPose-x@384x288 (原生17kp)
C. Wholebody perf      = YOLOX-m + RTMW-dw-x-l@384x288 (133→17, 高分辨率)
D. YOLO11x-pose        = ultralytics单阶段模型 (原生17kp, COCO训练)
E. BodyWithFeet perf   = YOLOX-x + RTMPose-x-halpe26@384x288 (26→17kp)
F. RTMO-l              = 单阶段姿态估计 (640x640, 原生17kp)
G. Custom最大精度      = YOLOX-x + RTMW-dw-x-l@384x288 (最强检测器+最强姿态)

ENSEMBLE: 对每个关键点，取所有模型中归一化置信度最高的结果

注意：
- 模型C/G使用RTMW输出logit值(>1.0)，需sigmoid归一化后参与集成比较
- 模型E输出26个关键点(halpe26格式)，取前17个即为COCO 17
- 模型D(YOLO11x)在COCO上训练，不含HumanArt数据，对真人精度高但动漫可能有差异
- 模型F(RTMO)为单阶段模型，无需检测器

输入：image/立绘/模型测试用/ 下的角色全身图片
输出：每个角色生成对比可视化图片，保存在 image/立绘/模型测试用/多模型对比结果/
"""

import os
import json
import cv2
import numpy as np
import time
import traceback

# COCO 17 关键点名称（索引 0-16 对应身体部位）
COCO_KEYPOINTS = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]

# COCO 17 关键点中文名
COCO_KEYPOINTS_CN = [
    "鼻子", "左眼", "右眼", "左耳", "右耳",
    "左肩", "右肩", "左肘", "右肘",
    "左手腕", "右手腕", "左臀", "右臀",
    "左膝", "右膝", "左脚踝", "右脚踝"
]

# COCO骨架连接定义
COCO_SKELETON = [
    (0, 1), (0, 2), (1, 3), (2, 4),      # 头部
    (5, 6),                                  # 肩膀
    (5, 7), (7, 9),                          # 左臂
    (6, 8), (8, 10),                         # 右臂
    (5, 11), (6, 12),                        # 躯干
    (11, 12),                                # 臀部
    (11, 13), (13, 15),                      # 左腿
    (12, 14), (14, 16),                      # 右腿
]

# 按身体部位分组的颜色方案（BGR格式）
PART_COLORS = {
    "head": (255, 200, 50),
    "shoulder": (50, 255, 50),
    "arm_left": (255, 100, 0),
    "arm_right": (0, 100, 255),
    "torso": (200, 200, 0),
    "leg_left": (255, 0, 200),
    "leg_right": (0, 200, 255),
}

# 每个关键点对应的部位分组
KP_TO_PART = {
    0: "head", 1: "head", 2: "head", 3: "head", 4: "head",
    5: "shoulder", 6: "shoulder",
    7: "arm_left", 9: "arm_left",
    8: "arm_right", 10: "arm_right",
    11: "torso", 12: "torso",
    13: "leg_left", 15: "leg_left",
    14: "leg_right", 16: "leg_right",
}

# 骨架连线对应的颜色
SKELETON_COLORS = []
for (a, b) in COCO_SKELETON:
    part = KP_TO_PART.get(a, "head")
    SKELETON_COLORS.append(PART_COLORS[part])

# 模型颜色方案（BGR格式）——为每个模型分配易区分的颜色
MODEL_COLORS = {
    'A': (100, 180, 255),   # 橙色
    'B': (100, 255, 100),   # 绿色
    'C': (255, 180, 100),   # 蓝色
    'D': (0, 255, 255),     # 黄色
    'E': (255, 100, 255),   # 粉色
    'F': (255, 255, 100),   # 青色
    'G': (100, 100, 255),   # 红色
    'ENS': (255, 255, 255), # 白色 - 集成
}


def sigmoid(x):
    """
    Sigmoid函数，将logit值转为0-1概率

    输入：x: float或numpy.ndarray - logit值
    输出：float或numpy.ndarray - 0-1之间的概率值
    """
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))


def load_image(image_path):
    """
    加载图像（支持中文路径）

    输入：image_path: str - 图像文件路径
    输出：numpy.ndarray - BGR格式图像，加载失败返回None
    """
    img_array = np.fromfile(image_path, np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return image


def save_image(path, image):
    """
    保存图像到指定路径（支持中文路径）

    输入：
        path: str - 目标路径
        image: numpy.ndarray - BGR格式图像
    输出：bool - 是否保存成功
    """
    success, encoded = cv2.imencode('.png', image)
    if success:
        encoded.tofile(path)
        return True
    return False


def draw_keypoints_on_image(image, keypoints_17, scores_17, model_name, threshold=0.3):
    """
    在图像上绘制COCO 17关键点和骨架

    输入：
        image: numpy.ndarray - BGR格式原始图像
        keypoints_17: numpy.ndarray - shape (17, 2) 像素坐标
        scores_17: numpy.ndarray - shape (17,) 置信度分数（已归一化到0-1）
        model_name: str - 模型名称
        threshold: float - 置信度阈值
    输出：numpy.ndarray - 标注后的图像副本
    """
    img = image.copy()
    h, w = img.shape[:2]

    scale_factor = max(w, h) / 1024.0
    font_scale = max(0.4, 0.5 * scale_factor)
    circle_radius = max(4, int(6 * scale_factor))
    line_thickness = max(2, int(3 * scale_factor))
    text_thickness = max(1, int(1.5 * scale_factor))

    # 模型名称标签
    label_bg_h = int(40 * scale_factor)
    cv2.rectangle(img, (0, 0), (w, label_bg_h), (0, 0, 0), -1)
    cv2.putText(img, model_name, (10, int(28 * scale_factor)),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale * 1.2, (255, 255, 255), text_thickness + 1)

    # 绘制骨架连线
    for idx, (a, b) in enumerate(COCO_SKELETON):
        if a < len(keypoints_17) and b < len(keypoints_17):
            sa = scores_17[a] if a < len(scores_17) else 0
            sb = scores_17[b] if b < len(scores_17) else 0
            if sa > threshold and sb > threshold:
                pt_a = (int(keypoints_17[a][0]), int(keypoints_17[a][1]))
                pt_b = (int(keypoints_17[b][0]), int(keypoints_17[b][1]))
                color = SKELETON_COLORS[idx]
                cv2.line(img, pt_a, pt_b, color, line_thickness)

    # 绘制关键点
    for idx in range(min(17, len(keypoints_17))):
        x, y = int(keypoints_17[idx][0]), int(keypoints_17[idx][1])
        score = scores_17[idx] if idx < len(scores_17) else 0
        part = KP_TO_PART.get(idx, "head")
        color = PART_COLORS[part]

        if score > threshold:
            cv2.circle(img, (x, y), circle_radius, color, -1)
            cv2.circle(img, (x, y), circle_radius, (255, 255, 255), 1)

            label = f"{idx}:{COCO_KEYPOINTS[idx]}({score:.2f})"
            text_x = x + circle_radius + 3
            text_y = y - 3
            if text_x + 150 * scale_factor > w:
                text_x = x - int(160 * scale_factor)
            if text_y < 20:
                text_y = y + int(20 * scale_factor)

            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.7, text_thickness)
            cv2.rectangle(img, (text_x - 2, text_y - th - 4), (text_x + tw + 2, text_y + 4), (0, 0, 0), -1)
            cv2.putText(img, label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.7, color, text_thickness)
        else:
            cv2.circle(img, (x, y), circle_radius, (0, 0, 200), 2)
            cv2.line(img, (x - circle_radius, y - circle_radius),
                     (x + circle_radius, y + circle_radius), (0, 0, 200), 2)
            cv2.line(img, (x - circle_radius, y + circle_radius),
                     (x + circle_radius, y - circle_radius), (0, 0, 200), 2)

            label = f"{idx}:{COCO_KEYPOINTS[idx]}({score:.2f})LOW"
            text_x = x + circle_radius + 3
            text_y = y - 3
            if text_x + 150 * scale_factor > w:
                text_x = x - int(160 * scale_factor)

            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, text_thickness)
            cv2.rectangle(img, (text_x - 2, text_y - th - 4), (text_x + tw + 2, text_y + 4), (0, 0, 0), -1)
            cv2.putText(img, label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.6, (0, 0, 200), text_thickness)

    return img


def normalize_scores(scores, model_key, needs_sigmoid_keys):
    """
    归一化分数：对RTMW系列模型应用sigmoid，其他保持不变

    输入：
        scores: numpy.ndarray - 原始分数
        model_key: str - 模型标识符
        needs_sigmoid_keys: set - 需要sigmoid归一化的模型key集合
    输出：numpy.ndarray - 归一化后的分数（0-1范围）
    """
    if model_key in needs_sigmoid_keys:
        return sigmoid(scores)
    return scores.copy()


def build_ensemble(results, needs_sigmoid_keys):
    """
    构建集成结果：对每个关键点，取归一化置信度最高的模型的坐标和分数

    输入：
        results: dict - {model_key: {'kps': ndarray(17,2), 'scores': ndarray(17), ...}}
        needs_sigmoid_keys: set - 需要sigmoid的模型key集合
    输出：dict - 集成结果 {'kps': ndarray(17,2), 'scores': ndarray(17), 'norm_scores': ndarray(17),
                          'source_models': list[str], 'avg': float}
    功能：对每个关键点独立选择最优模型结果
    """
    ens_kps = np.zeros((17, 2))
    ens_scores = np.zeros(17)      # 归一化后的分数
    ens_raw_scores = np.zeros(17)  # 对应的原始分数
    source_models = []

    for kp_idx in range(17):
        best_norm_score = -1
        best_key = ''
        best_kp = np.zeros(2)
        best_raw = 0

        for key, res in results.items():
            if res is None or res['scores'] is None:
                continue
            raw_score = res['scores'][kp_idx]
            norm_score = normalize_scores(
                np.array([raw_score]), key, needs_sigmoid_keys
            )[0]

            if norm_score > best_norm_score:
                best_norm_score = norm_score
                best_key = key
                best_kp = res['kps'][kp_idx].copy()
                best_raw = raw_score

        ens_kps[kp_idx] = best_kp
        ens_scores[kp_idx] = best_norm_score
        ens_raw_scores[kp_idx] = best_raw
        source_models.append(best_key)

    return {
        'kps': ens_kps,
        'scores': ens_scores,           # 归一化后的分数
        'raw_scores': ens_raw_scores,
        'norm_scores': ens_scores,
        'source_models': source_models,
        'avg': float(np.mean(ens_scores))
    }


def create_score_table_image(results, models, char_name, needs_sigmoid_keys, ensemble_result=None):
    """
    生成所有模型的归一化置信度对比表格图

    输入：
        results: dict - 各模型结果
        models: dict - 模型信息
        char_name: str - 角色名
        needs_sigmoid_keys: set - 需要sigmoid的模型key集合
        ensemble_result: dict或None - 集成结果
    输出：numpy.ndarray - 表格图（BGR）
    """
    keys = sorted(results.keys())
    n_cols = len(keys) + (1 if ensemble_result else 0) + 1  # +1 for Best column

    col_w = 110
    row_h = 26
    kp_col_w = 160
    total_w = kp_col_w + n_cols * col_w + 20
    total_h = 100 + (17 + 3) * row_h  # header + 17 kps + avg + separator + ensemble source

    summary = np.zeros((total_h, total_w, 3), dtype=np.uint8)
    summary[:] = (30, 30, 30)

    # 标题
    cv2.putText(summary, f"Normalized Score Comparison: {char_name}", (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    # 模型标签行
    y_label = 55
    for i, k in enumerate(keys):
        color = MODEL_COLORS.get(k, (200, 200, 200))
        label = models[k]['name'] if k in models else k
        cv2.putText(summary, label, (kp_col_w + i * col_w, y_label),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, color, 1)

    if ensemble_result:
        cv2.putText(summary, "ENSEMBLE", (kp_col_w + len(keys) * col_w, y_label),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, MODEL_COLORS['ENS'], 1)
    cv2.putText(summary, "Best", (kp_col_w + (len(keys) + (1 if ensemble_result else 0)) * col_w, y_label),
                cv2.FONT_HERSHEY_SIMPLEX, 0.32, (200, 200, 200), 1)

    # 表头分隔线
    y_header = 70
    cv2.line(summary, (10, y_header), (total_w - 10, y_header), (80, 80, 80), 1)

    # 表头
    y_h = y_header + 18
    cv2.putText(summary, "Keypoint", (15, y_h),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1)
    for i, k in enumerate(keys):
        cv2.putText(summary, k, (kp_col_w + i * col_w + 30, y_h),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, MODEL_COLORS.get(k, (200, 200, 200)), 1)
    if ensemble_result:
        cv2.putText(summary, "ENS", (kp_col_w + len(keys) * col_w + 20, y_h),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, MODEL_COLORS['ENS'], 1)

    cv2.line(summary, (10, y_h + 6), (total_w - 10, y_h + 6), (60, 60, 60), 1)

    # 统计每个模型的胜出次数
    model_wins = {k: 0 for k in keys}
    if ensemble_result:
        model_wins['ENS'] = 0

    # 逐关键点
    for kp_idx in range(17):
        y = y_h + 8 + (kp_idx + 1) * row_h

        # 关键点名
        name = f"{kp_idx:2d}:{COCO_KEYPOINTS[kp_idx]}"
        cv2.putText(summary, name, (15, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        # 收集每个模型的归一化分数
        norm_scores_map = {}
        for i, k in enumerate(keys):
            if k in results and results[k] is not None:
                raw = results[k]['scores'][kp_idx]
                norm = normalize_scores(np.array([raw]), k, needs_sigmoid_keys)[0]
                norm_scores_map[k] = norm
                color = MODEL_COLORS.get(k, (200, 200, 200))
                cv2.putText(summary, f"{norm:.4f}", (kp_col_w + i * col_w + 10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.33, color, 1)
            else:
                norm_scores_map[k] = 0.0
                cv2.putText(summary, "N/A", (kp_col_w + i * col_w + 10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.33, (80, 80, 80), 1)

        if ensemble_result:
            ens_score = ensemble_result['scores'][kp_idx]
            norm_scores_map['ENS'] = ens_score
            cv2.putText(summary, f"{ens_score:.4f}",
                        (kp_col_w + len(keys) * col_w + 10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.33, MODEL_COLORS['ENS'], 1)

            # 标注来源模型
            src = ensemble_result['source_models'][kp_idx]
            cv2.putText(summary, f"({src})",
                        (kp_col_w + len(keys) * col_w + 68, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.25, (150, 150, 150), 1)

        # 找最佳（排除ENS，因为ENS本身就是最佳的组合）
        best_key = max(norm_scores_map, key=norm_scores_map.get)
        model_wins[best_key] = model_wins.get(best_key, 0) + 1
        best_color = MODEL_COLORS.get(best_key, (200, 200, 200))
        x_best = kp_col_w + (len(keys) + (1 if ensemble_result else 0)) * col_w + 10
        cv2.putText(summary, best_key, (x_best, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, best_color, 1)

    # 平均行
    y_avg = y_h + 8 + 18 * row_h
    cv2.line(summary, (10, y_avg - 12), (total_w - 10, y_avg - 12), (80, 80, 80), 1)
    cv2.putText(summary, "Average", (15, y_avg),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)

    for i, k in enumerate(keys):
        if k in results and results[k] is not None:
            all_norm = normalize_scores(results[k]['scores'][:17], k, needs_sigmoid_keys)
            avg = float(np.mean(all_norm))
        else:
            avg = 0.0
        cv2.putText(summary, f"{avg:.4f}", (kp_col_w + i * col_w + 10, y_avg),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, MODEL_COLORS.get(k, (200, 200, 200)), 1)

    if ensemble_result:
        cv2.putText(summary, f"{ensemble_result['avg']:.4f}",
                    (kp_col_w + len(keys) * col_w + 10, y_avg),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, MODEL_COLORS['ENS'], 1)

    # 胜出统计行
    y_wins = y_avg + row_h
    cv2.putText(summary, "Wins/17", (15, y_wins),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
    for i, k in enumerate(keys):
        w_count = model_wins.get(k, 0)
        cv2.putText(summary, f"{w_count}", (kp_col_w + i * col_w + 30, y_wins),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, MODEL_COLORS.get(k, (200, 200, 200)), 1)
    if ensemble_result:
        w_count = model_wins.get('ENS', 0)
        cv2.putText(summary, f"{w_count}", (kp_col_w + len(keys) * col_w + 30, y_wins),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, MODEL_COLORS['ENS'], 1)

    return summary


def run_yolo11_inference(model, image):
    """
    使用YOLO11-pose模型进行推理

    输入：
        model: ultralytics.YOLO - YOLO模型实例
        image: numpy.ndarray - BGR图像
    输出：tuple(ndarray, ndarray) - (关键点坐标(17,2), 置信度(17,)) 或 (None, None)
    """
    results = model(image, verbose=False)
    r = results[0]
    if r.keypoints is not None and len(r.keypoints.data) > 0:
        # 取置信度最高的检测
        if r.boxes is not None and len(r.boxes.data) > 0:
            confs = r.boxes.conf.cpu().numpy()
            best_idx = np.argmax(confs)
        else:
            best_idx = 0

        kp_data = r.keypoints.data[best_idx].cpu().numpy()  # (17, 3) = x, y, conf
        kps = kp_data[:, :2]    # (17, 2)
        scores = kp_data[:, 2]  # (17,)
        return kps, scores
    return None, None


def run_rtmo_inference(model, image):
    """
    使用RTMO单阶段模型进行推理

    输入：
        model: rtmlib.RTMO - RTMO模型实例
        image: numpy.ndarray - BGR图像
    输出：tuple(ndarray, ndarray) - (关键点坐标(17,2), 置信度(17,)) 或 (None, None)
    """
    keypoints, scores = model(image)
    if keypoints is not None and len(keypoints) > 0:
        return keypoints[0][:17], scores[0][:17]
    return None, None


def main():
    """
    主函数：运行多模型+集成对比测试

    执行流程：
    1. 初始化所有模型
    2. 遍历测试角色，对每张图运行所有模型
    3. 构建集成结果（每个关键点取归一化置信度最高的模型）
    4. 生成可视化对比图和统计数据
    5. 输出综合统计报告
    """
    from rtmlib import Wholebody, Body, BodyWithFeet, RTMO, Custom

    # 构建路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(current_dir)
    test_dir = os.path.join(workspace_root, 'image', '立绘', '模型测试用')
    output_dir = os.path.join(test_dir, '多模型对比结果')

    if not os.path.exists(test_dir):
        print(f"测试目录不存在: {test_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)

    backend = 'onnxruntime'
    device = 'cpu'  # 无GPU可用

    # 需要sigmoid归一化的模型key（RTMW模型输出logit而非概率）
    needs_sigmoid_keys = set()

    # ===== 模型定义 =====
    models = {}
    model_init_start = time.time()

    # --- A: Wholebody balanced (基线) ---
    print("=" * 80)
    print("[A] Wholebody balanced: YOLOX-m + RTMW@256x192 (基线)")
    print("=" * 80)
    try:
        models['A'] = {
            'name': 'A:WB_bal',
            'full_name': 'A: Wholebody balanced (YOLOX-m + RTMW@256x192)',
            'model': Wholebody(mode='balanced', backend=backend, device=device),
            'type': 'rtmlib',
            'extract_17': True,  # 从133点中取前17
        }
        needs_sigmoid_keys.add('A')  # Wholebody的RTMW也可能输出logit
        print("  初始化成功")
    except Exception as e:
        print(f"  初始化失败: {e}")

    # --- B: Body performance ---
    print("\n[B] Body performance: YOLOX-x + RTMPose-x@384x288")
    try:
        models['B'] = {
            'name': 'B:Body_perf',
            'full_name': 'B: Body perf (YOLOX-x + RTMPose-x@384x288)',
            'model': Body(mode='performance', backend=backend, device=device),
            'type': 'rtmlib',
            'extract_17': False,  # 原生17关键点
        }
        print("  初始化成功")
    except Exception as e:
        print(f"  初始化失败: {e}")

    # --- C: Wholebody performance ---
    print("\n[C] Wholebody performance: YOLOX-m + RTMW@384x288")
    try:
        models['C'] = {
            'name': 'C:WB_perf',
            'full_name': 'C: Wholebody perf (YOLOX-m + RTMW@384x288)',
            'model': Wholebody(mode='performance', backend=backend, device=device),
            'type': 'rtmlib',
            'extract_17': True,
        }
        needs_sigmoid_keys.add('C')
        print("  初始化成功")
    except Exception as e:
        print(f"  初始化失败: {e}")

    # --- D: YOLO11x-pose ---
    print("\n[D] YOLO11x-pose: 单阶段模型 (COCO训练)")
    try:
        from ultralytics import YOLO
        yolo_model = YOLO('yolo11x-pose.pt')
        models['D'] = {
            'name': 'D:YOLO11x',
            'full_name': 'D: YOLO11x-pose (single-stage, COCO)',
            'model': yolo_model,
            'type': 'yolo11',
            'extract_17': False,
        }
        print("  初始化成功")
    except Exception as e:
        print(f"  初始化失败: {e}")

    # --- E: BodyWithFeet performance ---
    print("\n[E] BodyWithFeet performance: YOLOX-x + RTMPose-x-halpe26@384x288")
    try:
        models['E'] = {
            'name': 'E:BWF_perf',
            'full_name': 'E: BodyWithFeet perf (YOLOX-x + halpe26@384x288)',
            'model': BodyWithFeet(mode='performance', backend=backend, device=device),
            'type': 'rtmlib',
            'extract_17': True,  # 从26点取前17
        }
        print("  初始化成功")
    except Exception as e:
        print(f"  初始化失败: {e}")

    # --- F: RTMO-l (单阶段) ---
    print("\n[F] RTMO-l: 单阶段姿态估计 (640x640)")
    try:
        rtmo_url = 'https://download.openmmlab.com/mmpose/v1/projects/rtmo/onnx_sdk/rtmo-l_16xb16-600e_body7-640x640-b37118ce_20231211.zip'
        rtmo_model = RTMO(
            onnx_model=rtmo_url,
            model_input_size=(640, 640),
            backend=backend,
            device=device
        )
        models['F'] = {
            'name': 'F:RTMO-l',
            'full_name': 'F: RTMO-l (single-stage, 640x640)',
            'model': rtmo_model,
            'type': 'rtmo',
            'extract_17': False,
        }
        print("  初始化成功")
    except Exception as e:
        print(f"  初始化失败: {e}")
        traceback.print_exc()

    # --- G: Custom最大精度 (YOLOX-x + RTMW@384x288) ---
    print("\n[G] Custom: YOLOX-x + RTMW@384x288 (最强检测器+最强姿态)")
    try:
        det_url = 'https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_x_8xb8-300e_humanart-a39d44ed.zip'
        pose_url = 'https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/rtmw-dw-x-l_simcc-cocktail14_270e-384x288_20231122.zip'
        models['G'] = {
            'name': 'G:Custom_max',
            'full_name': 'G: Custom (YOLOX-x + RTMW@384x288)',
            'model': Custom(
                det_class='YOLOX',
                det=det_url,
                det_input_size=(640, 640),
                pose_class='RTMPose',
                pose=pose_url,
                pose_input_size=(288, 384),
                backend=backend,
                device=device
            ),
            'type': 'rtmlib',
            'extract_17': True,  # RTMW输出133点
        }
        needs_sigmoid_keys.add('G')
        print("  初始化成功")
    except Exception as e:
        print(f"  初始化失败: {e}")
        traceback.print_exc()

    init_time = time.time() - model_init_start
    print(f"\n模型初始化完成，耗时 {init_time:.1f}s，成功加载 {len(models)} 个模型")
    print(f"需要sigmoid归一化的模型: {needs_sigmoid_keys}")

    # 先检测模型A是否真的需要sigmoid（测量分数范围）
    # A模型(balanced)使用RTMW@256x192，分数可能 >1
    # 稍后在第一张图上自动检测

    # 获取测试角色
    characters = sorted([d for d in os.listdir(test_dir)
                         if os.path.isdir(os.path.join(test_dir, d)) and d not in ('对比结果', '多模型对比结果')])
    print(f"\n测试角色 ({len(characters)}): {characters}\n")

    # 总体统计
    total_stats = {k: {'wins': 0, 'total_norm_scores': [], 'per_char_avg': []}
                   for k in models}
    total_stats['ENS'] = {'wins': 0, 'total_norm_scores': [], 'per_char_avg': []}
    ensemble_source_count = {k: 0 for k in models}
    auto_sigmoid_checked = False

    # ===== 遍历测试角色 =====
    for char_idx, char_name in enumerate(characters):
        char_dir = os.path.join(test_dir, char_name)
        full_body_path = os.path.join(char_dir, f"{char_name}_全身.png")

        if not os.path.exists(full_body_path):
            print(f"[跳过] {char_name}: 未找到 _全身.png")
            continue

        print(f"\n{'#' * 80}")
        print(f"# [{char_idx+1}/{len(characters)}] 正在测试: {char_name}")
        print(f"{'#' * 80}")

        image = load_image(full_body_path)
        if image is None:
            print(f"  错误：无法加载图像")
            continue

        h, w = image.shape[:2]
        print(f"  图像尺寸: {w}x{h}")

        # 对每个模型运行推理
        results = {}
        for key in sorted(models.keys()):
            minfo = models[key]
            name = minfo['name']
            t0 = time.time()
            print(f"  运行 {name}...", end='', flush=True)

            try:
                if minfo['type'] == 'yolo11':
                    kps_17, scores_17 = run_yolo11_inference(minfo['model'], image)
                elif minfo['type'] == 'rtmo':
                    kps_17, scores_17 = run_rtmo_inference(minfo['model'], image)
                else:
                    # rtmlib标准接口
                    kps, scores = minfo['model'](image)
                    if kps is not None and len(kps) > 0:
                        kps_17 = kps[0][:17]
                        scores_17 = scores[0][:17]
                    else:
                        kps_17, scores_17 = None, None

                elapsed = time.time() - t0

                if kps_17 is not None and scores_17 is not None:
                    raw_avg = float(np.mean(scores_17))
                    norm_scores = normalize_scores(scores_17, key, needs_sigmoid_keys)
                    norm_avg = float(np.mean(norm_scores))
                    print(f" OK ({elapsed:.1f}s) 原始avg={raw_avg:.4f}, 归一化avg={norm_avg:.4f}")

                    # 自动检测是否需要sigmoid（首次处理时）
                    if not auto_sigmoid_checked and key == 'A':
                        if raw_avg > 1.0:
                            print(f"    ⚠ 模型A分数>1.0，确认需要sigmoid归一化")
                        else:
                            print(f"    ✓ 模型A分数在0-1范围，移除sigmoid")
                            needs_sigmoid_keys.discard('A')

                    results[key] = {
                        'kps': kps_17.copy(),
                        'scores': scores_17.copy(),
                        'norm_scores': norm_scores,
                        'avg': raw_avg,
                        'norm_avg': norm_avg,
                    }
                else:
                    print(f" 未检测到人体! ({elapsed:.1f}s)")
                    results[key] = None

            except Exception as e:
                elapsed = time.time() - t0
                print(f" 错误({elapsed:.1f}s): {e}")
                results[key] = None

        auto_sigmoid_checked = True

        # 过滤有效结果
        valid_results = {k: v for k, v in results.items() if v is not None}

        if not valid_results:
            print(f"  所有模型均未检测到人体，跳过")
            continue

        # ===== 构建集成结果 =====
        ensemble = build_ensemble(valid_results, needs_sigmoid_keys)
        print(f"\n  集成结果: 归一化avg={ensemble['avg']:.4f}")
        print(f"  集成来源: {ensemble['source_models']}")

        # 统计集成来源
        for src in ensemble['source_models']:
            ensemble_source_count[src] = ensemble_source_count.get(src, 0) + 1

        # ===== 绘制可视化 =====
        # 1. 每个模型的标注图
        annotated = {}
        for key in sorted(valid_results.keys()):
            minfo = models[key]
            res = valid_results[key]
            # 绘制时使用归一化分数（这样threshold判断才准确）
            norm_scores = normalize_scores(res['scores'], key, needs_sigmoid_keys)
            annotated[key] = draw_keypoints_on_image(
                image, res['kps'], norm_scores, minfo['full_name'])

        # 2. 集成结果标注图
        annotated['ENS'] = draw_keypoints_on_image(
            image, ensemble['kps'], ensemble['scores'],
            f"ENSEMBLE (best per-kp, src: {''.join(set(ensemble['source_models']))})")

        # 3. 保存单独标注图
        for key, img in annotated.items():
            fname = f"{char_name}_{key}.png"
            save_image(os.path.join(output_dir, fname), img)

        # 4. 拼接对比图（选择关键模型对比，避免太宽）
        # 4a. 全模型对比（缩小版）
        display_keys = sorted(valid_results.keys()) + ['ENS']
        target_h = max(h, 600)
        imgs = []
        for key in display_keys:
            if key in annotated:
                img = annotated[key]
                scale = target_h / img.shape[0]
                resized = cv2.resize(img, (int(img.shape[1] * scale), target_h))
                imgs.append(resized)

        if len(imgs) > 1:
            sep = np.zeros((target_h, 3, 3), dtype=np.uint8)
            sep[:] = (0, 255, 255)
            parts = [imgs[0]]
            for img in imgs[1:]:
                parts.append(sep)
                parts.append(img)
            comparison = np.hstack(parts)
            save_image(os.path.join(output_dir, f"{char_name}_全模型对比.png"), comparison)

        # 4b. 最佳3个 + 集成对比
        # 按归一化平均分排序取前3
        sorted_models = sorted(valid_results.keys(),
                                key=lambda k: float(np.mean(normalize_scores(
                                    valid_results[k]['scores'], k, needs_sigmoid_keys))),
                                reverse=True)
        top3 = sorted_models[:3]
        focus_keys = top3 + ['ENS']
        imgs_focus = []
        for key in focus_keys:
            if key in annotated:
                img = annotated[key]
                scale = target_h / img.shape[0]
                resized = cv2.resize(img, (int(img.shape[1] * scale), target_h))
                imgs_focus.append(resized)

        if len(imgs_focus) > 1:
            sep = np.zeros((target_h, 3, 3), dtype=np.uint8)
            sep[:] = (0, 200, 255)
            parts = [imgs_focus[0]]
            for img in imgs_focus[1:]:
                parts.append(sep)
                parts.append(img)
            comparison_focus = np.hstack(parts)
            top3_names = '+'.join(top3)
            save_image(os.path.join(output_dir, f"{char_name}_TOP3+集成对比.png"), comparison_focus)

        # 5. 分数对比表格
        score_table = create_score_table_image(valid_results, models, char_name,
                                                needs_sigmoid_keys, ensemble)
        save_image(os.path.join(output_dir, f"{char_name}_分数对比表.png"), score_table)

        print(f"  已保存所有可视化结果")

        # ===== 打印逐点对比表（文字版） =====
        keys_print = sorted(valid_results.keys())
        header = f"  {'关键点':<16}"
        for k in keys_print:
            header += f" {k:>8}"
        header += f" {'ENS':>8} {'来源':>4}"
        print(header)
        print(f"  {'-' * (16 + 10 * len(keys_print) + 16)}")

        for idx in range(17):
            line = f"  {idx:2d}:{COCO_KEYPOINTS[idx]:<12}"
            norm_map = {}
            for k in keys_print:
                norm = float(normalize_scores(
                    np.array([valid_results[k]['scores'][idx]]), k, needs_sigmoid_keys)[0])
                norm_map[k] = norm
                line += f" {norm:>8.4f}"

            ens_score = ensemble['scores'][idx]
            ens_src = ensemble['source_models'][idx]
            line += f" {ens_score:>8.4f}   {ens_src}"

            # 统计胜出（在单模型间）
            best_key = max(norm_map, key=norm_map.get)
            total_stats[best_key]['wins'] += 1
            print(line)

        print(f"  {'-' * (16 + 10 * len(keys_print) + 16)}")

        # 平均
        avg_line = f"  {'平均':<16}"
        for k in keys_print:
            all_norm = normalize_scores(valid_results[k]['scores'][:17], k, needs_sigmoid_keys)
            avg_norm = float(np.mean(all_norm))
            avg_line += f" {avg_norm:>8.4f}"
            total_stats[k]['per_char_avg'].append(avg_norm)
        avg_line += f" {ensemble['avg']:>8.4f}"
        total_stats['ENS']['per_char_avg'].append(ensemble['avg'])
        print(avg_line)

    # ===== 总体统计报告 =====
    print(f"\n{'=' * 80}")
    print(f"总体统计报告")
    print(f"{'=' * 80}")
    print(f"测试角色数: {len(characters)}")
    print(f"模型数: {len(models)} + ENSEMBLE")
    print(f"sigmoid归一化模型: {needs_sigmoid_keys}")
    print()

    print(f"{'模型':<20} {'平均归一化分':>12} {'关键点胜出':>12}")
    print(f"{'-' * 50}")
    all_model_keys = sorted(models.keys())
    for k in all_model_keys:
        stats = total_stats[k]
        avg = float(np.mean(stats['per_char_avg'])) if stats['per_char_avg'] else 0
        wins = stats['wins']
        total_kps = len(characters) * 17
        print(f"  {models[k]['name']:<18} {avg:>12.4f} {wins:>6}/{total_kps}")

    ens_avg = float(np.mean(total_stats['ENS']['per_char_avg'])) if total_stats['ENS']['per_char_avg'] else 0
    print(f"  {'ENSEMBLE':<18} {ens_avg:>12.4f}   ---")

    print(f"\n集成来源统计（每个关键点由哪个模型贡献）:")
    for k in sorted(ensemble_source_count.keys(), key=lambda x: ensemble_source_count.get(x, 0), reverse=True):
        count = ensemble_source_count.get(k, 0)
        if count > 0:
            total = len(characters) * 17
            print(f"  {models[k]['name']}: {count}/{total} ({100*count/total:.1f}%)")

    print(f"\n所有对比结果已保存到：{output_dir}")

    # ===== 保存JSON统计结果 =====
    report = {
        'test_characters': characters,
        'models': {k: {'name': models[k]['name'], 'full_name': models[k]['full_name']}
                   for k in models},
        'sigmoid_models': list(needs_sigmoid_keys),
        'per_model_stats': {},
        'ensemble_source_count': ensemble_source_count,
    }
    for k in all_model_keys:
        stats = total_stats[k]
        report['per_model_stats'][k] = {
            'avg_normalized_score': float(np.mean(stats['per_char_avg'])) if stats['per_char_avg'] else 0,
            'keypoint_wins': stats['wins'],
            'per_char_avg': stats['per_char_avg'],
        }
    report['per_model_stats']['ENSEMBLE'] = {
        'avg_normalized_score': ens_avg,
        'per_char_avg': total_stats['ENS']['per_char_avg'],
    }

    report_path = os.path.join(output_dir, 'comparison_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"统计报告已保存: {report_path}")


if __name__ == "__main__":
    main()
