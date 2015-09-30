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

  def __init__(self):
    """Build a new non-initialised mysql adapter"""
    Adapter.__init__(self, 'mysql', Adapter.TYPE_REMOTE)
    # store local instance of connection
    self.__connection = None
    # number of second between two consecutive server connection attempt
    self.__connection_wait_time = 30
    # number of second from epoch to the last server connection attempt
    self.__connection_wait_ref = 0.0
    # default parameter to use during database opening
    self.__param = dict(charset='utf8mb4')

  def load(self, config):
    """Load the MySQL settings and check it

    @return [bool] a boolean indicates success status
    """
    # if there is no current config available try to use the given
    assert 'db' not in self.__param

    if 'db' in config:
      self.__param['db'] = config['db']
    else:
      g_sys_log.error('Require \'db\' option in configuration file')
      return False

    if 'connection_wait_time' in config:
      try:
        self.__connection_wait_time = float(config['connection_wait_time'])
      except ValueError:
        g_sys_log.error('Invalid format for "connection_wait_time" option')
        return False

    # default parameters
    if 'user' in config:
      self.__param['user'] = config['user']
    else:
      self.__param['user'] = 'root'
    if 'passwd' in config and len(config['passwd']) > 0:
      self.__param['passwd'] = config['passwd']

    # access to server
    if 'unix_socket' in config:
      # Connect to the database with UNIX socket
      self.__param['unix_socket'] = config['unix_socket']
    elif 'host' in config:
      # Connect to the database with TCP
      self.__param['host'] = config['host']
    else:
      g_sys_log.warning('MySQL will used default address/socket to' +
                        ' connect to the server')
    return True

  def open(self):
    """Open the database for read/write operation

    Parse given configuration and try to open the database socket
    @param config [dict] : a list of key-value configuration
    @return [bool] inform about operation successfull True if success
              False otherwise
    """
    if self.__connection is not None and self.__connection.open:
      return True

    # if the last time we have tried to reach the server is over the defined
    # value RETRY
    if time.time() - self.__connection_wait_ref >= self.__connection_wait_time:
      g_sys_log.debug('Try to connect to MySQL server')
      # update the reference time by now
      try:
        self.__connection = MySQLdb.connect(**self.__param)
        return True
      except MySQLdb.MySQLError as e:
        # initialise the timer to prevent to attack server with new
        # authentication
        self.__connection_wait_ref = time.time()
        self.__connection = None
        g_sys_log.error('Error during connection to mysql database ' + str(e))
        return False
    # if not ABORT directly
    else:
      return False

  def close(self):
    """Close properly the database

    @return [bool] True if disconnection success, False otherwise
    """
    if self.__connection is None:
      return False

    try:
      # close if the connection is currently open
      if self.__connection.open:
        self.__connection.close()
      self.__connection = None
      return True
    except MySQLdb.MySQLError as e:
      g_sys_log.error('Error during close of connection to MySQL database %s',
                      str(e))
      self.__connection = None
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
      helper_log_fatal(g_sys_log, '#error_database.mysql.fatal')
      return None
    # SYSTEM error
    except MySQLdb.OperationalError as e:
      # if server or network link has fail
      if e.args[0] == MySQLdb.constants.CR.SERVER_GONE_ERROR:
        try:
          # try to relaunch the connection
          self.__connection.ping(True)
        except MySQLdb.MySQLError as e:
          # if error close defintively the connection
          self.close()
        except Exception as e:
          g_sys_log.error('Error with server connection %s', str(e))
      else:
        g_sys_log.error('Error with server %s',
                        str(e))
      return None
    except Exception as e:
      g_sys_log.error('Error during execution of this query %s', str(e))
      return None
    return cursor

  def require_connection(func):
    """Decorator for function that need running connection

    Apply this decorator to all functions that needs connection
    """
    def check_connection_status(self, *args, **kwargs):
      """Check connection for query

      This function verify that the current connection to database is open
      before execute request. If the connection is not available return None
      immediatly
      """
      # required basis connection instance
      if self.__connection is None:
        # connection simply not opened, try to open it
        if self.open():
          # success => execute query
          return func(self, *args, **kwargs)
        else:
          # failure
          g_sys_log.debug('Unable to open connection')
          return None
      # required connection is opened
      elif not self.__connection.open:
        g_sys_log.error('Connection with MySQL server fail')
        self.close()
        if self.open():
          # success => execute query
          g_sys_log.info('Connection with MySQL server restarted after being' +
                         ' cut off')
          return func(self, *args, **kwargs)
        else:
          # failure
          g_sys_log.debug('Unable to re-open connection')
          return None
      # connection not null and supposed to be connected
      else:
        return func(self, *args, **kwargs)
    return check_connection_status

  @require_connection
  def __queryDict(self, query, args=None, col_opts=None):
    """Execute a query with a DictCursor

    @param query [str] : the query to execute
    @param args [tuple] : a tuple of replacement value for query
    @param col_opts [dict] : the column option for post-treatment
    """
    assert self.__connection is not None
    cur = self.__connection.cursor(MySQLdb.cursors.DictCursor)
    sttm = self.__queryHelper(cur, query, args)
    # make a treatment
    if col_opts is not None and sttm is not None:
      # LOOP over each row of result
      for row in sttm:
        # loop over each col in a row
        for col in row:
          # if column is configured in opts
          if col in col_opts:
            # TYPE is given for this data column
            if 'type' in col_opts[col]:
              # APPLY the configured type
              if col_opts[col]['type'] == bool:
                row[col] = bool(row[col])
              if col_opts[col]['type'] == int:
                row[col] = int(row[col])
    return sttm

  def getUserList(self):
    """Query the database to retrieve the list of user with theirs hostnames

    This function make some query to Mysql database in order to retrieve the
    list of current user and their hostnames. It convert the result into some
    User objects and some Hostname objects.
    @return [list] the list of User
            [None] if the database query fail
    """
    l_user = []
    cur = self.__queryDict('SELECT ' + TableUser.getSelectColumns() +
                           'FROM ' + TableUser.getName(),
                           col_opts=TableUser.getColumnOptions())
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
    cur.close()
    # Commit to prevent MySQL isolation
    self.__connection.commit()
    return l_user

  def getHostnameListFromUserId(self, id):
    """Query the database to retrieve given user's id list of hostname

    This function retrieve from database the list of hostname associated with
    the given user's id. It convert the result into a list of Hostname objects
    @return [list] the list of Hostname of user identified by id
            [None] if the database query fail
    """
    l_host = []
    cur = self.__queryDict('SELECT ' + TableHostname.getSelectColumns() +
                           ' FROM ' + TableHostname.getName() +
                           ' WHERE ' + TableHostname.getForeign() + '= %s',
                           (id,),
                           TableHostname.getColumnOptions())
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
    cur.close()
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
        'SELECT ' + TableUserCertificate.getSelectColumns() +
        ' FROM ' + TableUserCertificate.getName() +
        ' WHERE ' + TableUserCertificate.getForeign() + ' = %s' +
        ' AND %s < `certificate_end_time`',
        (id, datetime.datetime.today()),
        TableUserCertificate.getColumnOptions())
    if cur is None:
      return None
    else:
      # loop over each certificates
      for l in cur:
        assert 'id' in l
        c = Model.Certificate()
        c.load(l)
        l_cert.append(c)
    cur.close()
    return l_cert

  def processUpdate(self, up):
    """Treat an update request

    @param up [Database.DbUpdate] the instance of update which contains
      all parameters field
    @return [bool] : the result of the operation
          True if update success
          False if not
    """
    assert type(up).__name__ == 'DbUpdate'

    model = None
    # try to read model that belong to
    if up.target_type == 'User':
      model = TableUser
    elif up.target_type == 'Hostname':
      model = TableHostname
    elif up.target_type == 'Certificate':
      model = TableUserCertificate
    else:
      up.is_error = True
      up.error_msg = "Not implemented update request"
      return False
    assert model is not None
    # check field exist in model
    if up.field not in model.getColumnOptions():
      up.is_error = True
      up.error_msg = "Unknown field in request"
      return False

    # EXECUTE QUERY
    cur = self.__queryDict(
        'UPDATE ' + model.getName() +
        ' SET ' + model.quote(up.field) + " = %s"
        ' WHERE ' + model.getPrimary() + ' = %s',
        (up.value, up.target.id))
    # check MySQL error
    if cur is None:
      up.is_error = True
      up.error_msg = "MySQL error"
      self.__connection.rollback()
      return False
    # check output number of row
    if up.expected_change != up.NO_CHANGE_CONSTRAINT:
      if up.expected_change != cur.rowcount:
        up.is_error = True
        up.error_msg = "Error bad result row number"
        cur.close()
        self.__connection.rollback()
        return False
    cur.close()
    # Commit to validate modification
    self.__connection.commit()
    return True