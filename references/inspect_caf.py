"""Inspect the .caf XML structure."""
import xml.etree.ElementTree as ET, collections

path = r'/tmp/caf_extract/for sct courthouse.caf.xml'
# git-bash maps /tmp to C:\Users\<u>\AppData\Local\Temp
import os
if not os.path.exists(path):
    path = r'C:\Users\jmsbo\AppData\Local\Temp\caf_extract\for sct courthouse.caf.xml'

ns = {'jci': 'http://johnsoncontrols.com/MetasysIII/2002/3/Core'}
tree = ET.parse(path)
root = tree.getroot()

objects = root.findall('jci:object', ns)
print(f"Total objects: {len(objects)}")
print()

# Count by classid
counts = collections.Counter()
samples = {}
for obj in objects:
    cid = obj.get('classid')
    ref = obj.get('ref', '')
    counts[cid] += 1
    if cid not in samples:
        samples[cid] = ref

print("Top classes:")
for cid, n in counts.most_common(30):
    print(f"  cid={cid:>5}  n={n:>5}  e.g. {samples[cid]}")

# Show the first object structurally (counts of property IDs)
first = objects[0]
print()
print(f"First object: ref={first.get('ref')} classid={first.get('classid')} objectid={first.get('objectid')}")
props = first.findall('jci:property', ns)
print(f"  {len(props)} properties: {[p.get('id') for p in props[:15]]}")

# Check for anything interesting — large structs, embedded code/graphs?
# Look for properties whose XML payload is >500 bytes
print()
print("Largest single properties:")
big = []
for obj in objects:
    for p in obj.findall('jci:property', ns):
        size = len(ET.tostring(p))
        if size > 1000:
            big.append((size, obj.get('ref'), p.get('id')))
big.sort(reverse=True)
for size, ref, pid in big[:8]:
    print(f"  {size:>6}B  ref={ref:<50} prop={pid}")
