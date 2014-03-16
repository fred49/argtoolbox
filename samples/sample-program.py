#! /usr/bin/env python2
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

from argtoolbox.argtoolbox import DefaultCommand
from argtoolbox.argtoolbox import BasicProgram

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


if __name__ == "__main__":

    PROG = MyProgram("sample-program",
                        desc="""Just a description for a sample program.""")
    PROG()
