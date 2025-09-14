from httpx import AsyncClient
from typing import Dict, Any, Optional
from httpx import Response
from .exceptions import *

BASE_URL = "http://apis.data.go.kr/B551011/KorService2"

def _require(dep_ok: bool, msg: str) -> None:
    if not dep_ok:
        raise ValueError(msg)

def _push(d: Dict[str, Any], k: str, v: Any) -> None:
    if v is not None:
        d[k] = v

class TourAPIClient:
    def __init__(self, api_key: str, app_name: str = "Nomadly", timeout: float = 10.0) -> None:
        self.api_key = api_key
        self.app_name = app_name
        self.client = AsyncClient(base_url=BASE_URL, timeout=timeout)

    async def close(self) -> None:
        await self.client.aclose()

    async def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        base = {
            "serviceKey": self.api_key,
            "_type": "json",
            "MobileOS": "ETC",
            "MobileApp": self.app_name,
        }
        base.update(params)
        url = f"{BASE_URL}{path}"
        r: Response = await self.client.get(url, params=base)
        r.raise_for_status()
        text = r.text

        # 1) JSON 우선
        try:
            data = r.json()
        except json.JSONDecodeError:
            # 2) 포털(XML) 오류 파싱
            try:
                root = ET.fromstring(text)
                hdr = root.find(".//cmmMsgHeader")
                if hdr is not None:
                    code = (hdr.findtext("returnReasonCode") or "").strip()
                    msg = (hdr.findtext("errMsg") or hdr.findtext("returnAuthMsg") or "").strip()
                    raise_portal(code, msg, text)
            except ET.ParseError:
                pass
            # 3) 알 수 없는 비JSON 응답
            raise PortalUnknownError("Non-JSON response", raw=text)

        # 4) 제공기관 헤더 코드 검사
        try:
            header = data["response"]["header"]
            code = str(header.get("resultCode", "")).strip()
            msg = str(header.get("resultMsg", "")).strip()
            raise_provider(code, msg, data)
        except (KeyError, TypeError):
            # 헤더가 없으면 원문 반환
            return data

        return data

    # 1) 지역코드 조회
    async def get_areacode(self, area_code: Optional[int] = None, num_of_rows: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        p: Dict[str, Any] = {}
        _push(p, "areaCode", area_code)
        _push(p, "numOfRows", num_of_rows)
        _push(p, "pageNo", page_no)
        return await self._get("/areaCode2", p)

    # 2) 서비스 분류코드 조회
    async def get_category_code(self, content_type_id: Optional[int] = None, cat1: Optional[str] = None, cat2: Optional[str] = None, cat3: Optional[str] = None, num_of_rows: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        p: Dict[str, Any] = {}
        _push(p, "contentTypeId", content_type_id)
        if cat2 is not None:
            _require(cat1 is not None, "cat2 사용 시 cat1 필요")
        if cat3 is not None:
            _require(cat1 is not None and cat2 is not None, "cat3 사용 시 cat1, cat2 필요")
        _push(p, "cat1", cat1)
        _push(p, "cat2", cat2)
        _push(p, "cat3", cat3)
        _push(p, "numOfRows", num_of_rows)
        _push(p, "pageNo", page_no)
        return await self._get("/categoryCode2", p)

    # 3) 지역기반 관광정보 조회
    async def get_area_based_list(
        self,
        arrange: Optional[str] = None,
        content_type_id: Optional[int] = None,
        area_code: Optional[int] = None,
        sigungu_code: Optional[int] = None,
        cat1: Optional[str] = None, cat2: Optional[str] = None, cat3: Optional[str] = None,
        modified_time: Optional[str] = None,  # YYYYMMDD or YYYYMMDDHHMMSS
        l_dong_regn_cd: Optional[int] = None, l_dong_signgu_cd: Optional[int] = None,
        lcls1: Optional[str] = None, lcls2: Optional[str] = None, lcls3: Optional[str] = None,
        num_of_rows: Optional[int] = None, page_no: Optional[int] = None,
    ) -> Dict[str, Any]:
        if sigungu_code is not None:
            _require(area_code is not None, "sigunguCode 사용 시 areaCode 필요")
        if cat2 is not None:
            _require(cat1 is not None, "cat2 사용 시 cat1 필요")
        if cat3 is not None:
            _require(cat1 is not None and cat2 is not None, "cat3 사용 시 cat1, cat2 필요")
        if l_dong_signgu_cd is not None:
            _require(l_dong_regn_cd is not None, "lDongSignguCd 사용 시 lDongRegnCd 필요")
        if lcls2 is not None:
            _require(lcls1 is not None, "lclsSystm2 사용 시 lclsSystm1 필요")
        if lcls3 is not None:
            _require(lcls1 is not None and lcls2 is not None, "lclsSystm3 사용 시 lclsSystm1, lclsSystm2 필요")

        p: Dict[str, Any] = {}
        _push(p, "arrange", arrange)
        _push(p, "contentTypeId", content_type_id)
        _push(p, "areaCode", area_code)
        _push(p, "sigunguCode", sigungu_code)
        _push(p, "cat1", cat1); _push(p, "cat2", cat2); _push(p, "cat3", cat3)
        _push(p, "modifiedtime", modified_time)
        _push(p, "lDongRegnCd", l_dong_regn_cd); _push(p, "lDongSignguCd", l_dong_signgu_cd)
        _push(p, "lclsSystm1", lcls1); _push(p, "lclsSystm2", lcls2); _push(p, "lclsSystm3", lcls3)
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/areaBasedList2", p)

    # 4) 위치기반 관광정보 조회
    async def get_location_based_list(
        self,
        map_x: float, map_y: float, radius: int,
        arrange: Optional[str] = None,
        content_type_id: Optional[int] = None,
        cat1: Optional[str] = None, cat2: Optional[str] = None, cat3: Optional[str] = None,
        lcls1: Optional[str] = None, lcls2: Optional[str] = None, lcls3: Optional[str] = None,
        num_of_rows: Optional[int] = None, page_no: Optional[int] = None,
    ) -> Dict[str, Any]:
        _require(1 <= radius <= 20000, "radius 1~20000(m) 범위 필요")
        if cat2 is not None:
            _require(cat1 is not None, "cat2 사용 시 cat1 필요")
        if cat3 is not None:
            _require(cat1 is not None and cat2 is not None, "cat3 사용 시 cat1, cat2 필요")
        if lcls2 is not None:
            _require(lcls1 is not None, "lclsSystm2 사용 시 lclsSystm1 필요")
        if lcls3 is not None:
            _require(lcls1 is not None and lcls2 is not None, "lclsSystm3 사용 시 lclsSystm1, lclsSystm2 필요")

        p: Dict[str, Any] = {
            "mapX": map_x, "mapY": map_y, "radius": radius
        }
        _push(p, "arrange", arrange)
        _push(p, "contentTypeId", content_type_id)
        _push(p, "cat1", cat1); _push(p, "cat2", cat2); _push(p, "cat3", cat3)
        _push(p, "lclsSystm1", lcls1); _push(p, "lclsSystm2", lcls2); _push(p, "lclsSystm3", lcls3)
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/locationBasedList2", p)

    # 5) 키워드 검색
    async def get_search_keyword(
        self,
        keyword: str,
        arrange: Optional[str] = None,
        area_code: Optional[int] = None, sigungu_code: Optional[int] = None,
        cat1: Optional[str] = None, cat2: Optional[str] = None, cat3: Optional[str] = None,
        l_dong_regn_cd: Optional[int] = None, l_dong_signgu_cd: Optional[int] = None,
        lcls1: Optional[str] = None, lcls2: Optional[str] = None, lcls3: Optional[str] = None,
        num_of_rows: Optional[int] = None, page_no: Optional[int] = None,
    ) -> Dict[str, Any]:
        _require(bool(keyword.strip()), "keyword 필수")
        if sigungu_code is not None:
            _require(area_code is not None, "sigunguCode 사용 시 areaCode 필요")
        if cat2 is not None:
            _require(cat1 is not None, "cat2 사용 시 cat1 필요")
        if cat3 is not None:
            _require(cat1 is not None and cat2 is not None, "cat3 사용 시 cat1, cat2 필요")
        if l_dong_signgu_cd is not None:
            _require(l_dong_regn_cd is not None, "lDongSignguCd 사용 시 lDongRegnCd 필요")
        if lcls2 is not None:
            _require(lcls1 is not None, "lclsSystm2 사용 시 lclsSystm1 필요")
        if lcls3 is not None:
            _require(lcls1 is not None and lcls2 is not None, "lclsSystm3 사용 시 lclsSystm1, lclsSystm2 필요")

        p: Dict[str, Any] = {"keyword": keyword}
        _push(p, "arrange", arrange)
        _push(p, "areaCode", area_code); _push(p, "sigunguCode", sigungu_code)
        _push(p, "cat1", cat1); _push(p, "cat2", cat2); _push(p, "cat3", cat3)
        _push(p, "lDongRegnCd", l_dong_regn_cd); _push(p, "lDongSignguCd", l_dong_signgu_cd)
        _push(p, "lclsSystm1", lcls1); _push(p, "lclsSystm2", lcls2); _push(p, "lclsSystm3", lcls3)
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/searchKeyword2", p)

    # 6) 행사정보 조회
    async def get_search_festival(
        self,
        event_start_date: str,  # YYYYMMDD
        event_end_date: Optional[str] = None,
        area_code: Optional[int] = None, sigungu_code: Optional[int] = None,
        cat1: Optional[str] = None, cat2: Optional[str] = None, cat3: Optional[str] = None,
        l_dong_regn_cd: Optional[int] = None, l_dong_signgu_cd: Optional[int] = None,
        lcls1: Optional[str] = None, lcls2: Optional[str] = None, lcls3: Optional[str] = None,
        arrange: Optional[str] = None, num_of_rows: Optional[int] = None, page_no: Optional[int] = None,
    ) -> Dict[str, Any]:
        _require(len(event_start_date) in (8, 14), "eventStartDate 형식 YYYYMMDD 또는 YYYYMMDDHHMMSS")
        if sigungu_code is not None:
            _require(area_code is not None, "sigunguCode 사용 시 areaCode 필요")
        if cat2 is not None:
            _require(cat1 is not None, "cat2 사용 시 cat1 필요")
        if cat3 is not None:
            _require(cat1 is not None and cat2 is not None, "cat3 사용 시 cat1, cat2 필요")
        if l_dong_signgu_cd is not None:
            _require(l_dong_regn_cd is not None, "lDongSignguCd 사용 시 lDongRegnCd 필요")
        if lcls2 is not None:
            _require(lcls1 is not None, "lclsSystm2 사용 시 lclsSystm1 필요")
        if lcls3 is not None:
            _require(lcls1 is not None and lcls2 is not None, "lclsSystm3 사용 시 lclsSystm1, lclsSystm2 필요")

        p: Dict[str, Any] = {"eventStartDate": event_start_date}
        _push(p, "eventEndDate", event_end_date)
        _push(p, "areaCode", area_code); _push(p, "sigunguCode", sigungu_code)
        _push(p, "cat1", cat1); _push(p, "cat2", cat2); _push(p, "cat3", cat3)
        _push(p, "lDongRegnCd", l_dong_regn_cd); _push(p, "lDongSignguCd", l_dong_signgu_cd)
        _push(p, "lclsSystm1", lcls1); _push(p, "lclsSystm2", lcls2); _push(p, "lclsSystm3", lcls3)
        _push(p, "arrange", arrange)
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/searchFestival2", p)

    # 7) 숙박정보 조회
    async def get_search_stay(
        self,
        arrange: Optional[str] = None,
        area_code: Optional[int] = None, sigungu_code: Optional[int] = None,
        cat1: Optional[str] = None, cat2: Optional[str] = None, cat3: Optional[str] = None,
        modified_time: Optional[str] = None,
        l_dong_regn_cd: Optional[int] = None, l_dong_signgu_cd: Optional[int] = None,
        lcls1: Optional[str] = None, lcls2: Optional[str] = None, lcls3: Optional[str] = None,
        num_of_rows: Optional[int] = None, page_no: Optional[int] = None,
    ) -> Dict[str, Any]:
        if sigungu_code is not None:
            _require(area_code is not None, "sigunguCode 사용 시 areaCode 필요")
        if cat2 is not None:
            _require(cat1 is not None, "cat2 사용 시 cat1 필요")
        if cat3 is not None:
            _require(cat1 is not None and cat2 is not None, "cat3 사용 시 cat1, cat2 필요")
        if l_dong_signgu_cd is not None:
            _require(l_dong_regn_cd is not None, "lDongSignguCd 사용 시 lDongRegnCd 필요")
        if lcls2 is not None:
            _require(lcls1 is not None, "lclsSystm2 사용 시 lclsSystm1 필요")
        if lcls3 is not None:
            _require(lcls1 is not None and lcls2 is not None, "lclsSystm3 사용 시 lclsSystm1, lclsSystm2 필요")

        p: Dict[str, Any] = {}
        _push(p, "arrange", arrange)
        _push(p, "areaCode", area_code); _push(p, "sigunguCode", sigungu_code)
        _push(p, "cat1", cat1); _push(p, "cat2", cat2); _push(p, "cat3", cat3)
        _push(p, "modifiedtime", modified_time)
        _push(p, "lDongRegnCd", l_dong_regn_cd); _push(p, "lDongSignguCd", l_dong_signgu_cd)
        _push(p, "lclsSystm1", lcls1); _push(p, "lclsSystm2", lcls2); _push(p, "lclsSystm3", lcls3)
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/searchStay2", p)

    # 8) 공통정보 조회
    async def get_detail_common(self, content_id: int, num_of_rows: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        p: Dict[str, Any] = {"contentId": content_id}
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/detailCommon2", p)

    # 9) 소개정보 조회
    async def get_detail_intro(self, content_id: int, content_type_id: int, num_of_rows: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        p: Dict[str, Any] = {"contentId": content_id, "contentTypeId": content_type_id}
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/detailIntro2", p)

    # 10) 반복정보 조회
    async def get_detail_info(self, content_id: int, content_type_id: int, num_of_rows: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        p: Dict[str, Any] = {"contentId": content_id, "contentTypeId": content_type_id}
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/detailInfo2", p)

    # 11) 이미지정보 조회
    async def get_detail_image(self, content_id: int, image_yn: Optional[str] = None, num_of_rows: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        if image_yn is not None:
            _require(image_yn in ("Y", "N"), "imageYN 값은 Y 또는 N")
        p: Dict[str, Any] = {"contentId": content_id}
        _push(p, "imageYN", image_yn)
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/detailImage2", p)

    # 12) 동기화 목록 조회
    async def get_area_based_sync_list(
        self,
        showflag: Optional[int] = None, modified_time: Optional[str] = None, arrange: Optional[str] = None,
        content_type_id: Optional[int] = None,
        area_code: Optional[int] = None, sigungu_code: Optional[int] = None,
        cat1: Optional[str] = None, cat2: Optional[str] = None, cat3: Optional[str] = None,
        l_dong_regn_cd: Optional[int] = None, l_dong_signgu_cd: Optional[int] = None,
        lcls1: Optional[str] = None, lcls2: Optional[str] = None, lcls3: Optional[str] = None,
        num_of_rows: Optional[int] = None, page_no: Optional[int] = None,
    ) -> Dict[str, Any]:
        if sigungu_code is not None:
            _require(area_code is not None, "sigunguCode 사용 시 areaCode 필요")
        if cat2 is not None:
            _require(cat1 is not None, "cat2 사용 시 cat1 필요")
        if cat3 is not None:
            _require(cat1 is not None and cat2 is not None, "cat3 사용 시 cat1, cat2 필요")
        if l_dong_signgu_cd is not None:
            _require(l_dong_regn_cd is not None, "lDongSignguCd 사용 시 lDongRegnCd 필요")
        if lcls2 is not None:
            _require(lcls1 is not None, "lclsSystm2 사용 시 lclsSystm1 필요")
        if lcls3 is not None:
            _require(lcls1 is not None and lcls2 is not None, "lclsSystm3 사용 시 lclsSystm1, lclsSystm2 필요")

        p: Dict[str, Any] = {}
        _push(p, "showflag", showflag)
        _push(p, "modifiedtime", modified_time)
        _push(p, "arrange", arrange)
        _push(p, "contentTypeId", content_type_id)
        _push(p, "areaCode", area_code); _push(p, "sigunguCode", sigungu_code)
        _push(p, "cat1", cat1); _push(p, "cat2", cat2); _push(p, "cat3", cat3)
        _push(p, "lDongRegnCd", l_dong_regn_cd); _push(p, "lDongSignguCd", l_dong_signgu_cd)
        _push(p, "lclsSystm1", lcls1); _push(p, "lclsSystm2", lcls2); _push(p, "lclsSystm3", lcls3)
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/areaBasedSyncList2", p)

    # 13) 반려동물 동반여행 정보 조회
    async def get_detail_pet_tour(self, content_id: int, num_of_rows: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        p: Dict[str, Any] = {"contentId": content_id}
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/detailPetTour2", p)

    # 14) 법정동 코드 조회
    async def get_ldong_code(self, l_dong_regn_cd: Optional[int] = None, l_dong_list_yn: Optional[str] = None, num_of_rows: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        if l_dong_list_yn is not None:
            _require(l_dong_list_yn in ("Y", "N"), "lDongListYn 값은 Y 또는 N")
        p: Dict[str, Any] = {}
        _push(p, "lDongRegnCd", l_dong_regn_cd)
        _push(p, "lDongListYn", l_dong_list_yn)
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/ldongCode2", p)

    # 15) 분류체계 코드 조회
    async def get_lcls_system_code(self, lcls1: Optional[str] = None, lcls2: Optional[str] = None, lcls3: Optional[str] = None, num_of_rows: Optional[int] = None, page_no: Optional[int] = None) -> Dict[str, Any]:
        if lcls2 is not None:
            _require(lcls1 is not None, "lclsSystm2 사용 시 lclsSystm1 필요")
        if lcls3 is not None:
            _require(lcls1 is not None and lcls2 is not None, "lclsSystm3 사용 시 lclsSystm1, lclsSystm2 필요")
        p: Dict[str, Any] = {}
        _push(p, "lclsSystm1", lcls1); _push(p, "lclsSystm2", lcls2); _push(p, "lclsSystm3", lcls3)
        _push(p, "numOfRows", num_of_rows); _push(p, "pageNo", page_no)
        return await self._get("/lclsSystmCode2", p)
