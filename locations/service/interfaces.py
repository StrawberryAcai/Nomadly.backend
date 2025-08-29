from typing import Protocol
from locations.model.request.distance import DistanceRequest
from locations.model.response.distance import DistanceResponse

class DistanceService(Protocol):
    def calculate(self, payload: DistanceRequest) -> DistanceResponse: ...