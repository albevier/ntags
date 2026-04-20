#!/usr/bin/env python3
"""
ntags - A TUI for editing audio file tags
Supports MP3, FLAC, and AIFF audio files
"""

import curses
import sys

from tag_editor_tui import TagEditorTUI

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: ntags.py <file_or_directory>")
        print("\nSupported formats: MP3, FLAC, AIFF")
        sys.exit(1)
    
    path = sys.argv[1]
    
    try:
        editor = TagEditorTUI(path)
        curses.wrapper(editor.run)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

