# 🤖 Clara Answers Automation Pipeline
Hey! This is my submission for the Clara Answers Intern Assignment. I built a zero-cost pipeline that takes demo and onboarding calls and turns them into production-ready Retell AI agent configurations. 

This pipeline handles 10 files (5 demo + 5 onboarding) and generates structured JSONs, Retell specs, and changelogs. Everything runs on free tools! 🚀

---

## 📁 Submission Deliverables
- **/outputs**: Contains all generated data for 5 accounts (v1 from demo calls, v2 from onboarding).
- **/scripts**: The Python core (Extraction, Prompt Generation, Batch Processing).
- **/data**: All transcripts used for the 10-file run.
- **/workflows**: Setup guides for Zapier and n8n.
- **dashboard.html**: A local UI I made to compare versions and view agent prompts.
- **README.md**: Setup and run instructions.

---

## 🛠️ Setup Instructions

### 1. Retell AI Setup
Since Retell's API is paid, I designed the output to be "Paste-Ready."
1. Go to [app.retellai.com](https://app.retellai.com) and create a free account.
2. In the dashboard, click **Create New Agent**.
3. Open `outputs/accounts/<id>/v2/agent_spec_v2.json`.
4. Copy the `system_prompt` and paste it into Retell's **System Prompt** box.
5. In Retell, add the variables (like phone numbers) found in the `key_variables` section of the JSON.
6. Tip: Use the **Retell Import Guide** found in each account's `/v1` folder for a step-by-step checklist.

### 2. LLM Setup (Groq - Zero Cost)
I used **Groq Llama 3.3 70B** because it's super fast and completely free. 
- Get an API key at [console.groq.com](https://console.groq.com).
- No credit card required!
- Add it to your environment: `export GROQ_API_KEY=your_key_here`

### 3. n8n / Zapier Setup
I've documented two ways to run this automatically:

#### Option A: n8n (Preferred)
See `workflows/n8n_setup.md` for:
- A `docker-compose.yml` to run n8n locally.
- A workflow JSON you can import.
- Steps to connect Google Drive and Groq.

#### Option B: Zapier
See `workflows/zapier_workflow.md` for a full guide on:
- Connecting Google Drive → Code by Zapier → Google Sheets.
- Managing tasks on a Trello board.

---

## 🚀 How to Run (Batch Processing)

If you want to run the whole 10-file dataset at once (A+B pipelines), just follow these steps:

1. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Batch Runner**:
   ```bash
   # Make sure your GROQ_API_KEY is set!
   python scripts/batch_run.py
   ```

**What happens next?**
- It transcribes any audio files using Groq Whisper.
- It extracts Account Memos from demo calls (v1).
- It applies updates from onboarding calls (v2).
- It generates a side-by-side **Diff** and **Changelog**.
- It saves everything to the `/outputs` folder.

---

## 📊 Evaluation Rubric Checklist

- [x] **A) Automation**: End-to-end run on 10 files. Handles Groq rate limits with delays.
- [x] **B) Quality**: Prompt hygiene followed (warm, professional, distinct AH vs. BH flows). No hallucinations.
- [x] **C) Engineering**: Pydantic-style schemas in `schema.py`, versioned outputs (v1/v2).
- [x] **D) Documentation**: This README + internal script comments.
- [x] **Bonus**: Local Dashboard (`dashboard.html`) with a search bar and version comparison!

---

## 📺 Demo Video (Loom)
[Link to your Loom Video here]
In the video, I show:
1. The pipeline running for Apex Fire Protection.
2. The agent prompt changing from v1 (preliminary) to v2 (confirmed).
3. The Dashboard UI showing the side-by-side diff.

---

## 📝 Final Notes
The pipeline is designed to be **Idempotent** (run it 100 times, it won't break) and **Logged** (check `outputs/pipeline_log.csv`). 

Thanks for checking out my work! I really enjoyed building this. 
- *Aaryan Sriv* (Intern Applicant)
