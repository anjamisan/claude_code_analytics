from fastapi import Depends
from sqlalchemy.orm import Session
from ..db.connection import get_db
from ..models.telemetry import TelemetryEvent

def get_telemetry_event(db: Session = Depends(get_db), event_id: int):
    return db.query(TelemetryEvent).filter(TelemetryEvent.id == event_id).first()