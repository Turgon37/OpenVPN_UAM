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

"""This file provide the base class that must be extended by all database
adapter
"""

# System import
import datetime
import logging
import traceback

# Project imports
from .. import models as Model

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.database.mysql')

class Adapter(object):
  """This is an abstract class that describe a basic database adapter"""

  # constant for adapter connection types
  LOCAL=0
  REMOTE=1

  def __init__(self, name, type):
    """You must call it in your adapter __init__

    This init must be call in the begining of your adapter extended init()
    @param name [str] the name of the adapter technology. This name must
    match the .py file in which the code is stored
    @param type [integer] the connection type of the adapter is use.
    see constants above for other details
    """
    self.name = name
    self.type = type

  def getName(self):
    """Return the name of this adapter

    @return [str] the
    """
    return self.name

  def getType(self):
    """

    @return [integer] the Adapter constants that desribe the type
    """
    return self.type

  def open(self, config):
    """This function must be overloaded

    This function must open/load the database. Make here all
    needed operation to start your database.
    @param config [dict]a key-value dict that contains all keyword in
    corresponding section of the config file
    @return [boolean] True if the open success, False otherwise
    """
    raise NotImplementedError()

  def close(self):
    """This function must be overloaded

    This function must close/unload the database. Make here all operation
    that properly close the database
    """
    raise NotImplementedError()
    
  def _fatal_(self, file='error'):
    error_out = open(file, 'a')
    error_out.write('----------------------------------------------------\n')
    error_out.write('ERROR AT ' + str(datetime.datetime.today()) + ' => \n')
    traceback.print_stack(file=error_out)
    error_out.write(traceback.format_exc())
    error_out.write('----------------------------------------------------')
    error_out.write("\n\n\n\n")
    error_out.close()
    g_sys_log.error('FATAL ERROR : contact developer and send him the file "' +
                    file + '"')