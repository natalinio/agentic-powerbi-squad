#!/usr/bin/env python3

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_KEEP_TASKS = 10
OPEN_STATUSES = {"open", "pending", "pending-user", "in-progress", "blocked"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_state(state_path: Path) -> dict:
    if not state_path.exists():
        raise FileNotFoundError(f"State file not found: {state_path}")

    with state_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_open_items(state: dict) -> list:
    open_items = state.get("openItems", [])
    return [item for item in open_items if item.get("status") in OPEN_STATUSES]


def normalize_recent_tasks(state: dict, keep_tasks: int) -> list:
    recent_tasks = state.get("recentTasks", [])
    persisted_tasks = [task for task in recent_tasks if task.get("persisted") is True]
    persisted_tasks.sort(key=lambda task: task.get("timestamp", ""), reverse=True)
    return persisted_tasks[:keep_tasks]


def refresh_summary(state: dict, recent_tasks: list, open_items: list) -> dict:
    current_summary = state.get("summary", {})
    latest_task = recent_tasks[0] if recent_tasks else {}

    return {
        "lastAgent": latest_task.get("agent", current_summary.get("lastAgent")),
        "lastTaskType": latest_task.get("taskType", current_summary.get("lastTaskType")),
        "lastOutcome": latest_task.get("status", current_summary.get("lastOutcome", "unknown")),
        "openHandOffRequired": any(
            task.get("handoff", {}).get("required") is True for task in recent_tasks
        ) or any(item.get("recommendedNextAgent") for item in open_items),
    }


def compact_state(state: dict, keep_tasks: int) -> dict:
    open_items = normalize_open_items(state)
    recent_tasks = normalize_recent_tasks(state, keep_tasks)

    state["openItems"] = open_items
    state["recentTasks"] = recent_tasks
    state["summary"] = refresh_summary(state, recent_tasks, open_items)
    state["lastUpdatedAt"] = utc_now()
    return state


def write_state(state_path: Path, state: dict) -> None:
    with state_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(state, handle, indent=2)
        handle.write("\n")


def resolve_state_path(project_root: Path, explicit_state_path: str | None) -> Path:
    if explicit_state_path:
        return Path(explicit_state_path).resolve()
    return (project_root / "agent_session_state.json").resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compact agent_session_state.json using bounded retention rules."
    )
    parser.add_argument("project", help="Path to the project root folder.")
    parser.add_argument(
        "--state-path",
        help="Optional explicit path to agent_session_state.json. Defaults to <project>/agent_session_state.json.",
    )
    parser.add_argument(
        "--keep-tasks",
        type=int,
        default=DEFAULT_KEEP_TASKS,
        help=f"Maximum number of persisted recentTasks to keep. Default: {DEFAULT_KEEP_TASKS}.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the compacted JSON to stdout instead of writing the file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project).resolve()
    state_path = resolve_state_path(project_root, args.state_path)

    state = load_state(state_path)
    compacted_state = compact_state(state, args.keep_tasks)

    if args.dry_run:
        print(json.dumps(compacted_state, indent=2))
        return 0

    write_state(state_path, compacted_state)
    print(f"Compacted standalone continuity state: {state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())