@echo off
setlocal

:: Get the directory of this batch file
set "DIR=%~dp0"

:: Convert the Windows path to a WSL path
for /f "usebackq tokens=*" %%i in (`wsl wslpath '%DIR%'`) do set "WSL_DIR=%%i"

:: Call python3 inside WSL with the translated path and pass all arguments
wsl python3 "%WSL_DIR%cli/devx.py" %*

endlocal
