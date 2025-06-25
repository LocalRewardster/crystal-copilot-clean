# Create Test Crystal Report
# ========================

Write-Host "Creating Test Crystal Report..." -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host ""

try {
    # Load Crystal Reports assemblies
    Add-Type -Path "C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64\dotnet\CrystalDecisions.CrystalReports.Engine.dll"
    Add-Type -Path "C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Common\SAP BusinessObjects Enterprise XI 4.0\win64_x64\dotnet\CrystalDecisions.Shared.dll"
    
    Write-Host "Crystal Reports assemblies loaded successfully" -ForegroundColor Green
    
    # Create a new report document
    $report = New-Object CrystalDecisions.CrystalReports.Engine.ReportDocument
    
    # Create a simple test report file
    $testReportPath = "TestReport.rpt"
    
    # Note: Creating a report programmatically is complex
    # Instead, let's create a minimal XML that simulates what we'd get
    Write-Host "Creating minimal test report structure..." -ForegroundColor Yellow
    
    # This is a simplified approach - we'll create a basic report structure
    $report.Save($testReportPath)
    
    Write-Host "SUCCESS: Test report created at $testReportPath" -ForegroundColor Green
    
} catch {
    Write-Host "Creating report programmatically is complex. Let's use alternative approach..." -ForegroundColor Yellow
    Write-Host ""
    
    # Alternative: Create a sample XML file that represents what RptToXml would output
    $sampleXmlPath = "sample-report-output.xml"
    
    $sampleXml = @"
<?xml version="1.0" encoding="utf-8"?>
<CrystalReport>
  <ReportInfo>
    <Name>TestReport</Name>
    <FilePath>TestReport.rpt</FilePath>
    <CreationDate>2024-01-15T10:30:00</CreationDate>
    <ReportVersion>13.0.33</ReportVersion>
    <ProcessedBy>Crystal Copilot RptToXml v1.0</ProcessedBy>
    <RecordSelectionFormula></RecordSelectionFormula>
    <FileSize>45632</FileSize>
    <LastModified>2024-01-15T10:30:00</LastModified>
  </ReportInfo>
  <Sections>
    <Section name="ReportHeaderSection1" kind="ReportHeader" height="720">
      <Objects>
        <Object name="Text1" kind="TextObject" left="720" top="240" width="2880" height="240" text="Sample Report Title" />
      </Objects>
    </Section>
    <Section name="PageHeaderSection1" kind="PageHeader" height="360">
      <Objects>
        <Object name="Text2" kind="TextObject" left="720" top="120" width="1440" height="240" text="Customer Name" />
        <Object name="Text3" kind="TextObject" left="2160" top="120" width="1440" height="240" text="Order Date" />
        <Object name="Text4" kind="TextObject" left="3600" top="120" width="1440" height="240" text="Amount" />
      </Objects>
    </Section>
    <Section name="DetailsSection1" kind="Detail" height="240">
      <Objects>
        <Object name="Field1" kind="FieldObject" left="720" top="0" width="1440" height="240" dataSource="Customer.CustomerName" />
        <Object name="Field2" kind="FieldObject" left="2160" top="0" width="1440" height="240" dataSource="Orders.OrderDate" />
        <Object name="Field3" kind="FieldObject" left="3600" top="0" width="1440" height="240" dataSource="Orders.Amount" />
      </Objects>
    </Section>
  </Sections>
  <Database>
    <Tables>
      <Table name="Customer" location="Northwind.Customer" className="Table" />
      <Table name="Orders" location="Northwind.Orders" className="Table" />
    </Tables>
  </Database>
  <Parameters>
    <Parameter name="StartDate" parameterFieldName="StartDate" valueType="DateTimeParameter" hasCurrentValue="False" />
    <Parameter name="EndDate" parameterFieldName="EndDate" valueType="DateTimeParameter" hasCurrentValue="False" />
  </Parameters>
  <Formulas>
    <Formula name="TotalAmount" formulaName="@TotalAmount" text="Sum({Orders.Amount})" />
  </Formulas>
</CrystalReport>
"@
    
    $sampleXml | Out-File -FilePath $sampleXmlPath -Encoding UTF8
    
    Write-Host "Created sample XML output: $sampleXmlPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "This shows what your RptToXml.exe tool would generate from a real .rpt file" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To test with a real Crystal Report:" -ForegroundColor Yellow
    Write-Host "1. Open Crystal Reports Designer" -ForegroundColor Gray
    Write-Host "2. Create a simple report with a few fields" -ForegroundColor Gray
    Write-Host "3. Save it as TestReport.rpt" -ForegroundColor Gray
    Write-Host "4. Run: .\RptToXml.exe TestReport.rpt output.xml --verbose" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test RptToXml.exe with any .rpt file you have" -ForegroundColor White
Write-Host "2. Update Crystal Copilot backend to use real parser" -ForegroundColor White
Write-Host "3. Start the full Crystal Copilot application" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue" 