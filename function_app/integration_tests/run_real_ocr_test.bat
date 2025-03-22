@echo off
echo Running real OCR test with Azure Document Intelligence...

rem Set environment variables for the test
rem Replace with your actual connection string for Azure Storage
set AzureWebJobsStorage=your_storage_connection_string_here

rem Run the test
python test_real_ocr.py

rem Check exit code
if %errorlevel% equ 0 (
    echo Test completed successfully!
) else (
    echo Test failed!
)

pause 