# Live Migration Stack

- id: `stack.live-migration-stack.v1`
- version: `1`
- working seal: `stack://live-migration-stack/23AA56B454`
- enter: Use when data, schemas, or infrastructure are changing in a live environment.

## Frames

### 1. Inventory

- artifact: Dependency and blast-radius map
- advance when: Moving parts are known

### 2. Prepare rollback

- artifact: Backup, snapshot, flag, or dual-read path
- advance when: Reversal is real

### 3. Expand compatibly

- artifact: Backward-compatible new structure
- advance when: Old paths still work

### 4. Backfill

- artifact: New representation
- advance when: Old path is not cut off

### 5. Compare parity

- artifact: Parity report
- advance when: Old and new paths agree

### 6. Cut over

- artifact: Read or write switch
- advance when: Parity holds and rollback is live

### 7. Observe

- artifact: Live metrics and divergence samples
- advance when: Safety window remains stable

### 8. Contract

- artifact: Removed old paths
- advance when: Safety window closes cleanly

## Failure Behavior

Rollback immediately using the prepared boundary and preserve divergence samples.

## Exit

Safety window closes cleanly
