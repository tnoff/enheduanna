from datetime import date
from pathlib import Path

import click

from enheduanna.defaults import CONFIG_DEFAULT
from enheduanna.types.config import Config
from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.types.markdown.markdown_section import MarkdownSection

from enheduanna.utils.collation import create_parent_folder
from enheduanna.utils.files import list_markdown_files, find_last_markdown_file, normalize_file_name
from enheduanna.utils.markdown import generate_markdown_collation, generate_markdown_merge, remove_empty_sections


def ensure_entry_file(parent_folder: Path, today: date, config: Config,
                      last_markdown_file: MarkdownFile) -> Path:
    '''
    Ensure entry file exists
    parent_folder : Folder for week
    today : Todays date
    config: Complete config
    last_markdown_file : Last created markdown file
    '''
    entry_file = parent_folder / f'{today.strftime(config.file.date_output_format)}.md'
    if entry_file.exists():
        return entry_file
    markdown_contents = MarkdownSection(today.strftime(config.file.date_output_format), '')
    for section in config.file.entry_sections:
        # Roll over existing section from last file if applicable
        if last_markdown_file and section.rollover:
            existing_section = last_markdown_file.root_section.remove_section(section.title)
            if existing_section:
                markdown_contents.add_section(existing_section)
                last_markdown_file.write()
                continue
        markdown_contents.add_section(section)
    entry_file.write_text(markdown_contents.write())
    return entry_file


@click.group()
@click.option('-c', '--config-file', default=CONFIG_DEFAULT, show_default=True,
              type=click.Path(file_okay=True, dir_okay=False, exists=False))
@click.pass_context
def main(context: click.Context, config_file: str):
    '''
    Enheduanna CLI Runner
    '''
    context.obj = Config.from_yaml(Path(config_file))

@main.command('new-entry')
@click.pass_context
def new_entry(context: click.Context):
    '''
    Create a new entry for today
    '''
    # Get date basics
    today = date.today()
    # Find last file, see if it has any carryover sections
    last_file = find_last_markdown_file(context.obj.file.entries_directory)
    if last_file:
        last_file = MarkdownFile.from_file(last_file)
    # Get folder and file ready
    parent_folder = create_parent_folder(context.obj, today)
    entry_file = ensure_entry_file(parent_folder, today, context.obj, last_file)
    click.echo(f'Created entry file {entry_file}')

@main.command('collate')
@click.option('-cn', '--collate-name', default='summary.md', show_default=True)
@click.option('-t', '--title')
@click.argument('file_dir', type=click.Path(file_okay=False, dir_okay=True, exists=True))
@click.pass_context
def collate(context: click.Context, file_dir: str, title, collate_name: str):
    '''
    Collate entry files
    '''
    file_dir = Path(file_dir)
    title = title or f'Summary | {file_dir.name.replace("_", " -> ")}'
    markdown_files = []
    for path in list_markdown_files(file_dir):
        markdown_files.append(MarkdownFile.from_file(path))
    # Ignore sections set automatically but not in collate
    ignore_sections = set(i.title for i in context.obj.file.entry_sections) - set([i.title for i in context.obj.file.collate_sections]) #pylint:disable=consider-using-set-comprehension
    combos, documents = generate_markdown_collation(markdown_files, context.obj.file.collate_sections, ignore_sections)
    new_document = MarkdownSection(title, '')
    for section in combos:
        section.level = 2
        new_document.add_section(section)
    new_path = file_dir / collate_name
    new_path.write_text(new_document.write())
    click.echo(f'Collation data written to file {new_path}')
    for document in documents:
        new_path = context.obj.file.document_directory / f'{normalize_file_name(document.title)}.md'
        new_file = MarkdownFile(new_path, document)
        new_file.write()
        click.echo(f'Writing document to file {new_path}')
    # Clean up files at the end
    click.echo(f'Cleaning up files in dir {file_dir}')
    remove_empty_sections(markdown_files)

@main.command('merge')
@click.option('-t', '--title')
@click.argument('file_dir', type=click.Path(file_okay=False, dir_okay=True, exists=True))
@click.argument('output_file', type=click.Path(file_okay=True, dir_okay=False, exists=False))
def merge(file_dir: str, output_file: str, title):
    '''
    Merge all markdown files into a single file
    '''
    file_dir = Path(file_dir)
    output_file = Path(output_file)
    title = title or f'Merged | {file_dir.name.replace("_", " -> ")}'
    markdown_files = []
    # Include all markdown files, not just entries
    for path in list_markdown_files(file_dir, only_include_entry=False):
        markdown_files.append(MarkdownFile.from_file(path))
    merged_section = generate_markdown_merge(markdown_files, title)
    output_file.write_text(merged_section.write())
    click.echo(f'Merged data written to file {output_file}')

if __name__ == '__main__':
    main(obj={}) # pylint:disable=no-value-for-parameter
