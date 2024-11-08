from typing import Any, List
from agate.i_message_retrieval import iMessageRetrieval


class EmptyMessageRetrieval(iMessageRetrieval):

    def receive_batch(self, exchange: str, queue_suffix: str, timeout: float) -> List[Any]:
        return []

    def acknowledge_message(self, message: Any) -> None:
        pass

    def nack_message(self, message: Any) -> None:
        pass
