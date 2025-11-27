# Analysis Tools

Python utilities for analyzing ChatGPT and Codex.

## Available Tools

### hash_scanner.py
Detects hashed numeric IDs throughout the repository.

**Usage:**
```bash
python tools/hash_scanner.py
```

### obfuscation_scanner.py
Identifies obfuscation patterns in JavaScript code.

**Usage:**
```bash
python tools/obfuscation_scanner.py
```

### service_function_scanner.py
Extracts service and function signatures from code.

**Usage:**
```bash
python tools/service_function_scanner.py
```

### statsig_inventory.py
Builds inventory of Statsig feature flags and experiments.

**Usage:**
```bash
python tools/statsig_inventory.py
```

### statsig_resolver.py
Resolves feature gates by hash value.

**Usage:**
```bash
python tools/statsig_resolver.py <hash>
```

## Requirements

Most tools require Python 3.8+ and may need additional dependencies.
