# Changelog

All notable changes to enheduanna will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-07-31

### Changed

- - `collate` can now aggregate a recurring document section into a single file instead of writing a new dated file each run. When the document folder already contains a file named exactly after the section (e.g. `Greg Weekly.md`), the extracted section is appended to the bottom of it as a new `## <date> <section title>` sub-section, where `<date>` is the source entry's date. Sections with no matching aggregator file keep producing standalone `<date> <section title>.md` files as before; the behaviour is opt-in per section by creating the aggregator file.

## [0.4.0] - 2026-07-30

### Changed

- `collate` now adds a `Contents` table of contents to the top of each `summary.md` linking to the daily entry files and any collated media in the folder, and creates or refreshes a root index file (`index.md` by default) in the entries folder linking to every collation summary, newest first. Media organization runs before the summary is built so freshly collated media is listed. Configurable via the new `file.toc` config block (`enabled`, `summary_title`, `include_entries`, `include_media`, `root_index_enabled`, `root_index_name`, `root_index_title`); enabled by default.

## [0.3.1] - 2026-07-30

### Changed

- Fixed `collate` reverting rewritten media references: the empty-section cleanup pass rewrote each entry from its in-memory tree after the media reference was updated on disk, leaving image links pointing at the pre-move source path (a broken link when the media was moved). The reference rewrite now runs after the cleanup.

## [0.3.0] - 2026-07-10

### Added

- Relative Markdown links are now rewritten when `collate`, `merge`, or `new-entry` rollover relocate a section's content to a file in a different directory, so `[text](path)` and `![alt](path)` links keep resolving to the same target. Anchor links are re-based to cross-file links when their heading stays behind in the source file, and left as-is when the heading moves along with the section. Absolute paths, `~/` home paths, and URLs are left untouched.

### Fixed

- `find_header` in `markdown_file.py` now only counts leading ATX `#`s, so a content line containing an anchor link (e.g. `See [work](#work-done)`) is no longer misparsed as a heading and dropped at parse time.

## [0.2.6] - 2026-07-06

### Changed

- Bumped setuptools to v83

## [0.2.5] - 2026-06-28

### Changed

- Bumped click to v8.4.2

## [0.2.4] - 2026-05-23

### Changed

- Bumped click to v8.4.1

## [0.2.3] - 2026-05-18

### Changed

- Bumped click to v8.4.0

## [0.2.2] - 2026-05-10

### Added
- GitLab Release is now published automatically on each new tag, with release notes pulled from the matching CHANGELOG section
- Renovate MRs now bump CHANGELOG.md alongside VERSION via the shared bump-version template's BUMP_CHANGELOG option

### Changed
- Source tarballs attached to GitLab Releases now contain only the runnable package plus install metadata (`LICENSE.rst`, `pyproject.toml`, `VERSION`); tests, CI configs, Dockerfile, and top-level docs are excluded via `.gitattributes`
