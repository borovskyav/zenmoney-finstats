from finstats.args import CliArgs
from finstats.daemons import PeriodicDaemon
from finstats.syncer import Syncer


class SyncDiffDaemon(PeriodicDaemon):
    def __init__(self, syncer: Syncer, cli_args: CliArgs) -> None:
        self._syncer = syncer
        self._zm_client_token = cli_args.get_token()
        return

    async def run(self) -> None:
        await self._syncer.sync_once(self._zm_client_token)

    def get_run_period_seconds(self) -> float:
        return 15.0
