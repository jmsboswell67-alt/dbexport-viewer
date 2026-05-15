"""Harvest property/class dictionaries from MULTIPLE Metasys versions and union them.

Walks every version directory under extracted/, pulls the four dictionary XMLs,
parses XML-comment-labeled <attribute> and <class> elements, and merges into a
single dictionary keyed by ID. First version to define an entry wins (we walk
newest-first so the current naming is preferred).
"""

import re, json, datetime, os, glob

ROOT = r'D:\metasys-viewer\references\extracted'

# Walk newest first so we prefer current naming on conflict
VERSIONS = ['14.0.0.43', '13.0.3.2', '13.0.2.2', '13.0.0.240', '10.4.0.1601']
SOURCES = [
    'AttributeSetList.xml',
    'AttributeSetListSCT.xml',
    'globalModifyList.xml',
    'commands.xml',
]

attrs = {}        # id -> {name, sources}
classes = {}      # id -> {name, sources}
attr_conflicts = []
class_conflicts = []

def is_real_label(s):
    if not s: return False
    s = s.strip()
    skips = ['Notes:', '*', 'Range checking', 'Attribute Filter ID', 'unitsId=',
             'Float/double', 'Default value', 'common to all', 'apply to',
             'apply only', 'listed here', 'edited with', '<![CDATA',
             'is the States enum', 'this is', 'TODO', 'FIXME', 'XXX',
             'Attributes added', 'NOTE', 'Note ']
    sl = s.lower()
    if any(sl.startswith(p.lower()) for p in skips): return False
    if any(p.lower() in sl for p in skips): return False
    if len(s) > 80: return False  # commentary, not a label
    return True

def harvest_one(version, xml_path):
    if not os.path.exists(xml_path):
        return 0, 0
    n_a, n_c = 0, 0
    with open(xml_path, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    last_comment = None
    for raw in lines:
        same_line_match = re.search(r'<!--\s*(.*?)\s*-->', raw)
        same_line_text = same_line_match.group(1).strip() if same_line_match else None
        m_attr = re.search(r'<attribute\s+(?:default="true"\s+)?id="(\d+)"', raw)
        m_class = re.search(r'<class\s+id="(\d+)"', raw)

        name = None
        if same_line_text and is_real_label(same_line_text) and (m_attr or m_class):
            name = same_line_text
        elif last_comment and is_real_label(last_comment) and (m_attr or m_class):
            name = last_comment

        if m_attr and name:
            aid = m_attr.group(1)
            if aid not in attrs:
                attrs[aid] = {'name': name, 'sources': [f"{version}:{os.path.basename(xml_path)}"]}
                n_a += 1
            else:
                attrs[aid]['sources'].append(f"{version}:{os.path.basename(xml_path)}")
                if attrs[aid]['name'] != name:
                    attr_conflicts.append((aid, attrs[aid]['name'], name, version, os.path.basename(xml_path)))

        if m_class and name:
            cid = m_class.group(1)
            if cid not in classes:
                classes[cid] = {'name': name, 'sources': [f"{version}:{os.path.basename(xml_path)}"]}
                n_c += 1
            else:
                classes[cid]['sources'].append(f"{version}:{os.path.basename(xml_path)}")
                if classes[cid]['name'] != name:
                    class_conflicts.append((cid, classes[cid]['name'], name, version, os.path.basename(xml_path)))

        if same_line_text and is_real_label(same_line_text) and not (m_attr or m_class):
            last_comment = same_line_text
        elif raw.strip() == '' or m_class or m_attr:
            last_comment = None
    return n_a, n_c

print("Harvesting across versions (newest first wins on conflict):")
for version in VERSIONS:
    # Look in two possible places: extracted/<v>/xmls or extracted/<v>/ui_fw/com/...
    candidate_dirs = [
        os.path.join(ROOT, version, 'xmls'),
        os.path.join(ROOT, version, 'ui_fw', 'com', 'jci', 'domain', 'summarydef'),
        os.path.join(ROOT, version, 'ui_fw', 'com', 'jci', 'domain', 'globalcommand'),
        os.path.join(ROOT, version, 'ui_fw', 'com', 'jci', 'domain', 'globalmodify'),
    ]
    files_found = []
    for d in candidate_dirs:
        if os.path.isdir(d):
            for src in SOURCES:
                p = os.path.join(d, src)
                if os.path.exists(p):
                    files_found.append(p)
    # Dedupe
    files_found = sorted(set(files_found))
    new_a, new_c = 0, 0
    for fp in files_found:
        a, c = harvest_one(version, fp)
        new_a += a
        new_c += c
    print(f"  {version}: {len(files_found)} files, +{new_a} attrs, +{new_c} classes (cumulative: {len(attrs)} attrs, {len(classes)} classes)")

print()
print(f"FINAL: {len(attrs)} unique attribute IDs, {len(classes)} unique class IDs")
print(f"Conflicts (kept first/newest): {len(attr_conflicts)} attribute, {len(class_conflicts)} class")
print()
if attr_conflicts[:8]:
    print("Sample attribute conflicts (kept first):")
    for c in attr_conflicts[:8]:
        print(f"  id={c[0]}: kept '{c[1]}' vs '{c[2]}' (newer doc said '{c[1]}', older '{c[2]}' from {c[3]})")

# Strip down to just {id: name} for the JSON output
attrs_flat = {k: v['name'] for k, v in attrs.items()}
classes_flat = {k: v['name'] for k, v in classes.items()}

out = {
    "_source": "JCI Metasys public Launcher resource bundles: 14.0.0.43, 13.0.3.2, 13.0.2.2, 13.0.0.240, 10.4.0.1601. Factual ID->name mappings extracted from XML comments. Original files not redistributed.",
    "_harvested_at": datetime.datetime.now().isoformat(timespec='seconds'),
    "versions": VERSIONS,
    "attributes_count": len(attrs_flat),
    "classes_count": len(classes_flat),
    "attributes": dict(sorted(attrs_flat.items(), key=lambda kv: int(kv[0]))),
    "classes": dict(sorted(classes_flat.items(), key=lambda kv: int(kv[0]))),
}
with open(r'D:\metasys-viewer\references\dictionary.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print()
print("Wrote dictionary.json")
