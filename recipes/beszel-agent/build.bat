@echo off
mkdir "%PREFIX%\Library\bin"
copy beszel-agent.exe "%PREFIX%\Library\bin\beszel-agent.exe"
if errorlevel 1 exit /b 1
