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
  "completedSteps": {
    "step_00": {
      "status": "completed",
      "completedAt": "2026-01-15T10:32:00Z",
      "artifacts": [
        "<ProjectName>/PBIP/<ProjectName>.pbip",
        "<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/model.tmdl",
        "<ProjectName>/PBIP/<ProjectName>.SemanticModel/definition/database.tmdl"
      ],
      "notes": "PBIP scaffold created successfully"
    },
    "step_01": {
      "status": "completed",
      "completedAt": "2026-01-15T10:45:00Z",
      "artifacts": [
        "<ProjectName>/spec/requirements_summary.md"
      ],
      "notes": "12 KPIs, 5 dimensions, 2 fact tables identified"
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
    "startedAt": "2026-01-15T11:05:00Z"
  }
}
```

### State Lifecycle Rules

1. **On workflow start (Step 00):** CREATE `workflow_state.json` with `currentStep: 0`.
2. **On step start:** UPDATE `pendingStep` with step number, name, status `"in-progress"`, and timestamp.
3. **On step completion (after user approval):** MOVE `pendingStep` into `completedSteps`, update `currentStep`, clear `pendingStep`.
4. **On step failure/rejection:** UPDATE `pendingStep.status` to `"rejected"` with user feedback in `notes`. Do NOT advance `currentStep`.

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

---

## 3. Context Flushing Protocol

### Rule: Never Rely on Chat History

When transitioning between steps, the agent MUST:

1. **READ** `workflow_state.json` to determine current progress and completed artifacts.
2. **READ** the specific artifact files from previous steps (NOT recall from chat memory).
3. **WRITE** outputs to disk before presenting results to the user.
4. **UPDATE** `workflow_state.json` after user approval.

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
```

### On user APPROVAL:

```
1. Confirm step completion in workflow_state.json (if not already done)
2. Proceed to next step
```

### On user REJECTION:

```
1. UPDATE workflow_state.json pendingStep.status = "rejected"
2. Add user feedback to pendingStep.notes
3. Re-execute the step with corrections
4. WRITE corrected artifacts to disk
5. UPDATE workflow_state.json
6. Present revised output and STOP
```
