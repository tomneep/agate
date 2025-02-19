# Agate

This project is a Django-based web api which records and presents data referring to attempts to ingest data into the climb-TRE system.

This is to offer near-real-time monitoring and feedback on the success or failure of such attempts.

### Ingestion attempts

The major item stored is the `IngestionAttempt`.

These record to attempts by a user to ingest data into the climb-TRE system and are the principle items maintained and recoded by the system.

see `models.py`.

### API calls

The api calls available are

+ Querying the profile associated with an authentication token.
+ Querying the projects permitted with an authentication token.
+ Querying the ingestion attempts of a single project, giving paginated results.
+ Querying the details of a single ingestion attempt.
+ Flagging a single ingestion attempt as archived.
+ Prompting the deletion of a single ingestion attempt.
+ Setting the fields (including the status) of a single ingestion attempt.

A homepage is also offered. It gives no useful functionality but can be used to test if the site is up.

See `urs.py` and `views.py`.


### Authentication

Authentication is achieved by requiring an authorization token in the headers of requests.
This api includes no independent system of users, instead it delegates authentication to an external system, Onyx.

The Authorization token provided is forwarded to the onyx API, whose address is hard coded in the agate settings file.

The location to authorize against is stored as a local setting named `ONYX_DOMAIN`.

Onyx will reply with the permissions associated with the token, and agate gives these exact same permissions.

See `authorisation.py`.

#### Authentication caching

To reduce the demands on the Onyx api, the permissions of the token are cached in a `TokenCache` item for an hour.

See `caching.py`

### Queue Reading

The usual method of populating ingestion attempts is to monitor the messages sent to a RabbitMQ queue.

We abstract away the queues and the acquisition of the messages by defining a `MessageRetrievalProtocol` which defines, but does not implement methods to query messages, acknowledge messages and nack messages.
The exact message retrieval is defined in the local setting file, as `MESSAGE_RETRIEVAL`.


Messages are sought and interpreted by a QueueReader class, which retrieves messages using an injected `MessageRetrievalProtocol`; it then  delegates the creation and update of IngestionAttempt records to the `IngestionUpdater` class.

The Queue reader knows which queues to search.

+ inbound-matched
+ inbound-to_validate-{project}
+ inbound-results-{project}-{site}

The inbound-matched queue is agnostic to projects and sites, so it is always monitored.
Messages on the inbound-matched queue are used to learn about new projects and sites, and record them in tracking models.
The detected projects and sites are thereafter used to monitor queues which need this information.

The `IngestionUpdater` uses the content of the message, along with its source queue to appropriately update records.
It has the job of allocating a name to the ingestion attempt which is still under contention.

See `message_retrieval_protocol.py`, `ingestion_updater.py`, and `queue_reader.py`.

#### Filtering queue reading by project

There is the option to ignore some messages received based on their project.
If the local setting `LIMITED_PROJECT_LIST` is not None, and is instead a list of strings, then only messages with those projects will be interpreted.

#### Varys message retrieval

The expected Message Retrieval will be one based on RabbitMQ queues queried by Varys. This is defined by the class `VarysMessageRetrieval`. Usage is not a hard coded certainty however, and is instead determined by the local setting `MESSAGE_RETRIEVAL`.

See `varys_message_retrieval.py`

### Scheduled jobs

`apscheduler` is used to invoke some functionality periodically. 
These involve
+ Clearing out of date `TokenCache` objects from the local database.
+ Using the queue_reader to retrieve new messages which would prompt updates to the ingestion attempts. 


See `scheduled_tasks.py` for the tasks, and `apps.py` for their invocation.

## Unit tests

There is a some test coverage on the queue reading functionality using a mock message retrieval. 

## Other assets

### Phonyx

Also included in this repository is a very simple project called phOnyx short for phony onyx. This is a one-file FastAPI which can used as a substitute for onyx as a authentication server. It currently uses hard coded name, site and project. The sole authorized token is determined from an environment variable called TOKEN.

### Docker compose

There is a docker-compose file which can be used to test agate locally. Upon running the docker compose, it creates containers for:

+ A rabbitMQ server (whose messages will be monitored by agate)
+ An instance of phonyx (which will be used to authenticate agate)
+ A postgres server (into which agate will store ingestion attempts and metadata)
+ An agate server, visible on port 8001

Running this docker compose file is a method to get an agate instance accessible without connecting to the real Onyx or remote rabbitMQ queues

### Github workflow

There are github work flows to invoke accessibility tests, flake8 tests and run the django unit tests