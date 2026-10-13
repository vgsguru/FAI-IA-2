@echo off
title AegisMed - Hospital Delivery Fleet Commander (Guru)
echo =====================================================================
echo  AEGIS-MED // AUTONOMOUS CLINICAL FLEET COMMANDER
echo  Student: Guru Prasath S ^| Reg No: 113223010101
echo  Subject: 25ML35T / Foundations of Artificial Intelligence
echo  Vel Tech High Tech Dr. Rangarajan Dr. Sakunthala Engineering College
echo =====================================================================
echo Launching standalone GUI software...
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying direct pythoncore path...
    "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" app.py
)
pause
