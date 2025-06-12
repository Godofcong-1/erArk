@echo off
REM PRTS角色立绘下载器 MCP服务器启动脚本 (Windows)

echo 正在启动 PRTS角色立绘下载器 MCP服务器...
echo ================================================

REM 检查是否在虚拟环境中
if defined VIRTUAL_ENV (
    echo 检测到虚拟环境: %VIRTUAL_ENV%
) else (
    echo 警告: 未检测到虚拟环境，建议在虚拟环境中运行
)

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装或不在PATH中
    pause
    exit /b 1
)

echo 检查依赖...

REM 尝试安装MCP依赖
pip show mcp >nul 2>&1
if %errorlevel% neq 0 (
    echo MCP库未安装，正在安装...
    pip install mcp
    if %errorlevel% neq 0 (
        echo 警告: MCP库安装失败，将使用独立模式
    )
)

echo 启动服务器...
python start_server.py

pause
