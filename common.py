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
