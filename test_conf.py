#!/usr/bin/python
# -*- coding: utf-8 -*-


# This file is part of fmatoolbox.
#
# fmatoolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fmatoolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare user cli.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2013 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


import os
import logging
import getpass
import base64
import copy
import datetime
from ordereddict import OrderedDict
import sys
import ConfigParser

from fmatoolbox import Base64DataHook , Config , Element , Section , myDebugFormat , streamHandler

# ---------------------------------------------------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__" :
	pass

log = logging.getLogger()
log.setLevel(logging.DEBUG)
streamHandler.setFormatter(myDebugFormat)

# global logger variable
log = logging.getLogger('fmatoolbox-config')


c = Config("linshare-cli" , description = " simple user cli for linshare")

#def __init__(self, name, description = None, prefix = None, suffix = None):
s = c.add_section(Section("server"))

#def __init__(self, name, e_type = str, required = False, default = None, required_as_arg = False, description = None, hooks = [ DefaultHook() ] ):
s.add_element(Element('host', default = 'http://localhost:8080/linshare'))
#s.add_element(Element('real'))
#s.add_element(Element('user'))
s.add_element(Element('password', hidden = True, hooks = [ Base64DataHook(),] ))
#s.add_element(Element('application_name'))
s.add_element(Element('config_file'))
s.add_element(Element('server_section'))
s.add_element(Element('nocache' , e_type=bool, default=False))
s.add_element(Element('debug' , e_type=int, default=0))
s.add_element(Element('verbose'))
s.add_element(Element('toto', e_type=int, default = 8))
#s.add_element(Element('tata', e_type=int, required = True))
s.add_element_list([ 'real' , 'user' , 'application_name' ])

s = c.get_default_section()
s.add_element(Element('tato', e_type=int, default = 8))

print c
c.load()

print c.default.tato
print c.server.host
print c.server.host.get_arg_parse_arguments()

