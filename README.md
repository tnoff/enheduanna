# Enheduanna

Note taking command line tool for keeping daily notes. Has tools to rollup daily notes into summaries, grouping different sections together.

Config values allow you to customize default sections within the markdown file.

## Install

Install via pip

```
$ git clone https://github.com/tnoff/enheduanna.git
$ pip install enheduanna/
```

## Basic Usage

Use the cli to create daily note files in markdown and other actiosn such as rolling up a weeks worth of notes into a summary.

## Daily Note File

Run the `enheduanna ready-file` command to create a markdown file for todays notes. This will create the file within a directory named for the current week. You can decide which root "Note Folder" all of these files and dirs are placed into via the config, its nothing is set it will default to the `~/Notes` directory.

The format will look like this:

```
Notes/
  2025-01-20_2025-01_26/
    2025-01-20.md
    2025-01-21.md
  2025-01-27_2025-02-02/
    2025-02-02.md
```

Each file will have default sections given, with a title of todays date:

```
# 2025-02-02

## Work Done

- 

## Meetings

| Time | Meeting Name |
| ---- | ------------ |
| | |

## Follow Ups

- 

## Scratch
```

These sections can be overriden via the config.

### Rollups

Combine a weeks worth of note files into a single `summary.md` file in the same directory using the `enheduanna rollup [directory]` command. The name of the rollup file can be specified via the `-rn` cli option.

Specific "Rollup Sections" are defined to know which Markdown Sections to include in the rollup file. By default the "Work Done" and "Follow Ups" sections are included, but these can be overriden via the config.

For every section you can add in a `regex` and `groupBy` option to have the rollup command group contents. By default, the "Work Done" section groups content lines that have the same "ticket pattern" that matches the `([a-zA-Z]+-[0-9]+)` regex.

For example if you had these lines in different note files

File1
```
## Work Done

- Working on some ticket (ABC-1234)
```

File2
```
## Work Done

- Working on that same ticket, had more issues (ABC-1234)
```

In the rollup file, the cli will group these lines together

```
## Work Done

- Working on some ticket (ABC-1234)
- Working on that same ticket, had more issues (ABC-1234)
```

## Config File

The config is a YAML config that allows for environment variable options through [pyaml-env](https://github.com/mkaranasou/pyaml_env).
By default the cli will look for the config file at `~/.enheduanna.yml`, and this can be overriden with the cli `-c` option.

## Config Options

The various config options.

### Date Format

Set the date format in the config file or via the `-df` cli option. The date format will determine the paths of the directories and the note files, as well as the default title of each note file.

Should be in the standard [python datetime format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

Example config:

```
---
date_format: %Y-%m-%d
```

### Note Folder

Override the note folder all weekly directories are placed in. Can be overriden via the cli with the `-nf` cli option.

Example Config

```
---
note_folder: /home/user/Notes
```

### Sections

The default sections for the daily note markdown files. Each "MarkdownSecion" should have the three following params:

- title # Title of section
- contents # Placeholder contents of secion
- level # Level of section, how many `#` chars are added before the title

The config can take a list of these, they will be added to the file in order. Note that these will override all of the existing defaults.

Example config:

```
---
sections:
  - title: Work Done
    contents: "- "
    level: 2
  - title: Meetings
    contents: " Time | Meeting Name |\n| ---- | ------------ |\n| | |"
    level: 2
  - title: Follow Ups
    contents: "- Follow Ups"
    level: 2
  - title: Scratch
    contents: "- "
    level: 2
```

## Rollup Sections

Rollup sections that determine which sections are combined together during the `rollup` command. A better summary is above, but you can set `regex` and `groupBy` options to group common bits of content in the sections.

Only the `title` is required, the `regex` and `groupBy` are optional.

Example config:

```
---
rollup_sections:
  - title: Work Done
    regex: "\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)"
    groupBy: ticket
  - title: Follow Ups
```