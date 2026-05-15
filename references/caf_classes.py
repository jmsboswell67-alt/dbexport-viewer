"""For each classid in the .caf, find an example object's Description (prop 28)
or Model Name (prop 70) — this gives us the CCT logic-block names directly from
the .caf itself, no decompilation needed."""

import xml.etree.ElementTree as ET, collections, os
ns = {'jci': 'http://johnsoncontrols.com/MetasysIII/2002/3/Core'}
path = r'C:\Users\jmsbo\AppData\Local\Temp\caf_extract\for sct courthouse.caf.xml'
tree = ET.parse(path)
root = tree.getroot()

# For each classid: collect distinct Description values
by_class = collections.defaultdict(lambda: collections.Counter())
for obj in root.findall('jci:object', ns):
    cid = obj.get('classid')
    for p in obj.findall('jci:property', ns):
        if p.get('id') == '28':
            data = p.find('jci:data', ns)
            if data is not None:
                s = data.find('jci:string', ns)
                if s is not None and s.text:
                    by_class[cid][s.text.strip()] += 1

print(f"{'cid':>5}  {'count':>5}  examples (top descriptions)")
for cid in sorted(by_class.keys(), key=int):
    descs = by_class[cid]
    total = sum(descs.values())
    top = ', '.join(f'"{d}" x{n}' for d, n in descs.most_common(3))
    print(f"  {cid:>3}  {total:>5}  {top[:120]}")
