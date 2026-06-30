@echo off
echo Starting Stock Portfolio Analyzer...
echo.
echo Opening in browser: http://localhost:8501
echo Press Ctrl+C to stop
echo.
cd /d "%~dp0"
streamlit run app.py
pause
