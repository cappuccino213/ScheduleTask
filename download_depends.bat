@echo off
cd %~dp0
cd  venv\Scripts
call activate.bat
md %~dp0depends
pip download -d "%~dp0depends" -r  "%~dp0requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/
pause
