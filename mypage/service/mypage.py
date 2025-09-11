from mypage.repository import mypage as repository


def get_plans():
    return repository.get_plans()


def get_bookmark_place():
    return repository.get_bookmark_place()


def get_bookmark_plans():
    return repository.get_bookmark_plans()