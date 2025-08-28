from fastapi import APIRouter, Depends, HTTPException
from typing import Set
from locations.model.request.distance import DistanceRequest
from locations.model.response.distance import DistanceResponse
from locations.service.interfaces import DistanceService
from locations.service.ai_distance_service import AIDistanceService

router = APIRouter(prefix="/locations")

def get_service() -> DistanceService:
    return AIDistanceService()

@router.post("/", response_model=DistanceResponse)
def calc_distances(payload: DistanceRequest, svc: DistanceService = Depends(get_service)):
    try:
        resp = svc.calculate(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    req_refs: Set[str] = {d.ref for d in payload.destinations}
    if req_refs != set(resp.destinations.keys()):
        raise HTTPException(status_code=500, detail="destination keys mismatch")
    return resp
