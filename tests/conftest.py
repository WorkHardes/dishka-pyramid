import pytest
from dishka import make_container
from pyramid.config import Configurator
from webtest import TestApp

from dishka_pyramid import PyramidProvider, setup_dishka
from tests.common import (
    MockProvider,
    both_interactors_view,
    get_user_view,
    update_user_language_view,
)


@pytest.fixture
def app() -> TestApp:
    container = make_container(PyramidProvider(), MockProvider())
    config = Configurator()
    setup_dishka(container, config)

    config.add_route("get_user", "/get_user")
    config.add_view(get_user_view, route_name="get_user")

    config.add_route("update_user_language", "/update_user_language")
    config.add_view(update_user_language_view, route_name="update_user_language")

    config.add_route("both", "/both")
    config.add_view(both_interactors_view, route_name="both")

    return TestApp(config.make_wsgi_app())
