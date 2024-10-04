# Agate - climb TRE ingestion monitoring system

Agate is a system to monitor and report on the status of attempts to ingest date into climb TRE.

Note that this works entirly in terms of ingestion *atempts* and 2 different attempts to ingest the same datafile are totally independent.

In includes a database of ingestion attempts, recoding their UUIDs, each attached to a site and project.

The database will be populated and maintained by monitoring RabbitMQ queues of ROZ which are the source.

There is a landing page, however it serves no information, interactions are expected to be via the api.

It offers an API to retrieve this data so downstream UIs can present it.
The API can also be used to post data and change records, however it is expected that this will not be needed, with most data coming from the queues.



## Agate django project

The database population and urls are hosted by a django project.

There is an django user project however this is not intended for use as user identification.
It is expected there will only need to be a single superuser who can intervene if things go amiss.

### Database content

Each attempt to inject is identified by a unique id given to it by ROZ. 

It is tied to a single project and a single site. These determine who is authorised to see and change the database item.

It has a status to identify which stage of the ingestion process it has reached.

They have booleans to indicate whether they are published and whether they are for test only.

Other options include a user-facing name, a platform, any error messages, and others such as a run id.



### Authorisation

This api does not include any direct users or authorisation, instead tokens sent to agate are passed onto onyx, whose status codes tell us if the
user is authorised to see the records related to a site and project.

### Population from Queues

TODO.


## Testing tools

### Phonyx project

There is an attached project which is not part of the production code, this hosts a mock onyx api to use for local testing without exposure to the production onyx.

### Docker compose

There is a docker-compose file which composes a postgres database, phonyx and agate for swift deployment of a test environment.