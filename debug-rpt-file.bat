@echo off
echo Crystal Reports File Diagnostics
echo =================================
echo.

if not exist "RptToXml.exe" (
    echo ERROR: RptToXml.exe not found in current directory
    echo Please copy RptToXml.exe to this folder first
    pause
    exit /b 1
)

echo Please drag and drop your .rpt file onto this window and press Enter:
set /p rpt_file="RPT File Path: "

if not exist "%rpt_file%" (
    echo ERROR: File not found: %rpt_file%
    pause
    exit /b 1
)

echo.
echo Testing Crystal Reports file: %rpt_file%
echo ==========================================

echo.
echo Step 1: Running RptToXml.exe...
echo --------------------------------
RptToXml.exe "%rpt_file%" "debug_output.xml" --verbose

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: RptToXml.exe failed with error code %ERRORLEVEL%
    echo This indicates an issue with the .rpt file
    pause
    exit /b 1
)

echo.
echo Step 2: Analyzing XML output...
echo ------------------------------

if not exist "debug_output.xml" (
    echo ERROR: No XML file was created
    echo The .rpt file may be corrupted or incompatible
    pause
    exit /b 1
)

for %%A in ("debug_output.xml") do set xml_size=%%~zA
echo XML file size: %xml_size% bytes

if %xml_size% LSS 1000 (
    echo WARNING: XML file is very small - possible parsing issue
    echo.
    echo XML Content:
    echo ------------
    type "debug_output.xml"
) else (
    echo SUCCESS: XML file looks good
    echo.
    echo First 500 characters of XML:
    echo ----------------------------
    powershell -Command "Get-Content 'debug_output.xml' -Raw | Select-Object -First 1 | ForEach-Object { $_.Substring(0, [Math]::Min(500, $_.Length)) }"
)

echo.
echo Step 3: Checking for common issues...
echo ------------------------------------

findstr /i "error" "debug_output.xml" > nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Found 'error' in XML content
    findstr /i "error" "debug_output.xml"
)

findstr /i "exception" "debug_output.xml" > nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Found 'exception' in XML content
    findstr /i "exception" "debug_output.xml"
)

findstr /i "<report_info>" "debug_output.xml" > nul
if %ERRORLEVEL% EQU 0 (
    echo GOOD: Found report_info section
) else (
    echo WARNING: Missing report_info section
)

findstr /i "<sections>" "debug_output.xml" > nul
if %ERRORLEVEL% EQU 0 (
    echo GOOD: Found sections
) else (
    echo WARNING: Missing sections
)

echo.
echo ========================================
echo DIAGNOSIS COMPLETE
echo ========================================
echo.
echo If you see warnings above, try a different .rpt file
echo The XML file 'debug_output.xml' contains the full output
echo.
pause 