# Mockup To Power BI Patterns

This reference defines the recommended translation pattern when the user provides a dashboard mockup, screenshot, Figma file, or React prototype and asks for a Power BI report aligned to that visual baseline.

## Core Principle

Translate the mockup into a Power BI-feasible design system and visual strategy before generating PBIR.

Do not attempt a pixel-perfect web clone. Preserve:

1. hierarchy of information;
2. visual rhythm;
3. semantic color usage;
4. perceived layout balance;
5. business intent of each component.

## Feasibility Decision Order

For every mockup component, evaluate in this order:

1. `native`
2. `composite-native`
3. `svg`
4. `deneb`
5. `approximation`
6. `not-feasible`

## Theme-First Extraction

Before visual mapping, extract:

1. page background;
2. card background;
3. primary and secondary accent colors;
4. positive / negative / neutral cues;
5. title, subtitle, KPI, and label typography;
6. spacing and container rules.

## Typical Mapping Patterns

### 1. Header Band With Branding And Filters

Mockup intent:

- branded horizontal header bar
- left-aligned logo/title
- right-aligned dropdown filters

Recommended mapping:

- `composite-native`
- shape/background rectangle for header band
- text boxes for title/subtitle
- image visual for logo if needed
- native dropdown slicers aligned on a top row

Constraints:

1. Power BI does not provide a single reusable web-style header component.
2. Precise responsive behavior of web nav bars is not available.

### 2. KPI Card With Progress Bar And Delta Badge

Mockup intent:

- card title
- headline metric
- mini progress bar
- current percentage
- delta badge vs prior period

Recommended mapping:

- `composite-native` first choice
- native card or text box for headline values
- shape or small bar visual for progress cue
- text box / conditional formatting for delta badge
- fallback `svg` when the visual must feel like a single unified component

Constraints:

1. Native card visuals do not embed arbitrary progress micro-components inside one visual shell.
2. Web-style pill badges are usually approximated unless rendered via SVG.

### 3. Donut Card In Elevated Container

Mockup intent:

- donut chart inside a card container
- category callouts
- local legend in footer area

Recommended mapping:

- `native` if standard donut is sufficient
- `composite-native` for donut + footer legend treatment
- `deneb` only if callout geometry or label choreography is highly bespoke

Constraints:

1. Native donut labels are less flexible than custom chart layouts.
2. Footer legend alignment often requires container composition.

### 4. Analytical Side Panel With KPI Summary And Small Trend Chart

Mockup intent:

- elevated right-side insight panel
- KPI summary plus small quarter trend chart

Recommended mapping:

- `composite-native`
- container treatment via theme + layout
- text boxes and card elements for summary
- clustered column or line/column native chart for trend

Constraints:

1. The panel is a layout composition, not a single Power BI component.
2. Tight text-and-chart integration may require approximation.

## Concrete Example Blueprint Snippet

The following example matches a typical dark-theme banking or sustainability dashboard mockup with a branded green header, KPI cards, donut cards, and a right-side analytical panel.

```json
{
  "sourceDesign": {
    "hasMockup": true,
    "mockupType": "image",
    "fidelityGoal": "high",
    "notes": [
      "Dark dashboard canvas with branded green header and orange KPI accents"
    ]
  },
  "designSystem": {
    "gridUnit": 8,
    "pagePadding": 16,
    "visualGap": 16,
    "sectionGap": 24,
    "containerStyle": {
      "mode": "elevated",
      "shadow": true,
      "border": true
    }
  },
  "pages": [
    {
      "pageId": "Page1",
      "displayName": "Sustainability Overview",
      "visuals": [
        {
          "visualId": "header_filters",
          "mockupComponentName": "Branded Header With Filters",
          "mockupIntent": "Top green band with report title and three dropdown filters",
          "visualType": "advancedSlicerVisual",
          "implementationStrategy": {
            "mode": "composite-native",
            "primaryVisualType": "shape",
            "secondaryVisualTypes": ["textbox", "image", "advancedSlicerVisual"],
            "fallbackMode": null,
            "fidelityRisk": "medium",
            "constraints": [
              "Header is a composed layout, not a single Power BI component"
            ],
            "workarounds": [
              "Use a full-width colored rectangle, title text boxes, optional logo image, and aligned dropdown slicers"
            ],
            "notFeasibleAspects": []
          }
        },
        {
          "visualId": "kpi_card_01",
          "mockupComponentName": "KPI Card With Progress And Delta",
          "mockupIntent": "Card showing metric, progress cue, current percentage, and delta badge",
          "visualType": "cardVisual",
          "implementationStrategy": {
            "mode": "composite-native",
            "primaryVisualType": "cardVisual",
            "secondaryVisualTypes": ["shape", "textbox"],
            "fallbackMode": "svg",
            "fidelityRisk": "medium",
            "constraints": [
              "Native card cannot host a true embedded progress bar and pill badge as a single component"
            ],
            "workarounds": [
              "Use a card for headline value and supporting shapes/text for progress and delta"
            ],
            "notFeasibleAspects": []
          }
        },
        {
          "visualId": "donut_card_01",
          "mockupComponentName": "Climate Credit Framework Donut",
          "mockupIntent": "Donut breakdown inside a dark elevated container with local legend",
          "visualType": "donutChart",
          "implementationStrategy": {
            "mode": "composite-native",
            "primaryVisualType": "donutChart",
            "secondaryVisualTypes": ["textbox"],
            "fallbackMode": "deneb",
            "fidelityRisk": "medium",
            "constraints": [
              "Precise label choreography may exceed native donut flexibility"
            ],
            "workarounds": [
              "Use native donut with controlled legend placement; escalate to Deneb only if label layout is critical"
            ],
            "notFeasibleAspects": []
          }
        },
        {
          "visualId": "side_panel_01",
          "mockupComponentName": "GAR Insight Side Panel",
          "mockupIntent": "Elevated side panel with KPI summary and quarterly trend",
          "visualType": "clusteredColumnChart",
          "implementationStrategy": {
            "mode": "composite-native",
            "primaryVisualType": "clusteredColumnChart",
            "secondaryVisualTypes": ["textbox", "shape", "cardVisual"],
            "fallbackMode": null,
            "fidelityRisk": "low",
            "constraints": [
              "Panel is assembled from multiple visuals and text elements"
            ],
            "workarounds": [
              "Use a container zone with KPI text elements above a native quarter chart"
            ],
            "notFeasibleAspects": []
          }
        }
      ]
    }
  ]
}
```

## Operational Rule

If a component is classified as `approximation` or `not-feasible`, record that in the blueprint explicitly. Do not hide the compromise in implementation.