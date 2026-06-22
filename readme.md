## to run all
powershell -ExecutionPolicy Bypass -File .\run_all.ps1

## to stop all
taskkill /F /IM node.exe /T
taskkill /F /IM python.exe /T