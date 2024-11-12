from .tracking_models import Project, ProjectSite
import json
import logging
from agate.queue_reading.ingestion_updater import IngestionUpdater
from agate.i_message_retrieval import iMessageRetrieval

logger = logging.getLogger(__name__)


class QueueReader:
    """
    Class to retrieve appropriate messages from the rabbitMQ queues.

    The queue interactions are delegated to an injected service.
    This class is responsible for reading the correctly named queues.

    It monitors 3 queue families, inbound-matched, inbound-to_validate-{project} and inbound-results-{project}-{site}

    It learns about new projects and sites by monitoring the inbound-matched queue.

    It delegates the actual interpretation of the message to the IngestionUpdater class
    """
    def __init__(self, message_retrieval: iMessageRetrieval):
        self._message_retrieval = message_retrieval

    def update(self) -> None:
        """
        This method reads the queues for new messages and interprets the information
        """

        # self._receive(exchange="inbound-s3", update_lists=False, exchange_key="inbound-s3")

        self._receive(exchange="inbound-matched", update_lists=True, exchange_key="inbound-matched")

        for project in Project.objects.all():
            self._receive(
                exchange=f"inbound-to_validate-{project.key}",
                update_lists=False,
                exchange_key="inbound-to-validate")

        for project_site in ProjectSite.objects.all():
            self._receive(
                exchange=f"inbound-results-{project_site.key}",
                update_lists=False,
                exchange_key="inbound-results")

    def _receive(self, exchange: str, update_lists: bool, exchange_key: str):
        messages = self._message_retrieval.receive_batch(exchange=exchange)

        for m in messages:
            try:
                self._update_item_from_message(m, exchange_key)
                if update_lists:
                    self._update_lists(m)
            finally:
                self._message_retrieval.acknowledge_message(m)

    def _update_item_from_message(self, message, stage: str):
        """
        Interprets the message body as a dictionary
        Delegates interpretation of the dictionary
        """

        try:
            data = json.loads(message.body)
        except json.decoder.JSONDecodeError:
            logger.critical(f"{stage}: not a valid json message: {message.body}")
            return

        if "uuid" in data:
            # This message prompts updates to an injection attempt
            IngestionUpdater.update(data, stage)
        else:
            logger.warning(f"{stage}: message did not refer to a uuid: {message.body}")

    def _update_lists(self, message):
        """
        This updates the records of projects and sites to monitor
        If the message refers to projects or sites we don't yet know about, then we add them
        """
        try:
            data = json.loads(message.body)
            project: str = data["project"]
            site: str = data["site"]
            project_site: str = f"{project}-{site}"
            Project.objects.get_or_create(key=project)
            ProjectSite.objects.get_or_create(key=project_site)
        except Exception as ex:
            logger.warning(f"Error during site/project update: {ex}")
            # non-crucial, proceed with the exiting sites/projects
            pass
