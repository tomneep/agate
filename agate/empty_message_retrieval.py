from typing import Any, List
from agate.message_retrieval_protocol import MessageRetrievalProtocol


class EmptyMessageRetrieval(MessageRetrievalProtocol):
    """
    A dummy message retriever which never receives any messages
    """

    def receive_batch(self, exchange: str) -> List[Any]:
        return []

    def acknowledge_message(self, message: Any) -> None:
        pass

    def nack_message(self, message: Any) -> None:
        pass
