"""Build a merged JS object literal from the harvested JCI dictionary,
combined with the existing hardcoded entries in index.html.

Outputs PROP_NAMES and CLASS_NAMES blocks that can be pasted into index.html.
"""

import json, re

with open(r'D:\metasys-viewer\references\dictionary.json', encoding='utf-8') as f:
    harvested = json.load(f)

def clean_class_name(s):
    s = re.sub(r'\s*-\s*Metasys release [\d.]+\s*$', '', s)
    s = re.sub(r'_CLASS$', '', s)
    s = re.sub(r'^NAE(\d+)$', r'NAE-\1 Engine', s)
    s = re.sub(r'^NCE(\d+)$', r'NCE-\1 Engine', s)
    s = re.sub(r'_SMARC$', ' (SMARC)', s)
    s = re.sub(r'_(\d+)L$', r'-\1L', s)
    # Hyphenate NAE35 -> NAE-35 etc. where bare
    s = re.sub(r'\b(NAE|NCE|NIE|SNE)(\d+)\b', r'\1-\2', s)
    return s

def js_escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

# === Class names: merge JCI harvested with existing hardcoded ===
# Existing hardcoded class names (from index.html, current state)
EXISTING_CLASSES = {
    0: "Analog Input", 1: "Analog Output", 2: "Analog Value", 3: "Binary Input",
    4: "Binary Output", 5: "Binary Value", 6: "Calendar", 8: "Device", 10: "File",
    11: "Group", 12: "Loop", 13: "Multistate Input", 14: "Multistate Output",
    15: "Notification Class", 17: "Schedule", 19: "Multistate Value", 20: "Trend Log",
    21: "Life Safety Point",
    129: "BACnet Protocol Eng", 135: "Subscription Server", 141: "Multistate Value (Metasys)",
    143: "AV/Calc", 146: "Programming", 147: "Analog Input (N2)", 148: "Analog Value (N2)",
    149: "Analog Input (N2)", 150: "Binary Value (N2)", 152: "Multistate (N2)",
    155: "Trend Log Extension", 156: "Alarm Extension", 165: "Analog Reference",
    168: "Logic Program", 172: "Alarm", 176: "Folder",
    192: "NAE-45 Engine", 194: "Trunk Configuration", 195: "Field Bus Trunk",
    196: "Engine State", 197: "Field Equipment Controller (FEC)",
    263: "Schedule", 264: "Calendar", 278: "N2 Device", 286: "Site Object",
    292: "Eth/IP DataLink", 336: "Logic Block", 337: "Logic Sub-block",
    338: "Logic Wire", 342: "Logic Parameter", 344: "Graphic",
    357: "Graphic Bindings", 425: "ADX Server", 448: "SNC Device (M4-SNC)",
    500: "BACnet AI (legacy class)", 502: "BACnet Analog Value", 503: "BACnet BI",
    505: "BACnet Binary Value", 508: "BACnet TEC Device", 519: "BACnet Schedule",
    599: "FEC Analog Value", 600: "FEC Binary Output", 601: "FEC Analog Input",
    602: "FEC Binary Input", 603: "FEC Binary Output", 604: "FEC Binary Value",
    605: "FEC Multistate Input", 606: "FEC Multistate Value",
    613: "NAE-35 Engine", 651: "NCE-25 Controller",
    699: "Summary Definition", 871: "SNE Controller (SNE-02)",
    872: "SNE Controller (SNE-01)",
    2000: "Archive Root", 2004: "Site Configuration", 2006: "Controller Templates",
    2011: "Summary Definitions",
}

# Merge: JCI harvested wins for conflicts, EXCEPT keep our friendlier names for items
# where ours is clearly more useful (point classes, schedules etc.)
KEEP_OURS = {197, 263, 344, 502, 505, 508, 599, 600, 601, 602, 603, 604, 605, 606}

merged_classes = dict(EXISTING_CLASSES)
for cid_str, name in harvested['classes'].items():
    cid = int(cid_str)
    cleaned = clean_class_name(name)
    if cid in merged_classes and cid in KEEP_OURS:
        continue  # ours is friendlier
    # JCI's wins, but log if changing
    merged_classes[cid] = cleaned

# Fix the 871/872 swap (JCI dictionary says these are NAE-45/NAE-35 SMARC, not SNE)
# The user's archive had them as "SNE" but the class itself is named NAE_SMARC.
# Trust JCI's class name.

# === Attribute names: JCI harvested wins ===
EXISTING_PROPS = {
    12: "Comment", 28: "Description", 44: "Internet Address", 58: "Vendor Identifier",
    70: "Model Name", 75: "Object Identifier", 77: "Object Name", 79: "Object Type",
    85: "Present Value", 103: "Units", 104: "Update Interval", 111: "Status Flags",
    116: "Notification Class", 117: "Time Delay", 118: "Notify Type",
    119: "Event Enable", 121: "Recipient List", 130: "Event State", 131: "Reliability",
    168: "Polarity", 196: "Reliability", 202: "Active COV Subscriptions",
    203: "Local Date / Time", 206: "Restart Notification Recipients",
    225: "Number Of Trend Records", 226: "Trend Log Records", 549: "Stop When Full",
    650: "Item Reference", 654: "Display Precision", 849: "Archive Date",
    850: "Archive Time", 1601: "Use Local Time",
    32521: "Archive Identifier", 32522: "Contract Number", 32523: "Created By",
    32524: "Software Version", 32527: "Archive Name",
}

# JCI's harvested attribute names are authoritative — replace ours where they differ.
# Specifically:
#   id=44  ours='Internet Address', JCI='Firmware Version' — JCI wins, we were wrong
#   id=103 ours='Units', JCI='Reliability' — JCI wins, we were wrong (103 is BACnet Reliability)
#   id=104 ours='Update Interval', JCI='Relinquish Default' — JCI wins
#   id=196 ours='Reliability', JCI='Last Restart Reason' — JCI wins
#   id=117 ours='Time Delay', JCI='Units' — JCI wins
# These corrections are valuable on their own.
merged_attrs = {}
for aid_str, name in harvested['attributes'].items():
    aid = int(aid_str)
    merged_attrs[aid] = name
# Add any of our entries that aren't in the harvest
for aid, name in EXISTING_PROPS.items():
    if aid not in merged_attrs:
        merged_attrs[aid] = name

print(f"Final: {len(merged_attrs)} attribute names, {len(merged_classes)} class names")

# Output as JS object literal
def js_block(d, name):
    lines = [f"const {name} = {{"]
    for k in sorted(d.keys()):
        v = d[k]
        lines.append(f'  {k}: "{js_escape(str(v))}",')
    lines.append("};")
    return '\n'.join(lines)

js = "// =================================================================\n"
js += "// CLASS_NAMES and PROP_NAMES — interop reference data\n"
js += "// Sourced from JCI Metasys 14.0.0.43 public Launcher resource bundle\n"
js += "// (factual ID->name mappings, extracted from XML comments in commands.xml,\n"
js += "// AttributeSetList.xml, globalModifyList.xml). Facts, not creative expression.\n"
js += "// =================================================================\n\n"
js += js_block(merged_classes, "CLASS_NAMES")
js += "\n\n"
js += js_block(merged_attrs, "PROP_NAMES")

with open(r'D:\metasys-viewer\references\dict_js_block.js', 'w', encoding='utf-8') as f:
    f.write(js)
print()
print("Wrote dict_js_block.js — paste into index.html")
print()
# Print first ~30 lines for visual check
print(js.split('\n')[0:30].__repr__().replace('\\n', '\n'))
