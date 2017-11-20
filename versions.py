#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  versions.py : checks releases and versions of programs through RSS
#                or Atom feeds and tells you
#
#  (C) Copyright 2016 - 2017 Olivier Delhomme
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
import re

__author__ = "Olivier Delhomme <olivier.delhomme@free.fr>"
__date__ = "15.11.2017"
__version__ = "1.3.0"

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


class Conf:
    """
    Class to store configuration of the program and check version.
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
        >>> conf = Conf()
        >>> conf.load_yaml_from_config_file('./bad_formatted.yaml')
        Error in configuration file ./bad_formatted.yaml at position: 9:1
        """

        config_file = codecs.open(filename, 'r', encoding='utf-8')

        try:
            self.description = yaml.safe_load(config_file)
        except yaml.YAMLError, err:
            if hasattr(err, 'problem_mark'):
                mark = err.problem_mark
                print(u'Error in configuration file {} at position: {}:{}'.format(filename, mark.line+1, mark.column+1))
            else:
                print(u'Error in configuration file {}'.format(filename))


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

        parser.add_argument('-f', '--file', action='store', dest='filename', help='Configuration file with projects to check', default='')
        parser.add_argument('-l', '--list-cache', action='store_true', dest='list_cache', help='Lists all projects and their version in cache', default=False)
        parser.add_argument('-d', '--debug', action='store_true', dest='debug', help='Starts in debug mode and prints things that may help', default=False)

        self.options = parser.parse_args()

        if self.options.filename != '':
            self.config_filename = self.options.filename
        else:
            self.config_filename = os.path.join(self.config_dir, 'versions.yaml')

    # End of get_command_line_arguments() function

    def extract_site_definition(self, site_name):
        """
        extracts whole site definition
        """

        if site_name in self.description:
            return self.description[site_name]
        else:
            return dict()

    # End of extract_site_definition()


    def extract_regex_from_site(self, site_name):
        """
        Extracts a regex from a site as defined in the YAML file.
        Returns the regex if it exists or None otherwise.
        """

        site_definition = self.extract_site_definition(site_name)

        if 'regex' in site_definition:
            regex = site_definition['regex']
        else:
            regex = None

        return regex

    # End of extract_regex_from_site() function


    def extract_project_list_from_site(self, site_name):
        """
        Extracts a project list from a site as defined in the YAML file.
        """

        site_definition = self.extract_site_definition(site_name)

        if 'projects' in site_definition:
            project_list = site_definition['projects']
            if project_list is None:
                print(u'Warning: no project for site "{}".'.format(site_name))
                project_list = []
        else:
            project_list = []

        return project_list

    # End of extract_project_list_from_site() function


    def extract_project_url(self, site_name):
        """
        Extracts the url definition where to check project version.
        """

        site_definition = self.extract_site_definition(site_name)

        if 'url' in site_definition:
            project_url = site_definition['url']
        else:
            project_url = ''

        return project_url

    # End of extract_project_url() function


    def is_site_of_type(self, site_name, type):
        """
        Returns True if site_name is of type 'type'
        """

        site_definition = self.extract_site_definition(site_name)
        if 'type' in site_definition:
            return (site_definition['type'] == type)
        else:
            return False

    # End of is_site_of_type() function


    def extract_site_list(self, type):
        """
        Extracts all sites from a specific type (byproject or list)
        """

        all_site_list = list(self.description.keys())
        site_list = []
        for site_name in all_site_list:
            if self.is_site_of_type(site_name, type):
                site_list.insert(0, site_name)
       
        return site_list

    # End of extract_site_list() function


    def make_site_cache_list_name(self):
        """
        Formats list of cache filenames for all sites.
        """

        all_site_list = list(self.description.keys())
        cache_list = []
        for site_name in all_site_list:
            site_cache = u'{}.cache'.format(site_name)
            cache_list.insert(0, site_cache)

        return cache_list

    # End of make_site_cache_list_name() function


    def print_cache_or_check_versions(self):
        """
        Decide to pretty print projects and their associated version that
        are already in the cache or to check versions of that projects upon
        selections made at the command line
        """

        print_debug(self.options.debug, u'Loading yaml config file')
        self.load_yaml_from_config_file(self.config_filename)

        if self.options.list_cache is True:
            # Pretty prints all caches.
            cache_list = self.make_site_cache_list_name()
            print_versions_from_cache(self.local_dir, cache_list, self.options.debug)

        else:
            # Checks version from online feeds
            self.check_versions()

    # End of print_list_or_check_versions() function.


    def check_versions(self):
        """
        Checks versions by parsing online feeds
        """

        # Checks projects from by project sites such as github and sourceforge
        byproject_site_list = self.extract_site_list('byproject')

        for site_name in byproject_site_list:

            print_debug(self.options.debug, u'Checking {} projects'.format(site_name))
            (project_list, project_url, cache_filename) = self.get_infos_for_site(site_name)
            check_versions_feeds_by_projects(project_list, self.local_dir, self.options.debug, project_url, cache_filename)

        # Checks projects from 'list' tupe sites such as freshcode.club
        list_site_list = self.extract_site_list('list')
        for site_name in list_site_list:
            print_debug(self.options.debug, u'Checking {} updates'.format(site_name))
            (project_list, project_url, cache_filename) = self.get_infos_for_site(site_name)
            regex = self.extract_regex_from_site(site_name)
            feed_filename = u'{}.feed'.format(site_name)
            check_versions_for_list_sites(project_list, project_url, cache_filename, feed_filename, self.local_dir, self.options.debug, regex)

    # End of check_versions() function
    
    
    def get_infos_for_site(self, site_name):
        """
        Returns informations about a site as a tuple
        (list of projects, url to check, filename of the cache)
        """

        project_list = self.extract_project_list_from_site(site_name)
        project_url = self.extract_project_url(site_name)
        cache_filename = u'{}.cache'.format(site_name)

        return (project_list, project_url, cache_filename)

    # End of get_infos_for_site() function


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
                print(u'{} {}'.format(project, version))
                self.cache_dict[project] = version

        except KeyError:
            print(u'{} {}'.format(project, version))
            self.cache_dict[project] = version

    # End of update_cache_dict() function


    def print_cache_dict(self, sitename):
        """
        Pretty prints the cache dictionary as it is recorded in the files.
        """

        print(u'{}:'.format(sitename))

        # Gets project and version tuple sorted by project lowered while sorting
        for project, version in sorted(self.cache_dict.iteritems(), key=lambda proj: proj[0].lower()):
            print(u'\t{} {}'.format(project, version))

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

        if exc.errno != errno.EEXIST or os.path.isdir(path) is not True:
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


def get_values_from_project(project):
    """
    Gets the values of 'regex' and 'name' keys if found and
    returns a tuple (valued, name, regex)
    """

    regex = ''
    name = project
    valued = False

    if 'regex' in project and 'name' in project:
        regex = project['regex']
        name = project['name']
        valued = True

    return (valued, name, regex)

# End of get_values_from_project() function


def get_latest_release_by_title(project, debug, feed_url):
    """
    Gets the latest release of a program on github. program must be a
    string of the form user/repository.
    """

    version = ''

    (valued, name, regex) = get_values_from_project(project)

    url = feed_url.format(name)
    feed = get_feed_entries_from_url(url)

    if feed is not None and len(feed.entries) > 0:
        version = feed.entries[0].title

    if valued:
        res = re.match(regex, version)
        if res:
            version = res.group(1)
        print_debug(debug, u'\tname: {}\n\tversion: {}\n\tregex: {} : {}'.format(name, version, regex, res))

    print_debug(debug, u'\tProject {}: {}'.format(name, version))

    return (name, version)

# End of get_latest_release_by_title() function


def check_versions_feeds_by_projects(project_list, local_dir, debug, feed_url, cache_filename):
    """
    Checks project's versions on feed_url if any are defined in the yaml
    file under the specified tag that got the project_list passed as an argument.
    """

    site_cache = FileCache(local_dir, cache_filename)

    for project in project_list:
        (project, version) = get_latest_release_by_title(project, debug, feed_url)
        if version != '':
            site_cache.update_cache_dict(project, version, debug)

    site_cache.write_cache_file()

# End of check_versions_feeds_by_projects() function


def cut_title_in_project_version(title, regex):
    """
    Cuts the title into a tuple (project, version) where possible
    """
    default = False

    if regex is not None:
        res = re.match(regex, title)
        if res:
            project = res.group(1)
            version = res.group(2)
        else:
            default = True
    else:
        default = True


    if default:
        try:
            (project, version) = title.strip().split(' ', 1)

        except ValueError as val:
            project = title.strip()
            version = ''

    return (project, version)

# End of cut_title_in_project_version() function


def make_list_of_newer_feeds(feed, feed_info, debug, regex):
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

        (project, version) = cut_title_in_project_version(a_feed.title, regex)
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


def check_and_update_feed(feed_list, project_list, cache, debug, regex):
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
        (project, version) = cut_title_in_project_version(entry.title, regex)
        print_debug(debug, u'\tChecking {0:16}: {1}'.format(project, version))
        if project.lower() in project_list_low:
            cache.update_cache_dict(project, version, debug)

    cache.write_cache_file()

# End of check_and_update_feed() function


def get_feed_entries_from_url(url):
    """
    Gets feed entries from an url that should be an
    RSS or Atom feed. 
    >>> get_feed_entries_from_url("http://delhomme.org/notfound.html")
    Error 404 while fetching "http://delhomme.org/notfound.html".
    >>> feed = get_feed_entries_from_url("http://blog.delhomme.org/index.php?feed/atom")
    >>> feed.status
    200
    """

    feed = feedparser.parse(url)
    err = feed.status / 100

    if err > 2:
        print(u'Error {} while fetching "{}".'.format(feed.status, url))
        feed = None

    return feed

# End of get_feed_entries_from_url() function


def check_versions_for_list_sites(feed_project_list, url, cache_filename, feed_filename, local_dir, debug, regex):
    """
    Checks projects of list type sites such as freshcode's web site's RSS
    """

    freshcode_cache = FileCache(local_dir, cache_filename)

    feed_info = FeedCache(local_dir, feed_filename)
    feed_info.read_cache_feed()

    feed = get_feed_entries_from_url(url)

    if feed is not None:
        length = len(feed.entries)
        print_debug(debug, u'\tFound {} entries'.format(length))

        feed_list = make_list_of_newer_feeds(feed, feed_info, debug, regex)
        print_debug(debug, u'\tFound {} new entries (relative to {})'.format(len(feed_list), feed_info.date_minutes))

        check_and_update_feed(feed_list, feed_project_list, freshcode_cache, debug, regex)

        # Updating feed_info with the latest parsed feed entry date
        feed_info.update_cache_feed(feed.entries[0].published_parsed)

    feed_info.write_cache_feed()

# End of check_versions_for_list_sites() function


def print_versions_from_cache(local_dir, cache_filename_list, debug):
    """
    Prints all projects and their associated data from the cache
    """
    for cache_filename in cache_filename_list:
        site_cache = FileCache(local_dir, cache_filename)
        site_cache.print_cache_dict(cache_filename)

# End of print_versions_from_cache()


def main():
    """
    This is the where the program begins
    """

    versions_conf = Conf()  # Configuration options

    if versions_conf.options.debug:
        doctest.testmod(verbose=True)

    if os.path.isfile(versions_conf.config_filename):
        versions_conf.print_cache_or_check_versions()

    else:
        print(u'Error: file {} does not exist'.format(versions_conf.config_filename))

# End of main() function


def print_debug(debug, message):
    """
    Prints 'message' if debug mode is True
    """

    if debug:
        print(message)

# End of print_debug() function


if __name__ == "__main__":
    main()
