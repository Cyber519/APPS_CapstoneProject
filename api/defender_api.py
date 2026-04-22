from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()

@router.get("/vulnerabilities")
def get_vulnerabilities():
    with open(Path("data/defender_mock.json")) as f:
        return json.load(f)