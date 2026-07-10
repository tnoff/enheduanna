from pathlib import Path

from enheduanna.types.markdown.markdown_section import MarkdownSection
from enheduanna.utils.links import rewrite_relative_links, rewrite_section_links


def test_rewrite_moves_relative_link_up_a_dir():
    # Content moves from notes/week1/ down to documents/; a sibling link must gain '../'
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/documents')
    content = 'See [spec](./attachments/spec.pdf) for details'
    result = rewrite_relative_links(content, source, dest)
    assert result == 'See [spec](../notes/week1/attachments/spec.pdf) for details'


def test_rewrite_parent_relative_link():
    # A link to a shared sibling folder must stay pointed at the same target
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/notes/week2')
    content = '[shared](../shared/notes.md)'
    result = rewrite_relative_links(content, source, dest)
    assert result == '[shared](../shared/notes.md)'


def test_rewrite_image_link():
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/documents')
    content = '![diagram](./media/diagram.png)'
    result = rewrite_relative_links(content, source, dest)
    assert result == '![diagram](../notes/week1/media/diagram.png)'


def test_preserves_anchor_and_title_on_file_link():
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/documents')
    content = '[x](./doc.md#section "A Title")'
    result = rewrite_relative_links(content, source, dest)
    assert result == '[x](../notes/week1/doc.md#section "A Title")'


def test_skips_non_relative_targets():
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/documents')
    content = (
        '[web](https://example.com/page) '
        '[mail](mailto:me@example.com) '
        '[abs](/etc/hosts) '
        '[home](~/notes/x.md)'
    )
    # Nothing relative to a file, so nothing should change
    assert rewrite_relative_links(content, source, dest) == content


def test_same_dir_leaves_file_links_alone():
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/notes/week1')
    content = '[x](./attachments/spec.pdf)'
    assert rewrite_relative_links(content, source, dest) == content


def test_anchor_left_alone_when_heading_moved_along():
    # #setup points at a heading inside the moved content -> still resolves
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/documents')
    content = '[jump](#setup)'
    result = rewrite_relative_links(content, source, dest, moved_slugs={'setup'})
    assert result == '[jump](#setup)'


def test_anchor_rewritten_when_heading_stayed_behind():
    # #setup points at a heading that stayed in the source file -> cross-file link
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/documents')
    content = '[jump](#setup)'
    result = rewrite_relative_links(content, source, dest, stayed_slugs={'setup'})
    assert result == '[jump](../notes/week1/2025-01-01.md#setup)'


def test_anchor_left_alone_when_heading_absent():
    # #setup is not a heading anywhere in the source -> already dangling, leave it
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/documents')
    content = '[jump](#setup)'
    result = rewrite_relative_links(content, source, dest)
    assert result == '[jump](#setup)'


def test_anchor_rewritten_within_same_dir_different_file():
    # A same-dir move to a different file still orphans a stayed-behind anchor
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/notes/week1')
    content = '[jump](#setup)'
    result = rewrite_relative_links(content, source, dest, stayed_slugs={'setup'})
    assert result == '[jump](2025-01-01.md#setup)'


def test_rewrite_section_links_uses_moved_and_stayed_headings():
    # Moved subtree owns 'Details'; source file keeps 'Setup'
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/documents')

    moved = MarkdownSection('Reboot Steps', '[a](#details) and [b](#setup)', level=1)
    moved.add_section(MarkdownSection('Details', 'stuff', level=2))

    stayed = MarkdownSection('2025-01-01', '', level=1)
    stayed.add_section(MarkdownSection('Setup', 'env notes', level=2))

    rewrite_section_links(moved, source, dest, stayed)

    # #details moved along -> unchanged; #setup stayed behind -> cross-file
    assert moved.contents == '[a](#details) and [b](../notes/week1/2025-01-01.md#setup)'


def test_rewrite_section_links_recurses_file_links():
    source = Path('/base/notes/week1/2025-01-01.md')
    dest = Path('/base/documents')
    root = MarkdownSection('Root', '[a](./a.md)', level=1)
    child = MarkdownSection('Child', '[b](./nested/b.md)', level=2)
    root.add_section(child)

    rewrite_section_links(root, source, dest)

    assert root.contents == '[a](../notes/week1/a.md)'
    assert root.sections[0].contents == '[b](../notes/week1/nested/b.md)'
