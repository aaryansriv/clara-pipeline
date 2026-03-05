# Clara Pipeline
**Automated Demo Call → Retell Agent Configuration → Onboarding Updates → Production-Ready Agent**

Zero-cost, end-to-end automation that converts sales/onboarding call transcripts into production-ready Retell AI voice agent configurations — with full versioning, change tracking, and batch processing.

---

## Architecture & Data Flow

```
                    PIPELINE A (Demo → v1)                     PIPELINE B (Onboarding → v2)
                    ─────────────────────                      ──────────────────────────────

   Audio File ──► Groq Whisper ──┐                    Audio File ──► Groq Whisper ──┐
                                 │                                                  │
   Transcript ───────────────────┤                    Transcript ───────────────────┤
                                 ▼                                                  ▼
                          ┌─────────────┐                                    ┌─────────────┐
                          │  Groq LLaMA │                                    │  Groq LLaMA │
                          │  3.3 70B    │                                    │  3.3 70B    │
                          │  Extraction │                                    │  Patch Ext. │
                          └──────┬──────┘                                    └──────┬──────┘
                                 │                                                  │
                                 ▼                                                  ▼
                    ┌────────────────────────┐                      ┌────────────────────────┐
                    │  account_memo_v1.json  │───── loads v1 ──────►│  apply_patch()         │
                    │  agent_spec_v1.json    │                      │  → account_memo_v2.json│
                    │  retell_import_guide.md│                      │  → agent_spec_v2.json  │
                    └────────────┬───────────┘                      │  → changes.md          │
                                 │                                  │  → changes.json        │
                                 ▼                                  └────────────┬───────────┘
                    ┌────────────────────────┐                                   │
                    │  outputs/accounts/     │◄──────────────────────────────────┘
                    │    <account_id>/       │
                    │      v1/ and v2/       │
                    └────────────┬───────────┘
                                 │
                    ┌────────────▼───────────┐
                    │  Google Sheets (log)   │
                    │  Trello (task cards)   │
                    │  dashboard.html (UI)   │
                    └────────────────────────┘
```

### Technology Stack (100% Free Tier)

| Layer | Tool | Why | Cost |
|-------|------|-----|------|
| **Orchestrator** | Zapier (free tier) | Native integrations, 100 tasks/mo | $0 |
| **LLM Extraction** | Groq LLaMA 3.3 70B (free) | Fast, accurate, generous free tier | $0 |
| **Transcription** | Groq Whisper (free) | Same API key, handles audio files | $0 |
| **Storage** | GitHub repo + local JSON | Version-controlled, zero setup | $0 |
| **Task Tracking** | Trello (free) | Zapier native integration, unlimited cards | $0 |
| **Reporting** | Google Sheets (free) | Easy tracking + sharing | $0 |
| **Retell** | Agent Spec JSON (mocked) | Free tier can't call Retell API | $0 |
| **Dashboard** | Static HTML | No server needed, opens in any browser | $0 |

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/clara-pipeline.git
cd clara-pipeline
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
# Required
export GROQ_API_KEY=your_groq_api_key_here

# Optional — Google Sheets integration
export GOOGLE_SHEETS_CREDENTIALS=/path/to/service-account.json
export GOOGLE_SHEET_ID=your_spreadsheet_id

# Optional — Trello integration
export TRELLO_API_KEY=your_trello_key
export TRELLO_TOKEN=your_trello_token
export TRELLO_BOARD_ID=your_board_id
```

Get a free Groq API key at: https://console.groq.com

### 4. Run the pipeline

```bash
cd scripts

# Run all 10 files (5 demo + 5 onboarding)
python batch_run.py

# Run only Pipeline A (all 5 demo calls)
python batch_run.py --only-a

# Run only Pipeline B (all 5 onboarding calls)
python batch_run.py --only-b

# Run a single account end-to-end
python batch_run.py --account bens-electric-solutions
```

### 5. View results
- **Dashboard**: Open `dashboard.html` in any browser
- **JSON outputs**: Check `outputs/accounts/<account_id>/v1/` and `v2/`
- **Batch summary**: `outputs/batch_summary.json`
- **Pipeline log**: `outputs/pipeline_log.csv`

---

## Project Structure

```
clara-pipeline/
├── scripts/
│   ├── schema.py              # Data models (AccountMemo, AgentSpec, etc.)
│   ├── extractor.py           # Groq LLM extraction + Whisper transcription
│   ├── prompt_generator.py    # Retell agent prompt builder
│   ├── pipeline_a.py          # Demo Call → v1 agent
│   ├── pipeline_b.py          # Onboarding Call → v2 agent
│   ├── batch_run.py           # Batch runner for all 10 files
│   ├── sheets_integration.py  # Google Sheets sync (with CSV fallback)
│   └── trello_integration.py  # Trello task tracking (with local fallback)
├── data/
│   └── transcripts/
│       ├── demo/              # 5 demo call transcripts
│       │   ├── bens_electric_demo.txt
│       │   ├── apex_fire_demo.txt
│       │   ├── shield_sprinkler_demo.txt
│       │   ├── blazeguard_demo.txt
│       │   └── peakfire_demo.txt
│       └── onboarding/        # 5 onboarding call transcripts
│           ├── bens_electric_onboarding.txt
│           ├── apex_fire_onboarding.txt
│           ├── shield_sprinkler_onboarding.txt
│           ├── blazeguard_onboarding.txt
│           └── peakfire_onboarding.txt
├── outputs/
│   ├── accounts/
│   │   └── <account_id>/
│   │       ├── v1/            # account_memo_v1.json, agent_spec_v1.json, retell_import_guide.md
│   │       └── v2/            # account_memo_v2.json, agent_spec_v2.json, changes.md, changes.json
│   ├── batch_summary.json     # Overall batch run results
│   └── pipeline_log.csv       # Local execution log (fallback for Sheets)
├── workflows/
│   └── zapier_workflow.md     # Full Zapier setup guide with screenshots
├── dashboard.html             # Visual diff viewer + prompt viewer
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Output Files

For each account `<account_id>`, the pipeline produces:

### v1 (from Demo Call — Pipeline A)
| File | Description |
|------|-------------|
| `account_memo_v1.json` | Structured data extracted from demo call |
| `agent_spec_v1.json` | Preliminary Retell agent configuration |
| `retell_import_guide.md` | Step-by-step Retell UI setup instructions |

### v2 (from Onboarding Call — Pipeline B)
| File | Description |
|------|-------------|
| `account_memo_v2.json` | Updated data with onboarding confirmations |
| `agent_spec_v2.json` | Production-ready Retell agent configuration |
| `changes.md` | Human-readable changelog (v1 → v2) |
| `changes.json` | Machine-readable diff (for automation) |

---

## Dataset

| # | Account | Type | Location | Demo | Onboarding |
|---|---------|------|----------|------|------------|
| 1 | Ben's Electric Solutions | Electrical | Calgary, AB (MST) | ✅ Real transcript | ✅ Real transcript |
| 2 | Apex Fire Protection | Fire Protection | Houston, TX (CST) | ✅ | ✅ |
| 3 | Shield Sprinkler Co. | Sprinkler | Phoenix, AZ (MST) | ✅ | ✅ |
| 4 | BlazeGuard Alarms | Alarm Systems (2 locations) | Chicago + Milwaukee (CST) | ✅ | ✅ |
| 5 | PeakFire Services | Fire Protection | Denver, CO (MST) | ✅ | ✅ |

---

## Key Design Decisions

### 1. Separation of Demo vs. Onboarding Data
- **Demo (v1)**: Extracts only explicitly stated information. Missing details are flagged in `questions_or_unknowns`. No hallucination.
- **Onboarding (v2)**: Applies a patch to v1. Only updates fields that changed. Preserves version history.

### 2. Prompt Hygiene
Generated agent prompts follow strict conversation flow:

**During Business Hours:**
1. Greet → 2. Understand purpose → 3. Collect name + phone → 4. Collect job details → 5. Transfer/route → 6. Fallback if transfer fails → 7. "Anything else?" → 8. Close

**After Hours:**
1. Greet (mention after hours) → 2. Ask purpose → 3. Determine if emergency → 4a. If emergency: collect name, phone, address → attempt transfer → fallback → 4b. If non-emergency: collect details → confirm follow-up during business hours → 5. "Anything else?" → 6. Close

### 3. Missing Data Handling
- Never invented or assumed
- Explicitly tracked in `questions_or_unknowns`
- Flagged in agent prompt as `⚠️ CONFIGURATION GAPS`
- Resolved during onboarding (v2)

### 4. Idempotency
- Running the pipeline twice doesn't create duplicates
- Output directories are created with `exist_ok=True`
- Files are overwritten cleanly on re-run

### 5. Retry & Rate Limiting
- Groq free tier has ~30 req/min limit
- `batch_run.py` adds 2s delays between accounts
- `extractor.py` has exponential backoff retry (3 attempts)
- Graceful error handling — one failed account doesn't stop the batch

---

## Retell Setup (Free Tier)

Retell's free tier does not support programmatic agent creation via API. Instead:

1. Open `outputs/accounts/<id>/v1/agent_spec_v1.json`
2. Go to [app.retellai.com](https://app.retellai.com) → **Create Agent**
3. Follow the steps in `retell_import_guide.md`
4. Paste the `system_prompt` field into the **System Prompt** box
5. Set voice, transfer numbers, and webhook from `key_variables`
6. For v2, repeat with `agent_spec_v2.json` — the prompt will be fully updated

---

## Dashboard

Open `dashboard.html` in any browser for:
- **Overview** — All 5 accounts, status, open items count
- **v1 → v2 Diff** — Side-by-side field comparison with change highlighting
- **Agent Prompts** — View and copy v1/v2 system prompts
- **Changelog** — Full field-level change history for all accounts

---

## Zapier Workflow

See `workflows/zapier_workflow.md` for the full Zapier setup.

**Zap A** (Pipeline A trigger):
- Trigger: New file in Google Drive `demo-transcripts/`
- Action 1: Run extraction via Code by Zapier
- Action 2: Create Trello card → "v1 Ready"
- Action 3: Log to Google Sheets

**Zap B** (Pipeline B trigger):
- Trigger: New file in Google Drive `onboarding-transcripts/`
- Action 1: Run Pipeline B via Code by Zapier
- Action 2: Update Trello card → "v2 Live"
- Action 3: Update Google Sheets row

---

## Audio Transcription

When audio files are provided instead of transcripts, the pipeline uses **Groq Whisper** (free tier):

```python
from extractor import transcribe_audio_if_needed

# Automatically detects audio vs. text and handles accordingly
transcript = transcribe_audio_if_needed("path/to/recording.m4a", client)
```

Supported audio formats: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.webm`, `.mp4`

---

## Known Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|------------|
| Groq free tier rate limit (~30 req/min) | Batch runs need delays | 2s delay between accounts, exponential backoff retry |
| Retell API requires paid plan | Can't auto-deploy agents | All outputs are Retell-compatible JSON with manual import guide |
| Zapier free tier: 100 tasks/month | Limited to ~25 pipeline runs/month | Sufficient for this demo; batch mode for larger runs |
| Ben's onboarding call ended early | Transfer number still pending | Flagged in `questions_or_unknowns` |

## What I Would Improve With Production Access

1. **Retell API integration** — Auto-deploy agent specs directly to Retell platform
2. **Supabase database** — Replace local JSON with PostgreSQL for multi-user access
3. **Webhook-based triggers** — Real-time pipeline execution on file upload
4. **Human review step** — Approval gate before v1 → live deployment
5. **Conflict resolution UI** — Visual tool for resolving contradictory onboarding data
6. **Streaming extraction** — Process long transcripts in chunks for better accuracy
7. **Quality scoring** — Automated validation of extracted data completeness
8. **n8n self-hosted** — Replace Zapier for unlimited executions
