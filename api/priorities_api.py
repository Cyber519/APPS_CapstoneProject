from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.ingestion_service import ingest_all_data
from services.scoring_service import (
    calculate_priority_scores,
    get_priority_list,
    simulate_deployment,
    approve_deployment,
    get_score_detail,
    export_priorities_csv,
)
from pydantic import BaseModel


class ApproveRequest(BaseModel):
    approver: str

router = APIRouter()

@router.post("/ingest")
def ingest():
    ingest_all_data()
    return {"status": "Ingestion complete"}

@router.post("/score")
def score():
    calculate_priority_scores()
    return {"status": "Scoring complete"}

@router.get("/priorities")
def priorities():
    return get_priority_list()

@router.get("/priorities/{score_id}")
def priority_detail(score_id: int):
    return get_score_detail(score_id)

@router.get("/export-csv")
def export_csv():
    csv_data = export_priorities_csv()
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=priorities.csv"}
    )

@router.post("/deploy/{score_id}")
def deploy(score_id: int):
    try:
        simulate_deployment(score_id)
        return {"status": "Deployment simulated", "score_id": score_id}
    except ValueError as e:
        # Duplicate or other business logic error
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Deployment failed")


@router.post("/deploy/{score_id}/approve")
def approve(score_id: int, req: ApproveRequest):
    try:
        approve_deployment(score_id, req.approver)
        return {"status": "Approved", "score_id": score_id, "approver": req.approver}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Approval failed")