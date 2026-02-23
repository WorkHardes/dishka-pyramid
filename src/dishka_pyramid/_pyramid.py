import atexit
from collections.abc import Callable
from typing import Final

from dishka import AsyncContainer, Container, Provider, Scope, from_context
from dishka.integrations.base import wrap_injection
from pyramid.config import Configurator
from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.response import Response

CONTAINER_WRAPPER_NAME: Final[str] = "dishka_container_wrapper"
CONTAINER_NAME: Final[str] = "dishka_container"


class PyramidProvider(Provider):
    """Provider for Pyramid-specific objects.

    Provides:
        - Request: Pyramid request object in REQUEST scope
    """

    request = from_context(provides=Request, scope=Scope.REQUEST)


def inject[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator for automatic dependency injection in Pyramid views.

    Injects dependencies marked with FromDishka[T] annotation into view functions.
    The first parameter must be a Pyramid Request object.

    Args:
        func: Pyramid view callable with signature (Request, ...) -> Response

    Returns:
        Wrapped view function with automatic dependency injection

    Raises:
        TypeError: If first argument is not a Request
        AttributeError: If setup_dishka() was not called

    Example:
        >>> from dishka_pyramid import FromDishka, inject
        >>> @inject
        ... def my_view(request: Request, interactor: FromDishka[MyInteractor]) -> Response:
        ...     me = interactor.execute(request)
        ...     return Response(f"Hello {me.name}")
    """

    def container_getter(args: tuple, _: dict) -> Container:
        request = args[0]
        if not isinstance(request, Request):
            msg = (
                f"Expected Pyramid Request as first argument, got {type(request).__name__}. "
                f"Make sure @inject is used only on Pyramid view callables."
            )
            raise TypeError(msg)

        container = getattr(request, CONTAINER_NAME, None)
        if container is None:
            msg = (
                f"Request missing '{CONTAINER_NAME}' attribute. "
                f"Ensure setup_dishka() was called and middleware is active."
            )
            raise AttributeError(msg)

        return container

    return wrap_injection(
        func=func,
        is_async=False,
        container_getter=container_getter,
    )


def dishka_middleware(
    handler: Callable[[Request], Response],
    registry: Registry,
) -> Callable[[Request], Response]:
    """
    Tween factory for Dishka integration.

    Creates a request-scoped container for each HTTP request and attaches it
    to the request object. The container is automatically cleaned up after
    request processing via context manager.

    Args:
        handler: Next handler in the tween chain
        registry: Pyramid registry containing the application container

    Returns:
        Tween handler function

    Raises:
        RuntimeError: If setup_dishka() was not called before make_wsgi_app()
    """

    try:
        app_container: Container = registry[CONTAINER_WRAPPER_NAME]
    except KeyError as e:
        msg = "Dishka container not found. Did you call setup_dishka()?"
        raise RuntimeError(msg) from e

    def wrapper(request: Request) -> Response:
        with app_container(context={Request: request}) as request_container:
            setattr(request, CONTAINER_NAME, request_container)
            return handler(request)

    return wrapper


def setup_dishka(container: Container, config: Configurator) -> None:
    """
    Set up Dishka integration with Pyramid.

    Registers middleware for dependency injection and configures container
    lifecycle management. Must be called before adding views that use @inject.

    Args:
        container: Dishka container (must be synchronous)
        config: Pyramid Configurator instance

    Raises:
        TypeError: If AsyncContainer is provided instead of synchronous Container

    Example:
        >>> from dishka import make_container
        >>> from dishka_pyramid import setup_dishka
        >>> from pyramid.config import Configurator
        >>>
        >>> container = make_container(MyProvider())
        >>> config = Configurator()
        >>> setup_dishka(container, config)
    """
    if isinstance(container, AsyncContainer):
        msg = "AsyncContainer is not supported with Pyramid. Use Container instead."
        raise TypeError(msg)

    config.registry[CONTAINER_WRAPPER_NAME] = container
    config.add_tween("dishka_pyramid._pyramid.dishka_middleware")

    atexit.register(container.close)
