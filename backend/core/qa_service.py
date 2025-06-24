"""
Crystal Reports Q&A Service - Week 2 Implementation
Uses OpenAI GPT-4o to answer natural language questions about report metadata
"""

import json
import os
from typing import Dict, List, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel


class QARequest(BaseModel):
    """Request model for Q&A queries"""
    report_id: str
    question: str


class QAResponse(BaseModel):
    """Response model for Q&A queries"""
    success: bool
    answer: str
    confidence: Optional[float] = None
    sources: Optional[List[str]] = None


class ReportQAService:
    """Service for answering questions about Crystal Reports using GPT-4o"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            # For testing or when API key is not available
            self.client = None
        # In-memory storage for parsed reports (Week 2 implementation)
        # In production, this would be a proper database
        self.report_cache: Dict[str, Dict] = {}

    def store_report_metadata(self, report_id: str, metadata: Dict) -> None:
        """Store parsed report metadata for Q&A queries"""
        self.report_cache[report_id] = metadata

    def get_report_metadata(self, report_id: str) -> Optional[Dict]:
        """Retrieve stored report metadata"""
        return self.report_cache.get(report_id)

    async def answer_question(self, report_id: str, question: str) -> QAResponse:
        """
        Answer a natural language question about a Crystal Report
        
        Uses GPT-4o to analyze report metadata and provide intelligent answers
        """
        
        # Get report metadata
        metadata = self.get_report_metadata(report_id)
        if not metadata:
            return QAResponse(
                success=False,
                answer="Report not found. Please upload the report first."
            )

        # Check if OpenAI client is available
        if not self.client:
            return QAResponse(
                success=False,
                answer="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )

        try:
            # Create a comprehensive context about the report
            context = self._create_report_context(metadata)
            
            # Generate the prompt for GPT-4o
            prompt = self._create_qa_prompt(context, question)
            
            # Query OpenAI GPT-4o
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Crystal Reports expert assistant. You help users understand their Crystal Reports by analyzing the report metadata and answering questions about report structure, data sources, fields, formulas, and relationships. Provide clear, accurate, and helpful answers based on the report metadata provided."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent, factual responses
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Extract confidence and sources if available
            confidence = self._estimate_confidence(answer, metadata)
            sources = self._identify_sources(answer, metadata)
            
            return QAResponse(
                success=True,
                answer=answer,
                confidence=confidence,
                sources=sources
            )
            
        except Exception as e:
            return QAResponse(
                success=False,
                answer=f"Sorry, I encountered an error while processing your question: {str(e)}"
            )

    def _create_report_context(self, metadata: Dict) -> str:
        """Create a comprehensive context string from report metadata"""
        
        context_parts = []
        
        # Report basic info
        report_info = metadata.get('report_info', {})
        context_parts.append(f"Report Name: {report_info.get('name', 'Unknown')}")
        context_parts.append(f"Version: {report_info.get('version', 'Unknown')}")
        context_parts.append(f"Created: {report_info.get('creation_date', 'Unknown')}")
        context_parts.append(f"Author: {report_info.get('author', 'Unknown')}")
        
        # Data sources
        data_sources = metadata.get('data_sources', [])
        if data_sources:
            context_parts.append("\nDATA SOURCES:")
            for ds in data_sources:
                context_parts.append(f"- {ds.get('name', 'Unknown')}")
                context_parts.append(f"  Connection: {ds.get('connection_string', 'Not specified')}")
                tables = ds.get('tables', [])
                if tables:
                    context_parts.append(f"  Tables: {', '.join(tables)}")
        
        # Sections
        sections = metadata.get('sections', [])
        if sections:
            context_parts.append("\nREPORT SECTIONS:")
            for section in sections:
                section_name = section.get('name', 'Unknown')
                context_parts.append(f"- {section_name}")
                
                # Text objects
                text_objects = section.get('text_objects', [])
                if text_objects:
                    context_parts.append("  Text Objects:")
                    for obj in text_objects:
                        context_parts.append(f"    • {obj.get('name', 'Unknown')}: \"{obj.get('text', '')}\"")
                
                # Field objects
                field_objects = section.get('field_objects', [])
                if field_objects:
                    context_parts.append("  Field Objects:")
                    for obj in field_objects:
                        name = obj.get('name', 'Unknown')
                        db_field = obj.get('database_field', '')
                        formula = obj.get('formula', '')
                        if db_field:
                            context_parts.append(f"    • {name} → {db_field}")
                        elif formula:
                            context_parts.append(f"    • {name} → Formula: {formula}")
                
                # Picture objects
                picture_objects = section.get('picture_objects', [])
                if picture_objects:
                    context_parts.append("  Picture Objects:")
                    for obj in picture_objects:
                        context_parts.append(f"    • {obj.get('name', 'Unknown')}: {obj.get('image_path', '')}")
        
        # Field lineage
        field_lineage = metadata.get('field_lineage', {})
        if field_lineage:
            context_parts.append("\nFIELD LINEAGE:")
            for field_name, lineage in field_lineage.items():
                source = lineage.get('source', 'Unknown')
                formula = lineage.get('formula', '')
                section = lineage.get('section', 'Unknown')
                
                if formula:
                    context_parts.append(f"- {field_name}: Formula '{formula}' in {section} section")
                else:
                    context_parts.append(f"- {field_name}: Database field '{source}' in {section} section")
        
        return "\n".join(context_parts)

    def _create_qa_prompt(self, context: str, question: str) -> str:
        """Create a prompt for GPT-4o with report context and user question"""
        
        return f"""Based on the following Crystal Report metadata, please answer the user's question accurately and helpfully.

CRYSTAL REPORT METADATA:
{context}

USER QUESTION: {question}

Please provide a clear, specific answer based on the report metadata above. If the question cannot be answered from the available metadata, please explain what information would be needed to answer it properly.

Focus on being helpful and educational - explain not just what the answer is, but provide context about how Crystal Reports work when relevant."""

    def _estimate_confidence(self, answer: str, metadata: Dict) -> float:
        """Estimate confidence level based on answer content and available metadata"""
        
        # Simple heuristic - in production this could be more sophisticated
        confidence = 0.8  # Base confidence
        
        # Lower confidence if answer contains uncertainty phrases
        uncertainty_phrases = [
            "not sure", "unclear", "cannot determine", "might be", "possibly",
            "it appears", "seems like", "probably"
        ]
        
        answer_lower = answer.lower()
        for phrase in uncertainty_phrases:
            if phrase in answer_lower:
                confidence -= 0.2
                break
        
        # Higher confidence if answer references specific metadata elements
        if any(ds.get('name', '').lower() in answer_lower for ds in metadata.get('data_sources', [])):
            confidence += 0.1
        
        if any(field in answer_lower for field in metadata.get('field_lineage', {}).keys()):
            confidence += 0.1
        
        return max(0.1, min(1.0, confidence))

    def _identify_sources(self, answer: str, metadata: Dict) -> List[str]:
        """Identify which parts of the metadata were likely used to answer the question"""
        
        sources = []
        answer_lower = answer.lower()
        
        # Check if data sources were referenced
        for ds in metadata.get('data_sources', []):
            if ds.get('name', '').lower() in answer_lower:
                sources.append(f"Data Source: {ds.get('name')}")
        
        # Check if sections were referenced
        for section in metadata.get('sections', []):
            if section.get('name', '').lower() in answer_lower:
                sources.append(f"Section: {section.get('name')}")
        
        # Check if fields were referenced
        for field_name in metadata.get('field_lineage', {}).keys():
            if field_name.lower() in answer_lower:
                sources.append(f"Field: {field_name}")
        
        return sources[:5]  # Limit to top 5 sources

    async def get_suggested_questions(self, report_id: str) -> List[str]:
        """Generate suggested questions based on report metadata"""
        
        metadata = self.get_report_metadata(report_id)
        if not metadata:
            return []
        
        suggestions = []
        
        # Basic questions everyone might ask
        suggestions.extend([
            "What data sources does this report use?",
            "What are the main sections of this report?",
            "Show me all the calculated fields and formulas."
        ])
        
        # Data source specific questions
        data_sources = metadata.get('data_sources', [])
        if len(data_sources) > 1:
            suggestions.append("How many different databases does this report connect to?")
        
        if data_sources:
            ds_names = [ds.get('name', '') for ds in data_sources]
            suggestions.append(f"What tables are used from {ds_names[0]}?")
        
        # Field-specific questions
        field_lineage = metadata.get('field_lineage', {})
        formula_fields = [name for name, lineage in field_lineage.items() 
                         if lineage.get('formula')]
        
        if formula_fields:
            suggestions.append("Which fields use formulas instead of direct database fields?")
        
        # Section-specific questions
        sections = metadata.get('sections', [])
        if any(section.get('picture_objects') for section in sections):
            suggestions.append("What images or logos are included in this report?")
        
        return suggestions[:6]  # Return top 6 suggestions 