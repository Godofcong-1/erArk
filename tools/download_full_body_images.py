import os
import sys
import shutil
import time

# Add workspace root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
workspace_root = os.path.dirname(current_dir)
sys.path.append(workspace_root)
# sys.path.append(os.path.join(workspace_root, 'tools', 'MCP', 'prts_character_downloader'))

import importlib.util
spec = importlib.util.spec_from_file_location("downloader", os.path.join(workspace_root, 'tools', 'MCP', 'prts_character_downloader', 'downloader.py'))
downloader_module = importlib.util.module_from_spec(spec)
sys.modules["downloader"] = downloader_module
spec.loader.exec_module(downloader_module)

PRTSCharacterDownloader = downloader_module.PRTSCharacterDownloader

# from tools.MCP.prts_character_downloader.downloader import PRTSCharacterDownloader

def main():
    downloader = PRTSCharacterDownloader()
    base_dir = os.path.join(workspace_root, 'image', '立绘', '干员', '差分')
    temp_dir = os.path.join(workspace_root, 'temp_download')
    
    if not os.path.exists(base_dir):
        print(f"Error: Directory {base_dir} does not exist.")
        return

    # Create temp dir for downloads
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Get list of character directories
    characters = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    print(f"Found {len(characters)} characters to process.")
    
    # Process only a few for testing first, or all? 
    # The user instruction implies executing the batch logic.
    # Let's process all but handle errors gracefully.
    
    for i, char_name in enumerate(characters):
        char_dir = os.path.join(base_dir, char_name)
        
        full_body_target = os.path.join(char_dir, f"{char_name}_全身.png")
        half_body_target = os.path.join(char_dir, f"{char_name}_半身.png")
        original_image = os.path.join(char_dir, f"{char_name}.png")
        
        print(f"\n[{i+1}/{len(characters)}] Processing {char_name}...")
        
        # 1. Download Full Body if missing
        if not os.path.exists(full_body_target):
            print(f"Downloading full body image for {char_name}...")
            # specific logic to find image
            # The downloader saves as {char_name}_立绘.png in save_dir
            success = downloader.download_character_image(char_name, temp_dir)
            
            downloaded_file = os.path.join(temp_dir, f"{char_name}_立绘.png")
            # Also check for jpg or other formats if png not found, though downloader defaults to checking extension from url
            # The downloader code: 
            # filename = f"{character_name}_立绘{file_ext}"
            
            # We need to find what file was downloaded
            possible_files = [f for f in os.listdir(temp_dir) if f.startswith(f"{char_name}_立绘")]
            
            if success and possible_files:
                src_file = os.path.join(temp_dir, possible_files[0])
                print(f"Move {src_file} to {full_body_target}")
                shutil.move(src_file, full_body_target)
            else:
                print(f"Failed to download or find downloaded image for {char_name}")
        else:
            print(f"Full body image already exists for {char_name}")
        
        # Rate limiting
        time.sleep(1)

        # 2. Rename Original to Half Body
        if os.path.exists(original_image):
            if not os.path.exists(half_body_target):
                print(f"Renaming original image to half body: {original_image} -> {half_body_target}")
                os.rename(original_image, half_body_target)
            else:
                print(f"Warning: Both {original_image} and {half_body_target} exist. Keeping both for safety.")
        elif os.path.exists(half_body_target):
             print(f"Half body image already exists for {char_name}")
        else:
            print(f"No original image found for {char_name} (Expected {original_image})")

    # Cleanup temp dir
    if os.path.exists(temp_dir):
        try:
           # shutil.rmtree(temp_dir) 
           pass
        except:
            pass
    
    print("\nBatch processing complete.")

if __name__ == "__main__":
    main()
