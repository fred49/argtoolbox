#! /usr/bin/env python2
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

# This file is part of argtoolbox.
#
# argtoolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# argtoolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare user cli.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014 Frédéric MARTIN
#
# Contributors list:
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#



import io
from argtoolbox import BasicProgram
from argtoolbox import TestCommand
from argtoolbox import SimpleSection, Element, Base64ElementHook

# if you want to debug argcomplete completion,
# you just need to export _ARC_DEBUG=True

# Step 1
SAMPLE_CONFIG = """
[ldap]

host=127.0.0.1
port=389
suffix=dc=nodomain
account=cn=admin,dc=nodomain
password=toto

\n"""


# Step 2
class MyProgram(BasicProgram):

    # Step 3
    def add_config_options(self):
        # Step 4
        # section ldap
        section_ldap = self.config.add_section(SimpleSection("ldap"))
        # Step 5
        section_ldap.add_element(Element('debug',
                                         e_type=int,
                                         default=0,
                                         desc="""debug level : default : 0."""))
        section_ldap.add_element(Element('host',
                                         required=True,
                                         default="192.168.1.1"))
        section_ldap.add_element(Element('account', required=True))
        section_ldap.add_element(Element('port', e_type=int))
        section_ldap.add_element(Element('password',
                                         required=True,
                                         hidden=True,
                                         desc="account password to ldap",
                                         hooks=[Base64ElementHook(), ]))


    def add_commands(self):
        # Step 6
        self.parser.add_argument(
            '--host', **self.config.ldap.host.get_arg_parse_arguments())
        self.parser.add_argument(
            '--port', **self.config.ldap.port.get_arg_parse_arguments())
        self.parser.add_argument(
            '-d',
            action="count",
            **self.config.ldap.debug.get_arg_parse_arguments())

        # Step 7
        subparsers = self.parser.add_subparsers()
        parser_tmp = subparsers.add_parser(
            'test',
            help="This simple command print cli argv and configuration read \
            form config file.")
        parser_tmp.set_defaults(__func__=TestCommand(self.config))


if __name__ == "__main__":
    # Step 8
    PROG = MyProgram("sample-program",
                     # Step 9
                     config_file=io.BytesIO(SAMPLE_CONFIG),
                     desc="""Just a description for a sample program.""")
    # Step 10
    PROG()
