# Kubernetes config (work in progress)

> [!CAUTION]
>
> This directory contains a yaml file for starting a RabbitMQ
> server. This is for testing and should not be used in production.


## Running

To deploy `agate` first edit the `config.yaml` and `secrets.yaml` to
include real configuration and settings. Then run

```sh
kubectl apply -f agate.yaml -f postgres.yaml -f config.yaml -f secrets.yaml
```

## Resources

This directory contains the kubernetes config required for running
Agate. The list of kubernetes resources required for Agate to work is as follows.


### Namespace

To try and keep things neat, every resource is placed in the `agate`
namespace.


### Deployments

- `django-app`: The django application. Runs via `gunicorn` on port
  `8000`.
- `django-scheduler`: A scheduled task that performs periodic
  operations such as getting data from the RabbitMQ queues and
  deleting old data from the database.
- `postgres`: A Postgres database that stores ingestion attempts as
  they occur. Attempts are deleted after 28 days.


### Services

- `django-service`: The service making `django-app` available on port
  `8000`.
- `postgres`: The service making the `postgres` deployment available
  on port `5432`.


### ConfigMaps

- `django-config` (`config.yaml`): Configuration for the `django-app`
  (set in django via environment variables). These will likely need to
  be edited for the specific deployment.
- `postgres-config` (`postgres.yaml`): Configuration for `postgres`
  such as database, user and host. Can probably be left alone.


### PersistentVolumeClaim

A single persistent volume claim is made for storing the `postgres`
database. 1Gi is requested but this is probably overkill.


### Secrets

All secrets are defined in `secrets.yaml` and will need to be edited
accordingly. The important settings are:

- `message-config-secret`: Writes `varys_config.cfg` that is used to
  configure the queue readers.
- `message-config-certs`: Contains the certificate files (encoded as
  `base64`) needed to connect to the rabbitMQ queues.
- `django-secret`: The `SECRET_KEY` django setting.
- `postgres-secret`: The `postgres` password.

