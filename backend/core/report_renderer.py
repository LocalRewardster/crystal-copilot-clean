"""
Crystal Reports Visual Renderer - Week 3 Enhancement
Converts report metadata into HTML/CSS visual representation
"""

import json
from typing import Dict, List, Optional, Tuple


class ReportRenderer:
    """Service for rendering Crystal Reports metadata as HTML/CSS visual layouts"""

    def __init__(self):
        pass

    def render_report_html(self, metadata: Dict, highlight_changes: Optional[Dict] = None) -> str:
        """
        Convert report metadata to HTML/CSS visual representation
        
        Args:
            metadata: Report metadata dictionary
            highlight_changes: Optional dict of changes to highlight
        
        Returns:
            HTML string representing the visual report layout
        """
        
        sections = metadata.get('sections', [])
        report_info = metadata.get('report_info', {})
        
        # Generate CSS styles
        css_styles = self._generate_css_styles()
        
        # Generate HTML structure
        html_content = []
        
        # Report container
        html_content.append('<div class="crystal-report">')
        
        # Report title bar
        html_content.append('<div class="report-title-bar">')
        html_content.append(f'<h3>{report_info.get("name", "Crystal Report")}</h3>')
        html_content.append(f'<span class="report-info">Version: {report_info.get("version", "Unknown")} | Author: {report_info.get("author", "Unknown")}</span>')
        html_content.append('</div>')
        
        # Render each section
        for section in sections:
            section_html = self._render_section(section, highlight_changes)
            html_content.append(section_html)
        
        html_content.append('</div>')
        
        # Combine CSS and HTML
        full_html = f"""
        <style>
        {css_styles}
        </style>
        {''.join(html_content)}
        """
        
        return full_html

    def _render_section(self, section: Dict, highlight_changes: Optional[Dict] = None) -> str:
        """Render a single report section"""
        
        section_name = section.get('name', 'Unknown')
        is_hidden = section.get('hidden', False)
        
        # Determine section CSS class
        section_class = f"report-section section-{section_name.lower().replace(' ', '-')}"
        if is_hidden:
            section_class += " section-hidden"
        
        # Check if this section has changes
        has_changes = False
        if highlight_changes:
            changes = highlight_changes.get('changes', [])
            for change in changes:
                if section_name.lower() in change.lower():
                    has_changes = True
                    break
        
        if has_changes:
            section_class += " section-changed"
        
        html = []
        html.append(f'<div class="{section_class}">')
        
        # Section header
        html.append('<div class="section-header">')
        html.append(f'<span class="section-name">{section_name}</span>')
        if is_hidden:
            html.append('<span class="hidden-indicator">HIDDEN</span>')
        html.append('</div>')
        
        # Section content
        html.append('<div class="section-content">')
        
        # Render text objects
        text_objects = section.get('text_objects', [])
        for text_obj in text_objects:
            obj_html = self._render_text_object(text_obj, highlight_changes)
            html.append(obj_html)
        
        # Render field objects
        field_objects = section.get('field_objects', [])
        for field_obj in field_objects:
            obj_html = self._render_field_object(field_obj, highlight_changes)
            html.append(obj_html)
        
        # Render picture objects
        picture_objects = section.get('picture_objects', [])
        for pic_obj in picture_objects:
            obj_html = self._render_picture_object(pic_obj, highlight_changes)
            html.append(obj_html)
        
        html.append('</div>')
        html.append('</div>')
        
        return ''.join(html)

    def _render_text_object(self, text_obj: Dict, highlight_changes: Optional[Dict] = None) -> str:
        """Render a text object with context menu support"""
        
        name = text_obj.get('name', 'Text')
        text = text_obj.get('text', '')
        is_hidden = text_obj.get('hidden', False)
        formatting = text_obj.get('formatting', {})
        
        # Check for changes
        is_changed = False
        if highlight_changes:
            changes = highlight_changes.get('changes', [])
            for change in changes:
                if name.lower() in change.lower():
                    is_changed = True
                    break
        
        css_class = "text-object"
        if is_hidden:
            css_class += " object-hidden"
        if is_changed:
            css_class += " object-changed"
        
        # Apply formatting styles
        style_attrs = []
        if formatting.get('bold'):
            style_attrs.append('font-weight: bold')
        if formatting.get('italic'):
            style_attrs.append('font-style: italic')
        if formatting.get('font_size'):
            style_attrs.append(f'font-size: {formatting["font_size"]}')
        
        style_str = f'style="{"; ".join(style_attrs)}"' if style_attrs else ''
        
        # Generate unique ID for context menu
        text_id = f"text-{name.replace(' ', '-').replace('(', '').replace(')', '').lower()}"
        
        return f'''
        <div class="{css_class}" {style_str}
             id="{text_id}"
             data-object-name="{name}"
             data-object-type="text"
             data-tooltip="Text Object: {name}"
             oncontextmenu="showTextContextMenu(event, '{text_id}'); return false;">
            <span class="object-label">{name}:</span>
            <span class="object-content">{text}</span>
            {('<span class="hidden-indicator">HIDDEN</span>' if is_hidden else '')}
            {('<span class="changed-indicator">CHANGED</span>' if is_changed else '')}
        </div>
        '''

    def _render_field_object(self, field_obj: Dict, highlight_changes: Optional[Dict] = None) -> str:
        """Render a field object with enhanced visualization and context menu support"""
        
        name = field_obj.get('name', 'Unknown Field')
        database_field = field_obj.get('database_field', '')
        formula = field_obj.get('formula', '')
        is_hidden = field_obj.get('hidden', False)
        formatting = field_obj.get('formatting', {})
        
        # Detect data type intelligently
        data_type = self._detect_field_data_type(name, database_field, formula)
        type_info = self._get_data_type_info(data_type)
        
        is_formula = bool(formula)
        source_type = 'Formula' if is_formula else 'Database'
        source_value = formula if is_formula else database_field
        
        # Check if this field was changed
        is_changed = False
        if highlight_changes and highlight_changes.get('fields'):
            is_changed = name in highlight_changes['fields']
        
        css_class = "field-object"
        if is_hidden:
            css_class += " object-hidden"
        if is_changed:
            css_class += " object-changed"
        
        # Apply formatting styles
        style_attrs = []
        if formatting.get('bold'):
            style_attrs.append('font-weight: bold')
        if formatting.get('italic'):
            style_attrs.append('font-style: italic')
        if formatting.get('font_size'):
            style_attrs.append(f'font-size: {formatting["font_size"]}')
        
        style_str = f'style="{"; ".join(style_attrs)}"' if style_attrs else ''
        
        # Generate unique ID for context menu
        field_id = f"field-{name.replace(' ', '-').replace('(', '').replace(')', '').lower()}"
        
        # Enhanced field object HTML with context menu support
        return f'''
        <div class="{css_class}" {style_str} 
             id="{field_id}" 
             data-field-name="{name}"
             data-field-type="{data_type}"
             data-source-type="{source_type}"
             data-tooltip="Field: {name} | Type: {data_type} | Source: {source_type}"
             oncontextmenu="showContextMenu(event, '{field_id}'); return false;">
            <div class="field-header">
                <span class="object-label">{name}</span>
                <div class="field-badges">
                    <span class="data-type-badge" style="background: {type_info['color']};">
                        {type_info['icon']} {data_type}
                    </span>
                    <span class="source-type-badge {'formula-badge' if is_formula else 'database-badge'}">
                        {'📝' if is_formula else '🗃️'} {source_type}
                    </span>
                </div>
            </div>
            <div class="field-content">
                {self._render_field_source_preview(source_value, is_formula)}
            </div>
            {('<span class="hidden-indicator">HIDDEN</span>' if is_hidden else '')}
            {('<span class="changed-indicator">CHANGED</span>' if is_changed else '')}
        </div>
        '''
    
    def _detect_field_data_type(self, name: str, database_field: str, formula: str) -> str:
        """Detect field data type from name and content"""
        
        name_lower = name.lower()
        field_lower = database_field.lower()
        formula_lower = formula.lower()
        
        # Date indicators
        if any(keyword in name_lower for keyword in ['date', 'time', 'created', 'modified', 'updated']):
            return 'Date'
        if any(keyword in field_lower for keyword in ['date', 'time', 'timestamp']):
            return 'Date'
        if any(keyword in formula_lower for keyword in ['date', 'now()', 'today()']):
            return 'Date'
        
        # Number indicators
        if any(keyword in name_lower for keyword in ['amount', 'total', 'sum', 'count', 'price', 'cost', 'id', 'number']):
            return 'Number'
        if any(keyword in field_lower for keyword in ['amount', 'total', 'price', 'cost', 'id', 'num']):
            return 'Number'
        if any(keyword in formula_lower for keyword in ['sum(', 'count(', 'avg(', '+', '-', '*', '/']):
            return 'Number'
        
        # Boolean indicators
        if any(keyword in name_lower for keyword in ['active', 'enabled', 'visible', 'flag']):
            return 'Boolean'
        if any(keyword in formula_lower for keyword in ['true', 'false', 'and', 'or', 'not']):
            return 'Boolean'
        
        # Default to text
        return 'Text'
    
    def _get_data_type_info(self, data_type: str) -> Dict[str, str]:
        """Get icon and color for data type"""
        
        type_mapping = {
            'Text': {'icon': '📝', 'color': '#6b7280'},
            'Number': {'icon': '🔢', 'color': '#3b82f6'},
            'Date': {'icon': '📅', 'color': '#10b981'},
            'Boolean': {'icon': '☑️', 'color': '#8b5cf6'},
            'Currency': {'icon': '💰', 'color': '#f59e0b'},
        }
        
        return type_mapping.get(data_type, {'icon': '❓', 'color': '#64748b'})
    
    def _render_field_source_preview(self, source_value: str, is_formula: bool) -> str:
        """Render enhanced source preview with syntax highlighting for formulas"""
        
        if not source_value:
            return '<div class="field-source-empty">No source defined</div>'
        
        if is_formula:
            # Enhanced: Basic syntax highlighting for formulas
            highlighted_formula = self._highlight_formula_syntax(source_value)
            return f'''
            <div class="formula-preview">
                <div class="formula-label">Formula:</div>
                <div class="formula-code">{highlighted_formula}</div>
            </div>
            '''
        else:
            return f'''
            <div class="database-field-preview">
                <div class="database-label">Database Field:</div>
                <div class="database-path">{source_value}</div>
            </div>
            '''
    
    def _highlight_formula_syntax(self, formula: str) -> str:
        """Basic syntax highlighting for Crystal Reports formulas"""
        
        # Simple highlighting - can be enhanced further
        highlighted = formula
        
        # Highlight functions
        import re
        functions = ['SUM', 'COUNT', 'AVG', 'MAX', 'MIN', 'IF', 'ELSE', 'THEN', 'AND', 'OR', 'NOT']
        for func in functions:
            pattern = rf'\b{func}\b'
            highlighted = re.sub(pattern, f'<span class="formula-function">{func}</span>', highlighted, flags=re.IGNORECASE)
        
        # Highlight strings
        highlighted = re.sub(r'"([^"]*)"', r'<span class="formula-string">"$1"</span>', highlighted)
        
        # Highlight numbers
        highlighted = re.sub(r'\b(\d+\.?\d*)\b', r'<span class="formula-number">$1</span>', highlighted)
        
        # Highlight operators
        operators = ['+', '-', '*', '/', '=', '<', '>', '<=', '>=', '<>']
        for op in operators:
            escaped_op = re.escape(op)
            highlighted = re.sub(f'({escaped_op})', r'<span class="formula-operator">$1</span>', highlighted)
        
        return highlighted

    def _render_picture_object(self, pic_obj: Dict, highlight_changes: Optional[Dict] = None) -> str:
        """Render a picture object"""
        
        name = pic_obj.get('name', 'Image')
        image_path = pic_obj.get('image_path', '')
        is_hidden = pic_obj.get('hidden', False)
        
        css_class = "picture-object"
        if is_hidden:
            css_class += " object-hidden"
        
        return f'''
        <div class="{css_class}">
            <span class="object-label">{name}:</span>
            <div class="picture-placeholder">📷 {image_path or 'Image'}</div>
            {('<span class="hidden-indicator">HIDDEN</span>' if is_hidden else '')}
        </div>
        '''

    def _generate_css_styles(self) -> str:
        """Generate enhanced CSS styles for the report visualization"""
        
        return """
        .crystal-report {
            border: 2px solid #e5e7eb;
            background: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
            position: relative;
        }
        
        .crystal-report::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        }
        
        .report-title-bar {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 16px 20px;
            border-bottom: 2px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .report-title-bar h3 {
            margin: 0;
            color: #1e293b;
            font-size: 20px;
            font-weight: 600;
        }
        
        .report-info {
            font-size: 13px;
            color: #64748b;
            background: #f1f5f9;
            padding: 4px 8px;
            border-radius: 4px;
        }
        
        .report-section {
            border-bottom: 1px solid #f1f5f9;
            min-height: 80px;
            transition: all 0.2s ease;
            position: relative;
        }
        
        .report-section:hover {
            background: #fafbfc;
            box-shadow: inset 0 0 0 1px #e2e8f0;
        }
        
        .section-header {
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            padding: 12px 20px;
            border-bottom: 1px solid #cbd5e1;
            font-weight: 600;
            font-size: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
        }
        
        .section-header::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: #3b82f6;
        }
        
        .section-name {
            color: #1e40af;
            font-weight: 600;
        }
        
        .section-content {
            padding: 16px 20px;
            min-height: 60px;
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: flex-start;
            background: 
                radial-gradient(circle at 20px 20px, #f1f5f9 1px, transparent 1px),
                radial-gradient(circle at 20px 20px, #f1f5f9 1px, transparent 1px);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
        }
        
        .text-object, .field-object, .picture-object {
            border: 2px solid #e2e8f0;
            padding: 12px 16px;
            background: white;
            border-radius: 8px;
            min-width: 140px;
            position: relative;
            transition: all 0.2s ease;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .text-object:hover, .field-object:hover, .picture-object:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            border-color: #3b82f6;
        }
        
        .field-object {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-color: #3b82f6;
        }
        
        .field-object::before {
            content: '🔢';
            position: absolute;
            top: -8px;
            left: -8px;
            background: #3b82f6;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
        }
        
        .text-object {
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
            border-color: #6b7280;
        }
        
        .text-object::before {
            content: 'T';
            position: absolute;
            top: -8px;
            left: -8px;
            background: #6b7280;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        
        .picture-object {
            background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
            border-color: #f59e0b;
        }
        
        .picture-object::before {
            content: '🖼️';
            position: absolute;
            top: -8px;
            left: -8px;
            background: #f59e0b;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
        }
        
        .object-label {
            font-weight: 600;
            font-size: 13px;
            color: #1e293b;
            display: block;
            margin-bottom: 4px;
        }
        
        .object-content {
            font-size: 14px;
            color: #475569;
            margin-top: 4px;
            display: block;
            line-height: 1.4;
        }
        
        .field-source {
            font-size: 11px;
            color: #64748b;
            font-style: italic;
            margin-top: 6px;
        }
        
        .field-details {
            font-size: 11px;
            color: #475569;
            margin-top: 6px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            background: rgba(59, 130, 246, 0.1);
            padding: 4px 6px;
            border-radius: 4px;
            border-left: 3px solid #3b82f6;
        }
        
        .picture-placeholder {
            font-size: 12px;
            color: #f59e0b;
            margin-top: 4px;
            font-weight: 500;
        }
        
        .hidden-indicator, .changed-indicator {
            position: absolute;
            top: -10px;
            right: -10px;
            background: #ef4444;
            color: white;
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .changed-indicator {
            background: #f59e0b;
            right: 20px;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
        }
        
        .object-hidden {
            opacity: 0.5;
            border-style: dashed;
            filter: grayscale(50%);
        }
        
        .section-hidden {
            opacity: 0.6;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 15px,
                rgba(239, 68, 68, 0.1) 15px,
                rgba(239, 68, 68, 0.1) 30px
            );
        }
        
        .object-changed {
            border-color: #f59e0b !important;
            background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%) !important;
            box-shadow: 0 8px 25px rgba(245, 158, 11, 0.2) !important;
            animation: highlight 1s ease-in-out;
        }
        
        @keyframes highlight {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .section-changed {
            border-left: 6px solid #f59e0b;
            background: linear-gradient(90deg, rgba(245, 158, 11, 0.1) 0%, transparent 100%);
        }
        
        .section-reportheader {
            background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
        }
        
        .section-details {
            background: white;
        }
        
        .section-reportfooter {
            background: linear-gradient(135deg, #f0fdf4 0%, #f7fee7 100%);
        }
        
        /* Enhanced tooltips */
        .text-object:hover::after,
        .field-object:hover::after,
        .picture-object:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #1e293b;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            white-space: nowrap;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        /* Loading states */
        .loading-skeleton {
            background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        /* Phase 2: Enhanced Field Object Styles */
        .field-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }
        
        .field-badges {
            display: flex;
            flex-direction: column;
            gap: 4px;
            align-items: flex-end;
        }
        
        .data-type-badge {
            font-size: 10px;
            color: white;
            padding: 2px 6px;
            border-radius: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 2px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .source-type-badge {
            font-size: 9px;
            padding: 2px 5px;
            border-radius: 8px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 2px;
        }
        
        .formula-badge {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #f59e0b;
        }
        
        .database-badge {
            background: #dbeafe;
            color: #1e40af;
            border: 1px solid #3b82f6;
        }
        
        .field-content {
            margin-top: 8px;
        }
        
        .field-source-empty {
            font-size: 11px;
            color: #9ca3af;
            font-style: italic;
            padding: 4px 0;
        }
        
        /* Formula Preview Styles */
        .formula-preview {
            background: #fefce8;
            border: 1px solid #fde047;
            border-radius: 6px;
            padding: 8px;
            margin-top: 4px;
        }
        
        .formula-label {
            font-size: 10px;
            color: #a16207;
            font-weight: 600;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .formula-code {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 11px;
            line-height: 1.4;
            color: #1f2937;
            background: white;
            padding: 6px 8px;
            border-radius: 4px;
            border: 1px solid #fbbf24;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        
        /* Formula Syntax Highlighting */
        .formula-function {
            color: #7c3aed;
            font-weight: 600;
        }
        
        .formula-string {
            color: #059669;
        }
        
        .formula-number {
            color: #dc2626;
            font-weight: 500;
        }
        
        .formula-operator {
            color: #ea580c;
            font-weight: 600;
        }
        
        /* Database Field Preview Styles */
        .database-field-preview {
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 6px;
            padding: 8px;
            margin-top: 4px;
        }
        
        .database-label {
            font-size: 10px;
            color: #1e40af;
            font-weight: 600;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .database-path {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 11px;
            color: #1f2937;
            background: white;
            padding: 6px 8px;
            border-radius: 4px;
            border: 1px solid #60a5fa;
            overflow-x: auto;
        }
        
        /* Data Type Specific Field Styling */
        .field-type-text {
            border-left: 4px solid #6b7280;
        }
        
        .field-type-number {
            border-left: 4px solid #3b82f6;
        }
        
        .field-type-date {
            border-left: 4px solid #10b981;
        }
        
        .field-type-boolean {
            border-left: 4px solid #8b5cf6;
        }
        
        .field-type-currency {
            border-left: 4px solid #f59e0b;
        }
        
        /* Context Menu Styles */
        .context-menu {
            position: absolute;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            padding: 4px 0;
            min-width: 180px;
            z-index: 1000;
            display: none;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .context-menu-item {
            padding: 8px 16px;
            cursor: pointer;
            font-size: 13px;
            color: #374151;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background-color 0.15s ease;
        }
        
        .context-menu-item:hover {
            background: #f3f4f6;
            color: #1f2937;
        }
        
        .context-menu-item.dangerous:hover {
            background: #fef2f2;
            color: #dc2626;
        }
        
        .context-menu-separator {
            height: 1px;
            background: #e5e7eb;
            margin: 4px 0;
        }
        
        .context-menu-icon {
            width: 16px;
            text-align: center;
        }
        
        /* Field object context highlight */
        .field-object.context-active {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            transform: translateY(-1px);
        }
        
        /* Text object context highlight */
        .text-object.context-active {
            border-color: #6b7280;
            box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.1);
            transform: translateY(-1px);
        }
        
        /* Overlay for context menu */
        .context-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 999;
            display: none;
        }
        </style>
        
        <script>
        let currentContextMenu = null;
        let currentActiveField = null;
        
        function showContextMenu(event, fieldId) {
            event.preventDefault();
            event.stopPropagation();
            
            // Hide any existing context menu
            hideContextMenu();
            
            const field = document.getElementById(fieldId);
            if (!field) return;
            
            // Get field data
            const fieldName = field.dataset.fieldName;
            const fieldType = field.dataset.fieldType;
            const sourceType = field.dataset.sourceType;
            
            // Create context menu
            const contextMenu = document.createElement('div');
            contextMenu.className = 'context-menu';
            contextMenu.innerHTML = `
                <div class="context-menu-item" onclick="copyFieldName('${fieldName}')">
                    <span class="context-menu-icon">📋</span>
                    Copy Field Name
                </div>
                <div class="context-menu-item" onclick="inspectField('${fieldId}')">
                    <span class="context-menu-icon">🔍</span>
                    Inspect Field
                </div>
                <div class="context-menu-separator"></div>
                <div class="context-menu-item" onclick="hideField('${fieldId}')">
                    <span class="context-menu-icon">👁️</span>
                    Hide Field
                </div>
                <div class="context-menu-item" onclick="duplicateField('${fieldId}')">
                    <span class="context-menu-icon">📄</span>
                    Duplicate Field
                </div>
                <div class="context-menu-separator"></div>
                <div class="context-menu-item" onclick="moveFieldUp('${fieldId}')">
                    <span class="context-menu-icon">⬆️</span>
                    Move Up
                </div>
                <div class="context-menu-item" onclick="moveFieldDown('${fieldId}')">
                    <span class="context-menu-icon">⬇️</span>
                    Move Down
                </div>
                <div class="context-menu-separator"></div>
                <div class="context-menu-item dangerous" onclick="deleteField('${fieldId}')">
                    <span class="context-menu-icon">🗑️</span>
                    Delete Field
                </div>
            `;
            
            // Create overlay
            const overlay = document.createElement('div');
            overlay.className = 'context-overlay';
            overlay.onclick = hideContextMenu;
            
            // Position context menu
            document.body.appendChild(overlay);
            document.body.appendChild(contextMenu);
            
            const rect = field.getBoundingClientRect();
            const menuRect = contextMenu.getBoundingClientRect();
            
            let left = event.clientX;
            let top = event.clientY;
            
            // Adjust position if menu would go off screen
            if (left + menuRect.width > window.innerWidth) {
                left = window.innerWidth - menuRect.width - 10;
            }
            if (top + menuRect.height > window.innerHeight) {
                top = window.innerHeight - menuRect.height - 10;
            }
            
            contextMenu.style.left = left + 'px';
            contextMenu.style.top = top + 'px';
            contextMenu.style.display = 'block';
            overlay.style.display = 'block';
            
            // Highlight the field
            field.classList.add('context-active');
            
            currentContextMenu = contextMenu;
            currentActiveField = field;
        }
        
        function hideContextMenu() {
            if (currentContextMenu) {
                currentContextMenu.remove();
                currentContextMenu = null;
            }
            
            if (currentActiveField) {
                currentActiveField.classList.remove('context-active');
                currentActiveField = null;
            }
            
            const overlay = document.querySelector('.context-overlay');
            if (overlay) {
                overlay.remove();
            }
        }
        
        // Context menu actions
        function copyFieldName(fieldName) {
            navigator.clipboard.writeText(fieldName).then(() => {
                showNotification('Field name copied to clipboard', 'success');
            });
            hideContextMenu();
        }
        
        function inspectField(fieldId) {
            const field = document.getElementById(fieldId);
            if (field) {
                showNotification(`Inspecting field: ${field.dataset.fieldName}`, 'info');
                // Could trigger a detailed inspection modal here
            }
            hideContextMenu();
        }
        
        function hideField(fieldId) {
            const field = document.getElementById(fieldId);
            if (field) {
                field.style.opacity = '0.3';
                field.style.filter = 'grayscale(100%)';
                showNotification('Field hidden (visual only)', 'warning');
            }
            hideContextMenu();
        }
        
        function duplicateField(fieldId) {
            showNotification('Duplicate field functionality would be implemented here', 'info');
            hideContextMenu();
        }
        
        function moveFieldUp(fieldId) {
            const field = document.getElementById(fieldId);
            if (field && field.previousElementSibling) {
                field.parentNode.insertBefore(field, field.previousElementSibling);
                showNotification('Field moved up (visual only)', 'success');
            }
            hideContextMenu();
        }
        
        function moveFieldDown(fieldId) {
            const field = document.getElementById(fieldId);
            if (field && field.nextElementSibling) {
                field.parentNode.insertBefore(field.nextElementSibling, field);
                showNotification('Field moved down (visual only)', 'success');
            }
            hideContextMenu();
        }
        
        function deleteField(fieldId) {
            if (confirm('Are you sure you want to delete this field?')) {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.style.transition = 'all 0.3s ease';
                    field.style.transform = 'scale(0)';
                    field.style.opacity = '0';
                    setTimeout(() => {
                        field.remove();
                        showNotification('Field deleted (visual only)', 'warning');
                    }, 300);
                }
            }
            hideContextMenu();
        }
        
        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 16px;
                border-radius: 6px;
                color: white;
                font-weight: 500;
                z-index: 1001;
                transition: all 0.3s ease;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            `;
            
            const colors = {
                success: '#10b981',
                warning: '#f59e0b', 
                error: '#ef4444',
                info: '#3b82f6'
            };
            
            notification.style.background = colors[type] || colors.info;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
        
        // Hide context menu when clicking elsewhere
        document.addEventListener('click', hideContextMenu);
        document.addEventListener('contextmenu', function(e) {
            // Only prevent default for field and text objects
            if (!e.target.closest('.field-object') && !e.target.closest('.text-object')) {
                hideContextMenu();
            }
        });
        
        // Text object context menu
        function showTextContextMenu(event, textId) {
            event.preventDefault();
            event.stopPropagation();
            
            // Hide any existing context menu
            hideContextMenu();
            
            const textObj = document.getElementById(textId);
            if (!textObj) return;
            
            // Get text object data
            const objectName = textObj.dataset.objectName;
            
            // Create context menu
            const contextMenu = document.createElement('div');
            contextMenu.className = 'context-menu';
            contextMenu.innerHTML = `
                <div class="context-menu-item" onclick="copyObjectName('${objectName}')">
                    <span class="context-menu-icon">📋</span>
                    Copy Object Name
                </div>
                <div class="context-menu-item" onclick="inspectObject('${textId}')">
                    <span class="context-menu-icon">🔍</span>
                    Inspect Object
                </div>
                <div class="context-menu-separator"></div>
                <div class="context-menu-item" onclick="hideObject('${textId}')">
                    <span class="context-menu-icon">👁️</span>
                    Hide Object
                </div>
                <div class="context-menu-item" onclick="duplicateObject('${textId}')">
                    <span class="context-menu-icon">📄</span>
                    Duplicate Object
                </div>
                <div class="context-menu-separator"></div>
                <div class="context-menu-item" onclick="moveObjectUp('${textId}')">
                    <span class="context-menu-icon">⬆️</span>
                    Move Up
                </div>
                <div class="context-menu-item" onclick="moveObjectDown('${textId}')">
                    <span class="context-menu-icon">⬇️</span>
                    Move Down
                </div>
                <div class="context-menu-separator"></div>
                <div class="context-menu-item dangerous" onclick="deleteObject('${textId}')">
                    <span class="context-menu-icon">🗑️</span>
                    Delete Object
                </div>
            `;
            
            // Create overlay
            const overlay = document.createElement('div');
            overlay.className = 'context-overlay';
            overlay.onclick = hideContextMenu;
            
            // Position context menu
            document.body.appendChild(overlay);
            document.body.appendChild(contextMenu);
            
            const rect = textObj.getBoundingClientRect();
            const menuRect = contextMenu.getBoundingClientRect();
            
            let left = event.clientX;
            let top = event.clientY;
            
            // Adjust position if menu would go off screen
            if (left + menuRect.width > window.innerWidth) {
                left = window.innerWidth - menuRect.width - 10;
            }
            if (top + menuRect.height > window.innerHeight) {
                top = window.innerHeight - menuRect.height - 10;
            }
            
            contextMenu.style.left = left + 'px';
            contextMenu.style.top = top + 'px';
            contextMenu.style.display = 'block';
            overlay.style.display = 'block';
            
            // Highlight the object
            textObj.classList.add('context-active');
            
            currentContextMenu = contextMenu;
            currentActiveField = textObj;
        }
        
        // Text object context menu actions
        function copyObjectName(objectName) {
            navigator.clipboard.writeText(objectName).then(() => {
                showNotification('Object name copied to clipboard', 'success');
            });
            hideContextMenu();
        }
        
        function inspectObject(objectId) {
            const obj = document.getElementById(objectId);
            if (obj) {
                showNotification(`Inspecting object: ${obj.dataset.objectName}`, 'info');
            }
            hideContextMenu();
        }
        
        function hideObject(objectId) {
            const obj = document.getElementById(objectId);
            if (obj) {
                obj.style.opacity = '0.3';
                obj.style.filter = 'grayscale(100%)';
                showNotification('Object hidden (visual only)', 'warning');
            }
            hideContextMenu();
        }
        
        function duplicateObject(objectId) {
            showNotification('Duplicate object functionality would be implemented here', 'info');
            hideContextMenu();
        }
        
        function moveObjectUp(objectId) {
            const obj = document.getElementById(objectId);
            if (obj && obj.previousElementSibling) {
                obj.parentNode.insertBefore(obj, obj.previousElementSibling);
                showNotification('Object moved up (visual only)', 'success');
            }
            hideContextMenu();
        }
        
        function moveObjectDown(objectId) {
            const obj = document.getElementById(objectId);
            if (obj && obj.nextElementSibling) {
                obj.parentNode.insertBefore(obj.nextElementSibling, obj);
                showNotification('Object moved down (visual only)', 'success');
            }
            hideContextMenu();
        }
        
        function deleteObject(objectId) {
            if (confirm('Are you sure you want to delete this object?')) {
                const obj = document.getElementById(objectId);
                if (obj) {
                    obj.style.transition = 'all 0.3s ease';
                    obj.style.transform = 'scale(0)';
                    obj.style.opacity = '0';
                    setTimeout(() => {
                        obj.remove();
                        showNotification('Object deleted (visual only)', 'warning');
                    }, 300);
                }
            }
            hideContextMenu();
        }
        </script>
        """

    def create_comparison_html(self, original_metadata: Dict, modified_metadata: Dict, changes: Dict) -> str:
        """Create side-by-side comparison of original vs modified report"""
        
        original_html = self.render_report_html(original_metadata)
        modified_html = self.render_report_html(modified_metadata, changes)
        
        comparison_html = f"""
        <style>
        .report-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        
        .comparison-column {{
            border: 2px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .comparison-header {{
            background: #1976d2;
            color: white;
            padding: 12px 16px;
            font-weight: bold;
            text-align: center;
        }}
        
        .original-header {{
            background: #666;
        }}
        
        .modified-header {{
            background: #ff9800;
        }}
        
        .comparison-content {{
            height: 600px;
            overflow-y: auto;
        }}
        
        .changes-summary {{
            background: #fff3e0;
            border: 1px solid #ff9800;
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 20px;
        }}
        
        .changes-summary h4 {{
            margin: 0 0 8px 0;
            color: #e65100;
        }}
        
        .changes-list {{
            list-style-type: none;
            padding: 0;
            margin: 0;
        }}
        
        .changes-list li {{
            padding: 4px 0;
            color: #e65100;
        }}
        
        .changes-list li:before {{
            content: "→ ";
            font-weight: bold;
        }}
        </style>
        
        <div class="changes-summary">
            <h4>Preview Changes</h4>
            <ul class="changes-list">
                {(''.join([f'<li>{change}</li>' for change in changes.get("changes", [])]))}
            </ul>
            <p><strong>{changes.get("summary", "No changes detected")}</strong></p>
        </div>
        
        <div class="report-comparison">
            <div class="comparison-column">
                <div class="comparison-header original-header">Original Report</div>
                <div class="comparison-content">{original_html}</div>
            </div>
            <div class="comparison-column">
                <div class="comparison-header modified-header">Modified Report</div>
                <div class="comparison-content">{modified_html}</div>
            </div>
        </div>
        """
        
        return comparison_html 