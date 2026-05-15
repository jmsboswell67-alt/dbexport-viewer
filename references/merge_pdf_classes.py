"""Merge PDF class harvest into index.html as the authoritative source.

Strategy:
- PDF entries win for any cid present in both
- PDF-only entries are added
- Ours-only entries are kept (empirical from archives, PDF doesn't cover them)
- Output: rewritten CLASS_NAMES block, ready to swap into index.html

We also produce a list of corrections (with annotation) for the commit message.
"""
import json, re
from pathlib import Path

pdf = json.load(open(r'D:\metasys-viewer\references\pdf_classes_raw.json'))
html_path = Path(r'D:\metasys-viewer\index.html')
html = html_path.read_text(encoding='utf-8')

# Parse current dictionary
m = re.search(r'const CLASS_NAMES = \{([\s\S]*?)\};', html)
body = m.group(1)
current = dict(re.findall(r'(\d+):\s*"((?:[^"\\]|\\.)*)"', body))

# Merge: PDF authoritative, keep ours-only
merged = dict(current)  # start with ours
corrections = []
additions = []
for cid, pdf_name in pdf.items():
    if cid in current and current[cid] != pdf_name:
        corrections.append((cid, current[cid], pdf_name))
        merged[cid] = pdf_name
    elif cid not in current:
        additions.append((cid, pdf_name))
        merged[cid] = pdf_name

print(f"Merged: {len(merged)} total classes")
print(f"Corrections: {len(corrections)}")
print(f"Additions:   {len(additions)}")

# Build the new JS object literal block
def js_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

lines = ["const CLASS_NAMES = {"]
for cid in sorted(merged.keys(), key=int):
    lines.append(f"  {cid}: {js_str(merged[cid])},")
lines.append("};")
new_block = "\n".join(lines)

# Write the replacement block to a file
Path(r'D:\metasys-viewer\references\new_class_names_block.js').write_text(new_block, encoding='utf-8')

# Replace in index.html
new_html = re.sub(r'const CLASS_NAMES = \{[\s\S]*?\};', new_block, html, count=1)
html_path.write_text(new_html, encoding='utf-8')
print(f"Wrote merged dictionary back to index.html ({len(merged)} classes)")
print()
print("=== Top 30 corrections (showing first) ===")
for cid, old, new in sorted(corrections, key=lambda x: int(x[0]))[:30]:
    print(f"  cid={cid:<5}  {old!r:55} -> {new!r}")
print()
print("=== Sample new additions ===")
for cid, name in sorted(additions, key=lambda x: int(x[0]))[:30]:
    print(f"  cid={cid:<5}  {name!r}")
