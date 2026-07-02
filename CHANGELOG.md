# Changelog

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
