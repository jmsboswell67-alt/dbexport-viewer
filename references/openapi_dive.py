"""Look at the most-likely dictionary sources in the OpenAPI spec."""
import json, re

with open(r'D:\metasys-viewer\references\openapi.json', encoding='utf-8') as f:
    spec = json.load(f)
schemas = spec['components']['schemas']

# 1. The objectType schema — likely an enum of class names
ot = schemas.get('objectType', {})
print("=== objectType schema ===")
print(json.dumps(ot, indent=2)[:2000])
print()

# 2. classification schema (had 12 enums)
print("=== classification schema ===")
print(json.dumps(schemas.get('classification', {}), indent=2)[:1000])
print()

# 3. Search all schemas for enum lists > 5 items (likely controlled vocabularies)
print("=== Schemas with enum > 5 ===")
for name, s in schemas.items():
    if isinstance(s, dict) and isinstance(s.get('enum'), list) and len(s['enum']) > 5:
        print(f"  {name}: {len(s['enum'])} values — sample: {s['enum'][:5]}")
print()

# 4. Recursively scan all schemas for "enum" arrays nested under 'properties'
print("=== Nested enums in property definitions ===")
def scan(node, path=''):
    if isinstance(node, dict):
        if 'enum' in node and isinstance(node['enum'], list) and len(node['enum']) > 5:
            print(f"  {path}: {len(node['enum'])} enums — sample: {node['enum'][:5]}")
        for k, v in node.items():
            scan(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            scan(v, f"{path}[{i}]")
scan(schemas, 'schemas')
