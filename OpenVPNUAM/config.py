# -*- coding: utf8 -*-

# This file is a part of openvpn-uam
#
# Copyright (c) 2015 Pierre GINDRAUD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Specific configuration parser for OpenVPN UAM module

It provide a parser class which extend the original ConfigParser class
in order to add some function, expecially for retrieving directly
several configuration keys in a dict
"""

# System imports
import grp
import logging
import pwd
import re
import sys
from configparser import ConfigParser
from configparser import Error

# Project imports

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.config')


class OVPNUAMConfigParser(ConfigParser):
  """(extend ConfigParser) Set specific function for configuration file parsing

  Refer to the config file provide some function to parse directly the config
  file as project's needed. This class give highlevel configuration file reading
  """

# CLASS CONSTANTS
# list of logging level available by configuration file
  LOGLEVEL_MAP = ['ERROR', 'WARN', 'INFO', 'DEBUG']
  MAIN_SECTION = 'main'
  DATABASE_SECTION = 'database'
  PKI_SECTION = 'pki'
  EVENT_SECTION = 'event'

  def __init__(self):
    """Constructor : init a new config parser
    """
    ConfigParser.__init__(self)

    # boolean that indicates if the configparser is available
    self.__is_config_loaded = False

  def load(self, path):
    """Try to load the configuration file

    @param path [str] : the path of the config file
    @return [boolean] : True if loading is sucess
                        False if loading fail
    """
    # if file is defined
    if path is None:
      return False

    if path in self.read(path):
      self.__is_config_loaded = True
    return self.__is_config_loaded

  def isLoaded(self):
    """Return the load state of this config parser

    @return [boolean] : the boolean that indicates if the config
              file is loaded or not
    """
    return self.__is_config_loaded

  def getPidPath(self, default='/var/run/openvpn-uam.pid'):
    """Return path to pid file option

    @param default [str] : the default value to return if nothing is found
                            in the config file
    @return [str] : the logtarget
    """
    return self.get(self.MAIN_SECTION, 'pid', fallback=default)

  def getLogLevel(self, default='INFO'):
    """Return loglevel option from configuration file

    @param default [str] : the default value to return if nothing is found
                            in the config file
    @return [str] : the loglevel
    """
    val = self.get(self.MAIN_SECTION, 'log_level', fallback=default)
    if val not in self.LOGLEVEL_MAP:
      g_sys_log.error("Incorrect loglevel : '%s' must be in %s",
                      val, self.LOGLEVEL_MAP)
      return default
    else:
      return val

  def getLogTarget(self, default='STDOUT'):
    """Return logtarget option

    @param default [str] : the default value to return if nothing is found
                            in the config file
    @return [str] : the logtarget
    """
    return self.get(self.MAIN_SECTION, 'log_target', fallback=default)

  def getUid(self):
    """Return the uid (int) option from configfile

    @return [int/None]: integer : the numeric value of
                        None: if group is not defined
    """
    user = self.get(self.MAIN_SECTION, 'user', fallback=None)
    if not user:
      return None
    try:
      return pwd.getpwnam(user).pw_uid
    except KeyError:
      g_sys_log.error("Incorrect username '%s' read in configuration file",
                      user)
      return None

  def getGid(self):
    """Return the gid (int) option from configfile

    @return [int/None] : integer : the numeric value of group id
                        None: if group is not defined
    """
    group = self.get(self.MAIN_SECTION, 'group', fallback=None)
    if not group:
      return None
    try:
      return grp.getgrnam(group).gr_gid
    except KeyError:
      g_sys_log.error("Incorrect groupname '%s' read in configuration file",
                      group)
      return None

  def getItems(self, section='default'):
    """Return all options item in section given by parameter

    @param section [str] the section from which to obtains configuration items
    @return [dict] all item in section in dict format
    """
    return dict(self.items(section))
