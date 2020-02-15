#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""TODO"""
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



import sys
import stat
import os
import shutil
import uuid
import tempfile
import importlib
import inspect
import logging
import argparse
from .argtoolbox import Config
from .argtoolbox import BasicProgram
from .argtoolbox import DefaultProgram
from .argtoolbox import DefaultCommand
from .argtoolbox import DefaultCompleter as Completer
from .argtoolbox import query_yes_no


# if you want to debug argcomplete completion,
# you just need to export _ARC_DEBUG=True

class ConfigGenerationCommand(DefaultCommand):
    """Deprecated. This command read a existing program and generate the associated
    configuration file"""

    def __call__(self, args):
        self.log.debug("args: %s", args)
        if args.debug:
            self.log.setLevel(logging.DEBUG)
        config = self.getconfig(args.program)
        return self.generate(args, config)

    def getconfig(self, program):
        """Looking for a Config Object into the input program."""
        self.log.info("Looking for Config object into input program ...")
        self.log.debug("input program name : '%s'", program)

        for path in os.environ['PATH'].split(':'):
            if os.path.isdir(path):
                for fil in os.listdir(path):
                    fullfile = path + "/" + fil
                    if os.path.isfile(fullfile) or os.path.islink(fullfile):
                        if fil == program:
                            program = fullfile
                            break
        self.log.info("Program found : %s", program)
        if not os.path.exists(program):
            self.log.error("the current input program does not exist : %s", program)
            raise IOError('No such file')

        dest = os.path.join(
            tempfile.gettempdir(),
            str(uuid.uuid4()).replace("-", "") + ".py")
        shutil.copyfile(program, dest)

        program = dest

        local_dir = os.path.dirname(program)
        self.log.debug("local_dir : '%s'", local_dir)
        sys.path.append(local_dir)

        module_name = program.split('/')[-1].split('.')[0]
        self.log.debug("module name found : %s", module_name)

        # level = logging.getLogger().getEffectiveLevel()
        module = importlib.import_module(module_name)
        # self.log.setLevel(level)
        self.log.debug("module loaded : %s", module)
        result = None
        for i in dir(module):
            temp_class = getattr(module, i)
            if isinstance(temp_class, Config):
                self.log.debug("variable name found : %s", i)
                self.log.debug("variable type found : %s", type(temp_class))
                result = temp_class
                break
            elif isinstance(temp_class, DefaultProgram):
                self.log.debug("variable name found : %s", i)
                self.log.debug("variable type found : %s", type(temp_class))
                result = temp_class.config
                break
            elif isinstance(temp_class, BasicProgram):
                self.log.debug("variable name found : %s", i)
                self.log.debug("variable type found : %s", type(temp_class))
                temp_class.add_config_options()
                result = temp_class.config
                break
        os.remove(program)
        program += "c"
        if os.path.exists(program):
            os.remove(program)
        if result:
            self.log.info("Config object found : %s", result.prog_name)
            return result
        self.log.error("Can 't find config object.")
        raise ValueError("This script does not contain or support argtoolbox")

    def generate(self, args, config):
        """Generate the default configuration file from the config object"""
        self.log.info("Trying to generate the default configuration file ...")
        if not config.use_config_file:
            self.log.info(
                "The current program does not support a configuration file.")
            return True
        configfile = os.path.expanduser('~/.' + config.prog_name + '.cfg')
        self.log.info("The default configuration file name is : %s", configfile)
        if args.output:
            configfile = args.output
            if configfile[-4:] != ".cfg":
                configfile += ".cfg"
            self.log.warn("Using '%s' as configuration file name.", configfile)

        if not args.force_yes:
            if os.path.exists(configfile):
                self.log.warn(
                    "The current file already exists : %s", configfile)
                if not query_yes_no("Overwrite ?", "no"):
                    self.log.error("Aborted.")
                    return False
        config.write_default_config_file(configfile, args.nocomments)
        self.log.info("Done.")
        return True

    def complete_bin(self, args, prefix):
        """autocomplete binary file into the $PATH"""
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        results = []
        for path in os.environ['PATH'].split(':'):
            if os.path.isdir(path):
                for fil in os.listdir(path):
                    fullfile = path + "/" + fil
                    if os.path.isfile(fullfile) or os.path.islink(fullfile):
                        if fil.startswith(prefix):
                            results.append(fil)
        return results


class GenerateCommand(DefaultCommand):
    """The command is design to generate a sample program"""
    # pylint: disable=too-few-public-methods

    def __call__(self, args):
        filename = args.prog_name.lower()
        if filename[-3:] != ".py":
            filename += ".py"
        self.log.info("Trying to generate script: %s ...", filename)
        prog_name = args.prog_name
        if prog_name[-3:] == ".py":
            prog_name = prog_name[:-3]
        prog_name = prog_name.capitalize().replace('.', '')
        command_name = args.command_name.lower().replace('.', '_')
        path = os.path.dirname(inspect.getfile(Config))
        src = os.path.join(path, 'templates', 'default.tml')
        self.log.info("Loading template: %s", src)
        template = ""
        with open(src, 'r') as fde:
            template = fde.read()
        template = template.replace('#{prog_name}', prog_name)
        template = template.replace('#{prog_name_class}', prog_name.title())
        template = template.replace('#{command_name}', command_name)
        template = template.replace('#{command_name_class}', command_name.title())
        if args.description:
            template = template.replace('#{description}', args.description)
        if os.path.exists(filename):
            if not args.force_yes:
                self.log.error("Script %s already exists. Aborted. Try -f to force.", filename)
                return False
            self.log.warn("Overwriting script %s...", filename)
        with open(filename, 'w') as fde:
            template = fde.write(template)
        filename_stat = os.stat(filename)
        os.chmod(filename, filename_stat.st_mode | stat.S_IEXEC)
        self.log.info("Generated script %s with one command '%s'", filename, command_name)
        return True


class MyProgram(BasicProgram):
    """Main program"""

    def add_commands(self):
        super(MyProgram, self).add_commands()
        self.parser.formatter_class = argparse.RawTextHelpFormatter
        subparsers = self.parser.add_subparsers()
        self.add_command_new(subparsers)
        self.add_command_generate(subparsers)

    def add_command_new(self, subparsers):
        """TODO"""
        parser_tmp = subparsers.add_parser(
            'new',
            help="Create a new program based on default template")
        parser_tmp.add_argument("-d", "--description")
        parser_tmp.add_argument("-p", "--progname", dest="prog_name",
                                default="sample")
        parser_tmp.add_argument("-c", "--commandname", dest="command_name",
                                default="sample")
        parser_tmp.add_argument(
            '-f',
            dest="force_yes",
            action="store_true",
            help="overwrite the current output file even it still exists.")
        parser_tmp.set_defaults(__func__=GenerateCommand(self.config))

    def add_command_generate(self, subparsers):
        """TODO"""
        # pylint: disable=no-self-use
        parser_tmp = subparsers.add_parser(
            'generate',
            help=(
                "Scan an existing program and generate the associated configuration file."
                "\nDepreacted, it should be supported by the program it self."
            )
        )
        parser_tmp.add_argument('-o', '--output', action="store")
        parser_tmp.add_argument(
            'program',
            action="store").completer = Completer("complete_bin")
        parser_tmp.add_argument(
            '-n',
            dest="nocomments",
            action="store_false",
            help="config file generation without commments.")
        parser_tmp.add_argument(
            '-f',
            dest="force_yes",
            action="store_true",
            help="overwrite the current output file even it still exists.")
        parser_tmp.set_defaults(__func__=ConfigGenerationCommand())


class ConfigGenerationV2Command(object):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, prog):
        self.prog = prog
        self.log = logging.getLogger()

    def __call__(self, args):
        if args.debug:
            self.log.setLevel(logging.DEBUG)
        self.log.debug("args: %s", args)
        self.log.debug("config: %s", type(self.prog))
        self.prog.add_config_options()
        return self.generate(args, self.prog.config)

    def generate(self, args, config):
        """Generate the default configuration file from the config object"""
        self.log.info("Trying to generate the default configuration file ...")
        if not config.use_config_file:
            self.log.info(
                "The current program does not support a configuration file.")
            return True
        configfile = os.path.expanduser('~/.' + config.prog_name + '.cfg')
        self.log.info("The default configuration file name is : %s", configfile)
        if args.output:
            configfile = args.output
            if configfile[-4:] != ".cfg":
                configfile += ".cfg"
            self.log.warn("Using '%s' as configuration file name.", configfile)

        if not args.force_yes:
            if os.path.exists(configfile):
                self.log.warn(
                    "The current file already exists : %s", configfile)
                if not query_yes_no("Overwrite ?", "no"):
                    self.log.error("Aborted.")
                    return False
        config.write_default_config_file(configfile, args.nocomments)
        self.log.info("Done.")
        return True


def cli_generate_config(prog_name, config, description=None, command_name="generate",
                        command_class=ConfigGenerationV2Command):
    """TODO"""
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description=description,
        add_help=False)
    subparsers = parser.add_subparsers()
    parser_tmp = subparsers.add_parser(
        command_name,
        help="Generate the default configuration file for he current program")
    parser_tmp.add_argument('-o', '--output', action="store")
    parser_tmp.add_argument(
        '-n',
        dest="nocomments",
        action="store_false",
        help="config file generation without commments.")
    parser_tmp.add_argument(
        '-d',
        dest="debug",
        action="store_true")
    parser_tmp.add_argument(
        '-f',
        dest="force_yes",
        action="store_true",
        help="overwrite the current output file even it still exists.")
    parser_tmp.set_defaults(__func__=command_class(config))
    args = parser.parse_args()
    if not hasattr(args, '__func__'):
        parser.error("You must provide a command. See --help.")
    return args.__func__(args)


PROG = MyProgram(
    "argtoolbox_utils",
    use_config_file=False,
    desc="""This tool help you generate config file for
        program based on argtoolbox package, create new basic
    program, ... make your dev life easier !""")
if __name__ == "__main__":
    PROG()
