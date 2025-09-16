# 완성 스키마: TourAPIClient 15개 메서드 전부를 LLM 함수호출용 JSON Schema로 정의
# - 메서드 시그니처와 파라미터명을 정확히 맞춤 (snake_case 그대로)
# - 가능한 제약을 스키마에 반영: enum, minimum/maximum, pattern 등
# - 교차 의존성(cat2→cat1, cat3→cat1+cat2 등)은 런타임 검증에 맡기고 description으로 고지
# - OpenAI tools 규격 호환(단일 파일로 import 하여 TOOL_SCHEMAS 사용)

from __future__ import annotations
from typing import Dict, Any, List


def _nullable_str() -> Dict[str, Any]:
    return {"type": "string", "nullable": True}

def _nullable_int() -> Dict[str, Any]:
    return {"type": "integer", "nullable": True}

def _nullable_num() -> Dict[str, Any]:
    return {"type": "number", "nullable": True}


# 1) 지역코드 조회

def tool_schema_get_areacode() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_areacode",
            "description": "지역코드 조회 (KorService2/areaCode2).",
            "parameters": {
                "type": "object",
                "properties": {
                    "area_code": _nullable_int(),
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": [],
            },
        },
    }

# 2) 서비스 분류코드 조회

def tool_schema_get_category_code() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_category_code",
            "description": "서비스 분류코드 조회 (KorService2/categoryCode2). cat2는 cat1 필요, cat3는 cat1+cat2 필요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content_type_id": _nullable_int(),
                    "cat1": _nullable_str(),
                    "cat2": _nullable_str(),
                    "cat3": _nullable_str(),
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": [],
            },
        },
    }

# 3) 지역기반 관광정보 조회

def tool_schema_get_area_based_list() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_area_based_list",
            "description": "지역기반 관광정보 조회 (KorService2/areaBasedList2). sigungu_code는 area_code 필요 등 의존성은 런타임 검증.",
            "parameters": {
                "type": "object",
                "properties": {
                    "arrange": _nullable_str(),
                    "content_type_id": _nullable_int(),
                    "area_code": _nullable_int(),
                    "sigungu_code": _nullable_int(),
                    "cat1": _nullable_str(),
                    "cat2": _nullable_str(),
                    "cat3": _nullable_str(),
                    "modified_time": {"type": "string", "nullable": True, "description": "YYYYMMDD 또는 YYYYMMDDHHMMSS", "pattern": r"^\d{8}(\d{6})?$"},
                    "l_dong_regn_cd": _nullable_int(),
                    "l_dong_signgu_cd": _nullable_int(),
                    "lcls1": _nullable_str(),
                    "lcls2": _nullable_str(),
                    "lcls3": _nullable_str(),
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": [],
            },
        },
    }

# 4) 위치기반 관광정보 조회

def tool_schema_get_location_based_list() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_location_based_list",
            "description": "위치기반 관광정보 조회 (KorService2/locationBasedList2). radius 1~20000.",
            "parameters": {
                "type": "object",
                "properties": {
                    "map_x": {"type": "number"},
                    "map_y": {"type": "number"},
                    "radius": {"type": "integer", "minimum": 1, "maximum": 20000},
                    "arrange": _nullable_str(),
                    "content_type_id": _nullable_int(),
                    "cat1": _nullable_str(),
                    "cat2": _nullable_str(),
                    "cat3": _nullable_str(),
                    "lcls1": _nullable_str(),
                    "lcls2": _nullable_str(),
                    "lcls3": _nullable_str(),
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": ["map_x", "map_y", "radius"],
            },
        },
    }

# 5) 키워드 검색

def tool_schema_get_search_keyword() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_search_keyword",
            "description": "키워드 검색 (KorService2/searchKeyword2). keyword 필수, 기타 의존성은 런타임 검증.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"},
                    "arrange": _nullable_str(),
                    "area_code": _nullable_int(),
                    "sigungu_code": _nullable_int(),
                    "cat1": _nullable_str(),
                    "cat2": _nullable_str(),
                    "cat3": _nullable_str(),
                    "l_dong_regn_cd": _nullable_int(),
                    "l_dong_signgu_cd": _nullable_int(),
                    "lcls1": _nullable_str(),
                    "lcls2": _nullable_str(),
                    "lcls3": _nullable_str(),
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": ["keyword"],
            },
        },
    }

# 6) 행사정보 조회

def tool_schema_get_search_festival() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_search_festival",
            "description": "행사정보 조회 (KorService2/searchFestival2). event_start_date 패턴: YYYYMMDD 또는 YYYYMMDDHHMMSS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_start_date": {"type": "string", "pattern": r"^\d{8}(\d{6})?$"},
                    "event_end_date": {"type": "string", "nullable": True, "pattern": r"^\d{8}(\d{6})?$"},
                    "area_code": _nullable_int(),
                    "sigungu_code": _nullable_int(),
                    "cat1": _nullable_str(),
                    "cat2": _nullable_str(),
                    "cat3": _nullable_str(),
                    "l_dong_regn_cd": _nullable_int(),
                    "l_dong_signgu_cd": _nullable_int(),
                    "lcls1": _nullable_str(),
                    "lcls2": _nullable_str(),
                    "lcls3": _nullable_str(),
                    "arrange": _nullable_str(),
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": ["event_start_date"],
            },
        },
    }

# 7) 숙박정보 조회

def tool_schema_get_search_stay() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_search_stay",
            "description": "숙박정보 조회 (KorService2/searchStay2).",
            "parameters": {
                "type": "object",
                "properties": {
                    "arrange": _nullable_str(),
                    "area_code": _nullable_int(),
                    "sigungu_code": _nullable_int(),
                    "cat1": _nullable_str(),
                    "cat2": _nullable_str(),
                    "cat3": _nullable_str(),
                    "modified_time": {"type": "string", "nullable": True, "pattern": r"^\d{8}(\d{6})?$"},
                    "l_dong_regn_cd": _nullable_int(),
                    "l_dong_signgu_cd": _nullable_int(),
                    "lcls1": _nullable_str(),
                    "lcls2": _nullable_str(),
                    "lcls3": _nullable_str(),
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": [],
            },
        },
    }

# 8) 공통정보 조회

def tool_schema_get_detail_common() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_detail_common",
            "description": "공통 상세 정보 조회 (KorService2/detailCommon2).",
            "parameters": {
                "type": "object",
                "properties": {
                    "content_id": {"type": "integer"},
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": ["content_id"],
            },
        },
    }

# 9) 소개정보 조회

def tool_schema_get_detail_intro() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_detail_intro",
            "description": "소개정보 조회 (KorService2/detailIntro2). content_type_id 필요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content_id": {"type": "integer"},
                    "content_type_id": {"type": "integer"},
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": ["content_id", "content_type_id"],
            },
        },
    }

# 10) 반복정보 조회

def tool_schema_get_detail_info() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_detail_info",
            "description": "반복정보 조회 (KorService2/detailInfo2). content_type_id 필요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content_id": {"type": "integer"},
                    "content_type_id": {"type": "integer"},
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": ["content_id", "content_type_id"],
            },
        },
    }

# 11) 이미지정보 조회

def tool_schema_get_detail_image() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_detail_image",
            "description": "이미지정보 조회 (KorService2/detailImage2). image_yn은 Y/N.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content_id": {"type": "integer"},
                    "image_yn": {"type": "string", "nullable": True, "enum": ["Y", "N"]},
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": ["content_id"],
            },
        },
    }

# 12) 동기화 목록 조회

def tool_schema_get_area_based_sync_list() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_area_based_sync_list",
            "description": "동기화 목록 조회 (KorService2/areaBasedSyncList2).",
            "parameters": {
                "type": "object",
                "properties": {
                    "showflag": _nullable_int(),
                    "modified_time": {"type": "string", "nullable": True, "pattern": r"^\d{8}(\d{6})?$"},
                    "arrange": _nullable_str(),
                    "content_type_id": _nullable_int(),
                    "area_code": _nullable_int(),
                    "sigungu_code": _nullable_int(),
                    "cat1": _nullable_str(),
                    "cat2": _nullable_str(),
                    "cat3": _nullable_str(),
                    "l_dong_regn_cd": _nullable_int(),
                    "l_dong_signgu_cd": _nullable_int(),
                    "lcls1": _nullable_str(),
                    "lcls2": _nullable_str(),
                    "lcls3": _nullable_str(),
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": [],
            },
        },
    }

# 13) 반려동물 동반여행 정보 조회

def tool_schema_get_detail_pet_tour() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_detail_pet_tour",
            "description": "반려동물 동반여행 정보 조회 (KorService2/detailPetTour2).",
            "parameters": {
                "type": "object",
                "properties": {
                    "content_id": {"type": "integer"},
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": ["content_id"],
            },
        },
    }

# 14) 법정동 코드 조회

def tool_schema_get_ldong_code() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_ldong_code",
            "description": "법정동 코드 조회 (KorService2/ldongCode2). l_dong_list_yn은 Y/N.",
            "parameters": {
                "type": "object",
                "properties": {
                    "l_dong_regn_cd": _nullable_int(),
                    "l_dong_list_yn": {"type": "string", "nullable": True, "enum": ["Y", "N"]},
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": [],
            },
        },
    }

# 15) 분류체계 코드 조회

def tool_schema_get_lcls_system_code() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "get_lcls_system_code",
            "description": "분류체계 코드 조회 (KorService2/lclsSystmCode2).",
            "parameters": {
                "type": "object",
                "properties": {
                    "lcls1": _nullable_str(),
                    "lcls2": _nullable_str(),
                    "lcls3": _nullable_str(),
                    "num_of_rows": _nullable_int(),
                    "page_no": _nullable_int(),
                },
                "required": [],
            },
        },
    }


# 일괄 등록
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    tool_schema_get_areacode(),
    tool_schema_get_category_code(),
    tool_schema_get_area_based_list(),
    tool_schema_get_location_based_list(),
    tool_schema_get_search_keyword(),
    tool_schema_get_search_festival(),
    tool_schema_get_search_stay(),
    tool_schema_get_detail_common(),
    tool_schema_get_detail_intro(),
    tool_schema_get_detail_info(),
    tool_schema_get_detail_image(),
    tool_schema_get_area_based_sync_list(),
    tool_schema_get_detail_pet_tour(),
    tool_schema_get_ldong_code(),
    tool_schema_get_lcls_system_code(),
]
