---
mode: ask
description: Translate a dashboard mockup, screenshot, Figma spec, or React UI into a Power BI-feasible report blueprint with explicit feasibility classification and implementation strategy.
---

You are starting a **mockup-to-PowerBI translation** task using the `pbi-report` agent.

Goal:

Translate the provided visual evidence into a Power BI-feasible report design and produce or update `<ProjectName>/spec/report_blueprint.json`.

Mandatory process:

1. Identify the target project folder.
2. Read any available requirements, semantic model, and existing report blueprint.
3. If visual evidence is provided, run a `mockup-to-powerbi translation` pass before final layout decisions.
4. For each significant mockup component, classify the implementation as one of:
   - `native`
   - `composite-native`
   - `svg`
   - `deneb`
   - `approximation`
   - `not-feasible`
5. Capture the chosen strategy inside `report_blueprint.json` using `implementationStrategy`.
6. Extract theme and layout tokens from the mockup before detailed PBIR implementation.
7. Respect Power BI constraints. Do not treat it like a generic web page.
8. If exact fidelity is not realistic, document constraints and workarounds explicitly instead of hiding them.

Expected output:

1. Updated `<ProjectName>/spec/report_blueprint.json`
2. Summary of:
   - pages designed
   - key visual mappings
   - components requiring SVG or Deneb
   - approximations or non-feasible elements

Stop after saving the blueprint and ask for approval before physical PBIR implementation.