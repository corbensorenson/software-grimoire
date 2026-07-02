# Software Grimoire Roadmap

This roadmap turns the three source manuscripts in this workspace into a public
Quarto-powered GitHub repository, a readable online book, a structured reference
system, and eventually a lightweight toolchain for AI-assisted software
spellcraft.

Source documents reviewed:

- `software_magic_grimoire_v3_public_release.docx`: canonical long manuscript,
  about 34k words, 64 rendered pages.
- `pocket_grimoire_software_spellcraft_final.docx`: condensed field edition,
  about 7.9k words, 24 rendered pages.
- `software_spellcraft_addendum_on_stacked_spells.docx`: companion addendum on
  queues, loops, recursive stacks, guards, handoffs, and recovery paths, about
  3.4k words, 12 rendered pages.

Working thesis:

> Software spellcraft is a disciplined language and process for turning human
> intent into bounded, verifiable AI-assisted software work. A spell is a
> structured instruction artifact. A stack is a reusable choreography of spells.
> A rune is a high-force word-sense that compresses engineering judgment into a
> reusable token. The public project should teach the practice, preserve the
> canon, and make the structure executable enough to lint, version, compare, and
> replay.

## 0. Porting and Reader-Experience Status

The grimoire has two completion bars:

1. Content port completeness.
2. Reader-experience completeness.

The content port is complete when every source manuscript has a durable home in
the Quarto project and every reusable structure is represented in data. The
reader experience is complete when a reader can move naturally between theory,
spells, stacks, runes, and examples without manually searching the site.

Current public-site status:

- The long public release is structurally ported into the main book spine,
  public canon, full lexicon data, and generated reference pages.
- The pocket edition is ported into the pocket field guide and 300-rune pocket
  canon.
- The stacked-spells addendum is ported into the Stackcraft chapter, stack
  grammar reference, and six generated stack pages.
- The structured canon includes 18 houses, 1,645 lexicon entries, 50 major canon
  entries, 300 pocket runes, six spell templates, and six stack workflows.
- The repository includes schemas, validation, seal generation, CI, GitHub Pages
  publishing, pull-request checks, contribution templates, examples, and public
  releases.
- The rendered Quarto site currently contains 65 pages, including six
  Proof-by-Difference cases and a dedicated Proof by Difference reference page.
- Important qualification: "ported" means the source material exists in the
  Quarto/data system. It does not mean every lexicon entry has been individually
  authored to final canon quality. The full 1,645-entry lexicon contains many
  category-gloss stubs. The current site marks this honestly: 343 entries are
  authored and 1,302 entries are stubs pending term-specific authoring.

Reader-experience requirements:

- Add a guided reader path that supports theory-first, practice-first, and
  tooling-first routes.
- Add a porting status page so readers can see how source manuscripts map to the
  public site.
- Give every rune a stable anchor of the form `#rune-0001`.
- Link major canon and pocket canon entries into their detailed house entries.
- Add a term index for people who know the word but not the sigil or house.
- Add a canon map for moving from a practical task to the right chapter, spell,
  stack, and rune cluster.
- Add related-page sections to chapters.
- Add related-rune sections to spell pages.
- Add related-spell and related-rune sections to stack pages.
- Keep these links generated from structured data where possible so they do not
  drift from the canon.

Reader-experience acceptance criteria:

- A new reader can start from the home page and choose a clear path.
- A practitioner can start from a task and reach a usable spell or stack in two
  clicks.
- A rune in the major or pocket canon links to its detailed canonical entry.
- Spell pages expose the vocabulary that makes the spell work.
- Stack pages expose the spell templates and vocabulary that support the stack.
- Quarto renders the full site locally and in GitHub Actions.
- The public GitHub Pages site returns HTTP 200 after deployment.

External review findings to absorb into the roadmap:

1. The pipeline and public site are real: GitHub Pages is live, CI deploys, data
   validates, seals generate, and reader cross-links exist.
2. The strongest hand-authored content is the core theory, chapters 1-8, six
   field spells, six stacks, and the major/pocket entry points.
3. The master lexicon had to become honest about completion state. An external
   review found that most entries still carry duplicated category boilerplate,
   most have no failure shadow, and many have no sense disambiguator.
4. Chapters 09 and 10 were too shallow relative to the roadmap promise
   around schema documentation, registry/replay, contribution practice, and
   adoption.
5. Proof by Difference needed to become a real reference section and example
   suite, not only a thesis inside the manuscript.
6. CI needed to run on pull requests and automate the internal-link audit
   performed locally.
7. The next phase should prioritize content integrity before adding new visual
   or mathematical features.

Absorption status:

- Findings 3 through 6 were implemented in `v0.3.0-integrity-evidence-ci`.
- The remaining long-term authoring work is the human-reviewed expansion of
  stub lexicon entries into final canon, starting from the pocket-canon layer.

## 1. End State

The project reaches its logical conclusion when it has all of these properties:

1. Public repository
   - Hosted as `corbensorenson/software-grimoire` or a similarly direct name.
   - Licensed intentionally.
   - Organized so source manuscripts, Quarto pages, generated reference data,
     examples, schemas, and scripts have clear ownership.
   - Easy for a reader to clone, render, inspect, and contribute to.

2. Public Quarto site
   - Published through GitHub Pages.
   - Built from Quarto source, not hand-edited HTML.
   - Uses a book-like spine for the main argument and a website-like reference
     layer for spell templates, stack patterns, lexicon lookup, schemas, and
     examples.
   - Can be rendered locally with `quarto render`.

3. Canonical manuscript
   - The long public release becomes the authoritative book spine.
   - The pocket edition becomes a companion quick-start and downloadable field
     guide.
   - The stacked-spells addendum becomes a formal part of the core system rather
     than an orphan appendix.
   - Repeated material is intentionally deduplicated: theory appears once,
     practice appears in templates/examples, reference material appears in data.

4. Formal vocabulary
   - The 18 lexicon houses and sigil ranges are preserved.
   - The 50 world-running words become expanded canonical entries.
   - The 300 pocket runes become the minimum public working canon.
   - The full 1,645-entry lexicon becomes a structured data file that can
     generate browsable reference pages.

5. Formal spell system
   - The eight-limb spell anatomy is represented in docs, schemas, templates,
     examples, and tests.
   - Cast levels are explicit: quick cast, working cast, full ritual.
   - Spells have human titles, working seals, and optional formal sigils.
   - Verification and failure behavior are treated as first-class fields.

6. Formal stack system
   - Stacks are represented as named, versioned workflows.
   - Stack frames, handoff artifacts, guards, loops, recursive calls, recovery
     paths, and exit rules are captured in structured form.
   - The worked stacks from the addendum become reusable examples and test
     fixtures.

7. Tooling
   - A spell schema validates individual spell files.
   - A stack schema validates multi-step spell choreography.
   - A lexicon schema validates rune entries and sigil ranges.
   - A generator builds Quarto reference pages from structured data.
   - A seal generator produces stable short digests from canonical spell and
     stack streams.
   - Optional later tooling renders clause-circle or stack diagrams.

8. Evidence discipline
   - Every major claim in the theory has examples, counterexamples, and practical
     checks.
   - The project distinguishes metaphor from formal machinery.
   - Examples show weak request, repaired spell, expected output shape, and
     verification behavior.
   - The project avoids selling promptcraft as magic. The metaphor remains a
     handle for operative language, not a substitute for engineering rigor.

9. Community and maintainability
   - Issues and pull requests have templates.
   - Contributions are reviewed against project-specific criteria.
   - New runes, spells, stacks, and examples can be proposed without corrupting
     the core canon.
   - Releases are versioned and changelogged.

## 2. Core Product Shape

The best structure is a hybrid:

- Use the AI-book pattern for the canonical manuscript: a Quarto book with
  numbered chapters, appendices, generated scaffold, and a stable reading order.
- Use the circle-math pattern for public navigation: sidebar sections, reference
  pages, status/roadmap pages, and repo links.
- Keep generated reference pages outside the hand-written manuscript so the
  lexicon can scale without making the reading path unwieldy.

Recommended public title:

> The Grimoire of Software Magic Words

Recommended practical subtitle:

> Operative Vocabulary, Prompt-Spells, and Stackcraft for AI-Assisted Software
> Engineering

Recommended repo name:

> `software-grimoire`

Recommended site URL:

> `https://corbensorenson.github.io/software-grimoire/`

Recommended content promise:

> A public field manual and formal reference for turning vague AI requests into
> bounded, verifiable software work.

## 3. Proposed Repository Layout

```text
software-grimoire/
  README.md
  ROADMAP.md
  LICENSE
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  CHANGELOG.md
  CITATION.cff
  .gitignore
  .nojekyll
  _quarto.yml
  book_structure.json

  index.qmd
  preface.qmd

  chapters/
    01-operative-language.qmd
    02-what-a-spell-is.qmd
    03-crafting-spells.qmd
    04-sigils-canonicalization-and-seals.qmd
    05-coil-inspection.qmd
    06-field-spells.qmd
    07-public-canon.qmd
    08-stackcraft.qmd
    09-tooling-and-formalization.qmd
    10-living-practice.qmd

  reference/
    index.qmd
    cast-levels.qmd
    spell-skeleton.qmd
    stack-grammar.qmd
    lexicon.qmd
    houses.qmd
    seals-and-sigils.qmd
    proof-by-difference.qmd
    failure-modes.qmd

  spells/
    index.qmd
    safe-refactoring.qmd
    bug-diagnosis-from-logs.qmd
    api-design.qmd
    migration-without-data-loss.qmd
    test-generation.qmd
    performance-tuning.qmd

  stacks/
    index.qmd
    code-generation-and-repair-loop.qmd
    bug-hunt-stack.qmd
    safe-refactor-stack.qmd
    live-migration-stack.qmd
    release-gate-stack.qmd
    recursive-decomposition-stack.qmd

  data/
    lexicon.json
    major_arcana.json
    pocket_runes.json
    spells.json
    stacks.json
    houses.json
    seals.json

  schemas/
    lexicon-entry.schema.json
    spell.schema.json
    stack.schema.json
    house.schema.json
    seal.schema.json

  scripts/
    bootstrap_project.py
    sync_scaffold.py
    validate_data.py
    generate_seals.py
    grimoire.py

  assets/
    styles.scss
    diagrams/
    images/
    downloads/

  examples/
    weak-vs-repaired/
    real-world-spells/
    stack-fixtures/
    evaluations/

  source_docs/
    software_magic_grimoire_v3_public_release.docx
    pocket_grimoire_software_spellcraft_final.docx
    software_spellcraft_addendum_on_stacked_spells.docx

  source_extracts/
    README.md

  tests/
    test_internal_links.py
    test_schema_conformance.py
    test_seal_stability.py
    test_validate_data.py
```

The existing workspace already contains `source_extracts/` and
`source_renders/` generated during review. For the public repo, keep
`source_extracts/` only if it is useful as provenance, and keep
`source_renders/` out of version control unless rendered snapshots are
explicitly wanted for editorial QA.

## 4. Content Architecture

### 4.1 Main Book Spine

Part I: Doctrine and Motivation

1. Preface
   - Explain why the project exists.
   - State that this is a practical discipline for operative engineering
     language, not a mystical claim.
   - Define the target reader: software engineers, AI-assisted coding users,
     technical leads, prompt-library maintainers, and tool builders.
   - State the promise: better prompts, better review surfaces, safer AI-driven
     work, and reusable vocabulary.

2. Operative Language
   - Adapt "On the Nature of the Software Magic Word."
   - Keep the three sources of force: semantic density, operational
     addressability, and placement.
   - Keep the five laws: compression, placement, adjacency, invocation surface,
     and shadow.
   - Add examples showing how a word changes behavior in code, prompts, tests,
     migrations, and incident response.

3. What a Spell Is
   - Define a spell as a structured instruction artifact.
   - Distinguish wish, ticket, specification, prompt, spell, program, runbook,
     and agent workflow.
   - Preserve the eight limbs:
     - Role
     - Objective
     - Context
     - Constraints
     - Procedure
     - Output contract
     - Verification
     - Failure behavior
   - Explain why missing limbs create predictable failure modes.

Part II: Practice

4. Cast Levels and Minimum Adequate Ritual
   - Quick cast: role, objective, context, verify.
   - Working cast: role, objective, context, constraints, output, verify.
   - Full ritual: all eight limbs.
   - Add a decision table for choosing a cast level by risk:
     - Low-risk explanation
     - Bounded code edit
     - Test writing
     - Refactor
     - Migration
     - Security review
     - Release or deployment
     - Agentic workflow

5. How to Craft Software Spells
   - Adapt the practical workflow:
     - Name the artifact.
     - State the invariant.
     - State the desired change.
     - Bound the search space.
     - Demand an output shape.
     - Force verification.
     - Decide failure behavior.
   - Expand with before/after examples.
   - Add a "spell repair clinic" that transforms weak prompts into strong
     spells.

6. Prompt Pathologies and Counter-Spells
   - Organize the existing pathologies into a diagnostic guide:
     - Vague target
     - Hidden constraints
     - Missing artifact boundary
     - No output contract
     - No truth test
     - No fallback behavior
     - False certainty
     - Overbroad autonomy
     - Monolithic prompt
     - Gate skipping
   - For each pathology, include:
     - Symptom
     - Likely output failure
     - Repair move
     - Example weak request
     - Example repaired spell

Part III: Formalization

7. Sigils, Seals, and Canonicalization
   - Explain human title, working seal, formal sigil.
   - Keep the canonicalization pipeline:
     - Normalize text.
     - Split by spell limbs.
     - Resolve word-senses.
     - Encode literals.
     - Serialize structure.
     - Assign token IDs.
     - Construct the formal number or digest.
   - Be clear that the Godel-style number is an injective encoding of an agreed
     representation, not a magical fingerprint of pure meaning.
   - Add implementation-friendly pseudocode.
   - Add a JSON/YAML representation of the toy example.

8. Coil Inspection
   - Keep clause circle and antinode concepts.
   - Treat geometry as a review lens.
   - Define useful crossings:
     - Objective x verification
     - Context x constraints
     - Procedure x output
     - Constraints x failure behavior
     - Role x output
   - Add a "manual coil review" checklist.
   - Later, render diagrams from structured spell files.

Part IV: Reusable Forms

9. Six Field Spells
   - Convert the existing six spells into reusable pages:
     - Safe refactoring
     - Bug diagnosis from logs
     - API design
     - Migration without data loss
     - Test generation
     - Performance tuning
   - For each spell, provide:
     - Use case
     - Cast level
     - Full template
     - Adaptation notes
     - Verification notes
     - Failure behavior
     - Example filled version
     - Example expected response shape

10. Proof by Difference
   - Preserve the three cases:
     - Refactor without breaking behavior
     - Online migration without data loss
     - Incident diagnosis without fake certainty
   - Add more cases over time:
     - Security review without theater
     - Performance tuning without micro-optimization drift
     - Test generation without overfitting to implementation
     - API design without hidden compatibility traps
     - Data cleanup without irreversible loss

Part V: Stackcraft

11. Stacked Spells
   - Promote the addendum into a core chapter.
   - Define spell stack, stack frame, handoff artifact, guard, loop, recursion,
     and recovery path.
   - Preserve the formal structure:
     - Entry condition
     - Ordered spells
     - Transition rules
     - Exit condition
     - Recovery map
   - Show how stacks sit above spells and below full engineering campaigns.

12. Stack Grammar and Notation
   - Turn the stack template into a structured grammar.
   - Define operators:
     - `->` for handoff
     - `[guard]` for transition gate
     - `LOOP` for repeated substack
     - `CALL` for recursive descent
     - `ON FAIL` for recovery
   - Add a canonical stream format.
   - Add YAML examples.

13. Worked Spell Stacks
   - Convert the six addendum stacks into standalone pages:
     - Code generation and repair loop
     - Bug-hunt stack
     - Safe refactor stack
     - Live migration stack
     - Release gate stack
     - Recursive decomposition stack
   - For each stack, include:
     - When to use it
     - Required inputs
     - Frames
     - Handoff artifacts
     - Guards
     - Loop rule
     - Failure path
     - Exit condition
     - Example transcript or issue workflow

Part VI: Lexicon and Canon

14. The Public Canon
   - Expand the 50 world-running words into a browsable reference.
   - Each entry should include:
     - Sigil
     - Word-sense
     - House
     - Force description
     - Practical use
     - Shadow or failure mode
     - Related runes
     - Example spell clause

15. The Pocket Canon
   - Preserve the 300 high-force runes as the "minimum working vocabulary."
   - Make it a quick reference page and printable/downloadable field guide.
   - Link each pocket rune to the full lexicon entry when available.

16. The Master Lexicon
   - Convert the full 1,645-entry lexicon into structured data.
   - Generate reference pages from data instead of editing them by hand.
   - Support browsing by:
     - House
     - Sigil range
     - Word
     - Failure shadow
     - Guarantee word
     - AI/promptcraft relevance
     - System domain

Part VII: Tooling and Living Practice

17. Schemas and Validation
   - Introduce the machine-readable project core.
   - Document the schema files.
   - Explain how data validation keeps the public canon from drifting.

18. Prompt Registry and Replay
   - Define how a team could store spells with stable seals.
   - Explain replay across model versions.
   - Add evaluation hooks:
     - Input context
     - Expected output contract
     - Verification commands
     - Model/tool version
     - Result notes

19. Community Use
   - Explain how to contribute new spells, stacks, and runes.
   - Define acceptance criteria.
   - Keep the core canon stable while allowing experimental extensions.

Appendices

- A. Source lineage
- B. Glossary
- C. Spell schema
- D. Stack schema
- E. Lexicon schema
- F. Changelog
- G. Contribution rubric
- H. Release checklist
- I. Quarto publishing notes

## 5. Structured Data Models

### 5.1 Lexicon Entry

Each rune should become a structured record:

```yaml
id: 1461
term: idempotent
sense: general
house: guarantee-words
house_range: "1421-1512"
aliases: []
summary: "Same request, same lasting effect."
force: "Makes retries survivable by bounding repeated effects."
shadow: "Duplicate side effects when retry behavior is not actually stable."
domains:
  - distributed-systems
  - APIs
  - databases
  - payments
prompt_uses:
  - "Require idempotency behavior for retryable write operations."
  - "Ask for duplicate-submission tests."
related:
  - 0576
  - 0943
  - 1152
status: canonical
source: software_magic_grimoire_v3_public_release
```

Required fields:

- `id`
- `term`
- `house`
- `summary`
- `status`
- `source`

Recommended fields:

- `sense`
- `aliases`
- `force`
- `shadow`
- `domains`
- `prompt_uses`
- `related`
- `examples`
- `notes`

Validation rules:

- IDs must be unique.
- IDs must fall inside the declared house range.
- Canonical entries must have a summary.
- Major canon entries should have force and shadow.
- Related IDs must exist.
- House names must match `data/houses.json`.

### 5.2 Spell

Each spell should become a structured record:

```yaml
id: spell.safe-refactoring.v1
title: Spell of Safe Refactoring
version: 1
cast_level: full
status: canonical
use_when: "Code quality must improve without changing externally visible behavior."
role: "Act as a senior engineer performing behavior-preserving refactoring."
objective: "Reduce duplication and improve readability without changing public behavior."
context: []
constraints:
  - "Do not change public function names, parameter order, or return schema."
  - "Do not add third-party dependencies."
procedure:
  - "Identify invariants that must remain true."
  - "List duplication or code-smell candidates."
  - "Propose the minimal refactor."
output_contract:
  - "Short summary"
  - "Invariants"
  - "Unified diff"
  - "Revised code"
  - "Targeted test plan"
verification:
  - "Include edge cases."
  - "State why behavior is preserved."
failure_behavior:
  - "If behavior is ambiguous, name the ambiguity and proceed with the safest minimal change."
runes:
  - 1172
  - 1088
  - 1152
  - 1445
source: software_magic_grimoire_v3_public_release
```

Validation rules:

- Every canonical spell must include title, version, cast level, objective,
  output contract, verification, and failure behavior.
- Full ritual spells must include all eight limbs.
- Working casts may omit procedure and failure behavior only if risk is low.
- Quick casts must still include verification.
- Referenced rune IDs must exist.

### 5.3 Stack

Each stack should become a structured record:

```yaml
id: stack.code-generation-repair-loop.v1
title: Code Generation and Repair Loop
version: 1
status: canonical
enter: "AI-assisted software generation or modification where execution evidence is available."
inputs:
  - "Precise task statement or failing test"
frames:
  - step: 1
    spell: Specify
    cast_level: working
    out: "Precise task statement, constraints, interfaces, and non-goals"
    advance_when: "Target is testable"
  - step: 2
    spell: Draft
    cast_level: working
    out: "Smallest plausible implementation or patch"
    advance_when: "Code compiles in principle and names assumptions"
  - step: 3
    spell: Run
    cast_level: quick
    out: "Build, test, lint, or type-check output"
    advance_when: "Actual failures are captured verbatim"
  - step: 4
    spell: Diagnose
    cast_level: working
    out: "Likely cause and repair surface"
    advance_when: "Diagnosis cites emitted evidence"
  - step: 5
    spell: Repair
    cast_level: working
    out: "Smallest diff addressing the diagnosed cause"
    advance_when: "Patch is explicit"
  - step: 6
    spell: Verify
    cast_level: working
    out: "Check results and residual risk"
    advance_when: "Exit condition holds"
loop:
  steps: [3, 4, 5, 6]
  until: "Checks pass, error surface stabilizes without progress, or attempt budget is exhausted"
on_fail: "Escalate with spec, code diff, failing output, diagnostic notes, and unresolved assumptions"
exit: "Checks pass and residual risk is summarized"
source: software_spellcraft_addendum_on_stacked_spells
```

Validation rules:

- Stack IDs must include a version.
- Every frame must emit an artifact.
- Every meaningful transition must have an advance rule.
- Loops must have an exit condition and attempt budget or stabilization rule.
- Recursive stacks must define a base case.
- Risky stacks must define `on_fail`.

### 5.4 Seal

The project should support three identity layers:

```yaml
human_title: "Safe refactor of account serializer"
working_seal: "spell://safe-refactor/9H4X2Q"
formal_sigil:
  canonical_stream: "ROLE|python-engineer|OBJECTIVE|behavior-preserving-refactor|..."
  digest_algorithm: "sha256-base32-truncated"
  digest: "9H4X2Q"
  godel_vector:
    encoding: "prime-exponent-symbolic"
    tokens: [1, 7, 2, 8, 3, 4, 5, 10, 6, 9]
```

Important principle:

The public project should not require readers to compute formal sigils. Formal
sigils are for tools. Human titles and working seals are for daily practice.

## 6. Roadmap Phases

### Phase 0: Preserve, Inspect, and Decide

Goal:

Create the project baseline without losing source lineage.

Tasks:

1. Initialize Git in the workspace or create a fresh repo directory.
2. Add `.gitignore` that excludes build artifacts:
   - `_site/`
   - `.quarto/`
   - rendered QA images unless intentionally tracked
   - local temporary extraction files
3. Move the three DOCX files into `source_docs/`.
4. Keep generated Markdown extracts in `source_extracts/` only if they are useful
   for provenance. Otherwise regenerate them through scripts.
5. Add `README.md` with:
   - one-paragraph project purpose
   - current status
   - local render instructions
   - link to roadmap
6. Choose license.
7. Choose repo name and public site URL.
8. Decide whether to publish the DOCX sources as public artifacts or preserve
   them as private/editorial lineage only.

Deliverables:

- Git repo initialized.
- Source files preserved.
- Initial README.
- Roadmap committed.
- License chosen.

Definition of done:

- A new contributor can understand what the project is and where the source
  manuscripts came from.

### Phase 1: Quarto Scaffold

Goal:

Create a renderable Quarto site/book skeleton before doing heavy editorial work.

Tasks:

1. Create `_quarto.yml`.
2. Decide project type:
   - Recommended: `project: type: book` for the main spine.
   - Add website-like reference sections through book chapters and appendices.
3. Set title, author, repo URL, site URL, output directory, theme, table of
   contents, and section numbering.
4. Add `assets/styles.scss` with minimal styling.
5. Add `index.qmd`, `preface.qmd`, and placeholder chapters.
6. Add `book_structure.json`.
7. Add `scripts/sync_scaffold.py` to generate `_quarto.yml` from the manifest,
   following the AI-book pattern.
8. Add `quarto render` to the local verification loop.
9. Add `.nojekyll` so GitHub Pages does not treat generated output as a Jekyll
   site.

Deliverables:

- Renderable Quarto project.
- Empty or stubbed book structure.
- Local `_site/` build.

Definition of done:

- `quarto render` completes locally.
- The generated site has navigation, chapter order, and repo links.

### Phase 2: Editorial Canonicalization

Goal:

Turn the DOCX manuscripts into coherent Quarto chapters.

Tasks:

1. Convert the long public release into draft `.qmd` chapters.
2. Remove duplicated title pages, Word-specific formatting, and extract noise.
3. Normalize heading hierarchy.
4. Replace Word image references with assets under `assets/diagrams/`.
5. Convert tables to Markdown or generated Quarto tables.
6. Mark source lineage in comments or front matter.
7. Merge pocket-edition improvements into the main text where they are clearer
   than the long manuscript.
8. Promote the stacked-spells addendum into the core book structure.
9. Split the lexicon out of the reading spine and into generated reference data.
10. Add editorial notes for open questions instead of silently deciding them.

Deliverables:

- Draft Quarto chapters for the main manuscript.
- Extracted diagrams.
- Source-to-chapter mapping.

Definition of done:

- The book can be read front to back without obvious DOCX conversion residue.
- The addendum is integrated into the project architecture.

### Phase 3: Reference System

Goal:

Move from static prose to navigable public reference.

Tasks:

1. Create `data/houses.json` for the 18 lexicon houses.
2. Create `data/major_arcana.json` for the 50 expanded words.
3. Create `data/pocket_runes.json` for the 300 high-force runes.
4. Create `data/lexicon.json` for the full 1,645-entry lexicon.
5. Add validation scripts for ID uniqueness, range membership, and required
   fields.
6. Generate:
   - `reference/houses.qmd`
   - `reference/lexicon.qmd`
   - per-house pages
   - per-major-entry pages if desired
7. Add search-friendly anchors for every rune.
8. Link spells to relevant runes.
9. Link pathologies to corresponding failure runes.
10. Add a short "how to browse the canon" guide.

Deliverables:

- Structured lexicon data.
- Generated reference pages.
- Validation tests.

Definition of done:

- A reader can find a term by house, ID, or concept.
- A script can detect invalid IDs, duplicate entries, and broken references.

### Phase 4: Spell Library

Goal:

Turn the example spells into reusable, structured templates.

Tasks:

1. Create `data/spells.json`.
2. Convert the six field spells into structured records.
3. Generate one page per spell.
4. Include both:
   - human-readable full text
   - structured JSON representation
5. Add blank templates for quick, working, and full casts.
6. Add "fill this in" examples.
7. Add verification patterns by task type:
   - unit tests
   - type checks
   - migration validation queries
   - benchmark checks
   - log evidence
   - security review criteria
8. Add failure behavior examples.
9. Add a spell-review checklist.
10. Add examples that show when a spell is too heavy for the task.

Deliverables:

- Spell library pages.
- Spell schema.
- Spell validation tests.
- User-facing templates.

Definition of done:

- A reader can copy a spell, adapt it, and know how to verify whether it worked.
- A data record can generate the corresponding reference page.

### Phase 5: Stack Library

Goal:

Make stacked spells practical enough to reuse.

Tasks:

1. Create `data/stacks.json`.
2. Convert the addendum's six worked stacks into structured records.
3. Generate one page per stack.
4. Include:
   - use case
   - entry condition
   - required inputs
   - frames
   - artifacts
   - advance rules
   - loop rules
   - failure paths
   - exit condition
5. Add stack diagrams.
6. Add a stack grammar reference.
7. Add examples for:
   - linear stack
   - guarded stack
   - branched stack
   - looped stack
   - recursive stack
   - macro-stack
8. Add validation rules for loops, recursion, and guards.
9. Add an "anti-patterns" page:
   - monolithic relapse
   - invisible handoffs
   - gate skipping
   - spin loops
   - infinite descent
   - process bloat
   - seal drift
10. Add a "choose a stack" decision guide.

Deliverables:

- Stack library pages.
- Stack schema.
- Stack validation tests.
- Generated diagrams.

Definition of done:

- A reader can select a stack for a real software task and understand what
  artifact moves from step to step.

### Phase 6: Formal Tooling

Goal:

Build enough tooling to prove the formalization is real without overbuilding.

Tasks:

1. Implement `scripts/validate_data.py`.
2. Implement `scripts/generate_seals.py`.
3. Implement canonical stream generation for spells:
   - deterministic field order
   - normalized whitespace
   - stable casing policy
   - explicit literal handling
4. Implement canonical stream generation for stacks:
   - stack name
   - version
   - entry condition
   - ordered spell/frame sequence
   - guards
   - loops
   - exit rule
   - recovery path
5. Generate short working seals from a digest.
6. Store seal outputs in generated files or page front matter.
7. Add tests for stable seal generation.
8. Add CLI examples:
   - validate all data
   - generate spell pages
   - generate stack pages
   - generate seals
   - render site
9. Add Makefile or task runner.
10. Add CI to run validation and render checks.

Deliverables:

- Validating scripts.
- Seal generation.
- Tests.
- CI-ready commands.

Definition of done:

- Changing a spell's structured content changes its generated seal.
- Broken data fails validation before publication.

### Phase 7: Diagrams and Visual Grammar

Goal:

Make the coil and stack ideas visually useful.

Tasks:

1. Recover or recreate the existing diagrams from the DOCX sources.
2. Store canonical diagrams in `assets/diagrams/`.
3. Add accessible alt text.
4. Build `render_clause_circle.py`:
   - input: structured spell record
   - output: SVG or PNG clause circle
   - highlight missing sectors
   - highlight selected antinodes
5. Build `render_stack_graph.py`:
   - input: structured stack record
   - output: graph showing frames, guards, loops, and failure path
6. Add diagram examples to the reference pages.
7. Keep diagrams secondary to the text. They should clarify structure, not turn
   the project into decorative mythology.

Deliverables:

- Diagram assets.
- Optional diagram generators.
- Diagram QA checklist.

Definition of done:

- Diagrams help readers find missing obligations, gates, loops, and failure
  behavior.

### Phase 8: Publishing and GitHub Pages

Goal:

Publish the project cleanly and repeatably.

Tasks:

1. Create the GitHub repository.
2. Push the local repo.
3. Configure GitHub Pages for the repo.
4. Use a GitHub Actions workflow to render Quarto and deploy the generated site.
5. Give GitHub Actions the required Pages/deployment permissions.
6. Keep rendered `_site/` out of source control unless choosing a branch-based
   publishing strategy that requires committed output.
7. Add build status badge to README.
8. Add `repo-url`, `repo-actions`, and `site-url` in `_quarto.yml`.
9. Verify the public URL.
10. Add a release tag after the first clean public build.

Recommended workflow direction:

- Prefer GitHub Actions deployment for the public repo.
- Keep generated site output out of the main branch.
- Use Quarto's official GitHub Pages guidance and GitHub's official Pages
  deployment model as the baseline.

Primary publishing references:

- Quarto GitHub Pages documentation:
  <https://quarto.org/docs/publishing/github-pages.html>
- Quarto continuous integration documentation:
  <https://quarto.org/docs/publishing/ci.html>
- GitHub Pages publishing source documentation:
  <https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site>
- GitHub `actions/deploy-pages` action:
  <https://github.com/actions/deploy-pages>

Deliverables:

- Public GitHub repo.
- Live GitHub Pages site.
- CI render/deploy workflow.

Definition of done:

- A push to `main` validates data, renders Quarto, and publishes the site.

### Phase 9: First Public Release

Goal:

Publish a coherent v0.1 that is useful even before all advanced tooling exists.

Minimum v0.1 contents:

1. Home page
2. Preface
3. Operative language chapter
4. What a spell is
5. Cast levels
6. Crafting spells
7. Six field spells
8. Stacked spells
9. 50 world-running words
10. Pocket canon page
11. Roadmap
12. Contribution guide

Release criteria:

- Site renders.
- Navigation works.
- No broken internal links.
- Source lineage is clear.
- Examples are usable.
- License is present.
- README explains local render.
- Roadmap distinguishes current, next, and future work.

Tag:

- `v0.1.0-public-seed`

### Phase 9.5: Reader-Linking Release

Goal:

Make the structurally ported site easy to traverse.

Status:

- Completed as `v0.2.0-reader-links`.

Delivered:

1. Guided reader path.
2. Porting status page.
3. Stable `#rune-NNNN` anchors for all lexicon entries.
4. Term index.
5. Canon map.
6. Major and pocket canon links into detailed rune entries.
7. Related-rune sections on spell pages.
8. Related-spell and related-rune sections on stack pages.
9. Related-page sections on core chapters.
10. Validation for rune anchors, spell rune references, stack rune references,
    and stack related-spell references.

Remaining risk:

- Reader navigation is now strong. The v0.3 integrity layer also prevents the
  reference layer from implying that every lexicon entry is authored canon.

### Phase 9.6: Lexicon Honesty and Content Integrity

Status:

- Integrity layer completed as part of `v0.3.0-integrity-evidence-ci`.
- The site now reports 343 authored entries and 1,302 stub entries.
- Major and pocket entries are authored from their source-canon glosses.
- Remaining full-lexicon stubs are explicitly marked for future authoring.
- Long-term human review of the full 1,645-entry canon remains v1.0 work.

Goal:

Make the public site truthful about which lexicon entries are authored and which
are stubs, then start the authoring campaign with the 300-rune pocket canon.

Tasks:

1. Add a `completion_status` field to every lexicon entry:
   - `authored`: unique, term-specific operative definition.
   - `stub`: duplicated or generic category gloss.
   - `needs_shadow`: term-specific definition exists but failure shadow is
     missing.
   - `needs_sense`: overloaded term lacks a useful sense disambiguator.
2. Detect obvious stubs programmatically:
   - Count duplicated summaries.
   - Mark shared boilerplate summaries as `stub`.
   - Preserve already-authored entries as `authored`.
3. Extend schemas and validation:
   - Require `completion_status`.
   - Require `shadow` for `authored` entries where feasible.
   - Validate that major canon entries are authored.
   - Validate that pocket canon entries are either authored or explicitly listed
     in the pocket authoring backlog.
4. Update generated pages:
   - Show authored/stub counts globally and per house.
   - Show a completion summary on `porting-status.qmd`.
   - Show completion status in `reference/lexicon.qmd`.
   - Style stub rows and stub detail blocks visibly but soberly.
   - Avoid claiming the master lexicon is complete authored canon until the
     counts support that claim.
5. Create a pocket-canon authoring tracker:
   - Group the 300 pocket runes by house.
   - Track authored, stub, missing-shadow, and missing-sense counts.
   - Review whole houses at a time rather than random individual entries.
6. Author the 300 pocket runes first:
   - Write unique summaries specific to each term.
   - Add a failure shadow.
   - Add sense disambiguation for overloaded terms.
   - Preserve existing sigil IDs.
   - Treat generated drafts as candidates until reviewed.
7. Add a human review gate:
   - Pocket entries should not move to `authored` merely because text was
     generated.
   - Review for technical accuracy, operational usefulness, and voice.

Definition of done:

- The site shows honest completion counts.
- Stub entries are visually distinct.
- No page implies that generic boilerplate entries are finished canon.
- The 50 major canon entries are authored.
- The 300 pocket runes have a clear authoring backlog and at least one complete
  house has been reviewed.

Recommended release:

- Shipped inside `v0.3.0-integrity-evidence-ci`.

### Phase 9.7: Proof by Difference and Evidence Layer

Status:

- Completed as part of `v0.3.0-integrity-evidence-ci`.
- Added one weak-vs-repaired case per field spell.
- Added a replayable evaluation template and six-case field-spell evaluation
  matrix under `examples/evaluations/`.

Goal:

Demonstrate the grimoire's core claim with visible before/after cases.

Tasks:

1. Create `reference/proof-by-difference.qmd`.
2. Define the method:
   - Same task.
   - Weak request.
   - Repaired spell.
   - Observable delta.
   - Verification rubric.
3. Create one weak-vs-repaired example per field spell:
   - Safe refactoring.
   - Bug diagnosis from logs.
   - API design.
   - Migration without data loss.
   - Test generation.
   - Performance tuning.
4. Link each spell page to its proof-by-difference case.
5. Expand `examples/evaluations/` beyond a placeholder:
   - Store input context.
   - Expected output contract.
   - Scoring rubric.
   - Result notes.
6. Add the proof page to `_quarto.yml` and the reference index.

Definition of done:

- A reader can see why the spell structure matters without trusting the thesis
  on assertion.
- Every field spell has at least one concrete weak-vs-repaired case.
- Evaluation examples can be replayed across model/tool versions.

Recommended release:

- Shipped inside `v0.3.0-integrity-evidence-ci`.

### Phase 9.8: Editorial Depth for Tooling and Living Practice

Status:

- Completed as part of `v0.3.0-integrity-evidence-ci`.
- Chapters 09 and 10 now explain schema responsibilities, validation,
  registry/replay, seal behavior, evaluation logs, solo practice, team registry
  use, contribution standards, adoption ladder, and canon governance.

Goal:

Bring chapters 09 and 10 up to the depth of the core chapters.

Tasks:

1. Expand `chapters/09-tooling-and-formalization.qmd`:
   - Schema responsibilities.
   - Required fields for houses, lexicon entries, spells, stacks, and seals.
   - How validation prevents canon drift.
   - How canonical streams are formed.
   - How working seals are computed.
   - What causes seal changes.
   - Prompt registry design.
   - Replay across model versions.
   - Evaluation and audit logs.
2. Expand `chapters/10-living-practice.qmd`:
   - Solo use.
   - Team prompt registry.
   - Code-review and incident-response workflows.
   - Contribution flow.
   - Canon change policy.
   - How to keep metaphor subordinate to engineering.
   - Adoption ladder from copy/paste templates to validated registry.

Definition of done:

- Chapters 09 and 10 no longer read as placeholders.
- The tooling chapter explains the actual repo implementation.
- The living-practice chapter gives a team a credible adoption path.

Recommended release:

- Shipped inside `v0.3.0-integrity-evidence-ci`.

### Phase 9.9: CI and Test Hardening

Status:

- Completed as part of `v0.3.0-integrity-evidence-ci`.
- Added PR/non-main check workflow.
- Added schema-conformance, seal-stability, validation, and rendered
  internal-link tests.
- Pages publishing now runs pytest before deployment.

Goal:

Make the repository safer for contributors.

Tasks:

1. Add `.github/workflows/check.yml`:
   - Run on `pull_request`.
   - Run on pushes to non-main branches.
   - Generate data/pages.
   - Validate data.
   - Run tests.
   - Render Quarto.
   - Do not deploy.
2. Add tests:
   - Seal stability for at least one known spell and one known stack.
   - Schema conformance for all generated data files.
   - Internal-link and anchor audit over rendered `_site` HTML.
   - Required `#rune-NNNN` anchors.
3. Add `pytest` to the existing Pages publish workflow.
4. Add a build/status badge to the README.
5. Keep deployment restricted to `main`.

Definition of done:

- Pull requests cannot break generation, validation, tests, render, or internal
  links without failing CI.
- Seal canonicalization changes fail loudly and require changelog notes.

Recommended release:

- Shipped inside `v0.3.0-integrity-evidence-ci`.

### Phase 9.10: Repository Hygiene

Status:

- Completed as part of `v0.3.0-integrity-evidence-ci`.
- Removed the empty `appendices/` directory from the working tree.
- Removed the stale duplicate `examples/weak-vs-repaired/refactor.md`.
- README now states MIT plainly, exposes badges, and reports the current
  65-page render size.

Goal:

Remove ambiguity and dead scaffolding.

Tasks:

1. Delete empty directories such as `appendices/` until they contain content.
2. State the license plainly in README: MIT.
3. Keep `CHANGELOG.md` aligned with each release.
4. Keep source manuscripts and extracts clearly marked as source lineage.
5. Avoid hand-editing generated QMD pages; edit data and generators instead.

Definition of done:

- Repository state matches public claims.
- New contributors can tell which files are source, generated, and review
  artifacts.

### Phase 10: Canonical v1.0

Goal:

Ship the first stable public canon.

Required v1.0 contents:

1. Complete edited book spine.
2. Integrated stackcraft chapter.
3. Structured 50-entry major canon.
4. Authored 300-entry pocket canon with shadows and sense disambiguation where
   needed.
5. Structured full lexicon with honest completion status for every entry:
   authored, stub, needs-shadow, or needs-sense.
6. Spell schema.
7. Stack schema.
8. Generated spell pages.
9. Generated stack pages.
10. Validation scripts.
11. CI render and validation.
12. Contribution policy.
13. Changelog.

v1.0 quality bar:

- The public theory is coherent.
- The metaphor is disciplined.
- The examples are practical.
- The formal structures validate.
- The site is easy to navigate.
- The generated reference does not drown the reader.
- The master lexicon does not overclaim completion.
- The pocket canon is genuinely usable as a minimum working vocabulary.
- Proof by Difference exists as a real evidence layer.
- Pull requests run generation, validation, tests, render, and internal-link
  checks before merge.
- The project is useful even to someone who ignores the metaphysical flavor and
  just wants better AI-assisted engineering workflows.

Tag:

- `v1.0.0-canonical-field-release`

### Phase 11: Tooling v1

Goal:

Make the grimoire executable as a small local toolkit.

Possible package:

- Python package name: `software-grimoire`
- CLI name: `grimoire`

Commands:

```text
grimoire validate
grimoire spell lint path/to/spell.json
grimoire spell seal path/to/spell.json
grimoire stack lint path/to/stack.json
grimoire stack seal path/to/stack.json
grimoire render reference
grimoire render coil path/to/spell.json
grimoire render stack path/to/stack.json
```

Tooling principles:

- Keep the CLI boring.
- Validate structure before inventing features.
- Make output diffable.
- Avoid model-specific dependencies in the core.
- Treat AI integrations as adapters, not as the heart of the project.

Definition of done:

- A user can define a spell or stack in JSON, validate it, generate a seal, and
  render a readable page.

### Phase 12: Evaluation and Replay

Goal:

Prove that stronger spell structure improves work quality in observable ways.

Tasks:

1. Create benchmark tasks:
   - refactor
   - bug diagnosis
   - API design
   - migration plan
   - test generation
   - performance tuning
2. For each task, store:
   - weak request
   - repaired spell
   - input context
   - expected output contract
   - verification rubric
   - model/tool version
   - result
3. Define metrics:
   - instruction adherence
   - artifact completeness
   - verification quality
   - hallucinated assumptions
   - blast-radius control
   - reversibility
   - reviewer effort
4. Add result pages.
5. Repeat periodically across model versions.

Definition of done:

- The project can show concrete deltas, not just assert that structure helps.

### Phase 13: Community Extension System

Goal:

Let the canon grow without becoming incoherent.

Contribution types:

- New rune
- Rune correction
- New spell
- New stack
- New proof-by-difference case
- New pathology
- New diagram
- New tool adapter

Required proposal fields:

- Motivation
- Source or example
- Affected house or domain
- Failure shadow
- Verification method
- Compatibility with existing canon
- Suggested status:
  - experimental
  - candidate
  - canonical
  - deprecated

Review rules:

- Canonical entries need examples.
- New runes need a distinct word-sense, not just a synonym.
- New spells need output contracts and verification.
- New stacks need concrete handoff artifacts and exit rules.
- Metaphor cannot substitute for technical content.

Definition of done:

- Contributions improve the reference instead of turning it into an unbounded
  prompt dump.

## 7. Project Governance

### Status Labels

Use simple statuses across data files and pages:

- `draft`: incomplete or actively changing
- `candidate`: coherent but not stable
- `canonical`: accepted into the stable public canon
- `experimental`: useful but speculative
- `deprecated`: preserved for history but not recommended

### Versioning

Use semantic versioning for the public project:

- Patch: typos, broken links, small wording fixes, data corrections.
- Minor: new spells, stacks, generated pages, examples, non-breaking schema
  additions.
- Major: schema changes, canon reorganizations, renamed IDs, incompatible seal
  logic.

### Changelog Sections

Recommended sections:

- Added
- Changed
- Fixed
- Deprecated
- Removed
- Security
- Canon changes
- Schema changes

### Canon Change Policy

Canon changes should be intentional:

- Do not renumber existing runes casually.
- Do not change a canonical spell's meaning without versioning it.
- Do not change stack frame order without changing the stack version.
- Preserve old seals when possible.
- If a seal changes, explain why.

## 8. Editorial Principles

1. Metaphor is allowed only when it improves operational clarity.
2. Every strong claim should eventually be paired with an example.
3. Every example should name what is being verified.
4. A spell without an output contract is not yet ready for public template use.
5. A stack without handoff artifacts is just a named checklist.
6. A loop without an exit condition is not a workflow; it is drift.
7. A recursive stack without a base case is not recursion.
8. A lexicon entry without a failure shadow is incomplete for engineering use.
9. Structured data should generate reference pages where possible.
10. Human-readable prose remains the primary interface; schemas support it.

## 9. Initial Backlog

High priority:

- Create Quarto scaffold.
- Move DOCX files into `source_docs/`.
- Convert long manuscript to draft chapters.
- Integrate stacked-spells addendum.
- Create README and license.
- Create GitHub Pages workflow.

Medium priority:

- Extract the 50 world-running words into `data/major_arcana.json`.
- Extract the six field spells into `data/spells.json`.
- Extract the six worked stacks into `data/stacks.json`.
- Add schemas for spells and stacks.
- Add validation script.
- Generate spell and stack pages.

Lower priority:

- Full 1,645-entry lexicon extraction.
- Seal generator.
- Clause-circle renderer.
- Stack graph renderer.
- Evaluation harness.
- CLI packaging.

## 10. Suggested First Sprint

The first sprint should create a useful public skeleton without getting trapped
in total formalization.

Sprint goal:

> A renderable Quarto repo with the core thesis, initial chapters, source
> lineage, six spell templates, stacked-spells chapter, and a live roadmap.

Tasks:

1. Initialize Git.
2. Add `.gitignore`.
3. Add Quarto skeleton.
4. Add README.
5. Add license.
6. Move source DOCX files.
7. Convert title/preface and first three chapters.
8. Convert stacked-spells addendum into one chapter.
9. Convert six field spells into `spells/*.qmd`.
10. Add roadmap page.
11. Run `quarto render`.
12. Fix navigation and broken links.
13. Push to GitHub.
14. Enable GitHub Pages.
15. Add GitHub Actions publish workflow.

Sprint deliverable:

- A public work-in-progress site that already communicates the project and gives
  readers usable templates.

## 11. Suggested Second Sprint

Sprint goal:

> Turn prose examples into a structured reference system.

Tasks:

1. Define spell schema.
2. Define stack schema.
3. Create `data/spells.json`.
4. Create `data/stacks.json`.
5. Build page generators.
6. Add validation.
7. Add tests.
8. Convert the 50 world-running words into structured data.
9. Generate major-canon reference pages.
10. Add cross-links from chapters to reference entries.

Sprint deliverable:

- A site where the key spells, stacks, and canon entries are generated from data
  and validated in CI.

## 12. Suggested Third Sprint

Sprint goal:

> Build the pocket field guide and prepare v0.1.

Tasks:

1. Convert pocket edition into a concise quick-start.
2. Create `reference/cast-levels.qmd`.
3. Create `reference/spell-skeleton.qmd`.
4. Create `reference/stack-grammar.qmd`.
5. Create `reference/proof-by-difference.qmd`.
6. Add printable/downloadable pocket guide if desired.
7. Add contribution guide.
8. Add changelog.
9. Add release checklist.
10. Tag v0.1.

Sprint deliverable:

- First public release candidate.

## 13. Risks and Mitigations

Risk: The metaphor overwhelms the engineering value.

Mitigation:

- Keep examples concrete.
- Keep output contracts and verification visible.
- Use plain engineering language beside grimoire terms.

Risk: The lexicon becomes too large to navigate.

Mitigation:

- Separate reading path from reference.
- Generate per-house pages.
- Keep the 50-word and 300-rune canons as smaller entry points.

Risk: The lexicon is structurally complete but semantically under-authored.

Mitigation:

- Track `completion_status` on every rune.
- Surface authored/stub counts publicly.
- Author the 300 pocket runes before treating the master lexicon as final.
- Require shadows and sense disambiguation for authored entries.
- Do not allow generic category boilerplate to masquerade as final canon.

Risk: Formalization becomes too abstract.

Mitigation:

- Prioritize schemas that validate existing useful examples.
- Delay advanced math until basic spell and stack data works.
- Treat Godel-style encoding as optional tooling.

Risk: The site ships as a manuscript but not as a system.

Mitigation:

- Add structured data early.
- Generate at least spell and stack pages from data.
- Add validation before v1.0.

Risk: Contribution quality becomes uneven.

Mitigation:

- Use templates.
- Require verification and failure behavior.
- Keep statuses explicit.

Risk: Seal stability creates maintenance burden.

Mitigation:

- Version spells and stacks.
- Document seal algorithms.
- Treat seal changes as changelog-worthy.

## 14. Acceptance Criteria for "Logical Conclusion"

The project is complete in the strong sense when:

1. The public site teaches the theory clearly.
2. The main book is readable and coherent.
3. The pocket guide is useful as a daily reference.
4. The stacked-spells system is integrated and validated.
5. The lexicon is structured, navigable, and honest about authored vs stub
   entries.
6. The six initial spells are reusable templates.
7. The six initial stacks are reusable workflows.
8. Spells and stacks have schemas.
9. Data validation, tests, render, and internal-link audit run in CI.
10. Quarto publication is automated.
11. Examples demonstrate Proof by Difference for every field spell.
12. The project can accept contributions without losing structure.
13. The project has versioned releases.
14. A user can go from vague request to structured spell to verified result.
15. A team can go from one-off prompt to reusable stack to versioned practice.
16. The 50 major canon entries are authored.
17. The 300 pocket canon entries are authored or explicitly marked as still in
    review.
18. Seal stability is tested and seal changes are documented.

## 15. Immediate Next Move

The highest-leverage next move is now the v1.0 canon-authoring campaign:

1. Review the 343 authored major/pocket entries for technical accuracy, voice,
   and source faithfulness.
2. Promote stub entries house by house only when they have term-specific force,
   shadow, and sense.
3. Add at least one working clause or Proof by Difference reference for newly
   promoted high-force runes.
4. Keep `completion_status` honest after every authoring pass.
5. Treat seal changes, schema changes, and canon promotions as changelog-worthy.

The project has moved past the "make it public and navigable" phase and past the
first integrity hardening pass. The next standard is reviewed canon quality:
every public claim about an authored rune should be technically useful under
real software work.
