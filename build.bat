@echo off
python scripts\build.py
if errorlevel 1 exit /b 1
echo.
echo Done. Open index.html in your browser to preview.
