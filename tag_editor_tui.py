#!/usr/bin/env python3
"""
TagEditorTUI class - TUI interface for editing audio file tags
"""

import curses
from pathlib import Path
from typing import List, Dict, Optional

from audio_file import AudioFile, SUPPORTED_EXTENSIONS
from audio_file_base import AudioFileBase


class TagEditorTUI:
    """TUI for editing audio file tags"""
    
    def __init__(self, path: str):
        self.path = Path(path).resolve()
        self.files: List[Path] = []
        self.current_file_index = 0
        self.current_audio: Optional[AudioFileBase] = None
        self.editing_field = 0
        self.status_message = ""
        self.error_message = ""
        
        # Multi-file selection
        self.selected_files: set = set()  # Set of file indices
        self.loaded_audio_files: Dict[int, AudioFileBase] = {}  # Cache of loaded files
        
        # UI state
        self.ui_mode = 'browser'  # 'browser' or 'editor'
        self.file_scroll_offset = 0  # For scrolling through file list
        self.sidebar_width = 40  # Width of file browser sidebar
        
        # Tag field names
        self.tag_fields = ['title', 'artist', 'albumartist', 'album', 'date', 'genre', 'tracknumber', 'discnumber', 'composer', 'comment']
        self.tag_labels = ['Title', 'Artist', 'Album Artist', 'Album', 'Date/Year', 'Genre', 'Track #', 'Disc #', 'Composer', 'Comment']
        
        # Load files
        self._load_files()
    
    def _load_files(self):
        """Load audio files from the given path"""
        if self.path.is_file():
            if self.path.suffix.lower() in SUPPORTED_EXTENSIONS:
                self.files = [self.path]
            else:
                raise ValueError(f"Unsupported file type: {self.path.suffix}")
        elif self.path.is_dir():
            self.files = sorted([
                f for f in self.path.rglob("*")
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
            ])
            if not self.files:
                raise ValueError("No supported audio files found in directory")
        else:
            raise ValueError("Path does not exist")
        
        # Load first file
        if self.files:
            self._load_current_file()
    
    def _load_current_file(self):
        """Load the currently selected audio file"""
        try:
            if self.current_file_index not in self.loaded_audio_files:
                self.loaded_audio_files[self.current_file_index] = AudioFile(self.files[self.current_file_index])
            self.current_audio = self.loaded_audio_files[self.current_file_index]
            self.error_message = ""
        except Exception as e:
            self.error_message = str(e)
            self.current_audio = None
    
    def _get_merged_tags(self) -> Dict[str, str]:
        """Get merged tags from all selected files. Returns tags with '*' for varying values."""
        if not self.selected_files:
            # No files selected, return current file's tags
            if self.current_audio:
                return self.current_audio.tags.copy()
            return {}
        
        # Load all selected files
        for idx in self.selected_files:
            if idx not in self.loaded_audio_files:
                try:
                    self.loaded_audio_files[idx] = AudioFile(self.files[idx])
                except:
                    pass  # Skip files that fail to load
        
        # Merge tags
        merged_tags = {}
        for field in self.tag_fields:
            values = set()
            for idx in self.selected_files:
                if idx in self.loaded_audio_files:
                    value = self.loaded_audio_files[idx].tags.get(field, '')
                    values.add(value)
            
            if len(values) == 0:
                merged_tags[field] = ''
            elif len(values) == 1:
                merged_tags[field] = values.pop()
            else:
                merged_tags[field] = '*'  # Indicates varying values
        
        return merged_tags
    
    def _get_display_path(self, file_path: Path) -> str:
        """Get a shortened display path for a file."""
        try:
            rel_path = file_path.relative_to(self.path if self.path.is_dir() else self.path.parent)
            return str(rel_path)
        except ValueError:
            return file_path.name
    
    def run(self, stdscr):
        """Main TUI loop"""
        curses.curs_set(0)  # Hide cursor
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        
        edit_mode = False
        edit_buffer = ""
        
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Draw header
            self._draw_header(stdscr, width)
            
            # Compute sidebar width based on screen size
            sidebar_width = min(self.sidebar_width, width // 3)
            
            # Draw file browser sidebar
            self._draw_file_browser(stdscr, height, sidebar_width)
            
            # Draw vertical separator
            for y in range(1, height - 3):
                try:
                    stdscr.addch(y, sidebar_width, '│', curses.color_pair(1))
                except:
                    pass
            
            # Draw tag editor on the right
            self._draw_tag_editor(stdscr, height, width, sidebar_width, edit_mode, edit_buffer)
            
            # Draw error message
            if self.error_message:
                y = height - 5
                stdscr.addstr(y, 2, "ERROR: " + self.error_message[:width-10], curses.color_pair(3))
            
            # Draw status message
            if self.status_message:
                y = height - 4
                stdscr.addstr(y, 2, self.status_message[:width-4], curses.color_pair(2))
            
            # Draw help
            self._draw_help(stdscr, height, width, edit_mode)
            
            stdscr.refresh()
            
            # Handle input
            try:
                key = stdscr.getch()
            except:
                continue
            
            if edit_mode:
                # Edit mode keybindings
                if key == 27:  # ESC
                    edit_mode = False
                    self.status_message = "Edit cancelled"
                elif key == 10 or key == curses.KEY_ENTER:  # Enter
                    # Save the edited value to selected files or current file
                    if self.selected_files:
                        # Apply to all selected files
                        for idx in self.selected_files:
                            if idx in self.loaded_audio_files:
                                self.loaded_audio_files[idx].tags[self.tag_fields[self.editing_field]] = edit_buffer
                        self.status_message = f"Field updated for {len(self.selected_files)} files (press 's' to save)"
                    elif self.current_audio:
                        self.current_audio.tags[self.tag_fields[self.editing_field]] = edit_buffer
                        self.status_message = "Field updated (press 's' to save to file)"
                    edit_mode = False
                elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                    edit_buffer = edit_buffer[:-1]
                elif 32 <= key <= 126:  # Printable characters
                    edit_buffer += chr(key)
            else:
                # Navigation mode keybindings
                if key == ord('q'):
                    break
                elif key == ord('\t') or key == 9:  # Tab - switch between browser and editor
                    if self.ui_mode == 'browser':
                        self.ui_mode = 'editor'
                        self.status_message = "Editor mode - navigate tags with j/k"
                    else:
                        self.ui_mode = 'browser'
                        self.status_message = "Browser mode - navigate files with j/k"
                elif key == ord(' '):  # Space - toggle selection of current file
                    if self.ui_mode == 'browser':
                        if self.current_file_index in self.selected_files:
                            self.selected_files.remove(self.current_file_index)
                            self.status_message = f"File deselected ({len(self.selected_files)} selected)"
                        else:
                            self.selected_files.add(self.current_file_index)
                            self.status_message = f"File selected ({len(self.selected_files)} selected)"
                elif key == curses.KEY_UP or key == ord('k'):
                    if self.ui_mode == 'browser':
                        self.current_file_index = (self.current_file_index - 1) % len(self.files)
                        self._load_current_file()
                    else:
                        self.editing_field = (self.editing_field - 1) % len(self.tag_fields)
                elif key == curses.KEY_DOWN or key == ord('j'):
                    if self.ui_mode == 'browser':
                        self.current_file_index = (self.current_file_index + 1) % len(self.files)
                        self._load_current_file()
                    else:
                        self.editing_field = (self.editing_field + 1) % len(self.tag_fields)
                elif key == curses.KEY_LEFT or key == ord('h'):
                    if self.ui_mode == 'browser' and len(self.files) > 1:
                        self.current_file_index = (self.current_file_index - 1) % len(self.files)
                        self._load_current_file()
                        self.status_message = "Previous file"
                elif key == curses.KEY_RIGHT or key == ord('l'):
                    if self.ui_mode == 'browser' and len(self.files) > 1:
                        self.current_file_index = (self.current_file_index + 1) % len(self.files)
                        self._load_current_file()
                        self.status_message = "Next file"
                elif key == 10 or key == curses.KEY_ENTER or key == ord('e'):
                    # Enter edit mode (only in editor mode)
                    if self.ui_mode == 'editor':
                        # Get the current value to edit
                        if self.selected_files:
                            merged_tags = self._get_merged_tags()
                            current_value = merged_tags.get(self.tag_fields[self.editing_field], "")
                            # If value is '*', start with empty string
                            edit_buffer = "" if current_value == '*' else current_value
                        elif self.current_audio:
                            edit_buffer = self.current_audio.tags.get(self.tag_fields[self.editing_field], "")
                        else:
                            continue
                        edit_mode = True
                        self.status_message = ""
                elif key == ord('s'):
                    # Save tags to file(s)
                    if self.selected_files:
                        # Save all selected files
                        saved_count = 0
                        failed_count = 0
                        for idx in self.selected_files:
                            if idx in self.loaded_audio_files:
                                try:
                                    audio_file = self.loaded_audio_files[idx]
                                    audio_file.save_tags(audio_file.tags)
                                    saved_count += 1
                                except Exception as e:
                                    failed_count += 1
                        if failed_count == 0:
                            self.status_message = f"Saved {saved_count} file(s) successfully!"
                        else:
                            self.status_message = f"Saved {saved_count}, failed {failed_count}"
                    elif self.current_audio:
                        try:
                            self.current_audio.save_tags(self.current_audio.tags)
                            self.status_message = "Tags saved successfully!"
                        except Exception as e:
                            self.error_message = f"Failed to save: {e}"
                elif key == ord('r'):
                    # Reload current file
                    if self.current_file_index in self.loaded_audio_files:
                        del self.loaded_audio_files[self.current_file_index]
                    self._load_current_file()
                    self.status_message = "File reloaded"
                elif key == ord('c'):
                    # Clear selection
                    self.selected_files.clear()
                    self.status_message = "Selection cleared"
                elif key == ord('a'):
                    # Select all files
                    self.selected_files = set(range(len(self.files)))
                    self.status_message = f"Selected all {len(self.files)} files"
    
    def _draw_header(self, stdscr, width):
        """Draw the header"""
        title = " ntags - Audio Tag Editor "
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.color_pair(1) | curses.A_BOLD)
    
    def _draw_file_browser(self, stdscr, height, sidebar_width):
        """Draw the file browser sidebar"""
        # Header
        header = " Files "
        if self.ui_mode == 'browser':
            stdscr.addstr(2, 1, header, curses.color_pair(5) | curses.A_BOLD)
        else:
            stdscr.addstr(2, 1, header, curses.color_pair(1) | curses.A_BOLD)
        
        # Show selection count if any files are selected
        if self.selected_files:
            sel_text = f"[{len(self.selected_files)} selected]"
            try:
                stdscr.addstr(2, sidebar_width - len(sel_text) - 1, sel_text, curses.color_pair(6))
            except:
                pass
        
        # Calculate visible area
        y_start = 3
        y_end = height - 3
        visible_lines = y_end - y_start
        
        # Adjust scroll offset to keep current file visible
        if self.current_file_index < self.file_scroll_offset:
            self.file_scroll_offset = self.current_file_index
        elif self.current_file_index >= self.file_scroll_offset + visible_lines:
            self.file_scroll_offset = self.current_file_index - visible_lines + 1
        
        # Draw files
        for i in range(visible_lines):
            file_idx = self.file_scroll_offset + i
            if file_idx >= len(self.files):
                break
            
            y = y_start + i
            file_path = self.files[file_idx]
            display_name = self._get_display_path(file_path)
            
            # Truncate if too long
            max_name_len = sidebar_width - 5
            if len(display_name) > max_name_len:
                display_name = display_name[:max_name_len-3] + "..."
            
            # Determine style
            is_current = file_idx == self.current_file_index
            is_selected = file_idx in self.selected_files
            
            prefix = ""
            if is_selected:
                prefix = "✓ "
            else:
                prefix = "  "
            
            line_text = prefix + display_name
            
            # Draw with appropriate style
            if is_current and self.ui_mode == 'browser':
                stdscr.addstr(y, 1, line_text[:sidebar_width-2], curses.color_pair(5))
            elif is_current:
                stdscr.addstr(y, 1, line_text[:sidebar_width-2], curses.color_pair(4))
            elif is_selected:
                stdscr.addstr(y, 1, line_text[:sidebar_width-2], curses.color_pair(6))
            else:
                stdscr.addstr(y, 1, line_text[:sidebar_width-2])
    
    def _draw_tag_editor(self, stdscr, height, width, sidebar_width, edit_mode, edit_buffer):
        """Draw the tag editor on the right side"""
        x_start = sidebar_width + 2
        available_width = width - x_start - 2
        
        # Header
        header = " Tag Editor "
        if self.ui_mode == 'editor':
            stdscr.addstr(2, x_start, header, curses.color_pair(5) | curses.A_BOLD)
        else:
            stdscr.addstr(2, x_start, header, curses.color_pair(1) | curses.A_BOLD)
        
        # Show what we're editing
        y = 3
        if self.selected_files:
            info = f"Editing {len(self.selected_files)} file(s)"
            stdscr.addstr(y, x_start, info[:available_width], curses.color_pair(2))
            y += 1
            stdscr.addstr(y, x_start, "* = varying values", curses.color_pair(6))
            tags_to_show = self._get_merged_tags()
        elif self.current_audio:
            filename = self.files[self.current_file_index].name
            file_info = f"{filename}"
            stdscr.addstr(y, x_start, file_info[:available_width], curses.color_pair(2))
            tags_to_show = self.current_audio.tags
        else:
            stdscr.addstr(y, x_start, "No file loaded", curses.color_pair(3))
            return
        
        y += 2
        
        # Draw tags
        for i, (field, label) in enumerate(zip(self.tag_fields, self.tag_labels)):
            if y >= height - 3:
                break
            
            value = tags_to_show.get(field, "")
            
            # Highlight current field
            if i == self.editing_field and not edit_mode and self.ui_mode == 'editor':
                stdscr.addstr(y, x_start, f"{label:14}: ", curses.color_pair(5))
                stdscr.addstr(y, x_start + 16, value[:available_width-18], curses.color_pair(5))
            elif i == self.editing_field and edit_mode:
                stdscr.addstr(y, x_start, f"{label:14}: ", curses.color_pair(4))
                stdscr.addstr(y, x_start + 16, edit_buffer[:available_width-18], curses.color_pair(4))
            else:
                stdscr.addstr(y, x_start, f"{label:14}: ", curses.color_pair(1))
                # Highlight varying values in magenta
                if value == '*':
                    stdscr.addstr(y, x_start + 16, value[:available_width-18], curses.color_pair(6))
                else:
                    stdscr.addstr(y, x_start + 16, value[:available_width-18])
            
            y += 1
    
    def _draw_help(self, stdscr, height, width, edit_mode):
        """Draw help text at the bottom"""
        y = height - 2
        if edit_mode:
            help_text = "ESC: Cancel | ENTER: Save field"
        elif self.ui_mode == 'browser':
            help_text = "TAB: Editor | ↑↓/jk: Navigate | SPACE: Select/Deselect | a: Select All | c: Clear | s: Save | q: Quit"
        else:
            help_text = "TAB: Browser | ↑↓/jk: Navigate | ENTER/e: Edit | s: Save | q: Quit"
        
        stdscr.addstr(y, 2, help_text[:width-4], curses.color_pair(1))
