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

"""PKI - Public Key Infrastructure program class

This class is in charge of management of all certificates operations
renewal and also their revocation.
This is the entry point of all SSL operations
"""

# System imports
import datetime
import logging
import os

try:
  import OpenSSL
  from OpenSSL import crypto
  from OpenSSL import SSL
  from OpenSSL.crypto import (_lib as lib, _ffi as ffi)
except ImportError:
  raise Exception("Module OpenSSL required " +
                  " https://pypi.python.org/pypi/pyOpenSSL")

# Project imports
from .pki_filetree import PKIFileTree
from .. import models as Model
from ..config import Error
from ..helpers import *

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.pki')


class PublicKeyInfrastructure(object):
  """Build an instance of the pki model class

  This instance must be called in the openvpn uam program class
  """

  def __init__(self, confparser):
    """Constructor : Build a new PKI API instance
    """
    self.__cp = confparser
    # the file tree to use to store all file
    self.__ft = PKIFileTree(confparser)
    # path to CA cert
    self.__certificate_authority = None
    # path to CA key
    # needed to certify new certificates for hostnames
    self.__certificate_authority_key = None
    # Path to the server certificate, use to ensure that this certificate is
    # still valid
    self.__server_certificate = None
    # number of bits for new private key
    self.__cert_key_size = int(2048)

    self.__cert_key_password_size = int(6)
    # the digest use for sign new certificates
    self.__digest = "sha512"
    # a boolean which determine if CSR must be exported to FS or not
    self.__keep_request = False

  def load(self):
    """Return a boolean indicates if PKI is ready to work or not

    This function check things required by PKI working and return a boolean
    that indicates if the PKI is ready to work with certificate or not
    @return [bool] The ready status
    """
    g_sys_log.info("Using %s",
                   SSL.SSLeay_version(SSL.SSLEAY_VERSION).decode())
    # check PKI section in configuration file
    if not self.__cp.has_section(self.__cp.PKI_SECTION):
      g_sys_log.fatal('Missing pki section in configuration file')
      return False
    if not self.__ft.load():
      g_sys_log.fatal('Enabled to load File Manager for PKI')
      return False

    self.__cert_key_size = self.__cp.getint(
        self.__cp.PKI_SECTION,
        'new_cert_key_size',
        fallback=self.__cert_key_size)

    self.__keep_request = self.__cp.getboolean(
        self.__cp.PKI_SECTION,
        'keep_certificate_request',
        fallback=self.__keep_request)

    self.__digest = self.__cp.get(
        self.__cp.PKI_SECTION,
        'digest',
        fallback=self.__digest)

    # BAD USAGE but no other solution
    if lib.EVP_get_digestbyname(self.__digest.encode()) == ffi.NULL:
      g_sys_log.fatal("No such digest method")
      return False

    if not self.__cp.has_option(self.__cp.PKI_SECTION, 'client_extensions'):
      g_sys_log.warning("No SSL extensions configured for client certificate.")

    if not self.__cp.has_option(self.__cp.PKI_SECTION, 'server_extensions'):
      g_sys_log.warning("No SSL extensions configured for server certificate.")

    try:
      self.__certificate_authority = self.loadCertificate(
          self.__cp.get(
              self.__cp.PKI_SECTION,
              'ca'))
      self.__certificate_authority_key = self.loadPrivateKey(
          self.__cp.get(
              self.__cp.PKI_SECTION,
              'ca_key'))
    except Error as e:
      g_sys_log.error('Configuration error : ' + str(e))
      return False
    if self.__certificate_authority is None:
      g_sys_log.error('CA Certificate is missing')
      return False
    else:
      g_sys_log.info("Using CA Certificate '%s'",
                     self.__certificate_authority.get_subject().CN)
    if self.__certificate_authority_key is None:
      g_sys_log.error('CA Key is missing')
      return False
    else:
      g_sys_log.info("Using CA Private Key with size '%s' bits",
                     self.__certificate_authority_key.bits())
    return True

  def checkRequirements(self):
    """Check requirement for PKI to running

    @return [bool] : True if all requirement are valid
                    False ifone of them are not valid
    """
    if self.__certificate_authority.has_expired():
      g_sys_log.error('CA Certificate has expired')
      return False
    if not self.__certificate_authority_key.check():
      g_sys_log.error('CA Private Key is invalid')
      return False
    return True

# TOOLS
  @staticmethod
  def loadCertificate(path):
    """Import an existing certificate from file to python object

    @param path [str] : the path to the certificate file to import
    @return [OpenSSL.crypto.X509] the certificate object that correspond to the
                                  certificate file
            [None] if an error occur
    """
    assert path is not None
    try:
      # open file in binary mode
      f_cert = open(path, 'rb').read()
    except IOError as e:
      g_sys_log.error('Unable to open certificate file : ' + str(e))
      return None

    try:
      # try to load the cert as PEM format
      cert = crypto.load_certificate(crypto.FILETYPE_PEM, f_cert)
    except crypto.Error as e:
      # if error try with another format
      try:
        # try to load the cert as ASN1 format
        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, f_cert)
        g_sys_log.warning('Certificate "%s" is not in PEM recommanded format',
                          path)
      except crypto.Error as e:
        g_sys_log.error('Unable to import certificate : ' + str(e))
        return None
    return cert

  @staticmethod
  def loadPrivateKey(path):
    """Import an private key from file to python object

    @param path [str] : the path to the private key file to import
    @return [OpenSSL.crypto.PKey] the certificate object that correspond to the
                                  certificate file
            [None] if an error occur
    """
    assert path is not None
    try:
      # open file in binary mode
      f_cert = open(path, 'rb').read()
    except IOError as e:
      g_sys_log.error('Unable to open private key file : ' + str(e))
      return None

    try:
      # try to load the key as PEM format
      key = crypto.load_privatekey(crypto.FILETYPE_PEM, f_cert)
    except crypto.Error as e:
      # if error try with another format
      try:
        # try to load the cert as ASN1 format
        key = crypto.load_privatekey(crypto.FILETYPE_ASN1, f_cert)
        g_sys_log.warning('Private Key "%s" is not in PEM recommanded format',
                          path)
      except crypto.Error as e:
        g_sys_log.error('Unable to import private key : ' + str(e))
        return None
    return key

  def loadExtensionFromSection(self, cert, section):
    """Extract the list of extensions listed in a section of conf file

    @param cert [X509] the certificate into add new extensions
    @param section [str] the section from which to extract extensions
      declarations
    @return [list] The list of extensions.
    """
    exts = []
    if not self.__cp.has_section(section):
      g_sys_log.warning("No extension found in section '%s'", section)
      return

    for (name, value) in self.__cp.items(section):
      critical = False
      subject = None
      issuer = None
      if name == 'subjectKeyIdentifier':
        subject = cert
      if name == 'authorityKeyIdentifier':
        subject = cert
        issuer = self.__certificate_authority
      exts.append(
          OpenSSL.crypto.X509Extension(name.encode(),
                                       critical,
                                       value.encode(),
                                       subject,
                                       issuer))
# Disabled because the OpenSSL library doesn't forbid the 'critical' word
#      items = value.split(',')
#      if 'critical' in items:
#        items.pop(items.index('critical'))
#        critical = True
#      data = str(','.join(items))
#      exts.append(OpenSSL.crypto.X509Extension(name.encode(),
#                                               critical,
#                                               data.encode()))
    cert.add_extensions(exts)

  def generateUserCertificate(self, user, hostname):
    """Generate a new Certificate for the given Hostname

    @param user [User]
    @param hostname [Hostname]
    """
    g_sys_log.debug("Building a new certificate for Hostname(%s) '%s'",
                    hostname.id, hostname.name)
    today = datetime.datetime.utcnow()

    # BUILD PRIVATE KEY
    g_sys_log.debug("Generate a %s bits RSA Private Key", self.__cert_key_size)
    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, self.__cert_key_size)

    # BUILD CERTIFICATE SIGNING REQUEST
    g_sys_log.debug("Generate a X509 request")
    req = OpenSSL.crypto.X509Req()
    req.get_subject().C = self.__certificate_authority.get_subject().C
    req.get_subject().ST = self.__certificate_authority.get_subject().ST
    req.get_subject().L = self.__certificate_authority.get_subject().L
    req.get_subject().O = self.__certificate_authority.get_subject().O
    req.get_subject().OU = self.__certificate_authority.get_subject().OU
    req.get_subject().CN = user.cuid + "_" + hostname.name
    req.get_subject().emailAddress = user.user_mail
    req.get_subject().name = (user.cuid + "_" + hostname.name + "_" +
                              str(today))
    req.set_pubkey(key)
    req.sign(key, self.__digest)

    # BUILD CERTIFICATE
    g_sys_log.debug("Generate a X509 certificate")
    cert = OpenSSL.crypto.X509()
    cert.set_version(2)
    #cert.gmtime_adj_notBefore(0)
    #cert.gmtime_adj_notAfter(60*60*24*365)
    cert.set_notBefore(datetimeToGeneralizedTimeB(today))
    cert.set_notAfter(
        datetimeToGeneralizedTimeB(
            today + datetime.timedelta(days=hostname.period_days)
        ))
    # /BUILD CERTIFICATE

    # build certificate model
    m_cert = Model.Certificate(
        generalizedTimeToDatetimeB(cert.get_notBefore()),
        generalizedTimeToDatetimeB(cert.get_notAfter()))
    # ask the hostname to register the new certificate
    if not hostname.addCertificate(m_cert) or m_cert.id is None:
      g_sys_log.error("Hostname unable to insert new certificate with" +
                      " the configured adapter.")
      return

    # BUILD CERTIFICATE
    cert.set_serial_number(m_cert.id)
    cert.set_issuer(self.__certificate_authority.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    self.loadExtensionFromSection(cert,
                                  self.__cp.get(self.__cp.PKI_SECTION,
                                                'client_extensions',
                                                fallback=None))
    cert.sign(self.__certificate_authority_key, self.__digest)
    # /BUILD CERTIFICATE

    # configure settings
    if user.password_mail is not None:
      m_cert.is_password = True
      # generate a random password
      password = random_generator(self.__cert_key_password_size)
    elif user.certificate_password is not None:
      m_cert.is_password = True
      # use configured password
      password = user.certificate_password
    else:
      password = None

    # export certificate
    self.__ft.storePKIUserCertificate(user, hostname, m_cert, key, password)
    if self.__keep_request:
      self.__ft.storePKIUserCertificate(user, hostname, m_cert, req)
    self.__ft.storePKIUserCertificate(user, hostname, m_cert, cert)
