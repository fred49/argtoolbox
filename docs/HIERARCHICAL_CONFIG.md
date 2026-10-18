# Hierarchical Configuration with INI Files - A Key Feature of Argtoolbox

## The Problem This Solves

**Scenario**: You need to configure multiple similar items (servers, databases, services, environments) where each has the same structure but different values.

**Traditional Approaches**:

### ❌ Flat INI (repetitive, hard to maintain)
```ini
[server]
server1_host=web1.example.com
server1_port=8080
server1_ssl=true
server2_host=web2.example.com
server2_port=8080
server2_ssl=true
server3_host=api.example.com
server3_port=443
server3_ssl=true
```
Problems: Keys get long, hard to add new servers, lots of duplication

### ❌ JSON/YAML (not INI)
```yaml
servers:
  - name: web1
    host: web1.example.com
    port: 8080
    ssl: true
  - name: web2
    host: web2.example.com
    port: 8080
    ssl: true
```
Problems: Requires different parser, loses INI simplicity

### ✅ Argtoolbox Solution (hierarchical INI)
```ini
[DEFAULT]
servers=web1 web2 api

[web1]
host=web1.example.com
port=8080
ssl=true

[web2]
host=web2.example.com
port=8080
ssl=true

[api]
host=api.example.com
port=443
ssl=true
```
**Benefits**: Clean, structured, easy to extend, still INI format!

---

## How It Works

### The Magic: ElementWithRelativeSubSection

This class creates a **template-based dynamic section loader**:

1. **Parent Element**: Contains a list of section names
2. **Template**: Defines the structure each section should have
3. **Dynamic Loading**: Automatically loads each named section using the template

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│ [DEFAULT]                                               │
│ servers=web1 web2 api  ← List of section names         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ ElementWithRelativeSubSection reads this
                 │ and creates SubSections for each name
                 ▼
    ┌────────────┴────────────┬────────────────┐
    ▼                         ▼                ▼
┌─────────┐            ┌─────────┐      ┌─────────┐
│ [web1]  │            │ [web2]  │      │  [api]  │
│ host=...│            │ host=...│      │ host=...│
│ port=...│            │ port=...│      │ port=...│
│ ssl=... │            │ ssl=... │      │ ssl=... │
└─────────┘            └─────────┘      └─────────┘
     │                      │                 │
     └──────────────────────┴─────────────────┘
                            │
                All loaded using the same template
```

---

## Basic Example

### Step 1: Define the Template

```python
from argtoolbox import (
    BasicProgram, SimpleSection, SubSection,
    Element, ElementWithRelativeSubSection
)

class MyProgram(BasicProgram):
    def add_config_options(self):
        # Create a template for what each server section looks like
        server_template = SubSection()
        server_template.add_element(Element('host', conf_required=True))
        server_template.add_element(Element('port', e_type=int, default=80))
        server_template.add_element(Element('ssl', e_type=bool, default=False))

        # Add to DEFAULT section
        default = self.config.get_default_section()
        default.add_element(
            ElementWithRelativeSubSection('servers', server_template)
        )
```

### Step 2: Create Config File

```ini
[DEFAULT]
servers=web1 web2 api

[web1]
host=web1.example.com
port=8080
ssl=true

[web2]
host=web2.example.com
port=8080
ssl=true

[api]
host=api.example.com
port=443
ssl=true
```

### Step 3: Access the Data

```python
class ListServersCommand(DefaultCommand):
    def __call__(self, args):
        # Access all servers
        servers = self.config.default.servers.sections

        for server_name, server in servers.items():
            host = server.host.value
            port = server.port.value
            ssl = server.ssl.value

            protocol = "https" if ssl else "http"
            print(f"{server_name}: {protocol}://{host}:{port}")
```

**Output**:
```
web1: https://web1.example.com:8080
web2: https://web2.example.com:8080
api: https://api.example.com:443
```

---

## Advanced Examples

### Example 1: Database Configurations

**Use Case**: Multiple database connections with connection pooling

```python
def add_config_options(self):
    # Template for database config
    db_template = SubSection()
    db_template.add_element(Element('host', conf_required=True))
    db_template.add_element(Element('port', e_type=int, default=5432))
    db_template.add_element(Element('database', conf_required=True))
    db_template.add_element(Element('user', conf_required=True))
    db_template.add_element(Element('password', conf_required=True,
                                   hidden=True))
    db_template.add_element(Element('pool_size', e_type=int, default=10))
    db_template.add_element(Element('timeout', e_type=int, default=30))

    default = self.config.get_default_section()
    default.add_element(
        ElementWithRelativeSubSection('databases', db_template)
    )
```

**Config File**:
```ini
[DEFAULT]
databases=primary replica analytics

[primary]
host=db-primary.example.com
port=5432
database=myapp
user=app_user
password=secret123
pool_size=20
timeout=30

[replica]
host=db-replica.example.com
port=5432
database=myapp
user=readonly_user
password=secret456
pool_size=10
timeout=60

[analytics]
host=analytics-db.example.com
port=5433
database=analytics
user=analyst
password=secret789
pool_size=5
timeout=120
```

**Usage**:
```python
def __call__(self, args):
    # Connect to primary
    primary = self.config.default.databases.sections['primary']
    conn = connect_db(
        host=primary.host.value,
        port=primary.port.value,
        database=primary.database.value,
        user=primary.user.value,
        password=primary.password.value,
        pool_size=primary.pool_size.value
    )

    # Or iterate all databases
    for db_name, db_config in self.config.default.databases.sections.items():
        print(f"Connecting to {db_name}...")
        # ... connection logic
```

### Example 2: Multi-Environment Deployment

**Use Case**: Different configurations for dev, staging, production

```python
def add_config_options(self):
    # Template for environment
    env_template = SubSection()
    env_template.add_element(Element('api_host', conf_required=True))
    env_template.add_element(Element('api_key', conf_required=True, hidden=True))
    env_template.add_element(Element('cdn_url'))
    env_template.add_element(Element('debug', e_type=bool, default=False))
    env_template.add_element(Element('log_level', default='INFO'))
    env_template.add_element(Element('max_workers', e_type=int, default=4))

    default = self.config.get_default_section()
    default.add_element(
        ElementWithRelativeSubSection('environments', env_template)
    )
```

**Config File**:
```ini
[DEFAULT]
environments=dev staging production

[dev]
api_host=localhost:8000
api_key=dev_key_12345
debug=true
log_level=DEBUG
max_workers=1

[staging]
api_host=staging-api.example.com
api_key=staging_key_67890
cdn_url=https://staging-cdn.example.com
debug=true
log_level=INFO
max_workers=2

[production]
api_host=api.example.com
api_key=prod_key_secret
cdn_url=https://cdn.example.com
debug=false
log_level=WARNING
max_workers=8
```

**Usage**:
```python
def __call__(self, args):
    env_name = args.environment  # e.g., "production"
    env = self.config.default.environments.sections[env_name]

    print(f"Deploying to {env_name}")
    print(f"API: {env.api_host.value}")
    print(f"Debug: {env.debug.value}")
    print(f"Workers: {env.max_workers.value}")
```

### Example 3: Service Monitoring Configuration

**Use Case**: Monitor multiple services with different check configurations

```python
def add_config_options(self):
    # Template for service monitoring
    service_template = SubSection()
    service_template.add_element(Element('url', conf_required=True))
    service_template.add_element(Element('check_interval', e_type=int, default=60))
    service_template.add_element(Element('timeout', e_type=int, default=10))
    service_template.add_element(Element('expected_status', e_type=int, default=200))
    service_template.add_element(Element('alert_email'))
    service_template.add_element(Element('retry_count', e_type=int, default=3))

    default = self.config.get_default_section()
    default.add_element(
        ElementWithRelativeSubSection('services', service_template)
    )
```

**Config File**:
```ini
[DEFAULT]
services=web api database cache

[web]
url=https://www.example.com
check_interval=30
timeout=5
expected_status=200
alert_email=ops@example.com

[api]
url=https://api.example.com/health
check_interval=60
timeout=10
expected_status=200
alert_email=api-team@example.com
retry_count=5

[database]
url=https://db.example.com:5432/health
check_interval=120
timeout=15
alert_email=dba@example.com

[cache]
url=https://cache.example.com:6379/ping
check_interval=30
timeout=2
expected_status=200
```

### Example 4: Multi-Level Nesting

**Use Case**: Servers with multiple environments, each with different configs

```python
def add_config_options(self):
    # Template for environment settings
    env_settings_template = SubSection()
    env_settings_template.add_element(Element('max_memory', e_type=int))
    env_settings_template.add_element(Element('threads', e_type=int))

    # Template for server
    server_template = SubSection()
    server_template.add_element(Element('host', conf_required=True))
    server_template.add_element(Element('port', e_type=int, default=22))
    # Nested: server has environment configs
    server_template.add_element(
        ElementWithRelativeSubSection('env_configs', env_settings_template)
    )

    default = self.config.get_default_section()
    default.add_element(
        ElementWithRelativeSubSection('servers', server_template)
    )
```

**Config File**:
```ini
[DEFAULT]
servers=web1 web2

[web1]
host=web1.example.com
port=22
env_configs=dev prod

[web1-dev]
max_memory=2048
threads=4

[web1-prod]
max_memory=8192
threads=16

[web2]
host=web2.example.com
port=22
env_configs=dev prod

[web2-dev]
max_memory=2048
threads=4

[web2-prod]
max_memory=8192
threads=16
```

**Note**: Multi-level nesting requires careful section naming conventions.

---

## Real-World Use Case: Complete Example

### Scenario: Multi-Region Cloud Deployment Tool

```python
#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from argtoolbox import (
    BasicProgram, DefaultCommand, SimpleSection,
    SubSection, Element, ElementWithRelativeSubSection,
    Base64ElementHook
)

class DeployCommand(DefaultCommand):
    def __call__(self, args):
        region_name = args.region
        region = self.config.default.regions.sections[region_name]

        print(f"\n🚀 Deploying to {region_name}")
        print(f"   Provider: {region.provider.value}")
        print(f"   API: {region.api_endpoint.value}")

        # Get all servers in this region
        for server_name, server in region.servers.sections.items():
            print(f"\n   📦 Server: {server_name}")
            print(f"      Host: {server.host.value}")
            print(f"      Type: {server.instance_type.value}")
            print(f"      Storage: {server.storage.value}GB")

class ListCommand(DefaultCommand):
    def __call__(self, args):
        print("\n📋 Available Regions:\n")
        for region_name, region in self.config.default.regions.sections.items():
            print(f"  {region_name}:")
            print(f"    Provider: {region.provider.value}")
            print(f"    Endpoint: {region.api_endpoint.value}")

            server_count = len(region.servers.sections)
            print(f"    Servers: {server_count}")

            for server_name in region.servers.sections.keys():
                print(f"      - {server_name}")

class CloudDeployTool(BasicProgram):
    def add_config_options(self):
        # Template for individual server
        server_template = SubSection()
        server_template.add_element(Element('host', conf_required=True))
        server_template.add_element(Element('instance_type', default='t2.micro'))
        server_template.add_element(Element('storage', e_type=int, default=20))
        server_template.add_element(Element('backup', e_type=bool, default=True))

        # Template for region (which contains servers)
        region_template = SubSection()
        region_template.add_element(Element('provider', conf_required=True))
        region_template.add_element(Element('api_endpoint', conf_required=True))
        region_template.add_element(Element('api_key', conf_required=True,
                                           hidden=True,
                                           hooks=[Base64ElementHook()]))
        region_template.add_element(Element('zone', default='a'))
        region_template.add_element(
            ElementWithRelativeSubSection('servers', server_template)
        )

        # Add to main config
        default = self.config.get_default_section()
        default.add_element(
            ElementWithRelativeSubSection('regions', region_template)
        )

    def add_commands(self):
        subparsers = self.parser.add_subparsers()

        # Deploy command
        deploy = subparsers.add_parser('deploy', help="Deploy to region")
        deploy.add_argument('region',
                          help="Region name (e.g., us-east, eu-west)")
        deploy.set_defaults(__func__=DeployCommand(self.config))

        # List command
        list_cmd = subparsers.add_parser('list', help="List all regions")
        list_cmd.set_defaults(__func__=ListCommand(self.config))

if __name__ == "__main__":
    PROG = CloudDeployTool(
        "cloudtool",
        desc="Multi-region cloud deployment tool"
    )
    PROG()
```

**Config File** (`~/.cloudtool.cfg`):
```ini
[DEFAULT]
regions=us-east eu-west ap-south

# ===== US East Region =====
[us-east]
provider=aws
api_endpoint=https://us-east-1.amazonaws.com
api_key=dXMtZWFzdC1rZXktMTIzNDU=
zone=us-east-1a
servers=web1 web2 db1

[us-east-web1]
host=10.0.1.10
instance_type=t3.medium
storage=50
backup=true

[us-east-web2]
host=10.0.1.11
instance_type=t3.medium
storage=50
backup=true

[us-east-db1]
host=10.0.1.100
instance_type=m5.large
storage=500
backup=true

# ===== EU West Region =====
[eu-west]
provider=aws
api_endpoint=https://eu-west-1.amazonaws.com
api_key=ZXUtd2VzdC1rZXktNjc4OTA=
zone=eu-west-1b
servers=web1 db1

[eu-west-web1]
host=10.1.1.10
instance_type=t3.small
storage=30

[eu-west-db1]
host=10.1.1.100
instance_type=m5.xlarge
storage=1000

# ===== AP South Region =====
[ap-south]
provider=gcp
api_endpoint=https://asia-south1.googleapis.com
api_key=YXAtc291dGgta2V5LWFiY2Rl
servers=web1

[ap-south-web1]
host=10.2.1.10
instance_type=n1-standard-1
storage=30
```

**Usage**:
```bash
# List all regions
$ ./cloudtool.py list

📋 Available Regions:

  us-east:
    Provider: aws
    Endpoint: https://us-east-1.amazonaws.com
    Servers: 3
      - web1
      - web2
      - db1
  eu-west:
    Provider: aws
    Endpoint: https://eu-west-1.amazonaws.com
    Servers: 2
      - web1
      - db1
  ap-south:
    Provider: gcp
    Endpoint: https://asia-south1.googleapis.com
    Servers: 1
      - web1

# Deploy to specific region
$ ./cloudtool.py deploy us-east

🚀 Deploying to us-east
   Provider: aws
   API: https://us-east-1.amazonaws.com

   📦 Server: web1
      Host: 10.0.1.10
      Type: t3.medium
      Storage: 50GB

   📦 Server: web2
      Host: 10.0.1.11
      Type: t3.medium
      Storage: 50GB

   📦 Server: db1
      Host: 10.0.1.100
      Type: m5.large
      Storage: 500GB
```

---

## Key Benefits of This Approach

### 1. **Scalability**
Add new items by just adding a name to the list and creating a new section:
```ini
# Before
servers=web1 web2

# After - just add web3 to the list and create [web3] section
servers=web1 web2 web3

[web3]
host=web3.example.com
port=8080
```

### 2. **Consistency**
Template ensures all sections have the same structure:
- Required fields are enforced
- Types are validated
- Defaults are applied uniformly

### 3. **Simplicity**
Users can edit config files without programming knowledge:
- Standard INI format
- Clear section boundaries
- Comments supported

### 4. **Maintainability**
Change the template once, affects all instances:
```python
# Add a new field to the template
server_template.add_element(Element('monitoring', e_type=bool, default=True))

# Now all servers can have monitoring config
```

### 5. **Validation**
Built-in validation for each subsection:
- Required fields checked automatically
- Type mismatches caught early
- Clear error messages

---

## Advanced Patterns

### Pattern 1: Dynamic Section Names from CLI

```python
class AddServerCommand(DefaultCommand):
    def __call__(self, args):
        server_name = args.name

        # Check if server exists
        if server_name in self.config.default.servers.sections:
            print(f"Server {server_name} already exists!")
            return False

        print(f"Add configuration for {server_name} to config file")
        print(f"[{server_name}]")
        print(f"host=...")
        print(f"port=...")
```

### Pattern 2: Validation Across All Sections

```python
class ValidateCommand(DefaultCommand):
    def __call__(self, args):
        servers = self.config.default.servers.sections

        # Check for port conflicts
        ports = {}
        for name, server in servers.items():
            port = server.port.value
            if port in ports:
                print(f"⚠️  Port conflict: {name} and {ports[port]} both use port {port}")
            else:
                ports[port] = name

        # Check for missing required fields
        for name, server in servers.items():
            if not server.host.value:
                print(f"❌ Server {name} missing host!")
```

### Pattern 3: Conditional Loading

```python
class DeployCommand(DefaultCommand):
    def __call__(self, args):
        # Only process servers matching filter
        env_filter = args.environment  # e.g., "production"

        servers = self.config.default.servers.sections
        for name, server in servers.items():
            # Assuming servers have environment field
            if server.environment.value == env_filter:
                print(f"Deploying {name}...")
                # Deploy logic
```

### Pattern 4: Section Generation

```python
def generate_config_template():
    """Generate a config template with example sections"""
    template = """[DEFAULT]
servers=example1 example2

[example1]
host=server1.example.com
port=8080
ssl=true

[example2]
host=server2.example.com
port=8080
ssl=true
"""
    with open('config-template.cfg', 'w') as f:
        f.write(template)
    print("Template generated: config-template.cfg")
```

---

## Comparison with Alternatives

### vs. Multiple Flat Sections

**Flat**:
```ini
[server_web1]
host=...
port=...

[server_web2]
host=...
port=...
```
❌ No relationship between sections
❌ Manual iteration
❌ No template/validation

**ElementWithRelativeSubSection**:
```ini
[DEFAULT]
servers=web1 web2

[web1]
host=...

[web2]
host=...
```
✅ Clear relationship
✅ Automatic iteration
✅ Template enforces structure

### vs. JSON/YAML Arrays

**JSON**:
```json
{
  "servers": [
    {"name": "web1", "host": "...", "port": 80},
    {"name": "web2", "host": "...", "port": 80}
  ]
}
```
❌ Different file format
❌ Requires JSON parser
❌ No comments (JSON)

**ElementWithRelativeSubSection**:
✅ Standard INI format
✅ Built-in Python ConfigParser
✅ Comments supported

---

## Best Practices

### 1. Naming Conventions

Use clear, hierarchical naming:
```ini
# Good
[us-east]
servers=web1 web2

[us-east-web1]
host=...

# Avoid
[server1]  # Which region?
[cfg_001]  # Not descriptive
```

### 2. Required Fields

Mark truly required fields in template:
```python
server_template.add_element(
    Element('host', conf_required=True)  # Will fail if missing
)
```

### 3. Sensible Defaults

Provide defaults for common values:
```python
server_template.add_element(
    Element('port', e_type=int, default=80)
)
```

### 4. Documentation in Config Files

Use comments:
```ini
[DEFAULT]
# List of servers to configure
# Format: space-separated names
servers=web1 web2 api

[web1]
# Server hostname or IP
host=web1.example.com

# Port number (1-65535)
port=8080
```

### 5. Validation Hooks

Add validation to ensure consistency:
```python
class PortRangeHook(DefaultHook):
    def __call__(self, elt):
        if elt.value and not (1 <= elt.value <= 65535):
            raise ValueError(f"Port must be 1-65535, got {elt.value}")

server_template.add_element(
    Element('port', e_type=int, hooks=[PortRangeHook()])
)
```

---

## Common Pitfalls

### 1. Forgetting to List Section Names

❌ **Wrong**:
```ini
[DEFAULT]
# servers= <-- Forgot to list them!

[web1]
host=...
```

✅ **Correct**:
```ini
[DEFAULT]
servers=web1 web2  # Must list all section names

[web1]
host=...
```

### 2. Typo in Section Names

❌ **Wrong**:
```ini
[DEFAULT]
servers=web1 web2

[web1]
host=...

[web2_typo]  # Typo! Should be web2
host=...
```
Error: Section 'web2' not found

### 3. Missing Required Fields

❌ **Wrong**:
```ini
[web1]
# host= <-- Missing required field!
port=8080
```

✅ **Correct**:
```ini
[web1]
host=web1.example.com
port=8080
```

### 4. Type Mismatches

❌ **Wrong**:
```ini
[web1]
host=web1.example.com
port=abc  # Should be integer!
```

✅ **Correct**:
```ini
[web1]
host=web1.example.com
port=8080
```

---

## Testing

```python
import unittest
from io import BytesIO

class TestHierarchicalConfig(unittest.TestCase):
    def test_multiple_servers(self):
        config_data = b"""
[DEFAULT]
servers=web1 web2

[web1]
host=web1.example.com
port=8080

[web2]
host=web2.example.com
port=9090
"""
        prog = MyProgram("test", config_file=BytesIO(config_data))
        prog.add_config_options()
        prog.load()

        servers = prog.config.default.servers.sections

        # Check we have 2 servers
        self.assertEqual(len(servers), 2)

        # Check web1
        self.assertEqual(servers['web1'].host.value, 'web1.example.com')
        self.assertEqual(servers['web1'].port.value, 8080)

        # Check web2
        self.assertEqual(servers['web2'].host.value, 'web2.example.com')
        self.assertEqual(servers['web2'].port.value, 9090)
```

---

## Summary

**ElementWithRelativeSubSection** is a powerful feature that allows you to:

✅ Create **hierarchical configurations** using simple INI files
✅ Define a **template once**, apply to **many instances**
✅ **Scale easily** by adding items to a list
✅ **Maintain consistency** through template validation
✅ Keep configuration **readable and maintainable**
✅ Use **standard INI format** (no YAML/JSON needed)

This is especially valuable for:
- Multi-server deployments
- Multi-environment configurations
- Service monitoring
- Database connection pools
- Any scenario with "many similar things"

**This is one of the most unique and powerful features of argtoolbox!** 🚀

---

For more information:
- Full API reference: DOCUMENTATION.md
- Quick syntax: QUICK_REFERENCE.md
- Internal architecture: ARCHITECTURE.md
