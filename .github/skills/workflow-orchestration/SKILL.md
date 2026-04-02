---
name: workflow-orchestration
description: >-
  Internal skill for the delivery-lead orchestrator. Manages end-to-end workflow state,
  decision tracking, phase transitions, and artifact checkpointing.
  Not invocable by users directly — consumed only by the delivery-lead agent.
user-invocable: false
---

# Skill: Workflow Orchestration & State Management

## Purpose

Provide the delivery-lead agent with state tracking, decision logging, artifact checkpointing, and context flushing protocols for coordinating multi-agent Power BI development workflows.

This skill is NOT invocable by users directly. It is consumed exclusively by the `delivery-lead` orchestrator agent when operating in end-to-end workflow mode.

## Core Principle: Disk as Long-Term Memory

> **ANTI-PATTERN**: Relying on chat history for state across multi-agent workflows.
> **PATTERN**: Persist ALL state and intermediate outputs to disk. Read from disk at the start of each phase.

## References

- `.github/skills/workflow-orchestration/references/workflow-core.md` — governance rules (context flushing, checkpointing, stop gate)
- `.github/skills/workflow-orchestration/references/workflow-state-management.md` — `workflow_state.json` schema, lifecycle rules, decision point tracking

## Workflow State File

**Location**: `<ProjectName>/workflow_state.json`

The orchestrator MUST maintain this file throughout the entire workflow. It is the single source of truth for workflow progress.

### State Lifecycle Rules

1. **On workflow start**: CREATE `workflow_state.json` with `currentPhase: "initialization"`.
2. **On phase start**: UPDATE `pendingPhase` with phase name, agent assignment, status `"in-progress"`, and timestamp.
3. **On phase completion (after user approval)**: MOVE `pendingPhase` into `completedPhases`, update `currentPhase`, clear `pendingPhase`.
4. **On phase failure/rejection**: UPDATE `pendingPhase.status` to `"rejected"` with feedback. Do NOT advance.
5. **On every decision point**: APPEND an immutable record in `decisionLedger`.

### Canonical State Shape

```json
{
  "$schema": "workflow_state_schema",
  "project": "<ProjectName>",
  "specificationFile": "<ProjectName>/spec/<spec_file>.md",
  "startedAt": "<ISO 8601>",
  "lastUpdatedAt": "<ISO 8601>",
  "currentPhase": "<phase-name>",
  "decisionLedger": [],
  "completedPhases": {},
  "pendingPhase": null
}
```

## Workflow Phases

The delivery-lead orchestrator coordinates the following phases, delegating execution to domain-specific agents:

| Phase | Agent | Skills Used | Primary Output |
|---|---|---|---|
| Initialization | delivery-lead | `project-initialization` | PBIP scaffold |
| Requirements | business-data-analyst | `requirements-analysis` | `spec/requirements_summary.md` |
| Semantic Model | pbi-semantic-model | `logical-model`, `physical-model-tmdl`, `dax-development` | TMDL files |
| Mock Data | data-generator | `mock-data-generation` | `data/*.csv` + updated partitions |
| Quality Assurance (Model) | pbi-qa | `code-review`, `functional-testing` | `tests/quality_review.md`, `tests/tests_execution.md` |
| Report Design & Impl | pbi-report | `report-design`, `report-implementation` | `spec/report_blueprint.json`, PBIR files |
| Quality Assurance (Report) | pbi-qa | `report-quality-validation` | `tests/report_validation_execution.md` |

## Stop / Approval Gate

After each phase completion, the orchestrator MUST:
1. Save all output artifacts to disk.
2. Update `workflow_state.json`.
3. Present a summary to the user.
4. **STOP and wait for explicit user approval** before delegating the next phase.

## Context Flushing Protocol

When transitioning between phases:
1. **READ** `workflow_state.json` to determine current progress.
2. **READ** specific artifact files from previous phases (NOT from chat memory).
3. **WRITE** outputs to disk before presenting results.
4. **UPDATE** `workflow_state.json` after user approval.

## Decision Point Tracking

Critical clarifications that are blocking for the workflow:
1. Time/period semantics required by calculations.
2. Classification and threshold semantics for status-style KPIs.
3. Grain reconciliation semantics when compared datasets are at different granularity levels.

These MUST be explicitly resolved (or assumption-approved) before advancing past the Requirements phase.

## Lessons Learned (Project-Scoped)

Create/update `<ProjectName>/lessons-learned.md` **only** when:
1. The user reports a defect found in Power BI Desktop or model execution.
2. The defect is a concrete malfunction.
3. The user asks for diagnosis/fix.

Never create it during normal phase progression.
