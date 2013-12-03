#!/usr/bin/python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK


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


import os , sys , io
import logging
import getpass
import base64
import copy
import datetime
from ordereddict import OrderedDict
import ConfigParser
import argparse


# ---------------------------------------------------------------------------------------------------------------------
# global logger variable
#log = logging.getLogger('fmatoolbox')
#log.setLevel(logging.INFO)
#log.setLevel(logging.DEBUG)
# logger formats
default_logging_format = logging.Formatter("%(asctime)s %(levelname)-8s: %(message)s", "%H:%M:%S")
debug_logging_format = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s:%(funcName)s:%(message)s", "%H:%M:%S")
# logger handlers
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(default_logging_format)

# debug mode
# if you need debug during class construction, file config loading, ...,  you need to modify the logger level here.
if False:
#if True:
	log.addHandler(streamHandler)
	log.setLevel(logging.DEBUG)
	streamHandler.setFormatter(debug_logging_format)



# ---------------------------------------------------------------------------------------------------------------------
class DefaultHook(object):
	def __init__(self):
		pass

	def __call__(self, elt):
		pass

# ---------------------------------------------------------------------------------------------------------------------
class Base64ElementHook(DefaultHook):
	def __init__(self, warning = False):
		self.warning = warning

	def __call__(self, elt):
		if elt.value :
			try:
				data = base64.b64decode(elt.value)
				elt.value = data
			except TypeError as e:
				if self.warning :
					log = logging.getLogger('fmatoolbox')
					log.warn("current field '%(name)s' is not stored in the configuration file with base64 encoding" , { "name" : elt.name })
				else :
					raise e
# ---------------------------------------------------------------------------------------------------------------------
class SectionHook(object):
	def __init__(self, section, attribute, opt_name):
		if not issubclass(section.__class__, AbstractSection):
			raise TypeError("First argument should be a subclass of Section.")
		self.section = section

		if not isinstance(attribute, str):
			raise TypeError("Second argument should be a string, attribute name.")
		self.attribute = attribute

		if not isinstance(opt_name, str):
			raise TypeError("Third argument should be a string, option name.")
		self.opt_name = opt_name

	def __call__(self , args):
		value = getattr(args, self.opt_name)
		if value != None :
			setattr(self.section , self.attribute, value)

# ---------------------------------------------------------------------------------------------------------------------
class Config(object):

	def __init__(self, prog_name, config_file = None, desc = None, mandatory = False ) :
		self.prog_name = prog_name
		self.config_file = config_file
		self.desc = desc
		self.mandatory = mandatory

		self.sections = OrderedDict()
		self._default_section = self.add_section(SimpleSection("DEFAULT"))
		self.parser = None

	def add_section(self, section):
		if not issubclass(section.__class__, AbstractSection):
			raise TypeError("argument should be a subclass of Section")
		self.sections[section.name] = section
		return section

	def get_default_section(self):
		return self._default_section

	def load(self):
		log = logging.getLogger('fmatoolbox')
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
			log.debug("defaultFileList: " + str(defaultFileList))
			discoveredFileList = self.fileParser.read(defaultFileList)

		log.debug("discoveredFileList: " + str(discoveredFileList))

		if self.mandatory and len(discoveredFileList) < 1 :
			msg="The required config file was missing. Default config files : " + str(defaultFileList)
			log.error(msg)
			raise EnvironmentError(msg)

		#print self.fileParser.items("DEFAULT")
		log.debug("loading configuration ...")
		for s in self.sections.values():
			log.debug("loading section : " + s.get_section_name())
			s.load(self.fileParser)
		log.debug("configuration loaded.")

	def get_parser(self , **kwargs):
		self.parser = argparse.ArgumentParser( prog = self.prog_name , description=self.desc, add_help = False,  **kwargs)
		# help is removed because parser.parse_known_args() show help, often partial help.
		# help action will be added during reloading step for parser.parse_args()
		self.parser.add_argument('-c', '--config-file',	action="store", help="Other configuration file.")
		return self.parser

	def reload(self , hooks = None):
		# Parsing the command line looking for the previous options like configuration file name or server section. Extra arguments will be store into argv.
		args , argv = self.parser.parse_known_args()

		if hooks != None :
			if isinstance(hooks, list) :
				for h in hooks :
					if isinstance(h, SectionHook):
						h(args)
			else:
				if isinstance(hooks, SectionHook):
					hooks(args)

		# After the first argument parsing, for configuration reloading, we can add the help action.
		self.parser.add_argument('-h', '--help',		action='help', 		default=argparse.SUPPRESS, help='show this help message and exit')

		# Reloading
		log = logging.getLogger('fmatoolbox')
		log.debug("reloading configuration ...")
		if args.config_file :
			self.fileParser.read(args.config_file)
		for s in self.sections.values():
			log.debug("loading section : " + s.get_section_name())
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

	def __str__(self):
		res = []
		res.append("Configuration of %(prog_name)s : " % self.__dict__)
		for s in self.sections.values():
			res.append("".join(s.get_representation("\t")))
		return "\n".join(res)

	def write_default_config_file(self , output , comments = True):
		log = logging.getLogger('fmatoolbox')
		with open(output, 'w') as f:
			if comments :
				f.write("#####################################\n")
				f.write("Description :\n")
				f.write("-------------\n")
				f.write(self.desc)
				f.write("\n\n")

			for s in self.sections.values():
				log.debug("loading section : " + s.get_section_name())
				s.write_config_file(f , comments)
		log.debug("config file generation complete : " + str(output))

# ---------------------------------------------------------------------------------------------------------------------
class AbstractSection(object):

	def __init__(self, desc = None, prefix = None, suffix = None, required = False):
		self.name = None
		self.desc = desc
		self.prefix = prefix
		self.suffix = suffix
		self.required = required

	def get_section_name(self):
		a = []
		if self.prefix :
			a.append(self.prefix)
		a.append(str(self.name))
		if self.suffix:
			a.append(self.suffix)
		return "-".join(a)

	def load(self, fileParser):
		raise NotImplemented("You must implement this method.")

	def get_representation(self , prefix = "" , suffix = "\n"):
		res = prefix + "Section " + self.get_section_name().upper() + suffix 
		return res

	def __str__(self):
		return "".join(self.get_representation())

	def write_config_file(self , f , comments):
		if comments :
			f.write("#####################################\n")
			f.write("# Section : " + "".join(self.get_representation()) + "\n")
			f.write("#####################################\n")
		f.write("[" + self.name + "]\n")
		if self.desc and comments:
			f.write("# Description : ")
			f.write(self.desc)
			f.write("\n")

# ---------------------------------------------------------------------------------------------------------------------
class Section(AbstractSection):

	def __init__(self, *args, **kwargs):
		super(Section, self).__init__(*args, **kwargs)
		self.elements = OrderedDict()

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
		section = self.get_section_name()
		try:
			for e in self.elements.values() :
				e.load(fileParser, section)
		except ConfigParser.NoSectionError as e:
			log = logging.getLogger('fmatoolbox')
			if self.required == True:
				log.error("Required section : " + section)
				raise ValueError(e)
			else:
				log.debug("Missing section : "  + section)

	def __getattr__(self, name):
		e = self.elements.get(name)
		if e :
			return e
		else:
			raise AttributeError("'%(class)s' object has no attribute '%(name)s'" 
						% { "name" : name, "class" : self.__class__.__name__ } )

	def write_config_file(self , f , comments):
		if len(self.elements) < 1 :
			return
		super(Section,self).write_config_file(f, comments)

		for e in self.elements.values() :
			e.write_config_file(f , comments)
		f.write("\n")

# ---------------------------------------------------------------------------------------------------------------------
class SimpleSection(Section):

	def __init__(self, name, *args, **kwargs):
		super(SimpleSection, self).__init__(*args, **kwargs)
		self.name = name

	def get_representation(self , prefix = "" , suffix = "\n"):
		res = []
		if self.count() > 0:
			res.append(prefix + "Section " + self.get_section_name().upper() + suffix)
			for elt in self.elements.values():
				res.append("".join(elt.get_representation(prefix)))
		return res

# ---------------------------------------------------------------------------------------------------------------------
class SubSection(Section):

	def get_representation(self , prefix = "" , suffix = "\n"):
		res = []
		if self.count() > 0:
			res.append(prefix + "SubSection : " + self.get_section_name().upper() + suffix)
			for elt in self.elements.values():
				res.append("".join(elt.get_representation(prefix)))
		return res

	def __copy__(self):
		newone = type(self)()
		newone.__dict__.update(self.__dict__)
		self.elements = OrderedDict()
		return newone

	def __deepcopy__(self, *args):
		newone = type(self)()
		newone.__dict__.update(self.__dict__)
		newone.elements = OrderedDict()
		for e in self.elements.values():
			newone.add_element(copy.deepcopy(e))
		return newone

# ---------------------------------------------------------------------------------------------------------------------
class ListSection(AbstractSection):
	def __init__(self, name, *args, **kwargs):
		super(ListSection, self).__init__(*args, **kwargs)
		self.elements = OrderedDict()
		self.name = name

	def load(self, fileParser):

		section = self.get_section_name()
		try:
			for key in [ item for item in fileParser.options(section) if item not in fileParser.defaults().keys() ]:
				self.elements[key] = fileParser.get(section, key)
		except ConfigParser.NoSectionError as e:
			log = logging.getLogger('fmatoolbox')
			if self.required == True:
				log.error("Required section : " + section)
				raise ValueError(e)
			else:
				log.debug("Missing section : "  + section)


	def get_representation(self , prefix = "" , suffix = "\n"):
		res = []
		res.append(prefix + "Section " + self.name + suffix)

		for key, val in self.elements.items():
			a = []
			a.append(prefix)
			a.append(" - " + str(key) + " : " + str(val))
			a.append(suffix)
			res.append("".join(a))
		return res

	def __getattr__(self, name):

		e = self.elements.get(name)
		if e != None :
			return e
		else:
			raise AttributeError("'%(class)s' object has no attribute '%(name)s'" 
						% { "name" : name, "class" : self.__class__.__name__ } )

# ---------------------------------------------------------------------------------------------------------------------
class Element(object):

	def __init__(self, name, e_type = str, required = False, default = None, conf_hidden = False, conf_required = False, desc = None, hooks = [ DefaultHook() ], hidden = False ):
		"""Information about how to declare a element to load from a configuration file.

	Keyword Arguments:

	- name	-- name of the attribute store into the configuration file.

	- e_type -- Data type of the attribute.

	- conf_required -- The current attribute must be present in the configuration file.

	- required -- The current attribute must be present into command line arguments except if it is present into configuration file.

	- default -- Default value used if the attribute is not set in configuration file.
		This value is also used during configuration file generation.
		ex: 'attribute = $default_value' or  ';attribute = $default_value' if this attribute is mandatory.

	- desc -- Description used into the configuration file and argparse.

	- conf_hidden -- The current attribute will not be used during configuration file generation.

	- hidden -- The current attribute will not be print on console (ex password)

	- hooks -- one hook or a list of hook. Should be an instance of DefaultHook. The hook well be apply to the element value once read from config file.

	"""

		self.name = name
		self.e_type = e_type
		self.required = required
		self.default = default
		self.desc = desc
		self.conf_hidden = conf_hidden
		self.conf_required  = conf_required
		self.desc_for_config = None
		self.desc_for_argparse = None
		self.value = None
		self.hidden = hidden
		self.hooks = hooks

		for h in hooks :
			if not isinstance(h, DefaultHook):
				raise TypeError("hook argument should be a subclass of DefaultHook")

	def get_representation(self , prefix = "" , suffix = "\n"):
		res = []
		if self.hidden :
			res.append(prefix + " - " + str(self.name) + " : xxxxxxxx" + suffix)
		else:
			res.append(prefix + " - " + str(self.name) + " : " + str(self.value) + suffix)
		return res

	def __str__(self):
		return "".join(self.get_representation())

	def __copy__(self):
		newone = type(self)(self.name)
		newone.__dict__.update(self.__dict__)
		self.elements = OrderedDict()
		return newone

	def post_load(self):
		for h in self.hooks :
			h(self)

	def set_value(self, val):
		if not instance(val, self.e_type):
			raise TypeError("Element value from config called '%(name)s' should have the type : '%(e_type)s'" 
				 % { "name": self.name , "e_type" : self.e_type })
		self.value = val

	def load(self, fileParser, section_name):
		self._load(fileParser , section_name)
		self.post_load()

	def _load(self, fileParser, section_name):
		log = logging.getLogger('fmatoolbox')
		try:
			log.debug("looking for field (section=" + section_name + ") : " + self.name )
			data = None
			try:
				if self.e_type == int :
					data = fileParser.getint( section_name, self.name)
				elif self.e_type == float :
					data = fileParser.getfloat( section_name, self.name)
				elif self.e_type == bool :
					data = fileParser.getboolean( section_name, self.name)
				elif self.e_type == list :
					data = fileParser.get( section_name, self.name)
					data = data.strip().split()
					if not data :
						msg = "The optional field '%(name)s' was present, type is list, but the current value is an empty list." % { "name": self.name }
						log.error(msg)
						raise ValueError(msg)
				elif self.e_type == str:
					data = fileParser.get( section_name, self.name)
					# happens only when the current field is present, type is string, but value is ''
					if not data :
						msg = "The optional field '%(name)s' was present, type is string, but the current value is an empty string." % { "name": self.name }
						log.error(msg)
						raise ValueError(msg)
				else:
					msg = "Data type not supported : %(type)s" % { "type": self.e_type}
					log.error(msg)
					raise TypeError(msg)

			except  ValueError as e:
				msg = "The current field '%(name)s' was present, but the required type is : %(e_type)s."  % { "name": self.name , "e_type" : self.e_type }
				log.error(msg)
				log.error(str(e))
				raise ValueError(str(e))

			log_data = { "name": self.name , "data": data , "e_type" : self.e_type}
			if self.hidden :
				log_data['data'] = "xxxxxxxx"
			log.debug("field found : '%(name)s', value : '%(data)s', type : '%(e_type)s'" , log_data )
			self.value = data

		except ConfigParser.NoOptionError :
			if self.conf_required :
				msg = "The required field " + self.name  + " was missing from the config file."
				log.error(msg)
				raise ValueError(msg)

			if self.default != None :
				self.value = self.default
				log_data = { "name": self.name , "data": self.default, "e_type" : self.e_type}
				if self.hidden :
					log_data['data'] = "xxxxxxxx"
				log.debug("Field not found : '%(name)s', default value : '%(data)s', type : '%(e_type)s'" , log_data )
			else:
				log.debug("Field not found : " + self.name)


	def get_arg_parse_arguments(self):
		ret = dict()
		if self.required :
			if self.value != None :
				ret["default"] = self.value
			else:
				ret["required"] = True
		ret["dest"] = self.name
		if self.value != None :
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


		if not self.conf_required:
			f.write(";")
		f.write(self.name)
		f.write("=")
		if self.default != None and not self.hidden:
			f.write(str(self.default))
		f.write("\n")

# ---------------------------------------------------------------------------------------------------------------------
class ElementWithSubSections(Element):

	def __init__(self, *args, **kwargs):
		super(ElementWithSubSections, self).__init__(*args, **kwargs)
		self.e_type = str
		self.sections= OrderedDict()

	def get_representation(self , prefix = "" , suffix = "\n"):
		res = ['\n']
		if self.hidden :
			res.append(prefix + " - " + str(self.name) + " : xxxxxxxx" + suffix)
		else:
			res.append(prefix + " - " + str(self.name) + " : " + str(self.value) + suffix)

		if len(self.sections) > 0:
			for elt in self.sections.values():
				res.append("".join(elt.get_representation(prefix + "\t")))
		return res

	def add_section(self, section):
		if not issubclass(section.__class__, SubSection):
			raise TypeError("Argument should be a subclass of SubSection, not :" + str(section.__class__) )
		self.sections[section.name] = section
		return section

	def load(self, fileParser, section_name):
		self._load(fileParser , section_name)
		if len(self.sections) > 0:
			for sec in self.sections.values():
				sec.name = self.value
				sec.load(fileParser)
		self.post_load()


# ---------------------------------------------------------------------------------------------------------------------
class ElementWithRelativeSubSection(ElementWithSubSections):

	def __init__(self, name, rss, **kwargs):
		super(ElementWithRelativeSubSection, self).__init__(name, **kwargs)
		self.e_type = list
		if not issubclass(rss.__class__, SubSection):
			raise TypeError("Argument should be a subclass of SubSection, not :" + str(section.__class__) )
		self.rss = rss

	def load(self, fileParser, section_name):
		self._load(fileParser , section_name)
		for sec_name in self.value :
			try:
				sec = copy.deepcopy(self.rss, None)
				sec.name = sec_name
				self.sections[sec_name] = sec
				sec.load(fileParser)
			except ValueError as e:
				log = logging.getLogger('fmatoolbox')
				log.error("Missing relative section, attribute : '[" + section_name + "]." + self.name + "', value : " + str(self.value))
				raise ValueError(e)
		self.post_load()

	def get_representation(self , prefix = "" , suffix = "\n"):
		res = ['\n']
		if self.hidden :
			res.append(prefix + " - " + str(self.name) + " : xxxxxxxx" + suffix)
		else:
			res.append(prefix + " - " + str(self.name) + " : " + str(self.value) + suffix)

		if len(self.sections) > 0:
			for elt in self.sections.values():
				res.append('\n')
				res.append("".join(elt.get_representation(prefix + "\t")))
		return res


# ---------------------------------------------------------------------------------------------------------------------
class DefaultCommand(object):

	def __init__(self, config = None):
		self.log = logging.getLogger('fmatoolbox' + "." + str(self.__class__.__name__.lower()))
		self.config =  config

	def __call__(self, args):
		# suppress __func__ object ang password just for display
		dict_tmp=copy.copy(args)
		delattr(dict_tmp, "__func__")
		#delattr(dict_tmp, "password")
		if hasattr(dict_tmp, "password"):
			setattr(dict_tmp, "password" , "xxx")
		self.log.debug("Namespace : begin :")
		for i in dict_tmp.__dict__:
			self.log.debug(i + " : " + str(getattr(dict_tmp, i)))
		self.log.debug("Namespace : end.")

	def complete(self, args,  prefix):
		"""Auto complete method, args is comming from argparse and prefix is the input data from command line.
		You must return a list."""
                return []

# ---------------------------------------------------------------------------------------------------------------------
class TestCommand(DefaultCommand):

	def __call__(self, args):
		super(TestCommand, self).__call__(args)
		print "Test command :"
		print "=============="
		print "argv : "
		print "-------"
		print args
		print "---------"
		print "config : "
		print "---------"
		print self.config

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
class DefaultProgram(object):

	def __init__(self , parser , config):
		self.parser = parser
		self.config = config

	def __call__(self):
		# integration with argcomplete python module (bash completion)
		try:
			import argcomplete
			argcomplete.autocomplete(self.parser)
		except ImportError as e :
			pass

		# parse cli arguments
		args = self.parser.parse_args()

		if getattr(args, 'debug'):
			llog = logging.getLogger()
			llog.setLevel(logging.DEBUG)
			streamHandler.setFormatter(debug_logging_format)
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
				log = logging.getLogger('fmatoolbox')
				log.error("ValueError : " + str(a))
			except KeyboardInterrupt as a :
				log = logging.getLogger('fmatoolbox')
				log.warn("Keyboard interruption detected.")
			except Exception as a :
				log = logging.getLogger('fmatoolbox')
				log.error("unexcepted error : " + str(a))
			return False

# ---------------------------------------------------------------------------------------------------------------------
def query_yes_no(question, default="yes"):
	res = _query_yes_no(question, default)
	if res == "yes":
		return True
	else:
		return False

# ---------------------------------------------------------------------------------------------------------------------
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



# ---------------------------------------------------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__" :

	sample_config = """
[ldap]

host=127.0.0.1
port=389
suffix=dc=nodomain
account=cn=admin,dc=nodomain
password=toto

\n"""

	# logger
	log = logging.getLogger()
	log.setLevel(logging.INFO)
	# logger handlers
	log.addHandler(streamHandler)
	# debug mode
	# if you need debug during class construction, file config loading, ...,  you need to modify the logger level here.
	#log.setLevel(logging.DEBUG)
	#streamHandler.setFormatter(debug_logging_format)

	# create configuration
	config = Config("sample-program" , config_file = io.BytesIO(sample_config), desc= """Just a description for a sample program. This program supports argcomplete.
To enable it, run in bash terminal :
	eval "$(register-python-argcomplete fmatoolbox.py)"
""")

	# section ldap
	section_ldap = config.add_section(SimpleSection("ldap"))
	section_ldap.add_element(Element('debug',	e_type=int,	default=0, desc="""debug level : default : 0."""))
	section_ldap.add_element(Element('host',	required=True,	default = "192.168.1.1"))
	section_ldap.add_element(Element('account',	required=True))
	section_ldap.add_element(Element('port',	e_type=int))
	section_ldap.add_element(Element('password',	required=True,	hidden=True, desc = "account password to ldap",
						 hooks = [ Base64ElementHook(),] ))

	# loading default configuration
	config.load()

	# ---------------------------------------------------------------------------------------------------------------------
	# arguments parser
	# ---------------------------------------------------------------------------------------------------------------------
	parser = config.get_parser(formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('-d',			action="count",		**config.ldap.debug.get_arg_parse_arguments())
	parser.add_argument('-v', '--verbose',		action="store_true", default=False)
	parser.add_argument('--version',		action="version", version="%(prog)s 0.1")

	# reloading configuration with previous optional arguments (ex config file name from argv, ...)
	config.reload()

	# Adding all others parsers.
	subparsers = parser.add_subparsers()
	parser_tmp = subparsers.add_parser('test', help="This simple command print cli argv and configuration read form config file.")
	parser_tmp.set_defaults(__func__=TestCommand(config))

	# run
	prog = DefaultProgram(parser , config)
	if prog() :
		sys.exit(0)
	else :
		sys.exit(1)
