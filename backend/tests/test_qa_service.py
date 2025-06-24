"""
Unit tests for Crystal Reports Q&A Service
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.core.qa_service import ReportQAService, QAResponse


class TestReportQAService:
    """Test cases for ReportQAService class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.qa_service = ReportQAService()
        
        # Sample metadata for testing
        self.sample_metadata = {
            'report_info': {
                'name': 'Test Sales Report',
                'version': '13.0',
                'creation_date': '2024-01-01',
                'author': 'Test User'
            },
            'data_sources': [
                {
                    'name': 'ERP_Database',
                    'connection_string': 'Provider=SQLOLEDB;Server=test-server;Database=ERP',
                    'tables': ['Customers', 'Orders', 'Products']
                }
            ],
            'sections': [
                {
                    'name': 'ReportHeader',
                    'text_objects': [
                        {'name': 'Title', 'text': 'Sales Report', 'font': 'Arial, 14pt'}
                    ],
                    'field_objects': [],
                    'picture_objects': []
                },
                {
                    'name': 'Details',
                    'text_objects': [],
                    'field_objects': [
                        {'name': 'CustomerName', 'database_field': 'Customers.CustomerName', 'formula': ''},
                        {'name': 'OrderTotal', 'database_field': '', 'formula': 'Sum({Orders.Amount})'}
                    ],
                    'picture_objects': []
                }
            ],
            'field_lineage': {
                'CustomerName': {
                    'source': 'Customers.CustomerName',
                    'formula': '',
                    'section': 'Details'
                },
                'OrderTotal': {
                    'source': 'Formula',
                    'formula': 'Sum({Orders.Amount})',
                    'section': 'Details'
                }
            }
        }
    
    def test_service_initialization(self):
        """Test Q&A service initializes correctly"""
        assert self.qa_service.client is not None
        assert self.qa_service.report_cache == {}
    
    def test_store_and_retrieve_metadata(self):
        """Test storing and retrieving report metadata"""
        report_id = "test-report-123"
        
        # Store metadata
        self.qa_service.store_report_metadata(report_id, self.sample_metadata)
        
        # Retrieve metadata
        retrieved = self.qa_service.get_report_metadata(report_id)
        
        assert retrieved == self.sample_metadata
        assert retrieved['report_info']['name'] == 'Test Sales Report'
    
    def test_get_nonexistent_metadata(self):
        """Test retrieving non-existent metadata returns None"""
        result = self.qa_service.get_report_metadata("nonexistent-id")
        assert result is None
    
    def test_create_report_context(self):
        """Test creating report context from metadata"""
        context = self.qa_service._create_report_context(self.sample_metadata)
        
        # Verify context contains key information
        assert 'Test Sales Report' in context
        assert 'ERP_Database' in context
        assert 'Customers' in context
        assert 'Orders' in context
        assert 'CustomerName' in context
        assert 'Sum({Orders.Amount})' in context
    
    def test_create_qa_prompt(self):
        """Test creating Q&A prompt"""
        context = "Test report context"
        question = "What data sources does this report use?"
        
        prompt = self.qa_service._create_qa_prompt(context, question)
        
        assert context in prompt
        assert question in prompt
        assert "CRYSTAL REPORT METADATA:" in prompt
        assert "USER QUESTION:" in prompt
    
    def test_estimate_confidence(self):
        """Test confidence estimation"""
        # High confidence answer
        high_conf_answer = "This report uses the ERP_Database data source with Customers and Orders tables."
        confidence = self.qa_service._estimate_confidence(high_conf_answer, self.sample_metadata)
        assert confidence > 0.8
        
        # Low confidence answer
        low_conf_answer = "I'm not sure about the data sources, it might be using some database."
        confidence = self.qa_service._estimate_confidence(low_conf_answer, self.sample_metadata)
        assert confidence < 0.8
    
    def test_identify_sources(self):
        """Test source identification"""
        answer = "The report uses ERP_Database and includes CustomerName field in the Details section."
        sources = self.qa_service._identify_sources(answer, self.sample_metadata)
        
        # Should identify data source, field, and section
        source_types = [source.split(':')[0] for source in sources]
        assert 'Data Source' in source_types
        assert 'Field' in source_types
        assert 'Section' in source_types
    
    @pytest.mark.asyncio
    async def test_answer_question_nonexistent_report(self):
        """Test answering question for non-existent report"""
        response = await self.qa_service.answer_question("nonexistent-id", "Test question")
        
        assert response.success is False
        assert "Report not found" in response.answer
    
    @pytest.mark.asyncio
    async def test_get_suggested_questions(self):
        """Test getting suggested questions"""
        report_id = "test-report-123"
        self.qa_service.store_report_metadata(report_id, self.sample_metadata)
        
        questions = await self.qa_service.get_suggested_questions(report_id)
        
        assert len(questions) > 0
        assert any("data sources" in q.lower() for q in questions)
        assert any("sections" in q.lower() for q in questions)
        assert any("fields" in q.lower() or "formulas" in q.lower() for q in questions)
    
    @pytest.mark.asyncio
    async def test_get_suggested_questions_nonexistent_report(self):
        """Test getting suggested questions for non-existent report"""
        questions = await self.qa_service.get_suggested_questions("nonexistent-id")
        assert questions == []
    
    @pytest.mark.asyncio
    @patch('backend.core.qa_service.AsyncOpenAI')
    async def test_answer_question_success(self, mock_openai_class):
        """Test successful question answering"""
        # Mock OpenAI response
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This report uses the ERP_Database data source."
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Store metadata and ask question
        report_id = "test-report-123"
        self.qa_service.store_report_metadata(report_id, self.sample_metadata)
        
        response = await self.qa_service.answer_question(report_id, "What data sources does this report use?")
        
        assert response.success is True
        assert "ERP_Database" in response.answer
        assert response.confidence is not None
        assert response.sources is not None
    
    @pytest.mark.asyncio
    @patch('backend.core.qa_service.AsyncOpenAI')
    async def test_answer_question_openai_error(self, mock_openai_class):
        """Test handling OpenAI API errors"""
        # Mock OpenAI to raise an exception
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        # Store metadata and ask question
        report_id = "test-report-123"
        self.qa_service.store_report_metadata(report_id, self.sample_metadata)
        
        response = await self.qa_service.answer_question(report_id, "Test question")
        
        assert response.success is False
        assert "error" in response.answer.lower()


class TestQAModels:
    """Test cases for Q&A request/response models"""
    
    def test_qa_response_creation(self):
        """Test QAResponse model creation"""
        response = QAResponse(
            success=True,
            answer="Test answer",
            confidence=0.85,
            sources=["Data Source: TestDB"]
        )
        
        assert response.success is True
        assert response.answer == "Test answer"
        assert response.confidence == 0.85
        assert response.sources == ["Data Source: TestDB"]
    
    def test_qa_response_minimal(self):
        """Test QAResponse with minimal required fields"""
        response = QAResponse(
            success=False,
            answer="Error message"
        )
        
        assert response.success is False
        assert response.answer == "Error message"
        assert response.confidence is None
        assert response.sources is None 