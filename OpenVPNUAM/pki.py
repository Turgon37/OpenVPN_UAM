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

"""PKI - Public Key Infrastructure program class

This program class aim to manage the users registering, certificates generation, their 
renewal and also their revocation.
"""

# System imports
import logging

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam')


class PKI:
  """Build an instance of the pki program class

  This instance must be called in the openvpn uam program class
  """

  def __init__(self):
    """Constructor : Build the program lead object
    """
  
  def start(self):
