from fastapi import APIRouter
from services.ingestion_service import ingest_all_data
from services.scoring_service import calculate_priority_scores, get_priority_list, simulate_deployment

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

@router.post("/deploy/{score_id}")
def deploy(score_id: int):
    simulate_deployment(score_id)
    return {"status": "Deployment simulated", "score_id": score_id}