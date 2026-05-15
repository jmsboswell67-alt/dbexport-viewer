"""Harvest class-ID and command-userId mappings from commands.xml.

The file uses XML comments to label each id; we extract them as a dictionary.

Pattern:
    <!-- Trend Log -->
    <class id="155" version="1.0" />
    <!-- Enable -->
    <command userId="11" access="5" />

Output: classes.json, commands.json
"""

import re, json, collections

with open(r'D:\metasys-viewer\references\extracted\14.0.0.43\ui_fw\com\jci\domain\globalcommand\commands.xml', encoding='utf-8') as f:
    text = f.read()

# Strip block comment at top (the "Notes:" multi-line one) so it doesn't grab its title
# We process line-by-line: track the most recent comment, then attach to the next class or command
classes = {}   # id -> name (first one wins, but log conflicts)
commands = {}  # userId -> name

last_comment = None
for line in text.splitlines():
    line_strip = line.strip()
    # Skip empty
    if not line_strip:
        last_comment = None
        continue
    # Match XML comment line
    m = re.match(r'<!--\s*(.*?)\s*-->', line_strip)
    if m:
        text_inside = m.group(1).strip()
        # Ignore multi-line note headers ("Notes:", "Range checking ...", etc.)
        if text_inside.startswith('Notes:') or 'Range checking' in text_inside or text_inside.startswith('*') or 'unitsId=' in text_inside:
            last_comment = None
        else:
            last_comment = text_inside
        continue
    # Match <class id="N"
    mc = re.search(r'<class\s+id="(\d+)"', line_strip)
    if mc and last_comment:
        cid = mc.group(1)
        if cid not in classes:
            classes[cid] = last_comment
        last_comment = None
        continue
    # Match <command userId="N"
    mu = re.search(r'<command\s+userId="(\d+)"', line_strip)
    if mu and last_comment:
        uid = mu.group(1)
        if uid not in commands:
            commands[uid] = last_comment
        last_comment = None
        continue
    # If line isn't a comment or matchable element, reset
    if '<' in line_strip and '-->' not in line_strip:
        last_comment = None

print(f"Harvested {len(classes)} class IDs and {len(commands)} command/userIds")
print()
print("Sample class IDs:")
for cid in sorted(classes.keys(), key=int)[:30]:
    print(f"  {cid:>5}: {classes[cid]}")
print()
print("Sample command userIds (first 30):")
for uid in sorted(commands.keys(), key=int)[:30]:
    print(f"  {uid:>5}: {commands[uid]}")

# Save as JSON
out = {
    "_source": "JCI Metasys-14.0.0.43 commands.xml (extracted comments only — interop reference data)",
    "_harvested_at": __import__('datetime').datetime.now().isoformat(timespec='seconds'),
    "classes": dict(sorted(classes.items(), key=lambda kv: int(kv[0]))),
    "commands": dict(sorted(commands.items(), key=lambda kv: int(kv[0]))),
}
with open(r'D:\metasys-viewer\references\dictionary_from_commands.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print()
print("Wrote dictionary_from_commands.json")
