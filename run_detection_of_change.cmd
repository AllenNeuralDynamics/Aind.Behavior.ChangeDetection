@echo off
setlocal

cd /d "%~dp0"

call build_extensions.cmd
if errorlevel 1 exit /b 1

cd /d "%~dp0src"
"..\bonsai\Bonsai.exe" "DetectionOfChange_with_template_and_mpe_comp.bonsai"
