# dbexport-viewer

**Read, audit, diff, and bulk-fix Metasys SCT archives without SCT, CCT, PCT, or a JCI service visit.**

**▶ [Try it now — live demo](https://jmsboswell67-alt.github.io/dbexport-viewer/)**

A single-file, offline, browser-based viewer for Johnson Controls Metasys
`.dbexport` archives and `.caf` controller files. Open a file you already have,
get the information SCT would charge a service call for.

The live demo above runs the latest `main` directly in your browser. Your files
are parsed locally — nothing is uploaded. Want to run offline? Download
`index.html` from this repo and open it directly.

> ⚠️ Not affiliated with, endorsed by, or supported by Johnson Controls.
> "Metasys", "SCT", "CCT", "ADX", "NAE", "NCE", "SNE", and "FEC" are trademarks
> of Johnson Controls, used here only for descriptive interoperability reference.

---

## What it does

**Browse + extract:**
- **Read `.dbexport` archives** — full hierarchical browse: Site → Engine → Trunk → Equipment → Points, with class labels, property names, and full object detail.
- **Read `.caf` files** — the controller logic files CCT writes. Tells you the controller model, firmware version, and every configured object. Answers ["Is there any way to open up a .caf file without a service tech?"](https://www.reddit.com/r/BuildingAutomation/) (real 2022 forum thread, accepted answer was "you can't") — now you can.
- **Reverse lookup** — click any point, see every graphic, program, schedule, and user tree that references it. Pre-deletion gut check ("if I remove this, what breaks?"), commissioning audit ("what does this sensor actually drive?"), cascade tracing.
- **Export to CSV / JSON / vendor-neutral point list** — scoped to whatever you've selected. Points, schedules, alarms, trends, or everything. Open in Excel, share with consultants, feed into your own tools. The vendor-neutral export strips JCI-specific property IDs in favor of clean columns any other BMS can ingest.

**Diff + compare:**
- **Same-site diff** — two snapshots of the same site, see what changed between them at object and property level. No SCT equivalent.
- **Cross-site comparison** — drop archives from two different sites, get a structural comparison: controller counts, point counts, class distributions, average objects per controller. Auto-detects when archives look like different sites and warns that ref-based diff isn't the right tool.

**Find + fix:**
- **Native unbound-references scanner** — drop a `.dbexport` alone (no SCT-exported CSV needed). The tool walks every XML in the zip plus every `Base64Zip`-wrapped logic/graphics payload, finds every ref-shaped string whose target isn't defined, and produces the same row shape as SCT's unbound-refs report. Calibrated against SCT ground truth at ~88% recall, with confidence pills showing whether rewrites land on real objects.
- **One-click bulk repoint** — when the unbound refs follow a clear rename pattern (e.g. `DACC-ADX-01:` → `DACC-ADX-02:`), the tool generates a corrected `.dbexport` you can import directly via SCT's Restore Archive. Decodes the Base64Zip-wrapped User Trees, Graphics, and Programming logic that SCT makes you fix one row at a time. Verified: 5,641 broken refs fixed in one click on a real DACC archive.
- **Delete-to-archive** — bulk, per-row, or multi-select via checkboxes. Removes selected items (graphics, programs, user trees) from a copy of the archive and emits a valid `.dbexport`. Categorized confirm dialog before any destructive action.

**Audit findings:**
- **Suppressed alarms** — every object where Event Enable has at least one transition disabled. Grouped by class. DACC test: 640 findings. CSV export.
- **Duplicate descriptions** — objects sharing a Description across multiple refs. Distinguishes within-engine (often intentional) from cross-engine (more suspicious copy-paste artifacts). DACC test: 558 groups, 222 cross-engine.
- **Orphaned graphics** — graphics files that nothing in the archive references. Builds on the reverse-lookup index. Cleanup candidates.

**Documentation:**
- **As-Built Documentation generator** — produces a printable HTML document covering cover page, site topology, full device inventory, point list per controller, schedules, alarm definitions with suppression flags, and any audit findings you've run. Open in a new tab, print to PDF. Replaces the commissioning consultant deliverable on many sites.

## Why it exists

SCT and the JCI Launcher are gated behind dealer agreements, service contracts,
and version-matched license keys. For everyone *else* who has a `.dbexport`
file — facility owners, consultants doing audits, contractors taking over
sites, anyone who needs to see what's in a Metasys backup — there has been
no answer until now.

This tool **never** talks to a live ADX, never pushes config to a device, never
needs the JCI Launcher, and works entirely in your browser. Your files are
parsed locally and never leave your machine.

## Quick start

**Easiest:** click the [live demo](https://jmsboswell67-alt.github.io/dbexport-viewer/) and drop a `.dbexport`, `.caf`, or unbound-references `.csv` onto the page. Done.

**Offline / self-hosted:**

1. Download `index.html` from this repo (or clone and open it).
2. Open it in any modern browser (Chrome, Edge, Firefox, Safari).
3. Drag a `.dbexport`, `.caf`, or unbound-references `.csv` onto the page.

No install, no signup, no internet required after download. Your files never leave your machine in either mode.

**Typical workflows:**
- **"What's in this archive?"** — drop the file, browse the tree. Click any object for full property detail and reverse-lookup of what references it.
- **"Fix unbound references"** — drop the archive, switch to the Unbound Refs tab, click "Scan now". Review the patterns. Click "Apply to archive" on any rename pattern with high confidence.
- **"Audit the site"** — drop the archive, switch to the Audit tab. Browse the suppressed-alarm and duplicate-description findings. Export CSVs.
- **"Diff two backups"** — drop two `.dbexport` files. Auto-detects same-site (use Diff mode) vs. different-site (auto-promotes structural comparison panel).
- **"Generate as-built docs"** — drop the archive, optionally run an Audit first, then Export ▾ → As-Built Documentation. New tab opens, hit Print, save as PDF.

## What it can't do

- It does **not** talk to live engines. No BACnet/IP polling, no Metasys REST API client. Read-only against files you already have.
- It does **not** simulate runtime behavior — yet. See [SIMULATOR.md](SIMULATOR.md) for the long-range plan toward an editable sandbox + control-logic emulator.
- It does **not** edit logic wiring or create new objects. Delete-to-archive removes whole files (graphics, programs, user trees); repoint substitutes ADX prefixes. The viewer doesn't add new objects or rewire programming.
- It does **not** carry the full JCI runtime dictionary. The 206+ attribute names and 124+ class names baked in come from publicly-distributed JCI Launcher resource files. The remaining ~10% of IDs (usually CCT-specific logic-block classes or runtime-only attributes) appear as `Property N` or `Class N`. **Contributions to expand the dictionary are very welcome** — see [Contributing](#contributing).
- It does **not** render Metasys graphics or CCT logic wiring diagrams (yet). Graphics and Programming `.xml` files use a proprietary Tom Sawyer Graph format. The parser is shipped (`parseTSEGraph`) and basic rendering exists in the Logic mode, but full point-binding-aware rendering is on the roadmap.

## How it works (interop reference data)

The viewer's property/class dictionaries (`PROP_NAMES` and `CLASS_NAMES` in
`index.html`) are factual ID → name mappings extracted from XML *comments* in
JCI's publicly-distributed Launcher resource bundle:

- `commands.xml` — class IDs with command associations
- `globalModifyList.xml` — per-class attribute lists
- `AttributeSetList.xml` + `AttributeSetListSCT.xml` — attribute summary definitions

These are facts (numeric ID, canonical name), not creative expression. Per
**Feist v. Rural** (US), **Software Directive Art. 6** (EU), and the Sega /
Sony / Connectix line of interop-reverse-engineering cases, factual extraction
for interoperability is permitted.

The original JCI Launcher resource files are **not** redistributed by this
project. Only the extracted ID → name table is included.

## What's in the box

```
index.html        — the entire app, single file, ~350 KB (JSZip inlined)
LICENSE           — Apache License 2.0
PUNCHLIST.md      — feature roadmap + session-by-session changelog
SIMULATOR.md      — long-range roadmap toward a BAS sandbox
README.md         — this file
.github/ISSUE_TEMPLATE/  — structured templates for bugs, unknown IDs,
                          dictionary contributions, sample archives
```

## Roadmap

Near-term feature list lives in [PUNCHLIST.md](PUNCHLIST.md). Long-range
vision (controls + BACnet sandbox, "Packet Tracer for BAS") is in
[SIMULATOR.md](SIMULATOR.md). Active near-term areas:

- Full TSEGraph graphics rendering with point-binding overlays
- Schedule weekly-calendar visualizer in the as-built docs
- Modification-timestamp harvesting for same-site drift detection
- Pre-export static validator (Phase 1 of the simulator roadmap)

## Contributing

This is a side project, maintained when the maintainer has free cycles. The
issue templates make it easy to file useful feedback even without writing
code.

Most useful contributions, in rough priority order:

1. **Live engine enum captures** — if you have access to an ADX, one curl
   against the Metasys REST API (`GET /api/v6/schemas/enums/...`) for
   `reliabilityEnumSet`, `unitEnumSet`, `objectCategoryEnumSet`, etc., would
   close the largest remaining dictionary gap. See the `enum-capture.yml`
   issue template.
2. **Unknown property/class IDs** — if your archive shows `Property N` or
   `Class N`, look it up in your own JCI documentation and file under the
   `unknown-id.yml` issue template (or PR directly).
3. **CCT logic block class names** — the ~30 CCT-specific block classes
   (526, 528, 555, 556, 561, 568, 658-660, etc.) need authoritative names.
   `cct-class-names.yml` template tracks the open list.
4. **`.dbexport` samples with unusual content** — non-DACC site structures,
   older firmware versions, weird edge cases. The `sample-archive.yml`
   template describes what to share (and what NOT to — never include
   live engine state or anything covered by site-confidentiality clauses).
5. **Cross-vendor analogues** — the basic architecture (zipped XML → tree
   → diff/export) maps to other BAS vendors' export formats. If you want
   to add Tridium Niagara, Siemens Desigo, Honeywell EBI, open an issue.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

The Apache 2.0 license includes an explicit patent grant. Useful here because
BAS protocols touch various patents and we want contributors and users covered.

## Acknowledgments

- The 2022 [r/BuildingAutomation forum thread](https://www.reddit.com/r/BuildingAutomation/) where someone asked "Is there any way to open up a .caf file without a service tech?" and got told "no." This project is the "yes" that didn't exist then.
- Every facility manager who's hand-fixed thousands of unbound references in SCT, one click at a time, wondering why there isn't a better way. There is now.
