[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/dupgit/versions/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/dupgit/versions/?branch=master)
[![Build Status](https://scrutinizer-ci.com/g/dupgit/versions/badges/build.png?b=master)](https://scrutinizer-ci.com/g/dupgit/versions/build-status/master)
[![Code Coverage](https://scrutinizer-ci.com/g/dupgit/versions/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/dupgit/versions/?branch=master)

# Description

Versions is an open source (GPL v3) software that checks releases and
versions of your favorite programs through RSS or Atom feeds and tells
you which changes.

It implements checking for projects in github.com and freshcode.club.
Projects must be added to a YAML file (named by default
```~/.config/versions/versions.yaml```). One can use ```--file=FILENAME```
option to specify an alternative YAML file.
github projects must be listed under a ```github.com:``` section and
freshcode ones must be listed under a ```freshcode.club:``` section.

Versions uses and produces text files. Those files are cache files
written into ```~/.local/versions``` directory. ```*.cache``` are cache
files containing the project list and their associated version (the latest).
```*.feed``` are information feed cache files containing on each line
the latest parsed post of the feed.


# Usage

```./version.py``` should be enought to bring you the list of updated
programs since last run. To verify each day one can use the following
command in a persistant terminal (tmux, screen…):

    watch -n 86400 ./versions.py


Option ```--list-cache``` prints the content of the local cache (ie
latest known versions).

Option `-f FILENAME` or `--file FILENAME` ease usage of different
YAML configuration files.

Option `-d` or `--debug` runs doctests and prints information about
what's going on in the program.


# Links of interest

* [https://release-monitoring.org/](https://release-monitoring.org/)
* [https://wiki.debian.org/debian/watch](https://wiki.debian.org/debian/watch)
