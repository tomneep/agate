import requests
from typing  import List

from varys import Varys


class AgateDomain:
    domain: str
    token: str

    def __init__(
        self,
        domain: str,
        token: str
    ):
        self.domain = domain
        self.token = token


class IngestionReader:
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

    def update(self, varys_client: Varys, agate_domain: AgateDomain) -> None:
        s3_messages = varys_client.receive_batch(exchange="inbound-s3", queue_suffix="agate", timeout=1)

        for m in s3_messages:
            try:
                # something
                varys_client.acknowledge_message(m)
            except Exception:
                varys_client.nack_message(m)
                raise

        matched_messages = varys_client.receive_batch(exchange="inbound-matched", queue_suffix="agate", timeout=1)

        for m in matched_messages:
            try:
                self._update_lists(m)
                # something
                varys_client.acknowledge_message(m)
            except Exception:
                varys_client.nack_message(m)
                raise

        for project in self.projects:
            to_validate_messages = varys_client.receive_batch(
                exchange=f"inbound-to_validate-{project}", queue_suffix="agate", timeout=1)
            for m in to_validate_messages:
                try:
                    # something
                    varys_client.acknowledge_message(m)
                except Exception:
                    varys_client.nack_message(m)
                    raise

        for project_site in self.project_sites:
            results_messages = varys_client.receive_batch(
                exchange=f"inbound-results-{project_site}", queue_suffix="agate", timeout=1)
            for m in results_messages:
                try:
                    # something
                    varys_client.acknowledge_message(m)
                except Exception:
                    varys_client.nack_message(m)
                    raise

    def _post(self, agate_domain: AgateDomain, data: dict) -> bool:

        r = requests.post(f"{agate_domain.domain}/update/", data=data,
                          headers={"Authorization": f"Token {agate_domain.token}"})

        return r.status_code == 201

    def _report(self, agate_domain: AgateDomain, message: str, status: str = 'SU') -> bool:
        data = dict(uuid='gg', project='mscape', site='bham', status=status, platform='K')
        return self._post(agate_domain, data)

    def _update_lists(self, message: str):
        project: str = 'mscape'
        project_site: str = 'mscape-bham'
        if project not in self.projects:
            self.projects.append(project)
        if project_site not in self.project_sites:
            self.project_sites.append(project_site)
