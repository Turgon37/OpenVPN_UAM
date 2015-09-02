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

This class provide a Driver for a MySQL storage system
To run correctly this must be initialized and opened by the following function
call :
  open(config) : this cause the config to be loaded and the database
  socket to be opened

And before to exit the main program you have to properly close the database by
using the following function call
  close() : close the current socket

In case where the connection with the MySQL server is being lost, the adapter
will no longer able to return data. But as soon as the server is being
available again, the driver will establish a new connection with the same
parameter as the initial connection and will restart to return data
"""

# System import
import logging
import time

try:
  import MySQLdb
  import MySQLdb.cursors
  import MySQLdb.constants.CR
except ImportError:
  raise Exception("Module MySQLdb required " +
                  " http://mysql-python.sourceforge.net/MySQLdb.html")

# Project imports
from .. import *
from .Table import *

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.database.mysql')


class Connector(Adapter):
  """This version of Connector use a MySQL Adapter to read/write data from/into
  the database
  """
  CONNECTION_ERROR_CODE = [MySQLdb.constants.CR.CONNECTION_ERROR]

  # mysql connection status
  CLOSE = 0
  OPEN = 1

  def __init__(self):
    """Build a new non-initialised mysql adapter"""
    Adapter.__init__(self, 'mysql', Adapter.REMOTE)
    self.__connection = None
    self.__config = None
    # number of second between two consecutive server connection attempt
    self.__server_poll_time = 30
    # number of second from epoch to the last server connection attempt
    self.__server_poll_ref = 0.0
    # store the current connection state
    self.__status = self.CLOSE
    # default parameter to use during database opening
    self.__param = dict(charset='utf8mb4')

  def open(self, config):
    """Open the database for read/write operation

    Parse given configuration and try to open the database socket
    @param config [dict] : a list of key-value configuration
    @return [boolean] inform about operation successfull True if success
              False otherwise
    """
    # if there is no current config available try to use the given
    if self.__config is None:
      # required parameters
      if config is None:
        g_sys_log.error('No configuration given')
        return False
      else:
        self.__config = config

      if 'db' not in config:
        g_sys_log.error('Require \'db\' option in configuration file')
        return False

      if 'server_poll_time' in config:
        try:
          self.__server_poll_time = float(config['server_poll_time'])
        except ValueError as e:
          g_sys_log.error('Invalid format for "server_poll_time" option')
          return False

      # default parameters
      if 'user' not in config:
        config['user'] = 'root'
      self.__param['user'] = config['user']
      if 'passwd' in config and len(config['passwd']) > 0:
        self.__param['passwd'] = config['passwd']
      self.__param['db'] = config['db']

      # access to server
      if 'unix_socket' in config:
        # Connect to the database with UNIX socket
        self.__param['unix_socket'] = config['unix_socket']
      elif 'host' in config:
        # Connect to the database with TCP
        self.__param['host'] = config['host']
      else:
        g_sys_log.warning('Mysql will used default address/socket to' +
                          'connect to the server')
    # open the database and handle all error type because it the first
    # opening of the DB
    try:
      return self.__open()
    except MySQLdb.MySQLError as e:
      g_sys_log.error('Error during connection to mysql database ' + str(e))
      return False

  def __open(self):
    """Open the database socket

    This function use the previously defined config dict to open
    the network socket with the database server
    @return [boolean] True if success False if not
    @throw MySQLdb.MySQLError
    """
    if self.__config is None:
      return False

    # if the last time we have tried to reach the server is
    # over the defined value RETRY
    if time.time() - self.__server_poll_ref >= self.__server_poll_time:
      # update the reference time by now
      self.__poll_ref = time.time()
      self.__connection = MySQLdb.connect(**self.__param)
      self.__status = self.OPEN
      return True
    # if not ABORT
    else:
      return False

  def close(self):
    """Close properly the database

    @return [bool] True if disconnection success, False otherwise
    """
    try:
      self.__connection.close()
      self.__status = self.CLOSE
      return True
    except MySQLdb.MySQLError as e:
      g_sys_log.error('Error during close of connection to MySQL database ' +
                      str(e))
      return False

  def __queryHelper(self, cursor, query, args=None):
    """Execute a basic query on the given cursor

    This helper execute a query on the given cursor and handle error reporting
    if exception occur
    @param cursor [MySQLdb.cursors] the cursor on which to execute the query
    @param query [str] the query to execute
    @param args [tuple] OPTIONNAL : a tuple of replacement argument to put
      instead string control character into query string
    @return [MySQLdb.cursors] the cursor after query execution or None if fail
    """
    # try at most two time to execute query
    try:
      if args is None:
        cursor.execute(query)
      else:
        cursor.execute(query, args)
    # DEVELOPPER error
    except MySQLdb.ProgrammingError as e:
      helper_log_fatal(g_sys_log, 'error_database.mysql.fatal')
      return None
    # SYSTEM error
    except MySQLdb.OperationalError as e:
      # case where the client lost connection with server
      if e.args[0] == MySQLdb.constants.CR.SERVER_GONE_ERROR:
        # it's the first time the connection is closed
        if self.__status == self.OPEN:
          g_sys_log.error('Connection with MySQL server fail')
        self.__status = self.CLOSE
        # TRY to re-open
        try:
          # if success
          if self.__open():
            g_sys_log.info('Connection with MySQL server restarted after ' +
                           'being cut off')

            return None
        # error in network unable to re-open connection
        except MySQLdb.OperationalError as e:
          if e.args[0] in self.CONNECTION_ERROR_CODE:
            return None
        except MySQLdb.MySQLError as e:
          g_sys_log.error('Error during connection to mysql database ' +
                          str(e))
          return None
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
    """Query the database to retrieve the list of user with theirs hostnames

    This function make some query to Mysql database in order to retrieve the
    list of current user and their hostnames. It convert the result into some
    User objects and some Hostname objects.
    @return [list] the list of User
            [None] if the database query fail
    """
    l_user = []
    cur = self.__queryDict('SELECT ' + MysqlTableUser.getSelectColumn() +
                           'FROM ' + MysqlTableUser.getName())
    # if the result is None immediatly return None for the entire query
    if cur is None:
      return None
    else:
      # loop over each user row
      for l in cur:
        assert 'id' in l
        u = Model.User(None, None)
        # retrieve hostname list associated with given user code
        l_h = self.getHostnameListFromUserId(l['id'])
        # if the result is None => immediatly fail the entire query
        # if there is not hostname associated with this user, the result
        # will be a empty list like []
        if l_h is None:
          return None
        else:
          u.load(l, l_h)
          l_user.append(u)
    return l_user

  def getHostnameListFromUserId(self, id):
    """Query the database to retrieve given user's id list of hostname

    This function retrieve from database the list of hostname associated with
    the given user's id. It convert the result into a list of Hostname objects
    @return [list] the list of Hostname of user identified by id
            [None] if the database query fail
    """
    l_host = []
    cur = self.__queryDict('SELECT ' + MysqlTableHostname.getSelectColumn() +
                           ' FROM ' + MysqlTableHostname.getName() +
                           ' WHERE ' + MysqlTableHostname.getForeign() + '= %s',
                           (id,))
    if cur is None:
      return None
    else:
      # loop over each hostname row
      for r in cur:
        assert 'id' in r
        h = Model.Hostname(None)
        # retrieve not-yet expired certificate list associated with given user
        # code
        l_c = self.getUserCertificateListFromHostnameId(r['id'])
        # if query fail this will propagate the error to other
        if l_c is None:
          return None
        else:
          h.load(r, l_c)
          l_host.append(h)
    return l_host

  def getUserCertificateListFromHostnameId(self, id):
    """Query the database to retrieve the list of not yet expired certificates

    This function retrieve from database the list of certificates associated
    with the given user's id. It convert the result into a list of Certificate
    objects according to the program Model.
    Only not-yet expired certificates are returned here.
    Each of theses certificates are returned as a single list. It's charge of
    Hostname class to provide there sorting into differents categories
    @return [list] the list of Certificates of hostname identified by given id
            [None] if the database query fail
    """
    l_cert = []
    cur = self.__queryDict(
        'SELECT ' + MysqlTableUserCertificate.getSelectColumn() +
        ' FROM ' + MysqlTableUserCertificate.getName() +
        ' WHERE ' + MysqlTableUserCertificate.getForeign() + '= %s',
        (id,))
    if cur is None:
      return None
    else:
      # loop over each certificates
      for l in cur:
        assert 'id' in l
        c = Model.Certificate()
        c.load(l)
        l_cert.append(c)
    return l_cert
