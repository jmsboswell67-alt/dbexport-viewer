"""Fully map TSEGraph structure. We need:
   - All node types (with frequency)
   - All <edge>/<link>/<connection> elements (the actual edges between nodes)
   - Field layout of a node, connector, edge
   - Where attrNum (point binding) lives
"""
import zipfile, re, base64, gzip, collections, os

ARC = r'C:\Users\jmsbo\Desktop\jci\DACC1092025POSTCHANGEMARCH2025.dbexport'

def decode_b64zip(text):
    m = re.search(r'<Base64Zip[^>]*>([\s\S]*?)</Base64Zip>', text)
    if not m: return None
    return gzip.decompress(base64.b64decode(m.group(1).strip())).decode('utf-8', errors='replace')

with zipfile.ZipFile(ARC) as z:
    # Look at Programming/System Programs files
    prog_files = [info for info in z.infolist()
                  if (info.filename.endswith('.xml')
                      and ('Programming.' in info.filename or 'System Programs.' in info.filename))
                  and 'archive.xml' not in info.filename]
    print(f"Programming files: {len(prog_files)}")
    for info in prog_files[:6]:
        print(f"  {info.file_size:>8}  {info.filename}")

# Decode the AHU-7-1 one — already known to have rich content
with zipfile.ZipFile(ARC) as z:
    target = next(info for info in z.infolist() if info.filename.endswith('Programming.AHU-7-1.xml'))
    with z.open(target) as f:
        raw = f.read().decode('utf-8', errors='replace')
inner = decode_b64zip(raw)

# Map structure
print(f"\n=== {target.filename} ({len(inner):,} chars) ===\n")

# All distinct top-level element types appearing in nesting
tags = collections.Counter(re.findall(r'<([A-Za-z][A-Za-z0-9_]+)>', inner))
print("Element types by frequency:")
for tag, n in tags.most_common(40):
    print(f"  {n:>5}  <{tag}>")

print()
# Look for edge-like elements
for et in ['edge', 'link', 'connection', 'wire', 'connect']:
    pat = rf'<{et}[ >]'
    hits = len(re.findall(pat, inner, re.I))
    print(f"  <{et}> matches: {hits}")

# Find the top-level structure — what comes between <topology> and </topology>?
m = re.search(r'<topology>([\s\S]{0,4000})', inner)
if m:
    print(f"\nFirst 1500 chars after <topology>:")
    print(m.group(1)[:1500])
