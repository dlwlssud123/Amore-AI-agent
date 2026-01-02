@echo off
chcp 65001
cls
title Glow Code AI Agent Launcher

echo ========================================================
echo       ✨ Glow Code AI Agent를 시작합니다...
echo ========================================================
echo.
echo [1] 필수 환경을 점검하고 있습니다...

:: 가상환경이 있다면 활성화 (conda 예시)
call conda activate base 
:: (필요하면 위 주석을 푸세요)

echo [2] 프로그램을 실행합니다. 잠시만 기다려주세요...
echo     (브라우저가 자동으로 열립니다)
echo.

:: 실행 명령어 (src 폴더 안의 app.py 실행)
streamlit run src/app.py

pause