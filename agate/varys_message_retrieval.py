from typing import Any, List
from agate.i_message_retrieval import iMessageRetrieval
from varys import Varys


class VarysMessageRetrieval(iMessageRetrieval):
    """
    A message retriever based on the Varys-RabbitMQ workflow
    """

    def __init__(self,
                 queue_suffix: str, 
                 timeout: float,
                 config_path: str,
                 profile: str,
                 logfile: str = "varys.log",
                 log_level: str = "DEBUG",
                 auto_acknowledge: bool = False):

        open(logfile, 'w').close()

        self._queue_suffix: str = queue_suffix
        self._timeout: float = timeout

        self._varys = Varys(
            config_path=config_path,
            profile=profile,
            logfile=logfile,
            log_level=log_level,
            auto_acknowledge=auto_acknowledge,
        )

    def receive_batch(self, exchange: str) -> List[Any]:
        return self._varys.receive_batch(exchange, self._queue_suffix, self._timeout)

    def acknowledge_message(self, message: Any) -> None:
        return self._varys.acknowledge_message(message)

    def nack_message(self, message: Any) -> None:
        return self._varys.nack_message(message)
