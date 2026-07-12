"""
The 5 LangGraph tools for the HCP interaction agent.

1. log_interaction      -- mandatory
2. edit_interaction      -- mandatory
3. search_hcp_history
4. schedule_followup
5. summarize_interaction
"""
import json
from datetime import datetime, timedelta

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import HCP, Interaction, FollowUp
from app.agent.llm import llm_primary, llm_context, extract_json


def _db() -> Session:
    return SessionLocal()


# ---------------------------------------------------------------------------
# TOOL 1 (mandatory): log_interaction
# ---------------------------------------------------------------------------
@tool
def log_interaction(hcp_id: str, raw_text: str) -> str:
    """Log a new HCP interaction from a rep's free-text/chat description.

    Uses the LLM to extract structured fields (interaction type, topics discussed,
    samples given, materials shared, sentiment, follow-up needed) from raw_text,
    then saves a new Interaction row against the given hcp_id.

    Args:
        hcp_id: The ID of the HCP this interaction is about.
        raw_text: The rep's free-text description of what happened, e.g.
            "Met Dr. Sharma at City Hospital today, discussed the new cardiology
            drug, left 2 samples, she wants a follow up call next week."
    """
    db = _db()
    try:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"No HCP found with id {hcp_id}"})

        extraction_prompt = f"""You are a life-science CRM assistant. Extract structured
data from a pharma sales rep's description of a visit/call with a doctor.

Return ONLY valid JSON with these exact keys:
- interaction_type: one of "visit", "call", "email", "conference"
- topics_discussed: short comma-separated string of topics/drugs discussed
- samples_given: comma-separated string of samples given, or "" if none
- materials_shared: comma-separated string of brochures/materials shared, or ""
- sentiment: one of "positive", "neutral", "negative" (HCP's receptiveness)
- follow_up_required: true or false
- follow_up_notes: short string describing the follow-up needed, or ""
- summary: a 1-2 sentence professional summary of the interaction

Rep's description:
\"\"\"{raw_text}\"\"\"

JSON:"""

        response = llm_primary.invoke(extraction_prompt)
        data = extract_json(response.content)

        interaction = Interaction(
            hcp_id=hcp_id,
            interaction_type=data.get("interaction_type", "visit"),
            topics_discussed=data.get("topics_discussed", ""),
            samples_given=data.get("samples_given", ""),
            materials_shared=data.get("materials_shared", ""),
            sentiment=data.get("sentiment", "neutral"),
            summary=data.get("summary", raw_text[:200]),
            raw_input=raw_text,
            follow_up_required=bool(data.get("follow_up_required", False)),
            follow_up_notes=data.get("follow_up_notes", ""),
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        # auto-create a FollowUp row if the LLM flagged one
        if interaction.follow_up_required:
            fu = FollowUp(
                interaction_id=interaction.id,
                due_date=datetime.utcnow() + timedelta(days=7),
                note=interaction.follow_up_notes or "Follow up with HCP",
            )
            db.add(fu)
            db.commit()

        return json.dumps({
            "status": "success",
            "interaction_id": interaction.id,
            "extracted": data,
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# TOOL 2 (mandatory): edit_interaction
# ---------------------------------------------------------------------------
@tool
def edit_interaction(interaction_id: str, edit_instruction: str) -> str:
    """Modify a previously logged interaction using a natural-language instruction.

    Example edit_instruction: "change the follow up date to next Monday and
    add that she also asked for pediatric dosage data."

    Args:
        interaction_id: ID of the interaction to edit.
        edit_instruction: What the rep wants to change, in plain English.
    """
    db = _db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return json.dumps({"error": f"No interaction found with id {interaction_id}"})

        current_state = {
            "interaction_type": interaction.interaction_type,
            "topics_discussed": interaction.topics_discussed,
            "samples_given": interaction.samples_given,
            "materials_shared": interaction.materials_shared,
            "sentiment": interaction.sentiment,
            "summary": interaction.summary,
            "follow_up_required": interaction.follow_up_required,
            "follow_up_notes": interaction.follow_up_notes,
        }

        edit_prompt = f"""You are editing a CRM record for an HCP interaction.

Current record (JSON):
{json.dumps(current_state, indent=2)}

The rep wants this change:
\"\"\"{edit_instruction}\"\"\"

Return ONLY the full updated JSON object with the same keys as the current
record, applying the requested change and leaving everything else unchanged.

JSON:"""

        response = llm_primary.invoke(edit_prompt)
        updated = extract_json(response.content)

        for field in current_state.keys():
            if field in updated and updated[field] not in (None, ""):
                setattr(interaction, field, updated[field])

        interaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(interaction)

        return json.dumps({
            "status": "success",
            "interaction_id": interaction.id,
            "updated_fields": updated,
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# TOOL 3: search_hcp_history
# ---------------------------------------------------------------------------
@tool
def search_hcp_history(hcp_id: str, limit: int = 5) -> str:
    """Retrieve recent past interactions for an HCP so the rep has context
    before their next call or visit.

    Args:
        hcp_id: The HCP to look up.
        limit: Max number of past interactions to return (default 5).
    """
    db = _db()
    try:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"No HCP found with id {hcp_id}"})

        rows = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id)
            .order_by(Interaction.interaction_date.desc())
            .limit(limit)
            .all()
        )
        history = [{
            "id": r.id,
            "date": r.interaction_date.isoformat(),
            "type": r.interaction_type,
            "topics": r.topics_discussed,
            "sentiment": r.sentiment,
            "summary": r.summary,
        } for r in rows]

        return json.dumps({"hcp_name": hcp.name, "history": history})
    finally:
        db.close()


# ---------------------------------------------------------------------------
# TOOL 4: schedule_followup
# ---------------------------------------------------------------------------
@tool
def schedule_followup(interaction_id: str, note: str, days_from_now: int = 7) -> str:
    """Create or update a follow-up task tied to a logged interaction.

    Args:
        interaction_id: The interaction this follow-up relates to.
        note: What needs to be done in the follow-up.
        days_from_now: Days from today when the follow-up is due (default 7).
    """
    db = _db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return json.dumps({"error": f"No interaction found with id {interaction_id}"})

        fu = FollowUp(
            interaction_id=interaction_id,
            due_date=datetime.utcnow() + timedelta(days=days_from_now),
            note=note,
        )
        db.add(fu)

        interaction.follow_up_required = True
        interaction.follow_up_notes = note
        db.commit()
        db.refresh(fu)

        return json.dumps({
            "status": "success",
            "followup_id": fu.id,
            "due_date": fu.due_date.isoformat(),
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# TOOL 5: summarize_interaction
# ---------------------------------------------------------------------------
@tool
def summarize_interaction(interaction_id: str) -> str:
    """Generate a concise manager-facing summary of a logged interaction,
    including HCP engagement/sentiment read, using the larger context model.

    Args:
        interaction_id: The interaction to summarize.
    """
    db = _db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return json.dumps({"error": f"No interaction found with id {interaction_id}"})

        prompt = f"""Summarize this pharma HCP interaction for a sales manager review,
in 2-3 crisp sentences. Mention engagement level and any risk/opportunity signal.

Interaction type: {interaction.interaction_type}
Topics discussed: {interaction.topics_discussed}
Samples given: {interaction.samples_given}
Sentiment: {interaction.sentiment}
Raw notes: {interaction.raw_input}

Summary:"""

        response = llm_context.invoke(prompt)
        summary_text = response.content.strip()

        interaction.summary = summary_text
        db.commit()

        return json.dumps({"interaction_id": interaction_id, "summary": summary_text})
    finally:
        db.close()


ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    search_hcp_history,
    schedule_followup,
    summarize_interaction,
]
