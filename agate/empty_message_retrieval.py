from typing import Any, List
from agate.i_message_retrieval import iMessageRetrieval


class EmptyMessageRetrieval(iMessageRetrieval):
    """
    A dummy message retriever which never receives any messages
    """

    def receive_batch(self, exchange: str) -> List[Any]:
        return []

    def acknowledge_message(self, message: Any) -> None:
        pass

    def nack_message(self, message: Any) -> None:
        pass
