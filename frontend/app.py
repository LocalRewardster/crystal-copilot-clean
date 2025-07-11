"""
Crystal Copilot - Professional B2B Interface
Modern Crystal Reports modernization platform with sidebar navigation
"""

import json
import requests
import streamlit as st
from typing import Dict, Any, List

# Configure Streamlit page with modern styling
st.set_page_config(
    page_title="Crystal Copilot",
    page_icon="CR",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Loom-inspired professional layout
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    .stApp > header {
        background-color: transparent;
    }
    
    .stApp {
        background: #fafafa;
        min-height: 100vh;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
        margin: 0;
        padding-left: 0;
        padding-right: 0;
    }
    
    /* Show sidebar with Loom-style design */
    .css-1d391kg {
        display: block !important;
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
        padding: 1rem;
    }
    
    /* Sidebar content styling */
    .css-1d391kg .css-1v0mbdj {
        color: #374151;
    }
    
    /* Main content area */
    .css-18e3th9 {
        background: #ffffff;
        margin-left: 280px;
        padding: 2rem;
        min-height: 100vh;
    }
    
    /* Header styling */
    .app-header {
        background: #ffffff;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #e5e7eb;
        margin: -2rem -2rem 2rem -2rem;
    }
    
    .app-title {
        color: #111827;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .app-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* Sidebar branding */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
    }
    
    .brand-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .brand-text {
        color: #111827;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
    }
    
    /* Navigation sections */
    .nav-section {
        margin: 1.5rem 0 0.75rem 0;
    }
    
    .nav-section-title {
        color: #6b7280;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    /* Navigation buttons */
    .stButton > button {
        background: transparent;
        color: #374151;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.2s ease;
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        margin-bottom: 0.25rem;
    }
    
    .stButton > button:hover {
        background: #f3f4f6;
        color: #111827;
    }
    
    .stButton > button[kind="primary"] {
        background: #3b82f6;
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #2563eb;
        color: white;
    }
    
    /* Content cards */
    .content-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .content-card h3 {
        color: #111827;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .content-card p {
        color: #6b7280;
        font-size: 0.875rem;
        margin: 0;
        line-height: 1.5;
    }
    
    /* Upload area */
    .upload-area {
        background: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    .upload-title {
        color: #111827;
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .upload-subtitle {
        color: #6b7280;
        font-size: 0.875rem;
        margin-bottom: 1.5rem;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.375rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    .status-healthy {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-error {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Feature grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-color: #3b82f6;
    }
    
    .feature-icon {
        width: 48px;
        height: 48px;
        background: #eff6ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #3b82f6;
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
    
    .feature-card h3 {
        color: #111827;
        font-size: 1.125rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .feature-card p {
        color: #6b7280;
        font-size: 0.875rem;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Hide Streamlit menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: transparent;
        border: none;
        padding: 0;
    }
    
    .stFileUploader label {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

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
    """Display natural language editing interface with improved preview layout"""
    
    st.header("Report Editor")
    st.markdown("Make changes to your Crystal Report using natural language commands.")
    
    # Check OpenAI status
    openai_status = check_openai_health()
    if openai_status.get("status") == "error":
        st.warning(f"WARNING: OpenAI API Issue: {openai_status.get('message')}")
        st.info("NOTE: Set your OPENAI_API_KEY environment variable to enable editing functionality.")
        return
    
    # Command Input Section - Full Width
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
        <h3 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.25rem; font-weight: 600;">📝 Edit Command</h3>
        <p style="margin: 0; color: #64748b; font-size: 0.875rem;">Describe what you want to change in plain English</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create input area with examples in expandable section
    col_input, col_examples = st.columns([2, 1])
    
    with col_input:
        # Command input
        edit_command = st.text_input(
            "Enter your edit command:",
            placeholder="e.g., Rename 'Customer Name' to 'Client Name'",
            help="Describe what you want to change in plain English",
            label_visibility="collapsed"
        )
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            preview_button = st.button("👁️ Preview", type="secondary", disabled=not edit_command.strip(), use_container_width=True)
        with col_btn2:
            apply_button = st.button("✅ Apply", type="primary", disabled=not edit_command.strip(), use_container_width=True)
    
    with col_examples:
        # Example commands for guidance
        with st.expander("💡 Example Commands"):
            st.markdown("""
            **Field Operations:**
            - "Rename 'Customer Name' to 'Client Name'"
            - "Hide the 'Internal ID' field"
            - "Move 'Total Amount' to footer"
            - "Make 'Company Name' bold"
            
            **Text Changes:**
            - "Change title to 'Q4 Sales Report'"
            - "Hide the 'Old Logo' text"
            
            **Section Operations:**
            - "Hide the page header"
            - "Show the report footer"
            """)
    
    # Initialize session state for preview mode
    if 'preview_mode' not in st.session_state:
        st.session_state.preview_mode = False
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None
    
    # Process Preview Command
    if preview_button and edit_command.strip():
        with st.spinner("🔄 Generating visual preview..."):
            # Get visual preview with changes
            visual_result = get_visual_preview(report_id, edit_command.strip())
            
            if visual_result.get("success"):
                st.session_state.preview_mode = True
                st.session_state.preview_data = {
                    'command': edit_command.strip(),
                    'result': visual_result
                }
                st.rerun()
            else:
                st.error(f"❌ Preview Error: {visual_result.get('message', 'Preview failed')}")
    
    # Process Apply Command
    if apply_button and edit_command.strip():
        with st.spinner("⚙️ Applying changes..."):
            result = apply_edit(report_id, edit_command.strip())
            
            if result.get("success"):
                st.success("✅ Edit applied successfully!")
                
                # Show what changed
                preview = result.get("preview", {})
                if preview.get("changes"):
                    st.info(f"**Applied:** {preview.get('summary', 'Changes applied')}")
                    for change in preview["changes"]:
                        if isinstance(change, dict):
                            # New structured format
                            change_type = change.get("type", "unknown")
                            description = change.get("description", str(change))
                            
                            # Add icons based on change type
                            icon_map = {
                                "rename": "🏷️",
                                "hide": "👁️‍🗨️",
                                "show": "👁️",
                                "move": "📦",
                                "text_change": "📝",
                                "format": "🎨",
                                "hide_section": "📂",
                                "show_section": "📁"
                            }
                            
                            icon = icon_map.get(change_type, "✓")
                            st.write(f"{icon} {description}")
                        else:
                            # Fallback for old string format
                            st.write(f"• {change}")
                
                # Update session state
                if 'edit_applied' not in st.session_state:
                    st.session_state.edit_applied = 0
                st.session_state.edit_applied += 1
                
                # Refresh metadata
                st.session_state.current_metadata = result.get("modified_metadata", st.session_state.current_metadata)
                
                # Clear preview mode and refresh
                st.session_state.preview_mode = False
                st.session_state.preview_data = None
                st.rerun()
                
            else:
                st.error(f"❌ Apply Error: {result.get('message', 'Apply failed')}")
    
    # Visual Preview Section - Much Larger and More Prominent
    st.markdown("---")
    
    if st.session_state.preview_mode and st.session_state.preview_data:
        # PREVIEW MODE - Show Before/After Comparison
        st.markdown("""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 2px solid #3b82f6; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="width: 12px; height: 12px; background: #3b82f6; border-radius: 50%; animation: pulse 2s infinite;"></div>
                <h2 style="margin: 0; color: #1e40af; font-size: 1.5rem; font-weight: 700;">📋 Preview Changes</h2>
            </div>
            <p style="margin: 0; color: #3730a3; font-size: 1rem; font-weight: 500;">
                Command: "{}"
            </p>
        </div>
        """.format(st.session_state.preview_data['command']), unsafe_allow_html=True)
        
        # Show changes summary
        changes = st.session_state.preview_data['result'].get("changes", {})
        if changes.get("changes"):
            st.success(f"**Changes Detected:** {changes.get('summary', 'Modifications found')}")
            
            # Display structured changes
            for change in changes["changes"]:
                if isinstance(change, dict):
                    # New structured format
                    change_type = change.get("type", "unknown")
                    description = change.get("description", str(change))
                    
                    # Add icons based on change type
                    icon_map = {
                        "rename": "🏷️",
                        "hide": "👁️‍🗨️",
                        "show": "👁️",
                        "move": "📦",
                        "text_change": "📝",
                        "format": "🎨",
                        "hide_section": "📂",
                        "show_section": "📁"
                    }
                    
                    icon = icon_map.get(change_type, "✓")
                    st.write(f"{icon} {description}")
                    
                    # Show additional details in smaller text
                    details = []
                    if change.get("section"):
                        details.append(f"Section: {change['section']}")
                    if change.get("old_value") and change.get("new_value"):
                        details.append(f"'{change['old_value']}' → '{change['new_value']}'")
                    
                    if details:
                        st.caption("   " + " | ".join(details))
                else:
                    # Fallback for old string format
                    st.write(f"✓ {change}")
        else:
            st.info("ℹ️ No changes detected - the command may not match any existing fields or sections.")
        
        # Before/After Comparison with Tabs
        tab1, tab2 = st.tabs(["🔍 **MODIFIED REPORT** (Preview)", "📄 **ORIGINAL REPORT** (Current)"])
        
        with tab1:
            st.markdown("""
            <div style="background: #f0fdf4; border: 2px solid #22c55e; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%;"></div>
                    <span style="font-weight: 600; color: #15803d; font-size: 1rem;">Preview with Your Changes Applied</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show modified preview - FULL WIDTH
            preview_html = st.session_state.preview_data['result'].get("preview_html", "")
            if preview_html:
                enhanced_html = f"""
                <div style="border: 2px solid #22c55e; border-radius: 8px; overflow: hidden; background: white; box-shadow: 0 4px 20px rgba(34, 197, 94, 0.1);">
                    {preview_html}
                    <style>
                    body {{ margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
                    </style>
                </div>
                """
                st.components.v1.html(enhanced_html, height=800, scrolling=True)
            else:
                st.warning("No preview HTML available")
        
        with tab2:
            st.markdown("""
            <div style="background: #f8fafc; border: 2px solid #64748b; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 8px; height: 8px; background: #64748b; border-radius: 50%;"></div>
                    <span style="font-weight: 600; color: #475569; font-size: 1rem;">Current Report (Before Changes)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show original report
            display_enhanced_visual_preview(report_id)
        
        # Action buttons for preview mode
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("❌ Cancel Preview", type="secondary", use_container_width=True):
                st.session_state.preview_mode = False
                st.session_state.preview_data = None
                st.rerun()
        with col2:
            if st.button("✅ Apply These Changes", type="primary", use_container_width=True):
                # Apply the previewed changes
                with st.spinner("⚙️ Applying changes..."):
                    result = apply_edit(report_id, st.session_state.preview_data['command'])
                    
                    if result.get("success"):
                        st.success("✅ Changes applied successfully!")
                        st.session_state.preview_mode = False
                        st.session_state.preview_data = None
                        st.session_state.current_metadata = result.get("modified_metadata", st.session_state.current_metadata)
                        st.rerun()
                    else:
                        st.error(f"❌ Apply failed: {result.get('message', 'Unknown error')}")
    
    else:
        # NORMAL MODE - Show Current Report
        st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%;"></div>
                <h2 style="margin: 0; color: #1e293b; font-size: 1.5rem; font-weight: 700;">📄 Current Report</h2>
            </div>
            <p style="margin: 0; color: #64748b; font-size: 1rem;">This is how your report currently looks. Use the command above to preview changes.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show current report - FULL WIDTH
        display_enhanced_visual_preview(report_id)
    
    # Edit History Section
    st.markdown("---")
    st.markdown("""
    <div style="background: #fafafa; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; margin-top: 2rem;">
        <h3 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.25rem; font-weight: 600;">📚 Edit History</h3>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.info("💡 No edits have been applied to this report yet. Try making your first change above!")

def display_enhanced_visual_preview(report_id: str):
    """Simplified visual preview without context menu functionality"""
    
    with st.spinner("🔄 Loading report preview..."):
        visual_result = get_visual_preview(report_id)
        if visual_result.get("success"):
            # Display the HTML preview with clean styling
            preview_html = visual_result.get("preview_html", "")
            if preview_html:
                st.markdown("""
                <div style="background: white; border: 2px solid #e2e8f0; border-radius: 8px; padding: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; padding-bottom: 0.75rem; border-bottom: 1px solid #f1f5f9;">
                        <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%;"></div>
                        <span style="font-size: 0.875rem; font-weight: 500; color: #1e293b;">Current Report Layout</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Enhanced iframe with disabled right-click
                enhanced_html = f"""
                <div style="border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; background: #fafbfc;">
                    {preview_html}
                    <style>
                    /* Completely disable right-click context menu */
                    * {{
                        -webkit-user-select: none;
                        -moz-user-select: none;
                        -ms-user-select: none;
                        user-select: none;
                        -webkit-touch-callout: none;
                        -webkit-tap-highlight-color: transparent;
                    }}
                    
                    /* Disable context menu completely */
                    body, html, * {{
                        context-menu: none !important;
                        -webkit-context-menu: none !important;
                        -moz-context-menu: none !important;
                    }}
                    </style>
                    <script>
                    // Disable right-click context menu completely
                    document.addEventListener('contextmenu', function(e) {{
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }}, true);
                    
                    // Disable right-click on all elements
                    document.addEventListener('mousedown', function(e) {{
                        if (e.button === 2) {{ // Right mouse button
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        }}
                    }}, true);
                    
                    // Disable context menu on touch devices
                    document.addEventListener('touchstart', function(e) {{
                        if (e.touches.length > 1) {{
                            e.preventDefault();
                        }}
                    }}, true);
                    
                    // Additional protection against context menu
                    window.addEventListener('contextmenu', function(e) {{
                        e.preventDefault();
                        return false;
                    }}, true);
                    
                    // Disable drag and drop
                    document.addEventListener('dragstart', function(e) {{
                        e.preventDefault();
                        return false;
                    }}, true);
                    </script>
                </div>
                """
                
                st.components.v1.html(enhanced_html, height=650, scrolling=True)
                
            else:
                st.markdown("""
                <div style="text-align: center; padding: 3rem; background: #f8fafc; border: 2px dashed #d1d5db; border-radius: 8px;">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">📄</div>
                    <h3 style="color: #6b7280; margin: 0;">No Visual Preview Available</h3>
                    <p style="color: #9ca3af; margin: 0.5rem 0 0 0;">The report structure will appear here once processed.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: center; padding: 3rem; background: #fef2f2; border: 2px solid #fecaca; border-radius: 8px;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">⚠️</div>
                <h3 style="color: #dc2626; margin: 0;">Preview Error</h3>
                <p style="color: #991b1b; margin: 0.5rem 0 0 0;">{visual_result.get('message', 'Unknown error occurred')}</p>
            </div>
            """, unsafe_allow_html=True)

def display_qa_interface(report_id: str):
    """Display Q&A interface for the uploaded report with modern styling"""
    
    # Check OpenAI status
    openai_status = check_openai_health()
    if openai_status.get("status") == "error":
        st.markdown("""
        <div class="content-card">
            <h3>AI Services Unavailable</h3>
            <p>OpenAI API connection issue: {}</p>
            <p><strong>Note:</strong> Set your OPENAI_API_KEY environment variable to enable Q&A functionality.</p>
        </div>
        """.format(openai_status.get('message')), unsafe_allow_html=True)
        return
    
    # Get suggested questions
    suggested_questions = get_suggested_questions(report_id)
    
    # Question input section
    st.markdown("""
    <div class="content-card">
        <h3>Ask Questions About Your Report</h3>
        <p>Use natural language to explore your Crystal Reports structure, data sources, and formulas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        placeholder="What data sources does this report use?",
        help="Ask about report structure, formulas, data sources, or any other aspect"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("Ask Question", type="primary", disabled=not question.strip())
    
    # Suggested questions
    if suggested_questions:
        st.markdown("**Suggested Questions:**")
        cols = st.columns(2)
        for i, suggested_q in enumerate(suggested_questions[:6]):  # Show up to 6 suggestions
            with cols[i % 2]:
                if st.button(f"• {suggested_q}", key=f"suggested_{i}", use_container_width=True):
                    question = suggested_q
                    ask_button = True
    
    # Process question
    if ask_button and question.strip():
        with st.spinner("Analyzing your question..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/reports/{report_id}/ask",
                    json={"question": question}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("answer", "No answer provided")
                    
                    # Display answer in a nice format
                    st.markdown("""
                    <div class="content-card">
                        <h4>Answer</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(answer)
                    
                    # Show confidence and sources if available
                    if "confidence" in result:
                        st.caption(f"Confidence: {result['confidence']:.1%}")
                else:
                    st.error(f"Error: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {str(e)}")
            except Exception as e:
                st.error(f"Error processing question: {str(e)}")
    
    # Show conversation history if available
    if 'qa_history' not in st.session_state:
        st.session_state.qa_history = []
    
    if st.session_state.qa_history:
        st.markdown("---")
        st.markdown("### Recent Questions")
        
        for i, (q, a) in enumerate(reversed(st.session_state.qa_history[-5:])):  # Show last 5
            with st.expander(f"Q: {q[:80]}{'...' if len(q) > 80 else ''}"):
                st.markdown(f"**Question:** {q}")
                st.markdown(f"**Answer:** {a}")
    
    # Add current Q&A to history
    if ask_button and question.strip() and 'answer' in locals():
        st.session_state.qa_history.append((question, answer))

def main():
    """Main Streamlit application with Loom-inspired layout"""
    
    # Initialize session state
    if 'current_report_id' not in st.session_state:
        st.session_state.current_report_id = None
    if 'current_metadata' not in st.session_state:
        st.session_state.current_metadata = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'upload'
    
    # Sidebar Navigation (Loom-style)
    with st.sidebar:
        # Brand section
        st.markdown("""
        <div class="sidebar-brand">
            <div class="brand-icon">CC</div>
            <div class="brand-text">Crystal Copilot</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Current report status (always visible)
        if st.session_state.current_report_id:
            metadata = st.session_state.current_metadata
            report_name = metadata.get('report_info', {}).get('name', 'Unknown Report') if metadata else 'Unknown Report'
            
            st.markdown('<div class="nav-section-title">Current Report</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="content-card" style="background: #eff6ff; border-color: #3b82f6;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1e40af; font-size: 1rem; font-weight: 600;">{report_name}</h4>
                <p style="margin: 0 0 0.5rem 0; color: #3730a3; font-size: 0.75rem;">Report ID: {st.session_state.current_report_id[:8]}...</p>
                <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
                    <span style="background: #dbeafe; color: #1e40af; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 500;">
                        {len(metadata.get("data_sources", [])) if metadata else 0} Tables
                    </span>
                    <span style="background: #dbeafe; color: #1e40af; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 500;">
                        {len(metadata.get("formulas", [])) if metadata else 0} Formulas
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="nav-section-title">No Report Loaded</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="content-card" style="background: #eff6ff; border-color: #3b82f6;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1e40af; font-size: 0.875rem; font-weight: 600;">Upload a Report</h4>
                <p style="margin: 0; color: #3730a3; font-size: 0.75rem;">Select "Upload Report" below to get started with Crystal Reports analysis.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Main navigation
        st.markdown('<div class="nav-section-title">Workspace</div>', unsafe_allow_html=True)
        
        # Upload button - always visible and clearly labeled
        upload_button_text = "Upload New Report" if st.session_state.current_report_id else "Upload Report"
        if st.button(upload_button_text, key="nav_upload", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'upload' else "secondary"):
            st.session_state.current_page = 'upload'
            st.rerun()
        
        # Report tools (only show if report is loaded)
        if st.session_state.current_report_id:
            st.markdown('<div class="nav-section-title">Analysis Tools</div>', unsafe_allow_html=True)
            
            if st.button("AI Assistant", key="nav_ai", use_container_width=True,
                        type="primary" if st.session_state.current_page == 'ai_assistant' else "secondary"):
                st.session_state.current_page = 'ai_assistant'
                st.rerun()
            
            if st.button("Report Editor", key="nav_editor", use_container_width=True,
                        type="primary" if st.session_state.current_page == 'editor' else "secondary"):
                st.session_state.current_page = 'editor'
                st.rerun()
            
            if st.button("Report Analysis", key="nav_analysis", use_container_width=True,
                        type="primary" if st.session_state.current_page == 'analysis' else "secondary"):
                st.session_state.current_page = 'analysis'
                st.rerun()
            
            if st.button("Raw Data", key="nav_raw", use_container_width=True,
                        type="primary" if st.session_state.current_page == 'raw_data' else "secondary"):
                st.session_state.current_page = 'raw_data'
                st.rerun()
        
        # System status
        st.markdown('<div class="nav-section-title">System Status</div>', unsafe_allow_html=True)
        
        openai_status = check_openai_health()
        if openai_status.get("status") == "healthy":
            st.markdown('<div class="status-indicator status-healthy">Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator status-error">Offline</div>', unsafe_allow_html=True)
    
    # Main content area with header
    if st.session_state.current_report_id:
        metadata = st.session_state.current_metadata
        report_name = metadata.get('report_info', {}).get('name', 'Unknown Report') if metadata else 'Unknown Report'
        
        st.markdown(f"""
        <div class="app-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 class="app-title">Crystal Copilot</h1>
                    <p class="app-subtitle">Working on: <strong style="color: #3b82f6;">{report_name}</strong></p>
                </div>
                <div style="text-align: right;">
                    <div style="background: #eff6ff; border: 1px solid #3b82f6; border-radius: 8px; padding: 0.75rem; display: inline-block;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.875rem;">Report Loaded</div>
                        <div style="color: #3730a3; font-size: 0.75rem; margin-top: 0.25rem;">
                            {len(metadata.get("data_sources", [])) if metadata else 0} Tables • 
                            {len(metadata.get("formulas", [])) if metadata else 0} Formulas • 
                            {len(metadata.get("sections", [])) if metadata else 0} Sections
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="app-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 class="app-title">Crystal Copilot</h1>
                    <p class="app-subtitle">Enterprise Crystal Reports modernization platform</p>
                </div>
                <div style="text-align: right;">
                    <div style="background: #eff6ff; border: 1px solid #3b82f6; border-radius: 8px; padding: 0.75rem; display: inline-block;">
                        <div style="color: #1e40af; font-weight: 600; font-size: 0.875rem;">No Report Loaded</div>
                        <div style="color: #3730a3; font-size: 0.75rem; margin-top: 0.25rem;">Upload a .rpt file to get started</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Content based on current page
    if st.session_state.current_page == 'upload':
        display_upload_interface()
    elif st.session_state.current_page == 'ai_assistant':
        if st.session_state.current_report_id:
            display_qa_interface(st.session_state.current_report_id)
        else:
            st.markdown("""
            <div class="content-card">
                <h3>No Report Loaded</h3>
                <p>Please upload a Crystal Reports file first to use the AI Assistant.</p>
            </div>
            """, unsafe_allow_html=True)
    elif st.session_state.current_page == 'editor':
        if st.session_state.current_report_id:
            display_editor_interface(st.session_state.current_report_id)
        else:
            st.markdown("""
            <div class="content-card">
                <h3>No Report Loaded</h3>
                <p>Please upload a Crystal Reports file first to use the Report Editor.</p>
            </div>
            """, unsafe_allow_html=True)
    elif st.session_state.current_page == 'analysis':
        if st.session_state.current_report_id:
            display_analysis_interface(st.session_state.current_report_id)
        else:
            st.markdown("""
            <div class="content-card">
                <h3>No Report Loaded</h3>
                <p>Please upload a Crystal Reports file first to view the analysis.</p>
            </div>
            """, unsafe_allow_html=True)
    elif st.session_state.current_page == 'raw_data':
        if st.session_state.current_report_id:
            display_raw_data_interface(st.session_state.current_report_id)
        else:
            st.markdown("""
            <div class="content-card">
                <h3>No Report Loaded</h3>
                <p>Please upload a Crystal Reports file first to view the raw data.</p>
            </div>
            """, unsafe_allow_html=True)

def display_upload_interface():
    """Loom-style upload interface with organized content cards"""
    
    # Show current report status if one is loaded
    if st.session_state.current_report_id:
        metadata = st.session_state.current_metadata
        report_name = metadata.get('report_info', {}).get('name', 'Unknown Report') if metadata else 'Unknown Report'
        
        st.markdown(f"""
        <div class="content-card" style="background: #eff6ff; border-color: #3b82f6; margin-bottom: 2rem;">
            <h3 style="color: #1e40af; margin-bottom: 1rem;">Currently Working On: {report_name}</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e40af;">{len(metadata.get("data_sources", [])) if metadata else 0}</div>
                    <div style="font-size: 0.875rem; color: #3730a3;">Database Tables</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e40af;">{len(metadata.get("formulas", [])) if metadata else 0}</div>
                    <div style="font-size: 0.875rem; color: #3730a3;">Formulas</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e40af;">{len(metadata.get("sections", [])) if metadata else 0}</div>
                    <div style="font-size: 0.875rem; color: #3730a3;">Sections</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e40af;">{len(metadata.get("parameters", [])) if metadata else 0}</div>
                    <div style="font-size: 0.875rem; color: #3730a3;">Parameters</div>
                </div>
            </div>
            <p style="color: #3730a3; margin: 0; font-size: 0.875rem;">
                Report ID: {st.session_state.current_report_id} • Use the tools in the sidebar to analyze and edit this report.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Upload a New Report")
        st.markdown("Upload a different Crystal Reports file to replace the current one:")
    else:
        st.markdown("### Get Started")
        st.markdown("Upload your first Crystal Reports file to begin analysis:")
    
    # Upload section
    st.markdown("""
    <div class="upload-area">
        <div class="upload-title">Upload Crystal Reports File</div>
        <div class="upload-subtitle">Select a .rpt file to begin AI-powered analysis and modernization</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a Crystal Reports file",
        type=['rpt'],
        help="Upload a .rpt file to analyze its structure and content",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Show warning if replacing existing report
        if st.session_state.current_report_id:
            st.warning("⚠️ Uploading a new file will replace the current report. All unsaved work will be lost.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cancel Upload", type="secondary", use_container_width=True):
                    st.rerun()
            with col2:
                proceed = st.button("Continue with Upload", type="primary", use_container_width=True)
        else:
            proceed = True
        
        if proceed:
            with st.spinner("Processing Crystal Reports file..."):
                try:
                    # Upload file to backend
                    files = {"file": (uploaded_file.name, uploaded_file.read(), "application/octet-stream")}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        report_id = result["report_id"]
                    
                    # Store in session state
                        st.session_state.current_report_id = report_id
                        st.session_state.current_metadata = result.get("metadata", {})
                        
                        st.success(f"Successfully processed: {uploaded_file.name}")
                        
                        # Auto-navigate to AI Assistant
                        st.session_state.current_page = 'ai_assistant'
                        st.rerun()
                        
                    else:
                        st.error(f"Upload failed: {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {str(e)}")
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
    
    # Feature overview
    if not st.session_state.current_report_id:
        st.markdown("### Platform Capabilities")
        
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">AI</div>
                <h3>AI-Powered Analysis</h3>
                <p>Ask natural language questions about your Crystal Reports and get instant insights about data sources, formulas, and structure.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">EDIT</div>
                <h3>Smart Editing</h3>
                <p>Modify your reports using natural language commands. Update formulas, change formatting, and restructure layouts effortlessly.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">VIEW</div>
                <h3>Visual Preview</h3>
                <p>See your reports rendered as modern HTML with preserved formatting and structure for easy review and validation.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_ai_assistant_interface():
    """AI Assistant page with modern layout"""
    
    st.markdown("""
    <div class="main-header">
        <h1>AI Assistant</h1>
        <p>Ask natural language questions about your Crystal Report structure, data sources, and logic</p>
    </div>
    """, unsafe_allow_html=True)
    
    display_qa_interface(st.session_state.current_report_id)

def display_editor_interface(report_id: str):
    """Report Editor page with modern layout"""
    
    st.markdown("""
    <div class="main-header">
        <h1>Report Editor</h1>
        <p>Modify your Crystal Report using natural language commands with preview and version control</p>
    </div>
    """, unsafe_allow_html=True)
    
    display_edit_interface(report_id)

def display_analysis_interface(report_id: str):
    """Report Analysis page with modern layout"""
    
    st.markdown("""
    <div class="main-header">
        <h1>Report Analysis</h1>
        <p>Comprehensive analysis of your Crystal Report structure, data sources, and field relationships</p>
    </div>
    """, unsafe_allow_html=True)
    
    display_metadata(st.session_state.current_metadata)

def display_raw_data_interface(report_id: str):
    """Raw Data page with modern layout"""
    
    st.markdown("""
    <div class="main-header">
        <h1>Raw Data</h1>
        <p>Complete JSON metadata extracted from your Crystal Report for technical analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>Complete Report Metadata</h3>
        <p>This is the raw JSON data extracted from your Crystal Report, including all sections, fields, formulas, and data sources.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.json(st.session_state.current_metadata)

if __name__ == "__main__":
    main()
