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

from fmatoolbox import *

import random
import unittest
import StringIO
import io


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
	sample_config = """[DEFAULT]
elt_type_int=5
elt_type_str=bbb
elt_type_str2=bbb
elt_type_bool= False
elt_type_float = 1.00009
elt_required=
elt_no_value=

\n"""
	self.c = Config("linshare-cli" , config_file = io.BytesIO(sample_config), description = " simple user cli for linshare")
	self.s = self.c.get_default_section()
 
	#s.add_element(Element('elt_type', e_type=int, default = 8))

        #self.assertRaises(TypeError, self.c.load())
	#AttributeError:

    def test_required(self):
	self.s.add_element(Element('elt_missing', required=True))
        self.assertRaises(ValueError, self.c.load)

    def test_required_without_value(self):
	self.s.add_element(Element('elt_required', default="plop", required=True))
        self.assertRaises(ValueError, self.c.load)

    def test_required_without_value_without_default(self):
	self.s.add_element(Element('elt_required', required=True))
        self.assertRaises(ValueError, self.c.load)

    def test_not_present(self):
	self.s.add_element(Element('elt_missing'))
	self.c.load()
	self.assertEqual(None, self.c.default.elt_missing)

    def test_not_present_with_default(self):
	self.s.add_element(Element('elt_missing', e_type=int, default = 8))
	self.c.load()
	self.assertEqual(8, self.c.default.elt_missing)

    def test_type_int(self):
	self.s.add_element(Element('elt_type_int', e_type=int))
	self.c.load()
	self.assertEqual(5, self.c.default.elt_type_int)

    def test_type_str(self):
	self.s.add_element(Element('elt_type_str'))
	self.c.load()
	self.assertEqual("bbb", self.c.default.elt_type_str)

    def test_type_bool(self):
	self.s.add_element(Element('elt_type_bool', e_type=bool))
	self.c.load()
	self.assertTrue(self.c.default.elt_type_bool)

    def test_type_float(self):
	self.s.add_element(Element('elt_type_float', e_type=float))
	self.c.load()
	self.assertEqual(1.00009, self.c.default.elt_type_float)


    def test_type_wrong_int(self):
	self.s.add_element(Element('elt_type_str2', e_type=int))
        self.assertRaises(ValueError, self.c.load)

    def test_without_default_without_value_str(self):
	self.s.add_element(Element('elt_no_value'))
        self.assertRaises(ValueError, self.c.load)
	self.assertEqual(None, self.c.default.elt_no_value)

    def test_without_default_without_value_int(self):
	self.s.add_element(Element('elt_no_value', e_type=int))
        self.assertRaises(ValueError, self.c.load)

    def test_without_default_without_value_float(self):
	self.s.add_element(Element('elt_no_value', e_type=float))
        self.assertRaises(ValueError, self.c.load)

if __name__ == '__main__':
    unittest.main()
