# Feature Specification: Semantic Model Compiler for Power BI

**Feature Branch**: `001-semantic-model-compiler`  
**Created**: 2026-02-19  
**Status**: Draft  
**Input**: User description: "Build a system that acts as a Semantic Model Compiler for Power BI. The target users are data architects and analytics engineers who need to create high-quality Power BI semantic models starting from a functional reporting specification and KPI definitions, without manually designing star schemas or writing extensive DAX by hand. The system accepts as input a functional reporting specification describing business questions and KPIs, a data table schema, the desired modeling mode (Import or Direct Lake), and optional row-level security requirements. The system produces a proposed semantic model including a star schema design, table relationships and cardinalities, a declared date dimension strategy, documented DAX measures aligned to the KPI glossary, and deployable Power BI semantic model artifacts accompanied by a validation and quality report. Users interact with the system by submitting the specification and reviewing the generated model and QA report before approving the artifacts for deployment. The feature is considered complete when the generated semantic model is valid, reviewable, and ready for use in Power BI, with all KPIs covered and modeling assumptions explicitly documented."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Generate a review-ready semantic model package (Priority: P1)

As a data architect or analytics engineer, I want to submit a functional reporting specification (business questions + KPIs), a table schema, and a modeling mode so that I receive a complete, review-ready semantic model proposal (design + artifacts + QA report) without manually designing a star schema or writing extensive DAX.

**Why this priority**: This is the primary value: rapid, standardized model creation that is deployable and auditable.

**Independent Test**: Provide a small but realistic table schema + KPI glossary + mode, then verify that the output package includes all mandatory components and passes validation.

**Acceptance Scenarios**:

1. **Given** a valid functional reporting specification, KPI glossary, table schema, and modeling mode, **When** the user requests generation, **Then** the system produces a proposed star schema, relationships with cardinalities, a declared date dimension strategy, documented DAX measures for all KPIs, deployable artifacts (TMDL/BIM), and a validation/quality report.
2. **Given** input that is structurally valid but incomplete (e.g., missing date fields needed by time-based KPIs), **When** the user requests generation, **Then** the system still produces a proposal and explicitly documents assumptions and gaps in the QA report.

---

### User Story 2 - Review, decision, and iteration (Priority: P2)

As a user, I want to review the generated model proposal and QA findings, understand assumptions, and decide whether to approve the artifacts for deployment or request changes.

**Why this priority**: Governance requires that generated artifacts are reviewable and that decisions are explicit before deployment.

**Independent Test**: Generate a model package, then verify that a reviewer can (a) see KPI coverage, assumptions, and validation results and (b) record an approve/reject decision with a reason.

**Acceptance Scenarios**:

1. **Given** a generated model package, **When** the user reviews it, **Then** the system shows KPI coverage, assumptions, and QA findings in a way that supports a clear approve/reject decision.
2. **Given** a rejected package with specified requested changes (e.g., rename a KPI or adjust a relationship direction), **When** the user re-submits the updated inputs, **Then** the system generates a new package and indicates what changed from the prior output at a high level (e.g., updated assumptions, updated measures, updated relationships).

---

### User Story 3 - Include row-level security requirements (Priority: P3)

As a user, I want to provide optional row-level security (RLS) requirements so that the output package includes RLS configuration or clear RLS guidance aligned to the requested access rules.

**Why this priority**: Many semantic models require controlled access; supporting RLS early reduces rework and adoption friction.

**Independent Test**: Provide a minimal RLS requirement (roles + filter logic in business terms) and verify the output package includes RLS components and that the QA report confirms RLS presence.

**Acceptance Scenarios**:

1. **Given** RLS requirements are provided, **When** the user requests generation, **Then** the output includes RLS configuration (or equivalent artifact content) and documents any assumptions or limitations in the QA report.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when the table schema is invalid, inconsistent, or missing keys required to form relationships?
- How does the system handle KPI definitions that are ambiguous, contradictory, or not computable from the available data?
- What happens when multiple plausible star schema designs exist (e.g., multiple candidate fact tables)?
- How does the system handle duplicate or conflicting names across tables/columns/KPIs?
- What happens when the requested modeling mode conflicts with the source data characteristics?
- How does the system handle RLS requirements that cannot be expressed with the provided data?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST accept a functional reporting specification describing business questions and KPIs.
- **FR-002**: System MUST accept a KPI glossary defining KPI names, descriptions, and required calculation intent.
- **FR-003**: System MUST accept a data table schema (tables, columns, and key information when available).
- **FR-004**: System MUST accept a modeling mode selection: Import or Direct Lake.
- **FR-005**: System MUST accept optional RLS requirements expressed in business terms (roles and access rules).
- **FR-006**: System MUST generate a proposed semantic model design using a star schema approach by default.
- **FR-007**: System MUST propose table relationships, including cardinalities and filter directions, and validate them for consistency.
- **FR-008**: System MUST declare a date dimension strategy (including how time intelligence is supported) and validate that time-based KPIs can be supported.
- **FR-009**: System MUST generate documented DAX measures aligned to the KPI glossary, including definitions that are understandable in review.
- **FR-010**: System MUST ensure KPI coverage by producing a measure (or a documented exception) for every KPI in the glossary.
- **FR-011**: System MUST produce deployable semantic model artifacts in at least one of: TMDL and/or BIM.
- **FR-012**: System MUST produce a validation and quality report that includes: checks performed, pass/fail results, warnings, and explicit assumptions.
- **FR-013**: When generation cannot produce a valid model package, the system MUST fail explicitly and return actionable diagnostics (what is missing, what is inconsistent, and what the user can change).
- **FR-014**: Users MUST be able to review the generated outputs and record an explicit approval or rejection decision prior to deployment.

### Assumptions

- The functional reporting specification and KPI glossary are provided by the business/domain team and are the source of truth for KPI names and meanings.
- If the table schema does not include explicit keys, the system may infer candidate keys/relationships but must flag them as assumptions in the QA report.
- If multiple designs are plausible, the system selects one and documents why (e.g., simplest star schema) and what alternatives were not chosen.

### Key Entities *(include if feature involves data)*

- **Functional Reporting Specification**: The user-provided description of business questions, reporting needs, and required KPIs.
- **KPI Definition**: A KPI name, business definition, and calculation intent; may include dependencies on other measures.
- **Table Schema**: The available tables/columns and any known keys or constraints used to design relationships.
- **Modeling Mode**: The chosen mode (Import or Direct Lake) that influences modeling constraints.
- **Semantic Model Proposal**: The generated model design (star schema, relationships, date strategy, measures) intended for review.
- **Relationship**: A link between two tables with cardinality and filter direction.
- **DAX Measure**: A named calculation aligned to a KPI definition and documented for review.
- **RLS Requirement**: A set of roles and access rules expressed in business terms.
- **Artifact Package**: The deployable outputs (TMDL/BIM) plus documentation.
- **QA Finding**: A validation result (pass/warn/fail) with explanation and any assumptions.
- **Approval Decision**: The reviewer’s approve/reject outcome with rationale.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: For a representative reporting spec + schema package, users receive a complete, review-ready model package on the first run in under 30 minutes.
- **SC-002**: In pilot usage, at least 90% of KPIs in the glossary have acceptable measures without manual rewrites on first review.
- **SC-003**: 100% of generated model packages include an explicit KPI coverage summary and an explicit assumptions section in the QA report.
- **SC-004**: In pilot usage, the median time from submission to “approved for deployment” is reduced by at least 50% compared to a manual modeling baseline.
