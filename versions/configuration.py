#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  configuration.py : configuration related class and functions for
#                     versions.py modules.
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
import errno
import yaml

__author__ = "Olivier Delhomme <olivier.delhomme@free.fr>"
__date__ = "23.04.2019"
__version__ = "1.5.4-rc2"


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
        Returns information about a site as a tuple
        (list of projects, url to check, filename of the cache, entry checking type)
        """

        project_list = self.extract_project_list_from_site(site_name)
        project_url = self.extract_project_url(site_name)
        project_entry = self.extract_project_entry(site_name)
        cache_filename = u'{}.cache'.format(site_name)

        return (project_list, project_url, cache_filename, project_entry)

    # End of get_infos_for_site() function
# End of Conf class
