#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  versions.py : checks releases and versions of programs through RSS
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
import codecs
import feedparser
import yaml
import argparse
import os
import errno
import time
import doctest


__author__ = "Olivier Delhomme <olivier.delhomme@free.fr>"
__date__ = "16.04.2017"
__version__ = "0.0.4"

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
        self.config_filename = ''  # At this stage we do not know if a filename has been set on the command line
        self.description = {}
        self.options = None

        # Make sure that the directories exists
        make_directories(self.config_dir)
        make_directories(self.local_dir)

        self._get_command_line_arguments()

    # End of init() function


    def load_yaml_from_config_file(self, filename):
        """
        Loads definitions from the YAML config file filename
        """

        config_file = codecs.open(filename, 'r', encoding='utf-8')

        self.description = yaml.safe_load(config_file)

        config_file.close()

    # End of load_yaml_from_config_file() function


    def _get_command_line_arguments(self):
        """
        Defines and gets all the arguments for the command line using
        argparse module. This function is called in the __init__ function
        of this class.
        """
        str_version = 'versions.py - %s' % __version__

        parser = argparse.ArgumentParser(description='This program checks releases and versions of programs through RSS or Atom feeds', version=str_version)

        parser.add_argument('-f', '--file', action='store', dest='filename', help='Configuration file with projects to check', default='versions.yaml')
        parser.add_argument('-l', '--list-cache', action='store_true', dest='list_cache', help='Lists all projects and their version in cache', default=False)
        parser.add_argument('-d', '--debug', action='store_true', dest='debug', help='Starts in debug mode and prints things that may help', default=False)

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
        self._read_cache_file()

    # End of __init__() function


    def _return_project_and_version_from_line(self, line):
        """
        Splits the line into a project and a version if possible (the line
        must contain a whitespace.
        """

        line = line.strip()

        if line.count(' ') > 0:
            (project, version) = line.split(' ', 1)

        elif line != '':
            project = line
            version = ''

        return (project, version)

    # End of _return_project_and_version_from_line() function


    def _read_cache_file(self):
        """
        Reads the cache file and puts it into a dictionnary of project with
        their associated version
        """

        if os.path.isfile(self.cache_filename):
            cache_file = codecs.open(self.cache_filename, 'r', encoding='utf-8')

            for line in cache_file:
                (project, version) = self._return_project_and_version_from_line(line)
                self.cache_dict[project] = version

            cache_file.close()

    # End of _read_cache_file() function


    def write_cache_file(self):
        """
        Owerwrites dictionnary cache to the cache file
        """

        cache_file = open_and_truncate_file(self.cache_filename)

        for (project, version) in self.cache_dict.iteritems():
            cache_file.write('%s %s\n' % (project, version))

        cache_file.close()

    # End of write_cache_file() function


    def update_cache_dict(self, project, version, debug):
        """
        Updates cache dictionnary if needed
        """

        try:
            version_cache = self.cache_dict[project]
            print_debug(debug, u'\t\tIn cache: {}'.format(version_cache))

            if version != version_cache:
                print('%s %s' % (project, version))
                self.cache_dict[project] = version

        except KeyError:
            print('%s %s' % (project, version))
            self.cache_dict[project] = version

    # End of update_cache_dict() function


    def print_cache_dict(self, sitename):
        """
        Pretty prints the cache dictionary as it is recorded in the files.
        """

        print('%s:' % sitename)

        # Gets project and version tuple sorted by project lowered while sorting
        for project, version in sorted(self.cache_dict.iteritems(), key=lambda proj: proj[0].lower()):
            print('\t%s %s' % (project, version))

        print('')

    # End of print_cache_dict() function
# End of FileCache class


class FeedCache:

    cache_filename = ''
    year = 2016
    month = 05
    day = 1
    hour = 0
    minute = 0
    date_minutes = 0


    def __init__(self, local_dir, filename):
        """
        Inits the class. 'local_dir' must be a directory where we want to
        store the cache file named 'filename'
        """

        self.cache_filename = os.path.join(local_dir, filename)
        self.read_cache_feed()

    # End of __init__() function


    def read_cache_feed(self):
        """
        Reads the cache file which should only contain one date on the
        first line
        """

        if os.path.isfile(self.cache_filename):
            cache_file = codecs.open(self.cache_filename, 'r', encoding='utf-8')
            (self.year, self.month, self.day, self.hour, self.minute) = cache_file.readline().strip().split(' ', 4)
            self.date_minutes = self._calculate_minutes(int(self.year), int(self.month), int(self.day), int(self.hour), int(self.minute))
            cache_file.close()

    # End of read_cache_feed() function


    def write_cache_feed(self):
        """
        Overwrites the cache file with values stored in this class
        """
        cache_file = open_and_truncate_file(self.cache_filename)

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
        self.date_minutes = self._calculate_minutes_from_date(date)

    # End of update_cache_feed() function


    def _calculate_minutes(self, year, mon, day, hour, mins):
        """
        Calculate a number of minutes with all parameters and returns
        this.
        >>> fc = FeedCache('localdir','filename')
        >>> fc._calculate_minutes(2016, 5, 1, 0, 0)
        1059827040
        """

        minutes = (year * 365 * 24 * 60) + \
                  (mon * 30 * 24 * 60) + \
                  (day * 24 * 60) + \
                  (hour * 60) + \
                  (mins)

        return minutes

    # End of _calculate_minutes() function


    def _calculate_minutes_from_date(self, date):
        """
        Transforms a date in a number of minutes to ease comparisons
        and returns this number of minutes
        """

        return self._calculate_minutes(date.tm_year, date.tm_mon, date.tm_mday, date.tm_hour, date.tm_min)

    # End of _calculate_minutes() function


    def is_newer(self, date):
        """
        Tells wether "date" is newer than the one in the cache (returns True
        or not (returns False)
        """

        minutes = self._calculate_minutes_from_date(date)

        if minutes > self.date_minutes:
            return True

        else:
            return False

    # End of is_newer() function
# End of FeedCache class


######## Below are some utility functions used by classes above ########

def make_directories(path):
    """
    Makes all directories in path if possible. It is not an error if
    path already exists.
    """

    try:
        os.makedirs(path)

    except OSError as exc:

        if exc.errno != errno.EEXIST or os.path.isdir(path) != True:
            raise

# End of make_directories() function


def open_and_truncate_file(filename):
    """
    Opens filename for writing truncating it to a zero length file
    and returns a python file object.
    """

    cache_file = codecs.open(filename, 'w', encoding='utf-8')
    cache_file.truncate(0)
    cache_file.flush()

    return cache_file

# End of open_and_truncate_file() function
####################### End of utility functions #######################


def get_latest_github_release(program, debug):
    """
    Gets the latest release of a program on github. program must be a
    string of the form user/repository.
    """

    version = ''
    url = 'https://github.com/' + program + '/releases.atom'
    feed = feedparser.parse(url)

    if len(feed.entries) > 0:
        version = feed.entries[0].title

    print_debug(debug, u'\tProject {}: {}'.format(program, version))

    return version

# End of get_latest_github_release() function


def check_versions_for_github_projects(github_project_list, local_dir, debug):
    """
    Checks project's versions on github if any are defined in the yaml
    file under the github.com tag.
    """

    github_cache = FileCache(local_dir, 'github.cache')

    for project in github_project_list:
        version = get_latest_github_release(project, debug)
        if version != '':
            github_cache.update_cache_dict(project, version, debug)

    github_cache.write_cache_file()

# End of check_versions_for_github_projects() function


def make_list_of_newer_feeds(feed, feed_info, debug):
    """
    Compares feed entries and keep those that are newer than the latest
    check we've done and inserting the newer ones in reverse order in
    a list to be returned
    """

    feed_list = []

    # inserting into a list in reverse order to keep the most recent
    # version in case of multiple release of the same project in the
    # feeds
    for a_feed in feed.entries:
        (project, version) = a_feed.title.strip().split(' ', 1)
        print_debug(debug, u'\tFeed entry ({0}): project: {1:16} version: {2}'.format(time.strftime('%x %X', a_feed.published_parsed), project, version))
        if feed_info.is_newer(a_feed.published_parsed):
            feed_list.insert(0, a_feed)

    return feed_list

# End of make_list_of_newer_feeds() function


def lower_list_of_strings(project_list):
    """
    Lowers every string in the list to ease sorting and comparisons
    """

    project_list_low = [project.lower() for project in project_list]

    return project_list_low

# End of lower_list_of_strings() function


def check_and_update_feed(feed_list, project_list, cache, debug):
    """
    Checks every feed entry in the list against project list cache and
    then updates the dictionnary then writes the cache file to the disk.
     - feed_list    is a list of feed (from feedparser module)
     - project_list is the list of project as read from the yaml
                    configuration file
     - cache is an initialized instance of FileCache
    """

    # Lowers the list before searching in it
    project_list_low = lower_list_of_strings(project_list)

    # Checking every feed entry that are newer than the last check
    # and updates the dictionnary accordingly
    for entry in feed_list:
        (project, version) = entry.title.strip().split(' ', 1)
        print_debug(debug, u'\tChecking {0:16}: {1}'.format(project, version))

        if project.lower() in project_list_low:
            cache.update_cache_dict(project, version, debug)

    cache.write_cache_file()

# End of check_and_update_feed()


def check_versions_for_freshcode(freshcode_project_list, local_dir, debug):
    """
    Checks projects with freshcode's web site's RSS
    """

    freshcode_cache = FileCache(local_dir, 'freshcode.cache')

    url = 'http://freshcode.club/projects.rss'
    feed = feedparser.parse(url)

    feed_info = FeedCache(local_dir, 'freshcode.feed')
    feed_info.read_cache_feed()

    length = len(feed.entries)

    if length > 0:
        print_debug(debug, u'\tFound {} entries'.format(length))

        feed_list = make_list_of_newer_feeds(feed, feed_info, debug)
        print_debug(debug, u'\tFound {} new entries (relative to {})'.format(len(feed_list), feed_info.date_minutes))

        check_and_update_feed(feed_list, freshcode_project_list, freshcode_cache, debug)

        # Updating feed_info with the latest parsed feed entry date
        feed_info.update_cache_feed(feed.entries[0].published_parsed)

    else:
        print_debug(debug, u'No entries found in feed')

    feed_info.write_cache_feed()

# End of check_versions_for_freshcode() function


def print_versions_from_cache(local_dir, debug):
    """
    Prints all projects and their associated data from the cache
    """

    github_cache = FileCache(local_dir, 'github.cache')
    freshcode_cache = FileCache(local_dir, 'freshcode.cache')

    github_cache.print_cache_dict('Github')
    freshcode_cache.print_cache_dict('Freshcode')

# End of print_versions_from_cache()


def print_cache_or_check_versions(versions_conf):
    """
    Decide to pretty print projects and their associated version that
    are already in the cache or to check versions of that projects upon
    selections made at the command line
    """

    debug = versions_conf.options.debug
    print_debug(debug, u'Loading yaml config file')
    versions_conf.load_yaml_from_config_file(versions_conf.config_filename)

    if versions_conf.options.list_cache == True:
        # Pretty prints all caches.
        print_versions_from_cache(versions_conf.local_dir, debug)

    else:
        # Checks projects from github
        print_debug(debug, u'Checking github prolects')
        check_versions_for_github_projects(versions_conf.description['github.com'], versions_conf.local_dir, debug)

        # Checks projects from freshcode.club
        print_debug(debug, u'Checking freshcode updates')
        check_versions_for_freshcode(versions_conf.description['freshcode.club'], versions_conf.local_dir, debug)

# End of print_list_or_check_versions() function.


def main():
    """
    This is the where the program begins
    """

    versions_conf = Conf()  # Configuration options

    if versions_conf.options.debug:
        doctest.testmod(verbose=True)

    if os.path.isfile(versions_conf.config_filename):
        print_cache_or_check_versions(versions_conf)

    else:
        print('Error: file %s does not exist' % config_filename)

# End of main() function


def print_debug(debug, message):
    """
    Prints 'message' if debug mode is True
    """

    if debug:
        print(message)

# End of print_debug() function


if __name__=="__main__" :
    main()
