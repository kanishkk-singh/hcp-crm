import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class HCP(Base):
    """Healthcare Professional master record."""
    __tablename__ = "hcps"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255))
    hospital = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="hcp", cascade="all, delete-orphan")


class Interaction(Base):
    """A single logged interaction between a rep and an HCP."""
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    hcp_id = Column(String(36), ForeignKey("hcps.id"), nullable=False)

    interaction_type = Column(String(50))       # call / visit / email / conference
    interaction_date = Column(DateTime, default=datetime.utcnow)
    topics_discussed = Column(Text)              # comma separated or JSON string
    samples_given = Column(Text)
    materials_shared = Column(Text)
    sentiment = Column(String(50))                # positive / neutral / negative
    summary = Column(Text)
    raw_input = Column(Text)                      # original chat/free-text the rep typed
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hcp = relationship("HCP", back_populates="interactions")
    followups = relationship("FollowUp", back_populates="interaction", cascade="all, delete-orphan")


class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    interaction_id = Column(String(36), ForeignKey("interactions.id"), nullable=False)
    due_date = Column(DateTime)
    note = Column(Text)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    interaction = relationship("Interaction", back_populates="followups")
