# PRTS角色立绘下载器 - GitHub Copilot 集成指南

## 🎯 概述

本指南将帮助您将PRTS角色立绘下载器MCP服务器集成到GitHub Copilot中，让您可以在VS Code中直接使用明日方舟角色立绘下载功能。

## ✅ 前置条件

1. ✅ Python 3.9+ 已安装
2. ✅ VS Code 已安装
3. ✅ GitHub Copilot 扩展已安装并激活
4. ✅ MCP库已安装 (`pip install mcp>=1.0.0`)

## 🚀 集成步骤

### 步骤 1: 验证MCP服务器功能

首先确保MCP服务器能正常运行：

```powershell
# 切换到MCP目录
cd "c:/code/era/erArk/tools/MCP"

# 测试模块导入
python -c "from prts_character_downloader.downloader import PRTSCharacterDownloader; print('模块导入成功')"

# 运行功能测试
cd prts_character_downloader
python test_downloader.py
```

### 步骤 2: 配置VS Code设置

您的VS Code设置已自动配置完成！配置位置：
`C:\Users\godof\AppData\Roaming\Code\User\settings.json`

已添加的配置：
```json
{
    // 启用MCP支持
    "chat.mcp.enabled": true,
    
    // MCP服务器配置
    "chat.mcp.servers": {
        "prts-character-downloader": {
            "command": "python",
            "args": ["-m", "prts_character_downloader"],
            "cwd": "c:/code/era/erArk/tools/MCP",
            "env": {
                "PYTHONPATH": "c:/code/era/erArk/tools/MCP"
            }
        }
    }
}
```

### 步骤 3: 重启VS Code

⚠️ **重要**：保存设置文件后，**必须重启VS Code**以使MCP配置生效。

### 步骤 4: 验证集成

1. **检查MCP服务器状态**
   - 重启VS Code后，打开命令面板 (`Ctrl+Shift+P`)
   - 查找MCP相关命令或查看输出面板

2. **使用VS Code任务测试**
   - 按 `Ctrl+Shift+P` → 输入 "Tasks: Run Task"
   - 选择 "测试PRTS下载器" 运行测试

3. **在GitHub Copilot Chat中测试**
   - 打开GitHub Copilot Chat (侧边栏或 `Ctrl+Alt+I`)
   - 尝试以下测试命令：

```
帮我使用PRTS下载器下载莱伊的立绘图片
```

或者：

```
我想搜索塔露拉的立绘URL但不下载
```

## 🛠️ 可用的MCP工具

集成成功后，GitHub Copilot可以调用以下工具：

### 1. 下载单个角色立绘
- **工具名**: `download_character_image`
- **参数**: `character_name` (必需), `save_dir` (可选)
- **示例**: "下载莱伊的立绘"

### 2. 批量下载多个角色立绘
- **工具名**: `batch_download_characters`  
- **参数**: `character_names` (必需), `save_dir` (可选), `delay_seconds` (可选)
- **示例**: "批量下载莱伊、塔露拉、陈的立绘"

### 3. 搜索角色立绘URL
- **工具名**: `search_character_image_url`
- **参数**: `character_name` (必需)
- **示例**: "搜索银灰的立绘URL"

## 📝 使用示例

### 示例1：下载单个角色
```
用户：帮我下载阿米娅的立绘图片
Copilot：我来帮您下载阿米娅的立绘图片...
[调用 download_character_image 工具]
```

### 示例2：批量下载
```
用户：我需要下载几个干员的立绘：莱伊、塔露拉、陈
Copilot：我来帮您批量下载这些干员的立绘...
[调用 batch_download_characters 工具]
```

### 示例3：搜索URL
```
用户：我想查看银灰的立绘URL但不下载
Copilot：让我为您搜索银灰的立绘URL...
[调用 search_character_image_url 工具]
```

## 🔧 故障排除

### 问题1：MCP服务器无法启动

**症状**：VS Code中找不到MCP相关功能或GitHub Copilot无法调用工具
**解决方案**：
1. 检查Python路径是否正确
2. 确保MCP库已正确安装：`pip install mcp>=1.0.0`
3. 验证工作目录路径是否正确
4. 重启VS Code

### 问题2：模块导入错误

**症状**：Python抛出`ModuleNotFoundError`
**解决方案**：
1. 确保工作目录设置为 `c:/code/era/erArk/tools/MCP`
2. 检查PYTHONPATH环境变量设置
3. 在正确目录运行：`python -c "import prts_character_downloader"`

### 问题3：权限问题

**症状**：无法创建下载目录或保存文件
**解决方案**：
1. 确保对目标目录有写入权限
2. 如有必要，以管理员权限运行VS Code

### 问题4：网络连接问题

**症状**：无法下载图片或搜索失败
**解决方案**：
1. 检查网络连接
2. 确认防火墙设置允许Python访问网络
3. 检查代理设置（如果使用代理）

## ⚙️ 高级配置

### 自定义下载目录

修改VS Code设置中的环境变量：

```json
"env": {
    "PYTHONPATH": "c:/code/era/erArk/tools/MCP",
    "PRTS_DOWNLOAD_DIR": "C:/Downloads/PRTS_Characters"
}
```

### 启用调试日志

```json
"env": {
    "PYTHONPATH": "c:/code/era/erArk/tools/MCP",
    "PRTS_DEBUG": "1"
}
```

## 🎮 支持的角色名称

- 使用中文角色名称（如：莱伊、塔露拉、陈、阿米娅等）
- 支持特殊角色映射（已预配置塔露拉等特殊情况）
- 支持常见别名和简称

## 🔄 更新和维护

### 更新MCP服务器
```powershell
cd "c:/code/era/erArk/tools/MCP/prts_character_downloader"
# 更新代码文件后重启VS Code
```

### 重启MCP服务器
修改代码后需要重启VS Code以重新加载MCP服务器。

## 🆘 技术支持

如果遇到问题，请：

1. 检查VS Code开发者控制台的错误信息（`Help` > `Toggle Developer Tools`）
2. 查看VS Code输出面板中的MCP相关日志
3. 运行测试脚本验证功能：`python test_downloader.py`
4. 使用VS Code任务：`Ctrl+Shift+P` → "Tasks: Run Task" → "测试PRTS下载器"

## 📁 文件结构

```
tools/MCP/prts_character_downloader/
├── __init__.py              # 包初始化
├── __main__.py              # 模块入口
├── server.py                # MCP服务器实现
├── downloader.py            # 核心下载功能
├── test_downloader.py       # 功能测试
├── verify_mcp_setup.py      # 集成验证
├── requirements.txt         # 依赖
├── mcp.json                # MCP配置
└── MCP_INTEGRATION_GUIDE.md # 本指南
```

## 🎉 总结

完成以上步骤后，您就可以在GitHub Copilot中直接使用PRTS角色立绘下载功能了！

### 核心优势：
- ✨ 无缝集成到VS Code开发环境
- 🤖 通过自然语言与MCP服务器交互
- 📥 直接在VS Code中下载明日方舟角色立绘
- 🔧 利用GitHub Copilot的智能对话能力
- 🎯 统一的开发工具体验

### 使用流程：
1. 重启VS Code ✅
2. 打开GitHub Copilot Chat
3. 输入自然语言请求（如："下载莱伊的立绘"）
4. Copilot自动调用MCP工具完成任务

祝您使用愉快！如有问题请参考故障排除部分或查看相关日志。
