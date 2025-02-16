# Enheduanna

Command line tool for creating daily note Markdown files. Organizes the daily note files into weekly directories, and has functions for "Rolling Up" the notes into weekly summaries.

Useful for staying on top of current projects, follow up items, and how many meetings you've had in a given week. Also useful for keeping track of work you've done in the past for yearly self-reviews and rsume updating.

## Install

Install via pip

```
$ git clone https://github.com/tnoff/enheduanna.git
$ pip install enheduanna/
```

## Basic Usage

Basic cli usage.

## Daily Note File

The `ready-file` command wll create a markdown file for todays notes. The note file will be named for the current day, such as `2025-01-21.md`. The file will be placed in a directory named for the current week. 


The format will look like this:

```
Notes/
  2025-01-20_2025-01_26/
    2025-01-20.md
    2025-01-21.md
    2025-01-22.md
    2025-01-23.md
```

The date format used in the file names can be overriden, as well as the note folder location.

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

Use the `rollup` command against a weekly note directory to roll up all of the daily note files in that directory into a `summary.md` file in that same directory.

By default the `Work Done` and `Follow Ups` sections will be combined together and placed into the new `summary.md` file.

The contents of the rolled up sections can also be grouped together to make it easier to edit later, by default the `Work Done` section is grouped together by a regex which looks for jira ticket numbers within parenthesis, such as `(ABC-1234)`.

If no regex grouping options are given, the contents will be placed into the rolled up sections in the order they are read.


For example if you had these lines in different note files:

2025-01-20.md
```
## Work Done

- Working on some ticket (ABC-1234)
- Fixing that one bug thats been bugging me forever (XYZ-2345)

## Follow Ups

- Message back my boss about that customer commit
```

2025-01-21.md
```
## Work Done

- Working on that same ticket, had more issues (ABC-1234)

## Follow Ups

- Watch that training video
```

After running the `rollup` command, the `summary.md` file will include:

summary.md
```
## Work Done

- Working on some ticket (ABC-1234)
- Working on that same ticket, had more issues (ABC-1234)
- Fixing that one bug thats been bugging me forever (XYZ-2345)

## Follow Ups

- Message back my boss about that customer commit
- Watch that training video
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