# AI-First CRM — HCP Module: Log Interaction Screen

An AI-first CRM module for pharma field reps to log, edit, and review interactions
with Healthcare Professionals (HCPs), via either a structured form or a
conversational chat interface, backed by a LangGraph agent running on Groq.

---

## 1. What this project does

A field rep visiting or calling a doctor needs a fast way to capture what happened
without typing into multiple fields every time. This project gives them two paths to
reach the same outcome:

- Structured form: fill in fields directly, or type one free-text description and let the AI extract the fields for you.
- Chat interface: talk to the CRM agent naturally, and the LangGraph agent decides which tool to call — log a new interaction, edit an old one, pull HCP history, schedule a follow-up, or summarize a visit for a manager.

The LangGraph agent is the core of the “AI-first” design: it routes the request to typed tools instead of letting the LLM write directly to the database.

---

## 2. Tech stack

| Layer | Tech |
|---|---|
| Frontend | React + Redux Toolkit |
| Backend | Python + FastAPI |
| AI Agent | LangGraph |
| LLMs | Groq |
| Database | SQLite for local demo, PostgreSQL-ready via SQLAlchemy |

---

## 3. Core features

### Structured logging
- Fill in interaction details manually.
- Or describe the interaction in plain English and let AI extract the fields.

### Conversational chat agent
- Send natural language messages such as:
  - “Met Dr. Sharma today, discussed the new cardiology drug, left 2 samples.”
  - “Show me the last 5 interactions for this HCP.”
  - “Schedule a follow-up in 7 days.”
  - “Summarize this interaction for my manager.”

### Tool-based workflow
The chat agent uses tools for:
1. Log interaction
2. Edit interaction
3. Search HCP history
4. Schedule follow-up
5. Summarize interaction

These tools are implemented in backend/app/agent/tools.py.

---

## 4. Project structure

```text
hcp-crm/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── agent/
│   │   │   ├── llm.py
│   │   │   ├── tools.py
│   │   │   └── graph.py
│   │   └── routers/
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── package.json
    └── src/
```

---

## 5. How to run it on Windows PowerShell

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
```

Edit backend/.env and set:

```text
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./hcp_crm.db
```

Start the backend:

```powershell
uvicorn app.main:app --reload --port 8000
```

Open:
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Frontend

Open a second PowerShell window:

```powershell
cd frontend
npm install
npm start
```

Open:
- Frontend UI: http://localhost:3000

---

## 6. Create a demo HCP

Once the backend is running, create a sample HCP with:

```powershell
$body = '{"name":"Dr. Sharma","specialty":"Cardiology","hospital":"City Hospital"}'
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/api/hcps/' -ContentType 'application/json' -Body $body
```

---

## 7. Where data is stored

For local development, the app uses SQLite. The database file is:

```text
backend/hcp_crm.db
```

Tables include:
- hcps
- interactions
- followups

---

## 8. Troubleshooting

### PowerShell blocks the venv activation script
Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### AI chat shows a generic error
Check:
- backend/.env has a valid GROQ_API_KEY
- the model names are still valid in backend/.env
- the backend was restarted after changing the model settings

---

## 9. Notes

- Chat session history is kept in-memory per HCP for this demo.
- The structured form and chat flow both use the same backend tool logic, so the stored interaction shape stays consistent.
