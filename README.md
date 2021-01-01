# python-rsync

A python utility for keeping 2 locations in sync.

## Features

Suported location types

| Type           | Supported |
| -------------- | --------- |
| Filesystem     | ✔️        |
| Zip filesystem | ✔️        |
| FTP            | ✔️        |

The script runs continuously and keeps the two locations in sync. More exactly:

- If a file is created in one location, the file is duplicated in the other location as well
- If a file is deleted from one location, it is also deleted from the other location
- If a file is modified from one location, the change is copied to the other shred.
  At the initial planting, the synchronization is done as follows.
- If a file exists only on one location - it is copied to the other location
- If the same file exists in both locations, but there are differences, copy the newest one
  file (depending on the time it was modified) from one location to the other.

## Installation

Git clone this repository

```
$ cd ./python-rsync
```

## Usage

The script needs to receive 2 locations defined as:
<LOCATION_TYPE>:<LOCATION_PATH>

| Type           | Definition syntax                               |
| -------------- | ----------------------------------------------- |
| Filesystem     | `folder:<path>`                                 |
| Zip filesystem | `zip:<zip path>`                                |
| FTP            | `ftp:<username>:<password>@<host><remote path>` |

Example

```
$ python3 main.py ftp:my_user:1234@127.0.0.1/folder zip:C:\aaa
```

## Project structure

```
├── main.py - Python entry file
├── monitors - Directory containing available monitor types
│   ├── Filesystem.py
│   ├── Ftp.py
│   └── Zip.py
├── StateManager.py - A utility class that handles state changes
├── Syncer.py - Manages the changes that are broadcasted by the monitors
└── utils.py - Miscellaneous helper functions
```

##### More examples of commands

```
python3 advanced_rsync.py folder:./test/a/ ftp:alex:1324@localhost/home/alex/Desktop/python-rsync/test/b/
python3 advanced_rsync.py zip:./test/a/file.zip ftp:alex:1324@localhost/home/alex/Desktop/python-rsync/test/b/
python3 advanced_rsync.py folder:./test/a/ folder:./test/b/
```
