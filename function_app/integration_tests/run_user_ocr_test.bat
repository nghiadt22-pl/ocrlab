@echo off
echo Running OCR test for specific user with real documents...

rem Run the test script (environment variables are set in the script)
cd %~dp0
python test_user_ocr.py

rem Check exit code
if %errorlevel% equ 0 (
    echo Test completed successfully!
) else (
    echo Test failed!
)

pause 