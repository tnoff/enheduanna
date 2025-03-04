# Enheduanna

Command line tool for creating daily note files in Markdown. Organizes the daily notes into weekly directories, and has functions to "rollup" into weekly summaries and create additional "documentation" files from these notes.

Useful for keeping track of work done throughout the week, tracking follow up items, and starting proper documentation from your notes. In particular helps with keeping track of your work throughout the year/quarter for when you do self-reviews or need to update your resume.

Named after [Enheduanna](https://en.wikipedia.org/wiki/Enheduanna), sometimes considered the first known author in history.

## Install

Install via pip

```
$ git clone https://github.com/tnoff/enheduanna.git
$ pip install enheduanna/
```

## Basic Usage

Comes with two commands to start:

- `enheduanna ready-file` Creates the daily note file for today
- `enheduanna rollup` Rolls up the daily notes into weekly summaries and other documentation.

Run `enheduanna --help` to see all options.

## Daily Note File

The `ready-file` command will create a markdown file for today's notes. The note file will be named for the current day, such as `2025-01-21.md`. The file will be placed in a directory named for the current week. 


The format will look like this:

```
Notes/
  2025-01-20_2025-01_26/
    2025-01-20.md
    2025-01-21.md
    2025-01-22.md
    2025-01-23.md
```

The date format used in the file names can be overridden, as well as the note folder location.

Each file will have default sections given, with a title of today's date:

```
# 2025-01-23

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

These default sections for the daily files can be overridden via the config.


### Carryover Sections

By default the `Follow Ups` section is set is a "carryover section". This means that enheduanna will find the most recent existing daily note file, find the section within that file, and "carry it over" to the new file. The contents of the section in the older file will be removed and automatically added into the new daily note file.


For example, if you have the following files, with `2025-01-23.md` being the most recent file:

```
Notes/
  2025-01-20_2025-01_26/
    2025-01-20.md
    2025-01-21.md
    2025-01-22.md
    2025-01-23.md
```

And the `2025-01-23.md` file contains a `Follow Ups` section:

2025-01-23.md
```
# 2025-01-23

## Follow Ups

- Need to follow up with product about the new feature
```

When you run the `ready-file` the next day (or any later date), a new file is created, it will have the following contents:

```
# 2025-01-24

## Work Done

- 

## Meetings

| Time | Meeting Name |
| ---- | ------------ |
| | |

## Follow Ups

- Need to follow up with product about the new feature

## Scratch
```

The contents of the `2025-01-23.md` file will also be updated to remove the `Follow Ups` section.


## Rollups

Use the `rollup` command against a weekly note directory to roll up all of the daily note files in that directory into a `summary.md` file in that same directory.

By default the `Work Done` section will be combined together and placed into the new `summary.md` file.

The contents of the combined sections can also be grouped together by a regex to make it easier to edit later. By default the `Work Done` section is grouped together by a regex which looks for Jira ticket numbers within parenthesis, such as `(ABC-1234)`.

If no regex grouping options are given, the contents will be placed into the rolled up sections in the order they are read.

For example if you had these lines in different note files:

2025-01-20.md
```
## Work Done

- Working on some ticket (ABC-1234)
- Fixing that one bug that's been bugging me forever (XYZ-2345)
```

2025-01-21.md
```
## Work Done

- Working on that same ticket, had more issues (ABC-1234)
```

After running the `rollup` command, the `summary.md` file will include:

summary.md
```
## Work Done

- Working on some ticket (ABC-1234)
- Working on that same ticket, had more issues (ABC-1234)
- Fixing that one bug that's been bugging me forever (XYZ-2345)
```

### Document Rollup

Additionally set a "Document" directory to pull out write ups you've placed in the daily notes. The idea here is that one-off sections that are not part of the normal section process can be removed and moved to the Document section, as a way of prototyping documentation bits such as runbooks. By default the new documents will be placed in the `~/Documents` directory.

For example if you have the following daily file:

2025-01-20.md
```
## Work Done

- Working on some ticket (ABC-1234)
- Fixing that one bug that's been bugging me forever (XYZ-2345)

## Steps to Reboot Servers

Run these commands
ssh ubuntu@foo.com
sudo reboot
```

The `rollup` command will create a new file named `2025-01-20 Steps to Reboot Servers.md` in the document directory with the following contents:

```
## 2025-01-20 Steps to Reboot Servers

Run these commands
ssh ubuntu@foo.com
sudo reboot
```

The contents of the section that was moved will also be removed from the original notes file, in this case `2025-01-20.md`.

## Config File

The config is a YAML config that allows for environment variable options through [pyaml-env](https://github.com/mkaranasou/pyaml_env).
By default the cli will look for the config file at `~/.enheduanna.yml`, and this can be overridden with the cli `-c` option.

## Config Options

The various config options.

### Date Format

Set the date format in the config file. The date format will determine the paths of the directories and the note files, as well as the default title of each note file.

Should be in the standard [python datetime format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

Example config:

```
---
file:
  date_format: %Y-%m-%d
```

### Note Directory

Override the note directory all weekly directories are placed in.

Example Config

```
---
file:
  note_directory: /home/user/Notes
```

### Document Directory

Override the document directory where rollup docs are placed in.

Example Config

```
---
file:
  document_directory: /home/user/Documents
```

### Daily Sections

The default sections for the daily note markdown files. Each "MarkdownSection" should have the following params:

| Param | Type | Description | 
| ----- | ---- | ----------- |
| title | str | Title of section |
| contents | str | Placeholder contents of section |
| level | int | Level of section, meaning how many `#`'s are placed before the title
| carryover | boolean | If the contents of the previous daily note folder should be carried over | 


The config can take a list of these, they will be added to the file in order. Note that these will override all of the existing defaults.

Example config:

```
---
file:
  daily_sections:
    - title: Work Done
      contents: "- "
      level: 2
    - title: Meetings
      contents: " Time | Meeting Name |\n| ---- | ------------ |\n| | |"
      level: 2
    - title: Follow Ups
      contents: "- Follow Ups"
      level: 2
      carryover: true
    - title: Scratch
      contents: "- "
      level: 2
```

### Rollup Sections

Rollup sections that determine which sections are combined together during the `rollup` command. A better summary is above, but you can set `regex` and `groupBy` options to group common bits of content in the sections.

Only the `title` is required, the `regex` and `groupBy` are optional. You can also override the `level` that is combined, meaning the section level of the rollup section, by default this is set to 2.

Example config:

```
---
file:
  rollup_sections:
    - title: Work Done
      level: 2
      regex: "\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)"
      groupBy: ticket
```