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

"""Models/Hostname

This file contains class for hostname.
It provide some function to manage this hostname and also to update
its attributes.
"""

# System imports
import datetime
import logging

# Project imports
from .certificate import Certificate

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.model.hostname')


class Hostname(object):
  """Build an instance of the hostname program class
  """

  def __init__(self, name):
    """Constructor: Build a new empty hostname

    @param name [str] : the name of the hostname
    """
    # database model
    self._id = None
    self._name = name
    self._period_days = None
    self._is_enabled = False
    self._is_online = False
    self._creation_time = datetime.datetime.today()
    self._update_time = None
    # python model
    # This is the list of NOT YET AVAILABLE certificates
    # These certificates doesn't need to perform specific action on them
    self.__lst_certificate_soon_valid = []
    # This is the list of VALID certificates
    # These certificates doesn't need to perform specific action on them
    self.__lst_certificate_valid = []
    # This is the list of SOON EXPIRED certificates
    # If there is a certificates in this list it indicates that the program
    # must begin to perform a regen of new certificate to prevent VPN accesss
    # failure
    self.__lst_certificate_soon_expired = []
    # This is the list of EXPIRED certificates
    # Certificates in this list are sentenced to be destroyed by python garbage
    # collector in the next DB update
    self.__lst_certificate_expired = []
    # This is the reference to the main database class
    # it is used to perform self object update call
    # Exemple if you want to update a attribut of an instance of this class
    # like one of theses above, you will need to call the main database to store
    # change into database engine
    self.__db = None
    # This is the current system datetime
    self.__cur_time = None

  def load(self, attributs, certs=[]):
    """Load an hostname entity with attributs

    @param attributs [dict] : a key-value dict which contains attributs
    to set to this Hostname object
    """
    assert self._id is None
    assert isinstance(attributs, dict)
    # loop for each given attributes
    for key in attributs:
      if hasattr(self, "_" + key):
        setattr(self, "_" + key, attributs[key])
      else:
        g_sys_log.error('Unknown attribute from source "' + key + '"')
    # load certificates
    self.loadCertificate(certs)

  def loadCertificate(self, certs):
    """Import and sort certificates into this hostname

    This function load given certificates list and sort them into four category
    according to their living dates
    @param certs [list<Certificate>] the pool of available certificates
    """
    assert isinstance(certs, list)
    # set uniq local time reference
    cur_time = datetime.datetime.today()
    self.__cur_time = cur_time
    # sort each given certificates into exiting categories
    for cert in certs:
      assert isinstance(cert, Certificate)
      # SOON VALID
      if cur_time < cert.getBeginTime():
        self.__lst_certificate_soon_valid.append(cert)
      # CURRENTLY VALID
      elif cert.getBeginTime() <= cur_time and cur_time <= cert.getEndTime():
        vd = self.__getValidityDuration(cert)
        if vd <= timedelta(0, 0, 6, 0, 0):
          self.sortValidCertificate(cert, 0, 0, 20)
        elif vd <= timedelta(0, 1, 0, 0, 0) and vd > timedelta(0, 0, 6, 0, 0):
          self.sortValidCertificate(cert, 0, 4, 0)
        elif vd <= timedelta(0, 3, 0, 0, 0) and vd > timedelta(0, 1, 0, 0, 0):
          self.sortValidCertificate(cert, 1, 0, 0)
        elif vd <= timedelta(0, 7, 0, 0, 0) and vd > timedelta(0, 3, 0, 0, 0):
          self.sortValidCertificate(cert, 2, 0, 0)
        else:
          self.sortValidCertificate(cert, 4, 0, 0)
      # EXPIRED
      else:
        self.__lst_certificate_expired.append(cert)

# Getters methods
  @property
  def is_enabled(self):
    """Return get the activation state of this hostname

    @return [bool] : the activation state of the hostname
    """
    return self._is_enabled
  
  @property
  def name(self):
    """Get name of this hostname

    @return [str] : the name of the hostname
    """
    return self._name

# Setters methods
  def setName(self, name):
    """setName(): Change the name of the hostname

    @param name [str] : name of the hostname
    """
    self._name = name
    self.__update()

  def setDb(self, db):
    """Set the internal DB link to allow self update

    Add reference to main database into this hostname
    @param db [Database] : the database instance to use for self update call
    """
    assert self.__db is None
    self.__db = db
    for h in self.__lst_certificate_soon_valid:
      h.setDb(db)
    for h in self.__lst_certificate_valid:
      h.setDb(db)
    for h in self.__lst_certificate_soon_expired:
      h.setDb(db)
    for h in self.__lst_certificate_expired:
      h.setDb(db)

# Private methods
  def __update(self):
    """update(): Change the date of the last update of the
    hostname
    """
    self._update_time = datetime.datetime.today()

  def enable(self):
    """enable(): Set hostname enable
    """
    self._is_enable = True
    self.__update()

  def disable(self):
    """disable(): Set hostname disable
    """
    self._is_enabled = False
    self.__update()

  def getValidityDuration(self, cert):
    """Calculate the validity duration of a certificate

    @param cert [Certificate] : a certificate
    @return [datetime] : validity duration of the certificate
    """
    return cert.getEndTime - cert.getBeginTime

  def setOnline(self):
    """setOnline(): Change the status of the hostname to
    online
    """
    self._is_online = True
    self.__update()

  def setOffline(self):
    """setOffline(): Change the status of the hostname to
    offline
    """
    self._is_online = False
    self.__update()

  def sortValidCertificate(self, cert, days, hours, minutes):
    """sortValidCertificate(): Check if a certificate is just valid
    or if it is valid and soon expired.
    """
    if self.__cur_time < cert.getEndTime - timedelta(0, days, hours, minutes, 0):
      self.__lst_certificate_valid.append(cert)
    else:
      self.__lst_certificate_soon_expired.append(cert)

  def __str__(self):
    """[DEBUG] Produce a description string for this hostname instance

    @return [str] a formatted string that describe this hostname
    """
    content = ("  HOSTNAME (" + str(self._id) + ")" +
               "\n    NAME = " + str(self._name) +
               "\n    STATUS = " + str(self._is_enabled) +
               "\n    ONLINE STATUS = " + str(self._is_online) +
               "\n    CREATED ON = " + str(self._creation_time) +
               "\n    UPDATED ON = " + str(self._update_time))
    for c in self.__lst_certificate_soon_valid:
      content += "\n  SV-" + str(c)
    for c in self.__lst_certificate_valid:
      content += "\n   V-" + str(c)
    for c in self.__lst_certificate_soon_expired:
      content += "\n  SE-" + str(c)
    for c in self.__lst_certificate_expired:
      content += "\n   E-" + str(c)
    return content

# utilities methods
  def __repr__(self):
    """[DEBUG] Produce a list of attribute as string for this hostname instance

    @return [str] a formatted string that describe this hostname
    """
    return ("[id(" + str(self._id) + ")," +
            " name(" + str(self._name) + ")," +
            " enable(" + str(self._is_enabled) + ")," +
            " createdon(" + str(self._creation_time) + ")," +
            " updatedon(" + str(self._update_time) + ")," +
            " certificate(" + str(len(self.__lst_certificate)) + ")]")
