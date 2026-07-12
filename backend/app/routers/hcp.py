from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HCP
from app.schemas import HCPCreate, HCPOut

router = APIRouter(prefix="/api/hcps", tags=["HCPs"])


@router.post("/", response_model=HCPOut)
def create_hcp(payload: HCPCreate, db: Session = Depends(get_db)):
    hcp = HCP(**payload.model_dump())
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


@router.get("/", response_model=list[HCPOut])
def list_hcps(db: Session = Depends(get_db)):
    return db.query(HCP).all()


@router.get("/{hcp_id}", response_model=HCPOut)
def get_hcp(hcp_id: str, db: Session = Depends(get_db)):
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(404, "HCP not found")
    return hcp
