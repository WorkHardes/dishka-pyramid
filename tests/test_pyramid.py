from http import HTTPStatus

import pytest
from dishka import make_async_container
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response
from webtest import TestApp

from dishka_pyramid import FromDishka, PyramidProvider, inject, setup_dishka
from tests.common import GetUserInteractor, MockProvider


def test_get_user_interactor_is_injected(app: TestApp) -> None:
    response = app.get("/get_user")
    assert response.status_int == HTTPStatus.OK
    assert response.json["id"] == 1
    assert response.json["name"] == "Ivan"


def test_set_user_language_interactor_is_injected(app: TestApp) -> None:
    response = app.get("/update_user_language")
    assert response.status_int == HTTPStatus.OK
    assert response.json["language"] == "ru"


def test_interactors_share_same_repository_instance(app: TestApp) -> None:
    response = app.get("/both")
    assert response.status_int == HTTPStatus.OK


def test_repository_is_app_scoped_singleton(app: TestApp) -> None:
    app.get("/get_user")
    app.get("/get_user")
    response = app.get("/get_user")
    assert response.json["id"] == 1


def test_setup_dishka_raises_on_async_container() -> None:
    async_container = make_async_container(PyramidProvider(), MockProvider())
    config = Configurator()

    with pytest.raises(TypeError, match="AsyncContainer is not supported"):
        setup_dishka(async_container, config)


def test_inject_raises_without_middleware() -> None:
    @inject
    def bare_view(
        request: Request,
        interactor: FromDishka[GetUserInteractor],
    ) -> Response:
        return Response("ok")

    fake_request = Request.blank("/")

    with pytest.raises(AttributeError, match="dishka_container"):
        bare_view(fake_request)


def test_inject_raises_on_non_request_first_arg() -> None:
    @inject
    def bad_view(
        not_a_request: str,
        interactor: FromDishka[GetUserInteractor],
    ) -> Response:
        return Response("ok")

    with pytest.raises(TypeError, match="Expected Pyramid Request"):
        bad_view("not a request")
