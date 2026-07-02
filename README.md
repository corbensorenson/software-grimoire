# The Grimoire of Software Magic Words

[![Check Quarto Site](https://github.com/corbensorenson/software-grimoire/actions/workflows/check.yml/badge.svg)](https://github.com/corbensorenson/software-grimoire/actions/workflows/check.yml)
[![Publish Quarto Site](https://github.com/corbensorenson/software-grimoire/actions/workflows/publish.yml/badge.svg)](https://github.com/corbensorenson/software-grimoire/actions/workflows/publish.yml)

Operative vocabulary, prompt-spells, and stackcraft for AI-assisted software
engineering.

This repository is the v3.0 evidence-package release of the Software
Grimoire: a public Quarto site, structured reference canon, reusable spell and
stack templates, measured evaluation bench, jailbreak-resilience harness,
installable prompt/rule exports, package manifests, visual review instruments,
and local validation tooling. The core claim is practical: better language
produces better software work when it names the artifact, invariant, output
contract, verification method, failure behavior, and trust boundary clearly
enough to inspect.

## Current Status

This is the public v3.0 release generated from the three source DOCX
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
  1,645 unique summaries, 1,645 unique shadows, overloaded terms with real
  senses, and explicit semantic status.
- Canon-quality report for authored summaries, semantic review status,
  generated-template counts, shadows, sense disambiguators, overloaded terms,
  reviewed major-canon shadows, prompt-use guidance, and examples.
- Stable rune anchors, term index, canon map, and generated cross-links between
  chapters, spells, stacks, and lexicon entries.
- Generated spell, stack, Proof by Difference, recorded evaluation, adoption,
  visual grammar, task chooser, and reference pages.
- Bench v2 surface contract, deterministic scoring notes, manual import
  template, and `grimoire bench import` validation.
- Execution-graded clean/trap bench contract, trap-tier fixtures for all six
  field spells, and runnable artifact grading for the safe-refactoring fixture.
- Surface comparison records that separate project-owned model transcripts from
  repository-owned deterministic graders.
- Codex-owned measured weak-vs-repaired evaluation runs for all six field
  spells across clean and trap tiers: executable fixtures, planted ground
  truth, outcome scores, reviewability scores, and three repetitions per
  variant where the surface matrix is complete.
- Defensive jailbreak-resilience layer: adversarial promptcraft chapter,
  source-mapped reference page, warded spell fields, AI red-team loop, eight
  harmless fixtures, and 24 preserved Codex-owned bench runs.
- Baseline-vs-warded jailbreak-resilience matrix using defanged fixtures on
  Claude Code safe mode and Codex CLI default surfaces, with preserved prompts,
  redacted transcripts, three repetitions per case/variant/surface cell, and
  an explicit project-owned evidence limitation.
- Ward-science seed with deterministic limb ablation over a defanged indirect
  injection shape, resistance/utility/audit/overrefusal scoring, and six
  additional defanged attack-shape designs.
- Adversarial harness v2 for simulated tool mediation, retrieval taint,
  multi-turn scope creep, long-context drift, canary redaction, and overrefusal.
- Semantic promotion ladder for moving generated-draft vocabulary into reviewed
  and canonical status, with the first two lexicon houses fully reviewed.
- Raw prompt assets in `prompts/` for the seven spells and seven stack
  workflows.
- Installable generated exports in `exports/` for Markdown, Codex task
  templates, Cursor rules, Claude Code skills, and stack workflows, with
  library manifest, checksums, release bundles, and a dry-run-first installer.
- Python packaging metadata for editable local use of `grimoire`,
  `grimoire-install-assets`, `grimoire-run-bench`,
  `grimoire-run-execution-bench`, and
  `grimoire-run-adversarial-harness`.
- Release-gate stack dogfood record tied to the public GitHub Pages workflow.
- Project-owned adoption evidence records, adoption report template, and public
  GitHub issue templates for adoption evidence and canon corrections.
- Standalone adoption-report generator for schema-valid project-owned,
  reviewer-supplied, or external-user report drafts without automatically
  counting them as external adoption.
- Adoption intake decision template, validator, and CLI route for accepting
  and publishing future non-maintainer reports without counting pending drafts
  as external adoption.
- Evidence taxonomy, calibration separation, real Claude Code second-surface
  runs, model-produced artifact execution, real cross-surface warded A/B runs,
  evidence browser pages, public smoke checks, package install checks, and
  usage-earned canon audit records.
- Package-index release plan for TestPyPI/PyPI human upload, with preflight,
  build, upload, post-upload, package-index smoke tooling, and
  evidence-recording instructions that keep public package availability pending
  until a maintainer performs it.
- Manual GitHub Actions package publish workflow using PyPI Trusted Publishing
  and post-upload smoke artifacts; public package-index availability still
  remains pending until a named maintainer dispatches it and records the smoke.
- Bench v4 seed hardness ladder with ambiguity, hidden-invariant,
  misleading-context, blast-radius, and agentic executable fixtures,
  weak/repaired seed artifacts, five deterministic repetitions per variant,
  and a generated reference page.
- Bench v4 Codex model-surface hardness ledger with 50 preserved runs across
  all five rungs, hidden-grader execution outcomes, extracted artifacts, and
  an explicit null-heavy result: weak and repaired artifacts each passed 1/25
  checks.
- Bench v4 manual hardness-import validator for reviewer-supplied or
  non-Codex surface bundles, including schema checks, repo-local path checks,
  artifact filename checks, provenance consistency, and fixture-local execution
  without automatically publishing the run.
- Bench v4 hardness intake decision template, validator, CLI route, and issue
  form for accepting future non-Codex or reviewer-supplied hardness bundles
  without counting pending templates as cross-surface evidence.
- Logical-conclusion status ledger for all 90 roadmap acceptance criteria,
  with evidence links and explicit blockers for human canon signoff, public
  package-index upload, non-maintainer adoption, and non-Codex/reviewer
  hardness evidence.
- Canon-audit decision template, public issue form, validator, and CLI route
  for recording future named maintainer signoff without treating pending
  templates as human evidence.
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
python3 scripts/grimoire.py new spell tmp/my-spell.json
python3 scripts/grimoire.py validate tmp/my-spell.json
python3 scripts/grimoire.py seal tmp/my-spell.json
python3 scripts/grimoire.py export --target cursor
python3 scripts/grimoire.py export --target claude-code
python3 scripts/grimoire.py bench execution
python3 scripts/grimoire.py bench hardness
python3 scripts/grimoire.py bench hardness-model -- --surface codex-cli-default --repetitions 5 --append
python3 scripts/grimoire.py bench import examples/evaluations/manual-import-template.json
python3 scripts/grimoire.py bench hardness-import examples/evaluations/hardness-v4/manual-import-template.json
python3 scripts/grimoire.py bench hardness-decision examples/evaluations/hardness-v4/hardness-intake-decision-template.json
python3 scripts/grimoire.py canon decision examples/canon/canon-audit-decision-template.json
python3 scripts/grimoire.py adoption decision examples/adoption/adoption-intake-decision-template.json
python3 scripts/grimoire.py adoption report -- --id adoption.example-review.v1 --title "Example Review" --provenance reviewer-supplied --task "Describe the real task." --spell-or-stack-used spell.safe-refactoring.v1 --surface "Reviewer workflow" --artifact-produced "Patch or review artifact." --verification-performed "Tests or review checks." --time-cost "Low" --failure-or-friction "Record friction honestly." --reuse-decision reuse --write-report tmp/adoption-report.json
python3 scripts/check_package_publish_workflow.py
python3 scripts/grimoire.py install --target cursor --dest tmp/grimoire-assets
python3 scripts/grimoire.py install --target claude-code --dest tmp/grimoire-assets --write
python3 scripts/install_assets.py --target cursor --dest tmp/grimoire-assets
python3 scripts/install_assets.py --target claude-code --dest tmp/grimoire-assets
python3 scripts/install_assets.py --target cursor --dest tmp/grimoire-assets --write
python3 scripts/grimoire.py all
```

The generated site is written to `_site/`.
Repo-local scratch files should go under `tmp/`, which is ignored except for
`tmp/.gitkeep`.

Current render size: 112 Quarto pages.

## Repository Map

- `chapters/`: main book spine.
- `reference/`: generated and hand-authored reference pages.
- `spells/`: reusable spell templates.
- `stacks/`: reusable stack workflows.
- `prompts/`: raw spell and stack assets for use in AI tools and prompt
  registries.
- `exports/`: generated installable Markdown, Codex, Cursor, Claude Code, and
  stack assets.
- `assets/diagrams/generated/`: generated visual review diagrams.
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
