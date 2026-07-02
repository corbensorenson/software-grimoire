# Recursive Decomposition Stack

- id: `stack.recursive-decomposition-stack.v1`
- version: `1`
- working seal: `stack://recursive-decomposition-stack/9E9D03E9C0`
- enter: Use when the task is too large for one spell or one session and scope can shrink recursively.

## Frames

### 1. Define contract

- artifact: Parent contract
- advance when: Boundary and obligations are clear

### 2. Split into children

- artifact: Smaller scopes
- advance when: Every child is smaller than parent scope

### 3. Call child stack

- artifact: Solved child scope
- advance when: Child base case or child verification passes

### 4. Integrate

- artifact: Integrated parent scope
- advance when: Children compose under parent contract

### 5. System verify

- artifact: Parent verification evidence
- advance when: Children are green and parent contract holds

## Failure Behavior

Stop descent if child scopes do not shrink or contract consistency is lost.

## Exit

Children are green and parent contract holds
