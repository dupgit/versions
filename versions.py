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
import sys
import locale
import os
import doctest
import configuration
import caches
import common

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


def check_versions(versions_conf):
    """
    Checks versions by parsing online feeds.
    """

    # Checks projects from by project sites such as github and sourceforge
    byproject_site_list = versions_conf.extract_site_list('byproject')

    for site_name in byproject_site_list:
        common.print_debug(versions_conf.options.debug, u'Checking {} projects'.format(site_name))
        (project_list, project_url, cache_filename, project_entry) = versions_conf.get_infos_for_site(site_name)
        feed_filename = u'{}.feed'.format(site_name)
        configuration.check_versions_feeds_by_projects(project_list, versions_conf.local_dir, versions_conf.options.debug, project_url, cache_filename, feed_filename, project_entry)

    # Checks projects from 'list' tupe sites such as freshcode.club
    list_site_list = versions_conf.extract_site_list('list')
    for site_name in list_site_list:
        common.print_debug(versions_conf.options.debug, u'Checking {} updates'.format(site_name))
        (project_list, project_url, cache_filename, project_entry) = versions_conf.get_infos_for_site(site_name)
        regex = versions_conf.extract_regex_from_site(site_name)
        multiproject = versions_conf.extract_multiproject_from_site(site_name)
        feed_filename = u'{}.feed'.format(site_name)
        configuration.check_versions_for_list_sites(project_list, project_url, cache_filename, feed_filename, versions_conf.local_dir, versions_conf.options.debug, regex, multiproject)

# End of check_versions() function


def print_cache_or_check_versions(versions_conf):
    """
    Decide to pretty print projects and their associated version that
    are already in the cache or to check versions of that projects upon
    selections made at the command line
    """

    common.print_debug(versions_conf.options.debug, u'Loading yaml config file')
    versions_conf.load_yaml_from_config_file(versions_conf.config_filename)

    if versions_conf.options.list_cache is True:
        # Pretty prints all caches.
        cache_list = versions_conf.make_site_cache_list_name()
        caches.print_versions_from_cache(versions_conf.local_dir, cache_list)

    else:
        # Checks version from online feeds
        check_versions(versions_conf)

# End of print_list_or_check_versions() function.


def main():
    """
    This is the where the program begins
    """

    if sys.version_info[0] == 2:
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

    versions_conf = configuration.Conf()  # Configuration options

    if versions_conf.options.debug:
        doctest.testmod(verbose=True)

    if os.path.isfile(versions_conf.config_filename):
        print_cache_or_check_versions(versions_conf)

    else:
        print(u'Error: file {} does not exist'.format(versions_conf.config_filename))

# End of main() function


if __name__ == "__main__":
    main()
