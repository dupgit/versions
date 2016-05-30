#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  versions.py : checks release and versions of programs through RSS
#                or Atom feeds and tells you
#
#  (C) Copyright 2016 Olivier Delhomme
#  e-mail : olivier.delhomme@free.fr
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
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

import feedparser
import yaml
import argparse


def define_command_line_arguments():
    """
    Defines all the arguments for the command line using argparse module
    """

    parser = argparse.ArgumentParser(description='This program checks release and versions of programs through RSS or Atom feeds')
    parser.add_argument('--file', action='store', dest='filename', help='Configuration file with projects to check', default='versions.yaml')

    options = parser.parse_args()

    return options

# End of define_command_line_arguments() function


def get_latest_github_release(program):
    """
    Gets the latest release of a program on github. program must be a
    string of the form user/repository
    """

    version = ''
    url = 'https://github.com/' + program + '/releases.atom'
    feed = feedparser.parse(url)


    if len(feed.entries) > 0:
        version = feed.entries[0].title

    return version

# End of get_latest_github_release() function


def load_yaml_from_config_file(filename):
    """
    Loads definitions from the YAML config file
    """

    config_file = open(filename, 'r')

    description = yaml.safe_load(config_file)

    config_file.close()

    return description

# End of load_yaml_from_config_file() function



def main():
    """
    This is the where the program begins
    """

    options = define_command_line_arguments()

    description = load_yaml_from_config_file(options.filename)

    github_project_list = description['github.com']

    for project in github_project_list:
        version = get_latest_github_release(project)

        if version != '':
            print('%s %s' % (project, version))

# End of main() function


if __name__=="__main__" :
    main()
