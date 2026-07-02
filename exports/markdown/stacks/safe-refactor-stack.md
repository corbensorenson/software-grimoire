# Safe Refactor Stack

- id: `stack.safe-refactor-stack.v1`
- version: `1`
- working seal: `stack://safe-refactor-stack/E351AC61F4`
- enter: Use when structure must improve without changing externally visible behavior.

## Frames

### 1. Freeze invariants

- artifact: Behavior and data contracts
- advance when: What must not change is named

### 2. Characterize

- artifact: Tests or characterization evidence
- advance when: Current behavior is pinned

### 3. Reshape

- artifact: Structural patch
- advance when: Structure improves without intentional behavior change

### 4. Static verify

- artifact: Type, lint, and architecture check output
- advance when: Static checks pass

### 5. Behavior verify

- artifact: Characterization test output
- advance when: Behavior evidence stays green

### 6. Review

- artifact: Human review notes
- advance when: No leaky abstractions, drift, or renamed confusion remain

## Failure Behavior

Revert to the last green state and restate invariants more precisely.

## Exit

No leaky abstractions, drift, or renamed confusion remain
