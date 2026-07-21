@echo off
setlocal

cd /d "%~dp0"

echo Building Bonsai Extensions...
dotnet build "src\Extensions.csproj" -c Release
if errorlevel 1 (
    echo.
    echo Build failed. Do not run the experiment until this succeeds.
    exit /b 1
)

copy /Y "src\bin\Release\net472\Extensions.dll" "src\Extensions.dll"
copy /Y "src\bin\Release\net472\Extensions.dll" "bonsai\Extensions.dll"

echo.
echo Extensions.dll built and copied successfully.
