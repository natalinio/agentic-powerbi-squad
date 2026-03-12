# Workflow State Management Reference

## Purpose
This document defines the mandatory state tracking protocol for the agentic workflow. The agent MUST use disk-based persistence for all state and intermediate artifacts, eliminating dependency on chat history.

## Core Principle: Disk as Long-Term Memory

> **ANTI-PATTERN**: Relying on chat history for state across multi-step workflows.
> **PATTERN**: Persist ALL state and intermediate outputs to disk. Read from disk at the start of each step.

---

## 1. Workflow State File (`workflow_state.json`)

**Location**: `<ProjectName>/workflow_state.json`

The agent MUST maintain this file throughout the entire workflow. It is the single source of truth for workflow progress.

### Schema

```json
{
  "$schema": "workflow_state_schema",
  "project": "<ProjectName>",
  "specificationFile": "<ProjectName>/spec/<spec_file>.md",
  "startedAt": "2026-01-15T10:30:00Z",
  "lastUpdatedAt": "2026-01-15T14:22:00Z",
  "currentStep": 3,
  "decisionLedger": [
    {
      "id": "DP-0001",
      "step": 1,
      "timestamp": "2026-01-15T10:46:00Z",
      "type": "approval",
      "question": "Proceed to Step 2?",
      "userInput": "Approved",
      "resolution": "Step 1 accepted, proceed to Step 2"
    }
  ],
  "completedSteps": {
    "step_00": {
      "status": "completed",
      "completedAt": "2026-01-15T10:32:00Z",
      "artifacts": [
        "<ProjectName>/PBIP/<ProjectName>.pbip",
        "<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/model.tmdl",
        "<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/database.tmdl"
      ],
      "notes": "PBIP scaffold created successfully",
      "decisionPoints": [],
      "userInputs": []
    },
    "step_01": {
      "status": "completed",
      "completedAt": "2026-01-15T10:45:00Z",
      "artifacts": [
        "<ProjectName>/spec/requirements_summary.md"
      ],
      "notes": "12 KPIs, 5 dimensions, 2 fact tables identified",
      "decisionPoints": [
        {
          "id": "DP-0001",
          "type": "approval",
          "question": "Proceed to Step 2?",
          "answer": "Approved",
          "timestamp": "2026-01-15T10:46:00Z"
        }
      ],
      "userInputs": [
        {
          "type": "confirmation",
          "content": "Approved",
          "timestamp": "2026-01-15T10:46:00Z"
        }
      ]
    },
    "step_02": {
      "status": "completed",
      "completedAt": "2026-01-15T11:00:00Z",
      "artifacts": [
        "<ProjectName>/spec/er_diagram.md"
      ],
      "notes": "Star schema with 7 tables, 9 relationships"
    }
  },
  "pendingStep": {
    "stepNumber": 3,
    "stepName": "Physical Model & TMDL",
    "status": "in-progress",
    "startedAt": "2026-01-15T11:05:00Z",
    "awaitingUserInput": true,
    "decisionPoints": [
      {
        "id": "DP-0002",
        "type": "clarification",
        "question": "Confirm unresolved critical requirement semantics",
        "status": "open",
        "createdAt": "2026-01-15T11:20:00Z"
      }
    ],
    "userInputs": []
  }
}
```

### State Lifecycle Rules

1. **On workflow start (Step 00):** CREATE `workflow_state.json` with `currentStep: 0`.
2. **On step start:** UPDATE `pendingStep` with step number, name, status `"in-progress"`, and timestamp.
3. **On step completion (after user approval):** MOVE `pendingStep` into `completedSteps`, update `currentStep`, clear `pendingStep`.
4. **On step failure/rejection:** UPDATE `pendingStep.status` to `"rejected"` with user feedback in `notes`. Do NOT advance `currentStep`.
5. **On every decision point:** APPEND an immutable record in `decisionLedger` and mirror it under the step (`decisionPoints`, `userInputs`).

### Canonical State Shape (MANDATORY)

To avoid state drift across sessions, the workflow file MUST maintain one canonical structure:

- `completedSteps` is an **object** keyed by `step_00`, `step_01`, ..., `step_10` (never an array).
- `pendingStep` uses fields: `stepNumber`, `stepName`, `status`, `startedAt`, `awaitingUserInput`, `decisionPoints`, `userInputs`.
- Top-level timestamp fields use ISO 8601 UTC format (`YYYY-MM-DDTHH:mm:ssZ`).

If a non-canonical or legacy structure is found, the agent MUST normalize it before executing the next step and record the normalization in step notes.

---

## 1.1 Decision Point Tracking Protocol (MANDATORY)

At the end of each step, the agent can stop and request:
- Clarification (missing/ambiguous requirement)
- Confirmation (approval to proceed)
- Choice (alternative A/B implementation path)

These interactions MUST be persisted explicitly (not only in `notes`).

### Critical clarification classes (Step 1 → Step 4)

The following clarification classes are considered **blocking** for this workflow:

1. Time/period semantics required by calculations (calendar boundaries, ordering, labels, and period-definition rules).
2. Classification and threshold semantics for status-style KPIs (explicit numeric boundaries and tie-break rules).
3. Grain reconciliation semantics when compared datasets are at different granularity levels.

Mandatory behavior:

- Open critical clarifications MUST be represented as explicit `decisionPoints` and mirrored in `decisionLedger`.
- A generic user message such as "proceed" does NOT resolve open critical clarifications.
- Step 3 → Step 4 transition is blocked until all critical clarifications are resolved or explicitly accepted as assumptions by the user and logged.

### Required fields

- `decisionPoints[]` (per step): what was asked and state (`open`, `resolved`, `rejected`)
- `userInputs[]` (per step): exact user response and timestamp
- `decisionLedger[]` (top-level): chronological, immutable audit trail

### Example decision records

```json
{
  "id": "DP-0015",
  "step": 6,
  "type": "clarification",
  "question": "Confirm period boundary rule for cumulative metrics",
  "userInput": "Use project calendar rule C-01",
  "resolution": "Applied approved period boundary C-01",
  "timestamp": "2026-01-15T13:40:00Z"
}
```

```json
{
  "id": "DP-0016",
  "step": 6,
  "type": "approval",
  "question": "Proceed to Step 7?",
  "userInput": "Approved",
  "resolution": "Step 6 accepted",
  "timestamp": "2026-01-15T13:58:00Z"
}
```

---

## 2. Intermediate Artifact Checkpointing

Every step MUST persist its primary output to disk. No significant output should remain only in chat.

### Mandatory Checkpoint Artifacts by Step

| Step | Artifact File | Location | Format |
|------|--------------|----------|--------|
| **Step 00** | PBIP scaffold | `<ProjectName>/PBIP/` | Files/folders |
| **Step 01** | Requirements summary | `<ProjectName>/spec/requirements_summary.md` | Markdown |
| **Step 02** | ER diagram | `<ProjectName>/spec/er_diagram.md` | Markdown (Mermaid) |
| **Step 03** | TMDL files | `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/` | TMDL |
| **Step 04** | DAX measures | `<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/tables/_Measures.tmdl` | TMDL |
| **Step 05** | Mock data + script | `<ProjectName>/data/*.csv` + `<ProjectName>/scripts/generate_mock_data.py` | CSV + Python |
| **Step 06** | Quality review report | `<ProjectName>/tests/quality_review.md` | Markdown |
| **Step 07** | Test definitions + results | `<ProjectName>/tests/tests_definition.json` + `<ProjectName>/tests/tests_execution.md` | JSON + Markdown |
| **Step 08** | Report blueprint | `<ProjectName>/spec/report_blueprint.json` | JSON |
| **Step 09** | PBIR report files | `<ProjectName>/PBIP/<ProjectName>.Report/definition/pages/` | JSON |
| **Step 10** | Report validation report | `<ProjectName>/tests/report_validation_execution.md` | Markdown |

### Incident-only artifact (outside normal step outputs)

| Trigger | Artifact File | Location | Format |
|---|---|---|---|
| User-reported runtime/model/report defect + fix request | Incident lessons learned log | `<ProjectName>/tests/lessons-learned.md` | Markdown |

> This artifact is created/updated only for user-reported defects. It is NOT part of `.github/references/` and must remain project-scoped.

---

## 3. Context Flushing Protocol

### Rule: Never Rely on Chat History

When transitioning between steps, the agent MUST:

1. **READ** `workflow_state.json` to determine current progress and completed artifacts.
2. **READ** the specific artifact files from previous steps (NOT recall from chat memory).
3. **WRITE** outputs to disk before presenting results to the user.
4. **UPDATE** `workflow_state.json` after user approval.

### Context Budgeting for Long 00-10 Workflows

The 00-10 workflow is intentionally long-lived. To prevent performance degradation as artifacts accumulate, the agent MUST treat chat context as short-term working memory only.

Mandatory context-budgeting rules:

1. Prefer compact registries and generated summaries over raw artifact dumps.
2. For bulk validation or scanning tasks, use repository scripts that write results to disk.
3. Read only the artifacts required by the current step input contract.
4. If a step generates many files, read a machine-generated summary first and inspect raw files only for targeted diagnosis.
5. Do not repeatedly reload large PBIR or TMDL artifact sets into chat when the same information already exists in:
  - `workflow_state.json`
  - step artifacts on disk
  - validation summaries in `tests/`

Recommended pattern:

```text
Run local script -> write summary artifact -> read summary -> inspect only failing files
```

This rule is especially important for Step 09 and Step 10, where PBIR artifacts can grow rapidly and degrade chat performance if naively reloaded.

### Resumability

If the chat session is interrupted or restarted mid-workflow:

1. The agent reads `<ProjectName>/workflow_state.json`.
2. It identifies the last completed step and the pending step.
3. It reads all artifact files from completed steps.
4. It resumes from the pending step (or the next step if the pending step was completed but state not updated).

### Example: Resuming from Step 5

```
Agent reads: workflow_state.json → currentStep: 4, all steps 00-04 completed
Agent reads: spec/requirements_summary.md (Step 1 output)
Agent reads: spec/er_diagram.md (Step 2 output)
Agent reads: TMDL files (Step 3 output)
Agent reads: _Measures.tmdl (Step 4 output)
Agent proceeds: Step 5 (Mock Data Generation)
```

---

## 4. Step-Level State Management Instructions

### At the START of each step, the agent MUST:

```
1. READ <ProjectName>/workflow_state.json
2. VERIFY all prerequisite steps are "completed"
3. READ artifact files from prerequisite steps (NOT from chat memory)
4. UPDATE workflow_state.json with pendingStep = current step

### Step Input Contract Gate (MANDATORY)

Before starting step `N` (`N > 0`), the agent MUST verify:

1. Required artifacts from step `N-1` exist on disk.
2. Required artifact formats are valid for the incoming step (Markdown/JSON/TMDL/CSV as applicable).
3. `workflow_state.json` is writable.

If any check fails, STOP and emit a blocking report with minimal recovery actions.

Additional blocking check for Step 2/3/4:

4. For Step 2, Step 3, and Step 4, verify there are no unresolved **critical** clarification decision points inherited from Step 1 unless they have an explicit user-approved assumption record.

If unresolved critical clarifications exist, STOP and request targeted answers before proceeding.
```

### At the END of each step (BEFORE asking user for approval), the agent MUST:

```
1. WRITE all output artifacts to disk (files, not chat)
2. UPDATE workflow_state.json:
   - Move pendingStep to completedSteps
   - Set artifacts list
   - Update currentStep
   - Update lastUpdatedAt timestamp
3. PRESENT summary to user
4. STOP and wait for user approval

### Step Output Contract Gate (MANDATORY)

Before marking a step as completed, the agent MUST verify:

1. Primary step artifact exists and is non-empty.
2. Artifact paths are persisted in the current step record under `completedSteps`.
3. Transition decision is recorded (`approval` or explicit `rejection`) in `decisionLedger` and step-local fields.
```

### On user APPROVAL:

```
1. Confirm step completion in workflow_state.json (if not already done)
2. Record decision point (`type: approval`) in `decisionLedger`, `pendingStep.decisionPoints`, and `pendingStep.userInputs`
2. Proceed to next step
```

### On user REJECTION:

```
1. UPDATE workflow_state.json pendingStep.status = "rejected"
2. Add user feedback to pendingStep.notes
3. Record decision point (`type: rejection`) and full user input payload in tracking fields
4. Re-execute the step with corrections
5. WRITE corrected artifacts to disk
6. UPDATE workflow_state.json
7. Present revised output and STOP
```

---

## 5. Execution Topology (Recommended)

Keep a **single orchestrator** as the only owner of workflow state and step transitions.

- Do not split the end-to-end process into multiple independent top-level state owners.
- Specialist workers are optional and should be used only inside a step (e.g., TMDL linting, DAX validation, PBIR schema checks).
- Specialist workers MUST NOT write `workflow_state.json` directly.
- The orchestrator is solely responsible for approvals, checkpointing, and state transitions.

This model improves traceability and reduces handoff inconsistencies.

## 6. Incident Lessons Learned Protocol (Project-Scoped)

Create or append `<ProjectName>/tests/lessons-learned.md` only when:
- the user reports a direct-check defect (model bug, report load failure, Power BI Desktop error, runtime malfunction), and
- asks the agent to fix it.

Do not generate this file for routine approvals or normal workflow execution.

Each entry should include:
1. Incident ID and date
2. Error message/signature
3. Root cause
4. Fix applied
5. Validation evidence
6. Guardrail/process update
7. Files changed
