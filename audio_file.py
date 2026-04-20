#!/usr/bin/env python3
"""
AudioFile factory for creating the appropriate audio file type
Supports MP3, FLAC, and AIFF audio files
"""

from pathlib import Path

from audio_file_base import AudioFileBase
from mp3_file import MP3File
from flac_file import FLACFile
from aiff_file import AIFFFile
from wav_file import WAVFile


# Supported file extensions
SUPPORTED_EXTENSIONS = {'.mp3', '.flac', '.aiff', '.aif', '.wav'}


def AudioFile(filepath: Path) -> AudioFileBase:
    """
    Factory function to create the appropriate audio file type based on extension.

    Args:
        filepath: Path to the audio file

    Returns:
        An instance of the appropriate AudioFile subclass (MP3File, FLACFile, AIFFFile, or WAVFile)

    Raises:
        ValueError: If the file extension is not supported
    """
    ext = filepath.suffix.lower()

    if ext == '.mp3':
        return MP3File(filepath)
    elif ext == '.flac':
        return FLACFile(filepath)
    elif ext in {'.aiff', '.aif'}:
        return AIFFFile(filepath)
    elif ext == '.wav':
        return WAVFile(filepath)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
