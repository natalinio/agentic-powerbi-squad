"""
Automated PBIR validation for Power BI reports.

This shared utility validates PBIR report artifacts against:
- the generated report blueprint,
- the semantic model TMDL registry,
- and repository-specific PBIR guardrails.

It is designed for Step 10 so that bulk file scanning happens locally on disk,
avoiding unnecessary chat-context growth in long 00-10 workflows.

Usage:
    python .github/scripts/validate_pbir_report.py <ProjectName>
    python .github/scripts/validate_pbir_report.py <ProjectName> --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
UTF8_BOM = b"\xef\xbb\xbf"


@dataclass
class Issue:
    section: str
    check: str
    status: str
    page: str = ""
    visual: str = ""
    details: str = ""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def read_json(path: Path) -> Tuple[Optional[Dict[str, Any]], bool, Optional[str]]:
    raw = read_bytes(path)
    has_bom = raw.startswith(UTF8_BOM)
    try:
        data = json.loads(raw.decode("utf-8-sig"))
        return data, has_bom, None
    except Exception as exc:  # pragma: no cover - defensive
        return None, has_bom, str(exc)


def parse_tmdl_name(line: str, keyword: str) -> Optional[str]:
    pattern = rf"^\s*{keyword}\s+(?:'([^']+)'|([A-Za-z_][\w]*))"
    match = re.match(pattern, line)
    if not match:
        return None
    return match.group(1) or match.group(2)


class ModelRegistry:
    def __init__(self) -> None:
        self.tables: Set[str] = set()
        self.columns_by_table: Dict[str, Set[str]] = defaultdict(set)
        self.measures: Set[str] = set()
        self.relationship_graph: Dict[str, Set[str]] = defaultdict(set)

    @classmethod
    def build(cls, semantic_model_path: Path) -> "ModelRegistry":
        registry = cls()
        tables_path = semantic_model_path / "tables"
        for tmdl_file in tables_path.glob("*.tmdl"):
            table_name = tmdl_file.stem
            text = tmdl_file.read_text(encoding="utf-8-sig")
            if table_name != "_Measures":
                registry.tables.add(table_name)
            for line in text.splitlines():
                column_name = parse_tmdl_name(line, "column")
                if column_name and table_name != "_Measures":
                    registry.columns_by_table[table_name].add(column_name)
                measure_name = parse_tmdl_name(line, "measure")
                if measure_name:
                    registry.measures.add(measure_name)

        relationships_file = semantic_model_path / "relationships.tmdl"
        if relationships_file.exists():
            pending_from: Optional[str] = None
            for line in relationships_file.read_text(encoding="utf-8-sig").splitlines():
                from_match = re.search(r"fromColumn:\s+([A-Za-z_][\w]*)\.[A-Za-z_][\w]*", line)
                to_match = re.search(r"toColumn:\s+([A-Za-z_][\w]*)\.[A-Za-z_][\w]*", line)
                if from_match:
                    pending_from = from_match.group(1)
                if to_match and pending_from:
                    to_table = to_match.group(1)
                    registry.relationship_graph[pending_from].add(to_table)
                    registry.relationship_graph[to_table].add(pending_from)
                    pending_from = None

        return registry

    def is_reachable(self, tables: Iterable[str]) -> bool:
        relevant = [table for table in tables if table != "_Measures"]
        if len(relevant) <= 1:
            return True
        start = relevant[0]
        visited = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in self.relationship_graph.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        return all(table in visited for table in relevant[1:])


def extract_refs(node: Any, refs: List[Tuple[str, str, str]]) -> None:
    if isinstance(node, dict):
        for kind in ("Measure", "Column"):
            payload = node.get(kind)
            if isinstance(payload, dict):
                entity = None
                expression = payload.get("Expression")
                if isinstance(expression, dict):
                    source_ref = expression.get("SourceRef")
                    if isinstance(source_ref, dict):
                        entity = source_ref.get("Entity")
                prop = payload.get("Property")
                if entity and prop:
                    refs.append((entity, prop, kind))
        for value in node.values():
            extract_refs(value, refs)
    elif isinstance(node, list):
        for item in node:
            extract_refs(item, refs)


def rects_overlap(first: Dict[str, Any], second: Dict[str, Any]) -> bool:
    left_a = float(first.get("x", 0))
    top_a = float(first.get("y", 0))
    right_a = left_a + float(first.get("width", 0))
    bottom_a = top_a + float(first.get("height", 0))

    left_b = float(second.get("x", 0))
    top_b = float(second.get("y", 0))
    right_b = left_b + float(second.get("width", 0))
    bottom_b = top_b + float(second.get("height", 0))

    return left_a < right_b and right_a > left_b and top_a < bottom_b and bottom_a > top_b


def logical_type_to_pbir(visual_type: str) -> str:
    mapping = {
        "card": "cardVisual",
        "multiRowCard": "cardVisual",
        "table": "tableEx",
        "slicer": "slicer",
        "clusteredBarChart": "clusteredBarChart",
        "clusteredColumnChart": "clusteredColumnChart",
        "lineClusteredColumnComboChart": "lineClusteredColumnComboChart",
        "scatterChart": "scatterChart",
        "gauge": "gauge",
        "treemap": "treemap",
        "azureMap": "azureMap",
    }
    return mapping.get(visual_type, visual_type)


class PbirValidator:
    def __init__(self, project_name: str, verbose: bool = False):
        self.project_name = project_name
        self.verbose = verbose
        self.project_path = REPO_ROOT / project_name
        self.blueprint_path = self.project_path / "spec" / "report_blueprint.json"
        self.report_path = self.project_path / "PBIP" / f"{project_name}.Report" / "definition"
        self.pages_path = self.report_path / "pages"
        self.semantic_model_path = self.project_path / "PBIP" / f"{project_name}.SemanticModel" / "definition"
        self.tests_path = self.project_path / "tests"
        self.report_output_path = self.tests_path / "report_validation_execution.md"
        self.summary_output_path = self.tests_path / "report_validation_execution.json"
        self.issues: List[Issue] = []
        self.model_registry = ModelRegistry.build(self.semantic_model_path)

    def add_issue(self, section: str, check: str, status: str, page: str = "", visual: str = "", details: str = "") -> None:
        self.issues.append(Issue(section=section, check=check, status=status, page=page, visual=visual, details=details))

    def validate(self) -> int:
        blueprint, _, blueprint_error = read_json(self.blueprint_path)
        if blueprint_error or blueprint is None:
            self.add_issue("Structural", "Blueprint JSON", "FAIL", details=f"Unable to parse blueprint: {blueprint_error}")
            self.write_outputs({}, {}, {})
            return 1

        pages_metadata_path = self.pages_path / "pages.json"
        pages_metadata, pages_bom, pages_error = read_json(pages_metadata_path)
        if pages_error or pages_metadata is None:
            self.add_issue("Structural", "pages.json parse", "FAIL", details=f"Unable to parse pages metadata: {pages_error}")
            self.write_outputs(blueprint, {}, {})
            return 1
        if pages_bom:
            self.add_issue("Structural", "pages.json encoding", "FAIL", details="File contains UTF-8 BOM")

        page_order = pages_metadata.get("pageOrder", [])
        active_page_name = pages_metadata.get("activePageName")
        page_dirs = sorted([directory for directory in self.pages_path.iterdir() if directory.is_dir()])
        page_dir_names = {directory.name for directory in page_dirs}

        self.add_issue(
            "Blueprint Compliance",
            "Page Count",
            "PASS" if len(page_order) == len(blueprint.get("pages", [])) and len(page_order) == len(page_dirs) else "FAIL",
            details=f"Expected {len(blueprint.get('pages', []))}, metadata has {len(page_order)}, disk has {len(page_dirs)}",
        )

        if active_page_name in page_order:
            self.add_issue("Structural", "Active Page Reference", "PASS", details=f"activePageName={active_page_name}")
        else:
            self.add_issue("Structural", "Active Page Reference", "FAIL", details=f"activePageName {active_page_name} not found in pageOrder")

        actual_visual_type_counts_by_page: Dict[str, Counter] = {}
        actual_visual_count_by_page: Dict[str, int] = {}
        page_display_names: Dict[str, str] = {}

        for index, page_runtime_id in enumerate(page_order):
            page_dir = self.pages_path / page_runtime_id
            page_json_path = page_dir / "page.json"
            page_data, has_bom, page_error = read_json(page_json_path)
            if page_error or page_data is None:
                self.add_issue("Structural", "page.json parse", "FAIL", page=page_runtime_id, details=f"Unable to parse page.json: {page_error}")
                continue
            if has_bom:
                self.add_issue("Structural", "page.json encoding", "FAIL", page=page_runtime_id, details="File contains UTF-8 BOM")
            if page_runtime_id not in page_dir_names:
                self.add_issue("Structural", "Page folder exists", "FAIL", page=page_runtime_id, details="Page metadata references a missing folder")
            if page_data.get("name") == page_runtime_id:
                self.add_issue("Structural", "Page folder/name contract", "PASS", page=page_runtime_id)
            else:
                self.add_issue("Structural", "Page folder/name contract", "FAIL", page=page_runtime_id, details=f"Folder={page_runtime_id}, page.json.name={page_data.get('name')}")

            page_display_name = page_data.get("displayName", "")
            page_display_names[page_runtime_id] = page_display_name
            if index < len(blueprint.get("pages", [])):
                expected_display_name = blueprint["pages"][index].get("displayName", "")
                status = "PASS" if expected_display_name == page_display_name else "WARNING"
                self.add_issue("Blueprint Compliance", "Page Display Name", status, page=page_runtime_id, details=f"Expected '{expected_display_name}', actual '{page_display_name}'")

            page_width = float(page_data.get("width", 0))
            page_height = float(page_data.get("height", 0))
            visual_dirs = sorted([directory for directory in (page_dir / "visuals").iterdir() if directory.is_dir()])
            actual_visual_count_by_page[page_runtime_id] = len(visual_dirs)
            visual_type_counter: Counter = Counter()
            actual_visual_type_counts_by_page[page_runtime_id] = visual_type_counter
            visual_positions: List[Tuple[str, Dict[str, Any], str]] = []

            for visual_dir in visual_dirs:
                visual_json_path = visual_dir / "visual.json"
                visual_data, visual_bom, visual_error = read_json(visual_json_path)
                if visual_error or visual_data is None:
                    self.add_issue("Structural", "visual.json parse", "FAIL", page=page_runtime_id, visual=visual_dir.name, details=f"Unable to parse visual.json: {visual_error}")
                    continue
                if visual_bom:
                    self.add_issue("Structural", "visual.json encoding", "FAIL", page=page_runtime_id, visual=visual_dir.name, details="File contains UTF-8 BOM")

                visual_name = visual_data.get("name")
                if visual_name == visual_dir.name:
                    self.add_issue("Structural", "Visual folder/name contract", "PASS", page=page_runtime_id, visual=visual_dir.name)
                else:
                    self.add_issue("Structural", "Visual folder/name contract", "FAIL", page=page_runtime_id, visual=visual_dir.name, details=f"Folder={visual_dir.name}, visual.json.name={visual_name}")

                visual = visual_data.get("visual", {})
                visual_type = visual.get("visualType", "")
                visual_type_counter[visual_type] += 1

                refs: List[Tuple[str, str, str]] = []
                extract_refs(visual_data, refs)
                tables_used = set()
                for entity, prop, ref_type in refs:
                    if ref_type == "Measure":
                        status = "PASS" if prop in self.model_registry.measures else "FAIL"
                        self.add_issue("Field Cross-Reference", "Measure binding", status, page=page_runtime_id, visual=visual_dir.name, details=f"{entity}.{prop}")
                    else:
                        status = "PASS" if entity in self.model_registry.tables and prop in self.model_registry.columns_by_table.get(entity, set()) else "FAIL"
                        self.add_issue("Field Cross-Reference", "Column binding", status, page=page_runtime_id, visual=visual_dir.name, details=f"{entity}.{prop}")
                        tables_used.add(entity)

                if not self.model_registry.is_reachable(tables_used):
                    self.add_issue("Field Cross-Reference", "Relationship reachability", "WARNING", page=page_runtime_id, visual=visual_dir.name, details=f"Tables not fully connected: {sorted(tables_used)}")

                position = visual_data.get("position", {})
                visual_positions.append((visual_dir.name, position, visual_type))
                out_of_bounds = (
                    float(position.get("x", 0)) < 0 or
                    float(position.get("y", 0)) < 0 or
                    float(position.get("x", 0)) + float(position.get("width", 0)) > page_width or
                    float(position.get("y", 0)) + float(position.get("height", 0)) > page_height
                )
                self.add_issue("Accessibility & Best Practices", "Position within bounds", "FAIL" if out_of_bounds else "PASS", page=page_runtime_id, visual=visual_dir.name)

                if visual_type == "slicer":
                    slicer_height = float(position.get("height", 0))
                    status = "PASS" if slicer_height >= 64 else "WARNING"
                    self.add_issue("Accessibility & Best Practices", "Slicer usable height", status, page=page_runtime_id, visual=visual_dir.name, details=f"height={slicer_height}")

                if visual_type == "cardVisual":
                    projections = visual.get("query", {}).get("queryState", {}).get("Data", {}).get("projections", [])
                    if len(projections) > 1:
                        font_size = None
                        for item in visual.get("objects", {}).get("value", []):
                            properties = item.get("properties", {})
                            font_size_expr = properties.get("fontSize", {}).get("expr", {}).get("Literal", {}).get("Value")
                            if font_size_expr:
                                font_size = font_size_expr
                                break
                        status = "PASS" if font_size == "20D" else "WARNING"
                        self.add_issue("Accessibility & Best Practices", "Grouped KPI callout size", status, page=page_runtime_id, visual=visual_dir.name, details=f"fontSize={font_size}")

                if visual_type == "gauge":
                    query_state = visual.get("query", {}).get("queryState", {})
                    status = "PASS" if "Y" in query_state and "TargetValue" in query_state else "FAIL"
                    self.add_issue("Structural", "Gauge query buckets", status, page=page_runtime_id, visual=visual_dir.name)
                elif visual_type == "treemap":
                    query_state = visual.get("query", {}).get("queryState", {})
                    status = "PASS" if "Group" in query_state and "Values" in query_state else "FAIL"
                    self.add_issue("Structural", "Treemap query buckets", status, page=page_runtime_id, visual=visual_dir.name)
                elif visual_type == "azureMap":
                    query_state = visual.get("query", {}).get("queryState", {})
                    objects = visual.get("objects", {})
                    status = "PASS" if "Category" in query_state and "Size" in query_state else "FAIL"
                    self.add_issue("Structural", "Azure Map query buckets", status, page=page_runtime_id, visual=visual_dir.name)
                    object_status = "PASS" if {"mapControls", "bubbleLayer", "filledMap"}.issubset(set(objects.keys())) else "WARNING"
                    self.add_issue("Accessibility & Best Practices", "Azure Map baseline objects", object_status, page=page_runtime_id, visual=visual_dir.name, details=f"Present object groups: {sorted(objects.keys())}")

            for first_index in range(len(visual_positions)):
                for second_index in range(first_index + 1, len(visual_positions)):
                    first_name, first_pos, _ = visual_positions[first_index]
                    second_name, second_pos, _ = visual_positions[second_index]
                    if rects_overlap(first_pos, second_pos):
                        self.add_issue("Accessibility & Best Practices", "Visual overlap", "FAIL", page=page_runtime_id, visual=f"{first_name} <> {second_name}")

        for index, blueprint_page in enumerate(blueprint.get("pages", [])):
            expected_count = len(blueprint_page.get("slicers", [])) + len(blueprint_page.get("visuals", []))
            if index < len(page_order):
                runtime_id = page_order[index]
                actual_count = actual_visual_count_by_page.get(runtime_id, 0)
                status = "PASS" if expected_count == actual_count else "FAIL"
                self.add_issue("Blueprint Compliance", "Visual count per page", status, page=runtime_id, details=f"Expected {expected_count}, actual {actual_count}")

                expected_types = Counter(logical_type_to_pbir("slicer") for _ in blueprint_page.get("slicers", []))
                expected_types.update(logical_type_to_pbir(item.get("visualType", "")) for item in blueprint_page.get("visuals", []))
                actual_types = actual_visual_type_counts_by_page.get(runtime_id, Counter())
                status = "PASS" if expected_types == actual_types else "WARNING"
                self.add_issue("Blueprint Compliance", "Visual type match", status, page=runtime_id, details=f"Expected {dict(expected_types)}, actual {dict(actual_types)}")

        summary = self.build_summary()
        self.write_outputs(blueprint, pages_metadata, summary)
        return 1 if summary["errors"] > 0 else 0

    def build_summary(self) -> Dict[str, Any]:
        warnings = sum(1 for item in self.issues if item.status == "WARNING")
        errors = sum(1 for item in self.issues if item.status == "FAIL")
        passes = sum(1 for item in self.issues if item.status == "PASS")
        overall = "FAIL" if errors > 0 else "WARNINGS" if warnings > 0 else "PASS"
        return {
            "generatedAt": utc_now(),
            "project": self.project_name,
            "overallStatus": overall,
            "passes": passes,
            "warnings": warnings,
            "errors": errors,
            "issues": [asdict(issue) for issue in self.issues],
        }

    def write_outputs(self, blueprint: Dict[str, Any], pages_metadata: Dict[str, Any], summary: Dict[str, Any]) -> None:
        self.tests_path.mkdir(parents=True, exist_ok=True)

        report_lines = [
            f"# Report Quality Validation — {self.project_name}",
            "",
            f"**Generated**: {summary.get('generatedAt', utc_now())}",
            f"**Blueprint**: {self.project_name}/spec/report_blueprint.json",
            f"**Report Path**: {self.project_name}/PBIP/{self.project_name}.Report/definition/",
            "",
            f"## Overall Status: {summary.get('overallStatus', 'FAIL')}",
            "",
            "## Summary",
            f"- Pages validated: {len(pages_metadata.get('pageOrder', []))}/{len(blueprint.get('pages', []))}",
            f"- Issues evaluated: {len(self.issues)}",
            f"- Warnings: {summary.get('warnings', 0)}",
            f"- Errors: {summary.get('errors', 0)}",
            "",
        ]

        for section in [
            "Field Cross-Reference",
            "Blueprint Compliance",
            "Accessibility & Best Practices",
            "Structural",
        ]:
            section_issues = [issue for issue in self.issues if issue.section == section]
            if not section_issues:
                continue
            report_lines.append(f"## {section}")
            report_lines.append("")
            report_lines.append("| # | Check | Page | Visual | Status | Details |")
            report_lines.append("|---|---|---|---|---|---|")
            for index, issue in enumerate(section_issues, start=1):
                report_lines.append(
                    f"| {index} | {issue.check} | {issue.page or '-'} | {issue.visual or '-'} | {issue.status} | {issue.details or '-'} |"
                )
            report_lines.append("")

        recommendations = [
            issue for issue in self.issues if issue.status in {"FAIL", "WARNING"}
        ]
        report_lines.append("## Recommendations")
        report_lines.append("")
        if recommendations:
            for issue in recommendations:
                report_lines.append(f"- [{issue.status}] {issue.check}: {issue.details or issue.visual or issue.page}")
        else:
            report_lines.append("- No remediation actions required.")

        report_lines.append("")
        report_lines.append("## Conclusion")
        report_lines.append("")
        if summary.get("overallStatus") == "PASS":
            report_lines.append("PBIR artifacts are ready for Power BI Desktop validation.")
        elif summary.get("overallStatus") == "WARNINGS":
            report_lines.append("PBIR artifacts are usable but should be reviewed for the warning items above.")
        else:
            report_lines.append("PBIR artifacts require fixes before Power BI Desktop validation.")

        self.report_output_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        self.summary_output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PBIR report artifacts for a project.")
    parser.add_argument("project_name", help="Project folder name, for example SalesOverview")
    parser.add_argument("--verbose", action="store_true", help="Print additional execution details")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validator = PbirValidator(args.project_name, verbose=args.verbose)
    exit_code = validator.validate()
    if args.verbose:
        print(f"Markdown report: {validator.report_output_path}")
        print(f"JSON summary: {validator.summary_output_path}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())