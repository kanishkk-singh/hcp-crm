from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Interaction
from app.schemas import InteractionCreate, InteractionUpdate, InteractionOut
from app.agent.tools import log_interaction, edit_interaction, summarize_interaction

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])


@router.post("/", response_model=dict)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    """Structured-form path. If raw_input is given, we still run it through the
    same log_interaction tool the chat path uses, so both entry modes produce
    identically-shaped, LLM-enriched records."""
    if payload.raw_input:
        result = log_interaction.invoke({
            "hcp_id": payload.hcp_id,
            "raw_text": payload.raw_input,
        })
        return {"source": "llm_enriched", "result": result}

    interaction = Interaction(**payload.model_dump(exclude={"raw_input"}))
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return {"source": "manual_form", "interaction_id": interaction.id}


@router.get("/", response_model=list[InteractionOut])
def list_interactions(hcp_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Interaction)
    if hcp_id:
        q = q.filter(Interaction.hcp_id == hcp_id)
    return q.order_by(Interaction.interaction_date.desc()).all()


@router.get("/{interaction_id}", response_model=InteractionOut)
def get_interaction(interaction_id: str, db: Session = Depends(get_db)):
    row = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not row:
        raise HTTPException(404, "Interaction not found")
    return row


@router.patch("/{interaction_id}")
def update_interaction(interaction_id: str, payload: InteractionUpdate, db: Session = Depends(get_db)):
    row = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not row:
        raise HTTPException(404, "Interaction not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return {"status": "updated", "interaction_id": row.id}


@router.post("/{interaction_id}/edit-nl")
def edit_interaction_nl(interaction_id: str, instruction: str, db: Session = Depends(get_db)):
    """Natural-language edit -- directly invokes the edit_interaction LangGraph tool."""
    result = edit_interaction.invoke({
        "interaction_id": interaction_id,
        "edit_instruction": instruction,
    })
    return {"result": result}


@router.post("/{interaction_id}/summarize")
def summarize(interaction_id: str):
    result = summarize_interaction.invoke({"interaction_id": interaction_id})
    return {"result": result}
