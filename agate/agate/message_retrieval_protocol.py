from typing import Any, List
from typing import Protocol
from abc import abstractmethod


class MessageRetrievalProtocol(Protocol):
    """
    This is the interface for the retrieval and acknowledgement of messages.
    The VarysRetrieval is an example which conforms to such an interface.
    It is left as an interface within agate, in order to reduce explicit dependence on Varys.
    """

    @abstractmethod
    def receive_batch(self, exchange: str) -> List[Any]:
        """
        Method to retrieve one or more messages from the provider
        """
        raise NotImplementedError

    @abstractmethod
    def acknowledge_message(self, message: Any) -> None:
        """
        Method to acknowledge that a message has been received, and prevent repeat sends by the provider
        """
        raise NotImplementedError

    @abstractmethod
    def nack_message(self, message: Any) -> None:
        """
        negative acknowlegement of the message, meaning it will be restored to the queue and will reoccur
        """
        raise NotImplementedError
