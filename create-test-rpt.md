# Creating a Test Crystal Report File

If you suspect your .rpt file is causing issues, create a simple test report:

## Method 1: Crystal Reports Designer (if available)

1. **Open Crystal Reports Designer**
2. **Create New Report**
3. **Use Sample Database** (usually Xtreme.mdb)
4. **Add simple fields:**
   - Customer Name
   - Order Date  
   - Order Amount
5. **Save as `test_simple.rpt`**

## Method 2: Use Sample Reports

Crystal Reports usually comes with sample reports in:
```
C:\Program Files (x86)\SAP BusinessObjects\Crystal Reports for .NET Framework 4.0\Samples\
```

Try these sample files:
- `World Sales Report.rpt`
- `Employee List.rpt`
- `Invoice.rpt`

## Method 3: Download Sample Reports

1. Visit SAP Crystal Reports documentation
2. Download sample reports from SAP Community
3. Use any basic .rpt file from online tutorials

## Testing Your .rpt File

Run the diagnostic script:
```
.\debug-rpt-file.bat
```

This will tell you if:
- ✅ RptToXml.exe can parse your file
- ✅ XML output contains expected sections
- ❌ File is corrupted or incompatible

## Common .rpt File Issues

1. **Password Protected**: Remove password protection
2. **Linked Subreports**: Use reports without subreports initially  
3. **External Images**: Ensure all linked files are available
4. **Very Old Versions**: Crystal Reports 6.0 or older may not work
5. **Complex Formulas**: Start with simple reports first

## Recommended Test File Properties

- **No password protection**
- **Single main report** (no subreports)
- **Simple data source** (Access, Excel, or SQL Server)
- **Basic fields only** (no complex formulas)
- **Recent Crystal Reports version** (2016 or newer) 