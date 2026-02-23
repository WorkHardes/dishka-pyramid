from dishka import Provider, Scope, provide
from pyramid.request import Request
from pyramid.response import Response

from dishka_pyramid import FromDishka, inject


class UsersRepository:
    def retrieve_one(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Ivan", "language": "ru"}

    def update_language(self, user_id: int, language: str) -> dict:
        return {"id": user_id, "name": "Ivan", "language": language}


class GetUserInteractor:
    def __init__(self, users_repo: UsersRepository) -> None:
        self.users_repo = users_repo

    def execute(self, user_id: int) -> dict:
        return self.users_repo.retrieve_one(user_id)


class UpdateUserLanguageInteractor:
    def __init__(self, users_repo: UsersRepository) -> None:
        self.users_repo = users_repo

    def execute(self, user_id: int, language: str) -> dict:
        return self.users_repo.update_language(user_id, language)


class MockProvider(Provider):
    @provide(scope=Scope.APP)
    def users_repository(self) -> UsersRepository:
        return UsersRepository()

    @provide(scope=Scope.REQUEST)
    def get_user_interactor(self, users: UsersRepository) -> GetUserInteractor:
        return GetUserInteractor(users)

    @provide(scope=Scope.REQUEST)
    def update_user_language_interactor(
        self,
        users: UsersRepository,
    ) -> UpdateUserLanguageInteractor:
        return UpdateUserLanguageInteractor(users)


@inject
def get_user_view(
    request: Request,
    interactor: FromDishka[GetUserInteractor],
) -> Response:
    user = interactor.execute(user_id=1)
    return Response(json_body=user)


@inject
def update_user_language_view(
    request: Request,
    interactor: FromDishka[UpdateUserLanguageInteractor],
) -> Response:
    user = interactor.execute(user_id=1, language="ru")
    return Response(json_body=user)


@inject
def both_interactors_view(
    request: Request,
    get_user: FromDishka[GetUserInteractor],
    set_language: FromDishka[UpdateUserLanguageInteractor],
) -> Response:
    assert get_user.users_repo is set_language.users_repo
    return Response("ok")
