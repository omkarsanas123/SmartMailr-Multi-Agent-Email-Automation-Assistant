# SmartMailr: Multi-Agent Email Automation
# File: smartmailr_kaggle_notebook_and_repo.py
# This single-file 'notebook-style' Python script contains:
# 1) A Kaggle-friendly notebook with demo cells (use `# %%` cell markers)
# 2) Backend FastAPI server code (as a module)
# 3) Streamlit dashboard code (as a module)
# 4) Instructions and a GitHub repo layout you can copy into a repo

"""
HOW TO USE
----------
- This file is formatted with cell markers ("# %%") so you can open it in VSCode
  or convert to an .ipynb using nbconvert if you prefer a notebook.
- To run the demo cells on Kaggle: paste the notebook cells into a new Kaggle
  notebook (or upload a converted .ipynb). The demo uses mocked Gmail data so
  it runs without any API keys.
- To run the full system (fastapi + streamlit + real Gmail/Calendar integration):
  split files into the repo structure shown at the end and provide your API
  credentials (instructions included).

FILES TO CREATE FOR GITHUB (suggested repo layout)
--------------------------------------------------
smartmailr/
├─ backend/
│  ├─ app.py                # FastAPI server (email processing endpoints)
│  ├─ agents.py             # Planner/Intent/Reply/QA/Action agents
│  └─ requirements.txt
├─ ui/
│  ├─ streamlit_app.py      # Streamlit dashboard to view inbox + actions
├─ notebooks/
│  └─ smartmailr_demo.ipynb # Notebook version of this file
├─ README.md
└─ LICENSE

"""

# %%
# CELL: Install dependencies (for Kaggle notebook, comment/uncomment as needed)
# !pip install fastapi uvicorn streamlit pydantic email-validator
# NOTE: On Kaggle, network installs may be restricted. The demo below uses pure Python stdlib.

# %%
# CELL: Imports
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

# %%
# CELL: Simple agent implementations (mocked, deterministic)
@dataclass
class Email:
    id: int
    sender: str
    subject: str
    body: str
    received_at: datetime

# Planner: breaks user task into subtasks (very simple here)
def planner_agent(email: Email) -> Dict[str, Any]:
    # Decide workflow based on intent
    intent = intent_agent(email)
    plan = {"intent": intent, "steps": []}
    if intent == "meeting_request":
        plan["steps"] = ["extract_datetime", "create_event", "draft_reply"]
    elif intent == "info_request":
        plan["steps"] = ["find_answer", "draft_reply"]
    elif intent == "acknowledgement":
        plan["steps"] = ["draft_ack"]
    else:
        plan["steps"] = ["draft_general_reply"]
    return plan

# Intent classifier (very small rule-based for demo)
def intent_agent(email: Email) -> str:
    text = (email.subject + " " + email.body).lower()
    if any(w in text for w in ["meet", "meeting", "schedule", "call"]):
        return "meeting_request"
    if any(w in text for w in ["please", "could you", "can you", "send"]):
        return "info_request"
    if any(w in text for w in ["thanks", "thank you", "acknowledge"]):
        return "acknowledgement"
    return "general"

# Worker agents (mocked actions)
def extract_datetime_agent(email: Email) -> Dict[str, Any]:
    # very naive: look for 'tomorrow' or 'today' or time like '4 pm'
    text = email.body.lower()
    result = {"datetime": None}
    now = datetime.now()
    if "tomorrow" in text:
        when = now + timedelta(days=1)
        result["datetime"] = when.replace(hour=16, minute=0, second=0, microsecond=0)
    elif "today" in text:
        when = now
        result["datetime"] = when.replace(hour=16, minute=0, second=0, microsecond=0)
    elif "4 pm" in text or "4pm" in text:
        when = now + timedelta(days=1)
        result["datetime"] = when.replace(hour=16, minute=0, second=0, microsecond=0)
    return result


def create_event_agent(event_info: Dict[str, Any]) -> Dict[str, Any]:
    # Mock creating an event; in production this would call Google Calendar API
    return {"event_id": "evt_" + str(int(time.time())), "status": "created", **event_info}


def reply_generator_agent(email: Email, plan: Dict[str, Any], context: Dict[str, Any]) -> str:
    intent = plan["intent"]
    if intent == "meeting_request":
        dt = context.get("datetime")
        dt_text = dt.strftime("%Y-%m-%d %I:%M %p") if dt else "a time"
        reply = f"Hi {email.sender.split('@')[0]},\n\nThanks — that works for me. I've scheduled the meeting for {dt_text}.\n\nBest,\nSmartMailr"
    elif intent == "info_request":
        reply = f"Hi {email.sender.split('@')[0]},\n\nThanks for reaching out. I will gather the information and send it shortly.\n\nBest,\nSmartMailr"
    elif intent == "acknowledgement":
        reply = f"Hi {email.sender.split('@')[0]},\n\nThanks for the update — noted.\n\nBest,\nSmartMailr"
    else:
        reply = f"Hi {email.sender.split('@')[0]},\n\nThanks for your message. I'll get back to you soon.\n\nBest,\nSmartMailr"
    return reply


def qa_agent(text: str) -> str:
    # Very small QA: tidy whitespace and ensure polite closing
    txt = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    if "Best,\nSmartMailr" not in txt:
        txt += "\n\nBest,\nSmartMailr"
    return txt

# Action executor: sends email or creates event (mocked)
def action_executor(plan: Dict[str, Any], email: Email, context: Dict[str, Any]) -> Dict[str, Any]:
    actions = {}
    for step in plan.get("steps", []):
        if step == "extract_datetime":
            dt = extract_datetime_agent(email)
            context.update(dt)
            actions["extract_datetime"] = dt
        elif step == "create_event":
            event = create_event_agent({"summary": f"Meeting with {email.sender}", "datetime": context.get("datetime")})
            actions["create_event"] = event
        elif step.startswith("draft") or step == "find_answer":
            pass
    # Finally build reply
    reply = reply_generator_agent(email, plan, context)
    reply = qa_agent(reply)
    actions["reply"] = reply
    # Mock sending
    actions["sent"] = True
    return actions

# %%
# CELL: Demo dataset (mock emails)
mock_inbox = [
    Email(id=1, sender="alice@example.com", subject="Meeting?", body="Hi, can we meet tomorrow at 4 PM to discuss the dataset?", received_at=datetime.now()),
    Email(id=2, sender="bob@example.com", subject="Request: docs", body="Could you send the latest report please?", received_at=datetime.now()),
    Email(id=3, sender="carol@example.com", subject="Thanks", body="Thanks for the update!", received_at=datetime.now()),
]

# %%
# CELL: Run orchestration on mock inbox and show results
results = []
for email in mock_inbox:
    print(f"Processing email {email.id} from {email.sender} — subject: {email.subject}")
    plan = planner_agent(email)
    print("Plan:", plan)
    context = {}
    actions = action_executor(plan, email, context)
    print("Actions:")
    print(json.dumps({k: (str(v) if not isinstance(v, dict) else v) for k, v in actions.items()}, default=str, indent=2))
    results.append({"email_id": email.id, "plan": plan, "actions": actions})
    print("---\n")

# %%
# CELL: Convert results to a small summary table (pandas optional)
try:
    import pandas as pd
    summary = pd.DataFrame([{"email_id": r["email_id"], "sender": next(e.sender for e in mock_inbox if e.id==r["email_id"]), "intent": r["plan"]["intent"], "sent": r["actions"]["sent"]} for r in results])
    display = getattr(__builtins__, 'display', None)
    if display:
        display(summary)
    else:
        print(summary)
except Exception as e:
    print("Pandas not available — here's a simple summary:")
    for r in results:
        print(r["email_id"], r["plan"]["intent"], r["actions"]["sent"])

# %%
# CELL: FastAPI backend (lightweight) - place into backend/app.py in real repo
fastapi_code = r'''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

app = FastAPI(title="SmartMailr API")

class EmailIn(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    received_at: datetime

@app.post('/process')
def process_email(email: EmailIn):
    # NOTE: For demo we will import agents from a module; in your repo split appropriately
    from agents import planner_agent, action_executor
    e = type('E', (), dict(id=email.id, sender=email.sender, subject=email.subject, body=email.body, received_at=email.received_at))
    plan = planner_agent(e)
    context = {}
    actions = action_executor(plan, e, context)
    return {"plan": plan, "actions": actions}
'''
print("--- FastAPI demo code (copy into backend/app.py) ---")
print(fastapi_code)

# %%
# CELL: Streamlit UI (place into ui/streamlit_app.py) - simple inbox viewer
streamlit_code = r'''import streamlit as st
import requests

st.title('SmartMailr - Demo Inbox')

# In a real deployment you'd fetch from your backend. Here we load sample JSON.
sample = st.file_uploader('Upload sample inbox JSON', type=['json'])
if sample is not None:
    data = sample.getvalue().decode('utf-8')
    inbox = __import__('json').loads(data)
    for e in inbox:
        with st.expander(f"Email {e['id']} from {e['sender']}"):
            st.write('Subject:', e['subject'])
            st.write('Body:', e['body'])
            if st.button(f"Process {e['id']}", key=e['id']):
                # Call your backend
                # resp = requests.post('http://localhost:8000/process', json=e)
                st.success('Processed (demo)')
'''
print("--- Streamlit demo code (copy into ui/streamlit_app.py) ---")
print(streamlit_code)

# %%
# CELL: README snippet to include in your GitHub repo
readme = r'''# SmartMailr

SmartMailr is a demo multi-agent email automation assistant. This repository includes:
- backend/: FastAPI app and agent modules
- ui/: Streamlit dashboard
- notebooks/: Kaggle notebook demonstrating the system with mocked data

## Quickstart (demo)
1. Open `notebooks/smartmailr_demo.ipynb` on Kaggle and run cells.
2. The demo runs offline with mocked emails and shows end-to-end flow.

## Full setup (with Gmail & Calendar)
1. Create Google Cloud credentials and enable Gmail & Calendar APIs.
2. Add credentials to `backend/credentials.json`.
3. Install dependencies from `backend/requirements.txt`.
4. Start backend: `uvicorn backend.app:app --reload`
5. Start UI: `streamlit run ui/streamlit_app.py`
'''
print("--- README snippet ---")
print(readme)

# %%
# CELL: GitHub helper - instructions how to split this file into repository files
helper = r'''# To create the GitHub repo from this single file, split into these files:
# - backend/agents.py      -> copy the agent functions (planner_agent, intent_agent, etc.)
# - backend/app.py         -> FastAPI code block above
# - ui/streamlit_app.py    -> streamlit_code block above
# - notebooks/smartmailr_demo.ipynb -> convert the demo cells into a notebook
# - backend/requirements.txt -> add the dependencies

# Commit those files into a repo and push to GitHub.
'''
print("--- Helper instructions for repo creation ---")
print(helper)

# %%
# CELL: Save a small JSON sample of mock inbox for UI demo
sample_inbox = [
    {"id": e.id, "sender": e.sender, "subject": e.subject, "body": e.body, "received_at": e.received_at.isoformat()} for e in mock_inbox
]
with open('sample_inbox.json', 'w') as f:
    json.dump(sample_inbox, f, indent=2)
print('\nWrote sample_inbox.json (you can upload this to the Streamlit demo).')

# %%
# CELL: End of notebook file. Good luck!
print('\nSmartMailr demo cells complete. Copy this file into your Kaggle notebook or split into repo files as described.')
