@echo off
REM 自动安装 PyInstaller
pip show pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

REM 查找根目录下的ico文件
set ICON=
for %%i in (*.ico) do set ICON=%%i
if "%ICON%"=="" (
    echo 未找到图标文件.ico，将使用默认图标。
) else (
    echo 已找到图标文件：%ICON%
)

REM 设置主程序入口（如需更换请修改此处）
set MAIN=kookvoice_bot_runtime.py

REM 开始打包
if "%ICON%"=="" (
    pyinstaller --clean --onefile --add-data "config.py;." --add-data "ffmpeg;ffmpeg" --name kook_music_streamer %MAIN%
) else (
    pyinstaller --clean --onefile --add-data "config.py;." --add-data "ffmpeg;ffmpeg" --icon %ICON% --name kook_music_streamer %MAIN%
)

echo.
echo 打包完成！请在 dist 目录下查找 kook_music_streamer.exe
pause 