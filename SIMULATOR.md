# Simulator Roadmap

A "Packet Tracer for BAS" — drag-and-drop sandbox where a tech can drop a real `.dbexport`, make edits, simulate the outcome (BACnet network behavior + HVAC physics + control logic), and catch the bricking-the-site failure modes *before* they brick anything.

This document is the long-range vision for where the `dbexport-viewer` project goes after the v0.x audit/repoint/reverse-lookup work that's already shipped.

## Why this matters

BAS techs work without a safety net. Edits to graphics, programming, or controller config get pushed to live engines, and the failure modes — bricked NAE, cascading alarm storms, freeze-fault on a chiller plant, lost comm across a whole MS/TP trunk — can take a site offline. The industry-standard mitigations are "test in a service window" and "have a rollback archive ready." That's it.

No vendor ships a true sandbox. JCI's CCT has a step-through debugger but it runs against your real archive and requires licenses. Tridium's WB sim is closed and Niagara-only. The "BAS simulator" market is research tools (Modelica, EnergyPlus) and vendor training environments — nothing for a field tech to drop a backup into and explore.

The pain point is real, expensive, and concentrated in the audience this project is already aimed at.

## Scope: the four layers

A complete simulator composes four layers. Each has different maturity in the open-source world.

### 1. Physics (HVAC equipment math)
What it does: given component layout (AHU + ductwork + VAVs + chiller plant) and physical inputs (OAT, RAT, duct sizes, fan curves, filter loading), compute realistic outputs (supply temp, supply static pressure, motor amps, kW, latent load).

### 2. Control logic (PID, state, schedule, sequences)
What it does: walk the parsed control graph from a `.dbexport`, apply each block's semantics (math, compare, PID, state machine, schedule, alarm), produce simulated outputs given simulated inputs. Same wires the tech sees in CCT.

### 3. BACnet network (protocol + topology + traffic)
What it does: simulate MS/TP buses, BACnet/IP routers, BBMDs, addressing, broadcast behavior. Lets the tech wire a virtual topology that matches their real site, push it through fault scenarios (comm loss, slow response, broadcast storms), and see what the operator UI would show.

### 4. UI (drag-and-drop sandbox)
What it does: visual canvas. Drop a `.dbexport`, see the parsed topology rendered, edit it, click run.

## What exists in open source (and what doesn't)

A focused review of every adjacent project, with honest verdicts on whether to integrate or pass.

### Physics layer

| Project | License | Status | Verdict |
|---|---|---|---|
| **EnergyPlus** (DOE/NREL) | BSD-3-ish | v26.1 (May 2026), biannual releases | **Borrow as backend.** Gold standard for equipment thermodynamics. Pipe simulated values to virtual BACnet objects. Never bake it in — co-sim via FMI only. |
| **Modelica Buildings Library** (LBNL) | Modelica L2 (BSD-ish) | v13.0.0 May 2026, very active | **The richest physics + controls combo.** Includes ASHRAE Guideline 36 reference sequences. Steep curve. Borrow specific FMUs via Spawn-of-EnergyPlus. |
| **OpenStudio / OpenStudio Application** | LGPL / GPL | v3.11 / v1.11 (Q1 2026) | **Complementary, wrong UI.** Heavyweight Qt geometry editor — wrong metaphor for a tech-facing sandbox. |
| **eppy** (Python) | MIT | Active | **Borrow** if going the E+ route — Python IDF parser saves writing one. |
| **CONTAM** (NIST) | Public domain | v3.4 Jan 2026 | **Skip for v1.** Niche (IAQ/pressurization). Revisit if customers ask. |
| **HVACSIM+** (NIST) | Public domain | Effectively dead (last meaningful update 2021) | **Skip.** Anything HVACSIM+ does, EnergyPlus or Modelica does better. |

**Recommendation:** EnergyPlus via FMI for v3+. For v1 static validation we don't need physics at all — just structural checks.

### Control logic layer

| Project | License | Status | Verdict |
|---|---|---|---|
| **Modelica Buildings G36 sequences** | Modelica L2 | Active | **Borrow as reference.** Guideline 36 is the ASHRAE-published canonical control language. Mapping JCI's CCT block library to G36 primitives is the right interop strategy. |
| **VOLTTRON** (PNNL / Eclipse) | Apache 2.0 | VOLTTRON 10, active but academic-flavored | **Borrow specific pieces.** The BACnet driver agent and BCVTB EnergyPlus bridge are battle-tested patterns. Don't wrap the whole platform — wrong user. |
| **ASHRAE Guideline 36** | Public document | Latest 2024 edition | **The spec to standardize on.** Vendor-neutral, free, growing adoption. |

**Recommendation:** Our own interpreter that maps Metasys CCT blocks → G36 primitives. This is the strategic moat — the bridge nobody else has.

### BACnet network layer

| Project | License | Status | Verdict |
|---|---|---|---|
| **bacnet-stack** (Steve Karg) | GPL-with-exception (commercial linking OK) | Continuously maintained since ~2003, commits weekly | **Wrap and integrate.** Reference open BACnet stack in C. There's also a Rust port (bacnet-stack-rs, April 2026). |
| **BACpypes3 / BAC0** (Bender / Tremblay) | MIT | Active, BAC0 released 2025-09 | **Wrap and integrate, alternative path.** Python BACnet stack. Faster iteration than C. Many existing OSS BACnet simulators are thin wrappers over BAC0. |
| **YABE** (Yet Another BACnet Explorer) | GPL | Active (commits May 2026) | **Complementary, not foundation.** Use it to validate the virtual devices our simulator exposes. |
| **Other OSS BACnet simulators** (Kretiss, openbms-io/bacnet-simulator, simbac, BACnetSim) | Various | Toy/demo scale | **Reference only.** Prove the wrapping pattern works; no fit-for-purpose simulator exists at integration scale. |

**Recommendation:** bacnet-stack (C) for production-grade virtual devices. bacpypes3 for fast prototyping. The protocol is fully open and well-documented.

### Data model layer

| Project | License | Status | Verdict |
|---|---|---|---|
| **Brick Schema** | BSD-3 | v1.4.4 May 2025 | **Borrow as internal data model.** RDF + SHACL gives free validation of topology built from `.dbexport`. "This VAV serves zones X,Y, downstream of AHU-3" is a Brick query. |
| **Project Haystack** | Academic Free License 3.0 | Xeto spec (2025), active | **Borrow tagging vocabulary** for point display. Don't build the sandbox around it (different product — analytics). |
| **buildingSMART / IFC** | CC-BY-ND, ISO 16739-1:2024 | IFC4.3 ADD2 (2024), active | **Skip for v1.** BAS techs live in P&IDs and point lists, not IFC trees. Revisit for commissioning workflows. |

**Recommendation:** Brick Schema as the internal model. Haystack tags as display layer for points. Output IFC only if a customer demands it.

### UI layer

No open-source project ships a fit-for-purpose UI for what we need. OpenStudio is geometry-focused (wrong metaphor). YABE is a tech-tool client (wrong audience). Modelica IDEs are research environments (wrong UX).

**Recommendation:** Build it. Web-first (extension of the current `dbexport-viewer` HTML/JS) for v1 and v2; consider desktop (Flutter or Tauri) if we need OS-level integrations later (USB BACnet adapters, etc.).

## Closest commercial / research competitors

- **BOPTEST** (`github.com/ibpsa/project1-boptest`) — IBPSA Project 2, very active 2025–2026. Containerized building emulators (Modelica + FMI) exposed via REST. The closest existing "sandbox for HVAC controls" in OSS. **But:** no BACnet wire, no GUI, no `.dbexport` ingest, aimed at algorithm researchers benchmarking RL controllers — not techs learning to read Metasys logic. Borrow patterns (FMI co-sim, REST control surface), don't compete head-on.
- **Spawn-of-EnergyPlus** (NREL/LBNL, 2023, now in Modelica Buildings 13) — modern E+/Modelica co-sim bridge. Use under the hood when we add physics.
- **SimpleSoft SimpleIoTSimulator** — commercial, ~$thousands/seat, proprietary. Loads BACnet device backups for testing client tools. No physics, no Metasys ingest.
- **Softdel BOSS Simulator** — most direct philosophical competitor. Closed-source. Doesn't ingest Metasys. Doesn't simulate equipment.

**No one has built what this project is heading toward.** The pieces exist; the integration doesn't.

## What we already have (foundation)

The current `dbexport-viewer` is meaningfully past the "viewer" stage and has shipped pieces that are pre-requisites for the simulator:

- **`.dbexport` parser** — full archive ingest, per-device, per-object, per-property. The strategic asset; no other project has this.
- **TSEGraph parser** — control logic structure extraction (nodes, edges, ports, references). The skeleton of every Programming.X block.
- **Reference index (`arc._refIndex`)** — every ref in the archive, where it's used. The dependency graph for impact analysis.
- **Audit pipeline** — static analysis precedent (suppressed alarms, duplicates, orphans). The pattern for v1 simulator validation rules.
- **Repoint + delete pipelines** — proof we can rewrite archives. SCT round-trip verified.
- **Validation against ground truth** — calibrated against SCT's unbound CSV at 87.9% recall.
- **Reverse lookup UI** — pre-deletion impact preview pattern.

These extend naturally into simulator features.

## Phased build plan

### Phase 0 (current state, shipped)
Audit + reverse-lookup + repoint + delete-to-archive. Production-ready as a viewer/auditor. **Done.**

### Phase 1: Static validator (4–6 weeks)
A new "Validate" mode (alongside Browse / Audit / Unbound). Loads original + edited archive (or just one if creating from scratch) and runs structural lint rules:
- Required-object check: engine root, NIC, security objects exist
- Ref integrity: every internal ref resolves to a defined object (extension of the unbound scan to apply to *edited* archives, not just published ones)
- Graphics binding lint: every `<reference>` inside a Base64Zip graphic payload points to something that exists
- Programming wire lint: every TSEGraph edge has a defined source and target port
- Setpoint sanity: heating SP < cooling SP, both in human ranges (e.g. 50°F < setpoint < 95°F), deadband > 0
- Schedule sanity: at least one occupied period defined, default event not malformed
- Alarm config: notification class refs resolve, hysteresis present where required
- Class-specific rules: AI objects have units, AO objects have a Relinquish Default, schedules have a weekly schedule, etc.

Output: pass/warning/error per rule with the offending refs and one-click "show in Browse mode" navigation.

**No physics, no BACnet stack, no UI builder.** This is the audit feature dressed up as a pre-flight validator. Ships in weeks, immediately useful.

### Phase 2: Impact preview (3–4 weeks)
Extension of reverse lookup into a "what if" UI:
- Right-click any object → "Simulate delete" → shows the blast radius (downstream graphics, programs, schedules, user trees that reference it)
- Right-click any prefix → "Simulate rename" → preview the repoint plan + confidence pill (we already have this pattern for unbound refs)
- Diff-with-validation: drop the original in slot A, the edited version in slot B, run static lint on the *delta* — "your edit creates 12 new unbound refs, removes 4 valid references, changes the setpoint on 3 objects"
- Sandbox edit mode: edit objects in-browser (Description, setpoints, schedule patterns), keep validation running live, export the modified archive

Output: a pre-export sanity check. By the time you click "save," you know it'll import cleanly.

### Phase 3: BACnet network simulator (8–12 weeks)
This is the "Packet Tracer for BACnet" piece. Layered on bacnet-stack (C, compiled to WASM for browser, or running as a sidecar service):
- Drag-and-drop topology canvas (MS/TP trunks, BACnet/IP routers, BBMDs)
- Auto-populate from `.dbexport` — every device in the archive becomes a virtual BACnet device exposing its objects
- Simulate addressing (instance numbers, MAC addresses on MS/TP, IP addresses)
- Simulate broadcast behavior (Who-Is/I-Am, change-of-value, alarm notifications)
- Inject faults: drop a trunk, kill an FEC, slow a controller's response time, force a token loss
- Wireshark-like packet log: see exactly what's on the wire under each scenario
- Connect external tools (YABE, real BACnet clients) to the virtual network for cross-validation

Output: a tech can wire up their virtual site, point their real engineering tool at it, and verify commissioning before driving to site.

### Phase 4: Control logic runtime (12–16 weeks)
The heaviest lift. Interpret the TSEGraph and produce simulated outputs:
- Map every CCT block type to its behavior (math, compare, PID, state, schedule, alarm, ramp, deadband, etc.)
- Walk the wires; given input values, propagate to outputs
- Support timing: PID integration, schedule transitions, debounce
- Map to ASHRAE Guideline 36 primitives where possible — gives us a vendor-neutral foundation
- Per-block JCI-specific quirks captured as data files (so future block-library updates don't require code changes)

Output: drop your archive, set OAT/RAT/setpoints, see how the supply temp tracks over a simulated day. Step through logic block-by-block.

**This is the technical moonshot.** Probably the longest lift. But the prize is large — once this works, the simulator can actually predict whether an edit will brick a sequence before it ships.

### Phase 5: Physics-backed runtime (additional 8–12 weeks on top of Phase 4)
Couple the control runtime to EnergyPlus or Modelica Buildings via FMI:
- A drop of `.dbexport` infers (or accepts user input for) the physical model: AHU type, zone areas, duct sizes, equipment capacities
- Map archive objects to E+/Modelica components
- Run a full coupled simulation: physical inputs → controls → equipment response → loop back
- Replay historical trend data: "yesterday's actual OAT cycle, applied to your edited logic — here's what would have happened"
- Fault injection at the physical layer: stuck damper, failed sensor, fouled coil

Output: validation that an edit not only doesn't break SCT import, but doesn't break the building either.

### Phase 6+: Operational features
- Save/load simulator scenarios
- Share scenarios as `.dbexport-sim` bundles (archive + simulated state + replay log)
- Training mode: pre-built scenarios with intentional faults, junior tech has to find + fix
- DR integration via openLEADR for utility customers
- Brick / Haystack tagging on all simulator outputs for analytics export

## Strategic positioning

**Vs. BOPTEST**: BOPTEST is for researchers; this is for techs. Different UI, different ingest (`.dbexport` not Modelica), different fault model (real Metasys quirks not theoretical), different value prop (don't brick the site vs. benchmark an algorithm).

**Vs. JCI's CCT**: CCT is the engineering tool of record and isn't going away. The simulator is the staging environment CCT lacks. Complementary, not competitive. Position the project as "the layer that catches CCT mistakes before they hit production." JCI itself probably benefits from this existing (fewer service-truck rolls).

**Vs. Tridium WB sim**: WB sim is Niagara-only and closed. This project is Metasys-first and open. Different ecosystems. Could expand to Niagara later (`.bog` parser is harder than `.dbexport` but tractable).

**Vs. SimpleSoft / Softdel**: Commercial, proprietary, both gated behind sales conversations and per-seat licensing. Open source + free for techs + `.dbexport` ingest is a clear differentiator. Their lunch is takeable.

**Vs. existing open-source BACnet simulators (Kretiss, simbac, openbms-io)**: All toy-scale. None ingests Metasys. None has physics. None has a UI. We compose them or skip them.

## Composition decisions (locked in)

| Layer | Choice | Status |
|---|---|---|
| `.dbexport` parser | **Our own** | Shipped |
| Static validation | **Our own** (extension of audit) | Phase 1 |
| Internal data model | **Brick Schema** + Haystack tags | Phase 2 |
| BACnet protocol stack | **bacnet-stack** (C/WASM) or **bacpypes3** (Python sidecar) | Phase 3 |
| Network UI | **Our own** | Phase 3 |
| Control logic interpreter | **Our own**, mapping to G36 primitives | Phase 4 |
| Physics engine | **EnergyPlus via FMI** (later: Modelica via Spawn) | Phase 5 |
| Topology editor | **Our own** | Phase 1+ |
| Wire-level packet log | **Wireshark BACnet dissector** semantics as reference | Phase 3 |

## What this isn't

- **Not a replacement for SCT.** SCT is JCI's engineering tool of record. This is the staging environment SCT doesn't have.
- **Not a Niagara/Honeywell/Siemens tool.** Metasys-first by design (because that's where the deepest archive-parsing knowledge sits). Cross-vendor is a v3+ conversation.
- **Not a thermodynamic research platform.** Researchers should keep using EnergyPlus and Modelica directly.
- **Not a building-energy model.** Energy modeling is what OpenStudio is for. This simulator answers "will this edit brick the site," not "will this building hit Energy Star Platinum."

## Open questions (research debt)

These need answers before committing to certain phases:

1. **`.caf` runtime semantics**: how does the NAE actually execute a compiled `.caf`? We can read the format but the runtime quirks (sample rates, propagation order, race conditions on shared variables) are JCI-internal. Probable solution: ASHRAE G36 mapping + empirical observation.
2. **Block library completeness**: the ~30 CCT block IDs we don't have names for (526, 528, 555, 556, etc.) need either JCI insider data or empirical inference from real archives. Punchlist mentions this.
3. **MS/TP timing accuracy**: real MS/TP trunks have token-passing dynamics that affect commissioning. How accurate does our simulator need to be? Probably "ballpark right" for v1 (catch broadcast storms) and "tight" for v2 (predict bus saturation).
4. **License-friendly G36 mapping**: ASHRAE 90.1 and G36 are public documents but their exact pseudocode may have licensing constraints. Need to verify.
5. **Browser vs. server**: bacnet-stack in C compiled to WASM is feasible (someone has done it) but heavy. A Python sidecar with bacpypes3 is easier but requires deployment. For a free in-browser tool, WASM is the right call long-term.

## Reference reading

External docs and projects worth bookmarking:

- [BOPTEST repo](https://github.com/ibpsa/project1-boptest) — closest analog, study the FMI co-sim patterns
- [EnergyPlus releases](https://github.com/NREL/EnergyPlus/releases) — the physics backend
- [Modelica Buildings Library](https://github.com/lbl-srg/modelica-buildings) — G36 sequences live here
- [bacnet-stack](https://github.com/bacnet-stack/bacnet-stack) — the BACnet protocol stack
- [BACpypes3](https://github.com/JoelBender/BACpypes3) and [BAC0](https://github.com/ChristianTremblay/BAC0) — Python prototyping
- [Brick Schema](https://github.com/BrickSchema/Brick) — internal data model
- [Project Haystack Xeto](https://www.project-haystack.org/) — tagging vocabulary
- [Spawn-of-EnergyPlus](https://www.energy.gov/cmei/buildings/articles/spawn-energyplus-spawn) — modern co-sim bridge
- [ASHRAE Guideline 36-2024](https://www.ashrae.org/technical-resources/ashrae-standards-and-guidelines) — canonical control sequences
- [openLEADR](https://openleadr.org/) — demand response, future feature
- [YABE](https://sourceforge.net/projects/yetanotherbacnetexplorer/) — validation target

## Honest bottom line

The pieces exist. The integration doesn't. The Metasys-specific knowledge (the `.dbexport` parser, the TSEGraph parser, the audit-rule library) is the strategic asset and is already shipped. The remaining work is real but mostly composition, not invention.

A focused six-month effort by one or two people could get to Phase 3 (validation + impact preview + BACnet network sim). A focused year could get to Phase 4 (control runtime). Phase 5 (physics) is open-ended but optional — many useful workflows don't need it.

Anyone willing to commit that time has a clear path to a category nobody else owns.
