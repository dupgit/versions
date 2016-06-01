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
import os
import errno

__author__ = "Olivier Delhomme <olivier.delhomme@free.fr>"
__date__ = "01.06.2016"
__version__ = "0.0.1"

"""
This program checks projects versions throught RSS and Atom feeds and
should only print those with new realease version
"""


class Conf:
    """
    Class to store configuration of the program
    """

    config_dir = ''
    local_dir = ''
    config_filename = ''
    description = {}

    def __init__(self):
        """
        Inits the class
        """
        self.config_dir = os.path.expanduser("~/.config/versions")
        self.local_dir = os.path.expanduser("~/.local/versions")
        config_filename = '' # At this stage we do not know if a filename has been set on the command line
        description = {}

        # Make sure that the directories exists
        make_directories(self.config_dir)
        make_directories(self.local_dir)

    # End of init() function


    def load_yaml_from_config_file(self, filename):
        """
        Loads definitions from the YAML config file filename
        """

        config_file = open(filename, 'r')

        self.description = yaml.safe_load(config_file)

        config_file.close()

    # End of load_yaml_from_config_file() function

# End of Conf class


class Cache:
    """
    This class should help in managing cache files
    """

    cache_filename = ''
    cache_dict = {}  # Dictionnary of projects and their associated version

    def __init__(self, local_dir, filename):
        """
        Inits the class. 'local_dir' must be a directory where we want to
        store the cache file named 'filename'
        """

        self.cache_filename = os.path.join(local_dir, filename)
        self.cache_dict = {}

    # End of __init__() function


    def read_cache_file(self):
        """
        Reads the cache file and puts it into a dictionnary of project with
        their associated version
        """

        if os.path.isfile(self.cache_filename):

            cache_file = open(self.cache_filename, 'r')

            for line in cache_file:

                line = line.strip()

                if line.count(' ') > 0:
                    (project, version) = line.split(' ', 1)

                elif line != '':
                    project = line
                    version = ''

                self.cache_dict[project] = version

            cache_file.close()

        # End of read_cache_file() function


    def write_cache_file(self):
        """
        Owerwrites dictionnary cache to the cache file
        """

        cache_file = open(self.cache_filename, 'w')
        cache_file.truncate(0)
        cache_file.flush()

        for (project, version) in self.cache_dict.iteritems():
            cache_file.write('%s %s\n' % (project, version))

        cache_file.close()

    # End of write_cache_file() function


    def update_cache_dict(self, project, version):
        """
        Updates cache dictionnary if needed
        """

        try:
            version_cache = self.cache_dict[project]

            if version != version_cache:
                print('%s %s' % (project, version_cache))
                self.cache_dict[project] = version_cache

        except KeyError:
            print('%s %s' % (project, version))
            self.cache_dict[project] = version

# End of Cache class


def make_directories(path):
    """
    Makes all directories in path if possible. It is not an error if
    path already exists
    """

    try:
        os.makedirs(path)

    except OSError as exc:

        if exc.errno != errno.EEXIST or os.path.isdir(path) != True:
            raise

# End of make_directories() function


def get_command_line_arguments():
    """
    Defines and gets all the arguments for the command line using
    argparse module
    """

    parser = argparse.ArgumentParser(description='This program checks release and versions of programs through RSS or Atom feeds', version='versions - 0.0.1')

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


def check_versions_for_github_projects(versions_conf):
    """
    Checks project's versions on github if any are defined in the yaml
    file under the github.com tag.
    """

    github_project_list = versions_conf.description['github.com']

    github_cache = Cache(versions_conf.local_dir, 'github.cache')
    github_cache.read_cache_file()

    for project in github_project_list:

        version = get_latest_github_release(project)
        github_cache.update_cache_dict(project, version)

    github_cache.write_cache_file()

# End of check_versions_for_github_projects() function


def main():
    """
    This is the where the program begins
    """

    versions_conf = Conf()  # Configuration options
    options = get_command_line_arguments()
    config_filename = os.path.join(versions_conf.config_dir, options.filename)

    if os.path.isfile(config_filename):

        versions_conf.load_yaml_from_config_file(config_filename)
        check_versions_for_github_projects(versions_conf)

    else:
        print('Error: file %s does not exist' % config_filename)

# End of main() function


if __name__=="__main__" :
    main()
