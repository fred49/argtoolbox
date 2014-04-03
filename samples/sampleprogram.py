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

from argtoolbox import DefaultCommand
from argtoolbox import BasicProgram

# Step 1
class TestCommand(DefaultCommand):
    """Just a simple command, using the default command class."""

    def __call__(self, args):
        super(TestCommand, self).__call__(args)
        # Step 2
        print ""
        print "This is the beginning of the TestCommand class."
        print "The command line arguments (argv) : "
        print "------------------------------------"
        print args
        print ""
        print "This is the end of the TestCommand class."
        print ""


# Step 3
class MyProgram(BasicProgram):

    def add_commands(self):
        # Step 4
        subparsers = self.parser.add_subparsers()
        parser_tmp = subparsers.add_parser(
            'test',
            help="This command will print cli argv and configuration read \
            from the config file.")
        parser_tmp.add_argument('--host', required=True)
        parser_tmp.add_argument('--port', default=3000)
        parser_tmp.set_defaults(__func__=TestCommand(self.config))


PROG = MyProgram("sample-program",
                 desc="""Just a description for a sample program.""")
if __name__ == "__main__":

    PROG()
