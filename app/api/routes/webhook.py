from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import CallRecord
from app.services.analysis.llm_processor import analyze_call

router = APIRouter()

class CallWebhookPayload(BaseModel):
    call_id: str = Field(min_length=1)
    transcript: str = ""
    structured_result: dict[str, Any] = Field(default_factory=dict)


@router.post("/webhook/call-e")
async def calle_webhook(payload: CallWebhookPayload, background_tasks: BackgroundTasks):
    db = SessionLocal()
    record = None
    try:
        record = db.query(CallRecord).filter_by(calle_call_id=payload.call_id).first()
        if record is not None:
            return {"status": "already_stored", "id": record.id}

        record = CallRecord(
            calle_call_id=payload.call_id,
            transcript=payload.transcript,
            structured_result=payload.structured_result,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        record = db.query(CallRecord).filter_by(calle_call_id=payload.call_id).first()
        if record is None:
            raise HTTPException(status_code=409, detail="Call could not be stored")
        return {"status": "already_stored", "id": record.id}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Call could not be stored") from exc
    finally:
        db.close()

    background_tasks.add_task(analyze_call, record.id)
    return {"status": "stored", "id": record.id}