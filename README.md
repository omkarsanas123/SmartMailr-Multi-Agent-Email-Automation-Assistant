# SmartMailr-Multi-Agent-Email-Automation-Assistant
People receive hundreds of emails every week—meeting requests, document approvals, follow-ups, reminders, and more. 
SmartMailr solves this problem by building an intelligent multi-agent system that automatically processes emails, understands intent, drafts replies, summarizes inboxes, and performs actions like scheduling meetings or sending reminders.
Why Agents?

Emails are messy and unstructured. A single email can contain:
✔ tasks, ✔ dates, ✔ requests, ✔ documents, ✔ follow-up items

Using multiple specialized agents makes the system powerful because each agent handles one specific capability:

One agent understands what the email wants

Another writes the perfect reply

Another checks facts

Another performs actions like scheduling

This teamwork makes automation accurate and scalable.

What I Created (Architecture Overview)
🔹 1. Email Reader Agent

Connects to Gmail inbox

Reads unread emails

Extracts sender, subject, body

🔹 2. Intent Classifier Agent

Understands what the email wants:

“Schedule a meeting”

“Send a file”

“Answer a question”

“Acknowledge status”

“Summarize document”

🔹 3. Reply Generator Agent

Writes professional email replies

Supports multiple styles (formal, simple, friendly)

🔹 4. Action Executor Agent

Sends emails

Creates calendar events

Sets reminders

Extracts attachments

🔹 5. QA & Correction Agent

Checks grammar

Fixes tone

Removes errors

Ensures correctness

Flow of the System

New email arrives

Reader agent fetches + cleans it

Intent agent detects what user should do

Worker agents generate the reply

QA agent polishes it

Final reply is sent automatically

User gets a daily summary of inbox actions

Demo (Example Run)
Email Received:

“Hi Omkar, can we meet tomorrow at 4 PM to discuss the dataset? Let me know.”

Agents Work:

Intent Agent: Meeting request

Reply Agent:
“Hi, yes 4 PM works. I will send a calendar invite shortly.”

Action Agent: Creates Google Calendar event

Email Sender Agent: Sends the reply

Output Sent Automatically:

“Meeting confirmed for tomorrow at 4 PM.”

The Build (Tools & Tech Used)

Gemini API for reasoning and text generation

LangGraph for agent orchestration

Python for backend

FastAPI for API server

Gmail API to fetch + send emails

Google Calendar API for scheduling

SQLite to store logs

Streamlit for UI dashboard

Main Features Built:

✔ Inbox reading & summarization
✔ Auto reply generation
✔ Multi-agent collaboration
✔ Email tone correction
✔ Scheduling and reminders
✔ Daily digest

If I Had More Time…

I would add:

Voice-based email assistant

Multi-language emails (Hindi + English)

RAG-based document attachment understanding

Auto-prioritization of important mails

WhatsApp notification integration

🔗 Attachments You Can Add:

GitHub Code

YouTube Demo

Kaggle Notebook

If you want, I can also give you:

✅ GitHub-ready code
✅ A 560×280 thumbnail image
✅ A YouTube script for demo
✅ UI design for your project
