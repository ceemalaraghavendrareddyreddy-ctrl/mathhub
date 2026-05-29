@echo off
title MathHub — Math App

:: =========================================
::  Anthropic key disabled (no credits)
::  Using Google Gemini (FREE) instead
:: =========================================
set ANTHROPIC_API_KEY=

echo.
echo  ==========================================
echo    MathHub — One Stop Math Solution
echo  ==========================================
echo.
echo  Starting app... please wait.
echo.
cd /d "%~dp0"
start "" "http://127.0.0.1:5050"
python app.py
pause
