@echo off
:: DevX Windows CMD/PowerShell Bridge
:: This simply forwards to the universal 'devx' shell script via WSL
wsl bash -c "cd $(wslpath -u '%~dp0') && ./devx %*"
