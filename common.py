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




def print_project_version(project, version):
    """
    Prints to the standard output project name and it's version.
    """

    print(u'{} {}'.format(project, version))

# End of print_project_version() function


def print_debug(debug, message):
    """
    Prints 'message' if debug mode is True
    """

    if debug:
        print(u'{}'.format(message))

# End of print_debug() function
