[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/dupgit/versions/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/dupgit/versions/?branch=master)
[![Build Status](https://scrutinizer-ci.com/g/dupgit/versions/badges/build.png?b=master)](https://scrutinizer-ci.com/g/dupgit/versions/build-status/master)
[![Code Coverage](https://scrutinizer-ci.com/g/dupgit/versions/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/dupgit/versions/?branch=master)

# Description

Versions is an open source (GPL v3) software that checks releases and
versions of your favorite programs through RSS or Atom feeds and tells
you which one has been released since last check.

It can check projects from :
* github.com
* sourceforge.net
* freshcode.club
* pypi.python.org
* savanah.gnu.org
* www.freshports.org (FreeBSD packages)
* fossies.org
* repo.continuum.io

Projects must be added to a YAML file (named by default
`~/.config/versions/versions.yaml`). One can use `--file=FILENAME`
option to specify an alternative YAML file. The structure of this
YAML file is explained below.

Versions uses and produces text files. Those files are cache files
written into `~/.local/versions` directory. `*.cache` are cache
files containing the project list and their associated version (the latest).
`*.feed` are information feed cache files containing on each line
the latest parsed post of the feed.


# YAML file structure

```
sitename:
  url: "https://the.url/to/theglobalfeed"
  type: list
  projects:
    - list
    - of
    - projects

othersitename:
  url: "https://by.projects.site/{}.atom"
  type: byproject
  projects:
    - list
    - name: of
      regex: '([\d.]+)'
      entry: last checked
    - projects
```

There is two types of sites : 
    
* 'list': The site has one feed with all projects in it such as
   freshcode.club or fossies.org
* 'byproject": The site gives access to one feed per project.
   brackets '{}' represents the name of the project as found in
   the 'project' list. Those projects can be listed directly or
   can take options. In the later case you have to name the
   project and then you can specify either a regex or an entry
   type option: regex is used to determine version number and
   entry is used to determine if versions has to print the latest
   entry (default behavior) or all entries from the "last checked"
   time.


# Installation

In pypi the project is named program_versions but is still invoked
by the command `versions`.


# Usage

`./version.py` should be enough to bring you the list of updated
programs since last run. To verify each day one can use the following
command in a persistant terminal (tmux, screen…):

    watch -n 86400 ./versions.py


Option `-l` or `--list-cache` prints the content of the local cache (ie
latest known versions).

Option `-f FILENAME` or `--file FILENAME` ease usage of different
YAML configuration files.

Option `-d` or `--debug` runs doctests and prints information about
what's going on in the program.


# Links of interest

* [https://release-monitoring.org/](https://release-monitoring.org/)
* [https://wiki.debian.org/debian/watch](https://wiki.debian.org/debian/watch)
* [http://semver.org/](http://semver.org/)
