# Changelog

## Unreleased

- Updated the roadmap with the post-v3 boundary-hunt direction: Bench v4
  hardness ladder, ward-limb ablations, usage-earned canon review queue,
  package-index preparation, one-step installs, adoption-report generation, and
  evidence-built methods write-up.
- Corrected roadmap phase statuses for the v3 evidence package while keeping
  human canon signoff, public package upload, and external adoption honestly
  pending.
- Added a repo-local `tmp/` scratch directory policy and changed docs/tests so
  project examples do not write to device-global `/tmp`.
- Hardened `scripts/smoke_public_site.py` so report output paths must stay
  inside the repository.
- Moved package checks, execution benches, model-artifact grading, Codex
  adapter output, and CLI/export tests onto repo-local `tmp/` scratch paths.
- Renamed the preserved evaluation metric from structural scoring to
  reviewability scoring across data, generated pages, scripts, schemas, and
  tests while retaining legacy JSON aliases for compatibility.
- Added per-surface and per-tier delta cells to recorded evaluation and surface
  comparison evidence so clean/trap and Codex/Claude results cannot be hidden
  inside aggregate case averages.
- Added the first Bench v4 hardness-ladder seed: ambiguity and
  hidden-invariant executable fixtures, weak/repaired seed artifacts,
  five deterministic repetitions per variant, a schema, CLI/console command,
  CI wiring, smoke coverage, and generated reference/evidence pages.
- Added a standalone adoption-report generator, schema, CLI/console command,
  package smoke coverage, and docs for producing valid report drafts without
  fabricating external adoption.

## v3.0.0-evidence-package

- Added `data/evidence_taxonomy.json` and `data/evidence_index.json` to
  separate calibration fixtures, project-owned model runs, deterministic
  execution, release checks, human-audit pending records, and adoption reports.
- Added shared surface adapters for Codex CLI, Claude Code safe mode, and
  manual imports.
- Recorded real Claude Code safe-mode field-spell runs across clean and trap
  tiers, with preserved prompts/transcripts and tool-version metadata.
- Added model-produced artifact execution for safe-refactoring and
  test-generation, applying extracted artifacts to fixture-local copies and
  running deterministic checks.
- Added real Claude Code baseline-versus-warded adversarial A/B runs across all
  eight defanged jailbreak-resilience fixtures.
- Added evidence browser, calibration, model-artifact execution, warded A/B,
  canon audit, usage-earned canon, and public-smoke-check reference pages.
- Added package build/install checks and public-site smoke checks to the local
  and CI release gates.
- Kept canonical rune promotion honestly gated on human maintainer signoff;
  canonical count remains zero until real signoff occurs.
- Rendered site size is now 107 Quarto pages.

## v2.5.0-roadmap-completion

- Added execution-graded clean/trap bench data, trap-tier fixtures for all six
  field spells, safe-refactoring artifact variants, `scripts/run_execution_bench.py`,
  and generated execution-bench pages/results.
- Added multi-surface comparison records separating project-owned model
  transcripts from repository-owned deterministic graders.
- Added defanged baseline-vs-warded jailbreak-resilience matrix, transcript
  artifacts, generated page, and validation preserving an explicit baseline
  failure without operational payloads.
- Promoted the first two lexicon houses through the semantic review ladder,
  added `data/semantic_promotion.json`, and generated the house review board.
- Added Claude Code skill exports, installer/CLI targets, package bundle,
  manifest/checksum coverage, and deterministic generation tests.
- Replaced generic diagram labels with data-derived spell and stack labels.
- Added CI execution-bench checks and a release-assets workflow that uploads
  generated bundles, manifest, and checksums to GitHub releases.
- Expanded schemas, validation, and pytest coverage for the new bench,
  semantic-promotion, surface-comparison, baseline, export, and release assets.
- Rendered site size is now 99 Quarto pages.

## v2.1.0-roadmap-completion

- Added semantic canon status for all 1,645 lexicon entries, including
  reviewed/canonical quality gates, prompt-use guidance, examples, and
  generated-template reporting in `data/canon_quality.json`.
- Added Bench v2 contracts: declared surfaces, deterministic check cards,
  manual import template, `scripts/run_bench.py`, and `grimoire bench import`.
- Added Adversarial Harness v2 with local read-only checks for simulated tool
  mediation, retrieval taint, multi-turn scope creep, long-context drift,
  canary redaction, and overrefusal.
- Added package-grade export artifacts: `exports/library-manifest.json`,
  `exports/checksums.sha256`, deterministic release bundles, dry-run-first
  asset installer, and editable Python package metadata.
- Split generator responsibility contracts into `scripts/grimoire_build/` and
  added deterministic generation tests for core data, exports, and bundles.
- Added generated visual review diagrams, visual grammar page, and task chooser
  so users can move from real work to a spell, stack, and verification path.
- Added adoption evidence scaffolding with project-owned dogfood reports,
  external/reviewer provenance policy, adoption report template, and GitHub
  issue templates for adoption evidence and canon corrections.
- Hardened CI to run data validation, the adversarial harness, bench import
  validation, Quarto render, and pytest before publishing.
- Rendered site size is now 95 Quarto pages.

## v1.4.0-jailbreak-resilience

- Added a defensive adversarial-promptcraft chapter covering jailbreaks,
  prompt injection, system-prompt leakage, tool hijacking, many-shot drift, and
  overrefusal without publishing operational bypass prompts.
- Added `reference/jailbreak-resilience.qmd` with a safe source map for Pliny,
  OWASP, NCSC, Microsoft, Anthropic, Promptfoo, and MITRE ATLAS references.
- Added canonical `spell.jailbreak-resilience-review.v1` with warded-spell
  fields: trust boundary, untrusted inputs, allowed tools, forbidden outputs,
  secret handling, refusal contract, and audit log.
- Added canonical `stack.ai-red-team-loop.v1` for fixture-based defensive
  red-team work.
- Added `data/jailbreak_resilience.json` and `schemas/jailbreak-case.schema.json`.
- Added eight harmless jailbreak-resilience fixtures covering indirect README
  injection, tainted logs, RAG chunk override, system-prompt leak requests,
  multi-turn scope creep, many-shot policy drift, forbidden tool calls, and
  canary leakage.
- Added `scripts/run_jailbreak_resilience.py` and recorded 24 Codex-owned
  defensive bench runs with attack-resistance, utility-preservation, and
  audit-quality scoring.
- Added generated jailbreak-resilience bench pages and installable exports for
  the new defensive spell and stack.
- Hardened validation and tests for warded fields, fixture integrity, preserved
  transcripts, and canary non-leakage.
- Rendered site size is now 89 Quarto pages.

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
