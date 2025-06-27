"""
Crystal Copilot MVP - FastAPI Backend
Main application with upload endpoint and RptToXml integration
Week 2: Added GPT-4o Q&A functionality
Week 3: Added Natural Language Editing functionality
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import xmltodict
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.core.report_parser import ReportParser
from backend.core.qa_service import ReportQAService, QARequest, QAResponse
from backend.core.edit_service import ReportEditService, EditRequest, EditResponse
from backend.core.report_renderer import ReportRenderer
from backend.models.report import ReportMetadata

app = FastAPI(
    title="Crystal Copilot MVP",
    description="Crystal Reports modernization API with GPT-4o Q&A and Natural Language Editing",
    version="0.3.0",
)

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
report_parser = ReportParser()
qa_service = ReportQAService()
edit_service = ReportEditService()
report_renderer = ReportRenderer()


class UploadResponse(BaseModel):
    """Response model for upload endpoint"""
    success: bool
    message: str
    report_id: Optional[str] = None
    metadata: Optional[dict] = None


class SuggestedQuestionsResponse(BaseModel):
    """Response model for suggested questions"""
    success: bool
    questions: List[str]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Crystal Copilot MVP API with Q&A", "version": "0.3.0"}


@app.post("/upload", response_model=UploadResponse)
async def upload_report(file: UploadFile = File(...)):
    """
    Upload and parse a Crystal Reports .rpt file
    
    Week 1 Milestone:
    - Accept file upload (≤ 25 MB)
    - Convert .rpt → XML via RptToXml
    - Return raw XML and basic metadata
    
    Week 2 Addition:
    - Store metadata for Q&A queries
    """
    
    # Validate file
    if not file.filename or not file.filename.lower().endswith('.rpt'):
        raise HTTPException(
            status_code=400, 
            detail="Only .rpt files are supported"
        )
    
    # Check file size (25MB limit)
    content = await file.read()
    file_size = len(content)
    
    if file_size > 25 * 1024 * 1024:  # 25MB
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 25MB"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.rpt') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Parse the report
        result = await report_parser.parse_report(temp_file_path, file.filename)
        
        # Store metadata for Q&A (Week 2 addition)
        qa_service.store_report_metadata(result.report_id, result.metadata)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        return UploadResponse(
            success=True,
            message="Report parsed successfully and ready for Q&A",
            report_id=result.report_id,
            metadata=result.metadata
        )
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse report: {str(e)}"
        )


@app.get("/reports/{report_id}/metadata")
async def get_report_metadata(report_id: str):
    """Get parsed metadata for a specific report"""
    metadata = qa_service.get_report_metadata(report_id)
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    
    return {
        "success": True,
        "report_id": report_id,
        "metadata": metadata
    }


@app.post("/reports/{report_id}/ask", response_model=QAResponse)
async def ask_question(report_id: str, request: dict):
    """
    Ask a natural language question about a Crystal Report
    
    Week 2 Milestone:
    - Accept natural language questions
    - Use GPT-4o to analyze report metadata
    - Return intelligent answers with confidence scores
    """
    
    question = request.get("question", "").strip()
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question is required"
        )
    
    # Check if report exists
    if not qa_service.get_report_metadata(report_id):
        raise HTTPException(
            status_code=404,
            detail="Report not found. Please upload the report first."
        )
    
    try:
        response = await qa_service.answer_question(report_id, question)
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@app.get("/reports/{report_id}/suggested-questions", response_model=SuggestedQuestionsResponse)
async def get_suggested_questions(report_id: str):
    """
    Get suggested questions for a Crystal Report
    
    Week 2 Feature:
    - Generate contextual question suggestions based on report content
    - Help users discover what they can ask about their reports
    """
    
    # Check if report exists
    if not qa_service.get_report_metadata(report_id):
        raise HTTPException(
            status_code=404,
            detail="Report not found. Please upload the report first."
        )
    
    try:
        questions = await qa_service.get_suggested_questions(report_id)
        return SuggestedQuestionsResponse(
            success=True,
            questions=questions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate suggested questions: {str(e)}"
        )


# Week 2 Health Check - Test OpenAI Connection
@app.get("/health/openai")
async def check_openai_health():
    """Check if OpenAI API is configured and accessible"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "OPENAI_API_KEY environment variable not set"
        }
    
    try:
        # Test a simple API call
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        return {
            "status": "healthy",
            "message": "OpenAI API connection successful",
            "model": "gpt-4o"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"OpenAI API connection failed: {str(e)}"
        }


# Week 3 Editing Endpoints
@app.post("/reports/{report_id}/preview-edit")
async def preview_edit(report_id: str, request: dict):
    """
    Preview what changes a natural language edit command would make
    
    Week 3 Feature:
    - Parse natural language edit commands
    - Show preview of changes before applying
    - Return structured diff of what will change
    """
    
    command = request.get("command", "").strip()
    if not command:
        raise HTTPException(
            status_code=400,
            detail="Edit command is required"
        )
    
    # Get original report metadata
    original_metadata = qa_service.get_report_metadata(report_id)
    if not original_metadata:
        raise HTTPException(
            status_code=404,
            detail="Report not found. Please upload the report first."
        )
    
    try:
        # Parse the edit command
        edit_command = await edit_service.parse_edit_command(command, original_metadata)
        
        # Apply edit to get modified metadata
        modified_metadata = await edit_service.apply_edit(report_id, edit_command, original_metadata)
        
        # Create preview showing changes
        preview = edit_service.create_edit_preview(original_metadata, modified_metadata)
        
        return EditResponse(
            success=True,
            message="Edit preview generated successfully",
            edit_command={
                "edit_type": edit_command.edit_type.value,
                "target": edit_command.target,
                "new_value": edit_command.new_value,
                "target_section": edit_command.target_section,
                "parameters": edit_command.parameters
            },
            preview=preview
        )
        
    except Exception as e:
        return EditResponse(
            success=False,
            message=f"Failed to preview edit: {str(e)}"
        )

@app.post("/reports/{report_id}/apply-edit")
async def apply_edit(report_id: str, request: dict):
    """
    Apply a natural language edit command to a Crystal Report
    
    Week 3 Milestone:
    - Parse natural language edit commands with GPT-4o
    - Apply structured edits to report metadata
    - Return modified report structure
    """
    
    command = request.get("command", "").strip()
    if not command:
        raise HTTPException(
            status_code=400,
            detail="Edit command is required"
        )
    
    # Get original report metadata
    original_metadata = qa_service.get_report_metadata(report_id)
    if not original_metadata:
        raise HTTPException(
            status_code=404,
            detail="Report not found. Please upload the report first."
        )
    
    try:
        # Parse the edit command
        edit_command = await edit_service.parse_edit_command(command, original_metadata)
        
        # Apply the edit
        modified_metadata = await edit_service.apply_edit(report_id, edit_command, original_metadata)
        
        # Update stored metadata with modified version
        qa_service.store_report_metadata(report_id, modified_metadata)
        
        # Create preview showing what changed
        preview = edit_service.create_edit_preview(original_metadata, modified_metadata)
        
        return EditResponse(
            success=True,
            message="Edit applied successfully",
            edit_command={
                "edit_type": edit_command.edit_type.value,
                "target": edit_command.target,
                "new_value": edit_command.new_value,
                "target_section": edit_command.target_section,
                "parameters": edit_command.parameters
            },
            preview=preview,
            modified_metadata=modified_metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply edit: {str(e)}"
        )

@app.get("/reports/{report_id}/edit-history")
async def get_edit_history(report_id: str):
    """Get the edit history for a report"""
    
    # Check if report exists
    if not qa_service.get_report_metadata(report_id):
        raise HTTPException(
            status_code=404,
            detail="Report not found. Please upload the report first."
        )
    
    try:
        history = edit_service.get_edit_history(report_id)
        return {
            "success": True,
            "report_id": report_id,
            "edit_history": history
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get edit history: {str(e)}"
        )

@app.post("/reports/{report_id}/undo-edit")
async def undo_edit(report_id: str):
    """
    Undo the last edit operation
    
    Week 3 Feature:
    - Revert to previous state
    - Remove last edit from history
    """
    
    # Get current metadata
    current_metadata = qa_service.get_report_metadata(report_id)
    if not current_metadata:
        raise HTTPException(
            status_code=404,
            detail="Report not found. Please upload the report first."
        )
    
    try:
        # Get edit history
        history = edit_service.edit_history.get(report_id, [])
        
        if not history:
            return {
                "success": False,
                "message": "No edits to undo"
            }
        
        # For now, we'll implement a simple approach
        # In a full implementation, you'd store snapshots or implement proper undo logic
        return {
            "success": False,
            "message": "Undo functionality requires report snapshots - coming soon!"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to undo edit: {str(e)}"
        )


# Week 3 Visual Preview Endpoint
@app.post("/reports/{report_id}/visual-preview")
async def get_visual_preview(report_id: str, request: dict):
    """
    Get visual HTML preview of report with optional edit changes
    
    Week 3 Enhancement:
    - Generate HTML/CSS visual representation of report
    - Show side-by-side comparison for edits
    - Highlight changes visually
    """
    
    command = request.get("command", "").strip()
    
    # Get original report metadata
    original_metadata = qa_service.get_report_metadata(report_id)
    if not original_metadata:
        raise HTTPException(
            status_code=404,
            detail="Report not found. Please upload the report first."
        )
    
    try:
        if command:
            # Parse and apply edit command to get modified version
            edit_command = await edit_service.parse_edit_command(command, original_metadata)
            modified_metadata = await edit_service.apply_edit(report_id, edit_command, original_metadata)
            
            # Create preview showing changes
            preview_changes = edit_service.create_edit_preview(original_metadata, modified_metadata)
            
            # Generate side-by-side comparison HTML
            comparison_html = report_renderer.create_comparison_html(
                original_metadata, 
                modified_metadata, 
                preview_changes
            )
            
            return {
                "success": True,
                "message": "Visual preview generated successfully",
                "preview_html": comparison_html,
                "changes": preview_changes
            }
        else:
            # Just show the current report without changes
            report_html = report_renderer.render_report_html(original_metadata)
            
            return {
                "success": True,
                "message": "Report rendered successfully",
                "preview_html": report_html
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate visual preview: {str(e)}"
        )


@app.get("/mock-report-demo")
async def mock_report_demo():
    """
    Mock endpoint for testing Phase 2 visual enhancements on Mac
    Returns sample report metadata to demonstrate enhanced field objects
    """
    
    # Create mock report metadata with various field types
    mock_metadata = {
        "report_info": {
            "name": "Phase 2 Demo Report",
            "version": "2020",
            "author": "Crystal Copilot",
            "creation_date": "2024-06-26"
        },
        "sections": [
            {
                "name": "Report Header",
                "hidden": False,
                "text_objects": [
                    {
                        "name": "Title",
                        "text": "Sales Performance Report",
                        "hidden": False,
                        "formatting": {"bold": True, "font_size": "18px"}
                    }
                ],
                "field_objects": [
                    {
                        "name": "Customer Name",
                        "database_field": "Customers.CustomerName",
                        "formula": "",
                        "hidden": False,
                        "formatting": {}
                    },
                    {
                        "name": "Total Amount",
                        "database_field": "",
                        "formula": "SUM({Orders.Amount})",
                        "hidden": False,
                        "formatting": {"bold": True}
                    },
                    {
                        "name": "Order Date",
                        "database_field": "Orders.OrderDate",
                        "formula": "",
                        "hidden": False,
                        "formatting": {}
                    },
                    {
                        "name": "Is Active",
                        "database_field": "",
                        "formula": "IF {Customer.Status} = \"Active\" THEN True ELSE False",
                        "hidden": False,
                        "formatting": {}
                    },
                    {
                        "name": "Revenue Calculation",
                        "database_field": "",
                        "formula": "SUM({LineItems.Quantity} * {LineItems.UnitPrice}) + {Orders.Tax}",
                        "hidden": False,
                        "formatting": {}
                    }
                ],
                "picture_objects": [
                    {
                        "name": "Company Logo",
                        "image_path": "logo.png",
                        "hidden": False
                    }
                ]
            },
            {
                "name": "Details",
                "hidden": False,
                "text_objects": [],
                "field_objects": [
                    {
                        "name": "Product ID",
                        "database_field": "Products.ProductID",
                        "formula": "",
                        "hidden": False,
                        "formatting": {}
                    },
                    {
                        "name": "Created Date",
                        "database_field": "",
                        "formula": "NOW()",
                        "hidden": False,
                        "formatting": {}
                    },
                    {
                        "name": "Price Total",
                        "database_field": "",
                        "formula": "COUNT({Orders.OrderID}) * AVG({Products.Price})",
                        "hidden": False,
                        "formatting": {}
                    }
                ],
                "picture_objects": []
            }
        ],
        "data_sources": [
            {
                "name": "Sales Database",
                "connection_string": "Data Source=localhost;Initial Catalog=SalesDB",
                "tables": ["Customers", "Orders", "Products", "LineItems"]
            }
        ],
        "formulas": [
            "SUM({Orders.Amount})",
            "IF {Customer.Status} = \"Active\" THEN True ELSE False",
            "SUM({LineItems.Quantity} * {LineItems.UnitPrice}) + {Orders.Tax}",
            "NOW()",
            "COUNT({Orders.OrderID}) * AVG({Products.Price})"
        ]
    }
    
    # Store the mock report in QA service for context menu testing
    mock_report_id = "mock-demo-report"
    qa_service.store_report_metadata(mock_report_id, mock_metadata)
    
    # Generate the enhanced HTML preview
    preview_html = report_renderer.render_report_html(mock_metadata)
    
    return {
        "success": True,
        "message": "Mock report generated for Phase 2 testing",
        "report_id": mock_report_id,
        "metadata": mock_metadata,
        "preview_html": preview_html
    }


# Context Menu API Endpoints
class ObjectActionRequest(BaseModel):
    """Request model for object actions"""
    object_name: str
    object_type: str  # 'field', 'text', 'picture'
    section_name: Optional[str] = None
    action_data: Optional[dict] = {}


class ObjectActionResponse(BaseModel):
    """Response model for object actions"""
    success: bool
    message: str
    object_info: Optional[dict] = None
    action_result: Optional[dict] = None


@app.post("/reports/{report_id}/object/inspect", response_model=ObjectActionResponse)
async def inspect_object(report_id: str, request: ObjectActionRequest):
    """
    Inspect a report object and return detailed information
    Context menu action: "Inspect Object"
    """
    
    # Get report metadata
    metadata = qa_service.get_report_metadata(report_id)
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    
    try:
        # Find the object in the metadata
        object_info = None
        found_section = None
        
        for section in metadata.get('sections', []):
            # Check field objects
            for field_obj in section.get('field_objects', []):
                if field_obj.get('name') == request.object_name:
                    object_info = field_obj.copy()
                    object_info['object_type'] = 'field'
                    found_section = section.get('name')
                    break
            
            # Check text objects
            for text_obj in section.get('text_objects', []):
                if text_obj.get('name') == request.object_name:
                    object_info = text_obj.copy()
                    object_info['object_type'] = 'text'
                    found_section = section.get('name')
                    break
            
            # Check picture objects
            for pic_obj in section.get('picture_objects', []):
                if pic_obj.get('name') == request.object_name:
                    object_info = pic_obj.copy()
                    object_info['object_type'] = 'picture'
                    found_section = section.get('name')
                    break
            
            if object_info:
                break
        
        if not object_info:
            return ObjectActionResponse(
                success=False,
                message=f"Object '{request.object_name}' not found in report"
            )
        
        # Add section information
        object_info['section'] = found_section
        
        # Add data type detection for field objects
        if object_info['object_type'] == 'field':
            data_type = _detect_field_data_type(object_info)
            object_info['detected_data_type'] = data_type
        
        return ObjectActionResponse(
            success=True,
            message=f"Object '{request.object_name}' inspected successfully",
            object_info=object_info,
            action_result={
                "action": "inspect",
                "timestamp": "2024-06-26T21:00:00Z",
                "details": f"Inspected {object_info['object_type']} object in {found_section} section"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to inspect object: {str(e)}"
        )


@app.post("/reports/{report_id}/object/copy", response_model=ObjectActionResponse)
async def copy_object_info(report_id: str, request: ObjectActionRequest):
    """
    Copy object information to clipboard (returns copyable data)
    Context menu action: "Copy Object Name" / "Copy Object Info"
    """
    
    # Get report metadata
    metadata = qa_service.get_report_metadata(report_id)
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    
    try:
        # Find the object and create copyable text
        copy_text = ""
        object_found = False
        
        for section in metadata.get('sections', []):
            # Check all object types
            all_objects = (
                [(obj, 'field') for obj in section.get('field_objects', [])] +
                [(obj, 'text') for obj in section.get('text_objects', [])] +
                [(obj, 'picture') for obj in section.get('picture_objects', [])]
            )
            
            for obj, obj_type in all_objects:
                if obj.get('name') == request.object_name:
                    object_found = True
                    
                    if request.action_data.get('copy_type') == 'name_only':
                        copy_text = obj.get('name', '')
                    elif request.action_data.get('copy_type') == 'formula':
                        copy_text = obj.get('formula', 'No formula')
                    else:
                        # Full object info
                        copy_text = f"Object: {obj.get('name')}\n"
                        copy_text += f"Type: {obj_type}\n"
                        copy_text += f"Section: {section.get('name')}\n"
                        
                        if obj_type == 'field':
                            if obj.get('database_field'):
                                copy_text += f"Database Field: {obj.get('database_field')}\n"
                            if obj.get('formula'):
                                copy_text += f"Formula: {obj.get('formula')}\n"
                        elif obj_type == 'text':
                            copy_text += f"Text: {obj.get('text', '')}\n"
                        elif obj_type == 'picture':
                            copy_text += f"Image Path: {obj.get('image_path', '')}\n"
                    
                    break
            
            if object_found:
                break
        
        if not object_found:
            return ObjectActionResponse(
                success=False,
                message=f"Object '{request.object_name}' not found"
            )
        
        return ObjectActionResponse(
            success=True,
            message=f"Object information copied to clipboard",
            action_result={
                "action": "copy",
                "copy_text": copy_text,
                "copy_type": request.action_data.get('copy_type', 'full'),
                "timestamp": "2024-06-26T21:00:00Z"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to copy object info: {str(e)}"
        )


@app.post("/reports/{report_id}/object/hide", response_model=ObjectActionResponse)
async def hide_object(report_id: str, request: ObjectActionRequest):
    """
    Hide a report object (sets hidden=True)
    Context menu action: "Hide Object"
    """
    
    # Get report metadata
    metadata = qa_service.get_report_metadata(report_id)
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    
    try:
        # Find and hide the object
        object_found = False
        modified_metadata = metadata.copy()
        
        for section in modified_metadata.get('sections', []):
            # Check all object types
            for obj_list_name in ['field_objects', 'text_objects', 'picture_objects']:
                for obj in section.get(obj_list_name, []):
                    if obj.get('name') == request.object_name:
                        obj['hidden'] = True
                        object_found = True
                        break
                if object_found:
                    break
            if object_found:
                break
        
        if not object_found:
            return ObjectActionResponse(
                success=False,
                message=f"Object '{request.object_name}' not found"
            )
        
        # Update the stored metadata
        qa_service.store_report_metadata(report_id, modified_metadata)
        
        return ObjectActionResponse(
            success=True,
            message=f"Object '{request.object_name}' hidden successfully",
            action_result={
                "action": "hide",
                "object_name": request.object_name,
                "timestamp": "2024-06-26T21:00:00Z",
                "reversible": True
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to hide object: {str(e)}"
        )


@app.post("/reports/{report_id}/object/duplicate", response_model=ObjectActionResponse)
async def duplicate_object(report_id: str, request: ObjectActionRequest):
    """
    Duplicate a report object (creates a copy with modified name)
    Context menu action: "Duplicate Object"
    """
    
    # Get report metadata
    metadata = qa_service.get_report_metadata(report_id)
    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    
    try:
        # Find the object to duplicate
        object_found = False
        modified_metadata = metadata.copy()
        
        for section in modified_metadata.get('sections', []):
            # Check all object types
            for obj_list_name in ['field_objects', 'text_objects', 'picture_objects']:
                obj_list = section.get(obj_list_name, [])
                for i, obj in enumerate(obj_list):
                    if obj.get('name') == request.object_name:
                        # Create duplicate
                        duplicate_obj = obj.copy()
                        duplicate_obj['name'] = f"{obj.get('name')} Copy"
                        
                        # Insert after original
                        obj_list.insert(i + 1, duplicate_obj)
                        object_found = True
                        break
                if object_found:
                    break
            if object_found:
                break
        
        if not object_found:
            return ObjectActionResponse(
                success=False,
                message=f"Object '{request.object_name}' not found"
            )
        
        # Update the stored metadata
        qa_service.store_report_metadata(report_id, modified_metadata)
        
        return ObjectActionResponse(
            success=True,
            message=f"Object '{request.object_name}' duplicated successfully",
            action_result={
                "action": "duplicate",
                "original_name": request.object_name,
                "duplicate_name": f"{request.object_name} Copy",
                "timestamp": "2024-06-26T21:00:00Z"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to duplicate object: {str(e)}"
        )


def _detect_field_data_type(field_obj: dict) -> str:
    """Helper function to detect field data type"""
    
    field_name = field_obj.get('name', '').lower()
    database_field = field_obj.get('database_field', '').lower()
    formula = field_obj.get('formula', '').lower()
    
    # Date patterns
    date_keywords = ['date', 'time', 'created', 'modified', 'updated', 'timestamp']
    if any(keyword in field_name for keyword in date_keywords):
        return 'date'
    if any(keyword in database_field for keyword in date_keywords):
        return 'date'
    if 'now()' in formula or 'date' in formula:
        return 'date'
    
    # Number patterns
    number_keywords = ['amount', 'total', 'price', 'cost', 'sum', 'count', 'avg', 'id']
    if any(keyword in field_name for keyword in number_keywords):
        return 'number'
    if 'sum(' in formula or 'count(' in formula or 'avg(' in formula:
        return 'number'
    
    # Boolean patterns
    bool_keywords = ['is', 'has', 'active', 'enabled', 'visible']
    if any(field_name.startswith(keyword) for keyword in bool_keywords):
        return 'boolean'
    if 'if ' in formula and 'then' in formula:
        return 'boolean'
    
    # Currency patterns
    currency_keywords = ['revenue', 'payment', 'salary', 'fee']
    if any(keyword in field_name for keyword in currency_keywords):
        return 'currency'
    
    # Default to text
    return 'text'


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)