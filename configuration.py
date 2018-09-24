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
import argparse
import os
import re
import errno
import time
import doctest
import feedparser
import yaml
import operator
import common
import caches

__author__ = "Olivier Delhomme <olivier.delhomme@free.fr>"
__date__ = "06.11.2018"
__version__ = "1.5.2"


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
        except yaml.YAMLError as err:
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

        parser = argparse.ArgumentParser(description='This program checks releases and versions of programs through RSS or Atom feeds')

        parser.add_argument('-v', '--version', action='version', version=str_version)
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

        return self.extract_variable_from_site(site_name, 'regex', None)

    # End of extract_regex_from_site() function


    def extract_multiproject_from_site(self, site_name):
        """
        Extracts from a site its separator list for its multiple
        projects in one title. It returns None if multiproject
        is not defined and the list of separators instead
        """

        return self.extract_variable_from_site(site_name, 'multiproject', None)

    # End of extract…multiproject_from_site() function


    def extract_variable_from_site(self, site_name, variable, default_return):
        """
        Extracts variable from site site_name if it exists and return
        default_return otherwise
        """

        site_definition = self.extract_site_definition(site_name)

        if variable in site_definition:
            value = site_definition[variable]
            if value is None:
                print(u'Warning: no variable "{}" for site "{}".'.format(variable, site_name))
                value = default_return
        else:
            value = default_return

        return value

    # End of extract_variable_from_site() function


    def extract_project_list_from_site(self, site_name):
        """
        Extracts a project list from a site as defined in the YAML file.
        """

        return self.extract_variable_from_site(site_name, 'projects', [])

    # End of extract_project_list_from_site() function


    def extract_project_url(self, site_name):
        """
        Extracts the url definition where to check project version.
        """

        return self.extract_variable_from_site(site_name, 'url', '')

    # End of extract_project_url() function


    def extract_project_entry(self, site_name):
        """
        Extracts the entry definition (if any) of a site.
        """

        return self.extract_variable_from_site(site_name, 'entry', '')

    # End of extract_project_entry() function.


    def is_site_of_type(self, site_name, site_type):
        """
        Returns True if site_name is of type 'site_type'
        """

        site_definition = self.extract_site_definition(site_name)
        if 'type' in site_definition:
            return (site_definition['type'] == site_type)
        else:
            return False

    # End of is_site_of_type() function


    def extract_site_list(self, site_type):
        """
        Extracts all sites from a specific type (byproject or list)
        """

        all_site_list = list(self.description.keys())
        site_list = []
        for site_name in all_site_list:
            if self.is_site_of_type(site_name, site_type):
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


    def get_infos_for_site(self, site_name):
        """
        Returns informations about a site as a tuple
        (list of projects, url to check, filename of the cache)
        """

        project_list = self.extract_project_list_from_site(site_name)
        project_url = self.extract_project_url(site_name)
        project_entry = self.extract_project_entry(site_name)
        cache_filename = u'{}.cache'.format(site_name)

        return (project_list, project_url, cache_filename, project_entry)

    # End of get_infos_for_site() function
# End of Conf class


def manage_http_status(feed, url):
    """
    Manages http status code present in feed and prints
    an error in case of a 3xx, 4xx or 5xx and stops
    doing anything for the feed by returning None.
    """

    err = feed.status / 100

    if err > 2:
        print(u'Error {} while fetching "{}".'.format(feed.status, url))
        feed = None

    return feed

# End of manage_http_status() function


def manage_non_http_errors(feed, url):
    """
    Tries to manage non http errors and gives
    a message to the user.
    """

    if feed.bozo:
        if feed.bozo_exception:
            exc = feed.bozo_exception
            if hasattr(exc, 'reason'):
                message = exc.reason
            else:
                message = 'unaddressed'

            print(u'Error {} while fetching "{}".'.format(message, url))

        else:
            print(u'Error while fetching url "{}".'.format(url))

# End of manage_non_http_errors() function


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

    if 'status' in feed:
        feed = manage_http_status(feed, url)
    else:
        # An error happened such that the feed does not contain an HTTP response
        manage_non_http_errors(feed, url)
        feed = None

    return feed

# End of get_feed_entries_from_url() function


def format_project_feed_filename(feed_filename, name):
    """
    Returns a valid filename formatted based on feed_filename (the site name)
    and name the name of the project
    """

    (root, ext) = os.path.splitext(feed_filename)
    norm_name = name.replace('/', '_')

    filename = "{}_{}{}".format(root, norm_name, ext)

    return filename

# End of format_project_feed_filename() function


def is_entry_last_checked(entry):
    """
    Returns true if entry is equal to last checked and
    false otherwise.
    >>> is_entry_last_checked('last checked')
    True
    >>> is_entry_last_checked('')
    False
    >>> is_entry_last_checked('latest')
    False
    """

    return entry == 'last checked'

# End of is_entry_last_checked() function


def get_values_from_project(project):
    """
    Gets the values of 'regex' and 'name' keys if found and
    returns a tuple (valued, name, regex, entry)
    """

    regex = ''
    entry = ''
    name = project
    valued = False

    if type(project) is dict:
        if 'name' in project:
            name = project['name']

        if 'regex' in project:
            regex = project['regex']
            valued = True

        if 'entry' in project:
            entry = project['entry']
            valued = True

    return (valued, name, regex, entry)

# End of get_values_from_project() function


def sort_feed_list(feed_list, feed):
    """
    Sorts the feed list with the right attribute which depends on the feed.
    sort is reversed because feed_list is build by inserting ahead when
    parsing the feed from the most recent to the oldest entry.
    Returns a sorted list (by date) the first entry is the newest one.
    """

    if feed.entries[0]:
        if 'published_parsed' in feed.entries[0]:
            feed_list = sorted(feed_list, key=operator.attrgetter('published_parsed'), reverse=True)
        elif 'updated_parsed' in feed.entries[0]:
            feed_list = sorted(feed_list, key=operator.attrgetter('updated_parsed'), reverse=True)

    return feed_list

# End of sort_feed_list() function


def get_releases_filtering_feed(debug, local_dir, filename, feed, entry):
    """
    Filters the feed and returns a list of releases with one
    or more elements
    """

    feed_list = []

    if is_entry_last_checked(entry):
        feed_info = caches.FeedCache(local_dir, filename)
        feed_info.read_cache_feed()
        feed_list = make_list_of_newer_feeds(feed, feed_info, debug)
        feed_list = sort_feed_list(feed_list, feed)

        # Updating feed_info with the latest parsed feed entry date
        if len(feed_list) >= 1:
            published_date = get_entry_published_date(feed_list[0])
            feed_info.update_cache_feed(published_date)

        feed_info.write_cache_feed()

    else:
        feed_list.insert(0, feed.entries[0])

    return feed_list


def get_latest_release_by_title(project, debug, feed_url, local_dir, feed_filename, project_entry):
    """
    Gets the latest release or the releases between the last checked time of
    a program on a site of type 'byproject'.
    project must be a string that represents the project (user/repository in
    github for instance).
    Returns a tuple which contains the name of the project, a list of versions
    and a boolean that indicates if we checked by last checked time (True) or
    by release (False).
    """

    feed_list = []

    (valued, name, regex, entry) = get_values_from_project(project)
    
    if is_entry_last_checked(project_entry):
        last_checked = True
        entry = project_entry
    else:
        last_checked = is_entry_last_checked(entry)
    filename = format_project_feed_filename(feed_filename, name)

    url = feed_url.format(name)
    feed = get_feed_entries_from_url(url)

    if feed is not None and len(feed.entries) > 0:
        feed_list = get_releases_filtering_feed(debug, local_dir, filename, feed, entry)

        if valued and regex != '':
            # Here we match the whole list against the regex and replace the
            # title's entry of the result of that match upon success.
            for entry in feed_list:
                res = re.match(regex, entry.title)
                # Here we should make a new list with the matched entries and leave tho other ones
                if res:
                    entry.title = res.group(1)
                common.print_debug(debug, u'\tname: {}\n\tversion: {}\n\tregex: {} : {}'.format(name, entry.title, regex, res))

        common.print_debug(debug, u'\tProject {}: {}'.format(name, entry.title))

    return (name, feed_list, last_checked)

# End of get_latest_release_by_title() function


def check_versions_feeds_by_projects(project_list, local_dir, debug, feed_url, cache_filename, feed_filename, project_entry):
    """
    Checks project's versions on feed_url if any are defined in the yaml
    file under the specified tag that got the project_list passed as an argument.
    """

    site_cache = caches.FileCache(local_dir, cache_filename)

    for project in project_list:
        (name, feed_list, last_checked) = get_latest_release_by_title(project, debug, feed_url, local_dir, feed_filename, project_entry)


        if len(feed_list) >= 1:
            # Updating the cache with the latest version (the first entry)
            version = feed_list[0].title

            if not last_checked:
                # printing only for latest release as last checked is
                # already filtered and to be printed entirely
                site_cache.print_if_newest_version(name, version, debug)

            site_cache.update_cache_dict(name, version, debug)

            if not last_checked:
                # we already printed this.
                del feed_list[0]

        for entry in feed_list:
            common.print_project_version(name, entry.title)

    site_cache.write_cache_file()

# End of check_versions_feeds_by_projects() function

#####################################################################$$

def cut_title_with_default_method(title):
    """
    Cuts title with a default method and a fallback
    >>> cut_title_with_default_method('versions 1.3.2')
    ('versions', '1.3.2')
    >>> cut_title_with_default_method('no_version_project')
    ('no_version_project', '')
    """

    try:
        (project, version) = title.strip().split(' ', 1)

    except ValueError:
        project = title.strip()
        version = ''

    return (project, version)

# End of cut_title_with_default_method() function


def cut_title_with_regex_method(title, regex):
    """
    Cuts title using a regex. If it does not success
    fallback to default.
    >>> cut_title_with_regex_method('versions 1.3.2', '([\w]+)\s([\d\.]+)')
    ('versions', '1.3.2', False)
    >>> cut_title_with_regex_method('versions 1.3.2', '([\w]+)notgood\s([\d\.]+)')
    ('', '', True)
    """

    default = False
    project = ''
    version = ''

    res = re.match(regex, title)
    if res:
        project = res.group(1)
        version = res.group(2)
    else:
        default = True

    return (project, version, default)

# End of cut_title_with_regex_method() function


def cut_title_in_project_version(title, regex):
    """
    Cuts the title into a tuple (project, version) where possible with a regex
    or if there is no regex or the regex did not match cuts the title with a
    default method
    """
    default = False

    if regex is not None:
        (project, version, default) = cut_title_with_regex_method(title, regex)
    else:
        default = True

    if default:
        (project, version) = cut_title_with_default_method(title)

    return (project, version)

# End of cut_title_in_project_version() function


def get_entry_published_date(entry):
    """
    Returns the published date of an entry.
    Selects the right field to do so
    """

    if 'published_parsed' in entry:
        published_date = entry.published_parsed
    elif 'updated_parsed' in entry:
        published_date = entry.updated_parsed
    elif 'pubDate' in entry:    # rss-0.91.dtd (netscape)
        published_date = entry.pubDate

    return published_date

# End of get_entry_published_date() function


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

        if a_feed:
            published_date = get_entry_published_date(a_feed)

            common.print_debug(debug, u'\tFeed entry ({0}): Feed title: "{1:16}"'.format(time.strftime('%x %X', published_date), a_feed.title))

            if feed_info.is_newer(published_date):
                feed_list.insert(0, a_feed)
        else:
            print(u'Warning: empty feed in {}'.format(feed))

    return feed_list

# End of make_list_of_newer_feeds() function


def lower_list_of_strings(project_list):
    """
    Lowers every string in the list to ease sorting and comparisons
    """

    project_list_low = [project.lower() for project in project_list]

    return project_list_low

# End of lower_list_of_strings() function


def split_multiproject_title_into_list(title, multiproject):
    """
    Splits title into a list of projects according to multiproject being
    a list of separators
    """

    if multiproject is not None:
        titles = re.split(multiproject, title)
    else:
        titles = [title]

    return titles

# End of split_multiproject_title_into_list() function




def check_and_update_feed(feed_list, project_list, cache, debug, regex, multiproject):
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

        titles = split_multiproject_title_into_list(entry.title, multiproject)

        for title in titles:
            (project, version) = cut_title_in_project_version(title, regex)
            common.print_debug(debug, u'\tChecking {0:16}: {1}'.format(project, version))
            if project.lower() in project_list_low:
                cache.print_if_newest_version(project, version, debug)
                cache.update_cache_dict(project, version, debug)

    cache.write_cache_file()

# End of check_and_update_feed() function


def check_versions_for_list_sites(feed_project_list, url, cache_filename, feed_filename, local_dir, debug, regex, multiproject):
    """
    Checks projects of 'list' type sites such as freshcode's web site's RSS
    """

    freshcode_cache = caches.FileCache(local_dir, cache_filename)

    feed_info = caches.FeedCache(local_dir, feed_filename)
    feed_info.read_cache_feed()

    feed = get_feed_entries_from_url(url)

    if feed is not None:
        common.print_debug(debug, u'\tFound {} entries'.format(len(feed.entries)))
        feed_list = make_list_of_newer_feeds(feed, feed_info, debug)
        common.print_debug(debug, u'\tFound {} new entries (relative to {})'.format(len(feed_list), feed_info.date_minutes))

        check_and_update_feed(feed_list, feed_project_list, freshcode_cache, debug, regex, multiproject)

        # Updating feed_info with the latest parsed feed entry date
        feed_info.update_cache_feed(feed.entries[0].published_parsed)

    feed_info.write_cache_feed()

# End of check_versions_for_list_sites() function
