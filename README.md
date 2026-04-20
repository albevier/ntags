# ntags - Audio Tag Editor TUI

A terminal user interface (TUI) application for editing audio file tags. Built with Python and ncurses.

## Features

- 🎵 Support for multiple audio formats: **MP3**, **FLAC**, and **AIFF**
- 📝 Edit common tags: Title, Artist, Album, Date/Year, Genre, Track Number
- 📁 Work with single files or entire directories
- 🔀 **Multi-file editing**: Select and edit multiple files at once
- ⌨️ Keyboard-driven interface with vim-style navigation
- 💾 Save changes directly to audio files
- 📊 Visual feedback for varying tag values across selected files

## Requirements

- Python 3.7+
- ncurses (included with most Unix-like systems)

## Installation

### Option 1: Using uv (Recommended)

1. Clone or download this repository
2. Install [uv](https://docs.astral.sh/uv/) if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Sync dependencies:

```bash
uv sync
```

### Option 2: Using pip (Traditional)

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install mutagen
```

## Usage

### Basic Usage

Edit a single file:
```bash
python ntags.py /path/to/audio/file.mp3
```

Edit all audio files in a directory:
```bash
python ntags.py /path/to/music/directory
```

Make the script executable (optional):
```bash
chmod +x ntags.py
./ntags.py /path/to/audio/file.mp3
```

### Keyboard Controls

#### Browser Mode (File List - default)
- `↑`/`k` - Move to previous file
- `↓`/`j` - Move to next file
- `SPACE` - Enter/exit selection or deselection mode
- `a` - Select all files
- `c` - Clear selection
- `TAB` - Switch to Editor Mode
- `e` - Switch to Editor Mode
- `s` - Save changes to selected files (or current file)
- `q` - Quit application

**Selection/Deselection Mode**: 
- Press `SPACE` on an **unselected** file to enter **selection mode** - navigate with arrow keys to select more files
- Press `SPACE` on a **selected** file to enter **deselection mode** - navigate with arrow keys to deselect files
- Press `SPACE` again to exit either mode

#### Editor Mode (Tag Editing)
- `↑`/`k` - Move to previous tag field
- `↓`/`j` - Move to next tag field
- `ENTER`/`e` - Edit current field
- `TAB` - Switch to Browser Mode
- `s` - Save changes to selected files (or current file)
- `r` - Reload current file (discard unsaved changes)
- `q` - Quit application

#### Edit Mode (Text Editing)
- Type to edit the field
- `ENTER` - Confirm changes (must press `s` to save to file)
- `ESC` - Cancel edit
- `BACKSPACE` - Delete character

### Multi-File Editing

When multiple files are selected:
- Tag values that are **identical** across all files are displayed normally
- Tag values that **differ** are shown as `*` (varying)
- Editing a field applies the change to **all selected files**
- Press `s` to save changes to all selected files at once

**Selection/Deselection Mode**: 
- Press `SPACE` on an **unselected file** to activate selection mode, then use arrow keys to quickly select multiple consecutive files
- Press `SPACE` on a **selected file** to activate deselection mode, then use arrow keys to quickly deselect multiple files
- Press `SPACE` again to exit either mode

## Workflow

### Single File Editing
1. Launch ntags with a file or directory path
2. Press `TAB` to switch to Editor Mode
3. Navigate between fields using `↑`/`↓` or `j`/`k`
4. Press `ENTER` or `e` to edit a field
5. Type your changes and press `ENTER` to confirm
6. Press `s` to save changes to the audio file
7. Press `q` to quit

### Multi-File Editing
1. Launch ntags with a directory path
2. In Browser Mode, use `↑`/`↓` or `j`/`k` to navigate files
3. Press `SPACE` on an unselected file to enter selection mode
4. Navigate with arrow keys to automatically select multiple files
5. Press `SPACE` again to exit selection mode (or use `a` to select all)
6. To deselect: Press `SPACE` on a selected file and navigate to deselect more
7. Press `TAB` to switch to Editor Mode
8. Fields showing `*` have varying values across selected files
9. Edit any field to apply the change to all selected files
10. Press `s` to save changes to all selected files
11. Press `q` to quit

## Supported Tag Fields

- **Title** - Song title
- **Artist** - Artist/performer name
- **Album Artist** - Album artist (often different from track artist)
- **Album** - Album name
- **Date/Year** - Release date or year
- **Genre** - Music genre
- **Track #** - Track number
- **Disc #** - Disc number (for multi-disc albums)
- **Composer** - Composer of the track
- **Comment** - Comments or notes about the track

## Supported Audio Formats

| Format | Extension | Tag System |
|--------|-----------|------------|
| MP3 | `.mp3` | ID3v2 |
| FLAC | `.flac` | Vorbis Comments |
| AIFF | `.aiff`, `.aif` | ID3v2 |

## Technical Details

- Built with Python's `curses` module (ncurses wrapper)
- Uses `mutagen` library for audio tag manipulation
- Supports recursive directory scanning
- UTF-8 encoding for text fields

## Troubleshooting

**Terminal too small error**: Resize your terminal window to be larger.

**Unsupported file format**: Ensure your file is MP3, FLAC, or AIFF format.

**Permission errors**: Make sure you have write permissions for the audio files.

**Display issues**: Ensure your terminal supports unicode and colors.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Contributing

Feel free to submit issues or improvements!
