# Code Generation and Repair Loop

- id: `stack.code-generation-and-repair-loop.v1`
- version: `1`
- working seal: `stack://code-generation-and-repair-loop/DBD637DB96`
- enter: Use when an AI system is helping write or modify software and generation should stay tied to execution evidence.

## Frames

### 1. Specify

- artifact: Precise task statement, constraints, interfaces, and non-goals
- advance when: The target is testable

### 2. Draft

- artifact: Smallest plausible implementation or patch
- advance when: The code compiles in principle and names assumptions

### 3. Run

- artifact: Build, test, lint, or type-check output
- advance when: Actual failures are captured verbatim

### 4. Diagnose

- artifact: Likely cause and repair surface
- advance when: The diagnosis uses only emitted evidence

### 5. Repair

- artifact: Smallest diff addressing the diagnosed cause
- advance when: The patch is explicit

### 6. Verify

- artifact: Check results and residual risk
- advance when: Checks pass or residual risk is clearly bounded

## Failure Behavior

Escalate with spec, code diff, failing output, diagnostic notes, and unresolved assumptions.

## Exit

Checks pass or residual risk is clearly bounded
