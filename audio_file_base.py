#!/usr/bin/env python3
"""
Base AudioFile class for loading and saving audio file tags
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict


class AudioFileBase(ABC):
    """Abstract base class for audio files with editable tags"""
    
    SUPPORTED_EXTENSIONS = set()
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.audio = None
        self.tags = {}
        self.load()
    
    @abstractmethod
    def load(self):
        """Load the audio file and extract tags"""
        pass
    
    @abstractmethod
    def _get_tag(self, tag_name: str) -> str:
        """Get a tag value from the audio file"""
        pass
    
    @abstractmethod
    def save_tags(self, new_tags: Dict[str, str]):
        """Save updated tags to the audio file"""
        pass
