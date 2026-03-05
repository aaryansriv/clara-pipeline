"""
Clara Pipeline — Google Sheets Integration
Syncs pipeline results to a Google Sheet for tracking and reporting.
Uses Google Sheets API v4 with service account (free).

Setup:
1. Create a Google Cloud project (free)
2. Enable Google Sheets API
3. Create a service account and download credentials JSON
4. Share your Google Sheet with the service account email
5. Set GOOGLE_SHEETS_CREDENTIALS env var to the path of the JSON file
6. Set GOOGLE_SHEET_ID env var to the spreadsheet ID
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs" / "accounts"


def _get_sheets_service():
    """Initialize Google Sheets API service."""
    try:
        from googleapiclient.discovery import build
        from google.oauth2.service_account import Credentials
    except ImportError:
        logger.warning(
            "Google Sheets dependencies not installed. "
            "Run: pip install google-api-python-client google-auth"
        )
        return None

    creds_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    if not creds_path:
        logger.warning("GOOGLE_SHEETS_CREDENTIALS not set. Skipping Sheets sync.")
        return None

    creds = Credentials.from_service_account_file(
        creds_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=creds)


def sync_account_to_sheets(
    account_id: str,
    company_name: str,
    pipeline: str,
    status: str,
    unknowns_count: int,
    notes: str = "",
    sheet_id: Optional[str] = None,
):
    """
    Sync a single account result to Google Sheets.

    Args:
        account_id: Account identifier
        company_name: Company name
        pipeline: "A" or "B"
        status: "v1 Ready", "v2 Ready", "Failed", etc.
        unknowns_count: Number of unresolved items
        notes: Additional notes
        sheet_id: Google Sheet ID (uses env var if not provided)
    """
    service = _get_sheets_service()
    if not service:
        logger.info("Sheets sync skipped (no credentials configured)")
        _log_to_local_csv(account_id, company_name, pipeline, status, unknowns_count, notes)
        return

    sheet_id = sheet_id or os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        logger.warning("GOOGLE_SHEET_ID not set. Skipping Sheets sync.")
        _log_to_local_csv(account_id, company_name, pipeline, status, unknowns_count, notes)
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    output_path = str(OUTPUTS_DIR / account_id / ("v2" if pipeline == "B" else "v1"))

    row = [account_id, company_name, pipeline, status, timestamp, unknowns_count, output_path, notes]

    try:
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="Sheet1!A:H",
            valueInputOption="USER_ENTERED",
            body={"values": [row]},
        ).execute()
        logger.info("✅ Synced %s to Google Sheets", account_id)
    except Exception as e:
        logger.error("❌ Failed to sync to Sheets: %s", e)
        _log_to_local_csv(account_id, company_name, pipeline, status, unknowns_count, notes)


def sync_batch_summary_to_sheets(summary: dict, sheet_id: Optional[str] = None):
    """Sync a full batch summary to Google Sheets."""
    service = _get_sheets_service()
    if not service:
        logger.info("Sheets sync skipped for batch summary")
        return

    sheet_id = sheet_id or os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        return

    # Write summary to a "Summary" sheet tab
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    rows = [
        ["Batch Run Summary", timestamp],
        ["Pipeline A Success", summary.get("pipeline_a", {}).get("success", 0)],
        ["Pipeline A Failed", summary.get("pipeline_a", {}).get("failed", 0)],
        ["Pipeline B Success", summary.get("pipeline_b", {}).get("success", 0)],
        ["Pipeline B Failed", summary.get("pipeline_b", {}).get("failed", 0)],
    ]

    try:
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="Summary!A:B",
            valueInputOption="USER_ENTERED",
            body={"values": rows},
        ).execute()
        logger.info("✅ Batch summary synced to Google Sheets")
    except Exception as e:
        logger.error("❌ Failed to sync batch summary: %s", e)


def _log_to_local_csv(account_id, company_name, pipeline, status, unknowns, notes):
    """Fallback: log results to a local CSV when Sheets is unavailable."""
    csv_path = Path(__file__).parent.parent / "outputs" / "pipeline_log.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    write_header = not csv_path.exists()

    with open(csv_path, "a", encoding="utf-8") as f:
        if write_header:
            f.write("account_id,company_name,pipeline,status,timestamp,unknowns,notes\n")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        f.write(f"{account_id},{company_name},{pipeline},{status},{timestamp},{unknowns},{notes}\n")

    logger.info("📄 Logged to local CSV: %s", csv_path)
