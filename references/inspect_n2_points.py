"""Look at the SIU VMA10 N2 points to see what properties hold the CCT point number."""
import zipfile, re, xml.etree.ElementTree as ET, os

ARC = r'C:\Users\jmsbo\Desktop\jci\SIUMedCurrent.dbexport'
NS = {'jci': 'http://johnsoncontrols.com/MetasysIII/2002/3/Core'}

# Find a device folder for the engine that has VMA10
with zipfile.ZipFile(ARC) as z:
    candidates = [info for info in z.infolist()
                  if info.filename.endswith('archive.xml') and 'SIUSOM825ANAE01' in info.filename]
    print(f"Candidate engine archives: {len(candidates)}")
    for c in candidates:
        print(f"  {c.filename} ({c.file_size:,} bytes)")
    if not candidates:
        print("none found; falling back to first archive.xml")
        candidates = [info for info in z.infolist() if info.filename.endswith('archive.xml')]

    # Read the largest one (likely the main engine archive)
    target = max(candidates, key=lambda c: c.file_size)
    print(f"\nReading: {target.filename}")
    with z.open(target) as f:
        text = f.read().decode('utf-8', errors='replace')

# Find a sample N2 point — DA-T on VMA10
root = ET.fromstring(text)
objects = root.findall('jci:object', NS)
print(f"\nTotal objects in this engine: {len(objects)}")

# Find VMA10's DA-T point
samples = []
for obj in objects:
    ref = obj.get('ref', '')
    cid = obj.get('classid', '')
    # Look for points under VMA10
    if 'VMA10' not in ref: continue
    if 'VMA10' == ref.split('.')[-1]: continue  # the controller itself
    samples.append((ref, cid, obj))

print(f"VMA10 points found: {len(samples)}")
for ref, cid, obj in samples[:5]:
    print(f"\n=== {ref} (cid {cid}) ===")
    for prop in obj.findall('jci:property', NS):
        pid = prop.get('id')
        data = prop.find('jci:data', NS)
        if data is not None:
            children = list(data)
            if children:
                tag = children[0].tag.split('}')[-1]
                # Get the inner text/value
                text = ET.tostring(children[0], encoding='unicode').strip()[:80]
                print(f"  prop {pid:>5} [{tag:15}]: {text}")
