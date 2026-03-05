# Zapier Workflow — Clara Pipeline Automation

## Overview

This document describes the Zapier automation that orchestrates the Clara Pipeline.
Two Zaps are configured to handle the end-to-end flow from transcript ingestion to agent configuration.

---

## Architecture

```
Google Drive                    Zapier                          Clara Pipeline
┌──────────────┐    ┌──────────────────────────┐    ┌──────────────────────┐
│ demo-transcripts/ │──►│  Zap A: Demo Pipeline    │──►│  Pipeline A           │
│                   │    │  1. Trigger: New file     │    │  → account_memo_v1    │
│                   │    │  2. Code: Run extraction  │    │  → agent_spec_v1      │
│                   │    │  3. Trello: Create card   │    │  → retell_import_guide│
│                   │    │  4. Sheets: Log result    │    │                       │
└──────────────┘    └──────────────────────────┘    └──────────────────────┘

┌──────────────┐    ┌──────────────────────────┐    ┌──────────────────────┐
│ onboarding-      │──►│  Zap B: Onboarding        │──►│  Pipeline B           │
│   transcripts/   │    │  1. Trigger: New file     │    │  → account_memo_v2    │
│                   │    │  2. Code: Run update      │    │  → agent_spec_v2      │
│                   │    │  3. Trello: Update card   │    │  → changes.md/.json   │
│                   │    │  4. Sheets: Update row    │    │                       │
└──────────────┘    └──────────────────────────┘    └──────────────────────┘
```

---

## Prerequisites

1. **Zapier Free Tier Account** — [zapier.com](https://zapier.com)
   - Free tier: 100 tasks/month, 5 Zaps
   - Sufficient for 10-file dataset (each Zap execution = ~4 tasks max)

2. **Google Drive** — For transcript file storage
3. **Google Sheets** — For pipeline tracking log
4. **Trello Free Tier** — For task tracking board
5. **Groq API Key** — For LLM extraction (free tier)

---

## Setup Steps

### Step 1: Create Google Drive Folders

Create two folders in Google Drive:
```
Clara Pipeline/
├── demo-transcripts/         ← Drop demo call transcripts here
└── onboarding-transcripts/   ← Drop onboarding transcripts here
```

### Step 2: Create Google Sheet

Create a Google Sheet called `Clara Pipeline Tracker` with these columns:

| Column | Description |
|--------|-------------|
| A: Account ID | Auto-generated from company name |
| B: Company Name | Extracted from transcript |
| C: Pipeline | A or B |
| D: Status | Processing / v1 Ready / v2 Ready / Failed |
| E: Timestamp | When the pipeline ran |
| F: Unknowns | Number of unresolved items |
| G: Output Path | Where files were saved |
| H: Notes | Any errors or special notes |

### Step 3: Create Trello Board

Create a Trello board called `Clara Pipeline` with these lists:
- **Inbox** — New transcripts detected
- **v1 Processing** — Pipeline A running
- **v1 Ready** — Demo agent generated
- **v2 Processing** — Pipeline B running
- **v2 Live** — Production-ready agent
- **Issues** — Failed or needs attention

### Step 4: Set Environment Variables

In Zapier's Code by Zapier steps, set these as input data:
```
GROQ_API_KEY: your_groq_api_key_here
GITHUB_REPO: your-username/clara-pipeline
```

---

## Zap A: Demo Call → v1 Agent

### Trigger
- **App**: Google Drive
- **Event**: New File in Folder
- **Folder**: `demo-transcripts/`
- **File Types**: .txt, .md

### Action 1: Code by Zapier (Python)
```python
# Extract account_id from filename
# Format: {company_name}_demo.txt
import re

filename = input_data['filename']
company = filename.replace('_demo.txt', '').replace('_demo', '')
account_id = re.sub(r'[^a-z0-9]+', '-', company.lower()).strip('-')

output = {
    'account_id': account_id,
    'company_name_guess': company.replace('_', ' ').title(),
    'transcript_url': input_data['file_url'],
    'filename': filename,
}
```

### Action 2: Webhooks by Zapier
- **Method**: POST
- **URL**: `https://your-pipeline-endpoint.com/api/pipeline-a`
- **Body**:
```json
{
  "account_id": "{{account_id}}",
  "transcript_url": "{{transcript_url}}",
  "source": "zapier"
}
```

> **Note (Free Tier):** Since Zapier free tier may not support Webhooks,
> use **Code by Zapier** to call the Groq API directly for extraction.
> See the `scripts/extractor.py` module for the extraction logic
> that can be adapted for Code by Zapier.

### Action 3: Trello — Create Card
- **Board**: Clara Pipeline
- **List**: v1 Processing
- **Card Name**: `{{company_name}} — v1 Processing`
- **Description**: `Pipeline A started for {{account_id}} at {{timestamp}}`
- **Labels**: Yellow (In Progress)

### Action 4: Google Sheets — Create Row
- **Spreadsheet**: Clara Pipeline Tracker
- **Worksheet**: Sheet1
- **Values**:
  - Account ID: `{{account_id}}`
  - Company Name: `{{company_name}}`
  - Pipeline: A
  - Status: v1 Ready
  - Timestamp: `{{current_timestamp}}`
  - Unknowns: `{{unknowns_count}}`

### Action 5: Trello — Update Card
- **Move card to**: v1 Ready
- **Update Label**: Green (Complete)
- **Add Comment**: `v1 agent generated. {{unknowns_count}} open items.`

---

## Zap B: Onboarding Call → v2 Agent

### Trigger
- **App**: Google Drive
- **Event**: New File in Folder
- **Folder**: `onboarding-transcripts/`

### Action 1: Code by Zapier
```python
# Match account_id from filename
import re

filename = input_data['filename']
company = filename.replace('_onboarding.txt', '').replace('_onboarding', '')
account_id = re.sub(r'[^a-z0-9]+', '-', company.lower()).strip('-')

output = {
    'account_id': account_id,
    'transcript_url': input_data['file_url'],
}
```

### Action 2: Webhook / Code — Run Pipeline B
- Calls Pipeline B endpoint or runs extraction inline
- Loads v1 memo for context
- Generates v2 memo, agent spec, and changelog

### Action 3: Trello — Find Card
- **Search**: Card name contains `{{company_name}}`
- **Board**: Clara Pipeline

### Action 4: Trello — Update Card
- **Move to**: v2 Live
- **Label**: Green
- **Add Comment**: `v2 agent ready. {{remaining_unknowns}} items still pending.`

### Action 5: Google Sheets — Update Row
- **Find row by**: Account ID = `{{account_id}}`
- **Update Status**: v2 Ready
- **Update Notes**: `Onboarding complete. Changelog generated.`

---

## Free Tier Limitations

| Constraint | Limit | Impact |
|-----------|-------|--------|
| Zapier tasks/month | 100 | 10 files × ~4 tasks each = ~40 tasks. Well within limit. |
| Zapier Zaps | 5 | Need 2. Well within limit. |
| Trello boards | Unlimited (free) | No impact. |
| Google Sheets | 5M cells (free) | No impact. |
| Groq API | ~30 req/min | Use 2s delay between accounts. |

---

## Alternative: Manual Batch Execution

If Zapier free tier doesn't support all required actions, you can run the pipeline
manually using the batch runner:

```bash
cd scripts
python batch_run.py          # Run all 10 files
python batch_run.py --only-a # Run only Pipeline A (5 demo calls)
python batch_run.py --only-b # Run only Pipeline B (5 onboarding calls)
```

Then manually update Trello and Google Sheets, or use the integration scripts:

```bash
python sheets_integration.py  # Sync results to Google Sheets
python trello_integration.py  # Sync results to Trello board
```

---

## Testing

1. Drop a test transcript into `demo-transcripts/` folder
2. Verify Zap A fires within 5 minutes
3. Check Trello board for new card
4. Check Google Sheet for new row
5. Check `outputs/accounts/<id>/v1/` for generated files
6. Drop the corresponding onboarding transcript
7. Verify Zap B fires and updates the card + row
8. Check `outputs/accounts/<id>/v2/` for v2 files + changelog
