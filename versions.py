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
should only print those with new release version.

It implements checking for projects in github.com and freshcode.club.
Projects must be added to a YAML file (named by default
~/.config/versions/versions.yaml). One can use --file=FILENAME option
to specify an alternative YAML file.
github projects must be listed under a "github.com:" section and
freshcode ones must be listed under a "freshcode.club:" section.

Versions uses and produces text files. Those files are cache files
written into ~/.local/versions directory. "*.cache" are cache files
containing the project list and their associated version (the latest).
"*.feed" are information feed cache files containing on only one line
the latest parsed post of the feed.
"""


class Conf:
    """
    Class to store configuration of the program
    """

    config_dir = ''
    local_dir = ''
    config_filename = ''
    description = {}
    options = None

    def __init__(self):
        """
        Inits the class
        """
        self.config_dir = os.path.expanduser("~/.config/versions")
        self.local_dir = os.path.expanduser("~/.local/versions")
        config_filename = '' # At this stage we do not know if a filename has been set on the command line
        description = {}
        options = None

        # Make sure that the directories exists
        make_directories(self.config_dir)
        make_directories(self.local_dir)

        self.get_command_line_arguments()

    # End of init() function


    def load_yaml_from_config_file(self, filename):
        """
        Loads definitions from the YAML config file filename
        """

        config_file = open(filename, 'r')

        self.description = yaml.safe_load(config_file)

        config_file.close()

    # End of load_yaml_from_config_file() function


    def get_command_line_arguments(self):
        """
        Defines and gets all the arguments for the command line using
        argparse module. This function is called in the __init__ function
        of this class.
        """

        parser = argparse.ArgumentParser(description='This program checks release and versions of programs through RSS or Atom feeds', version='versions - 0.0.1')

        parser.add_argument('--file', action='store', dest='filename', help='Configuration file with projects to check', default='versions.yaml')

        self.options = parser.parse_args()
        self.config_filename = os.path.join(self.config_dir, self.options.filename)

    # End of get_command_line_arguments() function
# End of Conf class


class FileCache:
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
                print('%s %s' % (project, version))
                self.cache_dict[project] = version

        except KeyError:
            print('%s %s' % (project, version))
            self.cache_dict[project] = version

    # End of update_cache_dict() function
# End of FileCache class


class FeedCache:

    cache_filename = ''
    year = 2016
    month = 05
    day = 01
    hour = 00
    minute = 00

    def __init__(self, local_dir, filename):
        """
        Inits the class. 'local_dir' must be a directory where we want to
        store the cache file named 'filename'
        """

        self.cache_filename = os.path.join(local_dir, filename)
        self.year = 2016
        self.month = 5
        self.day = 1
        self.hour = 0
        self.minute = 0

    # End of __init__() function


    def read_cache_feed(self):
        """
        Reads the cache file which should only contain one date on the
        first line
        """

        if os.path.isfile(self.cache_filename):
            cache_file = open(self.cache_filename, 'r')
            (self.year, self.month, self.day, self.hour, self.minute) = cache_file.readline().strip().split(' ', 4)
            cache_file.close()

    # End of read_cache_feed() function


    def write_cache_feed(self):
        """
        Overwrites the cache file with values stored in this class
        """
        cache_file = open(self.cache_filename, 'w')
        cache_file.truncate(0)
        cache_file.flush()

        cache_file.write('%s %s %s %s %s' % (self.year, self.month, self.day, self.hour, self.minute))

        cache_file.close()

    # End of write_cache_feed() function


    def update_cache_feed(self, date):
        """
        Updates the values stored in the class with the date which should
        be a time.struct_time
        """

        self.year = date.tm_year
        self.month = date.tm_mon
        self.day = date.tm_mday
        self.hour = date.tm_hour
        self.minute = date.tm_min

    # End of update_cache_feed() function


    def is_newer(self, date):
        """
        Tells wether "date" is newer than the one in the cache (returns True
        or not (returns False)
        """

        #print("%d %d" % (date.tm_year, self.year))

        if date.tm_year > self.year:
            return True
        elif date.tm_year == self.year:
            if date.tm_mon > self.month:
                return True
            elif date.tm_mon == self.month:
                if date.tm_mday > self.day:
                    return True
                elif date.tm_mday == self.day:
                    if date.tm_hour > self.hour:
                        return True
                    elif date.tm_hour == self.hour:
                        if date.tm_min > self.minute:
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False

    # End of is_newer() function

# End of FeedCache class


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


def check_versions_for_github_projects(github_project_list, local_dir):
    """
    Checks project's versions on github if any are defined in the yaml
    file under the github.com tag.
    """

    github_cache = FileCache(local_dir, 'github.cache')
    github_cache.read_cache_file()

    for project in github_project_list:

        version = get_latest_github_release(project)
        github_cache.update_cache_dict(project, version)

    github_cache.write_cache_file()

# End of check_versions_for_github_projects() function


def check_versions_for_freshcode(freshcode_project_list, local_dir):
    """
    Checks projects with freshcode web site's RSS
    """


    freshcode_cache = FileCache(local_dir, 'freshcode.cache')
    freshcode_cache.read_cache_file()

    url = 'http://freshcode.club/projects.rss'
    feed = feedparser.parse(url)

    feed_info = FeedCache(local_dir, 'freshcode.feed')
    feed_info.read_cache_feed()

    if len(feed.entries) > 0:

        feed_list = []

        # inserting into a list in reverse order to keep the most recent
        # version in case of multiple release of the same project in the
        # feeds
        for f in feed.entries:
            if feed_info.is_newer(f.published_parsed):
                feed_list.insert(0, f)

        feed_info.update_cache_feed(feed.entries[0].published_parsed)

        for entry in feed_list:
            (project, version) = entry.title.strip().split(' ', 1)

            if project in freshcode_project_list:
                freshcode_cache.update_cache_dict(project, version)

        freshcode_cache.write_cache_file()

    feed_info.write_cache_feed()

# End of check_versions_for_freshcode() function


def main():
    """
    This is the where the program begins
    """

    versions_conf = Conf()  # Configuration options

    if os.path.isfile(versions_conf.config_filename):

        versions_conf.load_yaml_from_config_file(versions_conf.config_filename)

        # Checks projects from github
        check_versions_for_github_projects(versions_conf.description['github.com'], versions_conf.local_dir)

        # Checks projects from freshcode.club
        check_versions_for_freshcode(versions_conf.description['freshcode.club'], versions_conf.local_dir)

    else:
        print('Error: file %s does not exist' % config_filename)

# End of main() function


if __name__=="__main__" :
    main()
