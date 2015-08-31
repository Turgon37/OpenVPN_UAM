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

"""This file contains the template of table description"""


class Table(object):
  """This is an abstract class that describe a basic database adapter"""

  table = None
  primary = None
  foreign = None
  column_options = dict()

  COL_QUOTE = '`'

  @classmethod
  def getName(cls, quote=True):
    """Return the name of tis table

    @return [str] the name of the table
    """
    if quote:
      return cls.COL_QUOTE + cls.table + cls.COL_QUOTE
    else:
      return cls.table

  @classmethod
  def getPrimary(cls, quote=True):
    """Return the name of the primary key column

    @return [str] the name of the primary column
    """
    if quote:
      return cls.COL_QUOTE + cls.primary + cls.COL_QUOTE
    else:
      return cls.primary

  @classmethod
  def getForeign(cls, quote=True):
    """Return the name of the foreign key column

    @return [str] the name of the foreign key column
    """
    if quote:
      return cls.COL_QUOTE + cls.foreign + cls.COL_QUOTE
    else:
      return cls.foreign

  @classmethod
  def getColumnOption(cls):
    """Return the column option of this class
    """
    return cls.column_options

  @classmethod
  def getSelectColumn(cls, sep=","):
    """Return the list of column relevant for select query

    Return a list of all column option as python list by default
    If string is set to True, return a SQL formatted field, with each column
    separated by 'sep' value
    @param string [bool] : if true the result will be a str else a list
    @param quote [bool] : if True all column name will be quoted
    @param sep [str] : the field separator
    """
    str_col = ''

    for key in cls.column_options:
      # if hide keyword is set => don't return this column in SELECT
      if 'hide' in cls.column_options[key] and cls.column_options[key]['hide']:
        continue

      # if rename keyword is set => alias the column in SELECT
      if 'rename' in cls.column_options[key]:
        key = (cls.COL_QUOTE + key + cls.COL_QUOTE + " AS " + cls.COL_QUOTE +
               cls.column_options[key]['rename'] + cls.COL_QUOTE)
      else:
        key = cls.COL_QUOTE + key + cls.COL_QUOTE

      # normal append
      if str_col:
        str_col += sep + " " + key
      else:
        str_col += key

    return str_col
