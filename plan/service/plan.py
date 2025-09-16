# plan/service/ai_plan.py
from __future__ import annotations
import os, json, re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any, List

from rag import ToolExecutor, TOOL_SCHEMAS
from rag.openai_adapter import OpenAIChatTools
from util.openai_client import openai_async_client

from plan.model.request.plan import PlanRequest as AIPlanRequest
from plan.model.response.plan import AIPlanResponse

# 시스템 프롬프트: 주소 포함, 모호성 제거, 도구 사용 필수
SYSTEM_PROMPT = """You are an itinerary planner that MUST use the provided TourAPI tools to gather places.
Hard rules:
- You MUST call tools (searchKeyword, locationBasedList, etc.) to fetch real places.
- Every place in the final plan MUST include a precise address in the string: "title — addr1 addr2".
- If a candidate place has no addr1/addr2, prefer another. If still none, skip or replace with a place that has address.
- Resolve ambiguous names by adding district/branch details returned by the tools.

Output ONLY valid JSON with this exact schema:
{
  "start_date": "yyyy-mm-dd",
  "end_date": "yyyy-mm-dd",
  "plan": [
    [ { "todo": "...", "place": "title — addr1 addr2", "time": "yyyy-mm-dd-hh-MM" }, ... ],
    ...
  ]
}
Additional rules:
- plan[n] corresponds to day n+1 between start_date and end_date inclusive.
- Use bookmarked places with priority when relevant.
- Keep reasonable hours based on user's preferred_time.
- Korean text for todo/place is OK.
Return ONLY JSON. No explanations.
"""

def _date_range_days(start: datetime, end: datetime) -> int:
    return (end.date() - start.date()).days + 1

def _fmt_ok(s: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$", s))

async def generate_ai_plan(req: AIPlanRequest, accept_tz: str | None) -> AIPlanResponse:
    # LLM 클라이언트/어댑터/도구 실행기
    client = openai_async_client()
    adapter = OpenAIChatTools(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), client=client)
    executor = ToolExecutor(api_key=os.environ["TOURAPI_KEY"])

    # 타임존
    client_tz = accept_tz or "UTC"
    try:
        tzinfo = ZoneInfo(client_tz)
    except Exception:
        tzinfo = ZoneInfo("UTC")

    # 사용자 입력
    user_payload: Dict[str, Any] = req.model_dump()
    user_payload["_meta"] = {
        "timezone": client_tz,
        "note": "All times in the final JSON must respect this timezone; format yyyy-mm-dd-hh-MM.",
    }

    # 대화 초기화
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Build a day-by-day plan using this input:\n{user_payload}"},
    ]

    # 도구 사용을 강제하고, 더 이상 툴콜이 안 나올 때까지 반복 수집
    # 안전장치: 최대 4 라운드
    tool_rounds = 0
    try:
        while tool_rounds < 4:
            # 첫 라운드는 무조건 required로 툴콜 강제
            tool_choice = "required" if tool_rounds == 0 else "auto"
            resp = await adapter.create_completion(messages=messages, tools=TOOL_SCHEMAS, tool_choice=tool_choice)

            # OpenAI 호환 tool_calls 읽기
            tcs = getattr(resp.choices[0].message, "tool_calls", None) or []
            if not tcs:
                # 첫 라운드부터 툴콜이 없으면 명시적으로 실패 처리
                if tool_rounds == 0:
                    raise RuntimeError("LLM did not call any tools; tool usage is mandatory.")
                # 이전 라운드에서 이미 도구 많이 썼다면 탈출
                break

            # 툴콜 실행
            tool_msgs = await executor.consume_tool_calls(resp)

            # 실행 결과를 대화에 축적
            messages.append(resp.choices[0].message)
            messages.extend(tool_msgs)

            tool_rounds += 1

        # 최종 산출(도구 사용 금지, 순수 JSON만)
        messages.append({
            "role": "system",
            "content": "Now produce ONLY the final JSON per the schema. Ensure each place includes ' — ' followed by addr1 and addr2."
        })
        final_resp = await adapter.create_completion(messages=messages, tools=None, tool_choice=None)
        raw = final_resp.choices[0].message.content or ""
    finally:
        await executor.close()

    # 파싱
    data = json.loads(raw)

    # 최소 정합성 보정
    start_dt = datetime.fromisoformat(req.start_date).replace(tzinfo=timezone.utc).astimezone(tzinfo)
    end_dt = datetime.fromisoformat(req.end_date).replace(tzinfo=timezone.utc).astimezone(tzinfo)
    days = max(1, _date_range_days(start_dt, end_dt))

    plan = data.get("plan", [])
    # 길이 보정
    if len(plan) != days:
        if len(plan) > days:
            plan = plan[:days]
        else:
            for _ in range(days - len(plan)):
                base_day = start_dt + timedelta(days=len(plan))
                hour_map = {"morning": 9, "afternoon": 13, "evening": 18}
                pref = (req.preferred_time or "morning").strip().lower()
                hour = hour_map.get(pref, 9)
                filler_time = base_day.replace(hour=hour, minute=0)
                plan.append([{
                    "todo": "자유 시간",
                    "place": f"{req.destination} — 정확한 주소 필요",
                    "time": filler_time.strftime("%Y-%m-%d-%H-%M")
                }])

    # 시간/주소 형식 점검 및 미흡 시 경고성 보정
    for day_idx, day in enumerate(plan):
        for item in day:
            # time 형식 보정
            t = item.get("time")
            if not isinstance(t, str) or not _fmt_ok(t):
                base = start_dt + timedelta(days=day_idx)
                hour_map = {"morning": 9, "afternoon": 13, "evening": 18}
                pref = (req.preferred_time or "morning").strip().lower()
                hour = hour_map.get(pref, 9)
                fixed = base.replace(hour=hour, minute=0)
                item["time"] = fixed.strftime("%Y-%m-%d-%H-%M")

            # place에 주소 포함 여부 보정 시도는 하지 않는다.
            # 여기서는 포맷만 확인하고, 없으면 그대로 두어 클라이언트가 감지 가능하게 한다.
            p = str(item.get("place", ""))
            if " — " not in p:
                # 무리한 조작 대신 경고성 마커만 유지
                item["place"] = f"{p} — 주소확인필요"

    out = {
        "start_date": req.start_date,
        "end_date": req.end_date,
        "plan": plan,
    }
    return AIPlanResponse.model_validate(out)
