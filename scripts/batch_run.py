"""
Clara Pipeline — Batch Runner
Runs Pipeline A on all demo transcripts, then Pipeline B on all onboarding transcripts.
Usage: python batch_run.py
       python batch_run.py --only-a   (run only Pipeline A)
       python batch_run.py --only-b   (run only Pipeline B)
"""

import os
import sys
import json
import logging
import argparse
import time
import traceback
from pathlib import Path
from datetime import datetime

from pipeline_a import run_pipeline_a
from pipeline_b import run_pipeline_b

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data" / "transcripts"
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"

# Dataset manifest — maps account_id to transcript files
DATASET = [
    {
        "account_id": "bens-electric-solutions",
        "company_name": "Ben's Electric Solutions",
        "demo_transcript": DATA_DIR / "demo" / "bens_electric_demo.txt",
        "onboarding_transcript": DATA_DIR / "onboarding" / "bens_electric_onboarding.txt",
    },
    {
        "account_id": "apex-fire-protection",
        "company_name": "Apex Fire Protection",
        "demo_transcript": DATA_DIR / "demo" / "apex_fire_demo.txt",
        "onboarding_transcript": DATA_DIR / "onboarding" / "apex_fire_onboarding.txt",
    },
    {
        "account_id": "shield-sprinkler-co",
        "company_name": "Shield Sprinkler Co.",
        "demo_transcript": DATA_DIR / "demo" / "shield_sprinkler_demo.txt",
        "onboarding_transcript": DATA_DIR / "onboarding" / "shield_sprinkler_onboarding.txt",
    },
    {
        "account_id": "blazeguard-alarms",
        "company_name": "BlazeGuard Alarms",
        "demo_transcript": DATA_DIR / "demo" / "blazeguard_demo.txt",
        "onboarding_transcript": DATA_DIR / "onboarding" / "blazeguard_onboarding.txt",
    },
    {
        "account_id": "peakfire-services",
        "company_name": "PeakFire Services",
        "demo_transcript": DATA_DIR / "demo" / "peakfire_demo.txt",
        "onboarding_transcript": DATA_DIR / "onboarding" / "peakfire_onboarding.txt",
    },
]


def run_batch_a(dataset: list) -> dict:
    """Run Pipeline A on all demo transcripts."""
    results = {"success": [], "failed": []}

    logger.info("=" * 60)
    logger.info("BATCH PIPELINE A — %d accounts", len(dataset))
    logger.info("=" * 60)

    for i, account in enumerate(dataset, 1):
        account_id = account["account_id"]
        transcript_path = account["demo_transcript"]

        logger.info("\n[%d/%d] Processing: %s", i, len(dataset), account_id)

        if not Path(transcript_path).exists():
            logger.warning("⚠️  Demo transcript not found: %s", transcript_path)
            results["failed"].append({
                "account_id": account_id,
                "pipeline": "A",
                "error": f"Transcript not found: {transcript_path}"
            })
            continue

        try:
            memo, spec = run_pipeline_a(str(transcript_path), account_id)
            results["success"].append({
                "account_id": account_id,
                "pipeline": "A",
                "company_name": memo.company_name,
                "unknowns": len(memo.questions_or_unknowns),
            })
            # Rate limit protection for Groq free tier
            if i < len(dataset):
                time.sleep(2)

        except Exception as e:
            logger.error("❌ Pipeline A failed for %s: %s", account_id, e)
            logger.debug(traceback.format_exc())
            results["failed"].append({
                "account_id": account_id,
                "pipeline": "A",
                "error": str(e)
            })

    return results


def run_batch_b(dataset: list) -> dict:
    """Run Pipeline B on all onboarding transcripts."""
    results = {"success": [], "failed": []}

    logger.info("=" * 60)
    logger.info("BATCH PIPELINE B — %d accounts", len(dataset))
    logger.info("=" * 60)

    for i, account in enumerate(dataset, 1):
        account_id = account["account_id"]
        transcript_path = account["onboarding_transcript"]

        logger.info("\n[%d/%d] Processing: %s", i, len(dataset), account_id)

        if not Path(transcript_path).exists():
            logger.warning("⚠️  Onboarding transcript not found: %s", transcript_path)
            results["failed"].append({
                "account_id": account_id,
                "pipeline": "B",
                "error": f"Transcript not found: {transcript_path}"
            })
            continue

        # Check v1 exists
        v1_path = OUTPUTS_DIR / "accounts" / account_id / "v1" / "account_memo_v1.json"
        if not v1_path.exists():
            logger.warning("⚠️  v1 memo not found for %s — run Pipeline A first", account_id)
            results["failed"].append({
                "account_id": account_id,
                "pipeline": "B",
                "error": "v1 memo not found. Run Pipeline A first."
            })
            continue

        try:
            memo, spec = run_pipeline_b(str(transcript_path), account_id)
            results["success"].append({
                "account_id": account_id,
                "pipeline": "B",
                "company_name": memo.company_name,
                "remaining_unknowns": len(memo.questions_or_unknowns),
            })
            if i < len(dataset):
                time.sleep(2)

        except Exception as e:
            logger.error("❌ Pipeline B failed for %s: %s", account_id, e)
            logger.debug(traceback.format_exc())
            results["failed"].append({
                "account_id": account_id,
                "pipeline": "B",
                "error": str(e)
            })

    return results


def save_batch_summary(a_results: dict, b_results: dict):
    """Save a batch run summary JSON."""
    summary = {
        "batch_run_at": datetime.utcnow().isoformat(),
        "pipeline_a": {
            "total": len(a_results["success"]) + len(a_results["failed"]),
            "success": len(a_results["success"]),
            "failed": len(a_results["failed"]),
            "results": a_results
        },
        "pipeline_b": {
            "total": len(b_results["success"]) + len(b_results["failed"]),
            "success": len(b_results["success"]),
            "failed": len(b_results["failed"]),
            "results": b_results
        }
    }

    summary_path = OUTPUTS_DIR / "batch_summary.json"
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info("\n📊 Batch Summary saved → %s", summary_path)
    logger.info("Pipeline A: %d/%d success", len(a_results["success"]),
                len(a_results["success"]) + len(a_results["failed"]))
    logger.info("Pipeline B: %d/%d success", len(b_results["success"]),
                len(b_results["success"]) + len(b_results["failed"]))

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch run Clara pipelines")
    parser.add_argument("--only-a", action="store_true", help="Run only Pipeline A")
    parser.add_argument("--only-b", action="store_true", help="Run only Pipeline B")
    parser.add_argument("--account", default=None, help="Run single account by ID")
    args = parser.parse_args()

    dataset = DATASET
    if args.account:
        dataset = [d for d in DATASET if d["account_id"] == args.account]
        if not dataset:
            logger.error("Account ID not found: %s", args.account)
            sys.exit(1)

    a_results = {"success": [], "failed": []}
    b_results = {"success": [], "failed": []}

    if not args.only_b:
        a_results = run_batch_a(dataset)

    if not args.only_a:
        b_results = run_batch_b(dataset)

    save_batch_summary(a_results, b_results)
