# Argtoolbox Quick Reference Guide

## Installation

```bash
pip install argtoolbox
```

## Minimal Template

```python
#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from argtoolbox import DefaultCommand, BasicProgram

class MyCommand(DefaultCommand):
    def __call__(self, args):
        print("Hello from MyCommand!")
        print(f"Args: {args}")

class MyProgram(BasicProgram):
    def add_commands(self):
        subparsers = self.parser.add_subparsers()
        cmd = subparsers.add_parser('mycommand', help="My command")
        cmd.add_argument('--option', default="value")
        cmd.set_defaults(__func__=MyCommand(self.config))

if __name__ == "__main__":
    PROG = MyProgram("myapp", desc="My application")
    PROG()
```

## Core Classes

### Config
```python
from argtoolbox import Config

config = Config(
    prog_name="myapp",
    config_file="path/to/config.cfg",  # or None for auto-discovery
    desc="Program description",
    mandatory=False,  # Config file required?
    use_config_file=True  # Enable config file support?
)
```

### Sections

```python
from argtoolbox import SimpleSection, ListSection, SubSection

# Simple section
section = SimpleSection("database", desc="Database configuration")

# List section (reads all keys dynamically)
list_section = ListSection("aliases")

# SubSection (for nesting)
subsection = SubSection()
```

### Element

```python
from argtoolbox import Element

element = Element(
    'host',
    e_type=str,              # str, int, float, bool, list
    required=False,          # Required in CLI?
    default="localhost",     # Default value
    conf_required=False,     # Required in config file?
    desc="Host address",     # Description
    hidden=False,            # Mask in output?
    conf_hidden=False,       # Hide in config generation?
    dest=None,               # Argparse destination
    hooks=[],                # Post-processing hooks
    e_type_exclude=False     # Don't pass type to argparse?
)
```

### Commands

```python
from argtoolbox import DefaultCommand

class MyCommand(DefaultCommand):
    def __init__(self, config=None):
        super().__init__(config)
        # self.config is available
        # self.log is the logger

    def __call__(self, args):
        super().__call__(args)  # Logs arguments
        # Your logic here
        value = self.config.section.element.value
        cli_value = args.option
        return True  # or False for failure

    def complete(self, args, prefix):
        """Optional: custom autocomplete"""
        return ['option1', 'option2']
```

### Programs

```python
from argtoolbox import BasicProgram

class MyProgram(BasicProgram):
    def __init__(self, *args, **kwargs):
        super().__init__(
            name="myapp",
            config_file=None,
            desc="Description",
            mandatory=False,
            use_config_file=True,
            version="1.0.0",
            force_debug=False,
            force_debug_to_file=False,
            *args, **kwargs
        )

    def add_config_options(self):
        """Define configuration structure"""
        section = self.config.add_section(SimpleSection("mysection"))
        section.add_element(Element('myoption'))

    def add_pre_commands(self):
        """Add arguments before config reload"""
        pass

    def add_commands(self):
        """Define CLI commands"""
        # Add global options
        self.parser.add_argument('--global-opt')

        # Add commands
        subparsers = self.parser.add_subparsers()
        cmd = subparsers.add_parser('command', help="Help text")
        cmd.add_argument('--option')
        cmd.set_defaults(__func__=MyCommand(self.config))
```

## Common Patterns

### With Config File

```python
class MyProgram(BasicProgram):
    def add_config_options(self):
        db = self.config.add_section(SimpleSection("database"))
        db.add_element(Element('host', required=True, default="localhost"))
        db.add_element(Element('port', e_type=int, default=5432))
        db.add_element(Element('user', required=True))
        db.add_element(Element('password', required=True, hidden=True))

    def add_commands(self):
        # Use config values as defaults
        self.parser.add_argument(
            '--host',
            **self.config.database.host.get_arg_parse_arguments()
        )
        self.parser.add_argument(
            '--port',
            **self.config.database.port.get_arg_parse_arguments()
        )

        subparsers = self.parser.add_subparsers()
        connect = subparsers.add_parser('connect')
        connect.set_defaults(__func__=ConnectCommand(self.config))
```

Config file `~/.myapp.cfg`:
```ini
[database]
host=192.168.1.100
port=5432
user=admin
password=secret
```

### Using Hooks

```python
from argtoolbox import Element, Base64ElementHook, DefaultHook

# Base64 decoding
element = Element(
    'password',
    hidden=True,
    hooks=[Base64ElementHook(warning=False)]
)

# Custom hook
class UpperCaseHook(DefaultHook):
    def __call__(self, elt):
        if elt.value:
            elt.value = elt.value.upper()

element = Element('name', hooks=[UpperCaseHook()])
```

### Nested Configuration

```python
from argtoolbox import SubSection, ElementWithSubSections

# Define subsection
nested = SubSection()
nested.add_element(Element('field1'))
nested.add_element(Element('field2'))

# Add to parent
section.add_element(ElementWithSubSections('nested_name', nested))
```

Config:
```ini
[section]
nested_name=sub1

[sub1]
field1=value1
field2=value2
```

Access:
```python
value = config.section.nested_name.section.field1.value
```

### Dynamic Lists of Sections

```python
from argtoolbox import ElementWithRelativeSubSection

# Define template
template = SubSection()
template.add_element(Element('host', conf_required=True))
template.add_element(Element('port', e_type=int, default=80))

# Add to section
section.add_element(ElementWithRelativeSubSection('servers', template))
```

Config:
```ini
[section]
servers=web1 web2 web3

[web1]
host=192.168.1.10
port=8080

[web2]
host=192.168.1.11
port=8080

[web3]
host=192.168.1.12
```

Access:
```python
for name, server in config.section.servers.sections.items():
    host = server.host.value
    port = server.port.value
```

### Section Hooks

```python
from argtoolbox import SectionHook

# Update section attribute from CLI arg
hook = SectionHook(
    section=config.mysection,
    attribute='dynamic_field',
    opt_name='cli_option'
)

# Apply during reload
config.reload(hooks=[hook])
```

## Element Types

| Type | e_type | Config File | Notes |
|------|--------|-------------|-------|
| String | `str` | `key=value` | Default type |
| Integer | `int` | `key=123` | Validates integer |
| Float | `float` | `key=3.14` | Validates float |
| Boolean | `bool` | `key=true` | true/false/yes/no/1/0 |
| List | `list` | `key=a b c` | Whitespace-separated |

## Accessing Values

```python
# From config
value = self.config.section.element.value

# From CLI args
value = args.argument_name

# Config with CLI override
value = args.option if hasattr(args, 'option') else self.config.section.element.value
```

## Config File Locations

Auto-discovery order:
1. `--config-file` argument
2. `./myapp.cfg`
3. `~/.myapp.cfg`
4. `/etc/myapp.cfg`

## Generate Sample Config

```python
config.write_default_config_file(
    output="~/.myapp.cfg",
    comments=True  # Include descriptions
)
```

## Logging

```python
class MyCommand(DefaultCommand):
    def __call__(self, args):
        self.log.debug("Debug message")
        self.log.info("Info message")
        self.log.warning("Warning message")
        self.log.error("Error message")
```

Enable debug mode:
```bash
./myapp.py -d command
```

## Autocomplete

Add to script:
```python
# PYTHON_ARGCOMPLETE_OK
```

Enable globally:
```bash
activate-global-python-argcomplete
```

Enable per-script:
```bash
eval "$(register-python-argcomplete myapp.py)"
```

## Built-in Commands

Use `TestCommand` for debugging:
```python
from argtoolbox import TestCommand

parser.set_defaults(__func__=TestCommand(self.config))
```

Prints config and args when run.

## CLI Arguments

Built-in arguments:
- `-h, --help` - Show help
- `--version` - Show version
- `-v, --verbose` - Verbose mode
- `-d` - Debug mode (if configured)
- `--config-file` - Custom config file path

## Common Patterns

### Optional Config File
```python
PROG = MyProgram("myapp", mandatory=False)
```

### No Config File
```python
PROG = MyProgram("myapp", use_config_file=False)
```

### In-Memory Config
```python
from io import BytesIO

config_data = b"""
[section]
key=value
"""

PROG = MyProgram("myapp", config_file=BytesIO(config_data))
```

### Multiple Commands
```python
def add_commands(self):
    subparsers = self.parser.add_subparsers()

    # Command 1
    cmd1 = subparsers.add_parser('cmd1', help="First command")
    cmd1.add_argument('--opt1')
    cmd1.set_defaults(__func__=Command1(self.config))

    # Command 2
    cmd2 = subparsers.add_parser('cmd2', help="Second command")
    cmd2.add_argument('--opt2')
    cmd2.set_defaults(__func__=Command2(self.config))
```

### Global + Command Options
```python
def add_commands(self):
    # Global options (before subparsers)
    self.parser.add_argument('--global-opt')

    # Commands with specific options
    subparsers = self.parser.add_subparsers()
    cmd = subparsers.add_parser('cmd')
    cmd.add_argument('--cmd-specific-opt')
    cmd.set_defaults(__func__=MyCommand(self.config))
```

Usage:
```bash
./myapp.py --global-opt value cmd --cmd-specific-opt value
```

### Required Arguments
```python
cmd.add_argument('required_arg')  # Positional = required
cmd.add_argument('--optional-arg')  # Optional with --
cmd.add_argument('--required-opt', required=True)  # Required with --
```

### Argument Types
```python
cmd.add_argument('--count', type=int)
cmd.add_argument('--rate', type=float)
cmd.add_argument('--enable', action='store_true')
cmd.add_argument('--files', nargs='+')  # List
cmd.add_argument('--choice', choices=['a', 'b', 'c'])
```

### Default Values
```python
# From config (preferred)
cmd.add_argument('--host',
    **self.config.section.host.get_arg_parse_arguments())

# Hardcoded
cmd.add_argument('--host', default='localhost')
```

## Error Handling

```python
class MyCommand(DefaultCommand):
    def __call__(self, args):
        super().__call__(args)
        try:
            # Your code
            pass
        except ValueError as e:
            self.log.error(f"Error: {e}")
            return False
        return True
```

## Protected Arguments

Mask sensitive CLI arguments:
```python
class MyCommand(DefaultCommand):
    def __init__(self, config=None):
        super().__init__(config)
        self.protected_args = ['password', 'token', 'secret']
```

## Testing

```python
import unittest
from io import BytesIO

class TestMyApp(unittest.TestCase):
    def test_config(self):
        config_data = b"[section]\nkey=value\n"
        prog = MyProgram("test", config_file=BytesIO(config_data))
        prog.add_config_options()
        prog.load()

        self.assertEqual(prog.config.section.key.value, "value")
```

## Tips

1. **Always call super().__call__(args)** in commands for logging
2. **Use descriptive names** for better help messages
3. **Group related options** in sections
4. **Use hidden=True** for passwords
5. **Add PYTHON_ARGCOMPLETE_OK** for autocomplete
6. **Provide sensible defaults** when possible
7. **Use appropriate types** to catch errors early
8. **Document in desc** for self-documenting code

## Common Issues

| Issue | Solution |
|-------|----------|
| Config not found | Set `mandatory=False` or provide path |
| Type error | Use correct `e_type` (int not str for numbers) |
| Missing required | Add `default` or make `required=False` |
| Argparse conflict | Use `e_type_exclude=True` |
| Completion not working | Add `# PYTHON_ARGCOMPLETE_OK` and register |

## Example Config File

```ini
# Sample configuration for myapp

[database]
# Database host (string)
host=localhost

# Database port (int)
port=5432

# Username (required)
user=admin

# Password - base64 encoded (required, hidden)
password=bXlzZWNyZXQ=

[logging]
# Log level: DEBUG, INFO, WARNING, ERROR
level=INFO

# Log file path
file=/var/log/myapp.log

[features]
# Enabled features (list)
enabled=feature1 feature2 feature3

# Maximum connections (int)
max_connections=100

# Enable cache (bool)
cache=true
```

## Resources

- **Full Documentation**: See DOCUMENTATION.md
- **Repository**: https://github.com/fred49/argtoolbox
- **PyPI**: https://pypi.org/project/argtoolbox/
- **License**: GPL3

---

**Happy Coding!**
