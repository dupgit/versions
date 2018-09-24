#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  caches.py : module that provides a class and tools to manage caches
#              for versions.py modules
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

import codecs
import os
import common


__author__ = "Olivier Delhomme <olivier.delhomme@free.fr>"


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

        for (project, version) in self.cache_dict.items():
            cache_file.write('%s %s\n' % (project, version))

        cache_file.close()

    # End of write_cache_file() function

    def print_if_newest_version(self, project, version, debug):
        """
        Prints the project and it's version if it is newer than the
        one in cache.
        """
        try:
            version_cache = self.cache_dict[project]
            common.print_debug(debug, u'\t\tIn cache: {}'.format(version_cache))

            if version != version_cache:
                common.print_project_version(project, version)

        except KeyError:
            common.print_project_version(project, version)

    # End of print_if_newest_version() function.


    def update_cache_dict(self, project, version, debug):
        """
        Updates cache dictionnary if needed. We always keep the latest version.
        """

        try:
            version_cache = self.cache_dict[project]
            common.print_debug(debug, u'\t\tUpdating cache with in cache: {} / new ? version {}'.format(version_cache, version))

            if version != version_cache:
                self.cache_dict[project] = version

        except KeyError:
            self.cache_dict[project] = version

    # End of update_cache_dict() function


    def print_cache_dict(self, sitename):
        """
        Pretty prints the cache dictionary as it is recorded in the files.
        """

        print(u'{}:'.format(sitename))

        # Gets project and version tuple sorted by project lowered while sorting
        for project, version in sorted(self.cache_dict.items(), key=lambda proj: proj[0].lower()):
            print(u'\t{} {}'.format(project, version))

        print('')

    # End of print_cache_dict() function
# End of FileCache class


class FeedCache:

    cache_filename = ''
    year = 2016
    month = 5
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


def print_versions_from_cache(local_dir, cache_filename_list):
    """
    Prints all projects and their associated data from the cache
    """
    for cache_filename in cache_filename_list:
        site_cache = FileCache(local_dir, cache_filename)
        site_cache.print_cache_dict(cache_filename)

# End of print_versions_from_cache()
