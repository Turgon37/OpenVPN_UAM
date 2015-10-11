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

"""This module provide some helper tools to help main program"""

# System import
import datetime
import random
import string
import traceback


def helper_log_fatal(logger, file='error'):
  """This is a helper for logging a fatal error

  @param logger [logging.logger] : the logger to use to make message
  @param file [str] OPTIONNAL : the file into write stacktrace
  """
  error_out = open(file, 'a')
  error_out.write('----------------------------------------------------\n')
  error_out.write('ERROR AT ' + str(datetime.datetime.today()) + ' => \n')
  traceback.print_stack(file=error_out)
  error_out.write(traceback.format_exc())
  error_out.write('----------------------------------------------------')
  error_out.write("\n\n\n\n")
  error_out.close()
  logger.error('FATAL ERROR : contact developer and send him the file "' +
               file + '"')


def datetimeToGeneralizedTime(date):
  """Convert a datetime instance to a date in GeneralizedFormat

  @param date [datetime] the datetime in input
  @return [str] the date in GeneralizedFormat
  """
  return date.strftime("%Y%m%d%H%M%SZ")


def datetimeToGeneralizedTimeB(date):
  """Convert a datetime instance to a date in GeneralizedFormat

  @param date [datetime] the datetime in input
  @return [bytes] the date in GeneralizedFormat compild in bytes object
  """
  return datetimeToGeneralizedTime(date).encode()


def generalizedTimeToDatetime(string):
  """Convert a date in GeneralizedFormat to a datetime instance

  @param string [str] the date in GeneralizedFormat
  @return [datetime] the datetime instance
  """
  return datetime.datetime.strptime(string, "%Y%m%d%H%M%SZ")


def generalizedTimeToDatetimeB(bytes_):
  """Convert a date in GeneralizedFormat to a datetime instance

  @param bytes [bytes] the date in bytes compiled GeneralizedFormat
  @return [datetime] the datetime instance
  """
  return generalizedTimeToDatetime(bytes_.decode())


def random_generator(size=6, chars=(string.ascii_uppercase +
                                    string.ascii_lowercase +
                                    string.digits)):
  """Generate a random string by take char from chars set

  @param size [int] the number of character to generate
  @param chars [str] the list of character to use
  @return [str] the random string
  """
  return ''.join(random.choice(chars) for x in range(size))


if __name__ == '__main__':
  print(random_generator())