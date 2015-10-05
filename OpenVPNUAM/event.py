# -*- coding: utf8 -*-

# This file is a part of OpenVPN-UAM
#
# Copyright (c) 2015 Thomas PAJON, Pierre GINDRAUD
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

"""Event

This file contains class for event.
It provide some function to manage this event and also to update
its attributes.
"""

# System imports
import logging

# Project imports
from .handlers import BaseHandler

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.event')

# g_crit_dict = [0: 'info', 1: 'warning', 2: 'critical']
# g_urge_defaultdict = [('low', []), ('normal', ['mail']), ('critical', ['sms', 'mail'])]


class EventReceiver(object):
  """This class represent the entry point of all generated event

  Each event that is generate by all other part of this program are handled
  here. After a little treatment, all event are dispatched through some event
  handler
  """

  def __init__(self, confparser):
    """Constructor: Build a new event Receiver with the specified config parser
    """
    self.__cp = confparser
    self.__l_handler = []
    # self._criticality = None
    # self._message = None
    # self._urgency = None

  def load(self):
    """Load configuration for event handler

    @return [bool] : the loading status, True if load successfull
              False, otherwise
    """
    if not self.__cp.has_section(self.__cp.EVENT_SECTION):
      g_sys_log.error("Missing '%s' section in configuration file",
                      self.__cp.EVENT_SECTION)
      return False

    try:
      hs = self.__cp.getItems(self.__cp.EVENT_SECTION)['handlers']
    except KeyError:
      g_sys_log.error("Missing 'handlers' item in section '%s' in" +
                      "configuration file", self.__cp.EVENT_SECTION)
      return False

    if len(hs) == 0:
      g_sys_log.warning("No specific event handler configured. " +
                        "Only syslog message will be generated on events")
    else:
      # this boolean indicates if at least one event handler support
      # the CAP.CAP_FILE capabilities
      have_file_cap = False
      for hs_n in hs.split(','):
        hs_n = hs_n.strip()
        g_sys_log.debug("Loading event handler with name '%s'", hs_n)
        try:
          mod = __import__('OpenVPNUAM.handlers.' + hs_n, fromlist=['Handler'])
          hdlr = mod.Handler()
        except ImportError as e:
          g_sys_log.error("Handler '%s' cannot be found in handlers/ folder." +
                          " %s", hs_n, str(e))
          return False
        except AttributeError as e:
          g_sys_log.error("Handler '%s' must use Handler as class name. %s",
                          hs_n,
                          str(e))
          return False

        # handler class checking
        if not isinstance(hdlr, BaseHandler):
          g_sys_log.error("Handler '%s' must extend BaseHandler class", name)
          return False

        # handler class name checking
        if hdlr.name != hs_n:
          g_sys_log.error("Handler name '%s' doesn't match with class name %s",
                          hdlr.name,
                          hs_n)
          return False

        if not self.__cp.has_section(hdlr.name):
          g_sys_log.error("Handler '%s' require a configuration section with " +
                          "the same name", hdlr.name)
          return False
        hdlr.logger = logging.getLogger('openvpn-uam.event.' + hdlr.name)
        hdlr.configuration = self.__cp.getItems(hdlr.name)
        try:
          if not hdlr.load():
            return False
        except KeyError as e:
          g_sys_log.error("Handler '%s' require a missing parameter. %s",
                          hdlr.name, str(e))

        g_sys_log.debug("Handler '%s' loaded with CAP %s",
                        hdlr.name, hdlr.capabilities)
        if BaseHandler.CAP.CAP_FILE in hdlr.capabilities:
          have_file_cap = True
        self.__l_handler.append(hdlr)
      # warning if no handler support CAP FILE
      if have_file_cap is False:
        g_sys_log.warning("No handler suppport FILE sending." +
                          " New certificate will not be send to user")

    return True
    # assert isinstance(criticality, (int, string))
    # assert isinstance(message, string)
    # assert isinstance(urgency, string)
    #
    # assert (criticality > 2 and criticality < 0)
    # assert urgency in g_urge_list
    #
    # self._criticality = criticality
    # self._message = message
    # self._urgency = urgency

  # def notify(self):
  #   """Select the applications to notify the administrators
  #   """
  #   for urg, apps_list in g_urge_defaultdict:
  #     if urg == self._urgency:
  #       for app in apps_list:
  #         if app == 'mail':
  #           str(app)
  #         elif app == 'sms':
  #           str(app)
  #         else:
  #           pass
