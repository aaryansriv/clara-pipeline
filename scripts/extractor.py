"""
Clara Pipeline — LLM Extraction Module
Uses Groq (free tier) to extract structured data from demo and onboarding transcripts.
Includes Whisper transcription support for audio files.
"""

import json
import logging
import time
import os
from typing import Optional

logger = logging.getLogger(__name__)

# ─── EXTRACTION PROMPTS ──────────────────────────────────────────────────────

DEMO_EXTRACTION_PROMPT = """You are a data extraction specialist for Clara AI, an AI voice receptionist for trades businesses.

Analyze the following DEMO CALL transcript between a Clara sales representative and a potential client.
Extract ONLY information that is EXPLICITLY stated in the transcript. Do NOT invent or assume any details.

Extract the following fields. If a field is not mentioned or unclear, set it to null or empty list:

{
  "company_name": "string — the client's business name",
  "owner_name": "string or null — the owner's full name",
  "business_hours": {
    "days": ["list of days mentioned"] or [],
    "start": "start time or null",
    "end": "end time or null",
    "timezone": "timezone or null"
  },
  "office_address": "string or null",
  "services_supported": ["list of services explicitly mentioned"],
  "emergency_definition": ["list of what counts as an emergency, as described"],
  "emergency_routing_rules": [
    {
      "name": "person name",
      "phone": "phone number or null",
      "order": 1,
      "fallback": "what to do if they don't answer, or null"
    }
  ],
  "non_emergency_routing_rules": "string description or null",
  "call_transfer_rules": {
    "timeout_seconds": null,
    "retries": null,
    "message_if_fails": null
  },
  "integration_constraints": ["list of integration rules mentioned, e.g. 'Uses Jobber CRM'"],
  "after_hours_flow_summary": "string summary or null",
  "office_hours_flow_summary": "string summary or null",
  "pricing_info": null,
  "notification_channels": null,
  "questions_or_unknowns": ["list of things NOT confirmed that would be needed to configure an agent"],
  "notes": "brief summary of the call context"
}

CRITICAL RULES:
1. Do NOT hallucinate details. If business hours are not explicitly stated, leave null.
2. If emergency handling is vague, capture it as-is and flag it in questions_or_unknowns.
3. If phone numbers are not provided, set phone to null and add to questions_or_unknowns.
4. Capture the client's CRM/software if mentioned (e.g., Jobber, ServiceTrade).
5. This is a DEMO call — expect incomplete information. That is normal.
6. Return ONLY valid JSON. No markdown, no explanation."""

ONBOARDING_EXTRACTION_PROMPT = """You are a data extraction specialist for Clara AI.

Analyze the following ONBOARDING CALL transcript. This call happens AFTER the client has purchased Clara.
The onboarding call focuses on operational configuration — confirmed details that override demo assumptions.

You are given the existing v1 account memo (from the demo call) for context.
Extract ONLY NEW or UPDATED information from the onboarding transcript.

Return a JSON patch object with ONLY the fields that have new/updated values.
If a field was not discussed in this onboarding call, do NOT include it.

Expected fields (include only those with updates):
{
  "company_name": "updated name if different",
  "owner_name": "updated if different",
  "business_hours": {
    "days": ["updated days"],
    "start": "confirmed start time",
    "end": "confirmed end time",
    "timezone": "confirmed timezone"
  },
  "office_address": "confirmed address",
  "services_supported": ["updated list if changed"],
  "emergency_definition": ["confirmed emergency definitions"],
  "emergency_routing_rules": [
    {
      "name": "person",
      "phone": "confirmed number",
      "order": 1,
      "fallback": "confirmed fallback"
    }
  ],
  "non_emergency_routing_rules": "confirmed rules",
  "call_transfer_rules": {
    "timeout_seconds": 45,
    "retries": 1,
    "message_if_fails": "confirmed message"
  },
  "integration_constraints": ["confirmed constraints"],
  "after_hours_flow_summary": "confirmed after-hours flow",
  "office_hours_flow_summary": "confirmed office-hours flow",
  "pricing_info": {
    "service_call_fee": "confirmed fee",
    "hourly_rate": "confirmed rate",
    "billing_increment": "confirmed increment",
    "disclose_on_request_only": true
  },
  "notification_channels": {
    "email": "confirmed email",
    "sms": "confirmed number"
  },
  "questions_or_unknowns": ["any items STILL unresolved after onboarding"],
  "changelog_notes": "brief summary of what changed and why"
}

EXISTING v1 ACCOUNT MEMO:
{v1_memo}

CRITICAL RULES:
1. Only include fields that have NEW or CHANGED information from this onboarding call.
2. Do NOT copy unchanged fields from v1.
3. If something was unknown in v1 and is now confirmed, include it.
4. If something is STILL unknown after onboarding, include it in questions_or_unknowns.
5. Return ONLY valid JSON. No markdown, no explanation."""


# ─── RETRY LOGIC ──────────────────────────────────────────────────────────────

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def _call_groq_with_retry(client, messages: list, temperature: float = 0.1) -> str:
    """Call Groq API with exponential backoff retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=temperature,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "rate_limit" in error_str.lower() or "429" in error_str:
                wait = RETRY_DELAY * (2 ** attempt)
                logger.warning(
                    "Rate limited (attempt %d/%d). Waiting %ds...",
                    attempt + 1, MAX_RETRIES, wait
                )
                time.sleep(wait)
            elif attempt < MAX_RETRIES - 1:
                logger.warning(
                    "Groq API error (attempt %d/%d): %s. Retrying...",
                    attempt + 1, MAX_RETRIES, e
                )
                time.sleep(RETRY_DELAY)
            else:
                logger.error("Groq API failed after %d attempts: %s", MAX_RETRIES, e)
                raise

    raise RuntimeError("Groq API call failed after all retries")


def _parse_json_response(response_text: str) -> dict:
    """Parse JSON from LLM response, handling edge cases."""
    # Try direct parse first
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code block
    import re
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find first { ... } block
    brace_start = response_text.find('{')
    brace_end = response_text.rfind('}')
    if brace_start != -1 and brace_end != -1:
        try:
            return json.loads(response_text[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from LLM response:\n{response_text[:500]}")


# ─── EXTRACTION FUNCTIONS ────────────────────────────────────────────────────

def extract_from_transcript(transcript: str, client) -> dict:
    """
    Extract structured account data from a demo call transcript.

    Args:
        transcript: Full text of the demo call transcript
        client: Initialized Groq client

    Returns:
        dict with extracted fields matching AccountMemo schema
    """
    logger.info("Extracting data from demo transcript (%d chars)...", len(transcript))

    # Truncate if very long (Groq context limit)
    max_chars = 28000
    if len(transcript) > max_chars:
        logger.warning("Transcript exceeds %d chars, truncating...", max_chars)
        transcript = transcript[:max_chars] + "\n\n[TRANSCRIPT TRUNCATED]"

    messages = [
        {
            "role": "system",
            "content": DEMO_EXTRACTION_PROMPT,
        },
        {
            "role": "user",
            "content": f"DEMO CALL TRANSCRIPT:\n\n{transcript}",
        },
    ]

    response_text = _call_groq_with_retry(client, messages)
    extracted = _parse_json_response(response_text)

    # Validate required fields
    if not extracted.get("company_name"):
        logger.warning("No company_name extracted — may indicate extraction failure")

    # Ensure lists are lists
    for list_field in ["services_supported", "emergency_definition",
                       "integration_constraints", "questions_or_unknowns"]:
        if extracted.get(list_field) is None:
            extracted[list_field] = []
        elif isinstance(extracted[list_field], str):
            extracted[list_field] = [extracted[list_field]]

    # Ensure emergency_routing_rules is a list of dicts
    if extracted.get("emergency_routing_rules") is None:
        extracted["emergency_routing_rules"] = []

    logger.info(
        "Extraction complete: company=%s, services=%d, unknowns=%d",
        extracted.get("company_name", "?"),
        len(extracted.get("services_supported", [])),
        len(extracted.get("questions_or_unknowns", [])),
    )

    return extracted


def extract_onboarding_patch(transcript: str, v1_memo: dict, client) -> dict:
    """
    Extract update patch from an onboarding call transcript.

    Args:
        transcript: Full text of the onboarding call transcript
        v1_memo: Existing v1 account memo as dict
        client: Initialized Groq client

    Returns:
        dict with only changed/new fields (patch format)
    """
    logger.info("Extracting onboarding updates (%d chars)...", len(transcript))

    # Truncate if needed
    max_chars = 28000
    if len(transcript) > max_chars:
        logger.warning("Transcript exceeds %d chars, truncating...", max_chars)
        transcript = transcript[:max_chars] + "\n\n[TRANSCRIPT TRUNCATED]"

    # Build prompt with v1 context
    prompt = ONBOARDING_EXTRACTION_PROMPT.replace(
        "{v1_memo}", json.dumps(v1_memo, indent=2)
    )

    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": f"ONBOARDING CALL TRANSCRIPT:\n\n{transcript}",
        },
    ]

    response_text = _call_groq_with_retry(client, messages)
    patch = _parse_json_response(response_text)

    logger.info(
        "Onboarding extraction complete: %d fields updated",
        len([k for k, v in patch.items() if v is not None and k != "changelog_notes"]),
    )

    return patch


# ─── WHISPER TRANSCRIPTION ────────────────────────────────────────────────────

def transcribe_audio(audio_path: str, client=None) -> str:
    """
    Transcribe audio file using Groq Whisper API (free tier).

    Args:
        audio_path: Path to audio file (mp3, wav, m4a, etc.)
        client: Initialized Groq client (will create one if None)

    Returns:
        Transcribed text
    """
    if client is None:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in environment")
        client = Groq(api_key=api_key)

    logger.info("Transcribing audio: %s", audio_path)

    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), audio_file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
            language="en",
        )

    text = transcription.text if hasattr(transcription, 'text') else str(transcription)
    logger.info("Transcription complete: %d characters", len(text))

    return text


def transcribe_audio_if_needed(input_path: str, client=None) -> str:
    """
    If input is audio, transcribe it. If it's already text, read it.

    Args:
        input_path: Path to audio or transcript file
        client: Initialized Groq client

    Returns:
        Transcript text
    """
    audio_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm', '.mp4'}
    ext = os.path.splitext(input_path)[1].lower()

    if ext in audio_extensions:
        logger.info("Input is audio file, transcribing with Whisper...")
        return transcribe_audio(input_path, client)
    else:
        logger.info("Input is text file, reading directly...")
        with open(input_path, "r", encoding="utf-8") as f:
            return f.read()
