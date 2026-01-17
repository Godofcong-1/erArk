import os
import json
import cv2
import numpy as np
from rtmlib import Wholebody

# COCO 17 Keypoint names (indices 0-16 for body)
COCO_KEYPOINTS = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]

def main():
    # Use CPU by default to ensure stability on all environments unless CUDA is explicitly known to work with ONNXRuntime here
    # Since onnxruntime-gpu was installed, we can try 'cuda' but fall back or just use CPU if it fails inside specific calls?
    # RTMlib will try to use the device specified.
    device = 'cpu'
    
    print(f"Initializing RTM Wholebody on {device}...")
    
    try:
        # Initialize Wholebody (RTMDet + RTMPose)
        wholebody = Wholebody(device=device)
    except Exception as e:
        print(f"Failed to initialize Wholebody: {e}")
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(current_dir)
    base_dir = os.path.join(workspace_root, 'image', '立绘', '干员', '差分')

    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} does not exist.")
        return

    characters = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    print(f"Found {len(characters)} character folders in {base_dir}.")

    count = 0
    updated_count = 0
    
    for i, char_name in enumerate(characters):
        char_dir = os.path.join(base_dir, char_name)
        full_body_path = os.path.join(char_dir, f"{char_name}_全身.png")
        json_path = os.path.join(char_dir, f"{char_name}_body.json")

        if not os.path.exists(full_body_path):
            continue

        # Check if already processed with v2.0
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('version') == '2.0' and data.get('model') == 'rtmlib_wholebody':
                         # print(f"[{i+1}/{len(characters)}] Skipping {char_name}: Already v2.0.")
                         # count += 1 # Count as processed? Or skip count?
                         continue
            except:
                pass # Re-process if corrupt
        
        print(f"[{i+1}/{len(characters)}] Analyzing {char_name}...", end='', flush=True)
        
        try:
            # Read image using numpy to handle unicode paths
            img_array = np.fromfile(full_body_path, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if image is None:
                print(f" Error: Could not read image.")
                continue

            height, width = image.shape[:2]

            # Run inference
            # keypoints: (N, K, 2), scores: (N, K)
            keypoints, scores = wholebody(image)

            landmarks_data = []
            
            if keypoints is None or len(keypoints) == 0:
                print(f" No body detected.", end='')
                # Even if no body detected, we create the file to mark it processed
                output_data = {
                    "version": "2.0",
                    "model": "rtmlib_wholebody",
                    "character": char_name,
                    "source_image": f"{char_name}_全身.png",
                    "image_width": width,
                    "image_height": height,
                    "landmarks": [],
                    "note": "No body detected by RTMPose"
                }
            else:
                # Take the detection with the highest average score if multiple?
                # Or just the first one?
                # Usually checking the scores is good. 
                # Let's take the first one for now as character images usually have one main subject.
                kps = keypoints[0] # (K, 2)
                scs = scores[0]    # (K,)
                
                for idx, (kp, score) in enumerate(zip(kps, scs)):
                    # kp is [x, y] in pixels.
                    # RTMlib outputs valid coordinates. 
                    norm_x = float(kp[0]) / width
                    norm_y = float(kp[1]) / height
                    
                    kp_name = f"KP_{idx}"
                    if idx < len(COCO_KEYPOINTS):
                        kp_name = COCO_KEYPOINTS[idx]
                    
                    landmarks_data.append({
                        "id": idx,
                        "name": kp_name,
                        "x": norm_x,
                        "y": norm_y,
                        "score": float(score),
                        "visibility": float(score) # Mapping score to visibility
                    })

                print(f" {len(landmarks_data)} landmarks found.", end='')
                
                output_data = {
                    "version": "2.0",
                    "model": "rtmlib_wholebody",
                    "character": char_name,
                    "source_image": f"{char_name}_全身.png",
                    "image_width": width,
                    "image_height": height,
                    "landmarks": landmarks_data
                }

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(" Saved.")
            updated_count += 1

        except Exception as e:
            print(f" Failed: {e}")
    
    print(f"Completed analysis. Updated {updated_count} characters.")

if __name__ == "__main__":
    main()
