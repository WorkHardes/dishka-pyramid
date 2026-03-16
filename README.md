# Pyramid integration for Dishka

Dishka DI integration for the [Pyramid](https://trypyramid.com/) framework.

## Installation

via uv:

```shell
uv add dishka-pyramid
```

via pip:

```shell
pip install dishka-pyramid
```

## Usage

Usage example

```python
from typing import Final

from dishka import Provider, Scope, make_container, provide
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from dishka_pyramid import FromDishka, PyramidProvider, inject, setup_dishka


class GetHelloInteractor:
    def execute(self) -> str:
        return "Hello from Dishka!"


class MyProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_hello_interactor(self) -> GetHelloInteractor:
        return GetHelloInteractor()


GET_HELLO_ROUTE_NAME: Final[str] = "hello"


@view_config(route_name=GET_HELLO_ROUTE_NAME)
@inject
def my_view(request: Request, interactor: FromDishka[GetHelloInteractor]) -> Response:
    response_text = interactor.execute()
    return Response(response_text)


container = make_container(PyramidProvider(), MyProvider())

config = Configurator()
setup_dishka(container=container, config=config)

config.add_route(name=GET_HELLO_ROUTE_NAME, pattern="/hello")
config.scan()

app = config.make_wsgi_app()
```
