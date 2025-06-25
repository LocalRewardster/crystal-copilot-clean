@echo off
echo Crystal Copilot - Simplified Compilation
echo =========================================

REM Check if we're in the right directory
if not exist "RptToXml.cs" (
    echo ERROR: RptToXml.cs not found in current directory
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo Found RptToXml.cs - checking content...
findstr /n "static.*Main" RptToXml.cs
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Main method found in RptToXml.cs
) else (
    echo ERROR: No Main method found in RptToXml.cs
    echo This might be why compilation is failing
    pause
    exit /b 1
)

echo.
echo ----------------------------------------
echo METHOD 1: Direct C# compilation (no Crystal Reports)
echo ----------------------------------------
echo Creating simplified version for development...

REM First, let's try compiling a simple version to test the environment
echo Testing C# compiler...
echo class Test { static void Main() { System.Console.WriteLine("Test OK"); } } > test.cs
csc test.cs
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: C# compiler is working
    test.exe
    del test.cs test.exe 2>nul
) else (
    echo ERROR: C# compiler not found or not working
    echo Installing .NET Framework Developer Pack might help
    del test.cs 2>nul
    pause
    exit /b 1
)

echo.
echo ----------------------------------------
echo METHOD 2: Mock version (no Crystal Reports dependencies)
echo ----------------------------------------

echo Creating mock RptToXml.cs...
(
echo using System;
echo using System.IO;
echo using System.Xml;
echo.
echo namespace CrystalCopilot.Tools
echo {
echo     /// ^<summary^>
echo     /// Crystal Copilot RptToXml Tool - Mock Version for Development
echo     /// ^</summary^>
echo     class RptToXml
echo     {
echo         static int Main^(string[] args^)
echo         {
echo             Console.WriteLine^("Crystal Copilot RptToXml Tool v1.0 - Mock Version"^);
echo             Console.WriteLine^("=========================================="^);
echo             Console.WriteLine^("This is a development version without Crystal Reports SDK"^);
echo             Console.WriteLine^(^);
echo.
echo             if ^(args.Length ^< 1^)
echo             {
echo                 ShowUsage^(^);
echo                 return 0;
echo             }
echo.
echo             if ^(args.Length ^< 2^)
echo             {
echo                 Console.WriteLine^("ERROR: Please specify both input and output files"^);
echo                 ShowUsage^(^);
echo                 return 1;
echo             }
echo.
echo             string inputFile = args[0];
echo             string outputFile = args[1];
echo             bool verbose = Array.Exists^(args, arg =^> arg == "--verbose"^);
echo.
echo             if ^(verbose^) Console.WriteLine^($"Input: {inputFile}"^);
echo             if ^(verbose^) Console.WriteLine^($"Output: {outputFile}"^);
echo.
echo             if ^(!File.Exists^(inputFile^)^)
echo             {
echo                 Console.WriteLine^($"ERROR: Input file '{inputFile}' not found."^);
echo                 return 1;
echo             }
echo.
echo             Console.WriteLine^($"Mock processing: {Path.GetFileName^(inputFile^)} -^> {Path.GetFileName^(outputFile^)}"^);
echo.
echo             // Create realistic mock XML output
echo             XmlDocument doc = new XmlDocument^(^);
echo             XmlElement root = doc.CreateElement^("CrystalReport"^);
echo             doc.AppendChild^(root^);
echo.
echo             // Add realistic report metadata
echo             XmlElement info = doc.CreateElement^("ReportInfo"^);
echo             info.SetAttribute^("name", Path.GetFileNameWithoutExtension^(inputFile^)^);
echo             info.SetAttribute^("type", "MockReport"^);
echo             info.SetAttribute^("created", DateTime.Now.ToString^("yyyy-MM-ddTHH:mm:ss"^)^);
echo             info.SetAttribute^("version", "13.0.33"^);
echo             root.AppendChild^(info^);
echo.
echo             // Add mock sections
echo             XmlElement sections = doc.CreateElement^("Sections"^);
echo             root.AppendChild^(sections^);
echo.
echo             string[] sectionNames = {"ReportHeader", "PageHeader", "Details", "PageFooter", "ReportFooter"};
echo             foreach ^(string sectionName in sectionNames^)
echo             {
echo                 XmlElement section = doc.CreateElement^("Section"^);
echo                 section.SetAttribute^("name", sectionName^);
echo                 section.SetAttribute^("height", "1000"^);
echo                 sections.AppendChild^(section^);
echo.
echo                 // Add mock objects
echo                 XmlElement objects = doc.CreateElement^("Objects"^);
echo                 section.AppendChild^(objects^);
echo.
echo                 XmlElement obj = doc.CreateElement^("Object"^);
echo                 obj.SetAttribute^("name", sectionName + "_Text"^);
echo                 obj.SetAttribute^("type", "TextObject"^);
echo                 obj.SetAttribute^("text", "Sample " + sectionName + " content"^);
echo                 objects.AppendChild^(obj^);
echo             }
echo.
echo             // Save XML with proper formatting
echo             XmlWriterSettings settings = new XmlWriterSettings
echo             {
echo                 Indent = true,
echo                 IndentChars = "  "
echo             };
echo.
echo             string outputDir = Path.GetDirectoryName^(outputFile^);
echo             if ^(!string.IsNullOrEmpty^(outputDir^) ^&^& !Directory.Exists^(outputDir^)^)
echo             {
echo                 Directory.CreateDirectory^(outputDir^);
echo             }
echo.
echo             using ^(XmlWriter writer = XmlWriter.Create^(outputFile, settings^)^)
echo             {
echo                 doc.Save^(writer^);
echo             }
echo.
echo             Console.WriteLine^($"SUCCESS: Created mock XML file: {outputFile}"^);
echo             
echo             if ^(verbose^)
echo             {
echo                 FileInfo outputInfo = new FileInfo^(outputFile^);
echo                 Console.WriteLine^($"Output size: {outputInfo.Length} bytes"^);
echo             }
echo.
echo             Console.WriteLine^("NOTE: This is mock data. Install Crystal Reports SDK for real parsing."^);
echo             return 0;
echo         }
echo.
echo         static void ShowUsage^(^)
echo         {
echo             Console.WriteLine^("Usage: RptToXml.exe ^<input.rpt^> ^<output.xml^> [options]"^);
echo             Console.WriteLine^(^);
echo             Console.WriteLine^("Options:"^);
echo             Console.WriteLine^("  --verbose         Show detailed processing information"^);
echo             Console.WriteLine^(^);
echo             Console.WriteLine^("Examples:"^);
echo             Console.WriteLine^("  RptToXml.exe report.rpt report.xml"^);
echo             Console.WriteLine^("  RptToXml.exe report.rpt report.xml --verbose"^);
echo             Console.WriteLine^(^);
echo             Console.WriteLine^("Converts Crystal Reports files to XML metadata for Crystal Copilot."^);
echo             Console.WriteLine^("This mock version creates realistic test data for development."^);
echo         }
echo     }
echo }
) > RptToXmlMock.cs

echo Mock version created: RptToXmlMock.cs

echo Compiling mock version...
csc /target:exe /out:RptToXml.exe RptToXmlMock.cs

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Mock RptToXml.exe compiled!
    echo ========================================
    
    REM Test the executable
    echo.
    echo Testing the compiled tool...
    RptToXml.exe
    
    echo.
    echo ========================================
    echo COMPILATION SUCCESSFUL!
    echo ========================================
    echo.
    echo File location: %CD%\RptToXml.exe
    dir RptToXml.exe | findstr RptToXml.exe
    echo.
    echo Usage examples:
    echo   RptToXml.exe "sample.rpt" "output.xml"
    echo   RptToXml.exe "sample.rpt" "output.xml" --verbose
    echo.
    echo NOTE: This is a mock version for development.
    echo      It creates realistic XML without needing Crystal Reports SDK.
    echo      Perfect for testing the Crystal Copilot MVP!
    echo.
    
    REM Clean up
    del RptToXmlMock.cs 2>nul
    
) else (
    echo ERROR: Mock compilation failed
    echo.
    echo This might indicate a .NET Framework issue.
    echo Try installing: .NET Framework 4.8 Developer Pack
    echo Download from: https://dotnet.microsoft.com/download/dotnet-framework/net48
    echo.
    del RptToXmlMock.cs 2>nul
)

echo.
echo ========================================
echo PROCESS COMPLETE
echo ========================================
pause 