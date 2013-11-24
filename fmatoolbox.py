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
import argparse


# ---------------------------------------------------------------------------------------------------------------------
log = logging.getLogger()
log.setLevel(logging.INFO)
# logger formats
myFormat = logging.Formatter("%(asctime)s %(levelname)-8s: %(message)s", "%H:%M:%S")
myDebugFormat = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s:%(funcName)s:%(message)s", "%H:%M:%S")
# logger handlers
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(myFormat)
# TODO : FIXME
#log.addHandler(streamHandler)
# debug mode
# if you need debug during class construction, file config loading, ...,  you need to modify the logger level here.
if True:
	log.setLevel(logging.DEBUG)
	streamHandler.setFormatter(myDebugFormat)

# global logger variable
log = logging.getLogger('fmatoolbox')


# ---------------------------------------------------------------------------------------------------------------------
class DefaultHook(object):
	def __init__(self):
		pass

	def __call__(self, elt):
		pass

# ---------------------------------------------------------------------------------------------------------------------
class Base64DataHook(DefaultHook):
	def __init__(self, warning = False):
		self.warning = warning

	def __call__(self, elt):
		if elt.value :
			try:
				data = base64.b64decode(elt.value)
				elt.value = data
			except TypeError as e:
				if self.warning :
					log.warn("current field '%(name)s' is not stored in the configuration file with base64 encoding" , { "name" : elt.name })
				else :
					raise e

# ---------------------------------------------------------------------------------------------------------------------
class Config(object):

	def __init__(self, prog_name, config_file = None, desc = None, mandatory = False ) :
		self.prog_name = prog_name
		self.config_file = config_file
		self.desc = desc
		self.mandatory = mandatory

		self.sections = OrderedDict()
		self._default_section = self.add_section(Section("DEFAULT"))
		self.parser = None

	def add_section(self, section):
		if not isinstance(section, Section):
			raise TypeError("argument should be a subclass of Section")
		self.sections[section.name] = section
		return section

	def get_section(self, section):
		return self.sections.get(section)

	def get_default_section(self):
		return self._default_section

	def load(self):
		self.fileParser = ConfigParser.SafeConfigParser()
		discoveredFileList = []
		if self.config_file :
			if isinstance(self.config_file , str):
				discoveredFileList = self.fileParser.read(self.config_file)
			else:
				discoveredFileList = self.fileParser.readfp(self.config_file, "file descriptor")
		else:
			defaultFileList = []
			defaultFileList.append(self.prog_name + ".cfg")
			defaultFileList.append(os.path.expanduser('~/.' + self.prog_name + '.cfg'))
			defaultFileList.append('/etc/' + self.prog_name + '.cfg')
			discoveredFileList = self.fileParser.read(defaultFileList)

		log.debug("discoveredFileList: " + str(discoveredFileList))

		if self.mandatory and len(discoveredFileList) < 1 :
			msg="The required config file was missing. Default config files : " + str(defaultFileList)
			log.error(msg)
			raise EnvironmentError(msg)

		#print self.fileParser.items("DEFAULT")
		log.debug("loading configuration ...")
		for s in self.sections.values():
			log.debug("loading section : " + s.name)
			s.load(self.fileParser)
		log.debug("configuration loaded.")

	def reload(self, args):
		log.debug("reloading configuration ...")
		if args.config_file :
			self.fileParser.read(args.config_file)
		for s in self.sections.values():
			log.debug("loading section : " + s.name)
			s.load(self.fileParser)
		log.debug("configuration reloaded.")

	def __getattr__(self, name):
		if name.lower() == "default":
			return self._default_section
		s = self.sections.get(name)
		if s :
			return s
		else:
			raise AttributeError("'%(class)s' object has no attribute '%(name)s'" 
						% { "name" : name, "class" : self.__class__.__name__ } )

	def get_parser(self , **kwargs):
		self.parser = argparse.ArgumentParser( prog = self.prog_name , description=self.desc, **kwargs)
		self.parser.add_argument('-c', '--config-file',	action="store", help="Other configuration file.")
		return self.parser

	def __str__(self):
		res = []
		res.append("Configuration of %(prog_name)s : " % self.__dict__)
		for s in self.sections.values():
			res.append("".join(s.get_representation("\t")))
		return "\n".join(res)

	def write_default_config_file(self , output , comments = True):
		with open(output, 'w') as f:
			if comments :
				f.write("#####################################\n")
				f.write("Description :\n")
				f.write("-------------\n")
				f.write(self.desc)
				f.write("\n\n")

			for s in self.sections.values():
				log.debug("loading section : " + s.name)
				s.write_config_file(f , comments)
		log.info("config file generation complete : " + str(output))

# ---------------------------------------------------------------------------------------------------------------------
class Section(object):

	def __init__(self, name, desc = None, prefix = None, suffix = None):
		self.elements = OrderedDict()
		self.name = name
		self.desc = desc
		self.prefix = prefix
		self.suffix = suffix

	def add_element(self, elt):
		if not isinstance(elt, Element):
			raise TypeError("argument should be a subclass of Element")
		self.elements[elt.name] = elt
		return elt

	def add_element_list(self, elt_list):
		for e in elt_list:
			self.add_element(Element(e))

	def count(self):
		return len(self.elements)

	def load(self, fileParser):
		a = []
		if self.prefix :
			a.append(self.prefix)
		a.append(self.name)
		if self.suffix:
			a.append(self.suffix)
		section = "-".join(a)
		for e in self.elements.values() :
			e.load(fileParser, section)

	def __getattr__(self, name):
		e = self.elements.get(name)
		if e :
			return e
		else:
			raise AttributeError("'%(class)s' object has no attribute '%(name)s'" 
						% { "name" : name, "class" : self.__class__.__name__ } )

	def get_representation(self , prefix = "" , suffix = "\n"):
		res = []
		if self.count() > 0:
			res.append(prefix)
			res.append("Section %(name)s : " % self.__dict__)
			res.append(suffix)
			for elt in self.elements.values():
				if not elt.hidden :
					a = []
					a.append(prefix)
					a.append(" - %(name)s : %(value)s" % elt.__dict__)
					res.append("".join(a))
					res.append(suffix)
		return res

	def __str__(self):
		return "".join(self.get_representation())

	def write_config_file(self , f , comments):
		if len(self.elements) < 1 :
			return

		if comments :
			f.write("#####################################\n")
			f.write("# Section : " + self.name + "\n")
			f.write("#####################################\n")
		f.write("[" + self.name + "]\n")
		if self.desc and comments:
			f.write("# Description : ")
			f.write(self.desc)
			f.write("\n")

		for e in self.elements.values() :
			e.write_config_file(f , comments)
		f.write("\n")

# ---------------------------------------------------------------------------------------------------------------------
class ListSection(object):

	def __init__(self, name, desc = None, prefix = None, suffix = None):
		pass
# ---------------------------------------------------------------------------------------------------------------------
class Element(object):
	def __init__(self, name, e_type = str, required = False, default = None, conf_hidden = False, desc = None, hooks = [ DefaultHook() ], hidden = False ):
		self.name = name
		self.e_type = e_type
		self.required = required
		self.default = default
		self.desc = desc
		self.conf_hidden = conf_hidden
		self.desc_for_config = None
		self.desc_for_argparse = None
		self.value = None
		self.hidden = hidden
		self.hooks = hooks

		for h in hooks :
			if not isinstance(h, DefaultHook):
				raise TypeError("hook argument should be a subclass of DefaultHook")

	def __str__(self):
		return self.name + " : " + str(self.value)

	def post_read(self):
		for h in self.hooks :
			h(self)

	def set_value(self, val):
		if not instance(val, self.e_type):
			raise TypeError("Element value from config called '%(name)s' should have the type : '%(e_type)s'" 
				 % { "name": self.name , "e_type" : self.e_type })
		self.value = val

	def load(self, fileParser, section_name):
		self._load(fileParser , section_name)
		self.post_read()

	def _load(self, fileParser, section_name):
		try:
			data = fileParser.get( section_name, self.name)
			log.debug("field found : " + self.name )
			if self.required :
				if not data :
					msg = "The required field '%(name)s' was missing from the config file." % { "name": self.name }
					log.error(msg)
					raise ValueError(msg)
				data = self.e_type(data)
			elif self.default :
				if not data :
					data = self.default

			log.debug("field found : '%(name)s' , value : '%(data)s', type : '%(e_type)s'" , { "name": self.name , "data": data , "e_type" : self.e_type })
			try:
				data = self.e_type(data)
			except  ValueError as e:
				msg = "The current field '%(name)s' was present, but the required type is : %(e_type)s instead of : %(c_type)s."  % { "name": self.name , "e_type" : self.e_type , "c_type": type(data) }
				log.error(msg)
				msg = "Error message : %(msg)s." % { "msg": str(e) }
				log.error(msg)
				raise ValueError(msg)

			# happens only when the current field is present, type is string, but value is ''
			if not data:
				msg = "The optional field '%(name)s' was present, type is string, but the current value is an empty string." % { "name": self.name }
				log.error(msg)
				raise ValueError(msg)

			self.value = data

		except ConfigParser.NoOptionError :
			if self.required :
				msg = "The required field " + self.name  + " was missing from the config file."
				log.error(msg)
				raise ValueError(msg)

			if self.default :
				self.value = self.default
				log.debug("Field not found : " + self.name + ", default value : " + str(self.default))
			else:
				log.debug("Field not found : " + self.name)

	def get_arg_parse_arguments(self):
		ret = dict()
		if self.required :
			ret["required"] = self.required
		if self.name :
			ret["dest"] = self.name
		if self.value :
			ret["default"] = self.value
		if self.desc :
			ret["help"] = self.desc
		return ret

	def write_config_file(self , f, comments):
		if self.conf_hidden:
			return False

		if comments:
			f.write("\n")
			f.write("# Attribute (")
			f.write(str(self.e_type.__name__))
			f.write(") : ")
			f.write(self.name.upper())
			f.write("\n")
			if self.desc and self.desc != argparse.SUPPRESS:
				f.write("# Description : ")
				f.write(self.desc)
				f.write("\n")


		if not self.required:
			f.write(";")
		f.write(self.name)
		f.write("=")
		if self.default:
			f.write(self.default)
		f.write("\n")

# ---------------------------------------------------------------------------------------------------------------------
class DefaultCompleter(object):
	def __init__(self , func_name = "complete"):
		self.func_name = func_name

	def __call__(self, prefix, **kwargs):
		import argcomplete
		from argcomplete import debug
		from argcomplete import warn
		try:
			debug("\n-----------------------------")
			debug(str(kwargs))
			for i , j in kwargs.items() :
				debug(i)
				debug("\t" + str(j))

			args = kwargs.get('parsed_args')
			parser = kwargs.get('parser')
			#a = parser.parse_known_args()
			a= args
			debug("\n-----------------------------")
			debug(str(a))

			# getting form args the current Command and looking for a method called by default 'complete'. 
			# The method name is specified  by func_name
			fn = getattr(args.__func__, self.func_name, None)
			if fn:
				return fn(args, prefix)

		except Exception as e:
			debug("\nERROR:An exception was caught :" + str(e) + "\n")
# ---------------------------------------------------------------------------------------------------------------------
class SampleProgram(object):

	def __init__(self , parser , config):
		self.parser = parser
		self.config = config

	def __call__(self):
		log = logging.getLogger()
		if not self.parser :
			log.error("Parser attribute is not set. Call get_parser() method or create your own parser.")
			return False

		# integration with argcomplete python module (bash completion)
		try:
			import argcomplete
			argcomplete.autocomplete(self.parser)
		except ImportError as e :
			pass

		# parse cli arguments
		args = self.parser.parse_args()

		if getattr(args, 'debug'):
			log.setLevel(logging.DEBUG)
			streamHandler.setFormatter(myDebugFormat)
			print "------------- config ------------------"
			print self.config
			print "----------- processing ----------------"

			# run command
			args.__func__(args)
			return True
		else:
			try:
				# run command
				args.__func__(args)
				return True
			except ValueError as a :
				log.error("ValueError : " + str(a))
			except KeyboardInterrupt as a :
				log.warn("Keyboard interruption detected.")
			except Exception as a :
				log.error("unexcepted error : " + str(a))
			return False

# ---------------------------------------------------------------------------------------------------------------------
#
#
def query_yes_no(question, default="yes"):
	res = _query_yes_no(question, default)
	if res == "yes":
		return True
	else:
		return False

# ---------------------------------------------------------------------------------------------------------------------
#
#
def _query_yes_no(question, default="yes"):
	"""Ask a yes/no question via raw_input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is one of "yes" or "no".
	"""
	valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
			 "no":"no",     "n":"no"}
	if default == None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while 1:
		sys.stdout.write(question + prompt)
		try:
			choice = raw_input().lower()
		except KeyboardInterrupt as e :
			print
			return "no"
		if default is not None and choice == '':
			return default
		elif choice in valid.keys():
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'yes' or 'no' "\
			                 "(or 'y' or 'n').\n")
