"""
This module defines the data types used in the ingestion process.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from django.contrib.gis.geos import Point
from enum import Enum


class SignalType(str, Enum):
    ROBBERY = 'robbery'
    ASSAULT = 'assault'
    BURGLARY = 'burglary'
    VEHICLE_THEFT = 'vehicle_theft'
    HARASSMENT = 'harassment'
    OTHER = 'other'

@dataclass
class RawSignal:
    """
    Original Signal from RSS feed.
    """
    title: str
    description: str
    signal_type: SignalType
    link: str
    published: datetime
    source_name: str  # Name of the source newspaper
    location: Optional[Point]
    has_photo: bool = False
    has_video: bool = False

@dataclass
class NormalizedSignal:
    """
    Standardized signal for scoring and storage.
    """
    title: str
    signal_type: SignalType
    description: str
    timestamp: datetime
    location: Optional[Point]
    source_platform: str
    source_identifier: str  # e.g., RSS feed URL or name
    additional_data: Optional[Dict] = None  # any extra info
