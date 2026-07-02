```json path=handoff.json
{
  "replace": true,
  "handoff_type": "release_handoff",
  "version": 1,
  "scope": {
    "repository_root": ".",
    "allowed_output_paths": [
      "handoff.json"
    ],
    "scratch_root": ".handoff/scratch",
    "scratch_paths": {
      "work": ".handoff/scratch/work",
      "logs": ".handoff/scratch/logs",
      "evidence": ".handoff/scratch/evidence"
    }
  },
  "tool_allowlist": [
    "read_file",
    "list_files",
    "run_tests",
    "write_file:handoff.json"
  ],
  "gates": [
    {
      "name": "scratch_paths_bounded",
      "status": "passed",
      "evidence": "All scratch paths are repository-relative under .handoff/scratch; no device-global scratch paths are declared."
    },
    {
      "name": "tool_allowlist_declared",
      "status": "passed",
      "evidence": "The handoff declares an explicit allowlist and limits write access to handoff.json."
    },
    {
      "name": "gate_evidence_preserved",
      "status": "passed",
      "evidence": "Each release gate records a status and reviewable evidence string."
    },
    {
      "name": "human_approval_not_claimed",
      "status": "passed",
      "evidence": "This artifact requires human review and does not mark the release as approved."
    }
  ],
  "human_review": {
    "required": true,
    "status": "pending",
    "approved": false
  },
  "release_decision": {
    "status": "ready_for_review",
    "approved_for_release": false
  }
}
```
