"""Extract the canonical Class ID table from the Metasys Object Help PDF
(pages 23-32, approximately). Each row in the original table is
"<Object Name>  <ID>" where the ID is a trailing integer.

We harvest into a dict, then merge with our existing dictionary.
"""
import re, json
from pypdf import PdfReader

r = PdfReader(r'D:\metasys-viewer\references\MetasysObjectHelp.pdf')
text = ""
# Read pages 23 through 32 (1-indexed), where the class table lives
for i in range(22, 35):
    text += "\n" + r.pages[i].extract_text()

# The table comes out as a stream where each "Name <ID>" pair is on its own line.
# But pypdf may concatenate. Let's tokenize by finding all "<text> <number>" patterns
# where the number is the last token before another capitalized word starts a new entry.

# Strategy: split on whitespace runs, walk tokens, build "name + id" entries.
# Numbers immediately following non-digits and followed by a capital letter delimit entries.

# Cleaner approach: regex for "<words> <digits or NA>" anchored by capitalization heuristics.
# Each line in PDF is one entry like:
#   "BACnet Analog Input 0"
#   "BACnet Analog Input Mapper 500"
# A simple regex: capture everything from start-of-line up to a trailing integer or "N/A"

entries = {}
for line in text.split("\n"):
    line = line.strip()
    if not line: continue
    # Match: "Name name name <int>" with optional whitespace, trailing integer is the ID
    # Allow "NA" too (some rows have no ID)
    m = re.match(r'^(.+?)\s+(\d+)\s*$', line)
    if not m: continue
    name = m.group(1).strip()
    cid = m.group(2)
    # Reject if name is too short or contains obvious non-name garbage
    if len(name) < 3: continue
    if name.lower().startswith('page '): continue
    if re.search(r'(figure|table|version)\b', name, re.I): continue
    # Reject if name has commas or weird structure that suggests it crossed entries
    if name.count(',') > 1: continue
    # Reject very long names (>80 chars probably means we caught multiple entries)
    if len(name) > 80: continue
    # Sometimes pypdf collapses multiple rows: "BACnet Analog Output 1N2 Analog Output 149"
    # In that case the "name" contains a number followed by more text. Split if so.
    # Look for "<digits><capital letter>" inside the name and split.
    parts = re.split(r'(\d+)(?=[A-Z])', name)
    if len(parts) > 1:
        # Re-assemble pairs: parts is [name0, id0, name1, id1, ..., nameN] where the trailing
        # is name and the trailing match-group provides id. Walk pairs.
        i = 0
        while i < len(parts) - 1:
            sub_name = parts[i].strip()
            sub_id = parts[i+1]
            if sub_name and len(sub_name) >= 3 and len(sub_name) <= 80:
                if sub_id not in entries: entries[sub_id] = sub_name
            i += 2
        # And the trailing name + outer cid
        last_name = parts[-1].strip()
        if last_name and len(last_name) >= 3:
            if cid not in entries:
                entries[cid] = last_name
    else:
        if cid not in entries:
            entries[cid] = name

# Filter results: keep only sensible class IDs (0 < id < 100000) and names that look like object types
filtered = {}
for cid, name in entries.items():
    icid = int(cid)
    if icid > 100000: continue
    # Strip any leading "Mapper"-like artifacts and trailing junk
    name = name.strip()
    # Skip names that are obviously not classes: pure digits, very short, "Page" header artifacts
    if name.lower() == 'page' or name.lower().startswith('page '): continue
    if name.startswith('Table '): continue
    if name == 'NA': continue
    filtered[cid] = name

print(f"Harvested {len(filtered)} class entries from PDF pages 23-35")
print()
print("Sample (first 40 sorted by ID):")
for cid in sorted(filtered.keys(), key=int)[:40]:
    print(f"  {cid:>5}: {filtered[cid]}")

# Save raw
with open(r'D:\metasys-viewer\references\pdf_classes_raw.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, sort_keys=True)
print()
print("Wrote pdf_classes_raw.json")
