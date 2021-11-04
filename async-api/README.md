# Model serving using [a]synchronous API

A simple construct using `falcon` `gunicorn` `celery` `redis` `flower` and `docker-compose` to expose a data science model as an API. Both [synchronous](#synchronous-version) & [asynchronous](#asynchronous-version) versions.

## Model structure

### Data

As you may have noticed in the code the input data needed by the API-embedded Data Science Model™ is not of the highest caliber. But it helps with wrapping your mind around what is needed, and where. Or at least it does for me.

The class in `app/data/dummy.py` is meant to be a connector to wherever the data is located, say, a datalake or a database. At the current state it simply generates a set of points around -_i.e._, manually fuzzed- a function; function that we are trying to fit in the next paragraph.

### The `.fit()` `.predict()` `.score()` trinity

All data science models should follow this simple rule of thumb, and contain _at least_ the structure described in here (together with some logging as well as testing, but these last two are not implemented in this project _yet_). Once again this is not the focus here, but it helps structuring an API: something to train/calibrate the model, something to serve prediction based on said trained model, and a way to evaluate its quality. This last one is rarely an endpoint in itself as the model should have its monitoring automated, and logged.

Any less and you can return the code to the data scientists. Together with the notebooks you do _not_ put in production.

The file `app/model/models.py` contains for now two algorithms, a simple multivariate regressor (`MultivariateRegressor`) and a polynomial regressor (`PolynomialRegressor`); with some inheritance from a meta-class (`Regressor`). Here again the goal is not the model itself, but how/where you would put this part of the code within your application. (But you get bonus point to follow on the matrix juggling.)

## Synchronous version

### Spin it up

Get to the right branch of this repo, and using a proper [setup](https://docs.docker.com/install/) of `Docker`:

```bash
$ docker build -t sync-app:0.1 .
$ docker run --rm sync-app
```

And see you at [http://localhost:5000/ping](http://localhost:5000/ping). For the other endpoints, I let you browse the code.

Check at the [bottom of this page](#but-it-worked-on-your-machine...) for the warnings you might encounter along the way.

### Structure of the project

```text
./
├── app/
|   ├── __init__.py
|   ├── data/
|   |   └── dummy.py
|   ├── model/
|   |   ├── models.py
|   |   └── evaluate.py
|   └── serve.py
└── Dockerfile
```

The file `__init__.py` creates the API itself while `serve.py` defines all its endpoints. To build the base image the stages defined in the `Dockerfile` are performed. The packages needed to build and run the application are also defined in the `Dockerfile`.

## Asynchronous version

I kept a generator in the `app/tasks.py` file as you might want to make data ingesting asynchronous (just add the `@queue.task` decorator) depending on the volume you are playing with. It also represent the final dataset that you will feed to the model; all joins and other transformations should be part of the code within `app/data/`.

### Spin it up

To spin the API, two `celery` workers, `redis` as broker _and_ backend, and `flower` for monitoring (five `alpine` containers out of two images), get to the right branch of this repo, and simply go with the usual:

```bash
$ docker-compose build
$ docker-compose up
```

Check if I am not making stuff up:

```bash
$ docker ps --no-trunc
```

Which should return:

```text
CONTAINER ID   IMAGE          COMMAND                                                                       CREATED       STATUS         PORTS                    NAMES
af0ac46d822f   redis:alpine   "docker-entrypoint.sh redis-server"                                           7 hours ago   Up 4 minutes   6379/tcp                 redis
fa112754d903   asycn-app      "gunicorn app:api --bind 0.0.0.0:5000"                                        7 hours ago   Up 4 minutes   0.0.0.0:5000->5000/tcp   gunicorn-falcon
67b748fa34f0   async-app      "celery worker --app app.tasks --concurrency 2 --loglevel WARNING --events"   7 hours ago   Up 4 minutes                            celery-worker1
776557bc7b54   async-app      "celery worker --app app.tasks --concurrency 2 --loglevel WARNING --events"   7 hours ago   Up 4 minutes                            celery-worker2
31507b50bcc7   async-app      "flower --app app.tasks"                                                      7 hours ago   Up 4 minutes   0.0.0.0:5555->5555/tcp   flower
```

If your [environment](https://docs.docker.com/compose/install/) (`Docker` & `docker-compose`) is setup correctly it should work straight out of the box. _(But does it ever...)_ Then see you at [http://localhost:5000/ping](http://localhost:5000/ping). For the other endpoints, I let you browse the code.

Check at the [bottom of this page](#but-it-worked-on-your-machine...) for the warnings you might encounter along the way.

### Structure of the project

```text
./
├── app/
|   ├── __init__.py
|   ├── data/
|   |   └── dummy.py
|   ├── model/
|   |   ├── models.py
|   |   └── evaluate.py
|   ├── serve.py
|   └── tasks.py
├── Dockerfile
└── docker-compose.yaml
```

(Changes from the previous version happen in `__init__.py`, `serve.py` & `requirements.txt`. The new files are `tasks.py` & `docker-compose.yaml`.)

The file `__init__.py` creates the API itself and the task queue (managed by `celery`), `serve.py` defines all the endpoints of the API (am not so proud of the clumsy decorator, but it does the trick); the tasks, asynchronous or not, are now all defined in `tasks.py`. To build the base image (used by all the services but the broker and the backend, both handled by `redis`), the stages defined in the `Dockerfile` are performed. As always, the packages needed to run this whole thing are defined within `requirements.txt`.

In this version, what is more interesting is the orchestrating happening in the `docker-compose.yaml`.

### Bonus!

Can you guess what is happening in the `docker ps` output below? What changes do you have to implement to run it so?

```text
CONTAINER ID   IMAGE             COMMAND                                                                       CREATED          STATUS          PORTS                                NAMES
1e1b3a0dfd4c   rabbitmq:alpine   "docker-entrypoint.sh rabbitmq-server"                                        28 seconds ago   Up 25 seconds   4369/tcp, 5671-5672/tcp, 25672/tcp   rabbitmq
f6e11242a929   redis:alpine      "docker-entrypoint.sh redis-server"                                           28 seconds ago   Up 25 seconds   6379/tcp                             redis
9afb513c0642   nginx             "nginx -g 'daemon off;'"                                                      28 seconds ago   Up 23 seconds   0.0.0.0:80->80/tcp                   nginx
f9fe09998a04   async-app         "gunicorn app:api --bind localhost:5000"                                      25 seconds ago   Up 23 seconds   5000/tcp                             gunicorn-falcon
b795d34f8d00   async-app         "celery worker --app app.tasks --concurrency 2 --loglevel WARNING --events"   23 seconds ago   Up 21 seconds                                        celery-worker
```

## But it worked better on your machine...

* `chromium` seems to mistreat drama queen `gunicorn` which in return breaks up often with a `[CRITICAL] WORKER TIMEOUT`. Read [#1801](https://github.com/benoitc/gunicorn/issues/1801) (towards the end) if you really have time; otherwise, know it is not impeding and let it be. And we are aiming at `nginx` anyway, see [below](#other-links).
* If/When encountering the delightful `AttributeError: module 'tornado.web' has no attribute 'asynchronous'` report to [#878](https://github.com/mher/flower/issues/878) or simply add `tornado==5.1.1` in your `requirements.txt` (last version including the asynchronous calls needed by `flower`; this latter should know better and make it a hard version requirement).
* I do not care about `RuntimeWarning: You're running the worker with superuser privileges: this is absolutely not recommended!` warnings, despite reading [this topic on their FAQ](http://docs.celeryproject.org/en/latest/faq.html#is-it-safe-to-run-celery-worker-as-root). I simply turn that off by setting the `loglevel` to `WARNING`. **(And decline all responsibilities.)** Good exercise to add some lines to the `Dockerfile` to fix that.
* The quantities marked `N/A` at [http://localhost:5555/broker](http://localhost:5555/broker) are only available for `RabbitMQ`; if you do not believe me see [#114](https://github.com/mher/flower/issues/114) (and especially [this comment](https://github.com/mher/flower/issues/114#issuecomment-23379895)).

## Some links

* Add a Best Practice™ reverse proxy with [their help](https://www.digitalocean.com/community/tutorials/how-to-deploy-falcon-web-applications-with-gunicorn-and-nginx-on-ubuntu-16-04).
* Very similar projects [here](https://testdriven.io/blog/asynchronous-tasks-with-falcon-and-celery/) and [there](https://testdriven.io/blog/asynchronous-tasks-with-flask-and-redis-queue/). Might even have sparked the idea of this one, who knows.
* Check the `docker-compose` API [here](https://docs.docker.com/compose/) to follow and extend what has been done here.
