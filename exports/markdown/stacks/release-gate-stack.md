# Release Gate Stack

- id: `stack.release-gate-stack.v1`
- version: `1`
- working seal: `stack://release-gate-stack/5798FD1FC7`
- enter: Use when a change set is already built and the question is whether it is ready to ship.

## Frames

### 1. Assemble candidate

- artifact: Frozen release artifact and config
- advance when: Candidate is exact

### 2. Quality gate

- artifact: Tests, static checks, scans, and prerequisites
- advance when: Quality gate is green

### 3. Stage deploy

- artifact: Staging or canary deployment
- advance when: Limited environment is live

### 4. Observe

- artifact: Metrics, logs, traces, dashboards, and critical-flow results
- advance when: Signals remain green

### 5. Promote or rollback

- artifact: Release decision
- advance when: Broad release happens only if guard remains green

## Failure Behavior

Rollback the candidate and open a repair stack instead of arguing from hope.

## Exit

Broad release happens only if guard remains green
