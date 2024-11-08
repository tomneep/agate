from typing import Any, List
from agate.i_message_retrieval import iMessageRetrieval
from varys import Varys


class VarysMessageRetrieval(iMessageRetrieval):

    def VarysMessageRetrieval(self,
                              config_path: str = "varys_config.cfg",
                              profile: str = "test",
                              logfile: str = "varys.log",
                              log_level: str = "DEBUG",
                              auto_acknowledge: bool = False):

        open(logfile, 'w').close()

        self._varys = Varys(
            config_path,
            profile,
            logfile,
            log_level,
            auto_acknowledge,
        )

    def receive_batch(self, exchange: str, queue_suffix: str, timeout: float) -> List[Any]:
        return self._varys.receive_batch(exchange, queue_suffix, timeout)

    def acknowledge_message(self, message: Any) -> None:
        return self._varys.acknowledge_message(message)

    def nack_message(self, message: Any) -> None:
        return self._varys.nack_message(message)
