"""
Data models for Crystal Reports
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class ReportMetadata(BaseModel):
    """Crystal Report metadata model"""
    report_id: str
    name: str
    version: str
    creation_date: Optional[datetime] = None
    sections: List[Dict] = []
    data_sources: List[Dict] = []
    field_lineage: Dict[str, Dict] = {}


class TextObject(BaseModel):
    """Text object in report"""
    name: str
    text: str
    font: str
    section: str


class FieldObject(BaseModel):
    """Field object in report"""
    name: str
    database_field: Optional[str] = None
    formula: Optional[str] = None
    section: str


class PictureObject(BaseModel):
    """Picture object in report"""
    name: str
    image_path: str
    section: str
