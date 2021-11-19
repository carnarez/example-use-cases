# Streaming incoming traffic

## Data & infrastructure

The client company [usually seen wearing dark-blue uniforms] has recently installed
cameras on several bridges of a rather crowded highway to capture licence plates of
speeding vehicules. The licence plates are extracted from the pictures and sent to a
`snapshots` feed managed via [`Redis Streams`](https://redis.io/topics/streams-intro).

For this proof of concept, the request from the client is fourfold:

1. Extract the content of the images to plain text for further processing by their
   services.
2. Post a signal to a `flagged` feed (that will eventally be subscribed to by said
   company cars cruising on the same highway to stop and fine those vehicules).
3. Store the extracted licence plates in a relational storage for court hearings.
4. Timing of the whole processing routine to assess the feasibility of a future
   deployment of the stack on the embedded `Kubernetes` micro-clusters running close to
   those sensors.

The backbone of the infrastructure for this setup can be started with:

```bash
$ docker-compose up --build
```

from the root of this directory.

## Extend the startup code

A few services need to be implemented, namely:

* A [fast] OCR service to extract data from the image. For this
  [`Tesseract`](https://github.com/tesseract-ocr/tesseract) or
  [`Apache Tika`](https://tika.apache.org/) could be used (both have wrappers to
  embed them into their own REST API). Depending on the speed of the service, more
  than one might need to be deployed to process the incoming data.
* A database of your choice. An easy choice is of course
  [`PostgreSQL`](https://www.postgresql.org/) that remains easy to interact with. The
  [data model](https://www.sqlalchemy.org/) and database schema are left up to the
  developer. Each record should however contain a timestamp, and the [un]certainty
  associated with the OCR processing. As this road is quite often used for international
  commerce, various nationalities might be encountered; several database tables are
  expected.
* One or several consumer(s) tying all the services together, _i.e._, posting to various
  queues (feeds) if different OCR engines are deployed, logging the requests, pushing to
  the database, _etc._ ([_Example_](producer/push.py) [_snippets_](consumer/pull.py)
  _to communicate with feeds hosted by_ `Redis` _are provided._)
* A dashboard to show in near real-time the amount of licence plates processed, and the
  average time necessary to do so for each. For this task, a simple
  [`Streamlit`](https://streamlit.io/) or [`Dash`](https://plotly.com/dash/) app would
  suffice, but do not fear the
  [command line window](https://github.com/FedericoCeratto/dashing).

Note all those services are expected to be containerised (additions to the
`docker-compose.yaml` file present in this repo), and any kind of data exchange done via
API calls and/or the central event hub (keep your feeds organised); with the exception of
the dashboard that will read data from the relational database.

Stress test on this proof of concept can be performed by enlarging the pool of producers.
