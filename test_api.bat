@echo off
setlocal enabledelayedexpansion

:: OCR Lab API Test Script for Windows (Automated)

:: Define path to env file
set ENV_FILE=function_app\.env

:: Define common variables
set FUNCTION_APP_URL=http://localhost:7071
set USER_ID=user_2tpkxxIIKb0ghgy1HLYZkEsUqFA
set TEST_PDF=test_pdfs\1742180735323.pdf
set CONTAINER=test-upload
set AUTO_CLEANUP=NO

echo === Testing OCR Lab API Endpoints ===

:: 1. List folders
echo.
echo 1. List folders:
curl -X GET "%FUNCTION_APP_URL%/api/folders" -H "x-user-id: %USER_ID%" > folders_response.json
type folders_response.json

:: Set default folder ID
set FOLDER_ID=10

:: Extract first folder ID from response - simplified method
for /f "tokens=1,2 delims=:," %%a in ('findstr "\"id\"" folders_response.json') do (
  if "%%a"==" \"id\"" (
    set FOLDER_ID=%%b
    set FOLDER_ID=!FOLDER_ID: =!
    goto :found_folder
  )
)

:found_folder
echo Using folder ID: %FOLDER_ID%

:: 2. Create a test folder automatically
echo.
echo 2. Creating test folder:
set RANDOM_SUFFIX=%RANDOM%
curl -X POST "%FUNCTION_APP_URL%/api/folders" ^
  -H "Content-Type: application/json" ^
  -H "x-user-id: %USER_ID%" ^
  -H "x-user-email: adminn@example.com" ^
  -d "{\"name\":\"Automated Test Folder %RANDOM_SUFFIX%\",\"parent_id\":null}" > folder_response.json
type folder_response.json

:: Extract folder ID from response with better parsing
set NEW_FOLDER_ID=
for /f "tokens=1,2 delims=:," %%a in ('findstr "\"id\"" folder_response.json') do (
  if "%%a"==" \"id\"" (
    set NEW_FOLDER_ID=%%b
    set NEW_FOLDER_ID=!NEW_FOLDER_ID: =!
    goto :got_new_folder
  )
)

:got_new_folder
if defined NEW_FOLDER_ID (
  set FOLDER_ID=%NEW_FOLDER_ID%
  echo Created new folder with ID: %FOLDER_ID%
)

:: 3. List files in folder
echo.
echo 3. List files in folder %FOLDER_ID%:
curl -X GET "%FUNCTION_APP_URL%/api/files?folder_id=%FOLDER_ID%" ^
  -H "x-user-id: %USER_ID%"

:: 4. Upload file - create a simplified file path
echo.
echo 4. Upload file:
curl -X POST "%FUNCTION_APP_URL%/api/files" ^
  -H "Content-Type: application/json" ^
  -H "x-user-id: %USER_ID%" ^
  -d "{\"name\":\"test.pdf\",\"folder_id\":%FOLDER_ID%,\"mime_type\":\"application/pdf\",\"size_bytes\":12345,\"blob_path\":\"test.pdf\"}" > file_response.json
type file_response.json

:: Extract file ID from response with better parsing
set FILE_ID=
for /f "tokens=1,2 delims=:," %%a in ('findstr "\"id\"" file_response.json') do (
  if "%%a"==" \"id\"" (
    set FILE_ID=%%b
    set FILE_ID=!FILE_ID: =!
    goto :got_file_id
  )
)

:got_file_id
if not defined FILE_ID (
  echo File upload failed or ID extraction failed
  set FILE_ID=0
) else (
  echo Uploaded file with ID: %FILE_ID%
)

:: 5. Check processing status if file ID was obtained
if %FILE_ID% NEQ 0 (
  echo.
  echo 5. Check processing status:
  curl -X GET "%FUNCTION_APP_URL%/api/processing-status/%FILE_ID%" ^
    -H "x-user-id: %USER_ID%"
) else (
  echo Skipping processing status check due to missing file ID
)

:: 6. Search query
echo.
echo 6. Search query:
curl -X POST "%FUNCTION_APP_URL%/api/query" ^
  -H "Content-Type: application/json" ^
  -H "x-user-id: %USER_ID%" ^
  -d "{\"query\":\"risk management\",\"top\":5}"

:: Check if environment variables file exists
echo.
echo Checking environment variables in: %ENV_FILE%
if exist "%ENV_FILE%" (
  echo Environment file found: %ENV_FILE%
) else (
  echo WARNING: Environment file not found: %ENV_FILE%
)

:: 7. Vector search
echo.
echo 7. Vector search:
curl -X POST "%FUNCTION_APP_URL%/api/vector_search" ^
  -H "Content-Type: application/json" ^
  -H "x-user-id: %USER_ID%" ^
  -d "{\"query\":\"banking sector challenges\",\"top_k\":5}"

:: 8. Get usage statistics
echo.
echo 8. Get usage statistics:
curl -X GET "%FUNCTION_APP_URL%/api/usage" ^
  -H "x-user-id: %USER_ID%"

:: 9. Process document - check if test file exists
echo.
echo 9. Process document:
if exist "%TEST_PDF%" (
  echo Found test file: %TEST_PDF%
  curl -X POST "%FUNCTION_APP_URL%/api/process_document?title=Test%%20Document" ^
    -H "Content-Type: application/pdf" ^
    -H "x-user-id: %USER_ID%" ^
    --data-binary "@%TEST_PDF%"
) else (
  echo WARNING: Test PDF file not found: %TEST_PDF%
)

:: Environment variable status
echo.
echo You need these in your .env file for vector search and document processing:
echo   AZURE_OPENAI_API_VERSION=2023-05-15
echo   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
echo.

:: Automatic cleanup
echo === Auto cleanup ===
if /i "%AUTO_CLEANUP%"=="YES" (
  :: Delete file if ID exists
  if %FILE_ID% NEQ 0 (
    echo.
    echo 10. Deleting file ID %FILE_ID%:
    curl -X DELETE "%FUNCTION_APP_URL%/api/files/%FILE_ID%" ^
      -H "x-user-id: %USER_ID%"
  )

  :: Delete test folder we created
  if defined NEW_FOLDER_ID (
    echo.
    echo 11. Deleting folder ID %FOLDER_ID%:
    curl -X DELETE "%FUNCTION_APP_URL%/api/folders/%FOLDER_ID%" ^
      -H "x-user-id: %USER_ID%"
  )
)

echo.
echo === Testing completed ===

:: Clean up temporary files
if exist folder_response.json del folder_response.json
if exist file_response.json del file_response.json
if exist folders_response.json del folders_response.json