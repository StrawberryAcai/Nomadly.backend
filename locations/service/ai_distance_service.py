import json, math
from typing import Dict, List
from util.openai_client import openai_client
from locations.model.request.distance import DistanceRequest
from locations.model.response.distance import DistanceResponse, DestinationOut

MAX_M = 21_000_000

class AIDistanceService:
    def __init__(self, model: str = "gpt-4o-mini", base_url: str | None = None):
        self.client = openai_client()
        self.model = model
    # 거의 신뢰 불가능합니다, 어떠한 위치가 A일떄 origin을 A의 위도, 경도, destination을 위치의 주소로하면 0이 아니라 거의 난수를 생성합니다
    def calculate(self, payload: DistanceRequest) -> DistanceResponse:
        schema = self._schema([d.ref for d in payload.destinations])
        r = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role":"system","content":"Compute great-circle distance in meters. Return only JSON per schema."},
                {"role":"user","content":json.dumps({
                    "origin":{"latitude":payload.origin.latitude,"longitude":payload.origin.longitude},
                    "destinations":{d.ref:d.address for d in payload.destinations}
                }, ensure_ascii=False)}
            ],
            response_format={"type":"json_schema","json_schema":schema}
        )
        data = json.loads(r.choices[0].message.content)["destinations"]
        out: Dict[str, dict] = {}
        for d in payload.destinations:
            x = float(data[d.ref]["distance"])
            if not math.isfinite(x) or not (0 <= x <= MAX_M):
                raise ValueError("invalid distance")
            out[d.ref] = DestinationOut(
                distance=int(round(x)),
                address=data[d.ref].get("address") or d.address
            ).model_dump()

        return DistanceResponse.model_validate({
            "origin": payload.origin.model_dump(),
            "destinations": out
        })

    def _schema(self, refs: List[str]) -> dict:
        props = {r: {"type":"object","properties":{
            "distance":{"type":"number","minimum":0,"maximum":MAX_M},
            "address":{"type":"string"}}, "required":["distance","address"],
            "additionalProperties":False} for r in refs}
        return {"name":"distance","schema":{"type":"object","properties":{
            "destinations":{"type":"object","properties":props,"required":refs,"additionalProperties":False}},
            "required":["destinations"],"additionalProperties":False},"strict":True}
