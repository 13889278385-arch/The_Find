@echo off
REM ============================================================
REM Windows 一键启动脚本
REM ============================================================
REM 作用：
REM 1. 进入脚本所在目录，避免“当前目录不对”导致找不到文件。
REM 2. 自动安装 requirements.txt 中的依赖。
REM 3. 启动 Flask 后端服务。
REM 4. 用 pause 保持窗口不立刻关闭，方便查看报错。

cd /d %~dp0
python -m pip install -r requirements.txt
python app.py
pause
