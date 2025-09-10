from tourapi.client import TourAPIClient
from haversine import haversine
import os

async def recommend(typeId: int, longitude: float, latitude: float):
    # 사용자가 반경으로 얼마나 멀리까지 정보를 찾을지 뜻합니다
    # TODO: 사용자 커스터마이징
    max_distance = 10000

    tourapi_key = os.environ.get("TOURAPI_KEY")
    client = TourAPIClient(tourapi_key)

    res = []
    items = await client.get_location_based_list(arrange='Q', content_type_id=typeId, map_x=longitude, map_y=latitude, radius=max_distance)
    items = items['response']['body']['items']['item']

    for item in items:
        if item['firstimage'] == '':
            continue

        origin = (latitude, longitude)
        destination = (item['mapy'], item['mapx'])

        res.append({
            "place_name": item['title'],
            # TODO: Need to fix this
            "rating": 4.9,
            "trend": True,
            "bookmark_cnt": 10101,
            # ---------------------
            "distance": haversine(origin, destination, unit='m'),
            "image": item['firstimage'],
        })