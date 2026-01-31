from collections.abc import Callable

import aiohttp.web
import punq


class _Sentinel:
    __slots__ = ()


_sentinel = _Sentinel()


class Container:
    __slots__ = (
        "__container",
        "__registered_services",
    )

    def __init__(self) -> None:
        self.__container = punq.Container()
        self.__registered_services: set[type] = set()

    def is_registered[TService](self, service: type[TService]) -> bool:
        return service in self.__registered_services

    def get_registered_services(self) -> list[type]:
        return list(self.__registered_services)

    def register[TService](
        self,
        service: type[TService],
        *,
        instance: TService | _Sentinel = _sentinel,
        factory: Callable[[], TService] | _Sentinel = _sentinel,
        impl: type[TService] | _Sentinel = _sentinel,
    ) -> None:
        if not isinstance(instance, _Sentinel):
            self.__container.register(service, instance=instance, scope=punq.Scope.singleton)
        elif not isinstance(factory, _Sentinel):
            self.__container.register(service, factory=factory, scope=punq.Scope.singleton)
        elif not isinstance(impl, _Sentinel):
            self.__container.register(service, factory=impl, scope=punq.Scope.singleton)
        else:
            self.__container.register(service, factory=service, scope=punq.Scope.singleton)
        self.__registered_services.add(service)

    def resolve[TService](self, service: type[TService]) -> TService:
        return self.__container.resolve(service)

    def resolve_all[TService](self, service: type[TService]) -> list[TService]:
        return self.__container.resolve_all(service)

    def create[TService](self, service: type[TService]) -> TService:
        return self.__container.instantiate(service)


def set_container(app: aiohttp.web.Application, container: Container) -> None:
    app["container"] = container


def get_container(app: aiohttp.web.Application) -> Container:
    return app["container"]
