from fastapi import APIRouter, Request, BackgroundTasks
from app.database import SessionLocal
from app.models import CallRecord
from app.services.analysis.llm_processor import analyze_call

router = APIRouter()

@router.post("/webhook/call-e")
async def calle_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    call_id = payload.get("call_id")
    transcript = payload.get("transcript", "")
    structured = payload.get("structured_result", {})

    db = SessionLocal()
    record = CallRecord(
        calle_call_id=call_id,
        transcript=transcript,
        structured_result=structured
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    db.close()

    # Kick off async LLM analysis
    background_tasks.add_task(analyze_call, record.id)

    return {"status": "stored", "id": record.id}