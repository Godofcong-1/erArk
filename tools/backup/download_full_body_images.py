import os
import sys
import shutil
import time

# 将工作区根目录添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
workspace_root = os.path.dirname(current_dir)
sys.path.append(workspace_root)

# 动态导入下载器模块
# 由于目录结构原因,使用 importlib 直接加载模块而非普通 import
import importlib.util
spec = importlib.util.spec_from_file_location("downloader", os.path.join(workspace_root, 'tools', 'MCP', 'prts_character_downloader', 'downloader.py'))
downloader_module = importlib.util.module_from_spec(spec)
sys.modules["downloader"] = downloader_module
spec.loader.exec_module(downloader_module)

PRTSCharacterDownloader = downloader_module.PRTSCharacterDownloader

def main():
    """
    主函数：批量下载干员全身立绘并重命名原有立绘为半身版本
    
    功能说明：
    1. 遍历所有干员差分目录
    2. 为缺少全身立绘的干员下载图片
    3. 将原有的 {角色名}.png 重命名为 {角色名}_半身.png
    4. 下载的图片保存为 {角色名}_全身.png
    """
    # 初始化下载器实例
    downloader = PRTSCharacterDownloader()
    
    # 定义目标目录：干员差分立绘存放位置
    base_dir = os.path.join(workspace_root, 'image', '立绘', '干员', '差分')
    # 临时下载目录：避免直接操作目标目录
    temp_dir = os.path.join(workspace_root, 'temp_download')
    
    # 验证基础目录是否存在
    if not os.path.exists(base_dir):
        print(f"错误：目录不存在 {base_dir}")
        return

    # 创建临时下载目录
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # 获取所有角色目录列表（每个子目录代表一个角色）
    characters = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    print(f"找到 {len(characters)} 个角色需要处理。")
    
    # 遍历所有角色目录进行批量处理
    for i, char_name in enumerate(characters):
        char_dir = os.path.join(base_dir, char_name)
        
        # 定义三个关键文件路径
        full_body_target = os.path.join(char_dir, f"{char_name}_全身.png")  # 全身立绘目标路径
        half_body_target = os.path.join(char_dir, f"{char_name}_半身.png")  # 半身立绘目标路径
        original_image = os.path.join(char_dir, f"{char_name}.png")        # 原始立绘路径
        
        print(f"\n[{i+1}/{len(characters)}] 正在处理角色：{char_name}...")
        
        # ========== 步骤1：下载全身立绘（如果不存在） ==========
        if not os.path.exists(full_body_target):
            print(f"正在为 {char_name} 下载全身立绘...")
            
            # 调用下载器下载图片到临时目录
            # 下载器会将文件保存为 {char_name}_立绘.png 格式
            success = downloader.download_character_image(char_name, temp_dir)
            
            # 查找所有可能的下载文件（支持不同扩展名）
            # 下载器实际文件名格式：{character_name}_立绘{file_ext}
            possible_files = [f for f in os.listdir(temp_dir) if f.startswith(f"{char_name}_立绘")]
            
            # 如果下载成功且找到了文件，移动到目标位置
            if success and possible_files:
                src_file = os.path.join(temp_dir, possible_files[0])
                print(f"移动文件：{src_file} -> {full_body_target}")
                shutil.move(src_file, full_body_target)
            else:
                print(f"下载失败或未找到 {char_name} 的图片文件")
        else:
            print(f"{char_name} 的全身立绘已存在，跳过下载")
        
        # 请求间隔限制，避免对服务器造成压力
        time.sleep(1)

        # ========== 步骤2：重命名原始立绘为半身版本 ==========
        if os.path.exists(original_image):
            # 只有在半身版本不存在时才执行重命名
            if not os.path.exists(half_body_target):
                print(f"重命名原始立绘为半身版本：{original_image} -> {half_body_target}")
                os.rename(original_image, half_body_target)
            else:
                # 安全提示：两个文件都存在时不进行操作
                print(f"警告：{original_image} 和 {half_body_target} 同时存在。为安全起见保留两者。")
        elif os.path.exists(half_body_target):
            print(f"{char_name} 的半身立绘已存在")
        else:
            print(f"未找到 {char_name} 的原始立绘文件（期望路径：{original_image}）")

    # ========== 清理临时目录 ==========
    if os.path.exists(temp_dir):
        try:
            # 取消注释以启用自动清理临时目录
            # shutil.rmtree(temp_dir)
            pass
        except:
            pass
    
    print("\n批量处理完成。")

if __name__ == "__main__":
    main()

