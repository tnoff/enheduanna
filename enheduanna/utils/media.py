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

def organize_media_for_collation(collation_dir: Path, start_date: datetime,
                                  end_date: datetime, config: MediaConfig) -> Dict[str, str]:
    '''
    Organize media files for a specific collation period

    collation_dir: The collation directory (e.g., 2025-01-20_2025-01-26/)
    start_date: Start of the collation period (inclusive)
    end_date: End of the collation period (inclusive)
    config: Media configuration

    Returns: Dictionary mapping old filenames to new filenames with subfolder info
             Format: {old_filename: (subfolder, new_filename)}
    '''
    if not config.enabled or not config.sources:
        return {}

    filename_mapping = {}

    # Process each source folder
    for source in config.sources:
        source_dir = Path(source.folder).expanduser()
        if not source_dir.exists():
            continue

        media_dir = collation_dir / source.subfolder
        media_dir.mkdir(parents=True, exist_ok=True)

        # Scan source folder for media files
        for file_path in source_dir.iterdir():
            if not file_path.is_file():
                continue

            # Check if file has matching extension
            if file_path.suffix.lower() not in [ext.lower() for ext in config.extensions]:
                continue

            # Get file modified time
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

            # Check if file is within date range
            if start_date > file_mtime or file_mtime > end_date:
                continue

            # Create new filename: YYYY-MM-DD_HH-MM-SS.ext
            new_filename = f"{file_mtime.strftime('%Y-%m-%d_%H-%M-%S')}{file_path.suffix}"
            new_path = media_dir / new_filename

            # Handle potential filename conflicts
            counter = 1
            while new_path.exists():
                new_filename = f"{file_mtime.strftime('%Y-%m-%d_%H-%M-%S')}_{counter}{file_path.suffix}"
                new_path = media_dir / new_filename
                counter += 1

            # Move or copy file
            if source.operation == "move":
                shutil.move(str(file_path), str(new_path))
                print(f'Moved {file_path.name} -> {new_path}')
            else:
                shutil.copy2(str(file_path), str(new_path))
                print(f'Copied {file_path.name} -> {new_path}')

            # Store mapping with subfolder information
            filename_mapping[file_path.name] = (source.subfolder, new_filename)

    return filename_mapping

def update_markdown_media_references(markdown_files: List[MarkdownFile],
                                      filename_mapping: Dict[str, Tuple[str, str]]):
    '''
    Update markdown image references to point to new media locations

    markdown_files: List of markdown files to update
    filename_mapping: Mapping of old filenames to (subfolder, new_filename) tuples
    '''
    if not filename_mapping:
        return

    for markdown_file in markdown_files:
        content = markdown_file.file_path.read_text()
        original_content = content

        # Update markdown image syntax: ![alt](path)
        for old_filename, (subfolder, new_filename) in filename_mapping.items():
            # Pattern to match image references with the old filename
            # Matches: ![...](~/path/to/old_filename) or ![...](/path/to/old_filename) or ![...](.../old_filename)
            markdown_pattern = rf'(!\[([^\]]*)\]\()([^)]*{re.escape(old_filename)})(\))'

            def replace_markdown_ref(match, subfolder=subfolder, new_filename=new_filename):
                alt_start = match.group(1)  # ![alt](
                end_paren = match.group(4)  # )

                # Replace with relative path to media directory
                new_path = f'./{subfolder}/{new_filename}'
                return f'{alt_start}{new_path}{end_paren}'

            content = re.sub(markdown_pattern, replace_markdown_ref, content)

            # Also handle HTML img tags: <img src="path">
            html_pattern = rf'(<img\s+[^>]*src=")([^"]*{re.escape(old_filename)})(")'

            def replace_html_ref(match, subfolder=subfolder, new_filename=new_filename):
                start = match.group(1)  # <img ... src="
                end_quote = match.group(3)  # "

                new_path = f'./{subfolder}/{new_filename}'
                return f'{start}{new_path}{end_quote}'

            content = re.sub(html_pattern, replace_html_ref, content)

        # Write back if changed
        if content != original_content:
            markdown_file.file_path.write_text(content)
