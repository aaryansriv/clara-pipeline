"""
Clara Pipeline A — Demo Call → v1 Account Memo + Agent Spec
Usage: python pipeline_a.py --transcript path/to/transcript.txt --account-id ACC001
"""

import os
import sys
import json
import logging
import argparse
import re
from pathlib import Path
from datetime import datetime

from groq import Groq

from schema import AccountMemo, BusinessHours, RoutingRule, CallTransferRules, slugify
from extractor import extract_from_transcript
from prompt_generator import generate_agent_spec

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs" / "accounts"


def build_account_memo(extracted: dict, account_id: str) -> AccountMemo:
    """Map raw extraction dict to AccountMemo dataclass."""
    bh_data = extracted.get("business_hours") or {}
    business_hours = BusinessHours(
        days=bh_data.get("days") or [],
        start=bh_data.get("start"),
        end=bh_data.get("end"),
        timezone=bh_data.get("timezone"),
    ) if bh_data else None

    routing_raw = extracted.get("emergency_routing_rules") or []
    routing_rules = [
        RoutingRule(
            name=r.get("name"),
            phone=r.get("phone"),
            order=r.get("order", 1),
            fallback=r.get("fallback"),
        )
        for r in routing_raw
    ]

    ct_data = extracted.get("call_transfer_rules") or {}
    call_transfer = CallTransferRules(
        timeout_seconds=ct_data.get("timeout_seconds"),
        retries=ct_data.get("retries"),
        message_if_fails=ct_data.get("message_if_fails"),
    ) if ct_data else None

    return AccountMemo(
        account_id=account_id,
        company_name=extracted.get("company_name") or "",
        owner_name=extracted.get("owner_name"),
        business_hours=business_hours,
        office_address=extracted.get("office_address"),
        services_supported=extracted.get("services_supported") or [],
        emergency_definition=extracted.get("emergency_definition") or [],
        emergency_routing_rules=routing_rules,
        non_emergency_routing_rules=extracted.get("non_emergency_routing_rules"),
        call_transfer_rules=call_transfer,
        integration_constraints=extracted.get("integration_constraints") or [],
        after_hours_flow_summary=extracted.get("after_hours_flow_summary"),
        office_hours_flow_summary=extracted.get("office_hours_flow_summary"),
        pricing_info=extracted.get("pricing_info"),
        notification_channels=extracted.get("notification_channels"),
        questions_or_unknowns=extracted.get("questions_or_unknowns") or [],
        notes=extracted.get("notes"),
        version="v1",
    )


def save_outputs(memo: AccountMemo, agent_spec, account_id: str):
    """Save memo JSON, agent spec JSON, and Retell import guide."""
    output_dir = OUTPUTS_DIR / account_id / "v1"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save account memo
    memo_path = output_dir / "account_memo_v1.json"
    with open(memo_path, "w") as f:
        f.write(memo.to_json())
    logger.info("Saved memo → %s", memo_path)

    # Save agent spec
    spec_path = output_dir / "agent_spec_v1.json"
    with open(spec_path, "w") as f:
        f.write(agent_spec.to_json())
    logger.info("Saved agent spec → %s", spec_path)

    # Save Retell import guide
    guide_path = output_dir / "retell_import_guide.md"
    guide_content = f"""# Retell Import Guide — {memo.company_name} (v1)

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## How to Configure This Agent in Retell UI

1. Log in to [app.retellai.com](https://app.retellai.com)
2. Click **Create Agent** → choose **Custom LLM** or **Retell LLM**
3. Set **Agent Name**: `{agent_spec.agent_name}`
4. Set **Voice**: Professional Female (warm tone recommended)
5. Paste the contents of `agent_spec_v1.json` → field `system_prompt` into the **System Prompt** box
6. Configure **Call Transfer**:
   - Timeout: {memo.call_transfer_rules.timeout_seconds if memo.call_transfer_rules else 'TBD'} seconds
   - Transfer numbers: See `key_variables.emergency_routing` in agent spec
7. Set **Post-Call Webhook** to your notification endpoint (email/SMS)
8. Click **Save & Test**

## ⚠️ Outstanding Items Before Going Live
{chr(10).join(f'- {q}' for q in memo.questions_or_unknowns) if memo.questions_or_unknowns else '- None. Ready to go live.'}

## Version
- This is **v1** (generated from demo call)
- After onboarding call, run Pipeline B to generate v2
"""
    with open(guide_path, "w") as f:
        f.write(guide_content)
    logger.info("Saved Retell guide → %s", guide_path)

    return output_dir


def run_pipeline_a(transcript_path: str, account_id: str = None):
    """Full Pipeline A execution."""
    logger.info("=" * 60)
    logger.info("PIPELINE A — Demo Call → v1 Agent")
    logger.info("Transcript: %s", transcript_path)

    # Read transcript
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    logger.info("Transcript loaded (%d chars)", len(transcript))

    # Init Groq client
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    client = Groq(api_key=api_key)

    # Step 1: Extract
    logger.info("Step 1: Extracting structured data via Groq...")
    extracted = extract_from_transcript(transcript, client=client)

    # Step 2: Build account_id if not provided
    if not account_id:
        company = extracted.get("company_name") or "unknown"
        account_id = slugify(company)
        logger.info("Auto-generated account_id: %s", account_id)

    # Step 3: Build memo
    logger.info("Step 2: Building AccountMemo...")
    memo = build_account_memo(extracted, account_id)

    # Step 4: Generate agent spec
    logger.info("Step 3: Generating Retell Agent Spec...")
    agent_spec = generate_agent_spec(memo)

    # Step 5: Save outputs
    logger.info("Step 4: Saving outputs...")
    output_dir = save_outputs(memo, agent_spec, account_id)

    logger.info("=" * 60)
    logger.info("✅ Pipeline A complete!")
    logger.info("Account ID: %s", account_id)
    logger.info("Output dir: %s", output_dir)
    logger.info("Unknowns flagged: %d", len(memo.questions_or_unknowns))
    logger.info("=" * 60)

    return memo, agent_spec


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline A: Demo Call → v1 Agent")
    parser.add_argument("--transcript", required=True, help="Path to transcript file")
    parser.add_argument("--account-id", default=None, help="Account ID (auto-generated if omitted)")
    args = parser.parse_args()

    run_pipeline_a(args.transcript, args.account_id)
