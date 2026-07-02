# Changelog

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
