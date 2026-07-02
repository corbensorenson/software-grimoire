#!/usr/bin/env python3
"""Run Proof by Difference evaluations against local Codex."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from bootstrap_project import EVALUATION_CONTEXTS, PROOF_CASES, ROOT


SURFACES = {
    "codex-cli-default": {
        "kind": "codex",
        "label": "Codex CLI default model",
    },
}

CRITERION_KEYWORDS = {
    "artifact_boundary": ["artifact", "module", "file", "endpoint", "table", "boundary", "scope", "function"],
    "invariants": ["invariant", "preserve", "must not", "unchanged", "compatibility", "correctness"],
    "output_contract": ["return", "section", "table", "plan", "format", "output", "checklist"],
    "verification": ["verify", "test", "measure", "check", "query", "evidence", "benchmark", "validate"],
    "failure_behavior": ["if", "fallback", "rollback", "insufficient", "unsafe", "risk", "cannot"],
    "assumption_control": ["assumption", "hypothesis", "unknown", "missing", "evidence", "uncertain", "insufficient"],
}


def build_prompt(slug: str, variant: str) -> str:
    case = PROOF_CASES[slug]
    request = case["weak"] if variant == "weak" else case["repaired"]
    return f"""You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
{EVALUATION_CONTEXTS[slug]}

USER REQUEST:
{request}
"""


def run_codex(prompt: str) -> str:
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        out_path = Path(tmp.name)
    try:
        result = subprocess.run(
            [
                "/Applications/Codex.app/Contents/Resources/codex",
                "exec",
                "--ephemeral",
                "--ignore-rules",
                "-s",
                "read-only",
                "-o",
                str(out_path),
                prompt,
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=240,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout)
        return out_path.read_text(encoding="utf-8").strip()
    finally:
        out_path.unlink(missing_ok=True)


def score_output(text: str) -> dict[str, int]:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for criterion, keywords in CRITERION_KEYWORDS.items():
        hits = sum(1 for keyword in keywords if keyword in lowered)
        scores[criterion] = 2 if hits >= 2 else 1 if hits == 1 else 0
    return scores


def observed_delta(runs: list[dict]) -> str:
    weak = [run["total_score"] for run in runs if run["variant"] == "weak"]
    repaired = [run["total_score"] for run in runs if run["variant"] == "repaired"]
    if not weak or not repaired:
        return "pending"
    weak_avg = sum(weak) / len(weak)
    repaired_avg = sum(repaired) / len(repaired)
    delta = repaired_avg - weak_avg
    if delta > 0:
        return f"repaired prompts scored {delta:.1f} points higher on average"
    if delta < 0:
        return f"weak prompts scored {-delta:.1f} points higher on average"
    return "weak and repaired prompts tied on the structural rubric"


def run_surface(kind: str, prompt: str) -> str:
    if kind == "codex":
        return run_codex(prompt)
    raise ValueError(kind)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", choices=sorted(SURFACES), action="append", help="surface to run; repeatable")
    parser.add_argument("--case", choices=sorted(PROOF_CASES), action="append", help="case to run; repeatable")
    args = parser.parse_args()

    surfaces = args.surface or list(SURFACES)
    slugs = args.case or list(PROOF_CASES)
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "surfaces": {name: SURFACES[name] for name in surfaces},
        "rubric": CRITERION_KEYWORDS,
        "cases": {},
    }

    for slug in slugs:
        case_runs = []
        for surface in surfaces:
            for variant in ["weak", "repaired"]:
                prompt = build_prompt(slug, variant)
                run_dir = ROOT / "examples" / "evaluations" / "runs" / surface / slug
                run_dir.mkdir(parents=True, exist_ok=True)
                prompt_path = run_dir / f"{variant}-prompt.md"
                transcript_path = run_dir / f"{variant}-output.md"
                prompt_path.write_text(prompt, encoding="utf-8")
                print(f"Running {surface} {slug} {variant}...")
                output = run_surface(SURFACES[surface]["kind"], prompt)
                run_timestamp = datetime.now(timezone.utc).isoformat()
                transcript_path.write_text(output + "\n", encoding="utf-8")
                scores = score_output(output)
                case_runs.append(
                    {
                        "surface": surface,
                        "surface_label": SURFACES[surface]["label"],
                        "variant": variant,
                        "run_timestamp": run_timestamp,
                        "prompt_path": str(prompt_path.relative_to(ROOT)),
                        "transcript_path": str(transcript_path.relative_to(ROOT)),
                        "output": output,
                        "scores": scores,
                        "total_score": sum(scores.values()),
                        "evaluator_notes": "Auto-scored with the structural rubric; transcript remains the primary evidence.",
                    }
                )
        results["cases"][slug] = {
            "title": PROOF_CASES[slug]["title"],
            "input_context": EVALUATION_CONTEXTS[slug],
            "expected_delta": PROOF_CASES[slug]["delta"],
            "observed_delta": observed_delta(case_runs),
            "runs": case_runs,
        }

    out = ROOT / "examples" / "evaluations" / "results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
