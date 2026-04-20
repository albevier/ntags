#!/usr/bin/env python3
"""
WAVFile class for handling WAV audio files with ID3 tags
"""

from pathlib import Path
from typing import Dict
from mutagen import File as MutagenFile
from mutagen.id3 import TIT2, TPE1, TPE2, TALB, TDRC, TCON, TRCK, TPOS, TCOM, COMM

from audio_file_base import AudioFileBase


class WAVFile(AudioFileBase):
    """Handles WAV files with ID3 tags"""

    SUPPORTED_EXTENSIONS = {'.wav'}

    def load(self):
        """Load the WAV file and extract tags"""
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
        """Get a tag value from the WAV file"""
        if not self.audio or not self.audio.tags:
            return ""

        # WAV uses ID3 tags similar to MP3
        tag_map = {
            'title': 'TIT2',
            'artist': 'TPE1',
            'albumartist': 'TPE2',
            'album': 'TALB',
            'date': 'TDRC',
            'genre': 'TCON',
            'tracknumber': 'TRCK',
            'discnumber': 'TPOS',
            'composer': 'TCOM',
            'comment': 'COMM::eng',
        }

        frame = tag_map.get(tag_name)
        if frame and frame in self.audio.tags:
            if frame == 'COMM::eng':
                value = str(self.audio.tags[frame].text[0]) if self.audio.tags[frame].text else ""
            else:
                value = str(self.audio.tags[frame])
            return value

        return ""

    def save_tags(self, new_tags: Dict[str, str]):
        """Save updated tags to the WAV file"""
        try:
            # WAV uses ID3 tags
            if self.audio.tags is None:
                self.audio.add_tags()

            self.audio.tags['TIT2'] = TIT2(encoding=3, text=new_tags.get('title', ''))
            self.audio.tags['TPE1'] = TPE1(encoding=3, text=new_tags.get('artist', ''))
            self.audio.tags['TPE2'] = TPE2(encoding=3, text=new_tags.get('albumartist', ''))
            self.audio.tags['TALB'] = TALB(encoding=3, text=new_tags.get('album', ''))
            self.audio.tags['TDRC'] = TDRC(encoding=3, text=new_tags.get('date', ''))
            self.audio.tags['TCON'] = TCON(encoding=3, text=new_tags.get('genre', ''))
            self.audio.tags['TRCK'] = TRCK(encoding=3, text=new_tags.get('tracknumber', ''))
            self.audio.tags['TPOS'] = TPOS(encoding=3, text=new_tags.get('discnumber', ''))
            self.audio.tags['TCOM'] = TCOM(encoding=3, text=new_tags.get('composer', ''))
            if new_tags.get('comment', ''):
                self.audio.tags['COMM::eng'] = COMM(encoding=3, lang='eng', desc='', text=new_tags.get('comment', ''))

            self.audio.save()
            self.tags = new_tags.copy()
            return True
        except Exception as e:
            raise ValueError(f"Error saving tags: {e}")
