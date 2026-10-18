# Argtoolbox Documentation Index

Welcome to the argtoolbox documentation! This index will help you find the right documentation for your needs.

---

## What is Argtoolbox?

Argtoolbox is a Python library that simplifies building command-line tools by unifying:
- Configuration file management (ConfigParser)
- Command-line argument parsing (argparse)
- Automatic bash completion (argcomplete)
- Type validation and hooks

**Key Benefits**:
1. Define your options once, use them everywhere - no more duplication!
2. **Create hierarchical, template-based configurations using simple INI files** - a unique and powerful feature!

---

## Documentation Files

### 1. **HIERARCHICAL_CONFIG.md** - Hierarchical INI Configurations ⭐ KEY FEATURE
🌟 **Start here to understand one of argtoolbox's most unique features!**

**Contents**:
- The problem: managing multiple similar configurations
- The solution: ElementWithRelativeSubSection
- How it works with diagrams
- Basic to advanced examples
- Real-world complete use case
- Comparison with alternatives
- Best practices and pitfalls

**Best for**:
- Understanding argtoolbox's unique value proposition
- Multi-server/multi-environment configurations
- Template-based dynamic config loading
- Anyone asking "why not just use JSON/YAML?"

**Length**: ~6,000 words / Feature-focused

---

### 2. **DOCUMENTATION.md** - Complete User Guide
📖 **Start here if you're new to argtoolbox**

**Contents**:
- What argtoolbox is and why it exists
- The problems it solves
- Core concepts explained
- Getting started tutorial
- Basic and advanced usage examples
- Complete API reference
- Best practices
- Troubleshooting guide

**Best for**:
- New users learning argtoolbox
- Understanding the "why" behind features
- Step-by-step tutorials
- Comprehensive examples
- API details

**Length**: ~15,000 words / Comprehensive

---

### 3. **QUICK_REFERENCE.md** - Quick Lookup Guide
⚡ **Use this for quick lookups while coding**

**Contents**:
- Installation
- Minimal template
- All core classes with syntax
- Common patterns and recipes
- Type reference table
- Quick tips and gotchas
- Common issues and solutions

**Best for**:
- Experienced users needing quick syntax reminders
- Copy-paste templates
- "How do I...?" questions
- Quick pattern lookup

**Length**: ~3,000 words / Concise

---

### 4. **ARCHITECTURE.md** - Internal Architecture Guide
🏗️ **Read this to understand how argtoolbox works internally**

**Contents**:
- System architecture diagrams
- Component responsibilities
- Data flow diagrams
- Design patterns used
- Extension points
- Performance considerations
- Comparison with alternatives

**Best for**:
- Contributors to the project
- Advanced users wanting deep understanding
- Debugging complex issues
- Extending argtoolbox functionality
- Architecture enthusiasts

**Length**: ~6,000 words / Technical

---

### 5. **README.rst** - Original Documentation
📝 **Original documentation from the project**

**Contents**:
- Basic introduction
- Installation instructions
- Quick start examples
- Basic and advanced usage

**Best for**:
- PyPI package page
- GitHub repository overview
- Quick introduction

**Length**: ~2,000 words / Original format

---

## Quick Start Path

### For Beginners

1. **Understand the Killer Feature**: Read HIERARCHICAL_CONFIG.md to see what makes argtoolbox unique
2. **Start**: Read "What is Argtoolbox?" in DOCUMENTATION.md
3. **Learn**: Follow "Getting Started" section in DOCUMENTATION.md
4. **Practice**: Try "Basic Usage" examples in DOCUMENTATION.md
5. **Reference**: Keep QUICK_REFERENCE.md open while coding

### For Experienced Developers

1. **Understand**: Read "Why Argtoolbox?" in DOCUMENTATION.md
2. **Template**: Copy minimal template from QUICK_REFERENCE.md
3. **Advanced**: Jump to "Advanced Usage" in DOCUMENTATION.md
4. **Deep Dive**: Read ARCHITECTURE.md if interested

### For Contributors

1. **Architecture**: Read ARCHITECTURE.md completely
2. **Design Patterns**: Understand patterns section
3. **Extension Points**: Review how to extend
4. **Code**: Dive into source with architectural understanding

---

## Common Use Cases

### "I want to build a simple CLI tool"
→ **DOCUMENTATION.md** → "Getting Started" → "Basic Usage"

### "I need to add config file support"
→ **DOCUMENTATION.md** → "Advanced Usage" → "Using Configuration Files"

### "How do I declare an Element?"
→ **QUICK_REFERENCE.md** → "Element" section

### "I want to use hooks"
→ **DOCUMENTATION.md** → "Advanced Usage" → "Using Hooks"

### "I need hierarchical configuration" ⭐
→ **HIERARCHICAL_CONFIG.md** → Complete guide to this key feature

### "I have multiple servers/databases/environments to configure" ⭐
→ **HIERARCHICAL_CONFIG.md** → See "Real-World Use Case"

### "Something's not working"
→ **DOCUMENTATION.md** → "Troubleshooting" section

### "I want to extend argtoolbox"
→ **ARCHITECTURE.md** → "Extension Points" section

### "How does the config loading work?"
→ **ARCHITECTURE.md** → "Data Flow" → "Configuration Loading Flow"

---

## Code Examples

### Minimal Working Example

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
        hello = subparsers.add_parser('hello')
        hello.add_argument('--name', default='World')
        hello.set_defaults(__func__=HelloCommand(self.config))

if __name__ == "__main__":
    PROG = MyProgram("myapp", desc="My first argtoolbox app")
    PROG()
```

**More examples**: See DOCUMENTATION.md "Examples" section

---

## Key Concepts at a Glance

### Config
Central configuration manager that coordinates everything.

### Section
Logical grouping of related options (e.g., "database", "logging").

### Element
Individual configuration option with type, default, validation.

### Command
Action your CLI can perform - extend `DefaultCommand`.

### Program
Main orchestrator - extend `BasicProgram`.

### Hook
Post-processing function for values (e.g., base64 decoding).

---

## API Quick Links

For detailed API documentation, see DOCUMENTATION.md "API Reference":

- **Config class**: Configuration manager
- **Section classes**: SimpleSection, ListSection, SubSection
- **Element class**: Configuration options
- **Command classes**: DefaultCommand, TestCommand
- **Program classes**: BasicProgram, DefaultProgram
- **Hook classes**: DefaultHook, Base64ElementHook, SectionHook

---

## Architecture Overview

```
User Code (MyProgram)
    ↓
BasicProgram (orchestration)
    ├── Config (configuration management)
    │   └── Sections → Elements → Hooks
    ├── ArgumentParser (CLI parsing)
    └── Commands (execution)
        ↓
Python stdlib (argparse, ConfigParser)
    ↓
argcomplete (bash completion)
```

**For detailed diagrams**: See ARCHITECTURE.md

---

## Frequently Asked Questions

### "Do I need a config file?"
No! Set `use_config_file=False` or just use CLI arguments.

### "Can I use YAML/JSON instead of INI?"
Not natively, but you can preprocess your config file.

### "Is it thread-safe?"
No, designed for single-threaded CLI apps.

### "Can I use async commands?"
Not natively, but you can wrap async code in `__call__`.

### "How do I store passwords?"
Use `hidden=True` and `Base64ElementHook` for basic protection.

**More FAQs**: See DOCUMENTATION.md "Troubleshooting"

---

## Best Practices Summary

1. **Always** call `super().__call__(args)` in commands
2. **Use** `hidden=True` for passwords
3. **Add** `# PYTHON_ARGCOMPLETE_OK` for completion
4. **Group** related options in sections
5. **Provide** sensible defaults
6. **Document** with `desc` parameter

**Complete list**: See DOCUMENTATION.md "Best Practices"

---

## Getting Help

1. **Read** the relevant documentation section
2. **Check** examples in DOCUMENTATION.md
3. **Try** the QUICK_REFERENCE.md patterns
4. **Debug** with `-d` flag for verbose output
5. **Review** ARCHITECTURE.md if debugging internal issues
6. **Check** GitHub issues: https://github.com/fred49/argtoolbox/issues

---

## Contributing

Interested in contributing?

1. Read **ARCHITECTURE.md** to understand internals
2. Check the repository: https://github.com/fred49/argtoolbox
3. Submit issues or pull requests

---

## Version Information

**Current Version**: 1.1.6
**Python Support**: Python 3.x
**License**: GPL3
**Author**: Frédéric MARTIN

---

## Document Metadata

| Document | Words | Purpose | Audience |
|----------|-------|---------|----------|
| HIERARCHICAL_CONFIG.md | ~6,000 | Hierarchical INI configs | Everyone (key feature!) |
| DOCUMENTATION.md | ~15,000 | Complete guide | New users, reference |
| QUICK_REFERENCE.md | ~3,000 | Quick lookup | Experienced users |
| ARCHITECTURE.md | ~6,000 | Internal details | Contributors, advanced |
| README.rst | ~2,000 | Introduction | Everyone |

---

## Navigation Tips

- **Ctrl+F** / **Cmd+F** to search within documents
- Use **table of contents** in each document
- Follow **cross-references** between documents
- Keep **QUICK_REFERENCE.md** open while coding
- Refer to **ARCHITECTURE.md** when extending

---

## Summary

- **New to argtoolbox?** → Start with DOCUMENTATION.md
- **Need quick syntax?** → Use QUICK_REFERENCE.md
- **Want to understand internals?** → Read ARCHITECTURE.md
- **Looking for examples?** → Check DOCUMENTATION.md "Examples"
- **Hit a problem?** → See DOCUMENTATION.md "Troubleshooting"

**Happy coding with argtoolbox!** 🚀

---

*Documentation created 2026-02-14*
*Last updated: 2026-02-14*
