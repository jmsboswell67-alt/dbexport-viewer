"""Explore the Metasys REST API OpenAPI spec to find attribute/property name sources."""
import json, collections, re

with open(r'D:\metasys-viewer\references\openapi.json', encoding='utf-8') as f:
    spec = json.load(f)

print(f"Title: {spec['info']['title']}")
print(f"Version: {spec['info']['version']}")
print(f"Top-level keys: {list(spec.keys())}")
print()

# Schemas — where the property name dictionaries usually live in OpenAPI
schemas = spec.get('components', {}).get('schemas', {})
print(f"Schemas: {len(schemas)}")
# Show schemas with 'object' in name or that look like attribute definitions
for name in sorted(schemas.keys())[:30]:
    sch = schemas[name]
    if isinstance(sch, dict):
        kind = sch.get('type', '?')
        n_props = len(sch.get('properties', {})) if sch.get('properties') else 0
        enum_n = len(sch.get('enum', [])) if sch.get('enum') else 0
        if n_props > 0 or enum_n > 0 or 'description' in sch:
            extra = f"({n_props} props, {enum_n} enums)" if (n_props or enum_n) else ""
            print(f"  {name:50}  type={kind:8} {extra}")

print()
print("=== Searching for 'attribute' or 'objectType' related schemas ===")
for name in sorted(schemas.keys()):
    if re.search(r'attribute|objectType|enumSet|metadata', name, re.I):
        print(f"  {name}")
