"""Harvest property/attribute IDs and class IDs from JCI XML metadata files.

Pattern in AttributeSetList.xml, globalModifyList.xml etc:
    <attribute id="631" />          <!-- High Alarm Limit -->

Pattern in commands.xml is variable:
    <!-- JCI Trend Log -->
    <class id="155" version="1.0" />
or
    <class id="156" version="1.0" />     <!-- Analog Alarm -->

We harvest both same-line-after and prev-line-before comment patterns.
"""

import re, json, datetime, os

ROOT = r'D:\metasys-viewer\references\extracted\14.0.0.43\ui_fw'

SOURCES = [
    'com/jci/domain/summarydef/AttributeSetList.xml',
    'com/jci/domain/summarydef/AttributeSetListSCT.xml',
    'com/jci/domain/globalmodify/globalModifyList.xml',
    'com/jci/domain/globalcommand/commands.xml',
]

# Capture either:
#   <tag id="N" ...> ... <!-- name -->
#   <!-- name --> ... <tag id="N" ...>
# We use a simple state-machine over lines so we don't need fragile XML parsing.

attrs = {}        # id -> name
classes = {}      # id -> name
attr_conflicts = []   # (id, name1, name2, source)
class_conflicts = []

def harvest_file(path):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    last_comment = None
    for raw in lines:
        # Same-line: capture comment on the line first if any
        same_line_match = re.search(r'<!--\s*(.*?)\s*-->', raw)
        same_line_text = same_line_match.group(1).strip() if same_line_match else None

        # Strip the noisy headers
        def is_real_label(s):
            if not s: return False
            if s.startswith('Notes:'): return False
            if s.startswith('*'): return False
            if 'Range checking' in s: return False
            if 'Attribute Filter ID' in s: return False
            if 'unitsId=' in s: return False
            if 'enum set' in s.lower() and 'is the' in s.lower(): return False
            if 'Float/double' in s: return False
            if 'Default value' in s: return False
            if 'common to all' in s.lower(): return False
            if 'apply to' in s.lower() and 'extension' in s.lower(): return False
            if 'apply only' in s.lower(): return False
            if 'listed here' in s.lower(): return False
            if 'edited with' in s.lower(): return False
            if '<![CDATA' in s: return False
            return True

        # Match attribute
        m_attr = re.search(r'<attribute\s+(?:default="true"\s+)?id="(\d+)"', raw)
        # Match class
        m_class = re.search(r'<class\s+id="(\d+)"', raw)

        # Determine name: prefer same-line comment, fall back to last_comment
        name = None
        if same_line_text and is_real_label(same_line_text) and (m_attr or m_class):
            name = same_line_text
        elif last_comment and is_real_label(last_comment) and (m_attr or m_class):
            name = last_comment

        if m_attr and name:
            aid = m_attr.group(1)
            if aid in attrs and attrs[aid] != name:
                attr_conflicts.append((aid, attrs[aid], name, os.path.basename(path)))
            else:
                attrs.setdefault(aid, name)

        if m_class and name:
            cid = m_class.group(1)
            if cid in classes and classes[cid] != name:
                class_conflicts.append((cid, classes[cid], name, os.path.basename(path)))
            else:
                classes.setdefault(cid, name)

        # Update last_comment for use by NEXT line
        if same_line_text and is_real_label(same_line_text) and not (m_attr or m_class):
            last_comment = same_line_text
        elif raw.strip() == '' or '<class' in raw or '<attribute' in raw:
            last_comment = None  # reset after blank or non-comment line, or after consuming

for p in SOURCES:
    full = os.path.join(ROOT, p)
    if not os.path.exists(full):
        print(f"skip missing: {p}")
        continue
    print(f"harvesting {p}")
    harvest_file(full)

print()
print(f"Total: {len(attrs)} unique attribute IDs, {len(classes)} unique class IDs")
print(f"Conflicts: {len(attr_conflicts)} attribute, {len(class_conflicts)} class")
if attr_conflicts[:5]:
    print("Sample attribute conflicts (kept first):")
    for c in attr_conflicts[:5]:
        print(f"  id={c[0]}: kept '{c[1]}' rejected '{c[2]}' (from {c[3]})")

# Save consolidated dictionary
out = {
    "_source": "JCI Metasys 14.0.0.43 — extracted from public Launcher resource bundle (commands.xml, AttributeSetList.xml, AttributeSetListSCT.xml, globalModifyList.xml). Comments are factual ID->name mappings, not creative expression — used as interop reference per Sega v. Accolade.",
    "_harvested_at": datetime.datetime.now().isoformat(timespec='seconds'),
    "attributes_count": len(attrs),
    "classes_count": len(classes),
    "attributes": dict(sorted(attrs.items(), key=lambda kv: int(kv[0]))),
    "classes": dict(sorted(classes.items(), key=lambda kv: int(kv[0]))),
}
out_path = r'D:\metasys-viewer\references\dictionary.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print()
print(f"Wrote {out_path}")
print()
print("=== Sample attributes ===")
for aid in sorted(attrs.keys(), key=int)[:40]:
    print(f"  {aid:>6}: {attrs[aid]}")
print()
print("=== Sample classes ===")
for cid in sorted(classes.keys(), key=int)[:40]:
    print(f"  {cid:>5}: {classes[cid]}")
