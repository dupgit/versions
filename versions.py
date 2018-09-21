#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  versions.py : checks releases and versions of programs through RSS
#                or Atom feeds and tells you
#
#  (C) Copyright 2016 - 2018 Olivier Delhomme
#  e-mail : olivier.delhomme@free.fr
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
import codecs
import sys
import locale
import argparse
import os
import re
import errno
import time
import doctest
import feedparser
import yaml
import operator
import configuration
import caches
import common

"""
This program checks projects versions through RSS and Atom feeds and
should only print those with new release version.

It implements checking for projects in github.com and freshcode.club.
Projects must be added to a YAML file (named by default
~/.config/versions/versions.yaml). One can use --file=FILENAME option
to specify an alternative YAML file. version.yaml is included as an
example in this project.

Versions uses and produces text files. Those files are cache files
written into ~/.local/versions directory. "*.cache" are cache files
containing the project list and their associated version (the latest).
"*.feed" are information feed cache files containing on only one line
the latest parsed post of the feed.
"""






def main():
    """
    This is the where the program begins
    """

    if sys.version_info[0] == 2:
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

    versions_conf = configuration.Conf()  # Configuration options

    if versions_conf.options.debug:
        doctest.testmod(verbose=True)

    if os.path.isfile(versions_conf.config_filename):
        versions_conf.print_cache_or_check_versions()

    else:
        print(u'Error: file {} does not exist'.format(versions_conf.config_filename))

# End of main() function


if __name__ == "__main__":
    main()
