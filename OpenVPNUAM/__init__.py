# -*- coding: utf8 -*-

# This file is a part of OpenVPN-UAM
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

"""OpenVPN-UAM - OpenVPN User Access Manager

This module provide a complete openvpn user access management system
It allow you to manage all your openvpn'users, including automatic certificate
building, user access control list, certificate revokation,

This program has two main mode :
  consist in a management daemon which has an internal schedule

USAGE:
To use this module you can :

  use the openvpn-uam-launcher class which is provided with the github project

   or

  put the following code into your python launcher :
>>> import OpenVPNUAM
>>> instance = OpenVPNUAM.OpenVPNUAM( (bool)daemonize?, (string)loglevel )
>>> instance.load( (string)configuration file )
>>> instance.start( (string)pid file )
"""

# Project imports
from .version import version
from .openvpnuam import OpenVPNUAM


__all__ = ['version', 'openvpnuam']
