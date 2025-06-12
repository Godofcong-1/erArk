# PRTS角色立绘下载器 MCP服务器

这是一个Model Context Protocol (MCP) 服务器，用于从PRTS网站下载明日方舟角色的立绘图片。

## 功能特性

- **多种下载方式**：支持MediaWiki API查询、剧情角色页面抓取、直接URL构建等多种方式
- **批量下载**：支持同时下载多个角色的立绘图片
- **URL搜索**：可以仅搜索图片URL而不下载
- **特殊角色支持**：预定义了一些特殊角色的图片映射

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 作为MCP服务器运行

```bash
python -m prts_character_downloader
```

### 独立运行（测试）

```python
from prts_character_downloader.downloader import PRTSCharacterDownloader

downloader = PRTSCharacterDownloader()

# 下载单个角色
success = downloader.download_character_image("阿米娅")

# 批量下载
characters = ["阿米娅", "陈", "德克萨斯"]
results = downloader.batch_download_characters(characters)

# 仅搜索URL
url = downloader.search_character_image_url("阿米娅")
```

## MCP工具

### 1. download_character_image

下载单个角色的立绘图片。

**参数：**
- `character_name` (string, 必需): 要下载立绘的角色名称（中文）
- `save_dir` (string, 可选): 保存图片的目录路径，默认为 "downloaded_images"

**返回：**
- 成功或失败的消息

### 2. batch_download_characters  

批量下载多个角色的立绘图片。

**参数：**
- `character_names` (array, 必需): 要下载立绘的角色名称列表（中文）
- `save_dir` (string, 可选): 保存图片的目录路径，默认为 "downloaded_images"
- `delay_seconds` (number, 可选): 每次下载之间的延迟秒数，默认为1秒

**返回：**
- 批量下载的结果统计和详细状态

### 3. search_character_image_url

仅搜索角色立绘图片的URL，不下载。

**参数：**
- `character_name` (string, 必需): 要搜索立绘的角色名称（中文）

**返回：**
- 找到的图片URL或未找到的消息

## 下载策略

下载器使用以下策略来查找角色立绘：

1. **特殊角色检查**：首先检查预定义的特殊角色映射表
2. **MediaWiki API查询**：使用PRTS网站的API搜索匹配的图片文件
3. **剧情角色页面抓取**：从剧情角色一览页面解析HTML获取图片链接
4. **直接URL构建**：尝试构建可能的图片URL并验证其有效性

## 文件结构

```
prts_character_downloader/
├── __init__.py          # 包初始化文件
├── __main__.py          # 主入口点
├── server.py            # MCP服务器实现
├── downloader.py        # 核心下载功能
├── requirements.txt     # Python依赖
├── mcp.json            # MCP服务器配置
└── README.md           # 说明文档
```

## 注意事项

1. **请求频率限制**：为了避免对PRTS网站造成过大压力，批量下载时会在每次请求之间添加延迟
2. **网络连接**：需要稳定的网络连接来访问PRTS网站
3. **图片格式**：下载的图片通常为PNG格式，会自动检测并设置正确的文件扩展名
4. **目录权限**：确保程序有权限在指定目录创建文件和文件夹

## 许可证

MIT License
