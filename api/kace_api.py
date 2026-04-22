from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()

@router.get("/devices-mock")
def get_devices_mock():
    with open(Path("data/kace_devices.json")) as f:
        return json.load(f)

@router.get("/patches-mock")
def get_patches_mock():
    with open(Path("data/kace_patches.json")) as f:
        return json.load(f)