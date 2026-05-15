"""Decode a Programming file and inventory the geometry / structure we'd need to render."""
import zipfile, re, base64, gzip, collections

ARC = r'C:\Users\jmsbo\Desktop\jci\DACC1092025POSTCHANGEMARCH2025.dbexport'

with zipfile.ZipFile(ARC) as z:
    target = None
    for info in z.infolist():
        if info.filename.endswith('Programming.AHU-7-1.xml'):
            target = info
            break
    if not target:
        print("not found")
        raise SystemExit

    with z.open(target) as f:
        raw = f.read().decode('utf-8', errors='replace')
    m = re.search(r'<Base64Zip[^>]*>([\s\S]*?)</Base64Zip>', raw)
    inner = gzip.decompress(base64.b64decode(m.group(1).strip())).decode('utf-8', errors='replace')

print(f"=== Decoded {target.filename} — {len(inner):,} chars ===\n")

# Element-type frequency
tag_counts = collections.Counter(re.findall(r'<([A-Za-z][A-Za-z0-9]+)[>\s/]', inner))
print("Top element types:")
for tag, n in tag_counts.most_common(20):
    print(f"  {n:>5}  <{tag}>")
print()

# Sample a node block
m = re.search(r'<node>(\d+)<type>.*?</node>', inner, re.S)
if m:
    print(f"Sample <node> (first one, {len(m.group(0))} chars):")
    print(m.group(0)[:1500])
    print()

# Count distinct geometry — how many nodes have visible x/y/w/h?
nodes_with_geom = re.findall(r'<node>(\d+)<type>[^<]*</type>(?:<text>[^<]*</text>)?<geometry><visible>true</visible><x>([\d.\-]+)</x><y>([\d.\-]+)</y><width>([\d.\-]+)</width><height>([\d.\-]+)</height>', inner)
print(f"Nodes with visible geometry: {len(nodes_with_geom)}")
if nodes_with_geom[:5]:
    print("Sample:")
    for n in nodes_with_geom[:5]:
        print(f"  id={n[0]:>6} x={n[1]:>8} y={n[2]:>8} w={n[3]:>6} h={n[4]:>6}")

# Connectors (edges)
connectors = re.findall(r'<connector>(\d+)<geometry>', inner)
print(f"\nConnector elements: {len(connectors)}")
