"""
Clara Pipeline — Task Tracker (Google Sheets-based)
Replaces Trello with a second Google Sheets tab for simplicity.
Falls back to a local JSON log when Sheets is unavailable.

Instead of a separate Trello board, tasks are tracked in a "Tasks" tab
in the same Google Sheet used for pipeline logging.

Task statuses: Inbox → v1 Processing → v1 Ready → v2 Processing → v2 Live → Issues
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

LOG_PATH = Path(__file__).parent.parent / "outputs" / "task_tracker.json"


def _load_tasks() -> list:
    """Load tasks from local JSON."""
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_tasks(tasks: list):
    """Save tasks to local JSON."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def update_task(
    account_id: str,
    company_name: str,
    pipeline: str,
    status: str,
    unknowns_count: int = 0,
    notes: str = "",
):
    """
    Create or update a task for an account.

    Status progression:
      Pipeline A: Inbox → v1 Processing → v1 Ready
      Pipeline B: v2 Processing → v2 Live

    Args:
        account_id: Account identifier
        company_name: Company name
        pipeline: "A" or "B"
        status: Current status (e.g., "v1 Ready", "v2 Live")
        unknowns_count: Number of unresolved items
        notes: Additional context
    """
    tasks = _load_tasks()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # Find existing task for this account
    existing = None
    for task in tasks:
        if task["account_id"] == account_id:
            existing = task
            break

    if existing:
        # Update existing task
        existing["status"] = status
        existing["pipeline"] = pipeline
        existing["unknowns"] = unknowns_count
        existing["updated_at"] = timestamp
        existing["notes"] = notes
        existing["history"].append({
            "status": status,
            "pipeline": pipeline,
            "timestamp": timestamp,
            "notes": notes,
        })
        logger.info("Updated task: %s → %s", account_id, status)
    else:
        # Create new task
        tasks.append({
            "account_id": account_id,
            "company_name": company_name,
            "status": status,
            "pipeline": pipeline,
            "unknowns": unknowns_count,
            "created_at": timestamp,
            "updated_at": timestamp,
            "notes": notes,
            "history": [{
                "status": status,
                "pipeline": pipeline,
                "timestamp": timestamp,
                "notes": notes,
            }],
        })
        logger.info("Created task: %s → %s", account_id, status)

    _save_tasks(tasks)

    # Also try to sync to Google Sheets "Tasks" tab
    _sync_to_sheets(account_id, company_name, pipeline, status, unknowns_count, timestamp, notes)


def _sync_to_sheets(account_id, company_name, pipeline, status, unknowns, timestamp, notes):
    """Sync task to Google Sheets 'Tasks' tab (optional — graceful if unavailable)."""
    try:
        from sheets_integration import _get_sheets_service
        service = _get_sheets_service()
        if not service:
            return

        sheet_id = os.environ.get("GOOGLE_SHEET_ID")
        if not sheet_id:
            return

        row = [account_id, company_name, pipeline, status, unknowns, timestamp, notes]

        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="Tasks!A:G",
            valueInputOption="USER_ENTERED",
            body={"values": [row]},
        ).execute()
        logger.info("Synced task to Google Sheets: %s", account_id)

    except Exception as e:
        logger.debug("Sheets task sync skipped: %s", e)


def get_all_tasks() -> list:
    """Get all tasks, sorted by status."""
    tasks = _load_tasks()
    status_order = ["Inbox", "v1 Processing", "v1 Ready", "v2 Processing", "v2 Live", "Issues"]
    tasks.sort(key=lambda t: (
        status_order.index(t["status"]) if t["status"] in status_order else 99,
        t["account_id"]
    ))
    return tasks


def get_task_summary() -> dict:
    """Get a summary of task statuses."""
    tasks = _load_tasks()
    summary = {}
    for task in tasks:
        status = task["status"]
        summary[status] = summary.get(status, 0) + 1
    return {
        "total": len(tasks),
        "statuses": summary,
        "tasks": tasks,
    }


def print_board():
    """Print a text-based task board (like a simple Trello view)."""
    tasks = _load_tasks()
    statuses = ["v1 Ready", "v2 Live", "Issues"]

    print("\n" + "=" * 60)
    print("  CLARA PIPELINE — TASK BOARD")
    print("=" * 60)

    for status in statuses:
        matching = [t for t in tasks if t["status"] == status]
        print(f"\n  [{status}] ({len(matching)} items)")
        print("  " + "-" * 40)
        for t in matching:
            unknowns_str = f" ⚠ {t['unknowns']} unknowns" if t["unknowns"] > 0 else " ✓ complete"
            print(f"    • {t['company_name']}{unknowns_str}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_board()
