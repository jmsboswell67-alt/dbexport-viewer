"""Tighter parser for attribute IDs in the SCT Help PDF.

Two distinct table formats:

(A) Common Object Attributes (pages 53-58):
    Pattern: "<Name> -- <ViewGroup>" on one line, then "<ID> [W][C][D][R]" on next.
    The "-- " separator is the unique anchor.

(B) Factory Supplied Summary Definitions (pages 114-200+):
    Two-column table. PDF text-extract concatenates "<Name><ID>" with no
    space, OR "<Name> <ID>" with one space. We need to scan column-by-column.

    The pattern is: a line where the trailing token is a 2-6 digit integer,
    where the leading text is between 4-50 chars and looks like a friendly
    attribute name (Title-cased, no weird words).
"""
import re, json, collections
from pypdf import PdfReader

r = PdfReader(r'D:\metasys-viewer\references\SCTToolHelp.pdf')

results = {}   # pid -> name (first-seen wins; we count votes)
votes = collections.defaultdict(collections.Counter)

# -----------------------------------------------------------------------
# Strategy A — Common Object Attributes (pages 53-58)
# Format: line ending with "-- <Group>", next line starts with "<ID> [WCDR ]+"
# -----------------------------------------------------------------------
common_text = "\n".join(r.pages[i].extract_text() for i in range(52, 60))

# Look for "Name -- Group\nID" — but pypdf may have collapsed newlines.
# Inspect: the page rendered text has each attribute as its own block.
# Real pattern in the extracted text looks like:
#   "Description -- Object\n28 W C ..."
# OR sometimes the ID is on a SEPARATE line at start.
# We use a regex that finds "<Name> -- <Group>" followed by whitespace + ID + flags.

pat_a = re.compile(r'([A-Z][A-Za-z0-9 \-/\(\),]+?)\s+--\s+([A-Z][A-Za-z]+)\s+(\d{2,6})\s+([WCDR\s]+)', re.M)
for m in pat_a.finditer(common_text):
    name = m.group(1).strip()
    group = m.group(2)
    pid = m.group(3)
    if len(name) >= 4 and len(name) <= 60:
        votes[pid][name] += 3   # higher weight — this format is reliable

print(f"After Strategy A: {len(votes)} pids have candidate names")

# -----------------------------------------------------------------------
# Strategy B — Summary Definitions tables (pages 114-200)
# Look for: pages that contain "Attribute IDNumber" or "Default Column Headings"
# Within those pages, scan for "<Name> <ID>" lines where <Name> is plausible
# and <ID> is 2-6 digits.
# -----------------------------------------------------------------------
def is_plausible_attr_name(s):
    if not s or len(s) < 3 or len(s) > 60: return False
    if not s[0].isupper(): return False
    # Reject text that looks like prose
    bad_words = ('release', 'version', 'value', 'range', 'default', 'example',
                 'select', 'click', 'when', 'enter', 'specify', 'maximum', 'minimum',
                 'available', 'updated', 'displayed', 'limited', 'rangeis',
                 'starting at', 'thedefault', 'whenyou', 'youmust', 'thereare',
                 'page ', 'figure ', 'table ', 'note:', 'note ', 'example:',
                 'note', 'this attribute', 'this value', 'this is', 'this',
                 'use this', 'enables ', 'indicates ', 'represents ', 'contains ',
                 'controls ', 'specifies ', 'shows ', 'displays ', 'a maximum',
                 'a list', 'the value', 'the range', 'the default', 'the system',
                 'the user', 'the object', 'the device')
    s_low = s.lower()
    if any(b in s_low for b in bad_words): return False
    # Reject names that are mostly lowercase (suggests prose)
    upper_word_count = sum(1 for w in s.split() if w and w[0].isupper())
    word_count = len(s.split())
    if word_count > 1 and upper_word_count / word_count < 0.5: return False
    # Reject anything with punctuation other than space/hyphen/paren/slash
    if re.search(r'[^\w \-/\(\),]', s): return False
    return True

# Match patterns like "Engine 1Engine 2" or "BACnet IP Port1223"
# from pages 114+ where columns are concatenated.
# These should be all reliably from the Summary Definition tables.
for i in range(113, 250):
    if i >= len(r.pages): break
    page_text = r.pages[i].extract_text()
    # Only proceed if this looks like a summary def page
    if 'Attribute ID' not in page_text and 'Default Column' not in page_text:
        continue
    # Find sequences where attribute name is followed by ID
    # Try two patterns: with space and without
    for m in re.finditer(r'([A-Z][A-Za-z0-9 \-/\(\),]{3,55}?)\s*(\d{2,6})\b', page_text):
        raw_name = m.group(1).strip()
        pid = m.group(2)
        pid_i = int(pid)
        if pid_i < 10 or pid_i > 100000: continue
        # Clean trailing whitespace & strip "View Group" suffix indicators
        name = raw_name.rstrip(' -')
        if not is_plausible_attr_name(name): continue
        votes[pid][name] += 1

# Pick best name per id
for pid, name_counts in votes.items():
    best = sorted(name_counts.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[0][0]
    results[pid] = best

print(f"\nAfter both strategies: {len(results)} candidate attribute ID -> name pairs")
print("\n=== Sample (sorted by ID) ===")
for pid in sorted(results.keys(), key=int)[:60]:
    print(f"  {pid:>6}: {results[pid]}")

with open(r'D:\metasys-viewer\references\pdf_attributes_raw.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, sort_keys=True)
print("\nWrote pdf_attributes_raw.json")
