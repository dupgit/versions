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
written into ```~/.local/versions directory```. ```*.cache``` are cache
files containing the project list and their associated version (the latest).
```*.feed``` are information feed cache files containing on only one line
the latest parsed post of the feed.

# Links of interest

* [https://release-monitoring.org/](https://release-monitoring.org/)
* [https://wiki.debian.org/debian/watch](https://wiki.debian.org/debian/watch)
