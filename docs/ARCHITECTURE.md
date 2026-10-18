# Argtoolbox Architecture Guide

## Overview

This document provides an in-depth look at argtoolbox's internal architecture, design patterns, and how the different components interact.

---

## System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Code                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          MyProgram (extends BasicProgram)              │ │
│  │                                                        │ │
│  │  • add_config_options()                               │ │
│  │  • add_commands()                                     │ │
│  │  • Custom logic                                       │ │
│  └───────────────┬────────────────────────────────────────┘ │
└──────────────────┼──────────────────────────────────────────┘
                   │
                   │ inherits & uses
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Argtoolbox Core                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              BasicProgram                             │  │
│  │  • Orchestrates lifecycle                            │  │
│  │  • Manages Config, Parser, Commands                  │  │
│  └──────┬───────────────────────────────────────────────┘  │
│         │                                                   │
│         ├──────────┬──────────────┬──────────────┐         │
│         ▼          ▼              ▼              ▼         │
│  ┌──────────┐ ┌─────────┐ ┌────────────┐ ┌──────────────┐ │
│  │  Config  │ │ Parser  │ │  Commands  │ │ Completion   │ │
│  └──────┬───┘ └─────────┘ └────────────┘ └──────────────┘ │
│         │                                                   │
│         ├──────────┬──────────────┐                        │
│         ▼          ▼              ▼                        │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐                    │
│  │ Sections │ │ Elements│ │  Hooks   │                    │
│  └──────────┘ └─────────┘ └──────────┘                    │
└─────────────────────────────────────────────────────────────┘
                   │
                   │ uses
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 Python Standard Library                     │
│  ┌──────────────┐  ┌────────────┐  ┌──────────────────┐   │
│  │   argparse   │  │ ConfigParser│  │    logging      │   │
│  └──────────────┘  └────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                   │
                   │ uses
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 External Dependencies                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              argcomplete                              │  │
│  │  • Bash completion support                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Classes and Their Responsibilities

### 1. Config Class

**Purpose**: Central configuration manager

**Responsibilities**:
- Store and manage sections
- Load/reload configuration from files
- Create and configure ArgumentParser
- Coordinate between config file and CLI parsing

**Key Attributes**:
```python
{
    'prog_name': str,              # Program name
    'config_file': str|file,       # Config file path/object
    'use_config_file': bool,       # Enable config files?
    'mandatory': bool,             # Config file required?
    'sections': OrderedDict,       # Section name -> Section object
    'file_parser': ConfigParser,   # Python's ConfigParser
    'parser': ArgumentParser        # argparse parser
}
```

**Key Methods**:
- `add_section(section)` - Register a section
- `load()` - Load config from file
- `reload()` - Reload with CLI arguments
- `get_parser()` - Create ArgumentParser

**Design Pattern**: Facade (simplifies interaction with ConfigParser and ArgumentParser)

### 2. Section Classes

#### Abstract Hierarchy

```
_AbstractSection (abstract base)
    ├── _Section (abstract, adds element management)
    │   ├── SimpleSection (concrete)
    │   └── SubSection (concrete, for nesting)
    └── ListSection (concrete, dynamic keys)
```

#### SimpleSection

**Purpose**: Standard section with named elements

**Responsibilities**:
- Store and manage elements
- Load element values from config file
- Provide element access by name

**Key Attributes**:
```python
{
    '_name': str,             # Section name
    'elements': OrderedDict,  # Element name -> Element object
    '_desc': str,            # Description
    '_prefix': str,          # Name prefix
    '_suffix': str,          # Name suffix
    '_required': bool        # Section required?
}
```

#### SubSection

**Purpose**: Nested section for hierarchical configs

**Differences from SimpleSection**:
- Used within ElementWithSubSections
- Supports deep copying for templates
- Name is set dynamically

#### ListSection

**Purpose**: Dynamic section that reads all key-value pairs

**Use Case**: When you don't know keys in advance

**Behavior**: Loads all keys from config section into `elements` dict

### 3. Element Class

**Purpose**: Individual configuration option

**Responsibilities**:
- Store metadata (type, required, default, etc.)
- Load and validate value from config
- Provide argparse configuration
- Apply post-processing hooks

**Key Attributes**:
```python
{
    '_name': str,            # Element name
    'e_type': type,          # Data type (str, int, float, bool, list)
    '_required': bool,       # Required in CLI?
    'conf_required': bool,   # Required in config?
    'default': any,          # Default value
    '_value': any,           # Current value
    '_desc': str,            # Description
    'hidden': bool,          # Mask in output?
    'conf_hidden': bool,     # Hide in config generation?
    'hooks': list,           # Post-processing hooks
    '_dest': str,            # Argparse destination
    'e_type_exclude': bool   # Don't pass type to argparse?
}
```

**Key Methods**:
- `load(file_parser, section_name)` - Load from config
- `get_arg_parse_arguments()` - Generate argparse kwargs
- `post_load()` - Apply hooks

**Design Pattern**: Builder (fluent configuration through kwargs)

### 4. Element Variants

#### ElementWithSubSections

**Purpose**: Element that points to a nested section

**Architecture**:
```
Element (value = "nested_section_name")
    └── SubSection (name = value)
            ├── Element 1
            ├── Element 2
            └── Element 3
```

**Example**:
```ini
[DEFAULT]
server_config=production

[production]
host=prod.example.com
port=443
```

#### ElementWithRelativeSubSection

**Purpose**: Element with a list of related subsections

**Architecture**:
```
Element (value = ["name1", "name2", "name3"])
    ├── SubSection (name = "name1")
    │       ├── Element 1
    │       └── Element 2
    ├── SubSection (name = "name2")
    │       ├── Element 1
    │       └── Element 2
    └── SubSection (name = "name3")
            ├── Element 1
            └── Element 2
```

**Use Case**: Multiple similar configurations (e.g., multiple servers)

**Template Pattern**: Uses SubSection as a template, deep-copies for each item

### 5. Command Classes

#### DefaultCommand

**Purpose**: Base class for all commands

**Responsibilities**:
- Provide logging infrastructure
- Store reference to config
- Log arguments (with protection for sensitive data)
- Define command execution interface

**Key Attributes**:
```python
{
    'log': Logger,           # Logger instance
    'config': Config,        # Config object
    'protected_args': list   # Args to mask in logs
}
```

**Key Methods**:
- `__call__(args)` - Execute command (override this)
- `complete(args, prefix)` - Autocomplete support

**Design Pattern**: Template Method (defines skeleton, subclasses fill in details)

#### TestCommand

**Purpose**: Built-in debugging command

**Behavior**: Prints config and arguments

**Use Case**: Quick testing and debugging

### 6. Program Classes

#### BasicProgram

**Purpose**: Complete program orchestration

**Responsibilities**:
- Manage full lifecycle
- Initialize config and parser
- Coordinate loading/reloading
- Handle execution and error handling

**Lifecycle Methods** (in order):
1. `__init__()` - Initialize
2. `add_config_options()` - Define config structure
3. `load()` - Load config from file
4. `init_parser()` - Create argparse parser
5. `add_pre_commands()` - Add early arguments
6. `reload()` - Reload config with CLI args
7. `add_commands()` - Add commands and arguments
8. `__call__()` - Execute

**Key Attributes**:
```python
{
    'config': Config,              # Config object
    'parser': ArgumentParser,      # Argparse parser
    'prog_name': str,             # Program name
    'version': str,               # Version string
    'force_debug': bool,          # Force debug mode?
    'force_debug_to_file': bool,  # Log to file?
    'log': Logger                 # Logger instance
}
```

**Design Pattern**: Template Method + Facade

#### DefaultProgram

**Purpose**: Lower-level program execution

**Use Case**: Custom workflows that need more control

**Responsibilities**:
- Parse arguments
- Handle argcomplete integration
- Execute commands
- Error handling

**Design Pattern**: Strategy (delegates to command objects)

### 7. Hook System

#### Hook Hierarchy

```
DefaultHook (base)
    ├── Base64ElementHook (concrete)
    └── SectionHook (concrete)
    └── [User Custom Hooks]
```

#### DefaultHook

**Purpose**: Base for post-processing

**Interface**:
```python
def __call__(self, elt: Element) -> None:
    # Modify elt.value in place
    pass
```

#### Base64ElementHook

**Purpose**: Decode base64-encoded values

**Use Case**: Store passwords/secrets in config file

**Behavior**:
- Attempts to decode `elt.value`
- Handles errors (warning or exception)

#### SectionHook

**Purpose**: Update section attributes from CLI

**Use Case**: Dynamic configuration based on CLI args

**Behavior**:
- Reads value from parsed args
- Sets attribute on section

**Design Pattern**: Observer-like (reacts to CLI parsing)

### 8. Completion System

#### DefaultCompleter

**Purpose**: Integrate with argcomplete

**Responsibilities**:
- Find completion method on command
- Call it with appropriate arguments
- Return completion suggestions

**Integration**:
```python
argument.completer = DefaultCompleter("complete")
# Will call command.complete(args, prefix)
```

**Design Pattern**: Adapter (adapts Command to argcomplete interface)

---

## Data Flow

### Configuration Loading Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Program Start                                             │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. MyProgram.__init__()                                      │
│    • Creates Config object                                   │
│    • Sets program name, description                          │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. add_config_options()                                      │
│    • User defines sections                                   │
│    • User adds elements to sections                          │
│    • Config structure is complete                            │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. load()                                                    │
│    • Config.file_parser looks for config files              │
│    • Discovery order: ./prog.cfg, ~/.prog.cfg, /etc/prog.cfg│
│    • Reads found file                                        │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. For each Section.load()                                   │
│    ┌────────────────────────────────────────────────────────┤
│    │ 5a. For each Element.load()                            │
│    │     • Read value from ConfigParser                     │
│    │     • Type conversion (getint, getbool, etc.)          │
│    │     • Validation (required?, correct type?)            │
│    │     • Store in element.value                           │
│    │     • Apply hooks (post_load)                          │
│    └────────────────────────────────────────────────────────┤
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. Config object ready                                       │
│    • All sections populated                                  │
│    • All elements have values                                │
│    • Ready for CLI integration                               │
└──────────────────────────────────────────────────────────────┘
```

### CLI Parsing Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. init_parser()                                             │
│    • Config.get_parser() creates ArgumentParser             │
│    • Adds built-in args: --config-file, -h, --version, -v   │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. add_pre_commands()                                        │
│    • User adds early arguments                               │
│    • Typically for options that affect config loading        │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. reload()                                                  │
│    • parse_known_args() - first pass                         │
│    • Check for --config-file argument                        │
│    • If found, reload config from that file                  │
│    • Apply section hooks                                     │
│    • Add -h/--help argument (after first parse)              │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. add_commands()                                            │
│    • User adds commands (subparsers)                         │
│    • For each command:                                       │
│      - Create subparser                                      │
│      - Add arguments (often using element.get_arg_parse_...) │
│      - Set __func__ to command instance                      │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. DefaultProgram.__call__()                                 │
│    • Argcomplete integration (if available)                  │
│    • parse_args() - final parse                              │
│    • Debug setup if requested                                │
│    • Extract __func__ from args                              │
│    • Execute: args.__func__(args)                            │
└──────────────────────────────────────────────────────────────┘
```

### Element to Argparse Bridge

```
Element Declaration:
┌─────────────────────────────────────────────────────┐
│ Element('host',                                     │
│         e_type=str,                                 │
│         required=True,                              │
│         default="localhost",                        │
│         desc="Server host")                         │
└────────────────────┬────────────────────────────────┘
                     │
                     │ .get_arg_parse_arguments()
                     ▼
Argparse kwargs:
┌─────────────────────────────────────────────────────┐
│ {                                                   │
│     'dest': 'host',                                 │
│     'default': 'localhost',  # or config value     │
│     'required': True,  # if no config value        │
│     'help': "Server host"                           │
│ }                                                   │
└────────────────────┬────────────────────────────────┘
                     │
                     │ **kwargs
                     ▼
Argparse call:
┌─────────────────────────────────────────────────────┐
│ parser.add_argument(                                │
│     '--host',                                       │
│     dest='host',                                    │
│     default='localhost',                            │
│     required=True,                                  │
│     help="Server host"                              │
│ )                                                   │
└─────────────────────────────────────────────────────┘
```

### Value Resolution Priority

```
Priority (highest to lowest):
1. CLI argument (if provided)
2. Config file value
3. Element default value
4. None

Example:
┌─────────────────────────────────────────────────────┐
│ Element default: "localhost"                        │
│ Config file:     "192.168.1.1"                      │
│ CLI arg:         "10.0.0.1"                         │
│                                                     │
│ Result: "10.0.0.1"  ← CLI wins                      │
└─────────────────────────────────────────────────────┘

If no CLI arg:
┌─────────────────────────────────────────────────────┐
│ Element default: "localhost"                        │
│ Config file:     "192.168.1.1"                      │
│ CLI arg:         (not provided)                     │
│                                                     │
│ Result: "192.168.1.1"  ← Config wins                │
└─────────────────────────────────────────────────────┘

If no config value:
┌─────────────────────────────────────────────────────┐
│ Element default: "localhost"                        │
│ Config file:     (missing)                          │
│ CLI arg:         (not provided)                     │
│                                                     │
│ Result: "localhost"  ← Default wins                 │
└─────────────────────────────────────────────────────┘
```

---

## Design Patterns

### 1. Template Method Pattern

**Used in**: BasicProgram, DefaultCommand

**Purpose**: Define algorithm skeleton, let subclasses fill in steps

**Example**:
```python
class BasicProgram:
    def __call__(self):
        self.add_config_options()  # Override point 1
        self.load()
        self.init_parser()
        self.add_pre_commands()    # Override point 2
        self.reload()
        self.add_commands()        # Override point 3
        self.run()
```

### 2. Facade Pattern

**Used in**: Config class

**Purpose**: Simplify interaction with ConfigParser and ArgumentParser

**Benefit**: Users don't need to understand complex details of stdlib modules

### 3. Builder Pattern

**Used in**: Element configuration

**Purpose**: Construct complex objects step-by-step

**Example**:
```python
element = Element('name')       # Basic
element = Element('name',       # With options
                 e_type=int,
                 required=True,
                 default=0)
```

### 4. Strategy Pattern

**Used in**: Command execution

**Purpose**: Encapsulate algorithms (commands) and make them interchangeable

**Example**:
```python
args.__func__ = ConnectCommand(config)  # Strategy selection
args.__func__(args)                     # Strategy execution
```

### 5. Observer Pattern (Hook System)

**Used in**: Element hooks, Section hooks

**Purpose**: React to events (config loading, CLI parsing)

**Example**:
```python
element.hooks = [Base64ElementHook(), CustomHook()]
element.load()  # Triggers hooks
```

### 6. Composite Pattern

**Used in**: Section/Element hierarchy

**Purpose**: Treat individual objects and compositions uniformly

**Structure**:
```
Config (root)
  └── Section (composite)
        ├── Element (leaf)
        └── ElementWithSubSections (composite)
              └── SubSection (composite)
                    └── Element (leaf)
```

---

## Threading and Safety

### Thread Safety

**Current Status**: Not thread-safe

**Reasons**:
- Config loading is single-threaded
- No locks on data structures
- Designed for single-threaded CLI applications

**Recommendations**:
- One Config instance per thread if multi-threading needed
- Don't share Config objects across threads

### Immutability

**Mutable Parts**:
- Element.value (can change during load/reload)
- Section.elements (OrderedDict)

**Immutable Parts**:
- Element metadata (type, required, etc.) - set at creation

---

## Performance Considerations

### Configuration Loading

**Time Complexity**:
- O(S × E) where S = number of sections, E = avg elements per section
- ConfigParser reads linearly through file
- Each element reads once from ConfigParser

**Optimization Tips**:
- Use conf_hidden=True for elements not in config file
- Minimize hooks (they run for every element)
- Use ListSection only when necessary (less structured)

### Argument Parsing

**Time Complexity**:
- Dominated by argparse (O(A) where A = number of arguments)
- Element.get_arg_parse_arguments() is O(1)

**Optimization Tips**:
- Use e_type_exclude=True when argparse doesn't need type info
- Minimize section hooks (run during reload)

### Memory Usage

**Typical Memory Footprint**:
- Small: < 1 MB for most applications
- Config, sections, elements are lightweight
- ConfigParser and ArgumentParser dominate memory

**Optimization Tips**:
- Don't store large data in config files
- Use file paths, not inline data

---

## Extension Points

### Custom Section Types

Subclass `_AbstractSection`:

```python
class CustomSection(_AbstractSection):
    def load(self, file_parser):
        # Custom loading logic
        pass

    def get_representation(self, prefix="", suffix="\n"):
        # Custom display logic
        pass
```

### Custom Element Types

Subclass `Element`:

```python
class PathElement(Element):
    def _load(self, file_parser, section_name):
        super()._load(file_parser, section_name)
        # Additional validation
        if self.value and not os.path.exists(self.value):
            raise ValueError(f"Path not found: {self.value}")
```

### Custom Hooks

Subclass `DefaultHook`:

```python
class ValidationHook(DefaultHook):
    def __init__(self, validator_func):
        self.validator = validator_func

    def __call__(self, elt):
        if elt.value and not self.validator(elt.value):
            raise ValueError(f"Validation failed for {elt.name}")
```

### Custom Commands

Subclass `DefaultCommand`:

```python
class AsyncCommand(DefaultCommand):
    async def run_async(self, args):
        # Async logic
        pass

    def __call__(self, args):
        import asyncio
        asyncio.run(self.run_async(args))
```

### Custom Programs

Subclass `BasicProgram`:

```python
class PluginProgram(BasicProgram):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugins = self.discover_plugins()

    def discover_plugins(self):
        # Plugin discovery logic
        pass

    def add_commands(self):
        super().add_commands()
        # Add plugin commands
        for plugin in self.plugins:
            plugin.register_commands(self.parser)
```

---

## Comparison with Alternatives

### vs. Pure argparse

| Feature | argparse | argtoolbox |
|---------|----------|-----------|
| Config file | Manual | Built-in |
| Duplication | High | Low |
| Type validation | Manual | Automatic |
| Completion | argcomplete | Integrated |
| Complexity | Low | Medium |

### vs. Click

| Feature | Click | argtoolbox |
|---------|-------|-----------|
| Config file | Via plugins | Built-in |
| Decorators | Yes | No |
| Subcommands | Easy | Easy |
| Config structure | Flat | Hierarchical |
| Type system | Rich | Basic |

### vs. argparse + ConfigParser

| Feature | Separate | argtoolbox |
|---------|----------|-----------|
| Integration | Manual | Automatic |
| DRY principle | No | Yes |
| Learning curve | Medium | Medium |
| Flexibility | High | Medium |

---

## Future Architecture Considerations

### Potential Improvements

1. **Type System**:
   - Add more built-in types (Path, URL, Email)
   - Type hints integration
   - Runtime type checking with pydantic

2. **Async Support**:
   - Async command execution
   - Async hooks
   - Parallel config loading

3. **Validation Framework**:
   - Declarative validators
   - Cross-field validation
   - Schema validation (JSON Schema)

4. **Plugin System**:
   - Formal plugin API
   - Plugin discovery mechanism
   - Plugin lifecycle management

5. **Modern Config Formats**:
   - YAML support
   - TOML support
   - JSON support
   - Keep INI for compatibility

6. **Better Error Messages**:
   - More context in exceptions
   - Suggestions for common mistakes
   - Configuration validation before runtime

---

## Conclusion

Argtoolbox's architecture is built around:
- **Separation of concerns**: Config, parsing, execution are distinct
- **Flexibility**: Multiple extension points
- **Integration**: Seamless config file + CLI integration
- **Simplicity**: Hide complexity of stdlib modules

Understanding this architecture helps in:
- Effective use of the library
- Debugging issues
- Extending functionality
- Contributing to the project

---

**For more information, see:**
- DOCUMENTATION.md - Complete user guide
- QUICK_REFERENCE.md - Quick lookup reference
- Source code - The ultimate documentation
