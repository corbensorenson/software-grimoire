# The Grimoire of Software Magic Words

[![Check Quarto Site](https://github.com/corbensorenson/software-grimoire/actions/workflows/check.yml/badge.svg)](https://github.com/corbensorenson/software-grimoire/actions/workflows/check.yml)
[![Publish Quarto Site](https://github.com/corbensorenson/software-grimoire/actions/workflows/publish.yml/badge.svg)](https://github.com/corbensorenson/software-grimoire/actions/workflows/publish.yml)

Operative vocabulary, prompt-spells, and stackcraft for AI-assisted software
engineering.

This repository turns the Software Grimoire source manuscripts into a public
Quarto site, structured reference canon, reusable spell and stack templates, and
validation tooling. The core claim is practical: better language produces better
software work when it names the artifact, invariant, output contract,
verification method, and failure behavior clearly enough to inspect.

## Current Status

This is the public-ready project scaffold generated from the three source DOCX
manuscripts in `source_docs/` and their Markdown extracts in
`source_extracts/`.

Implemented:

- Quarto book/site scaffold.
- Guided reader path and porting status pages.
- Manuscript chapters generated from the long public release and stacked-spells
  addendum.
- Structured JSON data for lexicon houses, full 1,645-entry lexicon, 50-entry
  major canon, 300-entry pocket canon, six field spells, and six worked stacks.
- Honest lexicon completion metadata: 343 authored entries and 1,302 marked
  stubs until they receive final term-specific authoring.
- Stable rune anchors, term index, canon map, and generated cross-links between
  chapters, spells, stacks, and lexicon entries.
- Generated spell, stack, Proof by Difference, and reference pages.
- JSON schemas, validation tooling, seal-stability tests, and rendered
  internal-link audit.
- Working seal generation for spells and stacks.
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
python3 scripts/grimoire.py all
```

The generated site is written to `_site/`.

Current render size: 65 Quarto pages.

## Repository Map

- `chapters/`: main book spine.
- `reference/`: generated and hand-authored reference pages.
- `spells/`: reusable spell templates.
- `stacks/`: reusable stack workflows.
- `data/`: structured canon data.
- `schemas/`: JSON schemas for validation.
- `scripts/`: ingestion, generation, validation, and seal tooling.
- `source_docs/`: original DOCX source manuscripts.
- `source_extracts/`: Markdown extracts used by the ingestion pipeline.
- `examples/`: weak-vs-repaired cases and evaluation scaffolds.

## Public Site

The public repository and site are:

- <https://github.com/corbensorenson/software-grimoire>
- <https://corbensorenson.github.io/software-grimoire/>

## License

Released under the MIT License.
