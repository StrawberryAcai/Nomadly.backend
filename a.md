# Locations API 명세서

- Base URL: https://{host}
- Content-Type: application/json
- 인증
  - 평점/북마크 쓰기 API는 Bearer 토큰 필요: Authorization: Bearer {access_token}
  - 토큰의 user_id와 요청의 user_id가 일치해야 함(불일치 시 403)

---

## POST /api/locations

### Description
사용자 위치를 기준으로 반경 10km 내의 장소를 추천합니다.

### Note
이 API 내부적으로 TourAPI의 [위치기반 관광정보 조회(locationBasedList2)]를 사용합니다.  
따라서 type은 TourAPI의 contentTypeId 사전 정의를 따라야 합니다.

목록은 다음과 같습니다 (2025-05-12 기준):
- 관광지
- 문화시설
- 축제공연행사
- 여행코스
- 레포츠
- 숙박
- 쇼핑
- 음식점

~~만약 contentTypeId 이외의 것을 type으로 요청할 경우 AI가 자율적으로 결정합니다~~  
→ 유효하지 않은 type이면 400 에러를 반환합니다.

### Request

| Name   | Type   | Required | Description                               |
| ------ | ------ | -------- | ----------------------------------------- |
| type   | str    | O        | 추천 주제. 위 ‘Note’에 기재된 타입 중 하나 |
| origin | object | O        | 현재 좌표 객체                             |
| └ longitude | number | O  | 경도                                      |
| └ latitude  | number | O  | 위도                                      |

예시
```json
{
  "type": "관광지",
  "origin": { "longitude": 126.9780, "latitude": 37.5665 }
}
```

### Response

| Name         | Type  | Required | Description                       |
| ------------ | ----- | -------- | --------------------------------- |
| type         | str   | O        | 요청 시 사용된 타입                |
| items        | list  | O        | 장소 객체 리스트                   |
| └ place_id   | UUID  | O        | 장소 식별자                        |
| └ place_name | str   | O        | 장소 이름                          |
| └ rating     | number| O        | 평점(0~5)                          |
| └ trend      | bool  | O        | 방문객 증가 여부                   |
| └ bookmark_cnt | int | O        | 북마크 수                          |
| └ distance   | int   | O        | 현재 위치로부터 거리(m 단위)        |
| └ address    | str   | O        | 주소                               |
| └ image      | str   | O        | 대표 이미지 URL                    |

예시
```json
{
  "type": "관광지",
  "items": [
    {
      "place_id": "123e4567-e89b-12d3-a456-426614174000",
      "place_name": "해운대 해수욕장",
      "rating": 4.9,
      "trend": true,
      "bookmark_cnt": 176000,
      "distance": 3100,
      "address": "부산광역시 해운대구 ...",
      "image": "https://example.com/example.jpg"
    }
  ]
}
```

---

## GET /api/locations/place/{place_name}

### Description
이름으로 장소를 조회합니다. 존재하지 않으면 외부 데이터(Kakao Local)를 이용해 최소 정보로 생성 후 반환합니다.  
이미지가 없으면 TourAPI 검색으로 대표 이미지를 보조 조회합니다.

### Note
- Kakao Local REST API를 사용해 장소 기본정보/좌표를 조회합니다.
- 이미지가 비어있으면 TourAPI [키워드 검색(searchKeyword2)]로 firstimage를 시도합니다.
- 인증 불필요.

### Request

Path
- place_name: string (따옴표 제거/제어문자 필터링 처리됨)

Query
- longitude: number? 현재 위치 경도
- latitude: number? 현재 위치 위도

예시
```
GET /api/locations/place/스타벅스%20강남점?longitude=127.0276&latitude=37.4979
```

### Response

| Name         | Type  | Required | Description                |
| ------------ | ----- | -------- | -------------------------- |
| place_id     | UUID  | O        | 장소 식별자                 |
| place_name   | str   | O        | 장소 이름                   |
| rating       | number| O        | 평점(0~5)                   |
| trend        | bool  | O        | 방문객 증가 여부            |
| bookmark_cnt | int   | O        | 북마크 수                   |
| distance     | int   | O        | 현재 위치 기준 거리(m)       |
| address      | str   | O        | 주소                        |
| image        | str   | O        | 대표 이미지 URL             |

예시
```json
{
  "place_id": "123e4567-e89b-12d3-a456-426614174000",
  "place_name": "스타벅스 강남점",
  "rating": 4.5,
  "trend": false,
  "bookmark_cnt": 10,
  "distance": 240,
  "address": "서울특별시 강남구 테헤란로 ...",
  "image": "https://example.com/image.jpg"
}
```

오류
- 400: 유효하지 않은 장소 이름
- 404: 외부 데이터 없음
- 500: 내부 처리 오류

---

## GET /api/locations/rating/{place_id}

### Description
장소의 평균 평점과 총 평가 수를 조회합니다.

### Note
- 인증 불필요.
- 데이터가 없으면 평균 0.0, 카운트 0을 반환합니다.

### Request

Path
- place_id: UUID

예시
```
GET /api/locations/rating/11111111-1111-1111-1111-111111111111
```

### Response

| Name           | Type | Required | Description     |
| -------------- | ---- | -------- | --------------- |
| place_id       | UUID | O        | 장소 식별자      |
| average_rating | number | O      | 평균 평점(소수1자리) |
| total_ratings  | int  | O        | 총 평가 수       |

예시
```json
{
  "place_id": "11111111-1111-1111-1111-111111111111",
  "average_rating": 4.2,
  "total_ratings": 15
}
```

---

## POST /api/locations/rating

### Description
사용자가 장소에 대한 평점을 등록하고, 갱신된 집계 결과를 반환합니다.

### Note
- 인증 필요: Bearer 토큰
- 요청의 user_id는 토큰의 user_id와 일치해야 합니다(불일치 403).

### Request

| Name     | Type  | Required | Description                    |
| -------- | ----- | -------- | ------------------------------ |
| place_id | UUID  | O        | 장소 식별자                     |
| user_id  | UUID  | O        | 평가 사용자(토큰과 일치 필요)    |
| score    | number(0.0~5.0) | O | 평점                          |

예시
```json
{
  "place_id": "11111111-1111-1111-1111-111111111111",
  "user_id": "22222222-2222-2222-2222-222222222222",
  "score": 4.5
}
```

### Response

| Name           | Type   | Required | Description          |
| -------------- | ------ | -------- | -------------------- |
| place_id       | UUID   | O        | 장소 식별자           |
| average_rating | number | O        | 갱신 후 평균 평점      |
| total_ratings  | int    | O        | 총 평가 수            |

오류
- 401: 인증 실패
- 403: 사용자 불일치
- 500: 서버 오류

---

## GET /api/locations/bookmark/{place_id}/{user_id}

### Description
특정 장소에 대한 사용자의 북마크 여부를 조회합니다.

### Note
- 인증 필요: Bearer 토큰
- Path의 user_id는 토큰의 user_id와 일치해야 합니다(불일치 403).

### Request

Path
- place_id: UUID
- user_id: UUID

예시
```
GET /api/locations/bookmark/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb
```

### Response

| Name         | Type | Required | Description       |
| ------------ | ---- | -------- | ----------------- |
| place_id     | UUID | O        | 장소 식별자        |
| user_id      | UUID | O        | 사용자 식별자       |
| is_bookmarked| bool | O        | 북마크 여부         |

오류
- 401: 인증 실패
- 403: 사용자 불일치

---

## POST /api/locations/bookmark

### Description
사용자의 장소 북마크를 추가합니다.

### Note
- 인증 필요: Bearer 토큰
- 요청의 user_id는 토큰의 user_id와 일치해야 합니다(불일치 403).

### Request

| Name     | Type | Required | Description               |
| -------- | ---- | -------- | ------------------------- |
| place_id | UUID | O        | 장소 식별자                |
| user_id  | UUID | O        | 사용자 식별자(토큰과 일치)  |

예시
```json
{
  "place_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "user_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
}
```

### Response

| Name         | Type | Required | Description       |
| ------------ | ---- | -------- | ----------------- |
| place_id     | UUID | O        | 장소 식별자        |
| user_id      | UUID | O        | 사용자 식별자       |
| is_bookmarked| bool | O        | true(추가됨)        |

오류
- 401/403: 인증/사용자 불일치
- 500: 서버 오류

---

## DELETE /api/locations/bookmark

### Description
사용자의 장소 북마크를 삭제합니다.

### Note
- 인증 필요: Bearer 토큰
- 요청의 user_id는 토큰의 user_id와 일치해야 합니다(불일치 403).

### Request

| Name     | Type | Required | Description               |
| -------- | ---- | -------- | ------------------------- |
| place_id | UUID | O        | 장소 식별자                |
| user_id  | UUID | O        | 사용자 식별자(토큰과 일치)  |

예시
```json
{
  "place_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "user_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
}
```

### Response

| Name         | Type | Required | Description         |
| ------------ | ---- | -------- | ------------------- |
| place_id     | UUID | O        | 장소 식별자          |
| user_id      | UUID | O        | 사용자 식별자         |
| is_bookmarked| bool | O        | false(삭제됨)         |

오류
- 401/403: 인증/사용자 불일치
- 500: 서버 오류
