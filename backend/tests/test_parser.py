"""
Unit tests for Crystal Reports parser
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from backend.core.report_parser import ReportParser, ParseResult


class TestReportParser:
    """Test cases for ReportParser class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = ReportParser()
    
    def test_parser_initialization(self):
        """Test parser initializes correctly"""
        assert self.parser.rpttoxml_path is not None
        assert isinstance(self.parser.rpttoxml_path, str)
    
    @pytest.mark.asyncio
    async def test_parse_report_with_valid_file(self):
        """Test parsing a valid report file"""
        # Create a temporary file to simulate .rpt file
        with tempfile.NamedTemporaryFile(suffix='.rpt', delete=False) as temp_file:
            temp_file.write(b"dummy content")
            temp_file_path = temp_file.name
        
        try:
            # Parse the report
            result = await self.parser.parse_report(temp_file_path)
            
            # Verify result structure
            assert isinstance(result, ParseResult)
            assert result.report_id is not None
            assert result.xml_content is not None
            assert result.metadata is not None
            
            # Verify metadata structure
            metadata = result.metadata
            assert 'report_info' in metadata
            assert 'sections' in metadata
            assert 'data_sources' in metadata
            assert 'field_lineage' in metadata
            
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_parse_report_with_nonexistent_file(self):
        """Test parsing a non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            await self.parser.parse_report("/nonexistent/file.rpt")
    
    @pytest.mark.asyncio
    async def test_convert_to_xml_generates_valid_xml(self):
        """Test XML conversion generates valid XML"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.rpt', delete=False) as temp_file:
            temp_file.write(b"dummy content")
            temp_file_path = temp_file.name
        
        try:
            # Convert to XML
            xml_content = await self.parser._convert_to_xml(temp_file_path)
            
            # Verify XML structure
            assert xml_content.startswith('<?xml version="1.0"')
            assert '<Report>' in xml_content
            assert '<ReportInfo>' in xml_content
            assert '<Sections>' in xml_content
            assert '<DataSources>' in xml_content
            
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
    
    def test_normalize_xml_to_json_structure(self):
        """Test XML normalization produces correct JSON structure"""
        # Sample XML dict (simulating xmltodict output)
        xml_dict = {
            'Report': {
                'ReportInfo': {
                    'Name': 'Test Report',
                    'Version': '13.0',
                    'CreationDate': '2024-01-01',
                    'Author': 'Test Author'
                },
                'Sections': {
                    'Section': {
                        '@Name': 'ReportHeader',
                        'TextObjects': {
                            'TextObject': {
                                '@Name': 'Title',
                                'Text': 'Test Title',
                                'Font': 'Arial, 12pt'
                            }
                        },
                        'FieldObjects': {
                            'FieldObject': {
                                '@Name': 'CustomerName',
                                'DatabaseField': 'Customers.Name'
                            }
                        }
                    }
                },
                'DataSources': {
                    'DataSource': {
                        '@Name': 'MainDB',
                        'ConnectionString': 'test connection',
                        'Tables': {
                            'Table': {'@Name': 'Customers'}
                        }
                    }
                }
            }
        }
        
        # Normalize to JSON
        result = self.parser._normalize_xml_to_json(xml_dict)
        
        # Verify structure
        assert 'report_info' in result
        assert result['report_info']['name'] == 'Test Report'
        assert result['report_info']['version'] == '13.0'
        assert result['report_info']['author'] == 'Test Author'
        
        assert 'sections' in result
        assert len(result['sections']) > 0
        assert result['sections'][0]['name'] == 'ReportHeader'
        
        assert 'data_sources' in result
        assert len(result['data_sources']) > 0
        assert result['data_sources'][0]['name'] == 'MainDB'
        
        assert 'field_lineage' in result
        assert 'CustomerName' in result['field_lineage']


class TestParseResult:
    """Test cases for ParseResult class"""
    
    def test_parse_result_creation(self):
        """Test ParseResult can be created with valid data"""
        result = ParseResult(
            report_id="test-123",
            xml_content="<xml>test</xml>",
            metadata={"test": "data"}
        )
        
        assert result.report_id == "test-123"
        assert result.xml_content == "<xml>test</xml>"
        assert result.metadata == {"test": "data"}


# Integration test (can be run when backend is available)
@pytest.mark.integration
class TestIntegration:
    """Integration tests for full parsing pipeline"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_parsing(self):
        """Test complete parsing flow"""
        parser = ReportParser()
        
        # Create a test .rpt file
        with tempfile.NamedTemporaryFile(suffix='.rpt', delete=False) as temp_file:
            temp_file.write(b"dummy crystal report content")
            temp_file_path = temp_file.name
        
        try:
            # Parse the report
            result = await parser.parse_report(temp_file_path)
            
            # Verify complete result
            assert result.report_id
            assert result.xml_content
            assert result.metadata
            
            # Verify specific metadata fields
            metadata = result.metadata
            assert metadata['report_info']['name']
            assert metadata['sections']
            assert metadata['data_sources']
            assert metadata['field_lineage']
            
        finally:
            os.unlink(temp_file_path) 