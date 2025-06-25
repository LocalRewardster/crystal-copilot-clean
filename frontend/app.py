"""
Crystal Copilot MVP - Streamlit Frontend
Drag-and-drop interface for Crystal Reports upload and analysis
Week 2: Added GPT-4o Q&A functionality
"""

import json
import requests
import streamlit as st
from typing import Dict, Any, List

# Configure Streamlit page
st.set_page_config(
    page_title="Crystal Copilot MVP",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API configuration
API_BASE_URL = "http://localhost:8000"

def upload_report(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Upload report file to FastAPI backend"""
    files = {"file": (filename, file_bytes, "application/octet-stream")}
    
    try:
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("ERROR: Cannot connect to backend API. Make sure FastAPI is running on port 8000.")
        return {"success": False, "message": "Backend connection failed"}
    except requests.exceptions.RequestException as e:
        st.error(f"ERROR: Upload failed: {str(e)}")
        return {"success": False, "message": str(e)}

def ask_question(report_id: str, question: str) -> Dict[str, Any]:
    """Ask a question about the report"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/reports/{report_id}/ask",
            json={"question": question}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("ERROR: Cannot connect to backend API. Make sure FastAPI is running on port 8000.")
        return {"success": False, "answer": "Backend connection failed"}
    except requests.exceptions.RequestException as e:
        st.error(f"ERROR: Question failed: {str(e)}")
        return {"success": False, "answer": str(e)}

def get_suggested_questions(report_id: str) -> List[str]:
    """Get suggested questions for the report"""
    try:
        response = requests.get(f"{API_BASE_URL}/reports/{report_id}/suggested-questions")
        response.raise_for_status()
        result = response.json()
        return result.get("questions", [])
    except requests.exceptions.RequestException:
        return []

def check_openai_health() -> Dict[str, Any]:
    """Check OpenAI API health"""
    try:
        response = requests.get(f"{API_BASE_URL}/health/openai")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"status": "error", "message": "Cannot check OpenAI status"}

def preview_edit(report_id: str, command: str) -> Dict[str, Any]:
    """Preview what changes an edit command would make"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/reports/{report_id}/preview-edit",
            json={"command": command}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("ERROR: Cannot connect to backend API. Make sure FastAPI is running on port 8000.")
        return {"success": False, "message": "Backend connection failed"}
    except requests.exceptions.RequestException as e:
        st.error(f"ERROR: Preview failed: {str(e)}")
        return {"success": False, "message": str(e)}

def apply_edit(report_id: str, command: str) -> Dict[str, Any]:
    """Apply an edit command to the report"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/reports/{report_id}/apply-edit",
            json={"command": command}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("ERROR: Cannot connect to backend API. Make sure FastAPI is running on port 8000.")
        return {"success": False, "message": "Backend connection failed"}
    except requests.exceptions.RequestException as e:
        st.error(f"ERROR: Apply edit failed: {str(e)}")
        return {"success": False, "message": str(e)}

def get_edit_history(report_id: str) -> List[Dict]:
    """Get edit history for the report"""
    try:
        response = requests.get(f"{API_BASE_URL}/reports/{report_id}/edit-history")
        response.raise_for_status()
        result = response.json()
        return result.get("edit_history", [])
    except requests.exceptions.RequestException:
        return []

def get_visual_preview(report_id: str, command: str = "") -> Dict[str, Any]:
    """Get visual HTML preview of the report"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/reports/{report_id}/visual-preview",
            json={"command": command}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("ERROR: Cannot connect to backend API. Make sure FastAPI is running on port 8000.")
        return {"success": False, "message": "Backend connection failed"}
    except requests.exceptions.RequestException as e:
        st.error(f"ERROR: Visual preview failed: {str(e)}")
        return {"success": False, "message": str(e)}

def display_qa_interface(report_id: str):
    """Display Q&A interface for the uploaded report"""
    
    st.header("AI Assistant")
    st.markdown("Use natural language to understand your Crystal Report structure and data flow.")
    
    # Check OpenAI status
    openai_status = check_openai_health()
    if openai_status.get("status") == "error":
        st.warning(f"WARNING: OpenAI API Issue: {openai_status.get('message')}")
        st.info("NOTE: Set your OPENAI_API_KEY environment variable to enable Q&A functionality.")
        return
    
    # Get suggested questions
    suggested_questions = get_suggested_questions(report_id)
    
    # Question input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question = st.text_input(
            "Ask a question about your report:",
            placeholder="e.g., What data sources does this report use?",
            help="Ask about data sources, fields, formulas, sections, or relationships"
        )
    
    with col2:
        ask_button = st.button("Ask", type="primary", disabled=not question.strip())
    
    # Suggested questions
    if suggested_questions:
        st.subheader("Suggested Questions")
        
        # Display suggested questions as clickable buttons
        cols = st.columns(2)
        for i, suggested_q in enumerate(suggested_questions):
            with cols[i % 2]:
                if st.button(f"{suggested_q}", key=f"suggested_{i}"):
                    question = suggested_q
                    ask_button = True
    
    # Process question
    if ask_button and question.strip():
        with st.spinner("Processing your question..."):
            result = ask_question(report_id, question.strip())
            
            if result.get("success"):
                # Display answer
                st.subheader("Answer")
                st.markdown(result.get("answer", "No answer provided"))
                
                # Display confidence and sources if available
                col1, col2 = st.columns(2)
                
                with col1:
                    confidence = result.get("confidence")
                    if confidence is not None:
                        st.metric("Confidence", f"{confidence:.1%}")
                
                with col2:
                    sources = result.get("sources", [])
                    if sources:
                        st.write("**Sources:**")
                        for source in sources:
                            st.write(f"• {source}")
            else:
                st.error(f"ERROR: {result.get('answer', 'Failed to get answer')}")

def display_metadata(metadata: Dict[str, Any]):
    """Display parsed report metadata in structured format"""
    
    # Report Info
    st.subheader("Report Information")
    report_info = metadata.get('report_info', {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Report Name", report_info.get('name', 'Unknown'))
    with col2:
        st.metric("Version", report_info.get('version', 'Unknown'))
    with col3:
        st.metric("Created", report_info.get('creation_date', 'Unknown'))
    with col4:
        st.metric("Author", report_info.get('author', 'Unknown'))
    
    # Quick Stats
    sections = metadata.get('sections', [])
    data_sources = metadata.get('data_sources', [])
    field_lineage = metadata.get('field_lineage', {})
    
    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sections", len(sections))
    with col2:
        st.metric("Data Sources", len(data_sources))
    with col3:
        st.metric("Fields", len(field_lineage))
    
    # Sections
    st.subheader("Report Sections")
    
    if sections:
        for section in sections:
            with st.expander(f"Section: {section.get('name', 'Unknown')}"):
                
                # Text Objects
                text_objects = section.get('text_objects', [])
                if text_objects:
                    st.write("**Text Objects:**")
                    for obj in text_objects:
                        st.write(f"- {obj.get('name', 'Unknown')}: {obj.get('text', 'No text')}")
                
                # Field Objects
                field_objects = section.get('field_objects', [])
                if field_objects:
                    st.write("**Field Objects:**")
                    for obj in field_objects:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{obj.get('name', 'Unknown')}**")
                        with col2:
                            if obj.get('database_field'):
                                st.write(f"Source: {obj['database_field']}")
                            elif obj.get('formula'):
                                st.write(f"Formula: {obj['formula']}")
                
                # Picture Objects
                picture_objects = section.get('picture_objects', [])
                if picture_objects:
                    st.write("**Picture Objects:**")
                    for obj in picture_objects:
                        st.write(f"- {obj.get('name', 'Unknown')}: {obj.get('image_path', 'No path')}")
    
    # Data Sources
    st.subheader("Data Sources")
    
    if data_sources:
        for ds in data_sources:
            with st.expander(f"Data Source: {ds.get('name', 'Unknown')}"):
                st.code(ds.get('connection_string', 'No connection string'), language='text')
                
                tables = ds.get('tables', [])
                if tables:
                    st.write("**Tables:**")
                    st.write(", ".join(tables))
    
    # Field Lineage
    st.subheader("Field Lineage")
    
    if field_lineage:
        for field_name, lineage_info in field_lineage.items():
            with st.expander(f"Field: {field_name}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Source:** {lineage_info.get('source', 'Unknown')}")
                    st.write(f"**Section:** {lineage_info.get('section', 'Unknown')}")
                with col2:
                    if lineage_info.get('formula'):
                        st.write("**Formula:**")
                        st.code(lineage_info['formula'], language='sql')

def display_edit_interface(report_id: str):
    """Display natural language editing interface"""
    
    st.header("Report Editor")
    st.markdown("Make changes to your Crystal Report using natural language commands.")
    
    # Check OpenAI status
    openai_status = check_openai_health()
    if openai_status.get("status") == "error":
        st.warning(f"WARNING: OpenAI API Issue: {openai_status.get('message')}")
        st.info("NOTE: Set your OPENAI_API_KEY environment variable to enable editing functionality.")
        return
    
    # Create two columns for input and preview
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Edit command input
        st.subheader("Edit Command")
        
        # Example commands for guidance
        with st.expander("Example Commands"):
            st.markdown("""
            **Field Operations:**
            - "Rename 'Customer Name' to 'Client Name'"
            - "Hide the 'Internal ID' field"
            - "Move 'Total Amount' to the footer section"
            - "Make 'Company Name' bold"
            
            **Text Changes:**
            - "Change the title to 'Q4 Sales Report'"
            - "Hide the 'Old Logo' text"
            
            **Section Operations:**
            - "Hide the page header"
            - "Show the report footer"
            """)
        
        # Command input
        edit_command = st.text_input(
            "Enter your edit command:",
            placeholder="e.g., Rename 'Customer Name' to 'Client Name'",
            help="Describe what you want to change in plain English"
        )
        
        # Buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            preview_button = st.button("Preview Changes", type="secondary", disabled=not edit_command.strip())
        
        with col_btn2:
            apply_button = st.button("Apply Changes", type="primary", disabled=not edit_command.strip())
    
    with col2:
        # Visual Preview Area
        st.subheader("Visual Preview")
        
        # Show current report or preview
        if 'show_visual_preview' not in st.session_state:
            st.session_state.show_visual_preview = True
        
        # Always show current report initially
        if st.session_state.show_visual_preview:
            with st.spinner("Loading report preview..."):
                visual_result = get_visual_preview(report_id)
                if visual_result.get("success"):
                    # Display the HTML preview
                    preview_html = visual_result.get("preview_html", "")
                    if preview_html:
                        st.markdown("**Current Report Layout:**")
                        st.components.v1.html(preview_html, height=600, scrolling=True)
                    else:
                        st.info("No visual preview available")
                else:
                    st.error(f"Failed to load preview: {visual_result.get('message', 'Unknown error')}")
    
    # Process commands
    if preview_button and edit_command.strip():
        with st.spinner("Generating visual preview..."):
            # Get visual preview with changes
            visual_result = get_visual_preview(report_id, edit_command.strip())
            
            if visual_result.get("success"):
                # Update the preview area
                with col2:
                    st.subheader("Preview Changes")
                    preview_html = visual_result.get("preview_html", "")
                    if preview_html:
                        st.components.v1.html(preview_html, height=700, scrolling=True)
                    
                    # Show text summary
                    changes = visual_result.get("changes", {})
                    if changes.get("changes"):
                        st.success(f"**Preview:** {changes.get('summary', 'Changes detected')}")
                        for change in changes["changes"]:
                            st.write(f"• {change}")
                    else:
                        st.warning("No changes detected in preview")
            else:
                st.error(f"ERROR: {visual_result.get('message', 'Preview failed')}")
    
    if apply_button and edit_command.strip():
        with st.spinner("Applying edit..."):
            result = apply_edit(report_id, edit_command.strip())
            
            if result.get("success"):
                st.success("Edit applied successfully!")
                
                # Show what changed
                preview = result.get("preview", {})
                if preview.get("changes"):
                    st.info(f"**Applied:** {preview.get('summary', 'Changes applied')}")
                    for change in preview["changes"]:
                        st.write(f"• {change}")
                
                # Update session state to trigger refresh
                if 'edit_applied' not in st.session_state:
                    st.session_state.edit_applied = 0
                st.session_state.edit_applied += 1
                
                # Refresh metadata
                st.session_state.current_metadata = result.get("modified_metadata", st.session_state.current_metadata)
                
                # Refresh visual preview to show updated report
                st.session_state.show_visual_preview = True
                
                # Clear the input and refresh
                st.rerun()
                
            else:
                st.error(f"ERROR: {result.get('message', 'Apply failed')}")
    
    # Edit History (moved below the main interface)
    st.divider()
    st.subheader("Edit History")
    
    edit_history = get_edit_history(report_id)
    
    if edit_history:
        st.write(f"**{len(edit_history)} edit(s) applied to this report:**")
        
        for i, edit in enumerate(reversed(edit_history), 1):
            with st.expander(f"Edit {i}: {edit.get('edit_type', 'Unknown').replace('_', ' ').title()}"):
                st.write(f"**Target:** {edit.get('target', 'Unknown')}")
                if edit.get('new_value'):
                    st.write(f"**New Value:** {edit.get('new_value')}")
                if edit.get('target_section'):
                    st.write(f"**Target Section:** {edit.get('target_section')}")
                if edit.get('parameters'):
                    st.write(f"**Parameters:** {edit.get('parameters')}")
    else:
        st.info("No edits have been applied to this report yet.")

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("Crystal Copilot")
    st.markdown("**Enterprise Crystal Reports modernization platform**")
    
    # Sidebar
    with st.sidebar:
        st.header("Getting Started")
        st.markdown("""
        1. **Upload** your .rpt file
        2. **Analyze** report structure
        3. **Ask questions** with AI
        4. **Make edits** with natural language
        """)
        
        st.header("Platform Features")
        st.markdown("""
        - File upload & parsing
        - Field lineage analysis
        - **AI Q&A with GPT-4o**
        - **Natural language editing**
        """)
        
        # OpenAI status check
        st.header("System Status")
        openai_status = check_openai_health()
        if openai_status.get("status") == "healthy":
            st.success("OpenAI API Connected")
        else:
            st.error("OpenAI API Issue")
    
    # Initialize session state
    if 'current_report_id' not in st.session_state:
        st.session_state.current_report_id = None
    if 'current_metadata' not in st.session_state:
        st.session_state.current_metadata = None
    
    # Main content area
    st.header("Upload Crystal Report")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a Crystal Reports file (.rpt)",
        type=['rpt'],
        help="Upload a Crystal Reports file (≤ 25MB) to analyze its structure and ask questions"
    )
    
    if uploaded_file is not None:
        # File info
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filename", uploaded_file.name)
        with col2:
            st.metric("Size", f"{file_size_mb:.2f} MB")
        with col3:
            st.metric("Type", uploaded_file.type or "Crystal Report")
        
        # Upload button
        if st.button("Analyze Report", type="primary"):
            with st.spinner("Uploading and analyzing report..."):
                # Upload to backend
                result = upload_report(uploaded_file.getvalue(), uploaded_file.name)
                
                # Debug information
                st.write("DEBUG - Upload result:", result)
                
                if result.get("success"):
                    st.success(f"SUCCESS: {result.get('message', 'Report analyzed successfully!')}")
                    
                    # Store in session state
                    report_id = result.get('report_id')
                    metadata = result.get('metadata')
                    
                    # Debug session state update
                    st.write(f"DEBUG - Report ID: {report_id}")
                    st.write(f"DEBUG - Metadata keys: {list(metadata.keys()) if metadata else 'None'}")
                    
                    if report_id and metadata:
                        st.session_state.current_report_id = report_id
                        st.session_state.current_metadata = metadata
                        st.write("DEBUG - Session state updated successfully")
                        
                        # Force refresh to show tabs
                        st.rerun()
                    else:
                        st.error("ERROR: Missing report_id or metadata in response")
                else:
                    st.error(f"ERROR: {result.get('message', 'Upload failed')}")
                    st.write("DEBUG - Full error response:", result)
    
    # Display Q&A interface if report is loaded
    if st.session_state.current_report_id and st.session_state.current_metadata:
        st.divider()
        
        # Debug session state
        st.write("DEBUG - Session State:")
        st.write(f"- Report ID: {st.session_state.current_report_id}")
        st.write(f"- Metadata available: {bool(st.session_state.current_metadata)}")
        if st.session_state.current_metadata:
            st.write(f"- Metadata keys: {list(st.session_state.current_metadata.keys())}")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["AI Assistant", "Report Editor", "Report Analysis", "Raw Data"])
        
        with tab1:
            display_qa_interface(st.session_state.current_report_id)
        
        with tab2:
            display_edit_interface(st.session_state.current_report_id)
        
        with tab3:
            display_metadata(st.session_state.current_metadata)
        
        with tab4:
            st.subheader("Raw Metadata JSON")
            st.json(st.session_state.current_metadata)
    
    # Demo section (only show if no report loaded)
    if not st.session_state.current_report_id:
        st.divider()
        st.header("Platform Capabilities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current Features")
            st.markdown("""
            Available now:
            - *"What data sources does this report use?"*
            - *"Which fields use formulas?"*
            - *"Show me all calculated fields"*
            - *"Rename 'Customer Name' to 'Client Name'"*
            - *"Hide the 'Internal ID' field"*
            - *"Move 'Total' to footer section"*
            """)
        
        with col2:
            st.subheader("Enterprise Ready")
            st.markdown("""
            Professional capabilities:
            - *Secure report processing*
            - *Edit history & version control*
            - *Preview before apply*
            - *Structured change management*
            - *Integration-ready APIs*
            """)

if __name__ == "__main__":
    main()
