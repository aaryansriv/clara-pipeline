# Retell Import Guide — PeakFire Services (v1)

Generated: 2026-03-05 19:48 UTC

## How to Configure This Agent in Retell UI

1. Log in to [app.retellai.com](https://app.retellai.com)
2. Click **Create Agent** → choose **Custom LLM** or **Retell LLM**
3. Set **Agent Name**: `Clara — PeakFire Services`
4. Set **Voice**: Professional Female (warm tone recommended)
5. Paste the contents of `agent_spec_v1.json` → field `system_prompt` into the **System Prompt** box
6. Configure **Call Transfer**:
   - Timeout: None seconds
   - Transfer numbers: See `key_variables.emergency_routing` in agent spec
7. Set **Post-Call Webhook** to your notification endpoint (email/SMS)
8. Click **Save & Test**

## ⚠️ Outstanding Items Before Going Live
- Confirm business hours
- Notification preferences
- Special rules
- Phone numbers for on-call team members

## Version
- This is **v1** (generated from demo call)
- After onboarding call, run Pipeline B to generate v2
