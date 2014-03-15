# Argtoolbox

## Description

It helps to build a command line tool with argparse module.
It also use ConfigParser module to store default values into a 
configuration file store in your profile.

It checks the data type, if it is required, etc... without repeat your
constraint once for the config file, and another time for the cli parser.
Usefull trick, data store in the configuration file can be used as the 
default value of the argparse argument.

This lets you focus on the command you want to do, not the input processing
(cli or config file)

Every program build with this tool have auto complete support on options and
arguments through argcomplete module.


## Installation

You can install dependencies using : `pip install -r requirements.txt`.

Then, you can install the argtoolbox module : `pip install argtoolbox`.


## QuickStart : Very Basic Usage

### 1. Imports :

First of all, you just need the following classes to build your own script :

* __DefaultCommand :__ The default class to extend in order to create your own
  command class.

* __BasicProgram :__ The most simple program to run your command classes.


### 2. Declaration :

There is a script called sample-program.py which contains all the following
lines of code.

1. First you have to create your command class TestCommand. (**Step 1**)
2. In the `__call__` method, you can do every thing you want. The first and only
   arg of this method is the args object created by Argparse.parser. (**Step
2**)
3. You create an other class MyProgram (which extends the BasicProgram) (**Step
   3**)
4. Now you create your  `argparse.parser` and your declare your argument, option
   and command. (**Step 4**)
5. Finally you just have to instanciate your class MyProgram and run it. (**Step
   5**).




```
#! /usr/bin/env python2
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK


from argtoolbox import DefaultCommand
from argtoolbox import BasicProgram

# Step 1
class TestCommand(DefaultCommand):
    """Just a simple command, using the default command class.
    It will print the inputs args to stdout"""

    def __call__(self, args):
        super(TestCommand, self).__call__(args)
        # Step 2
        print ""
        print "This is the beginning of the TestCommand class."
        print "The command line arguments (argv) : "
        print "------------------------------------"
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


# Step 5
if __name__ == "__main__":

    PROG = MyProgram("sample-program",
                        desc="""Just a description for a sample program.""")
    PROG()
```



### 3. Utilisation :

Now you can show the help menu using the following command :

`$ ./sample-program.py test -h`

__Console ouput :__
```
usage: sample-program test [-h] --message MESSAGE

optional arguments:
  -h, --help         show this help message and exit
  --message MESSAGE
```


Or run your command :

`$ ./sample-program.py test --host 127.0.0.1`

__Console ouput :__
```
This is the beginning of the TestCommand class.
The command line arguments (argv) : 
------------------------------------
Namespace(__func__=<__main__.TestCommand object at 0xb721a92c>,
config_file=None, host='127.0.0.1', port=3000, verbose=False)

This is the end of the TestCommand class.
```

You can see the variable `host` contains the input message `127.0.0.1` into the
args object.
The option `port` contains the default value `3000`.


## Advanced usage
At this point, this program does not do much more than the argparse module can
do. 
In the cas you have a lot of command and option, it could be usefull to store
default values in a configuration file like `sample-program.cfg`


### 1. Imports :

First of all, you just need the following classes to build your own script :

* __TestCommand :__ This command class will print to stdout the inputs args and
  the configuration file content.

* __BasicProgram :__ The most simple program to run your command classes.

* __SimpleSection :__ This class is used to declare a Section in the config file
  (ConfigFile)

* __Element :__ This class is used to declare an Option (a field) in the
  previous section.

* __Base64ElementHook :__ This hook is used as a post reading processing in
  order to convert
    base64 data stored into the config file into plain text data.

  

### 2. Declaration :

There is a script called sample-program2.py which contains all the following
lines of code.


1. Instead of creating a config file, we will use an in-memory config file
   (**Step 1**)
2. You create an other class MyProgram (which extends the BasicProgram) (**Step
   2**)
3. We override the default method called `add_config_options`. (**Step 3**)
4. We declare the section named `ldap` that we are looking for. (**Step 4**)
5. We declare all the fields store into the previous section.
For each fied, you can says if it is required, the default value, the type, an
optional description.
See the documentatino for more details. (**Step 5**)
6. The we declare all argparse arguments using the previous configuration
   declaration.
This is very usefull because the data store into the configuration file are used
as the default value for the argparse argument. The description, the type,
required or not, ... declared in the `add_config_options` method are used to
configure the parser argument. No need to repeat your self. (**Step 6**)
7. Declaration of the `test` argument using TestCommand class. (**Step 7**)
8. Finally you just have to instanciate your class MyProgram, the first argument
   is the program name. (**Step 8**)
9. We override the default config file name `'.<program name>.cfg'`. (**Step
   9**)
10. We launch the program. (**Step 10**)


```

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


if __name__ ≡ "__main__":

    # Step 8
    PROG = MyProgram("sample-program",
        # Step 9
                     config_file=io.BytesIO(SAMPLE_CONFIG),
                     desc="""Just a description for a sample program.""")
    # Step 10
    PROG()
```


