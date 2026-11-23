@echo off
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo Python 3.10+ is not on PATH. Install Python and run this file again.
  pause
  exit /b 1
)
python -c "import streamlit,pandas,plotly,openpyxl" 2>nul || python -m pip install -r requirements.txt
python -m streamlit run slab_trade_dashboard.py
if errorlevel 1 pause
