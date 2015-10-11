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

"""PKI - Public Key Infrastructure File Tree program class

This class is responsive of management of all SSL files
"""

# System imports
import logging
import os

import OpenSSL
from OpenSSL import crypto
from OpenSSL.crypto import (_lib as lib, _ffi as ffi)

# Project imports
from ..config import Error

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.pki.file')


class PKIFileTree(object):
  """Build an instance of the pki model class

  This instance must be called in the openvpn uam program class
  """

  def __init__(self, confparser):
    """Constructor : Build a new PKI API instance
    """
    self.__cp = confparser
    # the root path of file tree
    self.__new_cert_directory = "certificates/"
    # the cipher to use for private key encryption
    self.__cipher = "DES3"

  def load(self):
    """Return a boolean indicates if PKI is ready to work or not

    This function check things required by PKI working and return a boolean
    that indicates if the PKI is ready to work with certificate or not
    @return [bool] The ready status
    """

    # check PKI section in configuration file
    if not self.__cp.has_section(self.__cp.PKI_SECTION):
      g_sys_log.error('Missing pki section in configuration file')
      return False
    sec = self.__cp.getItems(self.__cp.PKI_SECTION)

    # read the new cert directory path from config file
    self.__new_cert_directory = self.__cp.get(
        self.__cp.PKI_SECTION,
        'cert_directory',
        fallback=self.__new_cert_directory).rstrip('/') + '/'

    self.__cipher = self.__cp.get(
        self.__cp.PKI_SECTION,
        'cert_key_cipher',
        fallback=self.__cipher)

    # BAD USAGE but no other solution
    if lib.EVP_get_cipherbyname(self.__cipher.encode()) == ffi.NULL:
      g_sys_log.fatal("Invalid cipher name")
      return False

    if not self.makePath(self.__new_cert_directory):
      g_sys_log.fatal("Certificate directory is invalid")
      return False
    return True

# Tools
  def makePath(self, path):
    """Ensure that the given path is builded on the file system

    @param path [str] the path to check for
    @return [bool] True if the entire path is existing on the FS
                   False if an error happen
    """
    p = ""
    for folder in path.split('/'):
      if len(folder) == 0:
        continue
      p += folder + '/'
      if not os.path.exists(p):
        # create it
        g_sys_log.info("Creating directory '%s'", p)
        try:
          os.mkdir(p)
        except OSError as e:
          g_sys_log.error("File '%s' already exist", p)
          return False
      # if cert path already exist
      else:
        # check if it is a valid directory
        if not os.path.isdir(p):
          g_sys_log.error("File '%s' is not a directory", p)
          return False
    return True

# API
  def storeBytesToFile(self, content, path):
    """Write a list of bytes into a file

    @param content [bytes/str] the content to write into the file
    @param path [str] the path to the file into
    """
    f = None
    if os.path.exists(path):
      g_sys_log.error("Error during export of file '%s'.", path)
      return

    if isinstance(content, bytes):
      # open output file in binary mode
      f = open(path, "wb")
    elif isinstance(content, str):
      # open output file in text mode
      f = open(path, "wt")
    assert f is not None

    f.write(content)
    f.close()

  def storePKIUserCertificate(self, user, hostname, certificate, obj,
                              password=None):
    """Store a given PKI object into a file

    @param user [User] the user to which the certificate is associated
    @param hostname [Hostname] the hostname to which the certificate is
                              associated
    @param certificate [Certificate] the Certificate instance associated with
                        the file
    @param obj [X509/PKey] The object that will be dump to the file
    @param password [str] OPTIONNAL : an optionnal passphrase to use for encrypt
          the output (if available)
    """
    path = (self.__new_cert_directory + str(user.id) + "/" + str(hostname.id) +
            "/")
    self.makePath(path)

    bytes_ = None
    if isinstance(obj, OpenSSL.crypto.X509):
      bytes_ = crypto.dump_certificate(crypto.FILETYPE_PEM, obj)
      path += str(certificate.id) + ".crt"
    if isinstance(obj, OpenSSL.crypto.X509Req):
      bytes_ = crypto.dump_certificate_request(crypto.FILETYPE_PEM, obj)
      path += str(certificate.id) + ".csr"
    elif isinstance(obj, OpenSSL.crypto.PKey):
      if isinstance(password, str):
        bytes_ = crypto.dump_privatekey(crypto.FILETYPE_PEM, obj,
                                        self.__cipher, password.encode())
      else:
        bytes_ = crypto.dump_privatekey(crypto.FILETYPE_PEM, obj)
      path += str(certificate.id) + ".key"
    assert bytes_ is not None
    self.storeBytesToFile(bytes_, path)
