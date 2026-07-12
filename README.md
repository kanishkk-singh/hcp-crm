<<<<<<< HEAD
# hcp-crm
=======
# AI-First CRM — HCP Module: Log Interaction Screen

An AI-first CRM module for pharma field reps to log, edit, and review interactions
with Healthcare Professionals (HCPs), via either a **structured form** or a
**conversational chat interface**, backed by a **LangGraph** agent running on **Groq**.

---

## 1. What this project understood from the task

A field rep visiting/calling a doctor needs a fast way to capture what happened —
without typing into 8 separate fields every time. This project gives them two
paths to the same outcome:

- **Structured form**: fill in fields directly, or type one free-text description
  and let the AI extract the fields for you.
- **Chat interface**: talk to the CRM agent naturally ("Met Dr. Sharma today,
  discussed the new cardiology drug, left 2 samples...") and the LangGraph agent
  decides which tool to call — log a new interaction, edit an old one, pull HCP
  history, schedule a follow-up, or summarize a visit for a manager.

The LangGraph agent is the core of the "AI-first" design: it's not just an LLM
call bolted onto CRUD — it's a routed, tool-using agent that keeps every write
to the database auditable (all writes go through a typed tool, never a raw LLM
free-text dump).

---

## 2. Tech stack

| Layer | Tech |
|---|---|
| Frontend | React + Redux Toolkit, Google Inter font |
| Backend | Python, FastAPI |
| AI Agent | LangGraph |
| LLMs | Groq — `gemma2-9b-it` (primary), `llama-3.3-70b-versatile` (context/summaries) |
| Database | PostgreSQL (SQLite fallback for local demo) |

---

## 3. LangGraph agent & tools

**Role of the agent**: The agent is the single entry point for all natural-language
interaction with the CRM. It receives the rep's message, decides intent, and
invokes exactly one of five tools to fulfil it, then confirms back in plain
language. This keeps the LLM's role to *understanding intent + extracting
structured data*, while all persistence logic lives in typed, testable Python
functions (the tools) — not inside the prompt.

**The 5 tools** (`backend/app/agent/tools.py`):

1. **`log_interaction`** *(mandatory)* — Takes an HCP id and the rep's raw
   free-text. Calls `gemma2-9b-it` with an extraction prompt to pull out
   `interaction_type`, `topics_discussed`, `samples_given`, `materials_shared`,
   `sentiment`, `follow_up_required`, `follow_up_notes`, and a short `summary`.
   Saves this as a new `Interaction` row, and auto-creates a `FollowUp` row if
   one was flagged.

2. **`edit_interaction`** *(mandatory)* — Takes an interaction id and a plain-English
   edit instruction (e.g. "change the follow-up date to next Monday and add that
   she asked about pediatric dosage"). Sends the current record + instruction to
   the LLM, gets back the full updated JSON, and writes only the changed fields
   back to the DB — so partial/ambiguous instructions don't wipe out untouched fields.

3. **`search_hcp_history`** — Pulls the N most recent interactions for a given
   HCP, so a rep can quickly get context before their next call/visit.

4. **`schedule_followup`** — Creates a `FollowUp` row tied to an interaction with
   a due date and note, and flags the parent interaction as needing follow-up.

5. **`summarize_interaction`** — Uses the larger `llama-3.3-70b-versatile` model
   to produce a 2-3 sentence manager-facing recap of an interaction, including
   an engagement/sentiment read.

The agent graph (`backend/app/agent/graph.py`) is a standard LangGraph
`agent -> tools -> agent` loop using `bind_tools` + `ToolNode` +
`tools_condition`, so the model itself decides which of the 5 tools to call
based on the conversation.

---

## 4. Project structure

```
hcp-crm/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, mounts routers, creates tables
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   ├── models.py            # HCP, Interaction, FollowUp tables
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── agent/
│   │   │   ├── llm.py           # Groq LLM clients (gemma2-9b-it, llama-3.3-70b)
│   │   │   ├── tools.py         # The 5 LangGraph tools
│   │   │   └── graph.py         # LangGraph agent definition
│   │   └── routers/
│   │       ├── hcp.py           # HCP CRUD
│   │       ├── interactions.py  # Structured-form path + edit/summarize
│   │       └── chat.py          # Conversational path (agent entry point)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── index.js / index.css
    │   ├── store/                # Redux Toolkit store + slices
    │   ├── components/
    │   │   ├── LogInteractionScreen.jsx   # form/chat toggle
    │   │   ├── StructuredForm.jsx
    │   │   ├── ChatInterface.jsx
    │   │   └── HcpSelector.jsx
    │   └── api/api.js            # axios client
    └── package.json
```

---

## 5. How to run it

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: add your GROQ_API_KEY (https://console.groq.com/keys)
# and DATABASE_URL (Postgres, or sqlite:///./hcp_crm.db for a quick local demo)

uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

Create a demo HCP first (via Swagger UI or curl):

```bash
curl -X POST http://localhost:8000/api/hcps/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Dr. Sharma", "specialty": "Cardiology", "hospital": "City Hospital"}'
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Runs at `http://localhost:3000`, calling the backend at `http://localhost:8000`
(override with `REACT_APP_API_BASE` env var if needed).

### Postgres quick setup (optional, for full DB)

```bash
createdb hcp_crm
# DATABASE_URL=postgresql://<user>:<pass>@localhost:5432/hcp_crm
```

If you don't have Postgres installed, just set `DATABASE_URL=sqlite:///./hcp_crm.db`
in `.env` — the schema is identical, only the connection string changes.

---

## 6. Key API endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/hcps/` | Create an HCP |
| GET | `/api/hcps/` | List HCPs |
| POST | `/api/interactions/` | Log interaction (manual fields or `raw_input` for AI extraction) |
| GET | `/api/interactions/?hcp_id=...` | List interactions for an HCP |
| PATCH | `/api/interactions/{id}` | Manually update fields |
| POST | `/api/interactions/{id}/edit-nl` | Natural-language edit via `edit_interaction` tool |
| POST | `/api/interactions/{id}/summarize` | Run `summarize_interaction` tool |
| POST | `/api/chat/` | Send a message to the LangGraph agent (routes to any of the 5 tools) |

---

## 7. Notes / assumptions

- Chat session history is kept in-memory per `hcp_id` for simplicity — a
  production build would persist this per rep/session in the DB or Redis.
- `search_hcp_history` and `schedule_followup` are exposed only through the chat
  agent in this build, since the form UI's job is fast structured logging, not
  history browsing.
- Both the form (assisted mode) and chat paths call the exact same
  `log_interaction` tool, so the extracted record shape is always consistent
  regardless of entry mode.
>>>>>>> e3d9f37 (AI-First CRM - HCP Module: Log Interaction Screen)
