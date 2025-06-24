"""
Crystal Reports Parser - Core functionality for Week 1
Handles RptToXml conversion and JSON normalization
"""

import json
import os
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Optional

import xmltodict


class ReportParser:
    """Handles Crystal Reports parsing via RptToXml CLI"""

    def __init__(self):
        self.rpttoxml_path = os.getenv('RPTTOXML_PATH', 'RptToXml.exe')

    async def parse_report(self, rpt_file_path: str) -> 'ParseResult':
        """
        Parse Crystal Report file to XML then normalize to JSON

        Week 1 Implementation:
        1. Shell out to RptToXml CLI
        2. Convert XML to dictionary
        3. Normalize and return metadata
        """

        # Generate unique report ID
        report_id = str(uuid.uuid4())

        # Convert .rpt to XML
        xml_content = await self._convert_to_xml(rpt_file_path)

        # Parse XML to dictionary
        xml_dict = xmltodict.parse(xml_content)

        # Normalize to JSON metadata
        metadata = self._normalize_xml_to_json(xml_dict)

        return ParseResult(
            report_id=report_id,
            xml_content=xml_content,
            metadata=metadata
        )

    async def _convert_to_xml(self, rpt_file_path: str) -> str:
        """Convert .rpt file to XML using RptToXml CLI"""

        if not os.path.exists(rpt_file_path):
            raise FileNotFoundError(f"Report file not found: {rpt_file_path}")

        # Read the sample file content to generate appropriate mock data
        file_content = ""
        try:
            with open(rpt_file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except UnicodeDecodeError:
            # Handle binary files by reading first part as text
            with open(rpt_file_path, 'rb') as f:
                file_content = f.read(1024).decode('utf-8', errors='ignore')

        # Generate mock XML based on file content
        mock_xml = self._generate_mock_xml_from_content(rpt_file_path, file_content)

        # TODO: Replace with actual RptToXml CLI call:
        # cmd = [self.rpttoxml_path, rpt_file_path, "-output", "xml"]
        # result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # return result.stdout

        return mock_xml

    def _generate_mock_xml_from_content(self, file_path: str, content: str) -> str:
        """Generate realistic mock XML based on the sample file content"""
        
        filename = Path(file_path).stem
        
        # Extract information from our structured sample files
        report_info = self._extract_report_info(content, filename)
        sections_xml = self._generate_sections_xml(content, filename)
        data_sources_xml = self._generate_data_sources_xml(content, filename)
        
        # Escape special characters in report info
        report_info['name'] = self._escape_xml(report_info['name'])
        report_info['author'] = self._escape_xml(report_info.get('author', 'Unknown'))
        
        mock_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <ReportInfo>
        <Name>{report_info['name']}</Name>
        <Version>{report_info['version']}</Version>
        <CreationDate>{report_info['creation_date']}</CreationDate>
        <Author>{report_info['author']}</Author>
    </ReportInfo>
    {sections_xml}
    {data_sources_xml}
</Report>"""
        
        return mock_xml

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters"""
        if not text:
            return text
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))

    def _extract_report_info(self, content: str, filename: str) -> Dict[str, str]:
        """Extract report metadata from sample file content"""
        
        # Default values
        info = {
            'name': filename.replace('_', ' ').title(),
            'version': '13.0',
            'creation_date': '2024-01-01',
            'author': 'Demo User'
        }
        
        # Parse content for specific information
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- Name:') or line.startswith('Report:'):
                info['name'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Version:') or line.startswith('Version:'):
                info['version'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Created:') or line.startswith('Created:'):
                info['creation_date'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Author:'):
                info['author'] = line.split(':', 1)[1].strip()
        
        return info

    def _generate_sections_xml(self, content: str, filename: str) -> str:
        """Generate sections XML based on file content"""
        
        # Parse sections from content
        if 'Simple_Customer_List' in filename:
            return """<Sections>
        <Section Name="ReportHeader">
            <TextObjects>
                <TextObject Name="Title">
                    <Text>Customer Directory</Text>
                    <Font>Arial, 14pt, Bold</Font>
                </TextObject>
                <TextObject Name="CurrentDate">
                    <Text>Current Date</Text>
                    <Font>Arial, 10pt</Font>
                </TextObject>
            </TextObjects>
        </Section>
        <Section Name="Details">
            <FieldObjects>
                <FieldObject Name="CompanyName">
                    <DatabaseField>Customers.CompanyName</DatabaseField>
                </FieldObject>
                <FieldObject Name="ContactName">
                    <DatabaseField>Customers.ContactName</DatabaseField>
                </FieldObject>
                <FieldObject Name="Phone">
                    <DatabaseField>Customers.Phone</DatabaseField>
                </FieldObject>
                <FieldObject Name="Email">
                    <DatabaseField>Customers.Email</DatabaseField>
                </FieldObject>
                <FieldObject Name="City">
                    <DatabaseField>Addresses.City</DatabaseField>
                </FieldObject>
                <FieldObject Name="State">
                    <DatabaseField>Addresses.State</DatabaseField>
                </FieldObject>
            </FieldObjects>
        </Section>
        <Section Name="ReportFooter">
            <TextObjects>
                <TextObject Name="TotalCount">
                    <Text>Total Customers</Text>
                    <Font>Arial, 10pt, Bold</Font>
                </TextObject>
            </TextObjects>
            <FieldObjects>
                <FieldObject Name="CustomerCount">
                    <Formula>Count({Customers.CustomerID})</Formula>
                </FieldObject>
            </FieldObjects>
        </Section>
    </Sections>"""
            
        elif 'Sales_Report' in filename:
            return """<Sections>
        <Section Name="ReportHeader">
            <TextObjects>
                <TextObject Name="Title">
                    <Text>Monthly Sales Summary</Text>
                    <Font>Arial, 16pt, Bold</Font>
                </TextObject>
            </TextObjects>
            <PictureObjects>
                <PictureObject Name="CompanyLogo">
                    <ImagePath>company_logo.png</ImagePath>
                </PictureObject>
            </PictureObjects>
        </Section>
        <Section Name="PageHeader">
            <TextObjects>
                <TextObject Name="CustomerHeader">
                    <Text>Customer Name</Text>
                    <Font>Arial, 10pt, Bold</Font>
                </TextObject>
                <TextObject Name="OrderDateHeader">
                    <Text>Order Date</Text>
                    <Font>Arial, 10pt, Bold</Font>
                </TextObject>
                <TextObject Name="TotalHeader">
                    <Text>Order Total</Text>
                    <Font>Arial, 10pt, Bold</Font>
                </TextObject>
            </TextObjects>
        </Section>
        <Section Name="Details">
            <FieldObjects>
                <FieldObject Name="CustomerName">
                    <DatabaseField>Customers.CustomerName</DatabaseField>
                </FieldObject>
                <FieldObject Name="CustomerID">
                    <DatabaseField>Customers.CustomerID</DatabaseField>
                </FieldObject>
                <FieldObject Name="OrderDate">
                    <DatabaseField>Orders.OrderDate</DatabaseField>
                </FieldObject>
                <FieldObject Name="OrderTotal">
                    <Formula>Sum({OrderItems.Amount})</Formula>
                </FieldObject>
                <FieldObject Name="ProductName">
                    <DatabaseField>Products.ProductName</DatabaseField>
                </FieldObject>
                <FieldObject Name="ProductCategory">
                    <DatabaseField>Products.Category</DatabaseField>
                </FieldObject>
                <FieldObject Name="NetMargin">
                    <Formula>({OrderTotal} - {OrderCost}) / {OrderTotal} * 100</Formula>
                </FieldObject>
                <FieldObject Name="YTDSales">
                    <Formula>Sum({Orders.Amount}, {{Orders.OrderDate}} >= DateSerial(Year(CurrentDate), 1, 1))</Formula>
                </FieldObject>
                <FieldObject Name="CustomerRank">
                    <Formula>Rank({CustomerTotal}, {{Customers.CustomerID}})</Formula>
                </FieldObject>
            </FieldObjects>
        </Section>
        <Section Name="ReportFooter">
            <TextObjects>
                <TextObject Name="GrandTotalLabel">
                    <Text>Grand Total</Text>
                    <Font>Arial, 12pt, Bold</Font>
                </TextObject>
            </TextObjects>
            <FieldObjects>
                <FieldObject Name="GrandTotal">
                    <Formula>Sum({OrderItems.Amount})</Formula>
                </FieldObject>
            </FieldObjects>
        </Section>
    </Sections>"""
            
        elif 'Inventory_Summary' in filename:
            return """<Sections>
        <Section Name="ReportHeader">
            <TextObjects>
                <TextObject Name="Title">
                    <Text>Inventory Summary Report</Text>
                    <Font>Arial, 16pt, Bold</Font>
                </TextObject>
                <TextObject Name="RunDate">
                    <Text>Report Generated</Text>
                    <Font>Arial, 10pt</Font>
                </TextObject>
            </TextObjects>
            <PictureObjects>
                <PictureObject Name="CompanyLogo">
                    <ImagePath>company_logo.png</ImagePath>
                </PictureObject>
            </PictureObjects>
        </Section>
        <Section Name="GroupHeader">
            <TextObjects>
                <TextObject Name="CategoryName">
                    <Text>Product Category</Text>
                    <Font>Arial, 12pt, Bold</Font>
                </TextObject>
            </TextObjects>
        </Section>
        <Section Name="Details">
            <FieldObjects>
                <FieldObject Name="ProductName">
                    <DatabaseField>Products.ProductName</DatabaseField>
                </FieldObject>
                <FieldObject Name="QuantityOnHand">
                    <DatabaseField>Inventory.QuantityOnHand</DatabaseField>
                </FieldObject>
                <FieldObject Name="ReorderLevel">
                    <DatabaseField>Inventory.ReorderLevel</DatabaseField>
                </FieldObject>
                <FieldObject Name="UnitPrice">
                    <DatabaseField>Products.UnitPrice</DatabaseField>
                </FieldObject>
                <FieldObject Name="SupplierName">
                    <DatabaseField>Suppliers.SupplierName</DatabaseField>
                </FieldObject>
                <FieldObject Name="StockValue">
                    <Formula>{Inventory.QuantityOnHand} * {Products.UnitPrice}</Formula>
                </FieldObject>
                <FieldObject Name="DaysSupply">
                    <Formula>{Inventory.QuantityOnHand} / {AverageDailyUsage}</Formula>
                </FieldObject>
                <FieldObject Name="ReorderStatus">
                    <Formula>If {{Inventory.QuantityOnHand}} &lt;= {{Inventory.ReorderLevel}} Then &quot;REORDER&quot; Else &quot;OK&quot;</Formula>
                </FieldObject>
            </FieldObjects>
        </Section>
        <Section Name="GroupFooter">
            <TextObjects>
                <TextObject Name="CategorySubtotal">
                    <Text>Category Subtotal</Text>
                    <Font>Arial, 10pt, Bold</Font>
                </TextObject>
            </TextObjects>
            <FieldObjects>
                <FieldObject Name="CategoryValue">
                    <Formula>Sum({StockValue})</Formula>
                </FieldObject>
            </FieldObjects>
        </Section>
        <Section Name="PageFooter">
            <TextObjects>
                <TextObject Name="PageNumber">
                    <Text>Page</Text>
                    <Font>Arial, 9pt</Font>
                </TextObject>
                <TextObject Name="Timestamp">
                    <Text>Generated</Text>
                    <Font>Arial, 9pt</Font>
                </TextObject>
            </TextObjects>
        </Section>
    </Sections>"""
        
        # Default sections for unknown files
        return """<Sections>
        <Section Name="ReportHeader">
            <TextObjects>
                <TextObject Name="Title">
                    <Text>Report Title</Text>
                    <Font>Arial, 12pt</Font>
                </TextObject>
            </TextObjects>
        </Section>
        <Section Name="Details">
            <FieldObjects>
                <FieldObject Name="DefaultField">
                    <DatabaseField>Table.Field</DatabaseField>
                </FieldObject>
            </FieldObjects>
        </Section>
    </Sections>"""

    def _generate_data_sources_xml(self, content: str, filename: str) -> str:
        """Generate data sources XML based on file content"""
        
        if 'Simple_Customer_List' in filename:
            return """<DataSources>
        <DataSource Name="CRM_Database">
            <ConnectionString>Provider=SQLOLEDB;Server=crm-server.company.com;Database=CRM</ConnectionString>
            <Tables>
                <Table Name="Customers"/>
                <Table Name="Addresses"/>
            </Tables>
        </DataSource>
    </DataSources>"""
            
        elif 'Sales_Report' in filename:
            return """<DataSources>
        <DataSource Name="ERP_Production">
            <ConnectionString>Provider=SQLOLEDB;Server=sql-server-01.company.com;Database=ERP_Production</ConnectionString>
            <Tables>
                <Table Name="Customers"/>
                <Table Name="Orders"/>
                <Table Name="OrderItems"/>
                <Table Name="Products"/>
            </Tables>
        </DataSource>
    </DataSources>"""
            
        elif 'Inventory_Summary' in filename:
            return """<DataSources>
        <DataSource Name="InventoryDB">
            <ConnectionString>Provider=OraOLEDB;Server=inv-oracle-prod.company.local;Schema=INVENTORY_MGMT</ConnectionString>
            <Tables>
                <Table Name="Products"/>
                <Table Name="Inventory"/>
                <Table Name="Suppliers"/>
                <Table Name="Categories"/>
            </Tables>
        </DataSource>
    </DataSources>"""
        
        # Default data source
        return """<DataSources>
        <DataSource Name="DefaultDB">
            <ConnectionString>Provider=SQLOLEDB;Server=localhost;Database=TestDB</ConnectionString>
            <Tables>
                <Table Name="DefaultTable"/>
            </Tables>
        </DataSource>
    </DataSources>"""

    def _normalize_xml_to_json(self, xml_dict: Dict) -> Dict:
        """Normalize XML dictionary to clean JSON metadata"""

        report_data = xml_dict.get('Report', {})

        # Extract key metadata
        metadata = {
            'report_info': {
                'name': report_data.get('ReportInfo', {}).get('Name', 'Unknown'),
                'version': report_data.get('ReportInfo', {}).get('Version', 'Unknown'),
                'creation_date': report_data.get('ReportInfo', {}).get('CreationDate', 'Unknown'),
                'author': report_data.get('ReportInfo', {}).get('Author', 'Unknown')
            },
            'sections': [],
            'data_sources': [],
            'field_lineage': {}
        }

        # Process sections
        sections = report_data.get('Sections', {})
        
        # Handle the Section element(s) within Sections
        if isinstance(sections, dict) and 'Section' in sections:
            section_list = sections['Section']
            if isinstance(section_list, dict):
                section_list = [section_list]
        else:
            section_list = []

        for section in section_list:
            if isinstance(section, dict):
                section_data = {
                    'name': section.get('@Name', 'Unknown'),
                    'text_objects': [],
                    'field_objects': [],
                    'picture_objects': []
                }

                # Process text objects
                text_objects = section.get('TextObjects', {})
                if isinstance(text_objects, dict) and 'TextObject' in text_objects:
                    text_obj = text_objects['TextObject']
                    if isinstance(text_obj, dict):
                        text_obj = [text_obj]

                    for obj in text_obj:
                        section_data['text_objects'].append({
                            'name': obj.get('@Name', 'Unknown'),
                            'text': obj.get('Text', ''),
                            'font': obj.get('Font', '')
                        })

                # Process field objects
                field_objects = section.get('FieldObjects', {})
                if isinstance(field_objects, dict) and 'FieldObject' in field_objects:
                    field_obj = field_objects['FieldObject']
                    if isinstance(field_obj, dict):
                        field_obj = [field_obj]

                    for obj in field_obj:
                        field_name = obj.get('@Name', 'Unknown')
                        db_field = obj.get('DatabaseField', '')
                        formula = obj.get('Formula', '')

                        section_data['field_objects'].append({
                            'name': field_name,
                            'database_field': db_field,
                            'formula': formula
                        })

                        # Add to lineage tracking
                        metadata['field_lineage'][field_name] = {
                            'source': db_field if db_field else 'Formula',
                            'formula': formula,
                            'section': section_data['name']
                        }

                # Process picture objects
                picture_objects = section.get('PictureObjects', {})
                if isinstance(picture_objects, dict) and 'PictureObject' in picture_objects:
                    pic_obj = picture_objects['PictureObject']
                    if isinstance(pic_obj, dict):
                        pic_obj = [pic_obj]

                    for obj in pic_obj:
                        section_data['picture_objects'].append({
                            'name': obj.get('@Name', 'Unknown'),
                            'image_path': obj.get('ImagePath', '')
                        })

                metadata['sections'].append(section_data)

        # Process data sources
        data_sources = report_data.get('DataSources', {})
        if isinstance(data_sources, dict) and 'DataSource' in data_sources:
            ds = data_sources['DataSource']
            if isinstance(ds, dict):
                ds = [ds]

            for source in ds:
                tables = source.get('Tables', {}).get('Table', [])
                if isinstance(tables, dict):
                    tables = [tables]

                metadata['data_sources'].append({
                    'name': source.get('@Name', 'Unknown'),
                    'connection_string': source.get('ConnectionString', ''),
                    'tables': [t.get('@Name', 'Unknown') for t in tables if isinstance(t, dict)]
                })

        return metadata


class ParseResult:
    """Result of report parsing operation"""

    def __init__(self, report_id: str, xml_content: str, metadata: Dict):
        self.report_id = report_id
        self.xml_content = xml_content
        self.metadata = metadata
