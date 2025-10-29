import uuid

from mypage.model.mypage import PlanDetailResponse, MyBookmarkResponse, \
    MyLikeBoardResponse, MyPlansResponse
from mypage.repository import mypage as repository


def get_plans(user_id: uuid.UUID):
    rows = repository.get_plans(user_id)
    print(rows)

    result = []
    for row in rows:
        if uuid.UUID(row[0]) not in result:
            result.append(MyPlansResponse(
                plan_id=uuid.UUID(row[0]),
                start_time=str(row[1]),
                end_time=str(row[2]),
                plan=[PlanDetailResponse(todo=row[3], place=row[4], time=str(row[5]))]
            ))
        elif uuid.UUID(row[0]) in result:
            temp = result.pop(result.index(uuid.UUID(row[0])))
            temp["plan"].append(PlanDetailResponse(todo=row[3], place=row[4], time=str(row[5])))

    return {"plans" : result}


def get_bookmark_place(user_id: uuid.UUID):
    rows = repository.get_bookmark_place(user_id)
    return {
        "plans" : [
                MyBookmarkResponse(
                    place_id = uuid.UUID(row[0]), name = row[1], address = row[2]
                    , overall_bookmark = row[3], overall_rating = row[4]
                )
                for row in rows
        ]
    }


def get_like_boards(user_id: uuid.UUID):
    rows = repository.get_like_boards(user_id)
    return [
        MyLikeBoardResponse(
            board_id = uuid.UUID(row[0]), title = row[1], content = row[2], likes = row[3]
        )
        for row in rows
    ]