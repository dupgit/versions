#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  common.py : common tools used by versions.py modules
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
import feedparser
import time


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

            print_debug(debug, u'\tFeed entry ({0}): Feed title: "{1:16}"'.format(time.strftime('%x %X', published_date), a_feed.title))

            if feed_info.is_newer(published_date):
                feed_list.insert(0, a_feed)
        else:
            print(u'Warning: empty feed in {}'.format(feed))

    return feed_list

# End of make_list_of_newer_feeds() function


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
        # An error happened such that the feed does not contain an HTTP answer.
        manage_non_http_errors(feed, url)
        feed = None

    return feed

# End of get_feed_entries_from_url() function


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
