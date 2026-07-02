# Changelog

## v1.3.0-full-roadmap-release

- Completed the full 1,645-entry master lexicon: 1,645 authored entries, zero
  stubs, 1,645 unique summaries, 1,645 unique shadows, and real senses for all
  overloaded terms.
- Hardened lexicon validation so stubs, generic boilerplate, missing shadows,
  duplicated shadows, and doubled `Shadow:` labels fail validation.
- Added executable benchmark fixtures with planted ground truth for all six
  field-spell evaluation cases.
- Re-ran the measured evaluation bench on the project-owned Codex surface with
  three weak/repaired repetitions per case, preserving 36 prompt/transcript
  runs.
- Added outcome scoring alongside the secondary structural rubric and disclosed
  the prompt-echo limitation of keyword-based structural scoring.
- Replaced Codex-exclusive evidence tests with surface-agnostic integrity tests
  that require prompt files, transcript files, fixture paths, timestamps,
  structural scores, outcome scores, and notes.
- Added generated installable exports for Markdown spells, Markdown stacks,
  Codex task templates, and Cursor rules.
- Added `grimoire export --target ...` for local inspection of generated
  installable assets.
- Added an installable-library adoption page and Pages resources for exports and
  evaluation fixtures.
- Added a release-gate stack dogfood record tied to the public GitHub Pages
  publish workflow.
- Updated the roadmap away from scope contraction and toward full completion.
- Rendered site size is now 76 Quarto pages.

## v1.0.0-canonical-field-release

- Rebuilt the homepage around the practical engineering payoff, with a weak
  request, repaired spell, expected delta, quick-start path, and direct spell
  link.
- Added `quick_start.qmd` with a plain-English map from grimoire vocabulary to
  ordinary engineering terms.
- Added `data/canon_quality.json`, `schemas/canon-quality.schema.json`, and
  validation coverage for authored-layer quality reporting.
- Reviewed all 50 major-canon shadows and made them term-specific.
- Clarified `sense` policy so category labels no longer masquerade as real
  disambiguators; current counts are 305 authored entries and 1,302 stubs.
- Moved the full house pages into a clearly labeled partially authored master
  lexicon appendix.
- Added copyable fenced templates and raw prompt links to every field-spell
  page.
- Added generated `prompts/` assets for all six field spells and six stack
  workflows.
- Added Codex-owned recorded weak-vs-repaired evaluation runs for all six field
  spells, including score tables, raw prompt files, raw transcript files, and
  one preserved non-win.
- Added `examples/evaluations/` result pages generated from
  `examples/evaluations/results.json`.
- Added adoption-kit pages for copying assets and using the local CLI in an
  external workflow.
- Expanded `scripts/grimoire.py` with `new spell`, single-file `validate`, and
  single-file `seal` commands.
- Added tests for recorded evaluation integrity, the local CLI round trip, and
  canon-quality schema conformance.
- Rendered site size is now 75 Quarto pages.

## v0.3.0-integrity-evidence-ci

- Added honest lexicon completion metadata for all 1,645 entries.
- Marked 343 major/pocket entries as authored and 1,302 master-lexicon entries
  as stubs pending term-specific authoring.
- Surfaced lexicon completion counts on porting status, reference index,
  lexicon, term index, and per-house pages.
- Added `reference/proof-by-difference.qmd`.
- Added one weak-vs-repaired Proof by Difference case for each field spell.
- Added a replayable evaluation template and six-case field-spell evaluation
  matrix.
- Linked every spell page to its matching Proof by Difference case.
- Expanded tooling and living-practice chapters with schema, registry, replay,
  seal, evaluation, team adoption, and canon-governance guidance.
- Tightened JSON schemas for lexicon entries, spells, stacks, and seals.
- Hardened validation for completion status, authored shadows/senses,
  spell-rune references, and stack-spell references.
- Added pytest coverage for schema conformance, seal stability, validation, and
  rendered internal links.
- Added a pull-request/non-main branch check workflow and made Pages publishing
  run pytest before deploy.
- Updated README badges, render size, commands, public URLs, and MIT license
  statement.
- Updated contribution guidance for generated pages, lexicon status, and Proof
  by Difference cases.
- Removed the stale duplicate weak-vs-repaired refactor Markdown example.

## v0.2.0-reader-links

- Added guided reader path and porting status pages.
- Added stable rune anchors for all 1,645 lexicon entries.
- Added generated major/pocket/master lexicon links into detailed house entries.
- Added generated term index and canon map.
- Added related-rune sections to spell pages.
- Added related-spell and related-rune sections to stack pages.
- Added chapter related-links sections.
- Extended validation to check rune anchors, spell rune references, stack rune
  references, and stack related-spell references.
- Verified the generated 58-page site with a local internal-link audit.

## v0.1.0-public-seed

- Created public Quarto project scaffold.
- Preserved source manuscripts.
- Added generated book chapters and reference pages.
- Added structured spell, stack, lexicon, major canon, and pocket canon data.
- Added schemas, validation tooling, seal generation, and GitHub Pages workflow.
