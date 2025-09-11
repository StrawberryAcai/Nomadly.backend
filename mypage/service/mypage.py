import uuid

from mypage.model.mypage import PlanItemDetailResponse, PlanDetailResponse, MyPlansResponse, MyBookmarkResponse
from mypage.repository import mypage as repository


def get_plans(user_id: uuid.UUID):
    rows = repository.get_plans(user_id)

    return MyPlansResponse(
        plan_id = rows[0][0],
        plan = PlanDetailResponse(
            start_time = rows[0][1],
            end_time = rows[0][2],
            plan = [
                PlanItemDetailResponse(
                    todo = row[-3], place = row[-2], time = row[-1]
                )
                for row in rows
            ]
        )
    )


def get_bookmark_place(user_id: uuid.UUID):
    rows = repository.get_bookmark_place(user_id)
    return [
                MyBookmarkResponse(
                    place_id = row[0], name = row[1], address = row[2]
                    , overall_bookmark = row[3], overall_rating = row[4]
                )
                for row in rows
            ]


def get_like_boards(user_id: uuid.UUID):
    return repository.get_like_boards(user_id)