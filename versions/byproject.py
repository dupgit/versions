#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  byproject.py : related to sites that gives an RSS/Atom feed for
#                 each project (such as github)
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
import os
import operator
import re
import caches
import common


def format_project_feed_filename(feed_filename, name):
    """
    Returns a valid filename formatted based on feed_filename (the site name)
    and name (the name of the project).
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
    >>> project = {'name': 'version', 'regex': 'v([\d\.]+)\s*:.*', 'entry': 'entry'}
    >>> get_values_from_project(project)
    (True, 'version', 'v([\\\\d\\\\.]+)\\\\s*:.*', 'entry')
    >>> project = {'name': 'version'}
    >>> get_values_from_project(project)
    (False, 'version', '', '')
    """

    regex = ''
    entry = ''
    name = project
    valued = False

    if isinstance(project, dict):
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
        (published_date, field_name) = common.get_entry_published_date(feed.entries[0])
        if field_name != '':
            feed_list = sorted(feed_list, key=operator.attrgetter(field_name), reverse=True)

    return feed_list

# End of sort_feed_list() function


def get_releases_filtering_feed(debug, local_dir, filename, feed, last_checked):
    """
    Filters the feed and returns a list of releases with one
    or more elements
    """

    feed_list = []

    if last_checked:
        feed_info = caches.FeedCache(local_dir, filename)
        feed_info.read_cache_feed()
        feed_list = common.make_list_of_newer_feeds(feed, feed_info, debug)
        feed_list = sort_feed_list(feed_list, feed)

        # Updating feed_info with the latest parsed feed entry date
        if len(feed_list) >= 1:
            (published_date, field_name) = common.get_entry_published_date(feed_list[0])
            feed_info.update_cache_feed(published_date)

        feed_info.write_cache_feed()

    else:
        feed_list.insert(0, feed.entries[0])

    return feed_list

# End of get_releases_filtering_feed() function


def is_one_entry_field_value_egal_to_last_check(site_entry, entry):
    """
    Returns True if the value of 'entry' field in the yaml file
    is last_checked and False otherwise.
    It checks firstly the 'entry' field for the whole site and if not
    found it then checks it for the project itself.
    """

    if is_entry_last_checked(site_entry):
        last_checked = True
    else:
        last_checked = is_entry_last_checked(entry)

    return last_checked

# End of get_relevant_entry_field_value() function


def get_latest_release_by_title(project, debug, feed_url, local_dir, feed_filename, site_entry):
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

    last_checked = is_one_entry_field_value_egal_to_last_check(site_entry, entry)
    filename = format_project_feed_filename(feed_filename, name)
    url = feed_url.format(name)
    feed = common.get_feed_entries_from_url(url)

    if feed is not None and len(feed.entries) > 0:
        feed_list = get_releases_filtering_feed(debug, local_dir, filename, feed, last_checked)

        if valued and regex != '':
            # Here we match the whole list against the regex and replace the
            # title's entry of the result of that match upon success.
            for feed_entry in feed_list:
                res = re.match(regex, feed_entry.title)
                # Here we should make a new list with the matched entries and leave the other ones
                if res:
                    feed_entry.title = res.group(1)
                common.print_debug(debug, u'\tname: {}\n\tversion: {}\n\tregex: {} : {}'.format(name, feed_entry.title, regex, res))

            common.print_debug(debug, u'\tProject {}: {}'.format(name, feed.entries[0].title))

    return (name, feed_list, last_checked)

# End of get_latest_release_by_title() function


def check_versions_feeds_by_projects(project_list, local_dir, debug, feed_url, cache_filename, feed_filename, site_entry):
    """
    Checks project's versions on feed_url if any are defined in the yaml
    file under the specified tag that got the project_list passed as an argument.
    """

    site_cache = caches.FileCache(local_dir, cache_filename)

    for project in project_list:
        (name, feed_list, last_checked) = get_latest_release_by_title(project, debug, feed_url, local_dir, feed_filename, site_entry)

        if len(feed_list) >= 1:
            # Updating the cache with the latest version (the first feed entry)
            version = feed_list[0].title

            if not last_checked:
                # printing only for latest release as last checked is
                # already filtered and to be printed entirely
                site_cache.print_if_newest_version(name, version, debug)
                # we already printed this.
                del feed_list[0]

            site_cache.update_cache_dict(name, version, debug)

        # Printing all entries in the list.
        for feed_entry in feed_list:
            common.print_project_version(name, feed_entry.title)

    site_cache.write_cache_file()

# End of check_versions_feeds_by_projects() function


def check_versions(versions_conf, byproject_site_list):
    """
    Checks version by checking each project's feed.
    """

    for site_name in byproject_site_list:
        common.print_debug(versions_conf.options.debug, u'Checking {} projects'.format(site_name))
        (project_list, project_url, cache_filename, site_entry) = versions_conf.get_infos_for_site(site_name)
        feed_filename = u'{}.feed'.format(site_name)
        check_versions_feeds_by_projects(project_list, versions_conf.local_dir, versions_conf.options.debug, project_url, cache_filename, feed_filename, site_entry)

# End of check_versions() function.
