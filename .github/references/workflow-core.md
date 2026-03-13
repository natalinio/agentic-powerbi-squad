# Workflow Core Governance

This reference is **inherited by all skill files (Steps 00–10)**. When any skill is loaded, these rules apply automatically. Do not repeat them inside individual skill files.

## 1. Step Scope Rule

Each skill governs exactly one step. Execute it only for its designated step number. Do NOT preload downstream skill files unless a blocking dependency explicitly requires it.

## 2. Context Flushing (Start of Every Step)

At the START of each step:

1. **READ** `<ProjectName>/workflow_state.json` — verify prerequisite steps are completed.
2. **READ** each input artifact listed in the skill's Step Contract **from disk** (never from chat memory).
3. If any required input artifact is missing or unreadable, **STOP** and report the blocking issue with a minimal recovery action list.

## 3. Artifact Checkpointing (End of Every Step)

**BEFORE presenting any results to the user:**

1. **SAVE** the primary output artifact to the path listed in the skill's Step Contract.
2. **UPDATE** `<ProjectName>/workflow_state.json`:
   - Set `pendingStep` to current step completed.
   - Add primary artifact path(s).
3. **CONFIRM** to the user that the artifact has been saved to disk.

## 4. Input / Output Gate

- **Before starting step N**: required input artifacts from step N-1 must exist on disk and be non-empty. Stop with a blocking error if any are missing.
- **Before marking step N complete**: primary output artifact must exist on disk, be non-empty, and be recorded in `workflow_state.json`.

## 5. Stop / Approval Gate (ABSOLUTE)

After every step: **STOP**. Do not advance until the user explicitly approves ("Proceed", "Approved", "Looks good"). Advancing without explicit approval is forbidden.

## 6. State Update Pattern

| Event | Action |
|---|---|
| Step start | Update `pendingStep` with step info and status `in_progress` |
| Step completion (after approval) | Move `pendingStep` → `completedSteps[step_NN]`, update `currentStep` |
| Rejection | Set `pendingStep.status = "rejected"` with user feedback |
| Decision / clarification | Record in `decisionPoints` and `decisionLedger` — not only in `notes` |
| Assumption approval | Persist explicit user approval text in `decisionLedger` |
