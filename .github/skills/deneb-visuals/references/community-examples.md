# Deneb Community Examples

Organized by chart type. Retrieve specific examples when you need a pattern for a chart type.

## Template Repositories

| Repo | File Pattern | Raw URL Base |
|---|---|---|
| avatorl/Deneb-Vega-Templates | `{category}/{slug}.deneb-template.json` | `https://raw.githubusercontent.com/avatorl/Deneb-Vega-Templates/main/` |
| PowerBI-tips/Deneb-Templates | `templates/{Title Case Name}.json` | `https://raw.githubusercontent.com/PowerBI-tips/Deneb-Templates/main/` |
| PBI-David/Deneb-Showcase | `{Title Case Dir}/Spec.json` | `https://raw.githubusercontent.com/PBI-David/Deneb-Showcase/main/` |
| clemviz/Deneb-Templates | `{file}.json` or `{subdir}/{file}.json` | `https://raw.githubusercontent.com/clemviz/Deneb-Templates/main/` |
| shadfrigui/vega-lite | `deneb-templates/{slug}/{slug}-deneb.json` | `https://raw.githubusercontent.com/shadfrigui/vega-lite/main/` |

## Deneb Template Format

Community examples come in three formats:

### 1. Deneb Template JSON
A valid Vega/Vega-Lite spec with a `usermeta` block. Contains `usermeta.deneb` (build, provider), `usermeta.information` (name, author), and `usermeta.dataset` (field placeholder definitions with `key`, `name`, `kind`, `type`).

**To use in PBIR:** Strip `usermeta`, replace placeholder keys (`__0__`, `__1__`) with actual field names, stringify for `jsonSpec`, extract `config` for `jsonConfig`.

### 2. Raw Spec JSON
A plain Vega or Vega-Lite spec without `usermeta`. Ready to inject after field name substitution.

### 3. Blog-embedded Spec
JSON embedded in HTML blog posts. Fetch the page and extract the spec from code blocks.

## UDF Libraries for SVG (Related)

Before writing custom SVG measures, check UDF libraries:
- **PowerofBI.IBCS** — IBCS-compliant bars, waterfalls, small multiples. Install from https://daxlib.org/package/PowerofBI.IBCS/
- **DaxLib.SVG** — sparklines, bars, boxplots, heatmaps, progress bars. Install from https://daxlib.org/package/DaxLib.SVG/
