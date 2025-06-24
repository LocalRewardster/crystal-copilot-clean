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
        """Render a text object"""
        
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
        
        return f'''
        <div class="{css_class}" {style_str}>
            <span class="object-label">{name}:</span>
            <span class="object-content">{text}</span>
            {('<span class="hidden-indicator">HIDDEN</span>' if is_hidden else '')}
            {('<span class="changed-indicator">CHANGED</span>' if is_changed else '')}
        </div>
        '''

    def _render_field_object(self, field_obj: Dict, highlight_changes: Optional[Dict] = None) -> str:
        """Render a field object"""
        
        name = field_obj.get('name', 'Field')
        database_field = field_obj.get('database_field', '')
        formula = field_obj.get('formula', '')
        is_hidden = field_obj.get('hidden', False)
        formatting = field_obj.get('formatting', {})
        
        # Check for changes
        is_changed = False
        if highlight_changes:
            changes = highlight_changes.get('changes', [])
            for change in changes:
                if name.lower() in change.lower():
                    is_changed = True
                    break
        
        css_class = "field-object"
        if is_hidden:
            css_class += " object-hidden"
        if is_changed:
            css_class += " object-changed"
        
        # Determine source type
        source_type = "Formula" if formula else "Database"
        source_value = formula if formula else database_field
        
        # Apply formatting styles
        style_attrs = []
        if formatting.get('bold'):
            style_attrs.append('font-weight: bold')
        if formatting.get('italic'):
            style_attrs.append('font-style: italic')
        if formatting.get('font_size'):
            style_attrs.append(f'font-size: {formatting["font_size"]}')
        
        style_str = f'style="{"; ".join(style_attrs)}"' if style_attrs else ''
        
        return f'''
        <div class="{css_class}" {style_str}>
            <span class="object-label">{name}</span>
            <span class="field-source">({source_type})</span>
            <div class="field-details">{source_value}</div>
            {('<span class="hidden-indicator">HIDDEN</span>' if is_hidden else '')}
            {('<span class="changed-indicator">CHANGED</span>' if is_changed else '')}
        </div>
        '''

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
        """Generate CSS styles for the report visualization"""
        
        return """
        .crystal-report {
            border: 2px solid #ddd;
            background: white;
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .report-title-bar {
            background: #f8f9fa;
            padding: 12px 16px;
            border-bottom: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .report-title-bar h3 {
            margin: 0;
            color: #333;
            font-size: 18px;
        }
        
        .report-info {
            font-size: 12px;
            color: #666;
        }
        
        .report-section {
            border-bottom: 1px solid #eee;
            min-height: 60px;
        }
        
        .section-header {
            background: #f1f3f4;
            padding: 8px 16px;
            border-bottom: 1px solid #e0e0e0;
            font-weight: bold;
            font-size: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .section-name {
            color: #1976d2;
        }
        
        .section-content {
            padding: 12px 16px;
            min-height: 40px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: flex-start;
        }
        
        .text-object, .field-object, .picture-object {
            border: 1px solid #e0e0e0;
            padding: 8px 12px;
            background: #fafafa;
            border-radius: 4px;
            min-width: 120px;
            position: relative;
        }
        
        .field-object {
            background: #f0f8ff;
            border-color: #1976d2;
        }
        
        .text-object {
            background: #f9f9f9;
            border-color: #666;
        }
        
        .picture-object {
            background: #fff9e6;
            border-color: #ff9800;
        }
        
        .object-label {
            font-weight: bold;
            font-size: 12px;
            color: #333;
            display: block;
        }
        
        .object-content {
            font-size: 14px;
            color: #555;
            margin-top: 4px;
            display: block;
        }
        
        .field-source {
            font-size: 10px;
            color: #666;
            font-style: italic;
        }
        
        .field-details {
            font-size: 11px;
            color: #777;
            margin-top: 4px;
            font-family: monospace;
            background: rgba(0,0,0,0.05);
            padding: 2px 4px;
            border-radius: 2px;
        }
        
        .picture-placeholder {
            font-size: 12px;
            color: #ff9800;
            margin-top: 4px;
        }
        
        .hidden-indicator, .changed-indicator {
            position: absolute;
            top: -8px;
            right: -8px;
            background: #f44336;
            color: white;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
            font-weight: bold;
        }
        
        .changed-indicator {
            background: #ff9800;
            right: 25px;
        }
        
        .object-hidden {
            opacity: 0.4;
            border-style: dashed;
        }
        
        .section-hidden {
            opacity: 0.5;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 10px,
                rgba(255,0,0,.1) 10px,
                rgba(255,0,0,.1) 20px
            );
        }
        
        .object-changed {
            border-color: #ff9800 !important;
            background: #fff3e0 !important;
            box-shadow: 0 0 8px rgba(255, 152, 0, 0.3);
        }
        
        .section-changed {
            border-left: 4px solid #ff9800;
        }
        
        .section-reportheader {
            background: linear-gradient(to bottom, #e3f2fd, #f5f5f5);
        }
        
        .section-details {
            background: white;
        }
        
        .section-reportfooter {
            background: linear-gradient(to top, #e8f5e8, #f5f5f5);
        }
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