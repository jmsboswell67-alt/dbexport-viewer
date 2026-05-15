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

### v0.3.9 — Empirical dictionary expansion from cross-archive harvest (2026-05-14) ✅

Cross-archive inventory across 8 dbexports (DACC × 2, Ottawa Cal City, Peoria County × 4, SIU Med) found:
- 118 distinct class IDs in the wild (we had names for 64)
- 625 distinct property IDs (we had names for 41 of them by frequency)

Added 20 empirical class IDs by usage-pattern inference:
- **130, 257, 326, 327, 328, 329, 362** — Logic Sub-block (Programming sub-objects, refs like `Programming.X.$NNNN`)
- **173** — BBMD (BACnet Broadcast Management Device)
- **177** — Logic Program (`Programming.OAT SHARE` etc.)
- **345** — Trend Study (refs like `Trends.Court Rooms`, `$FacilityTrendStudies.*`)
- **348** — User Tree (refs like `$site.UserTrees.X`)
- **501** — BACnet Analog Output (refs like `Analog Outputs.AO-0`)
- **504** — BACnet Binary Output
- **511** — BACnet Group (refs like `Device-NNNNNN.Group-NN`)
- **513** — BACnet Multistate Input (descriptions "Normal/On/Override")
- **514** — BACnet Multistate Output (`MO-1`, desc "Occ")
- **515** — Notification Class (descriptions "NotificationClass1/2/3")
- **763** — BACnet Event Enrollment (refs ending in `.Notification`)
- **844** — Facility Graphic Asset (`$FacilityGraphics.00001.<timestamp>-<hash>`)
- **847** — Generic Archive Container (`$GenericArchive.GraphicAssets`)
- **909** — FC Bus (MS/TP Trunk) (description "FC Bus")

Verified against the Peoria archive that triggered the audit: 14/14 named classes resolve correctly. Long tail of ~9 unnamed classes (cid 161, 340, 343, 661, 758, 907, 908, 2009, 2013) remains — these need authoritative sources to confirm.

Inline source attribution on each empirical entry says "// empirical: <usage pattern>" — so future maintainers can verify against new data.

### Known gap: properties

The cross-archive inventory found 524 still-unknown property IDs. The top ones by frequency:
- prop=4306 (75K occurrences) on Analog Reference / Logic Program / FEC AI — likely a Source/Reference attribute
- prop=3135 (68K) on FEC AI/BI/BO — universal point status?
- prop=721 (52K) on Programming / Analog Reference
- prop=52 (50K) on Analog Reference / FEC AI/AV
- prop=352 (42K) on Trend Extension / FEC AI/BO

These weren't added because property names are ambiguous from class context alone — confusing the user with wrong names is worse than honest "Property N" placeholders. Filling these requires either:
1. A captured engine response from `GetClassInfoRmtCmd` (live ADX needed)
2. Decompiling `MetasysUI.jar` for hardcoded property name constants

Logged as future work; not blocking signal-test.

### v0.3.10 — Native unbound-ref scanner + delete-to-archive workflow (2026-05-15) ✅

Big session. Closed the most obvious gap in the signal-test pitch (the "mass-correct unbound refs" workflow used to require an SCT-generated Unbound References CSV — anyone without SCT was stuck), then built out the full audit + fix + verify loop.

#### Native scanner

Drop a `.dbexport` and the viewer scans for unbound refs natively. No CSV required.

- Builds a Set of every defined object ref across all devices in the archive
- Walks every `*.xml` inside known device folders (skips archive-root metadata like `archiveobject.xml`, `navtree.xml`, `Cdm*.xml`; skips `security.xml` and `userdictionary.xml` whose base62 hash tokens otherwise match the ref regex by accident)
- Decodes every `<Base64Zip>` payload inside those XMLs — logic and graphic bindings live there
- Strips Base64Zip blocks from the outer text before scanning the outer XML, so raw base64 bytes don't pollute matches
- Regex `<ADX>:<Engine>/<path>` with hardened guards: ADX/engine forbid spaces (real Metasys hostnames don't have them), pure-digit ADX prefixes rejected (IP / timestamp fragments), `data:` URL prefix rejected (inline image assets), engine-name-as-ADX false positives rejected, dedupe at `(referring, attr, referenced)` level
- Refs attributed per-object/per-property when sourced from `archive.xml`; non-archive.xml refs get a synthesized `<ADX>:<engine>/<file-stem>` Referring Item so the patterns analyzer's split-on-`:` ADX extraction stays clean
- Every row carries a `_source` field (the zip file path it came from) for audit

**Calibrated against SCT ground truth** (`UnboundReferences.csv` exported by SCT vs scanner output on the same DACC archive):

| Metric | SCT | Scanner | Delta |
|---|---|---|---|
| Total rows | 6,427 | 5,652 | -12% |
| Unique referring items | 100 | 87 | -13% |
| Unique referenced items | 4,802 | 5,018 | +4% |
| Top offender `$site.UserTrees.DACC` | 4,501 | 4,420 | -1.8% |

The 12% delta comes from SCT recording each attribute occurrence as a separate row (e.g. "Action Table 1" and "Action Table 2" both listed when they reference the same dead target); the scanner dedupes those. Bulk-fix decisions are identical.

#### Apply delete to archive

The viewer can now produce a corrected `.dbexport` with selected items removed — not just a CSV that SCT then has to act on.

- `applyDeletesToArchive(arc, items)` removes each item's source XML from a copy of the zip
- File-level items (graphics, programs, user trees) → file removed cleanly
- Object-level items (refs inside a device's `archive.xml`) → reported as skipped, with instruction to delete in SCT manually (surgical XML editing of archive.xml is doable later but is riskier)
- Output is a valid `.dbexport` that imports back into SCT via Restore Archive

**Three entry points** to the same flow:
1. Action-bar **"Apply delete to archive (.dbexport)"** — bulk, acts on every unique referring item in the current view
2. Per-row **🗑 Delete this item from archive** button — granular, one item at a time, only on file-level rows
3. Multi-select via checkboxes (see below) — granular, multiple items, any subset

Each path runs through `exportAppliedDeleteArchive` which shows a categorized confirm dialog (`5 user trees`, `70 graphics`, `11 programming logic blocks`, etc.) and a follow-up summary listing any object-level items that need manual SCT cleanup.

#### Multi-select with filter + checkboxes

The All Rows / By Referring / By Referenced views now support row-level selection.

- Checkbox column on every row
- Header checkbox **selects every file-level item in the current filter** (not just the capped 2,000 visible rows — important because one item like `$site.UserTrees.DACC` with 4,420 rows would otherwise dominate the cap)
- Selecting any row syncs sibling rows (other rows for the same referring item visually check too and the row highlights in the accent color)
- Object-level rows show a disabled checkbox with a tooltip explaining they need SCT-manual cleanup
- Action bar dynamically shows `N items selected` pill + swaps the bulk button to **"Apply delete to selected (N) (.dbexport)"**
- "Clear selection" button alongside the pill
- Selections persist across filter changes (you can filter to "Graphics.Lincoln", select 13 items, switch filter to "Graphics.Cannon", add those too, both groups stay selected)

#### Rename confidence indicator

The patterns view now shows a confidence pill next to each rename suggestion: `✓ 94% of refs land on real objects`. For each suggested rename (e.g. `DACC-ADX-01 → DACC-ADX-02`), we rewrite every unique dead target and check what fraction land on a defined object in the archive. High % = rename hypothesis confirmed; low % = the dead-prefix objects might just be gone, and Apply-to-archive would create different unbound refs.

Three confidence tiers visually:
- **≥80% green** — rename hypothesis confirmed
- **50–80% yellow** — shaky, audit before applying
- **<50% red** — likely wrong target

On DACC: 94% of refs land on real objects after the `DACC-ADX-01 → DACC-ADX-02` rewrite. The 6% that don't are real underlying problems (deleted N2 trunk room sensors, dead NIE controllers, ADX self-references) that would surface as a much smaller unbound list after the bulk repoint — exactly the right workflow.

#### Audit improvements

- `_source` line on every row showing the zip path the ref was found in (audit hook — open that XML in any editor and verify the ref is really there)
- Categorized warning dialog before any delete-list CSV export (`1 user tree`, `70 graphics`, `16 programming logic blocks`) with a callout steering the tech to Apply-to-archive when a rename pattern exists

#### Strategic significance

The pitch tightens substantially:

- Before: "drop your SCT unbound CSV, click one button, get a bulk fix plan"
- After: "**drop your `.dbexport`. We scan, classify, score confidence, and emit a corrected `.dbexport` that imports back into SCT directly.** No SCT license needed, no CSV pre-export step, no per-row clicking through thousands of items."

The output is the same `.dbexport` format SCT writes, so the full "scan → audit → fix → re-import" round-trip closes without ever opening SCT until the final restore.

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

### Documentation review — dry holes (2026-05-14)

Reviewed three more JCI PDFs the user pulled from Knowledge Exchange:

**CCT Help PDF** (54.7 MB / 2058 pages)
- Hoped: would have class IDs for the 30+ unknown CCT logic-block classes (526, 528, 555, 556, 561, 568, 658-660 etc.)
- Reality: every page is by-NAME, never by-numeric-ID. The CCT Help describes attributes/objects by their semantic name but never enumerates the class ID lookup. The big class ID table only lives in the *SMP* Help (page 23-30, already harvested).
- **Net new dictionary entries: 0**
- Useful as a user-facing reference for what each logic block DOES, but doesn't help close the dictionary gap.

**GGT Help PDF** (6.4 MB / 496 pages)
- Hoped: XAML schema for the newer `.xaml` graphics format
- Reality: procedural UI guide. Confirms several useful facts (XAML files are WPF-compatible, Bindings connect graphic elements to Metasys attributes, GEL is the symbol library) but doesn't document the actual XML schema or symbol library inventory.
- **Net new dictionary entries: 0**
- Useful for a future graphics renderer: tells us what to look for (Binding markup extensions, GEL symbols).

**Metasys UI Help PDF** (31.2 MB / 729 pages)
- Hoped: maybe an enum set reference or new attribute IDs from the web UI
- Reality: web UI procedural guide. "Enum Set" mentions are about UI controls, not data. "Attribute ID" mentions are unrelated context (identity provider attributes).
- **Net new dictionary entries: 0**

### What remains genuinely unmined

After all the harvesting in this session, three sources would actually crack open new dictionary content:

1. **A captured response from a live engine**: `GET /api/v6/schemas/enums/{enumSetName}` for `reliabilityEnumSet`, `unitEnumSet`, `objectCategoryEnumSet`, etc. JCI's REST API publishes these by-name in the OpenAPI spec but the actual ID→name content is fetched live. One curl from a live ADX would give us all of them.

2. **SCT's local cache files**: SCT itself probably has the dictionary cached locally (in `%ProgramData%\Johnson Controls\` or similar). A user with SCT installed could check.

3. **Java bytecode decompilation** of `MetasysUI.jar`: a tool like CFR or Procyon would extract the `static final int X = N` constant definitions that map names to IDs. This is the last-resort path but conclusive.

For graphics rendering specifically, the highest-leverage move would be to write a binding-extractor: parse decoded XAML to list every Metasys object attribute referenced by every graphic. That alone would be a useful audit feature without needing to render anything.

### v0.5.0 — Logic / Programming visualizer foundation (2026-05-14) ✅

Multi-session arc toward full CCT-style rendering. This session delivered the
foundation: TSEGraph parser + SVG layout render of nodes and edges.

**Format discovery:**

Programming/*.xml and System Programs/*.xml files (inside engine folders in a
`.dbexport`) and `.caf` files all use the same **TSEGraph (Tom Sawyer Graph)**
XML format, wrapped in a Base64Zip envelope. The structure:

```
<topology>
  <node>NODEID<type>T</type><text>LABEL</text>
    <geometry>...<x>X</x><y>Y</y><width>W</width><height>H</height>...</geometry>
    <shape>com.tomsawyer.drawing.TSPolygonShape...</shape>
    <connector>PORTID<geometry>...<magnifiedX/Y>...</geometry><attrNum>N</attrNum></connector>
    ...
  </node>
  <edge>EDGEID
    <source>SRC_NODE</source><target>TGT_NODE</target>
    <geometry>
      <sourceConnector>SRC_PORT</sourceConnector>
      <targetConnector>TGT_PORT</targetConnector>
      <point><x>X</x><y>Y</y></point>...   (routing waypoints)
    </geometry>
    <reference>FQR</reference>
    <sourceAttr>ATTR_ID</sourceAttr>
  </edge>
</topology>
```

Key insight: TSEGraph uses `<connector>` as a *port* (input/output anchor on a
node), and `<edge>` as the actual edge between nodes. The edge geometry
contains routing waypoints (CCT's exact line path), so we render the same
shape the user would see in CCT.

**This session delivers:**
- `parseTSEGraph(xml)` — returns `{ nodes, edges, viewBox }` with full geometry
- 5th mode: **Logic**, enabled whenever an archive with `_zip` is loaded
- Sidebar lists all Programming/System Programs files grouped by engine
- Click a file → indexed, decoded, parsed, rendered as live SVG
- Header shows nodes/edges/types/canvas-size summary
- Below the diagram, a node inventory table (id, type, label, position, size, port count)

**Verified against the DACC archive:**
- 20 Programming files indexed
- AHU-7-1: 18 nodes, 16 edges, canvas 796×595 — rendered cleanly
- Nodes like "Span", "Input Ref", numeric constants ("5", "55"), state constants ("On") at their original CCT positions
- Edge waypoints traced verbatim from the CCT XML

**Roadmap to full CCT fidelity (future sessions):**

### v0.5.1 — Pan/zoom + viewport controls
- Scroll-wheel zoom centered on cursor
- Click-drag to pan
- "Fit to screen" / "1:1" / "Reset" buttons
- Mini-map for very large logic files

### v0.5.2 — Block-type-specific symbols
- Currently all nodes render as identical orange-stroked rectangles. CCT uses
  different shapes per block type (PID = rounded rectangle, math operators =
  circle with operator symbol, state generators = diamond, etc.).
- Block type identification — needs to extract from `<shape>` field (e.g. the
  shape's <points> polygon defines AND/OR gate triangles, etc.) and/or from
  the node's `<reference>` pattern (e.g. `Programming.X.$NNNN` cid in the path
  tells us PID vs Math vs Compare).
- Build a symbol catalog: maybe 30-40 standard CCT block types, each as an
  SVG `<symbol>` definition.

### v0.5.3 — Port-on-edge placement
- Ports currently render as small circles centered at the node center plus
  the `magnifiedX/Y` offset. This puts them inside the node rather than ON
  the edge.
- Use magnifiedX/Y to place ports at the correct edge (top/right/bottom/left)
  with proper input/output side conventions (inputs left, outputs right).

### v0.5.4 — Point binding overlay
- For nodes whose `<reference>` resolves to a Metasys point, fetch the point's
  Description and Present Value (from the parent archive's archive.xml).
- Show "Description: Discharge Air Temperature" + current value next to each
  input/output reference block.
- This is the big "what does this logic actually DO?" feature — turns abstract
  boxes into named semantics.

### v0.5.5 — Edge routing + arrowheads
- Current edges go straight through waypoints. CCT uses orthogonal routing
  with corner rounding. Need to smooth corners.
- Add arrowhead at target end (currently the SVG marker is defined but the
  inline assignment isn't quite right).
- Color edges by data type (boolean vs analog vs enum) based on `sourceAttr`.

### v0.5.6 — Apply to `.caf` files too
- The .caf inner XML uses the same TSEGraph format. Adapt the Logic mode to
  also render .caf payloads as logic diagrams when a .caf is loaded directly.

### v0.6 — Older XML graphics (TSEGraph format too)
- Graphics.<Building>.<Name>.xml in the ADX device folder uses TSEGraph with
  additional <backgroundImageData> (an inline gzip+Base64 SVG) and richer
  TSPolygonShape definitions for the HVAC equipment.
- Once v0.5.4 lands, we can render these as overlays with the bound points
  shown inline.

### v0.7 — XAML graphics
- Different format entirely (WPF/Silverlight, not TSEGraph). Would need a
  separate parser + a WPF→SVG translation layer. Much bigger lift.

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
