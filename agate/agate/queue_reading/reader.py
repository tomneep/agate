from .tracking_models import Project, ProjectSite
import json
import logging
from agate.models import IngestionAttempt
from agate.forms import IngestionAttemptForm

from varys import Varys

logger = logging.getLogger(__name__)


class QueueReader:

    def update(self, varys_client: Varys) -> None:

        self._receive(varys_client, exchange="inbound-s3", update_lists=False, exchange_key="inbound-s3")

        self._receive(varys_client, exchange="inbound-matched", update_lists=True, exchange_key="inbound-matched")

        for project in Project.objects.all():
            self._receive(
                varys_client,
                exchange=f"inbound-to_validate-{project.key}",
                update_lists=False,
                exchange_key="to-validate")

        for project_site in ProjectSite.objects.all():
            self._receive(
                varys_client,
                exchange=f"inbound-results-{project_site.key}",
                update_lists=False,
                exchange_key="inbound-results")

    def _receive(self, varys_client: Varys, exchange: str, update_lists: bool, exchange_key: str):
        messages = varys_client.receive_batch(exchange=exchange, queue_suffix="agate", timeout=1)

        for m in messages:
            try:
                self._update_item_from_message(m, exchange_key)
                if update_lists:
                    self._update_lists(m)
                varys_client.acknowledge_message(m)
            except Exception:
                varys_client.nack_message(m)
                raise

    def _status(self, data: dict, stage: str):
        match stage:
            case "inbound-s3":
                return IngestionAttempt.Status.UNSTARTED
            case 'inbound-matched':
                return IngestionAttempt.Status.METADATA
            case 'to-validate':
                return IngestionAttempt.Status.VALIDATION
            case 'inbound-results':
                # checks dict for failures here
                return IngestionAttempt.Status.SUCCESS
            case _:
                return IngestionAttempt.Status.UNSTARTED

    def _update_item_from_message(self, message, stage: str):
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
        data["status"] = self._status(data, stage)
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

    def _update_lists(self, message):
        try:
            data = json.loads(message.body)
            project: str = data["project"]
            site: str = data["site"]
            project_site: str = f"{project}-{site}"
            Project.objects.get_or_create(key=project)
            ProjectSite.objects.get_or_create(key=project_site)
        except Exception:
            pass
