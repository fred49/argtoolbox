#! /usr/bin/env python2
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

import io
from argtoolbox import TestCommand
from argtoolbox import BasicProgram
from argtoolbox import SimpleSection, Element, Base64ElementHook

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
