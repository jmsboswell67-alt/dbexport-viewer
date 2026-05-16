# Contributing

Thanks for stopping by. This project is a side project, maintained when the
maintainer has free cycles — but that hasn't stopped it from getting useful,
and the most valuable parts of it (the dictionary, the FX support coming
soon, the edge cases caught in real archives) come from people sending
fixes back.

If you're a BAS tech, a CCT programmer, an integrator, an SCT power user,
or anyone who's spent late nights staring at archive files: you have
domain knowledge this project needs. There are useful ways to help even if
you've never written a line of code.

## Ways to help (no code required)

**Share weird archives.** The parser was originally calibrated against
Metasys 13.x archives from a specific site. Every site we get a sample
from teaches us a new edge case. Older versions, FX, Verasys, archives
with unusual equipment or naming conventions — all useful. See the
[sample-archive issue template](https://github.com/jmsboswell67-alt/dbexport-viewer/issues/new?template=sample-archive.yml).

**Identify unknown property and class IDs.** When the tool shows
`Property 4306` or `Class 2009`, that's a gap in the dictionary. If your
JCI documentation tells you what those IDs actually are, the
[unknown-id template](https://github.com/jmsboswell67-alt/dbexport-viewer/issues/new?template=unknown-id.yml)
captures it in one filing.

**Capture live engine enums.** *The single highest-impact contribution.* If
you have access to a live ADX, one curl against the Metasys REST API for
the enum sets (`reliabilityEnumSet`, `unitEnumSet`, `objectCategoryEnumSet`,
etc.) closes the largest remaining dictionary gap. The
[enum-capture template](https://github.com/jmsboswell67-alt/dbexport-viewer/issues/new?template=enum-capture.yml)
walks through exactly what to grab.

**Name CCT logic block classes.** The ~30 CCT-specific block class IDs
(526, 528, 555, 556, 568, 658-660, etc.) need authoritative names. If you've
ever mapped any of these by hand from CCT's UI, the
[cct-class-names template](https://github.com/jmsboswell67-alt/dbexport-viewer/issues/new?template=cct-class-names.yml)
tracks the open list.

**File bug reports with detail.** If something rendered wrong, crashed, or
behaved unexpectedly, the
[bug template](https://github.com/jmsboswell67-alt/dbexport-viewer/issues/new?template=bug.yml)
asks for the right info up front — what you did, browser console errors,
file type, archive context. The more of those fields are filled, the
faster the fix.

**General feedback and "have you considered" thoughts** belong in
[Discussions](https://github.com/jmsboswell67-alt/dbexport-viewer/discussions)
rather than issues. Less ceremony.

## Ways to help (with code)

**Dictionary additions.** The `PROP_NAMES` and `CLASS_NAMES` objects near
the top of `index.html` are the simplest entry point for a code
contribution. Add an entry with a `// empirical: <usage pattern>` comment
explaining how you confirmed it. Source attribution matters — future
contributors need to be able to verify against new data.

**Parser improvements for new archive types.** If FX, Verasys, or older
Metasys versions parse incorrectly, the fix usually lives in `parseArchive`,
`parseNavtree`, or the regex assumptions in `analyzeArchiveForUnbound`.
Open an issue first describing what you're seeing so we don't duplicate
work.

**New audit rules.** The audit pipeline (`analyzeArchiveForAudit`) has
three categories shipped. Adding a new one (e.g. *missing trend coverage*,
*setpoint outliers*, *stale objects*) follows a clear pattern: a detector
function that returns rows, a render function, a sidebar entry. The
pattern's documented in the audit section of the code.

**Cross-vendor analogues.** The basic architecture (zipped XML → tree →
diff/export) maps to other BAS vendors' export formats. Tridium Niagara
(`.bog`), Siemens Desigo, Honeywell EBI all have analogous backup
formats. Open an issue if you want to start one — the dictionary and
parsing work is the heavy lift; the rest of the architecture is
ready-to-reuse.

**Anything tagged `good first issue`** in the [issue list](https://github.com/jmsboswell67-alt/dbexport-viewer/issues?q=is%3Aopen+label%3A%22good+first+issue%22)
— a curated set of contained improvements.

## What NOT to share

**Customer archives with site identification.** If your archive contains
building names, addresses, IP addresses, or anything covered by a site
confidentiality clause, **anonymize before sharing**. The bulk-rename
feature in the tool itself can substitute identifiers. When in doubt,
ask in the issue first and we'll figure out a sanitized version
together.

**Live engine credentials, API keys, certificates.** The `security.xml`
inside a `.dbexport` contains hashed credentials and certificate material.
Sharing the full archive without first stripping that file is a leak.
The tool already skips `security.xml` during the unbound scan precisely
because its contents aren't refs-to-fix.

**Anything covered by your employer's IP / confidentiality agreement.**
Internal JCI documents, leaked specifications, scraped product
documentation. The dictionary in this project is built from publicly-
distributed Launcher resource files (factual ID → name extraction is
permitted under interop precedent). Anything more proprietary belongs
nowhere near the repo.

If you're not sure whether something is shareable, ask first.

## Code conventions

This project is intentionally simple:

- **Single file** — everything lives in `index.html` (HTML, CSS, JS, the
  whole app). No build step. No bundler. Open the file in a browser, it
  works. This is a feature: it ships as one file, lives offline, no
  install required.
- **Vanilla ES2020+ JavaScript** — no framework. No TypeScript. The
  audience needs to be able to read the source and PR fixes without
  setting up a toolchain.
- **CSS variables defined at the top** of the `<style>` block — colors,
  spacing, fonts. Reuse the variables rather than hardcoding colors.
- **JSZip is the one external dependency** and it's inlined verbatim in
  `index.html`. Don't add more dependencies without a discussion.
- **No emojis in code or commits** unless the user explicitly asked for
  them or they're displayed in UI strings.

## Testing

There's no test framework. Test by:

1. Open `index.html` in a browser.
2. Drop a sample archive.
3. Exercise the relevant feature.
4. Check the browser console (F12) for errors.

For changes that touch the parser or the unbound scanner, test on at
least:
- A standard Metasys `.dbexport` (the DACC sample from your work or
  any equivalent)
- A `.caf` file
- Two archives loaded simultaneously (diff + cross-site detection)

For browser compatibility, Chrome and Firefox cover ~95% of users; Edge
and Safari are nice-to-haves.

## PR process

1. **Open an issue first** for non-trivial changes. Saves the case where
   two people PR the same thing in parallel.
2. **Reference the issue number** in your PR description.
3. **Single-purpose PRs.** "Fix the FX caf parser + add a new audit
   rule" is two PRs.
4. **Add a punchlist entry** in `PUNCHLIST.md` for anything substantive
   (new feature, parser change, new audit rule). Follow the existing
   entry pattern: section header, "What's new" bullets, calibration
   numbers where applicable.
5. **Test in 2+ browsers** before submitting.
6. **Response time varies** — this is a side project, expect 1-7 days.
   If something urgent is blocking you, say so in the PR and we'll
   prioritize.

## Public credit

Contributors get credited in commit messages, the README acknowledgments
section, and the PUNCHLIST entries that reference their work. The BAS
world is small. Names travel. If you'd rather not be credited, say so
in your PR / issue and we'll respect that.

## Code of conduct

Be excellent to each other. The BAS industry is small enough that
unprofessional behavior gets noticed. We're all trying to make the
tools that make our jobs easier — disagreements happen, snark is
fine, personal attacks aren't.

## License

This project is Apache License 2.0. By submitting a contribution, you
agree that your contribution is licensed under the same terms. The
Apache 2.0 patent grant is the relevant clause for BAS work — it
protects contributors and users from patent claims around the
protocols and formats touched by the code.

## A note from the maintainer

This started as one person reverse-engineering a binary format because
the alternative was paying for SCT. It's grown into something other
people find useful. The best way to keep it growing is for those
people — you — to contribute back the narrow piece of domain knowledge
only you have. Even a single dictionary entry, a single bug report
with a console screenshot, a single sample archive that exposes an
edge case — all of these add up.

Thanks for being here.
