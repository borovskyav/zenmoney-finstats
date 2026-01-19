from finstats.args import CliArgs
from finstats.daemons import PeriodicDaemon
from finstats.syncer import Syncer


class SyncDiffDaemon(PeriodicDaemon):
    __slots__ = (
        "__syncer",
        "__zm_client_token",
    )

    def __init__(self, syncer: Syncer, cli_args: CliArgs) -> None:
        self.__syncer = syncer
        self.__zm_client_token = cli_args.get_token()
        return

    async def run(self) -> None:
        await self.__syncer.sync_once(self.__zm_client_token)

    def get_run_period_seconds(self) -> float:
        return 15.0
