from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import re
import shutil

from enheduanna.types.config.media import MediaConfig
from enheduanna.types.markdown.markdown_file import MarkdownFile

def parse_collation_folder_name(folder_name: str, date_format: str) -> Tuple[datetime, datetime] | None:
    '''
    Parse collation folder name to extract start and end dates

    folder_name: Name of the collation folder (e.g., "2025-01-20_2025-01-26")
    date_format: Date format string from config (e.g., "%Y-%m-%d")

    Returns: Tuple of (start_datetime, end_datetime) or None if parsing fails
    '''
    parts = folder_name.split('_')
    if len(parts) < 2:
        return None

    try:
        # Parse start date from first part
        start_date = datetime.strptime(parts[0], date_format)
        # Parse end date from second part
        end_date = datetime.strptime(parts[1], date_format)
        # Set end date to end of day (23:59:59)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        return (start_date, end_date)
    except ValueError:
        return None

def parse_media_filename(filename: str, regex: str) -> datetime | None:
    '''
    Parse a media filename to extract datetime using a regex pattern

    filename: The filename to parse
    regex: Regex pattern with named groups: year, month, day, hour, minute, second

    Returns datetime if all groups match, None otherwise
    '''
    match = re.search(regex, filename)
    if not match:
        return None

    try:
        groups = match.groupdict()
        year = int(groups['year'])
        month = int(groups['month'])
        day = int(groups['day'])
        hour = int(groups['hour'])
        minute = int(groups['minute'])
        second = int(groups['second'])
        return datetime(year, month, day, hour, minute, second)
    except (KeyError, ValueError):
        return None

def organize_media_for_collation(collation_dir: Path, start_date: datetime,
                                  end_date: datetime, config: MediaConfig) -> Dict[str, str]:
    '''
    Organize media files for a specific collation period

    collation_dir: The collation directory (e.g., 2025-01-20_2025-01-26/)
    start_date: Start of the collation period (inclusive)
    end_date: End of the collation period (inclusive)
    config: Media configuration

    Returns: Dictionary mapping old filenames to new filenames
    '''
    if not config.enabled or not config.source_directory or not config.date_regex:
        return {}

    source_dir = Path(config.source_directory).expanduser()
    if not source_dir.exists():
        return {}

    media_dir = collation_dir / config.subfolder
    media_dir.mkdir(exist_ok=True)

    filename_mapping = {}

    # Scan source directory for media files
    for file_path in source_dir.iterdir():
        if not file_path.is_file():
            continue

        # Check if file has matching extension
        if file_path.suffix.lower() not in [ext.lower() for ext in config.extensions]:
            continue

        # Parse datetime from filename
        file_datetime = parse_media_filename(file_path.name, config.date_regex)
        if not file_datetime:
            continue

        # Check if file is within date range
        if start_date > file_datetime or file_datetime > end_date:
            continue

        # Create new filename: YYYY-MM-DD_HH-MM-SS.ext
        new_filename = f"{file_datetime.strftime('%Y-%m-%d_%H-%M-%S')}{file_path.suffix}"
        new_path = media_dir / new_filename

        # Move or copy file
        if config.operation == "move":
            shutil.move(str(file_path), str(new_path))
            print(f'Moved {file_path.name} -> {new_path}')
        else:
            shutil.copy2(str(file_path), str(new_path))
            print(f'Copied {file_path.name} -> {new_path}')

        filename_mapping[file_path.name] = new_filename

    return filename_mapping

def update_markdown_media_references(markdown_files: List[MarkdownFile],
                                      subfolder: str,
                                      filename_mapping: Dict[str, str]):
    '''
    Update markdown image references to point to new media locations

    markdown_files: List of markdown files to update
    subfolder: Subfolder name where media files are stored (e.g., "media")
    filename_mapping: Mapping of old filenames to new filenames
    '''
    if not filename_mapping:
        return

    for markdown_file in markdown_files:
        content = markdown_file.file_path.read_text()
        original_content = content

        # Update markdown image syntax: ![alt](path)
        for old_filename, new_filename in filename_mapping.items():
            # Pattern to match image references with the old filename
            # Matches: ![...](~/path/to/old_filename) or ![...](/path/to/old_filename) or ![...](.../old_filename)
            markdown_pattern = rf'(!\[([^\]]*)\]\()([^)]*{re.escape(old_filename)})(\))'

            def replace_markdown_ref(match, new_name=new_filename):
                alt_start = match.group(1)  # ![alt](
                end_paren = match.group(4)  # )

                # Replace with relative path to media directory
                new_path = f'./{subfolder}/{new_name}'
                return f'{alt_start}{new_path}{end_paren}'

            content = re.sub(markdown_pattern, replace_markdown_ref, content)

            # Also handle HTML img tags: <img src="path">
            html_pattern = rf'(<img\s+[^>]*src=")([^"]*{re.escape(old_filename)})(")'

            def replace_html_ref(match, new_name=new_filename):
                start = match.group(1)  # <img ... src="
                end_quote = match.group(3)  # "

                new_path = f'./{subfolder}/{new_name}'
                return f'{start}{new_path}{end_quote}'

            content = re.sub(html_pattern, replace_html_ref, content)

        # Write back if changed
        if content != original_content:
            markdown_file.file_path.write_text(content)
