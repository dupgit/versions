#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  bylist.py : related to sites that gives one RSS/Atom feed for
#              all the projects (such as freshcode.club)
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
import re
import caches
import common


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
    project = ''
    version = ''

    if regex is not None:
        (project, version, default) = cut_title_with_regex_method(title, regex)
    else:
        default = True

    if default:
        (project, version) = cut_title_with_default_method(title)

    return (project, version)

# End of cut_title_in_project_version() function


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

    feed = common.get_feed_entries_from_url(url)

    if feed is not None:
        common.print_debug(debug, u'\tFound {} entries'.format(len(feed.entries)))
        feed_list = common.make_list_of_newer_feeds(feed, feed_info, debug)
        common.print_debug(debug, u'\tFound {} new entries (relative to {})'.format(len(feed_list), feed_info.date_minutes))

        check_and_update_feed(feed_list, feed_project_list, freshcode_cache, debug, regex, multiproject)

        # Updating feed_info with the latest parsed feed entry date
        feed_info.update_cache_feed(feed.entries[0].published_parsed)

    feed_info.write_cache_feed()

# End of check_versions_for_list_sites() function

def check_versions(versions_conf, list_site_list):
    """
    Checks version by checking each project's feed.
    """

    for site_name in list_site_list:
        common.print_debug(versions_conf.options.debug, u'Checking {} updates'.format(site_name))
        (project_list, project_url, cache_filename, project_entry) = versions_conf.get_infos_for_site(site_name)
        regex = versions_conf.extract_regex_from_site(site_name)
        multiproject = versions_conf.extract_multiproject_from_site(site_name)
        feed_filename = u'{}.feed'.format(site_name)
        check_versions_for_list_sites(project_list, project_url, cache_filename, feed_filename, versions_conf.local_dir, versions_conf.options.debug, regex, multiproject)

# End of check_versions() function
