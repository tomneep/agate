from typing import Any, List


class iMessageRetrieval:
    """
    This is the interface for the retrieval and acknowledgement of messages.
    The Varys client is an example of a class which conforms to such an interface.
    It is left as an interface within agate, in order to reduce explicit dependence on Varys.
    """

    def receive_batch(self, exchange: str) -> List[Any]:
        """
        Method to retrieve one or more messages from the provider
        """
        raise NotImplementedError

    def acknowledge_message(self, message: Any) -> None:
        """
        Method to acknowledge that a message has been received, and prevent repeat sends by the provider
        """
        raise NotImplementedError

    def nack_message(self, message: Any) -> None:
        """
        negative acknowlegement of the message, meaning it will be restored to the queue and will reoccur
        """
        raise NotImplementedError
