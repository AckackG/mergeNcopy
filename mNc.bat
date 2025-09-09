@echo off
rem 设置活动代码页为 UTF-8，以正确显示Python脚本中的中文字符
chcp 65001 > nul

rem --- 执行 Python 脚本 ---
python.exe mNc.py %*
