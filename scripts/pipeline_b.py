"""
Clara Pipeline B — Onboarding Call → v2 Account Memo + Agent Spec + Changelog
Usage: python pipeline_b.py --transcript path/to/onboarding.txt --account-id ACC001
       python pipeline_b.py --transcript path/to/onboarding.m4a --account-id ACC001
"""

import os
import json
import logging
import argparse
import copy
from pathlib import Path
from datetime import datetime

from groq import Groq

from schema import AccountMemo, BusinessHours, RoutingRule, CallTransferRules
from extractor import extract_onboarding_patch, transcribe_audio_if_needed
from prompt_generator import generate_agent_spec
from pipeline_a import build_account_memo, OUTPUTS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def load_v1_memo(account_id: str) -> AccountMemo:
    """Load existing v1 account memo from disk."""
    memo_path = OUTPUTS_DIR / account_id / "v1" / "account_memo_v1.json"
    if not memo_path.exists():
        raise FileNotFoundError(
            f"No v1 memo found at {memo_path}. Run Pipeline A first."
        )
    with open(memo_path) as f:
        data = json.load(f)
    return AccountMemo.from_dict(data)


def deep_diff(v1: dict, v2: dict, path="") -> list:
    """Recursively compute differences between two dicts."""
    changes = []
    all_keys = set(list(v1.keys()) + list(v2.keys()))
    for key in all_keys:
        full_path = f"{path}.{key}" if path else key
        v1_val = v1.get(key)
        v2_val = v2.get(key)
        if v1_val == v2_val:
            continue
        if isinstance(v1_val, dict) and isinstance(v2_val, dict):
            changes.extend(deep_diff(v1_val, v2_val, full_path))
        else:
            changes.append({
                "field": full_path,
                "old_value": v1_val,
                "new_value": v2_val,
            })
    return changes


def apply_patch(v1_memo: AccountMemo, patch: dict) -> AccountMemo:
    """Apply onboarding patch onto v1 memo to produce v2 memo."""
    v1_dict = v1_memo.to_dict()
    v2_dict = copy.deepcopy(v1_dict)

    # Apply top-level scalar fields
    scalar_fields = [
        "company_name", "owner_name", "office_address",
        "non_emergency_routing_rules", "after_hours_flow_summary",
        "office_hours_flow_summary", "notes"
    ]
    for field in scalar_fields:
        if field in patch and patch[field] is not None:
            v2_dict[field] = patch[field]

    # Apply list fields (replace if present)
    list_fields = [
        "services_supported", "emergency_definition",
        "integration_constraints"
    ]
    for field in list_fields:
        if field in patch and patch[field]:
            v2_dict[field] = patch[field]

    # Apply nested business_hours
    if "business_hours" in patch and patch["business_hours"]:
        bh_patch = patch["business_hours"]
        if v2_dict.get("business_hours") is None:
            v2_dict["business_hours"] = {}
        for k, v in bh_patch.items():
            if v is not None:
                v2_dict["business_hours"][k] = v

    # Apply emergency routing (replace if present)
    if "emergency_routing_rules" in patch and patch["emergency_routing_rules"]:
        v2_dict["emergency_routing_rules"] = patch["emergency_routing_rules"]

    # Apply call transfer rules
    if "call_transfer_rules" in patch and patch["call_transfer_rules"]:
        ct_patch = patch["call_transfer_rules"]
        if v2_dict.get("call_transfer_rules") is None:
            v2_dict["call_transfer_rules"] = {}
        for k, v in ct_patch.items():
            if v is not None:
                v2_dict["call_transfer_rules"][k] = v

    # Apply pricing_info
    if "pricing_info" in patch and patch["pricing_info"]:
        if v2_dict.get("pricing_info") is None:
            v2_dict["pricing_info"] = {}
        for k, v in patch["pricing_info"].items():
            if v is not None:
                v2_dict["pricing_info"][k] = v

    # Apply notification_channels
    if "notification_channels" in patch and patch["notification_channels"]:
        if v2_dict.get("notification_channels") is None:
            v2_dict["notification_channels"] = {}
        for k, v in patch["notification_channels"].items():
            if v is not None:
                v2_dict["notification_channels"][k] = v

    # Merge questions_or_unknowns: remove resolved ones, add new ones
    existing_unknowns = set(v2_dict.get("questions_or_unknowns") or [])
    patch_unknowns = set(patch.get("questions_or_unknowns") or [])
    # Keep unknowns that weren't resolved (still in patch) + add new ones
    merged_unknowns = list(existing_unknowns | patch_unknowns)
    v2_dict["questions_or_unknowns"] = merged_unknowns

    # Update version and timestamp
    v2_dict["version"] = "v2"
    v2_dict["updated_at"] = datetime.utcnow().isoformat()

    return AccountMemo.from_dict(v2_dict)


def generate_changelog(v1_memo: AccountMemo, v2_memo: AccountMemo,
                       patch: dict, account_id: str) -> str:
    """Generate a human-readable changelog markdown file."""
    v1_dict = v1_memo.to_dict()
    v2_dict = v2_memo.to_dict()
    diffs = deep_diff(v1_dict, v2_dict)
    llm_notes = patch.get("changelog_notes", "No additional notes from extraction.")

    lines = [
        f"# Changelog — {v2_memo.company_name}",
        f"**Account ID:** {account_id}",
        f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Version:** v1 → v2",
        "",
        "## Summary",
        f"Onboarding call completed. Agent configuration updated with confirmed operational details.",
        "",
        "## LLM Extraction Notes",
        llm_notes,
        "",
        "## Field-Level Changes",
    ]

    if diffs:
        for diff in diffs:
            field = diff["field"]
            old = diff["old_value"]
            new = diff["new_value"]
            # Skip internal timestamps
            if field in ["updated_at", "version", "created_at"]:
                continue
            lines.append(f"\n### `{field}`")
            lines.append(f"- **Before (v1):** `{old}`")
            lines.append(f"- **After (v2):** `{new}`")
    else:
        lines.append("\nNo structural field changes detected.")

    lines += [
        "",
        "## Outstanding Items After Onboarding",
    ]
    if v2_memo.questions_or_unknowns:
        for q in v2_memo.questions_or_unknowns:
            lines.append(f"- ⚠️ {q}")
    else:
        lines.append("- ✅ All items resolved. Agent is production-ready.")

    return "\n".join(lines)


def save_v2_outputs(v1_memo: AccountMemo, v2_memo: AccountMemo,
                    agent_spec, patch: dict, account_id: str):
    """Save v2 memo, agent spec, and changelog."""
    output_dir = OUTPUTS_DIR / account_id / "v2"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save v2 memo
    memo_path = output_dir / "account_memo_v2.json"
    with open(memo_path, "w", encoding="utf-8") as f:
        f.write(v2_memo.to_json())
    logger.info("Saved v2 memo → %s", memo_path)

    # Save v2 agent spec
    spec_path = output_dir / "agent_spec_v2.json"
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(agent_spec.to_json())
    logger.info("Saved v2 agent spec → %s", spec_path)

    # Save changelog
    changelog_md = generate_changelog(v1_memo, v2_memo, patch, account_id)
    changelog_path = output_dir / "changes.md"
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(changelog_md)
    logger.info("Saved changelog → %s", changelog_path)

    # Also save changelog JSON for the dashboard
    changelog_json_path = output_dir / "changes.json"
    v1_dict = v1_memo.to_dict()
    v2_dict = v2_memo.to_dict()
    diffs = deep_diff(v1_dict, v2_dict)
    with open(changelog_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "account_id": account_id,
            "company_name": v2_memo.company_name,
            "date": datetime.utcnow().isoformat(),
            "version_from": "v1",
            "version_to": "v2",
            "changes": [d for d in diffs if d["field"] not in ["updated_at", "version", "created_at"]],
            "outstanding_items": v2_memo.questions_or_unknowns,
            "llm_notes": patch.get("changelog_notes", ""),
        }, f, indent=2)
    logger.info("Saved changelog JSON → %s", changelog_json_path)

    return output_dir


def run_pipeline_b(transcript_path: str, account_id: str):
    """Full Pipeline B execution."""
    logger.info("=" * 60)
    logger.info("PIPELINE B — Onboarding Call → v2 Agent")
    logger.info("Account ID: %s", account_id)
    logger.info("Input: %s", transcript_path)

    # Load v1 memo
    logger.info("Step 1: Loading v1 memo...")
    v1_memo = load_v1_memo(account_id)
    logger.info("Loaded v1 memo for: %s", v1_memo.company_name)

    # Init Groq
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    client = Groq(api_key=api_key)

    # Handle audio transcription if needed
    logger.info("Step 1.5: Loading input (auto-detecting audio vs text)...")
    transcript = transcribe_audio_if_needed(transcript_path, client)
    logger.info("Onboarding transcript ready (%d chars)", len(transcript))

    # Extract patch
    logger.info("Step 2: Extracting onboarding updates via Groq...")
    patch = extract_onboarding_patch(transcript, v1_memo.to_dict(), client=client)

    # Apply patch
    logger.info("Step 3: Applying patch to produce v2 memo...")
    v2_memo = apply_patch(v1_memo, patch)

    # Generate v2 agent spec
    logger.info("Step 4: Generating v2 Retell Agent Spec...")
    agent_spec = generate_agent_spec(v2_memo)

    # Save outputs
    logger.info("Step 5: Saving v2 outputs and changelog...")
    output_dir = save_v2_outputs(v1_memo, v2_memo, agent_spec, patch, account_id)

    # Sync to integrations
    logger.info("Step 6: Syncing to integrations...")
    try:
        from sheets_integration import sync_account_to_sheets
        sync_account_to_sheets(
            account_id=account_id,
            company_name=v2_memo.company_name,
            pipeline="B",
            status="v2 Ready",
            unknowns_count=len(v2_memo.questions_or_unknowns),
            notes="Onboarding complete. Changelog generated.",
        )
    except Exception as e:
        logger.debug("Sheets sync skipped: %s", e)

    try:
        from trello_integration import create_pipeline_card
        create_pipeline_card(
            account_id=account_id,
            company_name=v2_memo.company_name,
            pipeline="B",
            unknowns_count=len(v2_memo.questions_or_unknowns),
            notes="v2 agent generated from onboarding call.",
        )
    except Exception as e:
        logger.debug("Trello sync skipped: %s", e)

    logger.info("=" * 60)
    logger.info("✅ Pipeline B complete!")
    logger.info("Account ID: %s", account_id)
    logger.info("Output dir: %s", output_dir)
    logger.info("Remaining unknowns: %d", len(v2_memo.questions_or_unknowns))
    logger.info("=" * 60)

    return v2_memo, agent_spec


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline B: Onboarding Call → v2 Agent")
    parser.add_argument("--transcript", required=True, help="Path to onboarding transcript")
    parser.add_argument("--account-id", required=True, help="Account ID (must match v1)")
    args = parser.parse_args()

    run_pipeline_b(args.transcript, args.account_id)
