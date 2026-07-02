# The Grimoire of Software Magic Words

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
- Manuscript chapters generated from the long public release and stacked-spells
  addendum.
- Structured JSON data for lexicon houses, full 1,645-entry lexicon, 50-entry
  major canon, 300-entry pocket canon, six field spells, and six worked stacks.
- Generated spell, stack, and reference pages.
- JSON schemas and validation tooling.
- Working seal generation for spells and stacks.
- GitHub Pages publishing workflow.

## Local Development

Requirements:

- Quarto
- Python 3.10+

Common commands:

```bash
make generate
make validate
make render
make all
```

The generated site is written to `_site/`.

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

## Public Site

The intended public site URL is:

<https://corbensorenson.github.io/software-grimoire/>

## License

Content and code are released under the MIT License unless a future release
splits code/content licensing more narrowly.

