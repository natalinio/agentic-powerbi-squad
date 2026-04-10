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

This includes user-provided external artifacts passed through chat, such as screenshots, mockups, PDFs, Figma exports, and similar reference material. When such artifacts are relevant to the workflow, they must be archived under `<ProjectName>/spec/` and referenced from disk in later phases.

## References

- `.github/skills/workflow-orchestration/references/workflow-core.md` — governance rules (context flushing, checkpointing, stop gate)
- `.github/skills/workflow-orchestration/references/workflow-state-management.md` — `workflow_state.json` schema, lifecycle rules, decision point tracking

## State Ownership Model

Two different persistence models exist and MUST NOT be conflated:

1. `workflow_state.json` — owned exclusively by `delivery-lead` during end-to-end orchestrated workflows.
2. `agent_session_state.json` — optional compact continuity state for standalone, on-demand specialist agent tasks.

`workflow_state.json` is never written by specialist agents. `agent_session_state.json` is never used as the source of truth for end-to-end phase progression.

## Workflow State File

**Location**: `<ProjectName>/workflow_state.json`

The orchestrator MUST maintain this file throughout the entire workflow. It is the single source of truth for workflow progress.

Placeholder guardrail:
- The literal repository folder `[ProjectName]/` is an example only and MUST NOT be treated as the workflow target.
- Workflow start requires a real project folder created at repository root.
- If only `[ProjectName]/` exists, the orchestrator must create a new project folder and initialize that folder instead of reusing the placeholder.

Specialist workers MAY read this file when invoked by `delivery-lead`, but MUST NOT write it directly.

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

If the user shared supporting evidence in chat rather than as existing project files:
1. archive that evidence under `<ProjectName>/spec/` first;
2. hand off the archived file paths, not a chat-only description;
3. treat the archived copy as the canonical workflow input.

## Specialist Handoff Rule

When `delivery-lead` delegates a workflow phase to a specialist agent, the handoff must be explicit and artifact-based.

The minimum handoff payload is:

1. `projectName`
2. current phase name
3. exact task objective
4. required input artifact paths
5. relevant `decisionLedger` entries
6. unresolved blocking clarifications, if any

If chat-provided supporting artifacts exist, the handoff must include the archived `<ProjectName>/spec/` paths for those files.

Specialist agents must treat this payload plus project artifacts on disk as their source of task context. They must not assume full conversational history is available or authoritative.

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

## Standalone Agent Continuity State

For direct specialist-agent invocations outside `delivery-lead`, use a separate compact state file only when cross-task continuity is actually needed.

**Location**: `<ProjectName>/agent_session_state.json`

This file is optional and exists only to preserve relevant context across standalone invocations without relying on chat history.

Use it for:

1. unresolved decisions or assumptions;
2. open remediation items;
3. partial work likely to be resumed;
4. explicit handoff from one specialist agent to another;
5. recent artifact-level activity that is not yet obvious from final project outputs alone.

Do NOT use it for:

1. full audit logging;
2. tool-by-tool execution history;
3. complete prompt history;
4. end-to-end workflow ownership;
5. long retention of stale task history.

Retention policy:

1. Keep `openItems` until resolved.
2. Keep only the most recent 10 persisted standalone tasks in `recentTasks`.
3. Summarize aggressively; never store verbose command output.
4. Prefer accuracy and resumability over exhaustiveness.

Maintenance helper:

- `.github/skills/workflow-orchestration/scripts/compact_agent_session_state.py` — trims `recentTasks`, removes closed `openItems`, and refreshes the summary block for `agent_session_state.json`.
- `.github/skills/workflow-orchestration/references/agent_session_state.template.json` — initial template to create the file when standalone continuity state is needed for the first time.

Design choice:

- Default to bounded snapshot JSON (`agent_session_state.json`).
- Do NOT use append-only JSONL for standalone continuity by default. Append-only logs grow without improving decision quality, consume context budget, and force later agents to reconstruct semantics from noise.
