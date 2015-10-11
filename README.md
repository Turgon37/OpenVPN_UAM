# OVPNUAM - OpenVPN Users Access Manager

This project is licensed under the terms of the MIT license

Not yet available


A python3 daemon that manage users's access to OpenVPN service.

This daemon is in charge of ensure correct access to all user of an OpenVPN server.
It must rebuild new certificate for user with expired certificate.
It provide a dynamic adminitration system to control when an user is able to connect to the server and when not, eent if he have a valid certificate.
It perform some log of all users connection.

## Installation

### Requires:
  * python3 >= 3.2
  * python3-dev >= 3.2
  * pyMySQL : [WebSite](https://github.com/PyMySQL/mysqlclient-python)
  * libmysqlclient-dev (system package)
  * pyOpenSSL : [WebSite](https://pypi.python.org/pypi/pyOpenSSL)