import uuid

from mypage.model.mypage import PlanItemDetailResponse, PlanDetailResponse, MyPlansResponse
from mypage.repository import mypage as repository


def get_plans(user_id: uuid.UUID):
    rows = repository.get_plans(user_id)

    plan = []
    for row in rows:
        plan.append(
            PlanItemDetailResponse(
                todo = row[-3],
                place = row[-2],
                time = row[-1]
            )
        )

    return MyPlansResponse(
        plan_id = rows[0][0],
        plan = PlanDetailResponse(
            start_time = rows[0][1],
            end_time = rows[0][2],
            plan = plan
        )
    )


def get_bookmark_place(user_id: uuid.UUID):
    return repository.get_bookmark_place(user_id)


def get_like_boards(user_id: uuid.UUID):
    return repository.get_like_boards(user_id)