import uuid

from mypage.model.mypage import PlanItemDetailResponse, PlanDetailResponse, MyPlansResponse, MyBookmarkResponse, \
    MyLikeBoardResponse
from mypage.repository import mypage as repository


def get_plans(user_id: uuid.UUID):
    rows = repository.get_plans(user_id)

    return MyPlansResponse(
        plan_id = uuid.UUID(rows[0][0]),
        plan = PlanDetailResponse(
            start_time = str(rows[0][1]),
            end_time = str(rows[0][2]),
            plan = [
                PlanItemDetailResponse(
                    todo = row[-3], place = row[-2], time = str(row[-1])
                )
                for row in rows
            ]
        )
    )


def get_bookmark_place(user_id: uuid.UUID):
    rows = repository.get_bookmark_place(user_id)
    return [
                MyBookmarkResponse(
                    place_id = uuid.UUID(row[0]), name = row[1], address = row[2]
                    , overall_bookmark = row[3], overall_rating = row[4]
                )
                for row in rows
            ]


def get_like_boards(user_id: uuid.UUID):
    rows = repository.get_like_boards(user_id)
    return [
        MyLikeBoardResponse(
            board_id = uuid.UUID(row[0]), title = row[1], content = row[2], likes = row[3]
        )
        for row in rows
    ]