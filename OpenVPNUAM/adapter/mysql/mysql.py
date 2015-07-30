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

"""adapter/mysql

Python class for MySQL database support
"""

# System import
import logging

try:
  import MySQLdb
except ImportError:
  raise Exception("Module MySQLdb required " +
                  " http://mysql-python.sourceforge.net/MySQLdb.html")

try:
  import MySQLdb.cursors
except ImportError:
  raise Exception("Module MySQLdb failed to import dependencies")

# Project imports
from .. import *
from .Table import *

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.database.mysql')


class Connector(Adapter):
  """This version of Connector use a MySQL Adapter to read/write data from/into
  the database
  """

  def __init__(self):
    """Build a new non-initialised mysql adapter"""
    Adapter.__init__(self, 'mysql', Adapter.REMOTE)
    self.__connection = None
    self.__config = None

  def open(self, config):
    """Open the database for read/write operation

    @param config [dict] : a list of key-value configuration
    @return [boolean] inform about operation successfull
    """
    self.__config = config
    # required parameters
    if config is None:
      g_sys_log.error('No configuration given')
      return False
    if 'db' not in config:
      g_sys_log.error('Require \'db\' option in configuration file')
      return False

    # default parameters
    if 'user' not in config:
      config['user'] = 'root'

    param = dict()
    param['user'] = config['user']
    if 'passwd' in config and len(config['passwd']) > 0:
      param['passwd'] = config['passwd']
    param['db'] = config['db']
    param['charset'] = 'utf8mb4'
    # access to server
    if 'unix_socket' in config:
      # Connect to the database with UNIX socket
      param['unix_socket'] = config['unix_socket']
    elif 'host' in config:
      # Connect to the database with TCP
      param['host'] = config['host']
    else:
      g_sys_log.warning('Mysql will used default "localhost" address to' +
                        'connect to the server')

    try:
      self.__connection = MySQLdb.connect(**param)
    except MySQLdb.MySQLError as e:
      g_sys_log.error('Error during connection to mysql database ' + str(e))
      return False
    return True

  def close(self):
    """Close properly the database"""
    self.__connection.close()

  def __queryHelper(self, cursor, query, args=None):
    """Execute a basic query on the given cursor

    This helper execute a query on the given cursor and handle error reporting
    if exception occur
    @param cursor [MySQLdb.cursors] the cursor on which to execute the query
    @param query [str] the query to execute
    @return [MySQLdb.cursors] the cursor after query execution or None if fail
    """
    try:
      if args is None:
        cursor.execute(query)
      else:
        cursor.execute(query, args)
    except MySQLdb.ProgrammingError as e:
      helper_log_fatal(g_sys_log, 'error_database.mysql.fatal')
      return None
    except Exception as e:
      g_sys_log.error('Error during execution of this query ' + str(e))
      return None
    return cursor

  def __queryDict(self, query, args=None):
    """Execute a query with a DictCursor

    @param [str] query : the query to execute
    """
    cur = self.__connection.cursor(MySQLdb.cursors.DictCursor)
    return self.__queryHelper(cur, query, args)

  def getUserList(self):
    cur = self.__queryDict('SELECT ' + MysqlTableUser.getSelectColumn() +
                           'FROM ' + MysqlTableUser.getName())
    l_user = []
    if cur is not None:
      for l in cur:
        u = Model.User(None, None)
        u.load(l, self.getHostnameListFromUserId(l['id']))
        l_user.append(u)
    return l_user

  def getHostnameListFromUserId(self, id):
    l_host = []
    cur = self.__queryDict('SELECT ' + MysqlTableHostname.getSelectColumn() +
                           ' FROM ' + MysqlTableHostname.getName() +
                           ' WHERE ' + MysqlTableHostname.getForeign() + '= %s',
                           (id,))
    if cur is not None:
      for l in cur:
        h = Model.Hostname(None)
        h.load(l)
        l_host.append(h)
    return l_host
