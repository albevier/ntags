#!/usr/bin/env python3
"""
FLACFile class for handling FLAC audio files with Vorbis comments
"""

from pathlib import Path
from typing import Dict
from mutagen import File as MutagenFile

from audio_file_base import AudioFileBase


class FLACFile(AudioFileBase):
    """Handles FLAC files with Vorbis comments"""
    
    SUPPORTED_EXTENSIONS = {'.flac'}
    
    def load(self):
        """Load the FLAC file and extract tags"""
        try:
            self.audio = MutagenFile(str(self.filepath))
            if self.audio is None:
                raise ValueError("Unsupported file format")
            
            # Extract common tags
            self.tags = {
                'title': self._get_tag('title'),
                'artist': self._get_tag('artist'),
                'albumartist': self._get_tag('albumartist'),
                'album': self._get_tag('album'),
                'date': self._get_tag('date'),
                'genre': self._get_tag('genre'),
                'tracknumber': self._get_tag('tracknumber'),
                'discnumber': self._get_tag('discnumber'),
                'composer': self._get_tag('composer'),
                'comment': self._get_tag('comment'),
            }
        except Exception as e:
            raise ValueError(f"Error loading file: {e}")
    
    def _get_tag(self, tag_name: str) -> str:
        """Get a tag value from the FLAC file"""
        if not self.audio:
            return ""
        
        # FLAC uses vorbis comments
        if tag_name in self.audio:
            value = self.audio[tag_name][0] if self.audio[tag_name] else ""
            return value
        
        return ""
    
    def save_tags(self, new_tags: Dict[str, str]):
        """Save updated tags to the FLAC file"""
        try:
            # FLAC uses vorbis comments
            for key, value in new_tags.items():
                self.audio[key] = value
            
            self.audio.save()
            self.tags = new_tags.copy()
            return True
        except Exception as e:
            raise ValueError(f"Error saving tags: {e}")
