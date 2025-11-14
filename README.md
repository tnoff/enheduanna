# Enheduanna

Command line tool for creating entries in Markdown. Organizes entries into sub-directories, and has functions to "collate" multiple entries into summaries and create additional "documentation" files from these notes.

Useful for keeping track of work done throughout the week, tracking follow up items, and starting proper documentation from your notes. In particular helps with keeping track of your work throughout the year/quarter for when you do self-reviews or need to update your resume.

Named after [Enheduanna](https://en.wikipedia.org/wiki/Enheduanna), sometimes considered the first known author in history.

## Install

Install via pip

```
$ git clone https://github.com/tnoff/enheduanna.git
$ pip install enheduanna/
```

## Docker Usage

If you have trouble setting up Python environments, you can use Docker:

### Build the Docker image

```bash
$ git clone https://github.com/tnoff/enheduanna.git
$ cd enheduanna
$ docker build -t enheduanna .
```

### Run commands with Docker

The Docker container comes with a default configuration that uses `/notes` and `/documents` as the base directories. Mount your local directories to these paths:

```bash
# Run new-entry command (creates today's note)
$ docker run --rm \
  -v ~/Notes:/notes \
  enheduanna new-entry

# Run collate command on a specific week
$ docker run --rm \
  -v ~/Notes:/notes \
  -v ~/Documents:/documents \
  enheduanna collate /notes/2025-01-20_2025-01-26

# Run merge command
$ docker run --rm \
  -v ~/Documents:/documents \
  enheduanna merge /documents /documents/combined-runbook.md
```

### Using a custom config file

If you need custom settings, mount your config file and specify it:

```bash
$ docker run --rm \
  -v ~/Notes:/notes \
  -v ~/.enheduanna.yml:/config/.enheduanna.yml \
  enheduanna -c /config/.enheduanna.yml new-entry
```

**Note**: When using a custom config with Docker, paths should reference the container's mounted paths (e.g., `/notes` instead of `~/Notes`).

## Basic Usage

Comes with three commands to start:

- `enheduanna new-entry` Creates the entry file for today
- `enheduanna collate` Collates entries into summaries and other documentation
- `enheduanna merge` Merges multiple markdown files into a single file

Run `enheduanna --help` to see all options.

## Entry Files

The `new-entry` command will create a markdown entry file for today. The entry file will be named for the current day, such as `2025-01-21.md`. By default, the file will be placed in a sub-directory for the current week, but this can be configured to be a sub-directory for the entire month. 

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

Each entry file will have default sections given, with a title of today's date:

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

These default sections for the entry files can be overridden via the config.


### Rollover Sections

By default the `Follow Ups` section is set is a "rollover section". This means that enheduanna will find the most recent existing entry file, find the section within that file, and "roll it over" to the new file. The contents of the section in the older file will be removed and automatically added into the new entry file.


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

When you run the `new-entry` the next day (or any later date), a new file is created, it will have the following contents:

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


## Collation

Use the `collate` command against a note directory to collate all of the entry files in that directory into a `summary.md` file in that same directory.

By default the `Work Done` section will be combined together and placed into the new `summary.md` file.

The contents of the combined sections can also be grouped together by a regex to make it easier to edit later. By default the `Work Done` section is grouped together by a regex which looks for Jira ticket numbers within parenthesis, such as `(ABC-1234)`.

If no regex grouping options are given, the contents will be placed into the collated sections in the order they are read.

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

After running the `collate` command, the `summary.md` file will include:

summary.md
```
## Work Done

- Working on some ticket (ABC-1234)
- Working on that same ticket, had more issues (ABC-1234)
- Fixing that one bug that's been bugging me forever (XYZ-2345)
```

### Document Collation

Additionally set a "Document" directory to pull out write ups you've placed in your entries. The idea here is that one-off sections that are not part of the normal section process can be removed and moved to the Document section, as a way of prototyping documentation bits such as runbooks. By default the new documents will be placed in the `~/Documents` directory.

For example if you have the following entry:

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

The `collate` command will create a new file named `2025-01-20 Steps to Reboot Servers.md` in the document directory with the following contents:

```
## 2025-01-20 Steps to Reboot Servers

Run these commands
ssh ubuntu@foo.com
sudo reboot
```

The contents of the section that was moved will also be removed from the original notes file, in this case `2025-01-20.md`.

## Merge

Use the `merge` command to combine all markdown files from a directory into a single markdown file. Unlike `collate`, the merge command:

- Combines **all** sections from all files (doesn't use collate section configuration)
- Preserves each file as a separate section with subsections increased by 1 level
- Does not apply regex grouping or content reorganization
- Does not extract separate documentation files

Most useful as a utility to combine various documentation files. A common workflow is to use `collate` to extract documentation sections from entries, then use `merge` to combine related documentation files into comprehensive runbooks.

Each input file becomes a level 2 section (##) in the merged document, with all its subsections increased by one level (e.g., ## becomes ###).

**Usage:**

```bash
enheduanna merge <directory> <output_file>

# Example: Combine documentation files
enheduanna merge ~/Documents ~/Documents/complete-runbook.md

# Example: Merge project notes
enheduanna merge ~/Notes/Project_Prometheus_Notes ~/prometheus-notes.md

# With custom title
enheduanna merge ~/Documents ~/Documents/deploy-guide.md -t "Complete Deployment Guide"
```

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

### Entries Directory

Override the entries directory where all parent directories are placed.

Example Config

```
---
file:
  entries_directory: /home/user/Notes
```

### Document Directory

Override the document directory where collation docs are placed in.

Example Config

```
---
file:
  document_directory: /home/user/Documents
```

### Entry Sections

The default sections for the entry markdown files. Each "MarkdownSection" should have the following params:

| Param | Type | Description | 
| ----- | ---- | ----------- |
| title | str | Title of section |
| contents | str | Placeholder contents of section |
| level | int | Level of section, meaning how many `#`'s are placed before the title
| rollover | boolean | If the contents of the previous entry should be rolled over | 


The config can take a list of these, they will be added to the file in order. Note that these will override all of the existing defaults.

Example config:

```
---
file:
  entry_sections:
    - title: Work Done
      contents: "- "
      level: 2
    - title: Meetings
      contents: " Time | Meeting Name |\n| ---- | ------------ |\n| | |"
      level: 2
    - title: Follow Ups
      contents: "- Follow Ups"
      level: 2
      rollover: true
    - title: Scratch
      contents: "- "
      level: 2
```

### Collate Sections

Collate sections that determine which sections are combined together during the `collate` command. A better summary is above, but you can set `regex` and `groupBy` options to group common bits of content in the sections.

Only the `title` is required, the `regex` and `groupBy` are optional. You can also override the `level` that is combined, meaning the section level of the collate section, by default this is set to 2.

Example config:

```
---
file:
  collate_sections:
    - title: Work Done
      level: 2
      regex: "\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)"
      groupBy: ticket
```

### Collation Settings

You can configure whether you want the sub-directories created to be on a per week or per month basis. The accepted values here are `weekly` and `monthly`.

```
collation:
  type: monthly
```
