# n8n Setup Guide — Clara Pipeline

This guide helps you run the Clara Pipeline using **n8n**, a free and self-hostable automation tool.

---

## 1. Local n8n Setup (Docker)

If you don't have n8n, the fastest way to run it is with Docker Compose.

1. Create a file called `docker-compose.yml`:
```yaml
version: '3'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - 5678:5678
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
    volumes:
      - n8n_data:/home/node/.n8n
volumes:
  n8n_data:
```

2. Run it:
```bash
docker-compose up -d
```

3. Open [http://localhost:5678](http://localhost:5678) in your browser.

---

## 2. Environment Variables

In n8n, you'll need to set up **Credentials**:

| Credential Type | Purpose |
|-----------------|---------|
| **Groq API** | Used for Llama 3.3 and Whisper nodes. |
| **Google Drive** | Used to watch for new transcript files. |
| **Google Sheets** | (Optional) For logging results. |

---

## 3. Workflow Import

1. Download the `workflows/n8n_workflow.json` file from this repo.
2. In n8n, go to **Workflows** → **Add Workflow** → **Import from File**.
3. Select the JSON file.

---

## 4. How the Workflow Works

The workflow follows the logic of the Python scripts:

1. **Trigger**: Google Drive watches for a new `.txt` file.
2. **Read File**: Downloads the transcript content.
3. **LLM Node (Groq)**: 
   - Uses the **Demo Extraction Prompt** (for v1) or **Onboarding Prompt** (for v2).
   - Returns structured JSON.
4. **Code Node**: 
   - Normalizes the JSON fields to match the `AccountMemo` schema.
   - Saves files to the corresponding directory.
5. **Log Node**: Updates Google Sheets and moves a Trello card.

---

## 5. Running the Batch Dataset

To run all 10 files in n8n:
1. Upload all 5 demo transcripts to your Google Drive folder.
2. The workflow will trigger 5 times (concurrently or sequentially depending on settings).
3. Once those are finished, upload the 5 onboarding transcripts.
4. The workflow will match the `account_id` and generate the `v2` outputs.

---

## Why n8n?
- **Zero Cost**: Truly free if self-hosted.
- **Visual**: You can see exactly where a call fails.
- **Powerful**: Better handling of long transcripts than Zapier's free tier.
