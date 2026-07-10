from pathlib import Path
from re import match, sub
import os

from enheduanna.types.markdown.markdown_section import MarkdownSection

# Matches markdown inline links and images: [text](target) and ![alt](target)
LINK_REGEX = r'(!?\[[^\]]*\]\()([^)]+)(\))'
# Matches a URL scheme prefix like http:, https:, mailto:
SCHEME_REGEX = r'^[a-z][a-z0-9+.-]*:'


def _slugify(title: str) -> str:
    '''
    Convert a heading title into a GitHub-style anchor slug

    title : Heading title
    '''
    slug = title.strip().lower()
    slug = sub(r'[^\w\s-]', '', slug)
    slug = sub(r'\s+', '-', slug)
    return slug


def _collect_slugs(section: MarkdownSection) -> set:
    '''
    Collect anchor slugs for a section and all of its subsections

    section : MarkdownSection
    '''
    slugs = {_slugify(section.title)}
    for subsection in section.sections:
        slugs |= _collect_slugs(subsection)
    return slugs


def _split_suffixes(target: str) -> tuple:
    '''
    Split a link target into (path, anchor, title) suffixes

    target : Raw link target, may include "#anchor" and/or a "title"
    '''
    target = target.strip()
    title = ''
    for quote in ('"', "'"):
        idx = target.find(f' {quote}')
        if idx != -1:
            title = target[idx:]
            target = target[:idx]
            break
    anchor = ''
    if '#' in target:
        target, _, rest = target.partition('#')
        anchor = f'#{rest}'
    return target, anchor, title


def _rewrite_target(target: str, source_file: Path, dest_dir: Path,
                    moved_slugs: set, stayed_slugs: set) -> str:
    '''
    Rewrite a single link target so it resolves to the same file after moving
    from source_file's directory to dest_dir. Leaves non-relative targets alone.

    target : Raw link target, may include "#anchor" and/or a "title" suffix
    source_file : File the content is moving from
    dest_dir : Directory the content is moving to
    moved_slugs : Anchor slugs that moved along with the content
    stayed_slugs : Anchor slugs that stayed behind in the source file
    '''
    path, anchor, title = _split_suffixes(target)
    source_dir = source_file.parent
    # Anchor-only link ([x](#heading)) into the same document
    if not path and anchor:
        slug = anchor.lstrip('#').lower()
        # Heading moved along with the link, or exists nowhere: leave as-is
        if slug in moved_slugs or slug not in stayed_slugs:
            return f'{anchor}{title}'
        # Heading stayed behind: point back at the source file
        new_path = os.path.relpath(source_file, dest_dir)
        return f'{new_path}{anchor}{title}'
    # Schemes, absolute paths, home paths, and empty targets are left alone
    if not path or path.startswith(('/', '~')) or match(SCHEME_REGEX, path):
        return f'{path}{anchor}{title}'
    # Relative file link: only recompute when the directory actually changes
    if source_dir.resolve() == dest_dir.resolve():
        return f'{path}{anchor}{title}'
    new_path = os.path.relpath(source_dir / path, dest_dir)
    return f'{new_path}{anchor}{title}'


def rewrite_relative_links(content: str, source_file: Path, dest_dir: Path,
                           moved_slugs: set = frozenset(), stayed_slugs: set = frozenset()) -> str:
    '''
    Rewrite relative file links in markdown content so they resolve to the same
    target after moving the content from source_file's directory to dest_dir.

    content : Markdown content
    source_file : File the content is moving from
    dest_dir : Directory the content is moving to
    moved_slugs : Anchor slugs that moved along with the content
    stayed_slugs : Anchor slugs that stayed behind in the source file
    '''
    source_file = Path(source_file)
    dest_dir = Path(dest_dir)

    def _replace(matcher):
        prefix = matcher.group(1)
        target = matcher.group(2)
        suffix = matcher.group(3)
        new_target = _rewrite_target(target, source_file, dest_dir, moved_slugs, stayed_slugs)
        return f'{prefix}{new_target}{suffix}'

    return sub(LINK_REGEX, _replace, content)


def rewrite_section_links(section: MarkdownSection, source_file: Path, dest_dir: Path,
                          source_root: MarkdownSection = None) -> None:
    '''
    Rewrite relative links in a section and all of its subsections in place.

    Relative file links are re-based on the directory change. Anchor-only links
    are rewritten into cross-file links when the heading they point at stayed
    behind in the source file rather than moving along with the section.

    section : MarkdownSection whose contents are moving directories
    source_file : File the section came from
    dest_dir : Directory the section is moving to
    source_root : Root section remaining in the source file, used to detect
                  headings that stayed behind (None to skip anchor rewriting)
    '''
    source_file = Path(source_file)
    dest_dir = Path(dest_dir)
    moved_slugs = _collect_slugs(section)
    stayed_slugs = _collect_slugs(source_root) if source_root is not None else frozenset()
    _rewrite_section(section, source_file, dest_dir, moved_slugs, stayed_slugs)


def _rewrite_section(section: MarkdownSection, source_file: Path, dest_dir: Path,
                     moved_slugs: set, stayed_slugs: set) -> None:
    '''
    Recursively rewrite links in a section using pre-computed slug sets
    '''
    section.contents = rewrite_relative_links(section.contents, source_file, dest_dir, moved_slugs, stayed_slugs)
    for subsection in section.sections:
        _rewrite_section(subsection, source_file, dest_dir, moved_slugs, stayed_slugs)
