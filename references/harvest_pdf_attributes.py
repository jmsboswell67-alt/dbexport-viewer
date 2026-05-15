"""Harvest attribute (property) name -> ID mappings from the SCT Tool Help PDF.

Two strong source areas:
  - Pages 53-56: Common Object Attributes table (Name, Attribute ID, W/C, Description)
  - Pages 114-200: Factory Supplied SCT Summary Definitions (column headings + Attribute IDs)

The format consistently has "<attribute name>" followed by "<integer ID>" on
adjacent positions. The trick is filtering out noise (page numbers, version
strings, other random number occurrences).

Strategy: only accept rows where the attribute name LOOKS like an attribute
name (begins with capital, contains words separated by space/hyphen/paren)
AND the ID is in a plausible range (1-100000).
"""
import re, json, collections
from pypdf import PdfReader

r = PdfReader(r'D:\metasys-viewer\references\SCTToolHelp.pdf')

# Concatenate pages of likely-relevant areas
target_pages = list(range(52, 60)) + list(range(113, 250))   # 0-indexed
text_parts = []
for i in target_pages:
    if i < len(r.pages):
        text_parts.append(r.pages[i].extract_text())
text = "\n".join(text_parts)

# Find "<name> <ID>" tuples. We use a flexible pattern: name with optional dashes/parens,
# followed by whitespace, followed by a numeric ID (2-6 digits).
# We allow the name to span multiple words.
pat = re.compile(r'([A-Z][A-Za-z0-9 \-/\(\),]{2,60}?)\s+(\d{2,6})\b')

candidates = collections.Counter()
examples = collections.defaultdict(list)
for m in pat.finditer(text):
    name = m.group(1).strip()
    pid = m.group(2)
    # Filter noise
    if name.lower().startswith(('page', 'figure', 'table')): continue
    if name.lower() in ('release', 'version', 'note', 'example', 'description'): continue
    if 'release ' in name.lower(): continue
    if re.search(r'\bversion\b', name.lower()): continue
    if len(name) < 4: continue
    if name.isdigit(): continue
    # ID must be plausible
    pid_i = int(pid)
    if pid_i < 2 or pid_i > 100000: continue
    # Strip trailing artifacts (page numbers etc.)
    candidates[(name, pid)] += 1
    if len(examples[pid]) < 3:
        examples[pid].append(name)

# Build pid -> best-name dict
# Pick the most-frequent name for each ID; ties broken by alphabetical
by_id = {}
votes = collections.defaultdict(collections.Counter)
for (name, pid), count in candidates.items():
    votes[pid][name] += count

for pid, name_counts in votes.items():
    # Pick best: most votes, then shortest, then alphabetical
    best = sorted(name_counts.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[0][0]
    by_id[pid] = best

print(f"Harvested {len(by_id)} attribute ID -> name candidates")
print()
print("Sample (sorted by ID):")
for pid in sorted(by_id.keys(), key=int)[:50]:
    print(f"  {pid:>6}: {by_id[pid]}")

# Save
with open(r'D:\metasys-viewer\references\pdf_attributes_raw.json', 'w', encoding='utf-8') as f:
    json.dump(by_id, f, indent=2, sort_keys=True)
print()
print("Wrote pdf_attributes_raw.json")
