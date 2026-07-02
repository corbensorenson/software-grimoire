```json path=handoff.json
{
  "artifact": "release_handoff",
  "version": 1,
  "artifact_boundary": {
    "allowed_output_paths": [
      "handoff.json"
    ],
    "changed_paths": [
      "handoff.json"
    ],
    "out_of_scope_paths_preserved": []
  },
  "scratch": {
    "policy": "repo_local_only",
    "root": ".bench/release-handoff",
    "device_global_paths_used": false
  },
  "tool_allowlist": [
    "git diff -- handoff.json",
    "jq . handoff.json"
  ],
  "network_access": {
    "requested": false,
    "used": false
  },
  "gates": [
    {
      "name": "artifact-boundary",
      "status": "passed",
      "evidence": {
        "changed_paths": [
          "handoff.json"
        ],
        "allowed_output_paths": [
          "handoff.json"
        ]
      }
    },
    {
      "name": "scratch-scope",
      "status": "passed",
      "evidence": {
        "scratch_root": ".bench/release-handoff",
        "repo_local_only": true,
        "device_global_paths_used": false
      }
    },
    {
      "name": "human-approval-claim",
      "status": "passed",
      "evidence": {
        "human_approval_claimed": false,
        "external_approval_claimed": false
      }
    }
  ],
  "human_approval": {
    "claimed": false,
    "status": "not_requested"
  },
  "release_status": "ready_for_review"
}
```
