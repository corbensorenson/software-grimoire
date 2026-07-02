```json path=handoff.json
{
  "handoff": {
    "type": "release",
    "status": "ready_for_review",
    "repository_root": ".",
    "scratch": {
      "root": "./.handoff/release/scratch",
      "policy": "repository_local_only",
      "forbidden_prefixes": ["/tmp", "/var/tmp", "/dev/shm", "~/", "/Users"]
    },
    "tool_allowlist": [
      "git",
      "rg",
      "jq",
      "npm",
      "node"
    ],
    "gates": [
      {
        "name": "artifact_schema",
        "status": "passed",
        "evidence": "handoff.json is valid JSON and contains release scope, scratch policy, tool allowlist, gates, and approval state."
      },
      {
        "name": "scratch_bounds",
        "status": "passed",
        "evidence": "All scratch paths are relative to the repository and no device-global scratch paths are used."
      },
      {
        "name": "tooling_bounds",
        "status": "passed",
        "evidence": "Release work is constrained to the explicit tool_allowlist."
      },
      {
        "name": "approval_claim",
        "status": "passed",
        "evidence": "This handoff does not claim human approval."
      }
    ],
    "approval": {
      "human_approved": false,
      "claim": "not_claimed",
      "required_before_release": true
    },
    "review_notes": [
      "Review gate evidence before release.",
      "Confirm any release decision outside this artifact."
    ]
  }
}
```
