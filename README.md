# dbexport-viewer

**Read, diff, and bulk-fix Metasys SCT archives without SCT, CCT, PCT, or a JCI service visit.**

A single-file, offline, browser-based viewer for Johnson Controls Metasys
`.dbexport` archives and `.caf` controller files. Open a file you already have,
get the information SCT would charge a service call for.

> ⚠️ Not affiliated with, endorsed by, or supported by Johnson Controls.
> "Metasys", "SCT", "CCT", "ADX", "NAE", "NCE", "SNE", and "FEC" are trademarks
> of Johnson Controls, used here only for descriptive interoperability reference.

---

## What it does

- **Read `.dbexport` archives** — full hierarchical browse: Site → Engine → Trunk → Equipment → Points, with class labels, property names, and full object detail.
- **Read `.caf` files** — the controller logic files CCT writes. Tells you the controller model, firmware version, and every configured object. Answers ["Is there any way to open up a .caf file without a service tech?"](https://github.com/jmsboswell67-alt/dbexport-viewer/issues) (real 2022 forum thread, 2.3K views, accepted answer was "you can't") — now you can.
- **Diff two snapshots** — see what changed between archive backups at object-level and property-level. SCT has no equivalent.
- **Export to CSV / JSON** — scoped to whatever you've selected. Points, schedules, alarms, trends, or everything. Open in Excel, share with consultants, feed into your own tools.
- **Fix unbound references in bulk** — drop the `UnboundReferences.csv` SCT generates, get pattern detection (e.g. "6,348 refs point to a renamed ADX"), then **click one button to produce a fixed `.dbexport`** with the dead references repointed. Decodes the `Base64Zip`-wrapped User Trees, Graphics, and Programming logic that SCT makes you fix one row at a time.

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

1. Download `index.html` from this repo (or clone and open it).
2. Open it in any modern browser (Chrome, Edge, Firefox, Safari).
3. Drag a `.dbexport`, `.caf`, or unbound-references `.csv` onto the page.

That's it. No install, no signup, no internet required after download.

For diff mode, drop two `.dbexport` files into the two slots. For the bulk
unbound-references fixer, drop your archive into slot A and the unbound
references CSV into slot B, then switch to the "Unbound Refs" tab.

## What it can't do

- It does **not** talk to live engines. No BACnet/IP polling, no Metasys REST API client. Read-only against files you already have.
- It does **not** edit object structure or control logic. The "Apply repoint" feature only does prefix substitution on existing references; it doesn't create, delete, or rewire objects.
- It does **not** carry the full JCI runtime dictionary. The 206 attribute names and 104 class names baked in come from publicly-distributed JCI Launcher resource files. The remaining ~10% of IDs (usually CCT-specific logic-block classes or runtime-only attributes) appear as `Property N` or `Class N`. Contributions to expand the dictionary welcome.
- It does **not** render Metasys graphics or CCT logic wiring diagrams (yet). Graphics and Programming `.xml` files use a proprietary Tom Sawyer Graph format that we haven't tackled.

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
index.html        — the entire app, single file, ~210 KB (JSZip inlined)
LICENSE           — Apache License 2.0
PUNCHLIST.md      — feature roadmap + session-by-session changelog
README.md         — this file
```

## Roadmap

See [PUNCHLIST.md](PUNCHLIST.md) for the full feature roadmap. Active areas:

- Graphics viewer (XAML + older TSEGraph formats)
- Programming/logic-block viewer
- Schedule weekly-calendar visualizer
- Energy-waste heuristics (24/7 schedules, stuck overrides, suppressed alarms)
- Cross-vendor: same approach for Tridium Niagara, Siemens Desigo, Honeywell EBI

## Contributing

This is a side project, maintained when the maintainer has free cycles.

The most useful contributions, in rough priority order:
1. **Dictionary additions** — if your archive shows `Property N` or `Class N`, look it up in your own JCI documentation and PR the entry into `index.html`.
2. **`.dbexport` samples with unusual content** — non-DACC site structures, older firmware versions, weird edge cases. Open an issue describing what's not parsing right.
3. **Cross-vendor analogues** — the basic architecture (zipped XML → tree → diff/export) maps to other BAS vendors' export formats. Open an issue if you want to add Tridium Niagara, Siemens Desigo, etc.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

The Apache 2.0 license includes an explicit patent grant. Useful here because
BAS protocols touch various patents and we want contributors and users covered.

## Acknowledgments

- The 2022 [r/BuildingAutomation forum thread](https://www.reddit.com/r/BuildingAutomation/) where someone asked "Is there any way to open up a .caf file without a service tech?" and got told "no." This project is the "yes" that didn't exist then.
- Every facility manager who's hand-fixed thousands of unbound references in SCT, one click at a time, wondering why there isn't a better way. There is now.
