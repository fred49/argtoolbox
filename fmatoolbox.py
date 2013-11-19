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

# ---------------------------------------------------------------------------------------------------------------------
class DefaultHook(object):
	def __init__(self):
		pass

	def __call__(self, elt):
		#plugin ? hook ? post function ? ex decode pwd
		pass

# ---------------------------------------------------------------------------------------------------------------------
class Base64DataHook(DefaultHook):
	def __init__(self):
		pass

	def __call__(self, elt):
		if elt.value :
			try:
				data = base64.b64decode(elt.value)
				elt.value = data
			except TypeError as e:
				print "WARN: Password is not stored in the configuration file with base64 encoding"
				print e
				sys.exit(1)
	
# ---------------------------------------------------------------------------------------------------------------------
class Config(object):

	def __init__(self , config_file, prog_name, description = None, mandatory = False ) :
		self.config_file = config_file
		self.prog_name = prog_name
		self.sections = OrderedDict()


	def add_section(self, section):
		if not isinstance(section, Section):
			raise TypeError("argument should be a subclass of Section")
		self.sections[section.name] = section
		return section


	def write_default_config_file(self):
		pass

	def reload(self, args):
		pass

	def push(self, args):
		pass


# ---------------------------------------------------------------------------------------------------------------------
class Element(object):
	def __init__(self, name, e_type = str, required = False, default = None, required_as_arg = False, description = None, hooks = [ DefaultHook() ], hidden = False ):
		self.name = name
		self.e_type = e_type
		self.required = required
		self.default = default
		self.required_as_arg = required_as_arg
		self.description = description
		self.description_for_config = None
		self.description_for_argparse = None
		self.value = None
		self.hidden = hidden

		for h in hooks :
			if not isinstance(h, DefaultHook):
				raise TypeError("hook argument should be a subclass of DefaultHook")

	def post_read(self):
		for h in hooks :
			h(self)

	def set_value(self, val):
		if not instance(val, self.e_type):
			raise TypeError("Element value from config called '" + self.name + "' should have the type : " + str(self.e_type))
		self.value = val
			



# ---------------------------------------------------------------------------------------------------------------------
class Section(object):

	def __init__(self, name, description = None, prefix = None, suffix = None):
		self.elements = OrderedDict()
		self.name = name
		self.description = description
		self.prefix = prefix
		self.suffix = suffix

	def add_element(self, elt):
		if not isinstance(elt, Element):
			raise TypeError("argument should be a subclass of Element")
		self.elements[elt.name] = elt
		return elt





# ---------------------------------------------------------------------------------------------------------------------
class ListSection(object):

	def __init__(self, name, description = None, prefix = None, suffix = None):
		pass








# ---------------------------------------------------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------------------------------------------------

c = Config("/home/fred/.linshare.ini", "linshare-cli", description = " simple user cli for linshare")

#def __init__(self, name, description = None, prefix = None, suffix = None):
s = c.add_section(Section("server"))

#def __init__(self, name, e_type = str, required = False, default = None, required_as_arg = False, description = None, hooks = [ DefaultHook() ] ):
s.add_element(Element('host', default = 'http://localhost:8080/linshare'))
s.add_element(Element('real'))
s.add_element(Element('user'))
s.add_element(Element('password', hidden = True, hooks = [ Base64DataHook(),] ))
s.add_element(Element('application_name'))
s.add_element(Element('config_file'))
s.add_element(Element('server_section'))
s.add_element(Element('nocache'))
s.add_element(Element('debug'))
s.add_element(Element('verbose'))

print c


