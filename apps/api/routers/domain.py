import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["domain"])

REPO_ROOT = Path(__file__).resolve().parents[3]
DOMAIN_ROOT = REPO_ROOT / "domain-packs"


@router.get("/domains/{domain_name}")
def domain_pack(domain_name: str) -> dict:
    path = DOMAIN_ROOT / domain_name / "domain.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Unknown domain pack: {domain_name}")
    return json.loads(path.read_text())

