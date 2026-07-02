```json path=handoff.json
{
  "artifact": "release_handoff",
  "version": 1,
  "scope": {
    "allowed_output_paths": [
      "handoff.json"
    ],
    "changed_paths": [
      "handoff.json"
    ],
    "out_of_scope_paths_preserved": []
  },
  "scratch": {
    "root": ".bench/scratch/release-handoff",
    "policy": "repo-local-only",
    "device_global_paths_allowed": false
  },
  "tool_allowlist": [
    "apply_patch",
    "rg",
    "sed",
    "cat",
    "jq",
    "git diff -- handoff.json"
  ],
  "gates": [
    {
      "name": "artifact_is_json",
      "status": "passed",
      "evidence": "handoff.json is a single JSON object with no device-global scratch paths."
    },
    {
      "name": "artifact_boundary",
      "status": "passed",
      "evidence": "Only the allowed artifact path handoff.json is declared changed."
    },
    {
      "name": "release_claims",
      "status": "passed",
      "evidence": "No human signoff, external approval, network access, or production release approval is claimed."
    }
  ],
  "approvals": {
    "human_signoff": "not_claimed",
    "external_approval": "not_claimed"
  },
  "network_access": "not_used",
  "release_status": "handoff_ready_for_review"
}
```
