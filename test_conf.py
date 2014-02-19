#! /usr/bin/env python
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
# Copyright 2014 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


import logging
from fmatoolbox import Config, Element, SimpleSection, Base64ElementHook
from fmatoolbox import DEBUG_LOGGING_FORMAT, streamHandler

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    pass

log = logging.getLogger()
log.setLevel(logging.DEBUG)
streamHandler.setFormatter(DEBUG_LOGGING_FORMAT)

# global logger variable
log = logging.getLogger('fmatoolbox-config')


conf = Config("linshare-cli", desc=" simple user cli for linshare")

sec = conf.add_section(SimpleSection("server"))

sec.add_element(Element('host', default='http://localhost:8080/linshare'))
#sec.add_element(Element('real'))
#sec.add_element(Element('user'))
sec.add_element(Element(
    'password', hidden=True, hooks=[Base64ElementHook(), ]))
#sec.add_element(Element('application_name'))
sec.add_element(Element('config_file'))
sec.add_element(Element('server_section'))
sec.add_element(Element('nocache', e_type=bool, default=False))
sec.add_element(Element('debug', e_type=int, default=0))
sec.add_element(Element('verbose'))
sec.add_element(Element('toto', e_type=int, default=8))
#sec.add_element(Element('tata', e_type=int, required=True))
sec.add_element_list(['real', 'user', 'application_name'])

sec = conf.get_default_section()
sec.add_element(Element('tato', e_type=int, default=8))

print conf
conf.load()

print conf.default.tato
print conf.server.host
print conf.server.host.get_arg_parse_arguments()
