from __future__ import annotations

from abc import ABC, abstractmethod


class BaseDaemon(ABC):
    @abstractmethod
    async def run(self) -> None:
        pass


class CronDaemon(BaseDaemon, ABC):
    @abstractmethod
    def get_cron_expr(self) -> str:
        pass


class PeriodicDaemon(BaseDaemon, ABC):
    @abstractmethod
    def get_run_period_seconds(self) -> float:
        pass
