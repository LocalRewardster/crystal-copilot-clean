"""
Crystal Reports Edit Service - Week 3 Implementation
Handles natural language editing commands for Crystal Reports
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from openai import AsyncOpenAI
from pydantic import BaseModel

class EditType(Enum):
    """Types of edits that can be performed"""
    RENAME_FIELD = "rename_field"
    HIDE_FIELD = "hide_field"
    SHOW_FIELD = "show_field"
    MOVE_FIELD = "move_field"
    CHANGE_TEXT = "change_text"
    HIDE_SECTION = "hide_section"
    SHOW_SECTION = "show_section"
    FORMAT_FIELD = "format_field"

@dataclass
class EditCommand:
    """Structured representation of an edit command"""
    edit_type: EditType
    target: str  # What to edit (field name, section name, etc.)
    new_value: Optional[str] = None  # New value for renames/text changes
    target_section: Optional[str] = None  # For moves
    parameters: Optional[Dict] = None  # Additional parameters

class EditRequest(BaseModel):
    """Request model for edit operations"""
    report_id: str
    command: str  # Natural language command

class EditResponse(BaseModel):
    """Response model for edit operations"""
    success: bool
    message: str
    edit_command: Optional[Dict] = None
    preview: Optional[Dict] = None
    modified_metadata: Optional[Dict] = None

class ReportEditService:
    """Service for editing Crystal Reports using natural language commands"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            self.client = None
        
        # Store for tracking edit history
        self.edit_history: Dict[str, List[EditCommand]] = {}

    async def parse_edit_command(self, command: str, report_metadata: Dict) -> EditCommand:
        """
        Parse natural language edit command into structured EditCommand
        
        Uses GPT-4o to understand user intentions and map to available operations
        """
        
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        # Create context about available fields and sections
        context = self._create_editing_context(report_metadata)
        
        # Create prompt for GPT-4o to parse the command
        prompt = self._create_command_parsing_prompt(context, command)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Crystal Reports editing expert. Parse natural language editing commands into structured operations. Return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Get the response content
            response_content = response.choices[0].message.content.strip()
            
            # Debug logging
            print(f"DEBUG: GPT-4o response: '{response_content}'")
            
            if not response_content:
                raise ValueError("Empty response from GPT-4o")
            
            # Try to parse the JSON response
            try:
                result = json.loads(response_content)
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON decode error: {e}")
                print(f"DEBUG: Response content: '{response_content}'")
                
                # Try to extract JSON from the response if it's wrapped in text
                if "{" in response_content and "}" in response_content:
                    start = response_content.find("{")
                    end = response_content.rfind("}") + 1
                    json_part = response_content[start:end]
                    try:
                        result = json.loads(json_part)
                        print(f"DEBUG: Successfully extracted JSON: {result}")
                    except json.JSONDecodeError:
                        # Fall back to rule-based parsing
                        result = self._fallback_parse_command(command, report_metadata)
                else:
                    # Fall back to rule-based parsing
                    result = self._fallback_parse_command(command, report_metadata)
            
            # Validate required fields
            if "edit_type" not in result or "target" not in result:
                raise ValueError(f"Invalid response format: missing required fields in {result}")
            
            # Convert to EditCommand object
            edit_command = EditCommand(
                edit_type=EditType(result["edit_type"]),
                target=result["target"],
                new_value=result.get("new_value"),
                target_section=result.get("target_section"),
                parameters=result.get("parameters")
            )
            
            return edit_command
            
        except Exception as e:
            print(f"DEBUG: Exception in parse_edit_command: {e}")
            # Try fallback parsing as last resort
            try:
                fallback_result = self._fallback_parse_command(command, report_metadata)
                return EditCommand(
                    edit_type=EditType(fallback_result["edit_type"]),
                    target=fallback_result["target"],
                    new_value=fallback_result.get("new_value"),
                    target_section=fallback_result.get("target_section"),
                    parameters=fallback_result.get("parameters")
                )
            except Exception as fallback_error:
                raise ValueError(f"Failed to parse edit command: {str(e)}. Fallback also failed: {str(fallback_error)}")

    def _fallback_parse_command(self, command: str, report_metadata: Dict) -> Dict:
        """
        Fallback rule-based parsing when GPT-4o fails
        """
        command_lower = command.lower()
        
        # Get available fields and sections
        available_fields = list(report_metadata.get('field_lineage', {}).keys())
        available_sections = [s.get('name', '') for s in report_metadata.get('sections', [])]
        
        # Available text objects
        available_text_objects = []
        for section in report_metadata.get('sections', []):
            for text_obj in section.get('text_objects', []):
                available_text_objects.append(text_obj.get('name', ''))
        
        # Rule-based parsing
        if "rename" in command_lower:
            # Extract old and new names
            import re
            
            # Pattern: rename 'old' to 'new' or rename "old" to "new"
            patterns = [
                r"rename\s+['\"]([^'\"]+)['\"][\s\w]*to\s+['\"]([^'\"]+)['\"]",
                r"rename\s+([^\s]+)[\s\w]*to\s+([^\s]+)",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, command_lower)
                if match:
                    old_name = match.group(1)
                    new_name = match.group(2)
                    
                    # Find the actual field name (case-insensitive)
                    target = None
                    for field in available_fields + available_text_objects:
                        if field.lower() == old_name.lower():
                            target = field
                            break
                    
                    if target:
                        return {
                            "edit_type": "rename_field",
                            "target": target,
                            "new_value": new_name.title()
                        }
            
            # If no pattern matched, try to find any quoted strings
            quoted_strings = re.findall(r"['\"]([^'\"]+)['\"]", command)
            if len(quoted_strings) >= 2:
                old_name = quoted_strings[0]
                new_name = quoted_strings[1]
                
                # Find the actual field name
                target = None
                for field in available_fields + available_text_objects:
                    if field.lower() == old_name.lower():
                        target = field
                        break
                
                if target:
                    return {
                        "edit_type": "rename_field",
                        "target": target,
                        "new_value": new_name
                    }
        
        elif "hide" in command_lower:
            # Extract field name to hide
            quoted_match = re.search(r"hide.*['\"]([^'\"]+)['\"]", command_lower)
            if quoted_match:
                field_name = quoted_match.group(1)
                
                # Find the actual field name
                target = None
                for field in available_fields:
                    if field.lower() == field_name.lower():
                        target = field
                        break
                
                if target:
                    return {
                        "edit_type": "hide_field",
                        "target": target
                    }
        
        elif "show" in command_lower:
            # Extract field name to show
            quoted_match = re.search(r"show.*['\"]([^'\"]+)['\"]", command_lower)
            if quoted_match:
                field_name = quoted_match.group(1)
                
                # Find the actual field name
                target = None
                for field in available_fields:
                    if field.lower() == field_name.lower():
                        target = field
                        break
                
                if target:
                    return {
                        "edit_type": "show_field",
                        "target": target
                    }
        
        elif "move" in command_lower:
            # Extract field and target section
            field_match = re.search(r"move.*['\"]([^'\"]+)['\"]", command_lower)
            section_match = re.search(r"to.*['\"]?([^'\"]+)['\"]?\s*section", command_lower)
            
            if field_match:
                field_name = field_match.group(1)
                target_section = None
                
                if section_match:
                    section_name = section_match.group(1).strip()
                    # Find the actual section name
                    for section in available_sections:
                        if section.lower() == section_name.lower():
                            target_section = section
                            break
                
                # Find the actual field name
                target = None
                for field in available_fields:
                    if field.lower() == field_name.lower():
                        target = field
                        break
                
                if target and target_section:
                    return {
                        "edit_type": "move_field",
                        "target": target,
                        "target_section": target_section
                    }
        
        elif "change" in command_lower and "title" in command_lower:
            # Extract new title
            to_match = re.search(r"to\s+['\"]([^'\"]+)['\"]", command)
            if to_match:
                new_title = to_match.group(1)
                return {
                    "edit_type": "change_text",
                    "target": "Title",
                    "new_value": new_title
                }
        
        # Default fallback if nothing matches
        raise ValueError(f"Could not parse command: '{command}'. Please try rephrasing your request.")

    def _create_editing_context(self, metadata: Dict) -> str:
        """Create context about available fields and sections for editing"""
        
        context_parts = []
        
        # Available sections
        sections = metadata.get('sections', [])
        if sections:
            context_parts.append("AVAILABLE SECTIONS:")
            for section in sections:
                section_name = section.get('name', 'Unknown')
                context_parts.append(f"- {section_name}")
        
        # Available fields
        field_lineage = metadata.get('field_lineage', {})
        if field_lineage:
            context_parts.append("\nAVAILABLE FIELDS:")
            for field_name, lineage in field_lineage.items():
                section = lineage.get('section', 'Unknown')
                context_parts.append(f"- {field_name} (in {section} section)")
        
        # Available text objects
        context_parts.append("\nAVAILABLE TEXT OBJECTS:")
        for section in sections:
            text_objects = section.get('text_objects', [])
            for obj in text_objects:
                obj_name = obj.get('name', 'Unknown')
                text_content = obj.get('text', '')
                context_parts.append(f"- {obj_name}: \"{text_content}\"")
        
        return "\n".join(context_parts)

    def _create_command_parsing_prompt(self, context: str, command: str) -> str:
        """Create prompt for GPT-4o to parse the editing command"""
        
        return f"""Based on the Crystal Report structure below, parse the natural language editing command into a structured JSON operation.

REPORT STRUCTURE:
{context}

AVAILABLE EDIT TYPES:
- rename_field: Rename a field or text object
- hide_field: Hide a field from display
- show_field: Show a previously hidden field
- move_field: Move a field to a different section
- change_text: Change the text content of a text object
- hide_section: Hide an entire section
- show_section: Show a previously hidden section
- format_field: Change formatting (bold, italic, font size, etc.)

USER COMMAND: "{command}"

Return a JSON object with these fields:
{{
    "edit_type": "one_of_the_types_above",
    "target": "name_of_field_or_section_to_edit",
    "new_value": "new_value_if_applicable",
    "target_section": "destination_section_if_moving",
    "parameters": {{"any": "additional_formatting_parameters"}}
}}

Only return the JSON object, no other text."""

    async def apply_edit(self, report_id: str, edit_command: EditCommand, metadata: Dict) -> Dict:
        """Apply the parsed edit command to the report metadata"""
        
        # Create a deep copy of metadata to modify
        modified_metadata = json.loads(json.dumps(metadata))
        
        try:
            if edit_command.edit_type == EditType.RENAME_FIELD:
                modified_metadata = self._rename_field(modified_metadata, edit_command)
            elif edit_command.edit_type == EditType.HIDE_FIELD:
                modified_metadata = self._hide_field(modified_metadata, edit_command)
            elif edit_command.edit_type == EditType.SHOW_FIELD:
                modified_metadata = self._show_field(modified_metadata, edit_command)
            elif edit_command.edit_type == EditType.MOVE_FIELD:
                modified_metadata = self._move_field(modified_metadata, edit_command)
            elif edit_command.edit_type == EditType.CHANGE_TEXT:
                modified_metadata = self._change_text(modified_metadata, edit_command)
            elif edit_command.edit_type == EditType.HIDE_SECTION:
                modified_metadata = self._hide_section(modified_metadata, edit_command)
            elif edit_command.edit_type == EditType.SHOW_SECTION:
                modified_metadata = self._show_section(modified_metadata, edit_command)
            elif edit_command.edit_type == EditType.FORMAT_FIELD:
                modified_metadata = self._format_field(modified_metadata, edit_command)
            else:
                raise ValueError(f"Unsupported edit type: {edit_command.edit_type}")
            
            # Store edit in history
            if report_id not in self.edit_history:
                self.edit_history[report_id] = []
            self.edit_history[report_id].append(edit_command)
            
            return modified_metadata
            
        except Exception as e:
            raise ValueError(f"Failed to apply edit: {str(e)}")

    def _rename_field(self, metadata: Dict, edit_command: EditCommand) -> Dict:
        """Rename a field or text object"""
        
        # Update field lineage
        field_lineage = metadata.get('field_lineage', {})
        if edit_command.target in field_lineage:
            # Rename in field lineage
            field_data = field_lineage.pop(edit_command.target)
            field_lineage[edit_command.new_value] = field_data
        
        # Update in sections
        sections = metadata.get('sections', [])
        for section in sections:
            # Update field objects
            field_objects = section.get('field_objects', [])
            for field_obj in field_objects:
                if field_obj.get('name') == edit_command.target:
                    field_obj['name'] = edit_command.new_value
            
            # Update text objects
            text_objects = section.get('text_objects', [])
            for text_obj in text_objects:
                if text_obj.get('name') == edit_command.target:
                    text_obj['name'] = edit_command.new_value
        
        return metadata

    def _hide_field(self, metadata: Dict, edit_command: EditCommand) -> Dict:
        """Hide a field by marking it as hidden"""
        
        # Add hidden flag to field lineage
        field_lineage = metadata.get('field_lineage', {})
        if edit_command.target in field_lineage:
            field_lineage[edit_command.target]['hidden'] = True
        
        # Mark as hidden in sections
        sections = metadata.get('sections', [])
        for section in sections:
            field_objects = section.get('field_objects', [])
            for field_obj in field_objects:
                if field_obj.get('name') == edit_command.target:
                    field_obj['hidden'] = True
        
        return metadata

    def _show_field(self, metadata: Dict, edit_command: EditCommand) -> Dict:
        """Show a previously hidden field"""
        
        # Remove hidden flag from field lineage
        field_lineage = metadata.get('field_lineage', {})
        if edit_command.target in field_lineage:
            field_lineage[edit_command.target].pop('hidden', None)
        
        # Remove hidden flag in sections
        sections = metadata.get('sections', [])
        for section in sections:
            field_objects = section.get('field_objects', [])
            for field_obj in field_objects:
                if field_obj.get('name') == edit_command.target:
                    field_obj.pop('hidden', None)
        
        return metadata

    def _move_field(self, metadata: Dict, edit_command: EditCommand) -> Dict:
        """Move a field to different section"""
        
        if not edit_command.target_section:
            raise ValueError("Target section required for move operation")
        
        # Find and remove field from current section
        field_to_move = None
        sections = metadata.get('sections', [])
        
        for section in sections:
            field_objects = section.get('field_objects', [])
            for i, field_obj in enumerate(field_objects):
                if field_obj.get('name') == edit_command.target:
                    field_to_move = field_objects.pop(i)
                    break
            if field_to_move:
                break
        
        if not field_to_move:
            raise ValueError(f"Field '{edit_command.target}' not found")
        
        # Add to target section
        for section in sections:
            if section.get('name') == edit_command.target_section:
                if 'field_objects' not in section:
                    section['field_objects'] = []
                section['field_objects'].append(field_to_move)
                break
        else:
            raise ValueError(f"Target section '{edit_command.target_section}' not found")
        
        # Update field lineage
        field_lineage = metadata.get('field_lineage', {})
        if edit_command.target in field_lineage:
            field_lineage[edit_command.target]['section'] = edit_command.target_section
        
        return metadata

    def _change_text(self, metadata: Dict, edit_command: EditCommand) -> Dict:
        """Change text content of a text object"""
        
        sections = metadata.get('sections', [])
        for section in sections:
            text_objects = section.get('text_objects', [])
            for text_obj in text_objects:
                if text_obj.get('name') == edit_command.target:
                    text_obj['text'] = edit_command.new_value
                    break
        
        return metadata

    def _hide_section(self, metadata: Dict, edit_command: EditCommand) -> Dict:
        """Hide an entire section"""
        
        sections = metadata.get('sections', [])
        for section in sections:
            if section.get('name') == edit_command.target:
                section['hidden'] = True
                break
        
        return metadata

    def _show_section(self, metadata: Dict, edit_command: EditCommand) -> Dict:
        """Show a previously hidden section"""
        
        sections = metadata.get('sections', [])
        for section in sections:
            if section.get('name') == edit_command.target:
                section.pop('hidden', None)
                break
        
        return metadata

    def _format_field(self, metadata: Dict, edit_command: EditCommand) -> Dict:
        """Apply formatting to a field"""
        
        sections = metadata.get('sections', [])
        for section in sections:
            field_objects = section.get('field_objects', [])
            for field_obj in field_objects:
                if field_obj.get('name') == edit_command.target:
                    if 'formatting' not in field_obj:
                        field_obj['formatting'] = {}
                    field_obj['formatting'].update(edit_command.parameters or {})
                    break
            
            # Also check text objects
            text_objects = section.get('text_objects', [])
            for text_obj in text_objects:
                if text_obj.get('name') == edit_command.target:
                    if 'formatting' not in text_obj:
                        text_obj['formatting'] = {}
                    text_obj['formatting'].update(edit_command.parameters or {})
                    break
        
        return metadata

    def get_edit_history(self, report_id: str) -> List[Dict]:
        """Get edit history for a report"""
        
        history = self.edit_history.get(report_id, [])
        return [
            {
                "edit_type": cmd.edit_type.value,
                "target": cmd.target,
                "new_value": cmd.new_value,
                "target_section": cmd.target_section,
                "parameters": cmd.parameters
            }
            for cmd in history
        ]

    def create_edit_preview(self, original_metadata: Dict, modified_metadata: Dict) -> Dict:
        """Create a preview showing what will change - works with actual report structure"""
        
        preview = {
            "changes": [],
            "summary": ""
        }
        
        # Helper function to find all objects in sections
        def get_all_objects_from_sections(metadata):
            objects = {}
            sections = metadata.get('sections', [])
            for section in sections:
                section_name = section.get('name', 'Unknown Section')
                
                # Field objects
                for field_obj in section.get('field_objects', []):
                    obj_name = field_obj.get('name', '')
                    if obj_name:
                        objects[obj_name] = {
                            'type': 'field',
                            'section': section_name,
                            'data': field_obj,
                            'section_index': sections.index(section)
                        }
                
                # Text objects
                for text_obj in section.get('text_objects', []):
                    obj_name = text_obj.get('name', '')
                    if obj_name:
                        objects[obj_name] = {
                            'type': 'text',
                            'section': section_name,
                            'data': text_obj,
                            'section_index': sections.index(section)
                        }
            return objects
        
        # Get all objects from both versions
        original_objects = get_all_objects_from_sections(original_metadata)
        modified_objects = get_all_objects_from_sections(modified_metadata)
        
        # Check for renames (object disappeared from original, new object appeared in modified)
        original_names = set(original_objects.keys())
        modified_names = set(modified_objects.keys())
        
        # Simple rename detection: if exactly one object disappeared and one appeared
        removed_names = original_names - modified_names
        added_names = modified_names - original_names
        
        if len(removed_names) == 1 and len(added_names) == 1:
            old_name = list(removed_names)[0]
            new_name = list(added_names)[0]
            old_obj = original_objects[old_name]
            new_obj = modified_objects[new_name]
            
            # Check if they're in the same section and same type (likely a rename)
            if (old_obj['section'] == new_obj['section'] and 
                old_obj['type'] == new_obj['type']):
                preview["changes"].append({
                    "type": "rename",
                    "description": f"Renamed {old_obj['type']} '{old_name}' to '{new_name}' in {old_obj['section']}",
                    "old_value": old_name,
                    "new_value": new_name,
                    "section": old_obj['section']
                })
        
        # Check for visibility changes (hidden/shown)
        for obj_name in original_names.intersection(modified_names):
            original_obj = original_objects[obj_name]
            modified_obj = modified_objects[obj_name]
            
            original_hidden = original_obj['data'].get('hidden', False)
            modified_hidden = modified_obj['data'].get('hidden', False)
            
            if not original_hidden and modified_hidden:
                preview["changes"].append({
                    "type": "hide",
                    "description": f"Hidden {original_obj['type']} '{obj_name}' in {original_obj['section']}",
                    "target": obj_name,
                    "section": original_obj['section']
                })
            elif original_hidden and not modified_hidden:
                preview["changes"].append({
                    "type": "show", 
                    "description": f"Showed {original_obj['type']} '{obj_name}' in {original_obj['section']}",
                    "target": obj_name,
                    "section": original_obj['section']
                })
        
        # Check for moves between sections
        for obj_name in original_names.intersection(modified_names):
            original_obj = original_objects[obj_name]
            modified_obj = modified_objects[obj_name]
            
            if original_obj['section'] != modified_obj['section']:
                preview["changes"].append({
                    "type": "move",
                    "description": f"Moved {original_obj['type']} '{obj_name}' from {original_obj['section']} to {modified_obj['section']}",
                    "target": obj_name,
                    "old_section": original_obj['section'],
                    "new_section": modified_obj['section']
                })
        
        # Check for text content changes
        for obj_name in original_names.intersection(modified_names):
            original_obj = original_objects[obj_name]
            modified_obj = modified_objects[obj_name]
            
            if original_obj['type'] == 'text' and modified_obj['type'] == 'text':
                original_text = original_obj['data'].get('text', '')
                modified_text = modified_obj['data'].get('text', '')
                
                if original_text != modified_text:
                    preview["changes"].append({
                        "type": "text_change",
                        "description": f"Changed text in '{obj_name}' from '{original_text}' to '{modified_text}'",
                        "target": obj_name,
                        "old_value": original_text,
                        "new_value": modified_text,
                        "section": original_obj['section']
                    })
        
        # Check for formatting changes
        for obj_name in original_names.intersection(modified_names):
            original_obj = original_objects[obj_name]
            modified_obj = modified_objects[obj_name]
            
            original_formatting = original_obj['data'].get('formatting', {})
            modified_formatting = modified_obj['data'].get('formatting', {})
            
            if original_formatting != modified_formatting:
                preview["changes"].append({
                    "type": "format",
                    "description": f"Changed formatting for {original_obj['type']} '{obj_name}' in {original_obj['section']}",
                    "target": obj_name,
                    "old_formatting": original_formatting,
                    "new_formatting": modified_formatting,
                    "section": original_obj['section']
                })
        
        # Check for section-level changes
        original_sections = original_metadata.get('sections', [])
        modified_sections = modified_metadata.get('sections', [])
        
        for i, original_section in enumerate(original_sections):
            if i < len(modified_sections):
                modified_section = modified_sections[i]
                section_name = original_section.get('name', f'Section {i+1}')
                
                original_hidden = original_section.get('hidden', False)
                modified_hidden = modified_section.get('hidden', False)
                
                if not original_hidden and modified_hidden:
                    preview["changes"].append({
                        "type": "hide_section",
                        "description": f"Hidden section '{section_name}'",
                        "target": section_name
                    })
                elif original_hidden and not modified_hidden:
                    preview["changes"].append({
                        "type": "show_section",
                        "description": f"Showed section '{section_name}'",
                        "target": section_name
                    })
        
        # Also check field_lineage if it exists (for backward compatibility)
        original_field_lineage = original_metadata.get('field_lineage', {})
        modified_field_lineage = modified_metadata.get('field_lineage', {})
        
        if original_field_lineage or modified_field_lineage:
            original_lineage_fields = set(original_field_lineage.keys())
            modified_lineage_fields = set(modified_field_lineage.keys())
            
            # Check for field lineage renames (only if not already detected in sections)
            lineage_removed = original_lineage_fields - modified_lineage_fields
            lineage_added = modified_lineage_fields - original_lineage_fields
            
            if len(lineage_removed) == 1 and len(lineage_added) == 1:
                old_name = list(lineage_removed)[0]
                new_name = list(lineage_added)[0]
                
                # Only add if we haven't already detected this rename in sections
                existing_renames = [c for c in preview["changes"] if c.get("type") == "rename"]
                if not any(r.get("old_value") == old_name and r.get("new_value") == new_name for r in existing_renames):
                    preview["changes"].append({
                        "type": "rename",
                        "description": f"Renamed field '{old_name}' to '{new_name}' (from field lineage)",
                        "old_value": old_name,
                        "new_value": new_name,
                        "section": "Field Lineage"
                    })
        
        # Create summary
        if preview["changes"]:
            change_count = len(preview["changes"])
            change_types = list(set(change.get("type", "") for change in preview["changes"]))
            preview["summary"] = f"Will make {change_count} change{'s' if change_count != 1 else ''}: {', '.join(change_types)}"
        else:
            preview["summary"] = "No changes detected"
        
        return preview 