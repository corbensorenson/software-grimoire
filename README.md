# The Grimoire of Software Magic Words

[![Check Quarto Site](https://github.com/corbensorenson/software-grimoire/actions/workflows/check.yml/badge.svg)](https://github.com/corbensorenson/software-grimoire/actions/workflows/check.yml)
[![Publish Quarto Site](https://github.com/corbensorenson/software-grimoire/actions/workflows/publish.yml/badge.svg)](https://github.com/corbensorenson/software-grimoire/actions/workflows/publish.yml)

Operative vocabulary, prompt-spells, and stackcraft for AI-assisted software
engineering.

This repository is the v1.4 defensive-roadmap release of the Software Grimoire: a
public Quarto site, structured reference canon, reusable spell and stack
templates, measured evaluation bench, jailbreak-resilience bench, installable
prompt/rule exports, and local validation tooling. The core claim is practical:
better language produces better software work when it names the artifact,
invariant, output contract, verification method, failure behavior, and trust
boundary clearly enough to inspect.

## Current Status

This is the public v1.4 release generated from the three source DOCX
manuscripts in `source_docs/` and their Markdown extracts in
`source_extracts/`.

Implemented:

- Quarto book/site scaffold.
- Guided reader path and porting status pages.
- Manuscript chapters generated from the long public release and stacked-spells
  addendum.
- Structured JSON data for lexicon houses, full 1,645-entry lexicon, 50-entry
  major canon, 300-entry pocket canon, seven canonical spells, seven worked
  stacks, and the jailbreak-resilience source map/case set.
- Full lexicon completion metadata: all 1,645 entries authored, 0 stubs,
  1,645 unique summaries, 1,645 unique shadows, and overloaded terms with real
  senses.
- Canon-quality report for authored summaries, shadows, sense disambiguators,
  overloaded terms, and reviewed major-canon shadows.
- Stable rune anchors, term index, canon map, and generated cross-links between
  chapters, spells, stacks, and lexicon entries.
- Generated spell, stack, Proof by Difference, recorded evaluation, adoption,
  and reference pages.
- Codex-owned measured weak-vs-repaired evaluation runs for all six field
  spells: executable fixtures, planted ground truth, outcome scores, structural
  scores, and three repetitions per variant.
- Defensive jailbreak-resilience layer: adversarial promptcraft chapter,
  source-mapped reference page, warded spell fields, AI red-team loop, eight
  harmless fixtures, and 24 preserved Codex-owned bench runs.
- Raw prompt assets in `prompts/` for the seven spells and seven stack
  workflows.
- Installable generated exports in `exports/` for Markdown, Codex task
  templates, Cursor rules, and stack workflows.
- Release-gate stack dogfood record tied to the public GitHub Pages workflow.
- JSON schemas, validation tooling, seal-stability tests, and rendered
  internal-link audit.
- Working seal generation for spells and stacks, plus a local CLI for
  scaffolding, validating, and sealing local spell files.
- GitHub Pages publishing workflow and pull-request check workflow.

## Local Development

Requirements:

- Quarto
- Python 3.10+

Common commands:

```bash
make generate
make validate
make render
make test
make all
python3 scripts/grimoire.py validate
python3 scripts/grimoire.py seals
python3 scripts/grimoire.py new spell /tmp/my-spell.json
python3 scripts/grimoire.py validate /tmp/my-spell.json
python3 scripts/grimoire.py seal /tmp/my-spell.json
python3 scripts/grimoire.py export --target cursor
python3 scripts/grimoire.py all
```

The generated site is written to `_site/`.

Current render size: 89 Quarto pages.

## Repository Map

- `chapters/`: main book spine.
- `reference/`: generated and hand-authored reference pages.
- `spells/`: reusable spell templates.
- `stacks/`: reusable stack workflows.
- `prompts/`: raw spell and stack assets for use in AI tools and prompt
  registries.
- `exports/`: generated installable Markdown, Codex, Cursor, and stack assets.
- `data/`: structured canon data.
- `schemas/`: JSON schemas for validation.
- `scripts/`: ingestion, generation, validation, and seal tooling.
- `source_docs/`: original DOCX source manuscripts.
- `source_extracts/`: Markdown extracts used by the ingestion pipeline.
- `examples/`: weak-vs-repaired cases, executable fixtures, preserved
  evaluation runs, prompts, transcripts, and release-gate dogfood records.

## Public Site

The public repository and site are:

- <https://github.com/corbensorenson/software-grimoire>
- <https://corbensorenson.github.io/software-grimoire/>

## License

Released under the MIT License.
