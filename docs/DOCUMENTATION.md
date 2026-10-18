# Argtoolbox - Comprehensive Documentation

## Table of Contents

1. [What is Argtoolbox?](#what-is-argtoolbox)
2. [Why Argtoolbox?](#why-argtoolbox)
3. [Core Concepts](#core-concepts)
4. [Architecture](#architecture)
5. [How It Works](#how-it-works)
6. [Getting Started](#getting-started)
7. [Basic Usage](#basic-usage)
8. [Advanced Usage](#advanced-usage)
9. [API Reference](#api-reference)
10. [Examples](#examples)
11. [Best Practices](#best-practices)

---

## What is Argtoolbox?

**Argtoolbox** is a Python library that simplifies the creation of command-line interface (CLI) tools by providing a unified framework that combines:

- **Argument parsing** (via Python's `argparse` module)
- **Configuration file management** (via Python's `ConfigParser` module)
- **Automatic bash completion** (via `argcomplete` module)
- **Type validation and constraints** in a single declaration

### Key Features

- **DRY Principle**: Define your options once, use them everywhere (CLI, config file, validation)
- **Seamless Integration**: Configuration file values serve as defaults for CLI arguments
- **Type Safety**: Built-in type checking for int, float, bool, str, and list
- **Auto-completion**: Bash completion support out of the box
- **⭐ Hierarchical INI Configurations**: Create complex, template-based, nested configurations using simple INI files - a unique and powerful feature! (See HIERARCHICAL_CONFIG.md for details)
- **Hooks System**: Post-processing hooks for values (e.g., base64 decoding)
- **Hidden Values**: Support for sensitive data (passwords) that are masked in output

---

## Why Argtoolbox?

### The Problem

When building CLI tools with Python, developers typically face these challenges:

1. **Duplication**: Declaring the same option multiple times:
   - Once for the config file schema
   - Again for argparse argument definition
   - Yet again for validation logic

2. **Inconsistency**: Config file values and CLI arguments may become out of sync

3. **Boilerplate**: Lots of repetitive code for reading config files, parsing arguments, validating inputs

4. **Maintenance**: Changes require updates in multiple places

### The Solution

Argtoolbox solves these problems by:

- **Single Source of Truth**: Declare each option once with all its properties
- **Automatic Propagation**: The same declaration configures both config file reading and CLI parsing
- **Built-in Validation**: Type checking and required field validation happen automatically
- **Config as Defaults**: Values from config files automatically become defaults for CLI arguments
- **Less Code, More Focus**: Focus on your application logic, not input processing

### Example Comparison

**Without Argtoolbox:**
```python
# Config file definition
config = ConfigParser()
config.read('myapp.cfg')
host = config.get('ldap', 'host')
port = config.getint('ldap', 'port')
if not host:
    raise ValueError("host is required")

# Argparse definition
parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, required=True,
                   default=host, help="LDAP host")
parser.add_argument('--port', type=int, default=port,
                   help="LDAP port")
```

**With Argtoolbox:**
```python
section_ldap = config.add_section(SimpleSection("ldap"))
section_ldap.add_element(Element('host', required=True))
section_ldap.add_element(Element('port', e_type=int))

# Auto-generates argparse arguments with config file defaults
parser.add_argument('--host',
                   **config.ldap.host.get_arg_parse_arguments())
parser.add_argument('--port',
                   **config.ldap.port.get_arg_parse_arguments())
```

---

## Core Concepts

### 1. Config Object
The central configuration manager that:
- Contains all sections and elements
- Manages config file reading/writing
- Provides the argparse parser
- Coordinates the CLI and config file integration

### 2. Sections
Logical groupings of related configuration options:
- **SimpleSection**: Basic section with named elements
- **ListSection**: Dynamic section that reads all key-value pairs
- **SubSection**: Nested section for hierarchical configurations

### 3. Elements
Individual configuration options with properties:
- Name
- Data type (str, int, float, bool, list)
- Required flag
- Default value
- Description
- Validation hooks

### 4. Commands
Actions that your CLI tool can perform:
- Extend `DefaultCommand` class
- Implement `__call__` method with business logic
- Access config and parsed arguments

### 5. Programs
The main entry point that orchestrates everything:
- **BasicProgram**: Standard program with config file support
- **DefaultProgram**: Lower-level program for custom workflows

### 6. Hooks
Post-processing functions applied after reading values:
- **DefaultHook**: Base class for custom hooks
- **Base64ElementHook**: Decodes base64-encoded values
- **SectionHook**: Updates section attributes from CLI args

---

## Architecture

### Component Hierarchy

```
BasicProgram (Your Main Class)
    ├── Config
    │   ├── Section (SimpleSection, ListSection, SubSection)
    │   │   ├── Element
    │   │   │   ├── Hooks (DefaultHook, Base64ElementHook)
    │   │   │   └── Value
    │   │   └── ...
    │   └── ConfigParser (from stdlib)
    ├── ArgumentParser (from argparse)
    └── Commands (DefaultCommand subclasses)
```

### Workflow

```
1. Program Initialization
   └── Config object created

2. Configuration Declaration
   └── add_config_options() called
       └── Sections and Elements defined

3. Config File Loading
   └── load() reads from file
       └── Elements populated with values
       └── Hooks applied

4. Parser Initialization
   └── get_parser() creates ArgumentParser
       └── add_commands() defines CLI arguments
           └── Elements provide argparse kwargs

5. Config Reloading
   └── reload() processes CLI args
       └── May override config file path
       └── Re-reads config if needed

6. Argument Parsing
   └── parse_args() runs argparse
       └── CLI values override config defaults

7. Command Execution
   └── Command's __call__ method runs
       └── Access to config and args
```

---

## How It Works

### The Magic: Single Declaration, Multiple Uses

When you declare an Element:

```python
Element('host',
        e_type=str,
        required=True,
        default="192.168.1.1",
        desc="LDAP server host")
```

This single declaration provides:

1. **Config File Reading**:
   - Reads `host` from the `[section]` in config file
   - Validates it's a string
   - Uses default if missing
   - Marks as required if not found and no default

2. **Argparse Integration**:
   - Via `get_arg_parse_arguments()` returns:
     ```python
     {
         'dest': 'host',
         'default': '<value from config or default>',
         'required': True if (required and no config value),
         'help': "LDAP server host"
     }
     ```

3. **Runtime Access**:
   - `config.section.host.value` gives the final value
   - Hidden values are masked in string representation

### Configuration File Flow

1. **Discovery**: Looks for config files in order:
   - `<progname>.cfg` (current directory)
   - `~/.<progname>.cfg` (user home)
   - `/etc/<progname>.cfg` (system-wide)

2. **Reading**: Uses ConfigParser to read INI-style format:
   ```ini
   [ldap]
   host=127.0.0.1
   port=389
   ```

3. **Type Conversion**: Automatically converts values:
   - `getint()` for int
   - `getfloat()` for float
   - `getboolean()` for bool
   - `split()` for list
   - `get()` for str

4. **Validation**: Checks required fields and types

5. **Hook Application**: Runs post-processing hooks

### CLI Integration Flow

1. **First Parse**: `parse_known_args()` to check for `--config-file`
2. **Reload**: If custom config file specified, reload configuration
3. **Second Parse**: `parse_args()` for full argument parsing
4. **Merging**: CLI values override config file values

### Type System

| Python Type | ConfigParser Method | Element e_type | Notes |
|-------------|-------------------|----------------|-------|
| `str` | `get()` | `str` | Default type |
| `int` | `getint()` | `int` | Validates integer |
| `float` | `getfloat()` | `float` | Validates float |
| `bool` | `getboolean()` | `bool` | Accepts True/False/Yes/No |
| `list` | `get() + split()` | `list` | Whitespace-separated values |

---

## Getting Started

### Installation

```bash
pip install argtoolbox
```

### Minimal Example

```python
#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from argtoolbox import DefaultCommand, BasicProgram

class HelloCommand(DefaultCommand):
    def __call__(self, args):
        print(f"Hello, {args.name}!")

class MyProgram(BasicProgram):
    def add_commands(self):
        subparsers = self.parser.add_subparsers()
        parser = subparsers.add_parser('hello', help="Say hello")
        parser.add_argument('--name', default="World")
        parser.set_defaults(__func__=HelloCommand(self.config))

if __name__ == "__main__":
    PROG = MyProgram("myapp", desc="My first argtoolbox app")
    PROG()
```

Usage:
```bash
$ ./myapp.py hello --name Alice
Hello, Alice!
```

---

## Basic Usage

### Step 1: Create a Command Class

Commands encapsulate your application logic.

```python
from argtoolbox import DefaultCommand

class MyCommand(DefaultCommand):
    def __call__(self, args):
        # Your logic here
        print("Command executed!")
        print(f"Args: {args}")
        # Access config: self.config
```

### Step 2: Create a Program Class

The program class orchestrates everything.

```python
from argtoolbox import BasicProgram

class MyProgram(BasicProgram):
    def add_commands(self):
        # Add CLI arguments and commands
        subparsers = self.parser.add_subparsers()

        parser_cmd = subparsers.add_parser(
            'mycommand',
            help="Description of my command"
        )
        parser_cmd.add_argument('--option', default="value")
        parser_cmd.set_defaults(__func__=MyCommand(self.config))
```

### Step 3: Instantiate and Run

```python
if __name__ == "__main__":
    PROG = MyProgram(
        "my-program",
        desc="Description of my program"
    )
    PROG()
```

### Running Your Program

```bash
# Show help
$ ./myprogram.py -h
$ ./myprogram.py mycommand -h

# Run command
$ ./myprogram.py mycommand --option value

# Enable debug mode
$ ./myprogram.py -d mycommand --option value
```

---

## Advanced Usage

### Using Configuration Files

#### Step 1: Define Configuration Structure

```python
from argtoolbox import BasicProgram, SimpleSection, Element

class MyProgram(BasicProgram):
    def add_config_options(self):
        # Create a section
        database = self.config.add_section(SimpleSection("database"))

        # Add elements to the section
        database.add_element(Element(
            'host',
            e_type=str,
            required=True,
            default="localhost",
            desc="Database host address"
        ))

        database.add_element(Element(
            'port',
            e_type=int,
            default=5432,
            desc="Database port"
        ))

        database.add_element(Element(
            'username',
            required=True,
            desc="Database username"
        ))

        database.add_element(Element(
            'password',
            required=True,
            hidden=True,  # Will be masked in output
            desc="Database password"
        ))
```

#### Step 2: Create Configuration File

Create `~/.my-program.cfg`:

```ini
[database]
host=192.168.1.100
port=5432
username=admin
password=secret123
```

#### Step 3: Use Configuration in Commands

```python
def add_commands(self):
    # Use config values as defaults for CLI args
    self.parser.add_argument(
        '--host',
        **self.config.database.host.get_arg_parse_arguments()
    )
    self.parser.add_argument(
        '--port',
        **self.config.database.port.get_arg_parse_arguments()
    )

    subparsers = self.parser.add_subparsers()
    parser_cmd = subparsers.add_parser('connect')
    parser_cmd.set_defaults(__func__=ConnectCommand(self.config))

class ConnectCommand(DefaultCommand):
    def __call__(self, args):
        # Access config values
        host = self.config.database.host.value
        port = self.config.database.port.value
        username = self.config.database.username.value
        password = self.config.database.password.value

        # Or use CLI overrides
        host = args.host if hasattr(args, 'host') else host
        port = args.port if hasattr(args, 'port') else port

        print(f"Connecting to {host}:{port}...")
```

### Using Hooks for Post-Processing

#### Base64 Password Storage

```python
from argtoolbox import Base64ElementHook

database.add_element(Element(
    'password',
    required=True,
    hidden=True,
    desc="Database password (base64 encoded)",
    hooks=[Base64ElementHook()]
))
```

Config file:
```ini
[database]
password=c2VjcmV0MTIz  # base64 encoded "secret123"
```

The value will be automatically decoded when read.

#### Custom Hooks

```python
from argtoolbox import DefaultHook

class UpperCaseHook(DefaultHook):
    def __call__(self, elt):
        if elt.value:
            elt.value = elt.value.upper()

section.add_element(Element(
    'env',
    hooks=[UpperCaseHook()]
))
```

### Complex Configuration Structures

> **⭐ KEY FEATURE**: This section describes one of argtoolbox's most unique and powerful capabilities!
> For a complete guide with real-world examples, see **HIERARCHICAL_CONFIG.md**

#### ElementWithSubSections

For tree-like configurations where an element points to a nested section:

```python
from argtoolbox import SubSection, ElementWithSubSections

# Define the subsection structure
nested = SubSection()
nested.add_element(Element('proto', default='tcp'))
nested.add_element(Element('version', e_type=int, default=3))

# Add to parent section
default = self.config.get_default_section()
default.add_element(ElementWithSubSections('network_config', nested))
```

Config file:
```ini
[DEFAULT]
port=389
network_config=net1

[net1]
proto=tcp
version=3
```

Access:
```python
proto = self.config.default.network_config.section.proto.value
```

#### ElementWithRelativeSubSection ⭐ UNIQUE FEATURE

**This is argtoolbox's killer feature!** Create template-based hierarchical configurations using simple INI files.

For dynamic lists of similar configurations (servers, databases, environments, etc.):

```python
from argtoolbox import ElementWithRelativeSubSection

# Define template for each item
template = SubSection()
template.add_element(Element('type', conf_required=True))
template.add_element(Element('enabled', e_type=bool, default=True))

default.add_element(
    ElementWithRelativeSubSection('services', template)
)
```

Config file:
```ini
[DEFAULT]
services=web api db

[web]
type=nginx
enabled=true

[api]
type=python
enabled=true

[db]
type=postgres
enabled=false
```

Access:
```python
for service_name, service in self.config.default.services.sections.items():
    service_type = service.type.value
    enabled = service.enabled.value
```

### Generating Configuration Files

Your program can generate a sample configuration file:

```python
def add_commands(self):
    subparsers = self.parser.add_subparsers()

    parser_gen = subparsers.add_parser(
        'generate-config',
        help="Generate sample configuration file"
    )
    parser_gen.add_argument('-o', '--output',
                           default=f"~/.{self.prog_name}.cfg")
    parser_gen.add_argument('-n', '--no-comments',
                           action='store_true')
    parser_gen.set_defaults(__func__=GenerateConfigCommand(self.config))

class GenerateConfigCommand(DefaultCommand):
    def __call__(self, args):
        output = os.path.expanduser(args.output)
        self.config.write_default_config_file(
            output,
            comments=not args.no_comments
        )
        print(f"Configuration file written to: {output}")
```

### Custom Completion

Add autocomplete support for your arguments:

```python
from argtoolbox import DefaultCompleter

class MyCommand(DefaultCommand):
    def complete(self, args, prefix):
        """Custom completion logic"""
        # Return list of suggestions
        return ['option1', 'option2', 'option3']

# In add_commands:
parser_cmd.add_argument(
    'item'
).completer = DefaultCompleter()
```

### Debug Mode

```python
class MyProgram(BasicProgram):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            force_debug=False,  # Debug from start
            force_debug_to_file=False,  # Log to file
            **kwargs
        )
```

Enable at runtime:
```bash
$ ./myprogram.py -d mycommand  # Debug to console
```

---

## API Reference

### Config Class

#### Constructor
```python
Config(prog_name, config_file=None, desc=None,
       mandatory=False, use_config_file=True)
```

**Parameters:**
- `prog_name` (str): Name of the program
- `config_file` (str|file): Path to config file or file object
- `desc` (str): Program description
- `mandatory` (bool): Config file required?
- `use_config_file` (bool): Enable config file support?

#### Methods

**add_section(section)**
- Add a Section to the config
- Returns: The added section

**get_section(name)**
- Get section by name
- Returns: Section or None

**load(exit_on_failure=False)**
- Load configuration from file
- Raises: `EnvironmentError` if mandatory file missing

**get_parser(**kwargs)**
- Create and return ArgumentParser
- Returns: `argparse.ArgumentParser`

**reload(hooks=None)**
- Reload config with CLI args
- Parameters: `hooks` - List of SectionHook objects

**write_default_config_file(output, comments=True)**
- Generate sample config file
- Parameters:
  - `output` (str): Output file path
  - `comments` (bool): Include comments?

### Section Classes

#### SimpleSection
```python
SimpleSection(name, desc=None, prefix=None,
              suffix=None, required=False)
```

**Methods:**
- `add_element(elt)` - Add Element to section
- `add_element_list(elt_list, **kwargs)` - Add multiple similar elements
- `count()` - Number of elements
- `reset()` - Reset all element values

#### ListSection
```python
ListSection(name, desc=None, prefix=None,
            suffix=None, required=False)
```
Dynamically reads all key-value pairs from a section.

#### SubSection
```python
SubSection(desc=None, prefix=None,
           suffix=None, required=False)
```
For nested configurations.

### Element Class

```python
Element(name, e_type=str, required=False, default=None,
        conf_hidden=False, conf_required=False, desc=None,
        dest=None, hooks=None, hidden=False,
        e_type_exclude=False)
```

**Parameters:**
- `name` (str): Element name
- `e_type` (type): Data type (str, int, float, bool, list)
- `required` (bool): Required in CLI?
- `default` (any): Default value
- `conf_hidden` (bool): Hide in config file generation?
- `conf_required` (bool): Required in config file?
- `desc` (str): Description
- `dest` (str): Argparse destination name
- `hooks` (list): Post-processing hooks
- `hidden` (bool): Mask value in output?
- `e_type_exclude` (bool): Don't pass type to argparse?

**Properties:**
- `value` - Current value (property)
- `name` - Element name (property)

**Methods:**
- `get_arg_parse_arguments()` - Returns dict for argparse
- `load(file_parser, section_name)` - Load from config
- `reset()` - Reset value to None

### Command Classes

#### DefaultCommand
```python
class DefaultCommand:
    def __init__(self, config=None):
        self.log = logging.getLogger(...)
        self.config = config
        self.protected_args = ['password']

    def __call__(self, args):
        # Override this method
        pass

    def complete(self, args, prefix):
        # Override for custom completion
        return []
```

#### TestCommand
Built-in command that prints config and args. Useful for debugging.

### Program Classes

#### BasicProgram
```python
BasicProgram(name, config_file=None, desc=None,
            mandatory=False, use_config_file=True,
            version="0.1-alpha", force_debug=False,
            force_debug_to_file=False)
```

**Methods to Override:**
- `add_config_options()` - Define configuration structure
- `add_commands()` - Define CLI commands and arguments
- `add_pre_commands()` - Add arguments before config reload

**Lifecycle:**
1. `add_config_options()`
2. `load()` - Load config from file
3. `init_parser()` - Create argparse parser
4. `add_pre_commands()` - Add early arguments
5. `reload()` - Reload config with CLI args
6. `add_commands()` - Add commands
7. Command execution

#### DefaultProgram
```python
DefaultProgram(parser, config=None, force_debug=False)
```
Lower-level program for custom workflows.

### Hook Classes

#### DefaultHook
```python
class DefaultHook:
    def __call__(self, elt):
        # Process element
        pass
```

#### Base64ElementHook
```python
Base64ElementHook(warning=False)
```
Decodes base64-encoded values.

**Parameters:**
- `warning` (bool): Warn on decode failure instead of error?

#### SectionHook
```python
SectionHook(section, attribute, opt_name)
```
Updates section attribute from CLI arg.

### Utility Functions

#### query_yes_no
```python
query_yes_no(question, default="yes")
```
Prompt user for yes/no question.

**Returns:** bool

---

## Examples

### Example 1: Simple CLI Tool

```python
#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from argtoolbox import DefaultCommand, BasicProgram

class GreetCommand(DefaultCommand):
    def __call__(self, args):
        greeting = "Hello" if args.formal else "Hi"
        print(f"{greeting}, {args.name}!")

class MyGreeter(BasicProgram):
    def add_commands(self):
        subparsers = self.parser.add_subparsers()

        parser = subparsers.add_parser('greet', help="Greet someone")
        parser.add_argument('name', help="Name to greet")
        parser.add_argument('--formal', action='store_true',
                          help="Use formal greeting")
        parser.set_defaults(__func__=GreetCommand(self.config))

if __name__ == "__main__":
    PROG = MyGreeter("greeter", desc="A friendly greeter")
    PROG()
```

### Example 2: Database Tool with Config

```python
#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from argtoolbox import (
    DefaultCommand, BasicProgram,
    SimpleSection, Element, Base64ElementHook
)

class ConnectCommand(DefaultCommand):
    def __call__(self, args):
        host = args.host
        port = args.port
        db = self.config.database.name.value
        user = self.config.database.user.value
        passwd = self.config.database.password.value

        print(f"Connecting to {db} at {host}:{port} as {user}")
        # Your connection logic here

class DatabaseTool(BasicProgram):
    def add_config_options(self):
        db = self.config.add_section(SimpleSection("database"))
        db.add_element(Element('name', required=True,
                               desc="Database name"))
        db.add_element(Element('user', required=True,
                               desc="Database user"))
        db.add_element(Element('password', required=True,
                               hidden=True,
                               desc="Database password (base64)",
                               hooks=[Base64ElementHook()]))

    def add_commands(self):
        # Global options from config
        self.parser.add_argument('--host', default='localhost',
                                help="Database host")
        self.parser.add_argument('--port', type=int, default=5432,
                                help="Database port")

        # Commands
        subparsers = self.parser.add_subparsers()

        conn = subparsers.add_parser('connect',
                                     help="Connect to database")
        conn.set_defaults(__func__=ConnectCommand(self.config))

if __name__ == "__main__":
    PROG = DatabaseTool("dbtool", desc="Database management tool")
    PROG()
```

Config file `~/.dbtool.cfg`:
```ini
[database]
name=myapp_db
user=admin
password=bXlzZWNyZXQ=
```

Usage:
```bash
$ ./dbtool.py connect --host 192.168.1.100
Connecting to myapp_db at 192.168.1.100:5432 as admin

$ ./dbtool.py --config-file /path/to/other.cfg connect
```

### Example 3: Complex Hierarchical Config

```python
#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from argtoolbox import (
    BasicProgram, DefaultCommand,
    SimpleSection, SubSection, Element,
    ElementWithRelativeSubSection
)

class DeployCommand(DefaultCommand):
    def __call__(self, args):
        env = args.environment

        # Access nested configuration
        config = self.config.default.environments.sections[env]
        host = config.host.value
        port = config.port.value
        path = config.deploy_path.value

        print(f"Deploying to {env}: {host}:{port}{path}")

class DeployTool(BasicProgram):
    def add_config_options(self):
        default = self.config.get_default_section()

        # Define environment template
        env_template = SubSection()
        env_template.add_element(Element('host', conf_required=True))
        env_template.add_element(Element('port', e_type=int, default=22))
        env_template.add_element(Element('deploy_path',
                                        conf_required=True))
        env_template.add_element(Element('user', default='deploy'))

        # Add list of environments
        default.add_element(
            ElementWithRelativeSubSection('environments', env_template)
        )

    def add_commands(self):
        subparsers = self.parser.add_subparsers()

        deploy = subparsers.add_parser('deploy', help="Deploy application")
        deploy.add_argument('environment',
                           choices=['dev', 'staging', 'prod'],
                           help="Target environment")
        deploy.set_defaults(__func__=DeployCommand(self.config))

if __name__ == "__main__":
    PROG = DeployTool("deployer", desc="Application deployment tool")
    PROG()
```

Config file `~/.deployer.cfg`:
```ini
[DEFAULT]
environments=dev staging prod

[dev]
host=dev.example.com
port=22
deploy_path=/var/www/dev
user=developer

[staging]
host=staging.example.com
port=22
deploy_path=/var/www/staging

[prod]
host=prod.example.com
port=2222
deploy_path=/var/www/production
user=deploy
```

---

## Best Practices

### 1. Program Structure

**Recommended Project Layout:**
```
myproject/
├── myproject/
│   ├── __init__.py
│   ├── cli.py         # Main program class
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── command1.py
│   │   └── command2.py
│   └── config/
│       ├── __init__.py
│       └── schema.py  # Config structure
├── setup.py
└── README.md
```

### 2. Configuration Design

- **Use sections** to group related options
- **Set sensible defaults** for optional values
- **Mark truly required** fields as `required=True`
- **Use appropriate types** to catch errors early
- **Add descriptions** for better help messages and config generation

### 3. Security

- **Always use `hidden=True`** for passwords and secrets
- **Consider Base64ElementHook** for storing sensitive data in config
- **Never log** hidden values (argtoolbox handles this)
- **Use file permissions** to protect config files: `chmod 600 ~/.myapp.cfg`

### 4. Command Design

- **One action per command** - keep commands focused
- **Inherit from DefaultCommand** - get logging and config for free
- **Call super().__call__(args)** - ensures logging of arguments
- **Use self.log** for consistent logging
- **Add to protected_args** if you have custom sensitive fields

### 5. Error Handling

```python
class MyCommand(DefaultCommand):
    def __call__(self, args):
        super().__call__(args)
        try:
            # Your logic
            pass
        except ValueError as e:
            self.log.error(f"Invalid input: {e}")
            return False
        except Exception as e:
            self.log.error(f"Unexpected error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return False
        return True
```

### 6. Testing

```python
import unittest
from io import BytesIO
from myproject.cli import MyProgram

class TestMyProgram(unittest.TestCase):
    def test_config_loading(self):
        config_data = b"""
        [section]
        option=value
        """
        prog = MyProgram("test", config_file=BytesIO(config_data))
        prog.add_config_options()
        prog.load()

        self.assertEqual(prog.config.section.option.value, "value")
```

### 7. Documentation

- Add the magic comment: `# PYTHON_ARGCOMPLETE_OK`
- Provide good help strings for all arguments
- Generate a sample config file for users
- Include examples in your README

### 8. Versioning

```python
PROG = MyProgram(
    "myapp",
    version="1.2.3",
    desc="My application"
)
```

Users can check version:
```bash
$ ./myapp.py --version
myapp 1.2.3
```

### 9. Config File Location

Standard locations (in order of precedence):
1. Custom path via `--config-file`
2. `./myapp.cfg` (current directory)
3. `~/.myapp.cfg` (user home)
4. `/etc/myapp.cfg` (system-wide)

### 10. Argcomplete Integration

Enable bash completion:

**For development (virtualenv):**
```bash
activate-global-python-argcomplete --dest $VIRTUAL_ENV/bin
```

**For system-wide:**
```bash
sudo activate-global-python-argcomplete
```

**Per-script:**
```bash
eval "$(register-python-argcomplete myapp.py)"
```

---

## Advanced Topics

### Custom Element Types

While argtoolbox supports str, int, float, bool, and list, you can extend Element for custom types:

```python
class PathElement(Element):
    def __init__(self, name, must_exist=True, **kwargs):
        super().__init__(name, e_type=str, **kwargs)
        self.must_exist = must_exist

        # Add validation hook
        self.hooks.append(PathValidationHook(must_exist))

class PathValidationHook(DefaultHook):
    def __init__(self, must_exist):
        self.must_exist = must_exist

    def __call__(self, elt):
        import os
        if elt.value and self.must_exist:
            if not os.path.exists(elt.value):
                raise ValueError(f"Path does not exist: {elt.value}")
```

### Dynamic Configuration

Load configuration from multiple sources:

```python
def add_config_options(self):
    # Load base config
    base_section = self.config.add_section(SimpleSection("base"))
    base_section.add_element(Element('include', e_type=list))

def load(self):
    super().load()

    # Load additional files
    includes = self.config.base.include.value
    if includes:
        for include_file in includes:
            self.config.file_parser.read(include_file)
            # Reload sections
            for section in self.config.sections.values():
                section.reset()
                section.load(self.config.file_parser)
```

### Plugin System

Create a plugin-based architecture:

```python
class PluginCommand(DefaultCommand):
    def __call__(self, args):
        plugin_name = args.plugin
        plugin_module = importlib.import_module(f'myapp.plugins.{plugin_name}')
        plugin_class = getattr(plugin_module, 'Plugin')
        plugin = plugin_class(self.config)
        return plugin.run(args)
```

### Internationalization

```python
import gettext

class I18nProgram(BasicProgram):
    def __init__(self, *args, **kwargs):
        # Setup i18n
        lang = os.getenv('LANG', 'en_US').split('.')[0]
        localedir = os.path.join(os.path.dirname(__file__), 'locale')
        trans = gettext.translation('myapp', localedir,
                                   languages=[lang], fallback=True)
        self._ = trans.gettext

        super().__init__(*args, **kwargs)

    def add_commands(self):
        subparsers = self.parser.add_subparsers()
        parser = subparsers.add_parser('hello',
                                       help=self._("Say hello"))
```

---

## Troubleshooting

### Common Issues

**1. Config file not found**
```python
# Make config file optional
PROG = MyProgram("myapp", mandatory=False)
```

**2. Type conversion errors**
```python
# Use appropriate e_type
Element('port', e_type=int)  # Not str!
```

**3. Required field missing**
```python
# Either make it not required, or provide default
Element('host', required=False, default='localhost')
```

**4. Argparse conflicts**
```python
# Use e_type_exclude for argparse conflicts
Element('debug', e_type=int, e_type_exclude=True)
# Then use action="count" in add_argument
```

**5. Completion not working**
```bash
# Ensure magic comment is present
# PYTHON_ARGCOMPLETE_OK

# Register completion
eval "$(register-python-argcomplete myapp.py)"
```

### Debug Mode

Enable debug logging:
```bash
$ ./myapp.py -d command  # -d for debug
```

Or force debug in code:
```python
PROG = MyProgram("myapp", force_debug=True)
```

Log to file:
```python
PROG = MyProgram("myapp", force_debug_to_file=True)
# Creates myapp.log
```

---

## Migration Guide

### From argparse-only to argtoolbox

**Before:**
```python
import argparse

parser = argparse.ArgumentParser(description="My app")
parser.add_argument('--host', default='localhost')
parser.add_argument('--port', type=int, default=8080)
args = parser.parse_args()

# Your logic
connect(args.host, args.port)
```

**After:**
```python
from argtoolbox import DefaultCommand, BasicProgram, SimpleSection, Element

class ConnectCommand(DefaultCommand):
    def __call__(self, args):
        connect(args.host, args.port)

class MyProgram(BasicProgram):
    def add_config_options(self):
        config = self.config.add_section(SimpleSection("server"))
        config.add_element(Element('host', default='localhost'))
        config.add_element(Element('port', e_type=int, default=8080))

    def add_commands(self):
        self.parser.add_argument('--host',
            **self.config.server.host.get_arg_parse_arguments())
        self.parser.add_argument('--port',
            **self.config.server.port.get_arg_parse_arguments())

        subparsers = self.parser.add_subparsers()
        conn = subparsers.add_parser('connect')
        conn.set_defaults(__func__=ConnectCommand(self.config))

if __name__ == "__main__":
    PROG = MyProgram("myapp", desc="My app")
    PROG()
```

---

## Contributing

Argtoolbox is open source (GPL3 license). Contributions welcome!

**Repository:** https://github.com/fred49/argtoolbox

**To contribute:**
1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Submit a pull request

---

## License

GNU General Public License v3 (GPLv3)

Copyright 2014 Frédéric MARTIN

---

## Changelog

### Version 1.1.6
- Current stable version
- Python 3 support
- Bug fixes and improvements

---

## Credits

**Author:** Frédéric MARTIN (frederic.martin.fma@gmail.com)

**Dependencies:**
- argparse (Python standard library)
- configparser (Python standard library)
- argcomplete (for bash completion)

---

## Conclusion

Argtoolbox streamlines CLI tool development by:
- Eliminating duplication between config files and argparse
- Providing a clean, object-oriented API
- Including built-in validation and type checking
- Supporting complex configurations with nested sections
- Offering extensibility through hooks and subclassing

Whether you're building a simple script or a complex CLI application, argtoolbox helps you focus on your application logic rather than input processing boilerplate.

**Happy coding!**
