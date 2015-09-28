# -*- coding: utf8 -*-

# This file is a part of OpenVPN-UAM
#
# Copyright (c) 2015 Thomas PAJON
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

# Global project declarations
g_crit_dict = [0: 'info', 1: 'warning', 2: 'critical']
g_urge_defaultdict = [('low', []), ('normal', ['mail']), ('critical', ['sms', 'mail'])]

class Event(object):
  """Build an instance of the event program class
  """

  def __init__(self):
    """Constructor: Build a new event
    """
    self._criticality = None
    self._message = None
    self._urgency = None

  def load(self, criticality, message, urgency):
    """Load attributes of the event
    
    @param criticality [int] : the level of the criticality of the event
       message [string] : the containing message in the event
       urgency [string] : the urgency of the event to notify the
          administrators
    """
    assert isinstance(criticality, (int, string))
    assert isinstance(message, string)
    assert isinstance(urgency, string)
    
    assert (criticality > 2 and criticality < 0)
    assert urgency in g_urge_list
    
    self._criticality = criticality
    self._message = message
    self._urgency = urgency
  
  def notify(self):
    """Select the applications to notify the administrators
    """
    for urg, apps_list in g_urge_defaultdict:
      if urg == self._urgency:
        for app in apps_list:
          if app == 'mail':
            str(app)
          elif app == 'sms':
            str(app)
          else:
            pass
 