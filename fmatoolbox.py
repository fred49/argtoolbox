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


# ---------------------------------------------------------------------------------------------------------------------
log = logging.getLogger()
log.setLevel(logging.INFO)
# logger formats
myFormat = logging.Formatter("%(asctime)s %(levelname)-8s: %(message)s", "%H:%M:%S")
myDebugFormat = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s:%(funcName)s:%(message)s", "%H:%M:%S")
# logger handlers
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(myFormat)
log.addHandler(streamHandler)
# debug mode
# if you need debug during class construction, file config loading, ...,  you need to modify the logger level here.
if True:
	log.setLevel(logging.DEBUG)
	streamHandler.setFormatter(myDebugFormat)

# global logger variable
log = logging.getLogger('linshare-cli')


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

	def __init__(self, prog_name, config_file = None, description = None, mandatory = False ) :
		self.config_file = config_file
		self.prog_name = prog_name
		self.sections = OrderedDict()
		self.mandatory = mandatory

	def add_section(self, section):
		if not isinstance(section, Section):
			raise TypeError("argument should be a subclass of Section")
		self.sections[section.name] = section
		return section

	def load(self):
		fileParser = ConfigParser.SafeConfigParser()
		discoveredFileList  = []
		if self.config_file :
			discoveredFileList = fileParser.read([ self.config_file ])
		else:
			discoveredFileList = fileParser.read([ self.prog_name + ".cfg", os.path.expanduser('~/.' + self.prog_name + '.cfg'), '/etc/' + self.prog_name + '.cfg'])
		log.debug("discoveredFileList: " + str(discoveredFileList))

		if self.mandatory and len(discoveredFileList) < 1 :
			print "Error : config file missing !"
			sys.exit(1)

		for s in self.sections.values():
			s.load(fileParser)

	def write_default_config_file(self):
		pass

	def reload(self, args):
		pass

	def push(self, args):
		pass


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

	def load(self, fileParser):
		for e in self.elements.values() :
			e.load(fileParser, self.name)





# ---------------------------------------------------------------------------------------------------------------------
class ListSection(object):

	def __init__(self, name, description = None, prefix = None, suffix = None):
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
			

	def load(self, fileParser, section_name):
		try:
			self.value = fileParser.get( section_name, self.name)
		except ConfigParser.NoOptionError :
			log.debug("Not found : " + self.name)








# ---------------------------------------------------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------------------------------------------------

c = Config("linshare-cli" , description = " simple user cli for linshare")
#c = Config("linshare-cli" , "/home/fred/.linshare-cli.ini", description = " simple user cli for linshare")

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
c.load()


