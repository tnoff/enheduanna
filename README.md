# Enheduanna

Note taking command line tool for keeping daily, weekly, and quarterly notes.

## Config File

The config is a YAML config that allows for environment variable options through [pyaml-env](https://github.com/mkaranasou/pyaml_env).

Allow options are as follows

```
---
date_format: '%Y-%m-%d' # Datetime format used in folders and files
note_folder: '/home/user/Notes' # Default folder for notes
```

## Folder Format

Creates folders for every week, with the name of the start date and the end date. It will create a generic markdown file 

The format will look like this:

```
Notes/
  2025-01-20_2025-01_26/
    2025-01-20.md
    2025-01-21.md
  2025-01-27_2025-02-02/
    2025-02-02.md
```

## Daily File Contents

The cli will make a markdown file for the days notes in the following format:

```
# <todays-date-formatted>

## Work Done

## Meetings

| Time | Meeting Name |
| ---- | ------------ |
| | |

## Follow Ups

## Scratch

```

These options can be overriden using the `sections` config, which can be given the a list of dictionaries containing the `title` and `contents` keys.

For example with the following config:

```
---
sections:
  - title: Customer Notes
    contents: Various Customer Notes
```

You will get a file with the following format:

```
# <todays-date-formatted>

## Customer Notes

Various Customer Notes
```