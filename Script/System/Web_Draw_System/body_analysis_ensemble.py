"""
集成方案批量身体部位识别工具

功能说明：
使用7个姿态估计模型的集成方案，对所有角色立绘进行身体关键点检测。
对每个关键点，取所有模型中归一化置信度最高的模型结果。

模型列表：
A. Wholebody balanced  = YOLOX-m + RTMW-dw-x-l@256x192 (133→17)
B. Body performance    = YOLOX-x + RTMPose-x@384x288 (原生17kp)
C. Wholebody perf      = YOLOX-m + RTMW-dw-x-l@384x288 (133→17, sigmoid归一化)
D. YOLO11x-pose        = ultralytics单阶段模型 (原生17kp, COCO训练)
E. BodyWithFeet perf   = YOLOX-x + RTMPose-x-halpe26@384x288 (26→17kp)
F. RTMO-l              = 单阶段姿态估计 (640x640, 原生17kp)
G. Custom最大精度      = YOLOX-x + RTMW-dw-x-l@384x288 (最强检测器+最强姿态, sigmoid归一化)

输入：image/立绘/干员/ 和 image/立绘/特殊NPC/ 下的角色全身图片
输出：每个角色文件夹中的 {角色名}_body.json（v2.0格式，model="ensemble"）
"""

import os
import sys
import json
import cv2
import numpy as np
import time
import traceback

# --- 将 pip 安装的 NVIDIA CUDA 12 DLL 加入搜索路径 (Windows GPU 加速所需) ---
_site_packages = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", "nvidia")
if os.path.isdir(_site_packages):
    for _sub in os.listdir(_site_packages):
        _bin = os.path.join(_site_packages, _sub, "bin")
        if os.path.isdir(_bin):
            os.add_dll_directory(_bin)
            os.environ["PATH"] = _bin + os.pathsep + os.environ.get("PATH", "")

# COCO 17 关键点名称
COCO_KEYPOINTS = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]


def sigmoid(x):
    """
    Sigmoid函数，将logit值转为0-1概率

    输入：x: float或numpy.ndarray - logit值
    输出：float或numpy.ndarray - 0-1之间的概率值
    """
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))


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
        results: dict - {model_key: {'kps': ndarray(17,2), 'scores': ndarray(17)}}
        needs_sigmoid_keys: set - 需要sigmoid的模型key集合
    输出：dict - 集成结果
    功能：对每个关键点独立选择最优模型结果
    """
    ens_kps = np.zeros((17, 2))
    ens_norm_scores = np.zeros(17)
    source_models = []

    for kp_idx in range(17):
        best_norm_score = -1
        best_key = ''
        best_kp = np.zeros(2)

        for key, res in results.items():
            if res is None or res['scores'] is None:
                continue
            raw_score = res['scores'][kp_idx]
            norm_score = normalize_scores(np.array([raw_score]), key, needs_sigmoid_keys)[0]

            if norm_score > best_norm_score:
                best_norm_score = norm_score
                best_key = key
                best_kp = res['kps'][kp_idx].copy()

        ens_kps[kp_idx] = best_kp
        ens_norm_scores[kp_idx] = best_norm_score
        source_models.append(best_key)

    return {
        'kps': ens_kps,
        'norm_scores': ens_norm_scores,
        'source_models': source_models,
        'avg': float(np.mean(ens_norm_scores))
    }


def run_yolo11_inference(model, image):
    """
    使用YOLO11-pose模型进行推理

    输入：
        model: ultralytics.YOLO - YOLO模型实例
        image: numpy.ndarray - BGR图像
    输出：tuple(ndarray, ndarray) - (关键点坐标(17,2), 置信度(17,)) 或 (None, None)
    """
    results = model(image, verbose=False, device='cuda')
    r = results[0]
    if r.keypoints is not None and len(r.keypoints.data) > 0:
        if r.boxes is not None and len(r.boxes.data) > 0:
            confs = r.boxes.conf.cpu().numpy()
            best_idx = np.argmax(confs)
        else:
            best_idx = 0
        kp_data = r.keypoints.data[best_idx].cpu().numpy()
        kps = kp_data[:, :2]
        scores = kp_data[:, 2]
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


def init_models():
    """
    初始化所有7个模型

    输入：无
    输出：tuple(dict, set) - (模型字典, 需要sigmoid归一化的模型key集合)
    """
    from rtmlib import Wholebody, Body, BodyWithFeet, RTMO, Custom

    backend = 'onnxruntime'
    device = 'cuda'
    models = {}
    needs_sigmoid_keys = set()

    # A: Wholebody balanced (基线)
    print("[A] Wholebody balanced: YOLOX-m + RTMW@256x192...", end='', flush=True)
    try:
        models['A'] = {
            'name': 'A:WB_bal',
            'model': Wholebody(mode='balanced', backend=backend, device=device),
            'type': 'rtmlib', 'extract_17': True,
        }
        needs_sigmoid_keys.add('A')  # 可能输出logit，稍后自动检测
        print(" OK")
    except Exception as e:
        print(f" 失败: {e}")

    # B: Body performance
    print("[B] Body performance: YOLOX-x + RTMPose-x@384x288...", end='', flush=True)
    try:
        models['B'] = {
            'name': 'B:Body_perf',
            'model': Body(mode='performance', backend=backend, device=device),
            'type': 'rtmlib', 'extract_17': False,
        }
        print(" OK")
    except Exception as e:
        print(f" 失败: {e}")

    # C: Wholebody performance
    print("[C] Wholebody performance: YOLOX-m + RTMW@384x288...", end='', flush=True)
    try:
        models['C'] = {
            'name': 'C:WB_perf',
            'model': Wholebody(mode='performance', backend=backend, device=device),
            'type': 'rtmlib', 'extract_17': True,
        }
        needs_sigmoid_keys.add('C')
        print(" OK")
    except Exception as e:
        print(f" 失败: {e}")

    # D: YOLO11x-pose
    print("[D] YOLO11x-pose: 单阶段 (COCO训练)...", end='', flush=True)
    try:
        from ultralytics import YOLO
        yolo_model = YOLO('yolo11x-pose.pt')
        models['D'] = {
            'name': 'D:YOLO11x',
            'model': yolo_model,
            'type': 'yolo11', 'extract_17': False,
        }
        print(" OK")
    except Exception as e:
        print(f" 失败: {e}")

    # E: BodyWithFeet performance
    print("[E] BodyWithFeet performance: YOLOX-x + halpe26@384x288...", end='', flush=True)
    try:
        models['E'] = {
            'name': 'E:BWF_perf',
            'model': BodyWithFeet(mode='performance', backend=backend, device=device),
            'type': 'rtmlib', 'extract_17': True,
        }
        print(" OK")
    except Exception as e:
        print(f" 失败: {e}")

    # F: RTMO-l
    print("[F] RTMO-l: 单阶段 (640x640)...", end='', flush=True)
    try:
        rtmo_url = 'https://download.openmmlab.com/mmpose/v1/projects/rtmo/onnx_sdk/rtmo-l_16xb16-600e_body7-640x640-b37118ce_20231211.zip'
        rtmo_model = RTMO(
            onnx_model=rtmo_url,
            model_input_size=(640, 640),
            backend=backend, device=device
        )
        models['F'] = {
            'name': 'F:RTMO-l',
            'model': rtmo_model,
            'type': 'rtmo', 'extract_17': False,
        }
        print(" OK")
    except Exception as e:
        print(f" 失败: {e}")
        traceback.print_exc()

    # G: Custom最大精度
    print("[G] Custom: YOLOX-x + RTMW@384x288...", end='', flush=True)
    try:
        det_url = 'https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/yolox_x_8xb8-300e_humanart-a39d44ed.zip'
        pose_url = 'https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/rtmw-dw-x-l_simcc-cocktail14_270e-384x288_20231122.zip'
        models['G'] = {
            'name': 'G:Custom_max',
            'model': Custom(
                det_class='YOLOX', det=det_url, det_input_size=(640, 640),
                pose_class='RTMPose', pose=pose_url, pose_input_size=(288, 384),
                backend=backend, device=device
            ),
            'type': 'rtmlib', 'extract_17': True,
        }
        needs_sigmoid_keys.add('G')
        print(" OK")
    except Exception as e:
        print(f" 失败: {e}")
        traceback.print_exc()

    return models, needs_sigmoid_keys


def run_model_inference(minfo, key, image):
    """
    对单个模型运行推理

    输入：
        minfo: dict - 模型信息字典
        key: str - 模型标识符
        image: numpy.ndarray - BGR图像
    输出：dict或None - {'kps': ndarray(17,2), 'scores': ndarray(17)} 或 None
    """
    try:
        if minfo['type'] == 'yolo11':
            kps_17, scores_17 = run_yolo11_inference(minfo['model'], image)
        elif minfo['type'] == 'rtmo':
            kps_17, scores_17 = run_rtmo_inference(minfo['model'], image)
        else:
            kps, scores = minfo['model'](image)
            if kps is not None and len(kps) > 0:
                kps_17 = kps[0][:17]
                scores_17 = scores[0][:17]
            else:
                kps_17, scores_17 = None, None

        if kps_17 is not None and scores_17 is not None:
            return {'kps': kps_17, 'scores': scores_17}
    except Exception:
        pass
    return None


def process_character(char_name, full_body_path, json_path, models, needs_sigmoid_keys):
    """
    处理单个角色：运行所有模型并生成集成结果JSON

    输入：
        char_name: str - 角色名
        full_body_path: str - 全身图像路径
        json_path: str - 输出JSON路径
        models: dict - 模型字典
        needs_sigmoid_keys: set - 需要sigmoid的模型key集合
    输出：bool - 是否成功处理
    """
    # 加载图像
    img_array = np.fromfile(full_body_path, np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if image is None:
        return False

    h, w = image.shape[:2]

    # 运行所有模型
    results = {}
    for key in sorted(models.keys()):
        res = run_model_inference(models[key], key, image)
        results[key] = res

    # 检查是否至少有一个模型成功
    valid_results = {k: v for k, v in results.items() if v is not None}
    if not valid_results:
        # 所有模型都失败，生成空结果
        output_data = {
            "version": "2.0",
            "model": "ensemble",
            "character": char_name,
            "source_image": f"{char_name}_全身.png",
            "image_width": w,
            "image_height": h,
            "landmarks": [],
            "note": "所有模型均未检测到人体"
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        return True

    # 构建集成结果
    ensemble = build_ensemble(results, needs_sigmoid_keys)

    # 构建landmarks数据
    landmarks_data = []
    for idx in range(17):
        kp = ensemble['kps'][idx]
        norm_x = float(kp[0]) / w
        norm_y = float(kp[1]) / h
        norm_score = float(ensemble['norm_scores'][idx])
        source = ensemble['source_models'][idx]

        landmarks_data.append({
            "id": idx,
            "name": COCO_KEYPOINTS[idx],
            "x": norm_x,
            "y": norm_y,
            "score": norm_score,
            "visibility": norm_score,
            "source_model": source,
        })

    # 统计各模型成功率和来源分布
    source_count = {}
    for src in ensemble['source_models']:
        source_count[src] = source_count.get(src, 0) + 1

    model_scores = {}
    for key, res in results.items():
        if res is not None:
            norm_s = normalize_scores(res['scores'][:17], key, needs_sigmoid_keys)
            model_scores[key] = float(np.mean(norm_s))

    output_data = {
        "version": "2.0",
        "model": "ensemble",
        "ensemble_models": list(sorted(models.keys())),
        "character": char_name,
        "source_image": f"{char_name}_全身.png",
        "image_width": w,
        "image_height": h,
        "ensemble_avg_score": ensemble['avg'],
        "per_model_avg": model_scores,
        "source_distribution": source_count,
        "landmarks": landmarks_data,
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    return True


def collect_characters(base_dirs):
    """
    收集所有待处理的角色信息

    输入：base_dirs: list[str] - 角色目录列表
    输出：list[tuple(str, str, str)] - [(角色名, 全身图路径, JSON输出路径), ...]
    """
    characters = []
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            print(f"目录不存在，跳过: {base_dir}")
            continue
        for d in sorted(os.listdir(base_dir)):
            char_dir = os.path.join(base_dir, d)
            if not os.path.isdir(char_dir):
                continue
            full_body_path = os.path.join(char_dir, f"{d}_全身.png")
            json_path = os.path.join(char_dir, f"{d}_body.json")
            if os.path.exists(full_body_path):
                characters.append((d, full_body_path, json_path))
    return characters


def main():
    """
    主函数：使用集成方案批量处理所有角色

    执行流程：
    1. 初始化7个模型
    2. 收集干员和特殊NPC目录下所有角色
    3. 对每个角色运行集成方案并保存JSON
    4. 输出统计信息
    """
    start_time = time.time()

    # 构建路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(current_dir)
    base_dirs = [
        os.path.join(workspace_root, 'image', '立绘', '干员'),
        os.path.join(workspace_root, 'image', '立绘', '特殊NPC'),
    ]

    # 初始化模型
    print("=" * 70)
    print("集成方案批量处理 - 初始化模型")
    print("=" * 70)
    models, needs_sigmoid_keys = init_models()
    init_time = time.time() - start_time
    print(f"\n模型初始化完成: {len(models)}个模型, 耗时{init_time:.1f}s")
    print(f"sigmoid归一化模型: {needs_sigmoid_keys}")

    if len(models) == 0:
        print("错误：没有成功加载任何模型")
        return

    # 自动检测A模型是否真的需要sigmoid（用第一张图测试）
    # 在首次推理时检测，见下方

    # 收集所有角色
    characters = collect_characters(base_dirs)
    print(f"\n共找到 {len(characters)} 个角色待处理")
    for bd in base_dirs:
        dir_name = os.path.basename(bd)
        count = sum(1 for c in characters if bd in c[1])
        print(f"  {dir_name}: {count}个")

    # 处理所有角色
    print(f"\n{'=' * 70}")
    print("开始批量处理")
    print(f"{'=' * 70}")

    success_count = 0
    fail_count = 0
    skip_count = 0
    auto_sigmoid_checked = False
    process_start = time.time()

    for i, (char_name, full_body_path, json_path) in enumerate(characters):
        elapsed = time.time() - process_start
        if i > 0:
            avg_per_char = elapsed / i
            remaining = avg_per_char * (len(characters) - i)
            eta_str = f" ETA:{remaining/60:.0f}min"
        else:
            eta_str = ""

        print(f"[{i+1}/{len(characters)}] {char_name}...{eta_str}", end='', flush=True)

        # 首次推理时自动检测A模型是否需要sigmoid
        if not auto_sigmoid_checked and 'A' in models:
            img_array = np.fromfile(full_body_path, np.uint8)
            test_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if test_img is not None:
                test_res = run_model_inference(models['A'], 'A', test_img)
                if test_res is not None:
                    max_score = float(np.max(test_res['scores'][:17]))
                    if max_score <= 1.05:
                        needs_sigmoid_keys.discard('A')
                        print(f"\n  [自动检测] A模型分数范围正常(max={max_score:.4f})，移出sigmoid集合")
                    else:
                        print(f"\n  [自动检测] A模型输出logit(max={max_score:.4f})，保留sigmoid")
            auto_sigmoid_checked = True
            print(f"  sigmoid模型: {needs_sigmoid_keys}")
            print(f"[{i+1}/{len(characters)}] {char_name}...", end='', flush=True)

        try:
            ok = process_character(char_name, full_body_path, json_path, models, needs_sigmoid_keys)
            if ok:
                success_count += 1
                print(f" OK")
            else:
                fail_count += 1
                print(f" 图像加载失败")
        except Exception as e:
            fail_count += 1
            print(f" 错误: {e}")

    # 完成统计
    total_time = time.time() - start_time
    process_time = time.time() - process_start
    print(f"\n{'=' * 70}")
    print(f"批量处理完成")
    print(f"{'=' * 70}")
    print(f"总角色数: {len(characters)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"模型初始化: {init_time:.1f}s")
    print(f"处理耗时: {process_time:.1f}s ({process_time/60:.1f}min)")
    print(f"总耗时: {total_time:.1f}s ({total_time/60:.1f}min)")
    if success_count > 0:
        print(f"平均每角色: {process_time/success_count:.2f}s")


if __name__ == "__main__":
    main()
