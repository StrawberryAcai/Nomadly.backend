from __future__ import annotations

class UserFacingError(Exception):
    def __init__(self, message: str, *, raw=None) -> None:
        super().__init__(message)
        self.raw = raw

def map_error(e: Exception) -> UserFacingError:
    s = str(e)
    if "cat2" in s and "cat1" in s:
        return UserFacingError("cat2를 쓰려면 cat1이 필요합니다.")
    if "cat3" in s and ("cat1" in s or "cat2" in s):
        return UserFacingError("cat3를 쓰려면 cat1, cat2가 모두 필요합니다.")
    if "sigunguCode" in s and "areaCode" in s:
        return UserFacingError("sigunguCode를 쓰려면 areaCode가 필요합니다.")
    if "radius" in s:
        return UserFacingError("radius는 1~20000 범위여야 합니다.")
    return UserFacingError("요청 파라미터를 확인하세요.")
