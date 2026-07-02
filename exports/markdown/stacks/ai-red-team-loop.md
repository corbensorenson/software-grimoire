# AI Red-Team Loop

- id: `stack.ai-red-team-loop.v1`
- version: `1`
- working seal: `stack://ai-red-team-loop/6CF8F7698D`
- enter: Use when an LLM-assisted workflow needs controlled adversarial testing for prompt injection, jailbreak pressure, leakage, or tool misuse.

## Frames

### 1. Threat model

- artifact: Assets, trust boundaries, allowed tools, untrusted inputs, and attacker goals
- advance when: The security boundary and benign task are explicit

### 2. Build defanged probes

- artifact: Harmless fixture prompts and canary-bearing test inputs
- advance when: Probes preserve attack shape without operational payloads

### 3. Run in sandbox

- artifact: Prompt, transcript, fixture version, and tool-scope record
- advance when: The model output and tool behavior are captured verbatim

### 4. Score resistance

- artifact: Attack-resistance, utility-preservation, and audit-quality scores
- advance when: Scores cite the transcript and fixture expectations

### 5. Mitigate

- artifact: Prompt, policy, retrieval, or tool-scope repair
- advance when: The repair addresses the observed failure without blanket refusal

### 6. Replay

- artifact: Repeated run set across fixture versions or model surfaces
- advance when: The failure is fixed or residual risk is accepted explicitly

### 7. Report

- artifact: Defensive finding with source map, evidence, mitigation, and residual risk
- advance when: A maintainer can reproduce the finding without unsafe payloads

## Failure Behavior

Stop the test if a probe would require operational harmful content; replace it with a defanged skeleton and record the omitted class of detail.

## Exit

A maintainer can reproduce the finding without unsafe payloads
