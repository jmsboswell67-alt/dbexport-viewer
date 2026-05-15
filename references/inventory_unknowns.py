"""Walk every .dbexport in the JCI folder. For every class/property ID we
encounter, count occurrences and collect example references + descriptions.
Compare against the dictionary baked into index.html and report what's missing.

Output: references/unknowns_report.md  (human-readable, can scan for new entries)
        references/unknowns_inventory.json  (machine-readable for follow-up)
"""

import zipfile, re, collections, os, glob, json, base64, gzip
from io import BytesIO

# ----- pull current dictionary out of index.html -----
HTML = open(r'D:\metasys-viewer\index.html', encoding='utf-8').read()

def parse_js_dict(name):
    m = re.search(r'const ' + name + r' = \{([\s\S]*?)\};', HTML)
    if not m: return {}
    body = m.group(1)
    out = {}
    for k, v in re.findall(r'(\d+):\s*"((?:[^"\\]|\\.)*)"', body):
        out[k] = v
    return out

CLASS_NAMES = parse_js_dict('CLASS_NAMES')
PROP_NAMES = parse_js_dict('PROP_NAMES')
print(f"Loaded dictionary: {len(CLASS_NAMES)} class names, {len(PROP_NAMES)} property names")

# ----- walk archives -----
JCI_DIR = r'C:\Users\jmsbo\Desktop\jci'
archives = sorted(glob.glob(os.path.join(JCI_DIR, '*.dbexport')))
print(f"Found {len(archives)} archives to inventory")

ns_strip = re.compile(r'^\{[^}]+\}')
class_counts = collections.Counter()
class_examples = collections.defaultdict(list)   # cid -> [(archive, ref, description)]
prop_counts = collections.Counter()
prop_examples = collections.defaultdict(list)    # pid -> [(archive, classid_of_owner, description_of_owner)]

# Limit examples per id (just enough to recognize the pattern)
MAX_EXAMPLES = 5

def iter_objects(xml_text):
    """Yield (ref, classid, props_dict) for each <object> in this XML.
    Use regex instead of an XML parser for speed — XML can be large."""
    obj_re = re.compile(r'<object\s+([^>]*?)>(.*?)</object>', re.S)
    attr_re = re.compile(r'(\w+)="([^"]*)"')
    prop_re = re.compile(r'<property\s+id="(\d+)">(.*?)</property>', re.S)
    desc_re = re.compile(r'<property\s+id="28">\s*<data>\s*<string>([^<]*)</string>', re.S)
    for m in obj_re.finditer(xml_text):
        attrs = dict(attr_re.findall(m.group(1)))
        body = m.group(2)
        ref = attrs.get('ref', '')
        cid = attrs.get('classid', '')
        prop_ids = prop_re.findall(body)
        prop_id_set = {p[0] for p in prop_ids}
        dm = desc_re.search(body)
        desc = dm.group(1) if dm else ''
        yield ref, cid, prop_id_set, desc

processed = 0
for arc_path in archives:
    if os.path.getsize(arc_path) == 0:
        continue
    name = os.path.basename(arc_path)
    print(f"  scanning {name} ({os.path.getsize(arc_path)/1024/1024:.0f} MB)")
    try:
        with zipfile.ZipFile(arc_path) as z:
            for info in z.infolist():
                if not info.filename.lower().endswith('.xml'):
                    continue
                # Read and decode
                with z.open(info) as f:
                    raw = f.read()
                try:
                    text = raw.decode('utf-8')
                except UnicodeDecodeError:
                    text = raw.decode('utf-8', errors='replace')
                # If the file is Base64Zip-wrapped, decompress it first
                if '<Base64Zip' in text:
                    b64m = re.search(r'<Base64Zip[^>]*>([\s\S]*?)</Base64Zip>', text)
                    if b64m:
                        try:
                            inner_bytes = base64.b64decode(b64m.group(1).strip())
                            text = gzip.decompress(inner_bytes).decode('utf-8', errors='replace')
                        except Exception:
                            pass  # leave wrapped
                # Walk objects
                for ref, cid, prop_id_set, desc in iter_objects(text):
                    if not cid: continue
                    class_counts[cid] += 1
                    if len(class_examples[cid]) < MAX_EXAMPLES:
                        class_examples[cid].append((name, ref[:80], desc[:80]))
                    for pid in prop_id_set:
                        prop_counts[pid] += 1
                        if len(prop_examples[pid]) < MAX_EXAMPLES:
                            prop_examples[pid].append((name, cid, desc[:60]))
    except zipfile.BadZipFile:
        print(f"    SKIP: bad zip")
        continue
    processed += 1
print(f"Processed {processed} archives. Found {len(class_counts)} distinct class IDs, {len(prop_counts)} distinct property IDs.")

# Compute unknowns
missing_classes = [(c, n) for c, n in class_counts.most_common() if c not in CLASS_NAMES]
missing_props   = [(p, n) for p, n in prop_counts.most_common() if p not in PROP_NAMES]
print(f"Missing from dictionary: {len(missing_classes)} class IDs, {len(missing_props)} property IDs")

# Save report
out_md = [f"# Unknown class/property IDs across {processed} archives\n",
          f"Dictionary baseline: {len(CLASS_NAMES)} classes, {len(PROP_NAMES)} properties.\n",
          f"After this scan: {len(class_counts)} class IDs and {len(prop_counts)} property IDs seen in the wild.\n",
          f"**Unknown**: {len(missing_classes)} classes, {len(missing_props)} properties.\n",
          "\n## Unknown class IDs (ranked by frequency)\n"]
for cid, n in missing_classes[:80]:
    out_md.append(f"\n### `cid={cid}`  ({n:,} objects)\n")
    examples = class_examples[cid]
    descs = sorted(set(e[2] for e in examples if e[2]))
    refs = sorted(set(e[1] for e in examples if e[1]))
    if descs:
        out_md.append(f"Descriptions: {', '.join(repr(d) for d in descs[:3])}\n")
    if refs:
        out_md.append("Example refs:\n")
        for r in refs[:3]:
            out_md.append(f"- `{r}`\n")

out_md.append("\n## Unknown property IDs (ranked by frequency)\n")
for pid, n in missing_props[:120]:
    out_md.append(f"\n### `prop={pid}`  ({n:,} occurrences)\n")
    examples = prop_examples[pid]
    owner_classes = collections.Counter(e[1] for e in examples)
    descs = sorted(set(e[2] for e in examples if e[2]))
    if owner_classes:
        items = ', '.join(f"cid {c} ({CLASS_NAMES.get(c, '?')})" for c, _ in owner_classes.most_common(3))
        out_md.append(f"Owner classes: {items}\n")
    if descs:
        out_md.append(f"On objects with descriptions: {', '.join(repr(d) for d in descs[:3])}\n")

with open(r'D:\metasys-viewer\references\unknowns_report.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_md))

# JSON for follow-up
with open(r'D:\metasys-viewer\references\unknowns_inventory.json', 'w', encoding='utf-8') as f:
    json.dump({
        'archives_processed': processed,
        'class_counts': dict(class_counts.most_common()),
        'prop_counts': dict(prop_counts.most_common()),
        'missing_classes': [{'id': c, 'count': n, 'examples': class_examples[c]} for c, n in missing_classes],
        'missing_props': [{'id': p, 'count': n, 'examples': prop_examples[p]} for p, n in missing_props],
    }, f, indent=2, default=str)
print("Wrote unknowns_report.md and unknowns_inventory.json")
