# Bug-Hunt Stack

- id: `stack.bug-hunt-stack.v1`
- version: `1`
- working seal: `stack://bug-hunt-stack/08B5079286`
- enter: Use when a defect is real but the cause is not yet localized.

## Frames

### 1. Reproduce

- artifact: Stable reproduction
- advance when: The failure can be triggered on demand

### 2. Localize

- artifact: Smaller suspect surface
- advance when: The search field is smaller

### 3. Instrument

- artifact: Logs, traces, asserts, or counters
- advance when: New evidence can distinguish hypotheses

### 4. Hypothesize

- artifact: Likely failure mechanism
- advance when: Repair surface is stated

### 5. Patch

- artifact: Minimal change
- advance when: Patch matches current hypothesis

### 6. Verify

- artifact: Regression sweep
- advance when: Defect is gone and neighboring behavior is checked

## Failure Behavior

Escalate to a deeper diagnostic stack and preserve reproduction, traces, and rejected hypotheses.

## Exit

Defect is gone and neighboring behavior is checked
