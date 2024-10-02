import json
import logging
from typing import List
from .models import IngestionAttempt
from .forms import IngestionAttemptForm

from varys import Varys

logger = logging.getLogger(__name__)


class QueueReader:
    ""
    projects: List[str] = []
    project_sites: List[str] = []

    def __init__(
        self,
        projects: List[str] = [],
        project_sites: List[str] = []
    ):
        self.projects = projects
        self.project_sites = project_sites

    def update(self, varys_client: Varys) -> None:
        s3_messages = varys_client.receive_batch(exchange="inbound-s3", queue_suffix="agate", timeout=1)

        for m in s3_messages:
            try:
                self._update_item_from_message(m, "s3")
                varys_client.acknowledge_message(m)
            except Exception:
                varys_client.nack_message(m)
                raise

        matched_messages = varys_client.receive_batch(exchange="inbound-matched", queue_suffix="agate", timeout=1)
        for m in matched_messages:
            try:
                self._update_lists(m)
                self._update_item_from_message(m, "matched")
                varys_client.acknowledge_message(m)
            except Exception:
                varys_client.nack_message(m)
                raise

        for project in self.projects:
            to_validate_messages = varys_client.receive_batch(
                exchange=f"inbound-to_validate-{project}", queue_suffix="agate", timeout=1)
            for m in to_validate_messages:
                try:
                    self._update_item_from_message(m, "to_validate")
                    varys_client.acknowledge_message(m)
                except Exception:
                    varys_client.nack_message(m)
                    raise

        for project_site in self.project_sites:
            results_messages = varys_client.receive_batch(
                exchange=f"inbound-results-{project_site}", queue_suffix="agate", timeout=1)
            for m in results_messages:
                try:
                    self._update_item_from_message(m, "inbound_results")
                    varys_client.acknowledge_message(m)
                except Exception:
                    varys_client.nack_message(m)
                    raise
        logger.info("checking")

    def _update_item_from_message(self, message: str, stage: str):
        try:
            data = json.loads(message.body)
        except json.decoder.JSONDecodeError:
            logger.fatal(f"{stage}: not a valid json message: {message.body}")
            return
        try:
            uuid = data["uuid"]
        except KeyError:
            logger.fatal("no uuid")
            return
        status = 'SU'
        data["status"] = status
        return self._update_item(uuid, data)

    def _update_item(self, uuid: str, data: dict):
        try:
            instance = IngestionAttempt.objects.get(uuid=uuid)
            form = IngestionAttemptForm(data, instance=instance)
        except IngestionAttempt.DoesNotExist:
            # IngestionAttempt doesn't exists, so we create a new one
            form = IngestionAttemptForm(data)
        if form.is_valid():
            form.save()
        else:
            logger.fatal(f"invalid ingestion attempt message: {form.errors}")

    def _update_lists(self, message: str):
        try:
            data = json.loads(message.body)
            project: str = data["project"]
            site: str = data["site"]
            project_site: str = f"{project}-{site}"
            if project not in self.projects:
                self.projects.append(project)
            if project_site not in self.project_sites:
                self.project_sites.append(project_site)
        except Exception:
            pass
