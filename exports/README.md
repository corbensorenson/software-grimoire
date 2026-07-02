# Installable Software Grimoire Library

These generated files are installable prompt, rule, and workflow assets. Edit canonical spell and stack data, then regenerate; do not hand-maintain exports.

Package metadata lives in [`library-manifest.json`](library-manifest.json), and release bundles live in [`bundles/`](bundles/).

Dry-run an install with `python3 scripts/install_assets.py --target codex --dest /tmp/grimoire-assets`; add `--write` to copy files.

| Target   | Path                                                         | Source                                   | Seal                                               |
| -------- | ------------------------------------------------------------ | ---------------------------------------- | -------------------------------------------------- |
| Markdown | `exports/markdown/spells/safe-refactoring.md`                | spell.safe-refactoring.v1                | spell://safe-refactoring/517A86095D                |
| Codex    | `exports/codex/safe-refactoring.md`                          | spell.safe-refactoring.v1                | spell://safe-refactoring/517A86095D                |
| Cursor   | `exports/cursor/rules/safe-refactoring.mdc`                  | spell.safe-refactoring.v1                | spell://safe-refactoring/517A86095D                |
| Markdown | `exports/markdown/spells/bug-diagnosis-from-logs.md`         | spell.bug-diagnosis-from-logs.v1         | spell://bug-diagnosis-from-logs/2BC4379FD0         |
| Codex    | `exports/codex/bug-diagnosis-from-logs.md`                   | spell.bug-diagnosis-from-logs.v1         | spell://bug-diagnosis-from-logs/2BC4379FD0         |
| Cursor   | `exports/cursor/rules/bug-diagnosis-from-logs.mdc`           | spell.bug-diagnosis-from-logs.v1         | spell://bug-diagnosis-from-logs/2BC4379FD0         |
| Markdown | `exports/markdown/spells/api-design.md`                      | spell.api-design.v1                      | spell://api-design/828C8A1237                      |
| Codex    | `exports/codex/api-design.md`                                | spell.api-design.v1                      | spell://api-design/828C8A1237                      |
| Cursor   | `exports/cursor/rules/api-design.mdc`                        | spell.api-design.v1                      | spell://api-design/828C8A1237                      |
| Markdown | `exports/markdown/spells/migration-without-data-loss.md`     | spell.migration-without-data-loss.v1     | spell://migration-without-data-loss/AD15B25ECB     |
| Codex    | `exports/codex/migration-without-data-loss.md`               | spell.migration-without-data-loss.v1     | spell://migration-without-data-loss/AD15B25ECB     |
| Cursor   | `exports/cursor/rules/migration-without-data-loss.mdc`       | spell.migration-without-data-loss.v1     | spell://migration-without-data-loss/AD15B25ECB     |
| Markdown | `exports/markdown/spells/test-generation.md`                 | spell.test-generation.v1                 | spell://test-generation/16A7DCF9E2                 |
| Codex    | `exports/codex/test-generation.md`                           | spell.test-generation.v1                 | spell://test-generation/16A7DCF9E2                 |
| Cursor   | `exports/cursor/rules/test-generation.mdc`                   | spell.test-generation.v1                 | spell://test-generation/16A7DCF9E2                 |
| Markdown | `exports/markdown/spells/performance-tuning.md`              | spell.performance-tuning.v1              | spell://performance-tuning/75981D9E3F              |
| Codex    | `exports/codex/performance-tuning.md`                        | spell.performance-tuning.v1              | spell://performance-tuning/75981D9E3F              |
| Cursor   | `exports/cursor/rules/performance-tuning.mdc`                | spell.performance-tuning.v1              | spell://performance-tuning/75981D9E3F              |
| Markdown | `exports/markdown/spells/jailbreak-resilience-review.md`     | spell.jailbreak-resilience-review.v1     | spell://jailbreak-resilience-review/36B797783D     |
| Codex    | `exports/codex/jailbreak-resilience-review.md`               | spell.jailbreak-resilience-review.v1     | spell://jailbreak-resilience-review/36B797783D     |
| Cursor   | `exports/cursor/rules/jailbreak-resilience-review.mdc`       | spell.jailbreak-resilience-review.v1     | spell://jailbreak-resilience-review/36B797783D     |
| Markdown | `exports/markdown/stacks/code-generation-and-repair-loop.md` | stack.code-generation-and-repair-loop.v1 | stack://code-generation-and-repair-loop/DBD637DB96 |
| Markdown | `exports/markdown/stacks/bug-hunt-stack.md`                  | stack.bug-hunt-stack.v1                  | stack://bug-hunt-stack/08B5079286                  |
| Markdown | `exports/markdown/stacks/safe-refactor-stack.md`             | stack.safe-refactor-stack.v1             | stack://safe-refactor-stack/E351AC61F4             |
| Markdown | `exports/markdown/stacks/live-migration-stack.md`            | stack.live-migration-stack.v1            | stack://live-migration-stack/23AA56B454            |
| Markdown | `exports/markdown/stacks/release-gate-stack.md`              | stack.release-gate-stack.v1              | stack://release-gate-stack/5798FD1FC7              |
| Markdown | `exports/markdown/stacks/recursive-decomposition-stack.md`   | stack.recursive-decomposition-stack.v1   | stack://recursive-decomposition-stack/9E9D03E9C0   |
| Markdown | `exports/markdown/stacks/ai-red-team-loop.md`                | stack.ai-red-team-loop.v1                | stack://ai-red-team-loop/6CF8F7698D                |
