"""Merge harvested PDF attribute names into PROP_NAMES in index.html.

- Clean concatenated names: "FooBar" -> "Foo Bar"
- Filter known noise (page-number IDs 114-119 with name "Page")
- PDF authoritative on conflicts
- Print correction/addition report
"""
import json, re
from pathlib import Path

pdf = json.load(open(r'D:\metasys-viewer\references\pdf_attributes_raw.json'))

# Clean concatenated camelCase
def fix_concat(name):
    # Insert space between lowercase-uppercase boundaries: "FooBar" -> "Foo Bar"
    # But only AFTER 2+ lowercase chars (so we don't break "BACnet")
    s = re.sub(r'([a-z]{2})([A-Z])', r'\1 \2', name)
    # Collapse runs of whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# Noise filter
def is_noise(pid, name):
    if name.lower() == 'page': return True
    if name.lower() == 'note': return True
    return False

cleaned = {}
for pid, name in pdf.items():
    name = fix_concat(name)
    if is_noise(pid, name): continue
    cleaned[pid] = name

print(f"After cleanup: {len(cleaned)} attribute entries (was {len(pdf)})")

# Parse current dictionary out of index.html
html_path = Path(r'D:\metasys-viewer\index.html')
html = html_path.read_text(encoding='utf-8')
m = re.search(r'const PROP_NAMES = \{([\s\S]*?)\};', html)
current = dict(re.findall(r'(\d+):\s*"((?:[^"\\]|\\.)*)"', m.group(1)))
print(f"Current PROP_NAMES: {len(current)}")

# Merge
merged = dict(current)
corrections = []
additions = []
for pid, pdf_name in cleaned.items():
    if pid in current and current[pid] != pdf_name:
        # Only correct if PDF name is meaningfully different (avoid e.g. "Description" -> "Description")
        if current[pid].lower() != pdf_name.lower():
            corrections.append((pid, current[pid], pdf_name))
            merged[pid] = pdf_name
    elif pid not in current:
        additions.append((pid, pdf_name))
        merged[pid] = pdf_name

print(f"Merged: {len(merged)} attributes  (added {len(additions)}, corrected {len(corrections)})")

# Write back into index.html
def js_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

lines = ["const PROP_NAMES = {"]
for pid in sorted(merged.keys(), key=int):
    lines.append(f"  {pid}: {js_str(merged[pid])},")
lines.append("};")
new_block = "\n".join(lines)

new_html = re.sub(r'const PROP_NAMES = \{[\s\S]*?\};', new_block, html, count=1)
html_path.write_text(new_html, encoding='utf-8')
print(f"Wrote merged PROP_NAMES back to index.html")
print()
print("=== Corrections ===")
for pid, old, new in sorted(corrections, key=lambda x: int(x[0])):
    print(f"  {pid:>6}: {old!r} -> {new!r}")
print()
print("=== Sample new additions (first 30) ===")
for pid, name in sorted(additions, key=lambda x: int(x[0]))[:30]:
    print(f"  {pid:>6}: {name!r}")
