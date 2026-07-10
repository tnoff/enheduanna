# Changelog

All notable changes to enheduanna will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
