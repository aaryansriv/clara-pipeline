"""
Clara Pipeline — Trello Integration
Creates and updates Trello cards for pipeline task tracking.
Uses Trello REST API (free tier — unlimited boards, lists, cards).

Setup:
1. Create a Trello account (free)
2. Get API key: https://trello.com/app-key
3. Generate a token from the API key page
4. Create a board called "Clara Pipeline" with lists:
   - Inbox, v1 Processing, v1 Ready, v2 Processing, v2 Live, Issues
5. Set environment variables:
   - TRELLO_API_KEY
   - TRELLO_TOKEN
   - TRELLO_BOARD_ID (from board URL)
"""

import os
import json
import logging
import requests
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

TRELLO_BASE_URL = "https://api.trello.com/1"


def _get_trello_auth() -> Optional[dict]:
    """Get Trello auth params."""
    api_key = os.environ.get("TRELLO_API_KEY")
    token = os.environ.get("TRELLO_TOKEN")
    if not api_key or not token:
        logger.info("Trello credentials not configured. Skipping Trello sync.")
        return None
    return {"key": api_key, "token": token}


def _get_board_lists(board_id: str, auth: dict) -> dict:
    """Get all lists on a Trello board, mapped by name."""
    url = f"{TRELLO_BASE_URL}/boards/{board_id}/lists"
    resp = requests.get(url, params=auth)
    resp.raise_for_status()
    return {lst["name"]: lst["id"] for lst in resp.json()}


def _find_card_by_name(board_id: str, search_text: str, auth: dict) -> Optional[dict]:
    """Find a card on the board by name search."""
    url = f"{TRELLO_BASE_URL}/boards/{board_id}/cards"
    resp = requests.get(url, params=auth)
    resp.raise_for_status()
    for card in resp.json():
        if search_text.lower() in card["name"].lower():
            return card
    return None


def create_pipeline_card(
    account_id: str,
    company_name: str,
    pipeline: str,
    unknowns_count: int = 0,
    notes: str = "",
):
    """
    Create a Trello card for a pipeline run.

    Args:
        account_id: Account identifier
        company_name: Company name
        pipeline: "A" (demo) or "B" (onboarding)
        unknowns_count: Number of open items
        notes: Additional context
    """
    auth = _get_trello_auth()
    if not auth:
        _log_locally(account_id, company_name, pipeline, "created", notes)
        return

    board_id = os.environ.get("TRELLO_BOARD_ID")
    if not board_id:
        logger.warning("TRELLO_BOARD_ID not set. Skipping.")
        _log_locally(account_id, company_name, pipeline, "created", notes)
        return

    try:
        lists = _get_board_lists(board_id, auth)

        if pipeline == "A":
            list_name = "v1 Ready"
            card_name = f"{company_name} — v1 Ready"
            label_color = "yellow" if unknowns_count > 0 else "green"
        else:
            list_name = "v2 Live"
            card_name = f"{company_name} — v2 Live"
            label_color = "green" if unknowns_count == 0 else "orange"

        list_id = lists.get(list_name)
        if not list_id:
            logger.warning("List '%s' not found on board. Available: %s", list_name, list(lists.keys()))
            list_id = list(lists.values())[0]  # fallback to first list

        # Check if card already exists
        existing = _find_card_by_name(board_id, company_name, auth)
        if existing and pipeline == "B":
            # Update existing card for Pipeline B
            _update_card(existing["id"], card_name, list_id, unknowns_count, notes, auth)
            return

        # Create new card
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        desc = (
            f"**Account ID:** {account_id}\n"
            f"**Pipeline:** {'Demo → v1' if pipeline == 'A' else 'Onboarding → v2'}\n"
            f"**Status:** {'v1 Ready' if pipeline == 'A' else 'v2 Live'}\n"
            f"**Open Items:** {unknowns_count}\n"
            f"**Processed:** {timestamp}\n"
            f"\n{notes}"
        )

        url = f"{TRELLO_BASE_URL}/cards"
        params = {
            **auth,
            "idList": list_id,
            "name": card_name,
            "desc": desc,
        }
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        logger.info("✅ Trello card created: %s", card_name)

    except Exception as e:
        logger.error("❌ Trello integration failed: %s", e)
        _log_locally(account_id, company_name, pipeline, "created", notes)


def _update_card(card_id, name, list_id, unknowns_count, notes, auth):
    """Update an existing Trello card (for Pipeline B updates)."""
    url = f"{TRELLO_BASE_URL}/cards/{card_id}"
    params = {
        **auth,
        "name": name,
        "idList": list_id,
    }
    resp = requests.put(url, params=params)
    resp.raise_for_status()

    # Add comment
    comment_url = f"{TRELLO_BASE_URL}/cards/{card_id}/actions/comments"
    comment_params = {
        **auth,
        "text": (
            f"🔄 **Pipeline B complete** — v2 agent generated.\n"
            f"Remaining unknowns: {unknowns_count}\n"
            f"{notes}"
        ),
    }
    requests.post(comment_url, params=comment_params)
    logger.info("✅ Trello card updated: %s", name)


def _log_locally(account_id, company_name, pipeline, action, notes):
    """Fallback: log Trello actions locally when API is unavailable."""
    from pathlib import Path

    log_path = Path(__file__).parent.parent / "outputs" / "trello_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entries = []
    if log_path.exists():
        with open(log_path) as f:
            entries = json.load(f)

    entries.append({
        "account_id": account_id,
        "company_name": company_name,
        "pipeline": pipeline,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        "notes": notes,
    })

    with open(log_path, "w") as f:
        json.dump(entries, f, indent=2)

    logger.info("📄 Trello action logged locally: %s", log_path)
