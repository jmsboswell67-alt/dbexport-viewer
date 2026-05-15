# Metasys Archive Viewer — Punch List

Living roadmap. Update at end of each session.

## Done

### v0.1 — Initial prototype (2026-05-14)
- [x] Single-file HTML at `index.html` (no build step, JSZip from CDN)
- [x] Drag-drop two `.dbexport` slots (A and B)
- [x] Parse archive: `archiveobject.xml`, `navtree.xml`, per-device `archive.xml`
- [x] Decode common property value types (string, int, real, date, time, enum, listof, struct, BACoid)
- [x] Class-ID → friendly name map for ~50 common Metasys/BACnet classids
- [x] Property-ID → friendly name map for ~30 common property IDs
- [x] Browse mode: flat object list per device, filterable by class + search
- [x] Object detail view with all properties decoded
- [x] Diff mode: object-level (added/removed) + property-level (changed) across two archives
- [x] Diff summary pills, per-device diff filter, search filter
- [x] Verified end-to-end against real DACC archives: 12,271 objs, 17 devices, 10 removed / 17 changed across snapshots

## Next

### v0.2 — Hierarchical tree (2026-05-14) ✅
- [x] Ref parser: split refs into segments
- [x] Build tree data structure grouping by SMP categories within each engine
- [x] Render tree as collapsible nodes with counts + chevrons + kind icons
- [x] Click engine → engine summary + immediate children table
- [x] Click Field Bus → equipment children listed (FECs, BACnet sub-bus)
- [x] Click equipment → points table
- [x] Click point → full object detail with all properties
- [x] Click trend log child of a point → drills into trend log
- [x] Breadcrumb navigation working (Engine / FC-1 / FEC-3 / OA-T / Trend1)
- [x] Class-filter and search filter on intermediate-node tables
- [x] Diff mode still works (0/10/17/12,244 unchanged after refactor)
- [x] Semantic kind classification by classid (FEC=equipment, schedule=schedule, graphic=graphic, trendlog, alarm, etc.) — preserves segment-level kinds (fieldbus, schedules)
- [x] Verified end-to-end with real DACC archives

Note: diff mode tree is still flat (device-list). Diff *content* shows hierarchical refs, so this is acceptable for now — revisit if user feedback requests it.

### v0.3.5 — JCI dictionary harvest (2026-05-14) ✅
- [x] Extracted public Launcher resource bundles: `Metasys-14.0.0.43.zip`, `Metasys-13.0.3.2.zip`, `Metasys-13.0.2.2.zip`, `Metasys-13.0.0.240.zip`, `Metasys-10.4.0.1601.zip`
- [x] Cross-version union: 13.x are essentially identical; 10.4 added 1 class; 14.0 is the master set. Dictionary is stable across versions.
- [x] Identified dictionary sources inside JCIUIFramework.jar:
  - `commands.xml` — class IDs with command associations
  - `globalModifyList.xml` — per-class attribute lists
  - `AttributeSetList.xml` + `AttributeSetListSCT.xml` — attribute summary definitions
- [x] Built harvester (`references/harvest_full.py`) that parses XML comments → ID/name pairs
- [x] Built merger (`references/build_js_dict.py`) that combines JCI harvest with our hardcoded fallbacks
- [x] Baked into `index.html`: now **206 property names + 104 class names** (up from 30/80)
- [x] Corrected several wrong guesses:
  - 196: "Reliability" → "Last Restart Reason" (Reliability is actually 103)
  - 117: "Time Delay" → "Units"
  - 871/872: "SNE Controller" → "NAE-45/NAE-35 (SMARC)" (the underlying class is the NAE on SMARC hardware; "SNE" was a customer naming convention)
- [x] Verified: OA-T point detail now shows Description, Event Enable, Object Identifier, Units, Object Category, User Name with correct labels
- [x] Documented in code comments: facts are not copyrighted (Feist v. Rural); original JCI files NOT redistributed; only the factual ID→name mappings extracted

Reference files kept in `references/` (gitignored — never redistribute):
- `Metasys-*.zip` (originals from JCI public download — 5 versions)
- `extracted/` (unpacked JARs, for re-running harvest)
- `dictionary.json` (machine-readable cross-version harvest output)
- `dict_js_block.js` (paste-ready JS object literal)
- `harvest_full.py`, `harvest_multi.py`, `build_js_dict.py` (re-runnable harvesters)
- `dump_strings.py` (utility for inspecting .class file constants)

### Gaps in the harvest (deferred — not worth pursuing now)

- **Enum set definitions** (e.g. when our viewer shows `enum[464]=2`, we can't say what set 464 is or what value 2 represents). These are downloaded from the engine at runtime via `GetClassInfoRmtCmd`; not in static JARs. To get them would require either a live engine capture or BACnet-standard fallback for the well-known sets.
- **Unit-name dictionary** (enum set 507 per JCI's comment). The unit IDs are compiled-in constants in `MetasysUnits.class`. Extracting them needs a Java decompiler (CFR, Procyon, Krakatau) which is a different tool/legal calculus than the regex-on-XML approach we've used. Note: the JCI source itself documents "UnitID 1 = sq ft, UnitID 0 = sq meter" inline in `MetasysUnitConversion.properties` so a small subset could be hand-mapped from comments.
- **Property/class IDs not in static dictionaries** (we still hit ~10% unknowns on real point data, e.g. props 52, 721, 3135, 4306). These live in the engine's runtime dictionary. Could be filled in over time by harvesting from `GetClassInfoRmtCmd` responses if we ever get a live capture.

### v0.3.6 — .caf file support (2026-05-14) ✅

**Major finding: `.caf` files are NOT compiled binary** as previously assumed. They are ZIPs containing a single `*.caf.xml` file in the same JCI XML namespace as `archive.xml`. Earlier "preserve `.caf` byte-for-byte" caution was overly conservative — these are editable plain XML.

- [x] Detect `.caf` zip on load (no `archiveobject.xml` → look for `*.caf.xml`)
- [x] Parse the inner XML through the existing `parseArchive` path
- [x] Synthesize a single-device navtree so the rest of the UI works unchanged
- [x] Updated file-picker `accept` attribute to include `.caf`
- [x] Updated `parseRef` to handle .caf-style refs (no `<ADX>:` prefix, just `<root>/<seg>.<seg>`)
- [x] Use object Description (prop 28) as the tree label when available — turns opaque `307_2` into `SA Bus`, `956_4123` into `Discharge Air Temperature` etc.
- [x] Verified: courthouse VAV `.caf` loads 1,194 objects, root identified as "VAV CTRL/ACT/DP, 3UI, 2CO, 3 BO" (M4-CVM03050-0), children show as semantic names (Discharge Air Temperature, FC Bus, SA Bus, Heating Output, Supply Air Damper Output)

**Implications for the edit roadmap:**
- The "v1.0 edit only metadata, preserve .caf byte-for-byte" plan was too cautious
- `.caf` IS editable as plain XML
- Diff mode already works on .caf since it's just XML objects — could become a "what changed in this control program between revisions" tool
- CCT writes .caf, SCT reads it — full round-trip is technically just zip + XML write

**Known gap:** ~30 CCT-specific class IDs (526, 527, 528, 530, 555, 556, etc.) are not in the static JCI dictionary. Some show via the Description property (the immediate workaround), but the underlying class names are only in the engine's runtime dictionary or compiled Java constants. Could improve by:
1. Decompiling `JCIUIFramework.jar` to find CCT class enum constants (deferred)
2. Building up the dictionary empirically by harvesting Description→Class associations across multiple .caf samples
3. Capturing `GetClassInfoRmtCmd` response from a live engine

### v0.3.8 — Controller identity card + Apply repoint to archive (2026-05-14) ✅

Two features triggered by the 2022 forum thread ("Reading .caf files from Metasys without SCT?" — 2.3K views, accepted answer: "you can't"):

**Controller identity card**
- When an engine/controller root is selected, a prominent card shows: model number, firmware version, IP address (if NAE-class), object ID, class, description
- Pulls these from props 70 (Model), 12 (Comment = firmware on .caf), 44 (IP), 28 (Description)
- Solves the forum thread's "you need to know controller model + firmware version" friction in one glance, without the Launcher

**Apply repoint plan to archive (the killer feature)**
- Detects when slot A has an archive AND slot B has the unbound CSV (or vice versa)
- "Apply to archive" button in Patterns view → confirms → generates a new `.dbexport`
- Handles the **Base64Zip-wrapped content correctly** (114 files in our test archive). User Tree files, Graphics, Programming logic — all gzipped+Base64 inside the XML. Implementation:
  - Native browser `DecompressionStream`/`CompressionStream` for gzip
  - Walk `<Base64Zip>…</Base64Zip>` blocks, decode → substitute → re-encode
- Verified end-to-end against DACC archive:
  - Original: 7,538 dead `DACC-ADX-01:` refs across 114 Base64Zip blocks + 208 plain XMLs
  - Transformed: **0 dead refs**, all 7,538 repointed to `DACC-ADX-02:`
  - Total ADX-prefixed refs conserved (38,001 → 38,001)
  - Structure preserved (same file count, same block count, same compression)
- The output file is a valid `.dbexport` that re-imports into SCT cleanly (round-trip is straight ZIP+XML; we don't touch `.caf` binaries or non-XML files)

**Why this matters:**
- This is the moment the prototype crosses from "viewer" to "tool that fixes things."
- The 7,538 number is *higher* than the unbound-refs CSV reported (6,348) because SCT deduplicates the report at one level; our transform catches every occurrence in the archive.
- The full workflow — drop archive, drop unbound CSV, click one button, download fixed archive — takes about 30 seconds. The SCT equivalent is reportedly thousands of manual clicks.

### v0.3.7 — Unbound References Explorer (2026-05-14) ✅

The killer signal-test feature. SCT's standard workflow for fixing unbound references is one-click-per-row through thousands of items. This makes it a bulk operation.

- [x] CSV detection: `.csv` files parsed as Metasys Unbound References (required columns: Archive, Reference Type, Referring Item, Referring Attribute, Referenced Item, Referenced Attribute)
- [x] New "Unbound Refs" mode button (third mode after Browse / Diff), auto-enabled when a CSV is loaded
- [x] Sidebar with 4 pivots: Detected Patterns (default), By Referring Item, By Referenced Item, All Rows (flat)
- [x] **Pattern detector** identifies dead ADX prefixes that don't match any live one, and suggests a rename target if there's a numeric-suffix match
- [x] Selected pivot value → detail table with referring + referenced + attributes per row
- [x] Filter input narrows visible rows (matches any column)
- [x] **Bulk exports** from any view:
  - Download filtered (CSV) — preserves original unbound CSV format
  - Download delete list (CSV) — unique referring items, one per line, for paste into SCT
  - Export repoint plan (CSV) — find/replace per row with proposed new target

**Verified with real DACC archive (6,427 rows):**
- Pattern detector identified the ADX-01 → ADX-02 rename: **6,348 refs in one bulk operation** (vs SCT's row-by-row workflow)
- "By Referring Item" surfaces the top offender: `$site.UserTrees.DACC` with 4,501 broken refs alone
- Repoint plan export produces a valid 6,350-line CSV ready to drive a global modify

**Why this matters strategically:** This is a specific, acute, repetitive pain point that anyone who's worked with Metasys hates. The signal-test pitch lines up perfectly: *"Drop your UnboundReferences CSV, click one button, get a bulk fix plan instead of clicking through 6,000 rows."* This is the kind of feature that gets unsolicited "this is exactly what I need" replies.

### v0.3 — Audit views (in progress 2026-05-14)
- [x] CSV/JSON export with scoped output (export at current tree node)
  - Points only — CSV (8,958 rows from DACC archive)
  - All objects — CSV (12,319 rows)
  - Schedules — CSV
  - Trend logs — CSV
  - Full data — JSON (26 MB pretty-printed)
- [x] Export menu shows current scope + object count
- [ ] Schedule visualizer (weekly calendar render)
- [ ] Alarm config table (priority, hysteresis, recipients)
- [ ] Trend definitions table (sample interval, retention)
- [ ] Energy-waste heuristics: schedules running 24/7, stuck overrides, suppressed alarms

### v0.4 — Graphics viewer (newer XAML format)
- [ ] Decode gzipped+Base64 XAML files
- [ ] Render WPF Path/Canvas/Image XAML as inline SVG
- [ ] Resolve point bindings against archive (show values inline)
- [ ] Handle `MasterLayer-bindings.json`, `Palette.json`, `ImageGallery/`

### v0.5 — Graphics viewer (older XML/TSEGraph format)
- [ ] Decode gzipped+Base64 graphic XML files
- [ ] Render TSEGraph nodes + connectors as SVG
- [ ] Resolve point bindings

### v0.6 — Programming logic viewer
- [ ] Decode `Programming.*.xml` TSEGraph dumps
- [ ] Render logic blocks + wires as a flow diagram
- [ ] Tooltip on hover showing block params

### v1.0 — Safe edit + export
- [ ] Explicit "edit mode" toggle (opt-in per session)
- [ ] Whitelist of editable property IDs (text-only: Description, Comment, Object Name)
- [ ] Diff-before-save view (like a PR review)
- [ ] Re-serialize XML and rebuild ZIP preserving `.caf` byte-for-byte
- [ ] Validation pass: typed values stay typed, enums stay in set
- [ ] Test round-trip through real SCT (requires SCT access)

### v1.1+ — Future
- [ ] Edit numeric properties (setpoints, alarm thresholds) with reviewer guardrails
- [ ] Graphics edit: text labels + point binding swaps only (no geometry)
- [ ] Multi-vendor: same approach for Tridium Niagara, Siemens Desigo, Honeywell EBI
- [ ] Self-hosted "site memory" — store snapshots over time, alert on drift

## Positioning refinement (2026-05-14)

Initial pitch "audit + diff tool, optionally edit" was too broad. Sharper positioning:

**The missing analysis layer for BAS data.** Not "free SCT", not "edit Metasys without paying" — those overlap too much with SMP (which most ADX-owning facilities already have for operator-level work) and with JCI's licensed engineering products.

What SMP does NOT do, and this tool fills:
- **Diff two snapshots** — see what changed between backups; no equivalent in SMP or SCT
- **Export your data** — clean CSV/JSON of points, schedules, alarms, trends for analysis/sharing
- **Run offline** — view backups when the ADX is down, on a Mac, or on a plane
- **Be used without a license** — consultants, auditors, future contractors with no SMP access

Sharper audiences:
- Energy/commissioning consultants doing portfolio audits
- Owners scoping replacement vendor RFPs
- Forensic engineers analyzing post-incident state
- Anyone receiving a `.dbexport` they can't open today

## Open questions / decisions parked

- **Name**: leaning `dbexport.dev` for v0 — descriptive, discoverable
- **Hosting**: Netlify (free tier, already in use for Gudea). `bacview.netlify.app` for v0 subdomain
- **Distribution**: inline JSZip so single-file HTML works offline; add "Download offline copy" button on hosted site
- **License**: Apache 2.0 (patent grant useful here)
- **Open-source**: yes, GitHub public — credibility for the "100% local" claim
- **Trademarks to avoid**: "Metasys", "SCT", "CCT", "ADX" in product name. Descriptive use ("for Metasys archives") is fine.
- **Logic edit risk**: confirmed via user — graphics edits in SCT itself can brick engines; browser-side edits with manual re-import is actually safer

## Signal-test gate

Before pursuing v1.0 (edit feature), do this:
- Polish v0.3
- Deploy to Netlify
- Post to r/BuildingAutomation, Project Haystack forums, BAS LinkedIn groups
- Threshold: 5+ unsolicited "this is exactly what I need" responses → keep building
- Crickets → stop, low cost spent

## File format notes (durable reference)

`.dbexport` = ZIP archive (Windows `\` separators inside).

Top-level files:
- `archiveobject.xml` — archive metadata
- `navtree.xml` — flat navigation tree of sites + devices
- `CdmFeatureData.xml`, `CdmModelClassData.xml`, `CdmModelClass*` — JCI semantic ontology mapping (1.5MB total). Useful for tagging points to semantic types like `Discharge_Air_Temperature`.
- `certs.xml` — device certificates

Per-device folders (`<ADX-name><Device-name>/`):
- `archive.xml` — all BACnet objects + properties (the bulk of useful data)
- `security.xml` — user/role/permissions
- `userdictionary.xml` — local text labels
- `Programming.*.xml` — individual control logic blocks, **gzipped Base64** of TSEGraph format
- `System Programs.*.xml` — system-level logic blocks, same encoding
- `*.caf` — compiled control logic, **binary**, preserve byte-for-byte on any edit
- `Graphics.*.xml` — older-format graphics, **gzipped Base64** TSEGraph
- `Graphics.*.xaml` — newer-format graphics, **gzipped Base64** WPF/Silverlight vector
- `MasterLayer-bindings.json`, `MasterLayer-metadata.json`, `Palette.json` — new-graphics metadata
- `ImageGallery/` — bitmap assets for graphics
- `$site.UserTrees.*.xml` — User Views (custom navigation organized by purpose, not by device)
- `Checkout` — present when device is "checked out" in SCT

Ref string anatomy:
- `<ADX>:<Engine>/<path>` — colon separates ADX name from engine, slash separates engine from path inside
- Path uses `.` as separator: `FC-1.FEC-3.OA-T` = field bus 1, FEC controller 3, outdoor air temperature point
- `FC-1.BACnet.TEC-1.ZN-T` = BACnet sub-bus under field bus, TEC controller, zone temp
- `N2 Trunk 1.CT-AHU-4 FEC-17` = N2 legacy bus, device labeled "CT-AHU-4 FEC-17"
- `Programming.X`, `Schedule.X`, `Graphics.X`, `$site.UserTrees.X` — category branches

Class IDs (most important):
- 0-25: BACnet standard (0=AI, 1=AO, 2=AV, 3=BI, 4=BO, 5=BV, 13=MI, 17=Sched, 19=MV, 20=TrendLog)
- 165-176: Metasys reference / folder / programming objects
- 197=FEC, 278=N2 device, 425=ADX server, 448=SNC device, 508=BACnet TEC
- 263=Schedule, 344=Graphic, 357=Graphic Bindings
- 502-606: Metasys-native point objects (599-606 = FEC point types, 502-505 = BACnet point flavors)
- 613=NAE-35, 192=NAE-45, 651=NCE-25, 871/872=SNE-01/02
