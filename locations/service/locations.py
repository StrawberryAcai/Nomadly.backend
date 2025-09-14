from tourapi.client import TourAPIClient
from haversine import haversine
from locations.repository.place import PlaceRepository
import os

async def recommend(typeId: int, longitude: float, latitude: float):
    """
    특정 위치를 기준으로 추천 장소를 반환합니다.

    Args:
        typeId (int): 콘텐츠 유형 ID
        longitude (float): 사용자의 경도
        latitude (float): 사용자의 위도

    Returns:
        list: 추천 장소 목록
    """
    # 사용자가 반경으로 얼마나 멀리까지 정보를 찾을지 뜻합니다
    max_distance = 10000

    # TourAPI 클라이언트 초기화
    tourapi_key = os.environ.get("TOURAPI_KEY")
    if not tourapi_key:
        raise ValueError("TOURAPI_KEY 환경 변수가 설정되지 않았습니다.")
    client = TourAPIClient(tourapi_key)

    # PlaceRepository 초기화
    place_repo = PlaceRepository()

    res = []
    items = await client.get_location_based_list(
        arrange='Q',
        content_type_id=typeId,
        map_x=longitude,
        map_y=latitude,
        radius=max_distance
    )
    items = items['response']['body']['items']['item']

    for item in items:
        if not item.get('firstimage'):  # 이미지가 없는 항목은 제외
            continue

        origin = (latitude, longitude)
        destination = (item['mapy'], item['mapx'])

        # 장소 이름으로 DB에서 정보 가져오기
        place_info = place_repo.get_place_by_name(item['title'])
        if place_info:
            rating = place_info.get('overall_rating', 0)
            bookmark_cnt = place_info.get('overall_bookmark', 0)

            # 트렌드 계산: 최근 북마크 수가 일정 기준 이상이면 트렌드로 간주
            trend = bookmark_cnt > 100  # 예: 북마크 수가 100 이상이면 트렌드
        else:
            # DB에 없는 경우 기본값 설정
            rating = 4.9
            bookmark_cnt = 0
            trend = False

        res.append({
            "place_name": item['title'],
            "rating": rating,
            "trend": trend,
            "bookmark_cnt": bookmark_cnt,
            "distance": haversine(origin, destination, unit='m'),
            "image": item['firstimage'],
        })

    return res