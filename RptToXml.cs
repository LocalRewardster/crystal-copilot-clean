using System;
using System.IO;
using System.Xml;
using System.Collections.Generic;
using System.Reflection;
using CrystalDecisions.CrystalReports.Engine;
using CrystalDecisions.Shared;

namespace CrystalCopilot.Tools
{
    /// <summary>
    /// Crystal Copilot RptToXml Tool - Production Version
    /// Converts Crystal Reports (.rpt) files to XML metadata
    /// </summary>
    class RptToXml
    {
        static int Main(string[] args)
        {
            try
            {
                Console.WriteLine("Crystal Copilot RptToXml Tool v1.0");
                Console.WriteLine("Converting Crystal Reports to XML metadata");
                Console.WriteLine();

                if (args.Length < 2)
                {
                    ShowUsage();
                    return 1;
                }

                string inputFile = args[0];
                string outputFile = args[1];
                bool includeData = Array.Exists(args, arg => arg == "--include-data");
                bool verbose = Array.Exists(args, arg => arg == "--verbose");

                if (verbose) Console.WriteLine($"Input: {inputFile}");
                if (verbose) Console.WriteLine($"Output: {outputFile}");

                if (!File.Exists(inputFile))
                {
                    Console.WriteLine($"ERROR: Input file '{inputFile}' not found.");
                    return 1;
                }

                if (verbose) Console.WriteLine("Loading Crystal Report...");

                // Load the Crystal Report
                using (ReportDocument report = new ReportDocument())
                {
                    report.Load(inputFile);

                    if (verbose) Console.WriteLine("Extracting metadata...");

                    // Create XML document
                    XmlDocument xmlDoc = new XmlDocument();
                    XmlElement root = xmlDoc.CreateElement("CrystalReport");
                    xmlDoc.AppendChild(root);

                    // Add report metadata
                    AddReportInfo(xmlDoc, root, report, inputFile, verbose);
                    
                    // Add sections
                    AddSections(xmlDoc, root, report, verbose);
                    
                    // Add database info
                    AddDatabaseInfo(xmlDoc, root, report, verbose);
                    
                    // Add parameters
                    AddParameters(xmlDoc, root, report, verbose);
                    
                    // Add formulas
                    AddFormulas(xmlDoc, root, report, verbose);

                    // Save XML
                    if (verbose) Console.WriteLine($"Saving XML to: {outputFile}");
                    
                    // Create output directory if it doesn't exist
                    string outputDir = Path.GetDirectoryName(outputFile);
                    if (!string.IsNullOrEmpty(outputDir) && !Directory.Exists(outputDir))
                    {
                        Directory.CreateDirectory(outputDir);
                    }

                    // Save with proper formatting
                    XmlWriterSettings settings = new XmlWriterSettings
                    {
                        Indent = true,
                        IndentChars = "  "
                    };

                    using (XmlWriter writer = XmlWriter.Create(outputFile, settings))
                    {
                        xmlDoc.Save(writer);
                    }

                    Console.WriteLine($"SUCCESS: Converted '{Path.GetFileName(inputFile)}' to '{Path.GetFileName(outputFile)}'");
                    
                    if (verbose)
                    {
                        FileInfo outputInfo = new FileInfo(outputFile);
                        Console.WriteLine($"Output size: {outputInfo.Length} bytes");
                    }

                    return 0;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR: {ex.Message}");
                
                if (args.Length > 0 && Array.Exists(args, arg => arg == "--verbose"))
                {
                    Console.WriteLine();
                    Console.WriteLine("Stack trace:");
                    Console.WriteLine(ex.StackTrace);
                }
                
                return 1;
            }
        }

        static void ShowUsage()
        {
            Console.WriteLine("Usage: RptToXml.exe <input.rpt> <output.xml> [options]");
            Console.WriteLine();
            Console.WriteLine("Options:");
            Console.WriteLine("  --include-data    Include sample data in output (future feature)");
            Console.WriteLine("  --verbose         Show detailed processing information");
            Console.WriteLine();
            Console.WriteLine("Examples:");
            Console.WriteLine("  RptToXml.exe report.rpt report.xml");
            Console.WriteLine("  RptToXml.exe report.rpt report.xml --verbose");
            Console.WriteLine();
            Console.WriteLine("Converts Crystal Reports files to XML metadata for Crystal Copilot.");
        }

        static void AddReportInfo(XmlDocument doc, XmlElement parent, ReportDocument report, string filePath, bool verbose)
        {
            if (verbose) Console.WriteLine("  Adding report info...");
            
            XmlElement info = doc.CreateElement("ReportInfo");
            parent.AppendChild(info);

            AddElement(doc, info, "Name", Path.GetFileNameWithoutExtension(filePath));
            AddElement(doc, info, "FilePath", filePath);
            AddElement(doc, info, "CreationDate", DateTime.Now.ToString("yyyy-MM-ddTHH:mm:ss"));
            AddElement(doc, info, "ReportVersion", "13.0.33");
            AddElement(doc, info, "ProcessedBy", "Crystal Copilot RptToXml v1.0");
            
            try
            {
                AddElement(doc, info, "RecordSelectionFormula", report.RecordSelectionFormula ?? "");
            }
            catch 
            { 
                AddElement(doc, info, "RecordSelectionFormula", ""); 
            }

            try
            {
                FileInfo fileInfo = new FileInfo(filePath);
                AddElement(doc, info, "FileSize", fileInfo.Length.ToString());
                AddElement(doc, info, "LastModified", fileInfo.LastWriteTime.ToString("yyyy-MM-ddTHH:mm:ss"));
            }
            catch { /* Ignore file info errors */ }
        }

        static void AddSections(XmlDocument doc, XmlElement parent, ReportDocument report, bool verbose)
        {
            if (verbose) Console.WriteLine("  Adding sections...");
            
            XmlElement sections = doc.CreateElement("Sections");
            parent.AppendChild(sections);

            foreach (Section section in report.ReportDefinition.Sections)
            {
                XmlElement sectionElem = doc.CreateElement("Section");
                sections.AppendChild(sectionElem);

                sectionElem.SetAttribute("name", section.Name);
                sectionElem.SetAttribute("kind", section.Kind.ToString());
                sectionElem.SetAttribute("height", section.Height.ToString());

                // Add objects in section
                XmlElement objects = doc.CreateElement("Objects");
                sectionElem.AppendChild(objects);

                foreach (ReportObject obj in section.ReportObjects)
                {
                    XmlElement objElem = doc.CreateElement("Object");
                    objects.AppendChild(objElem);

                    objElem.SetAttribute("name", obj.Name);
                    objElem.SetAttribute("kind", obj.Kind.ToString());
                    objElem.SetAttribute("left", obj.Left.ToString());
                    objElem.SetAttribute("top", obj.Top.ToString());
                    objElem.SetAttribute("width", obj.Width.ToString());
                    objElem.SetAttribute("height", obj.Height.ToString());

                    // Add specific properties based on object type
                    try
                    {
                        if (obj is TextObject textObj)
                        {
                            objElem.SetAttribute("text", textObj.Text ?? "");
                        }
                        else if (obj is FieldObject fieldObj)
                        {
                            objElem.SetAttribute("dataSource", fieldObj.DataSource?.ToString() ?? "");
                        }
                    }
                    catch { /* Ignore property access errors */ }
                }
            }
        }

        static void AddDatabaseInfo(XmlDocument doc, XmlElement parent, ReportDocument report, bool verbose)
        {
            if (verbose) Console.WriteLine("  Adding database info...");
            
            XmlElement database = doc.CreateElement("Database");
            parent.AppendChild(database);

            XmlElement tables = doc.CreateElement("Tables");
            database.AppendChild(tables);

            foreach (Table table in report.Database.Tables)
            {
                XmlElement tableElem = doc.CreateElement("Table");
                tables.AppendChild(tableElem);

                tableElem.SetAttribute("name", table.Name ?? "");
                tableElem.SetAttribute("location", table.Location ?? "");
                
                // Note: ClassName property may not be available in all Crystal Reports versions
                try
                {
                    // Try to get additional table properties if available
                    var tableType = table.GetType();
                    var classNameProp = tableType.GetProperty("ClassName");
                    if (classNameProp != null)
                    {
                        var className = classNameProp.GetValue(table, null);
                        tableElem.SetAttribute("className", className?.ToString() ?? "");
                    }
                    else
                    {
                        tableElem.SetAttribute("className", "Table");
                    }
                }
                catch
                {
                    tableElem.SetAttribute("className", "Table");
                }
            }
        }

        static void AddParameters(XmlDocument doc, XmlElement parent, ReportDocument report, bool verbose)
        {
            if (verbose) Console.WriteLine("  Adding parameters...");
            
            XmlElement parameters = doc.CreateElement("Parameters");
            parent.AppendChild(parameters);

            foreach (ParameterFieldDefinition param in report.DataDefinition.ParameterFields)
            {
                XmlElement paramElem = doc.CreateElement("Parameter");
                parameters.AppendChild(paramElem);

                paramElem.SetAttribute("name", param.Name ?? "");
                paramElem.SetAttribute("parameterFieldName", param.ParameterFieldName ?? "");
                paramElem.SetAttribute("valueType", param.ValueType.ToString());
                paramElem.SetAttribute("hasCurrentValue", param.HasCurrentValue.ToString());
            }
        }

        static void AddFormulas(XmlDocument doc, XmlElement parent, ReportDocument report, bool verbose)
        {
            if (verbose) Console.WriteLine("  Adding formulas...");
            
            XmlElement formulas = doc.CreateElement("Formulas");
            parent.AppendChild(formulas);

            foreach (FormulaFieldDefinition formula in report.DataDefinition.FormulaFields)
            {
                XmlElement formulaElem = doc.CreateElement("Formula");
                formulas.AppendChild(formulaElem);

                formulaElem.SetAttribute("name", formula.Name ?? "");
                formulaElem.SetAttribute("formulaName", formula.FormulaName ?? "");
                
                try
                {
                    formulaElem.SetAttribute("text", formula.Text ?? "");
                }
                catch { /* Ignore if text not accessible */ }
            }
        }

        static void AddElement(XmlDocument doc, XmlElement parent, string name, string value)
        {
            XmlElement elem = doc.CreateElement(name);
            elem.InnerText = value ?? "";
            parent.AppendChild(elem);
        }
    }
}
