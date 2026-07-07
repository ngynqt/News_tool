@echo off
title Cafef AI Facebook Poster Launcher
echo =======================================================
echo   KHOI CHAY CONG CU CAO CAFEF & FB AI POSTER
echo =======================================================
echo.
echo [1/2] Dang kiem tra va tu dong cai dat cac thu vien can thiet...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [LOI] Khong the cai dat cac thu vien. Vui long kiem tra xem Python da duoc cai dat chua va da duoc them vao PATH (environment variables).
    pause
    exit /b
)
echo.
echo [2/2] Dang khoi chay giao dien Web UI...
echo (Trinh duyet web se tu dong mo dia chi http://localhost:5000 sau vai giay)
echo.
echo Nhan Ctrl+C tren cua so nay de tat ung dung.
echo -------------------------------------------------------

:: Tu dong mo trinh duyet sau 1.5 giay
start /b cmd /c "timeout /t 2 >nul && start http://localhost:5000"

python app.py
pause
