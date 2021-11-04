# Database management in `Python`

> I suggest **not** to use `Pandas` for this whole thing. It is actually slower than the vanilla `csv` [module](https://docs.python.org/3/library/csv.html) from the `Python` standard library during ingestion, and will not help you build the queries. `Polars` could also be interesting to test out...

> Note we are not using a single `SQL` command line; each model you will write can be shared with anyone else to query the database you are structuring.

> At any moment you can check what is in the `SQL` database by using a free database developer/administrator tool like `DBeaver`.

## Data

The client company offers bikes to rent after registering to its service. The management wants to simulate the flow of people registering to their service over six months, and check if the number of bikes they prepared is enough for the region they cover.

You are receiving a database dump of two tables in `.csv` format. The company expects events to be updated every 20 minutes, scaled down to 2 seconds for the simulation. Each timestep, non-registered customers have a 30% chance to subscribe to the rental service, and a 40% chance to contract an insurance before renting the bike. Each timestep, registered users have a 60% chance to rent a bike if not renting one yet; or a 90% chance if between 7 and 9 am or 5 and 7 pm. Each timestep, customers already renting bikes can drop them with a probability equal to the amount of hours-plus-one they kept them times 10, with a cap at 90%. When dropped, a bike has a 3% chance to be totalled (unusable), and 10% chance to have an issue needing to be fixed (light, chains, flat tire, _etc._); for which a insured subscribed user would not have to pay for, contrary to a customer without insurance.

Prices (subscription, insurance, repairs, _etc._) are left to your discretion if you decide to give an estimation of the rentability of the service.

_Please let me know of any improvements needed on the statistics._

## SQL

> Update the database after each event, once the data is ingested.

To ingest the data we will use `SQLAlchemy` as we want a fine-grained management of each `.csv` record (see _Extras_ below): To begin with, write your own [data models](https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/basic_use.html) describing both tables (column names and [data types](https://docs.sqlalchemy.org/en/13/core/type_basics.html)). Pull your favourite database flavour from the `DockerHub` (if no favourite, what about [this one](https://hub.docker.com/_/postgres)) and fill it with the data.

_Keep in mind_ **statelessness** _when running your database containers in case you do not want to re-ingest data each time. And remember to_ **publish** _ports to be able to reach the applications inside._

To ingest the data you want to loop over each row and create the corresponding object (_e.g._, data model) before sending it to the database. To avoid too many network exchanges with the database, [bulk-inserting](https://docs.sqlalchemy.org/en/13/_modules/examples/performance/bulk_inserts.html) is a common solution.

Each timestep, [query](https://docs.sqlalchemy.org/en/13/orm/tutorial.html#querying) a random number of users (keep a list of bike/customer IDs in your loop and `random.choice()` through it; keep it reasonable, timeframe is 20 minutes) and pick random non-rented bikes (when needed) and perform the little probabilistic gymnastics described above. Keep track of the IDs of the bikes/customers in the opposite tables respectively; or in a third table if you prefer/find it cleaner. You want to know which bike is rented by which customer at any moment!

### Extras

#### Datetime management

You will notice that if you define a field as `Date` or `DateTime` the ingest process will spit the data back at you: you need to _format_ the string read from the `.csv` to a `Python` `datetime` object (using `datetime.strptime()` for instance). You can do so in ~~three~~ two ways:

* ~~Use `str` instead and [re]format it on the fly [each time].~~ **NO**
* Convert to the `datetime` object in your reading loop, before creating the object, and provide it as the right data type when doing so.
* Ask `SQLAlchemy` to make it happen right before sending the data to the database, using [event hooks](https://stackoverflow.com/a/12513904) (documentation is cryptic, look for examples instead).

Note the last solution offers quite a lot of flexibility (apply a function right before an insert/update/_etc._) and leave things quite transparent for the user that is left manipulating simple strings. It requires however to know the date [format](https://strftime.org/).

#### Pseudonymisation and encryption of sensitive data

> Yes it is a [real word](https://en.wikipedia.org/wiki/Pseudonymization).

The company is trying its best to follow the GDPR ruling. Two teams are claiming access to the data for analytics perspective, and two use cases are discussed:

* The **BI team** would like to build a completely anonymous dashboard. They are planning to query the database directly; but the legal team did not allow them to _see_ the sensitive data (BSN, bank accounts, name, _etc._), only a _hashed_ version of it. Strong of your previous implementation (last bullet of the previous section), create a new table that will hold the events (subscription/insurance, bike rent, bike drop), including _hashed_ data using the [common library](https://docs.python.org/3/library/hashlib.html). _Keep in mind that it isn't completely anonymised as the same data will produce the same hash!_
* The **Advanced Analytics team** who would like to join this data with other data sources related to the same customers (identified by their BSN). Identically as the BI team, the data scientists members of this team did not receive agreement from the legal team to _see_ the sensitive data. But their data engineer is allowed to perform joins with data queried from your tables. After discussion with all parties, it has been decided that you would provide the data in an encrypted form, the data engineer being the only one allowed to decrypt it (the only one with the key). Modify your models to store this data in an encrypted format (see [example](https://sqlalchemy-utils.readthedocs.io/en/latest/_modules/sqlalchemy_utils/types/encrypted/encrypted_type.html); look in the docstring of the `StringEncryptedType` object); anyone (data scientist) with a version of the data models _without_ the decryption logic will see random gibberish, but the engineer to which you delivered the complete data models will get the _clear_ data without, automatically decrypted by `SQLAlchemy` on the fly. _Note that in this case the visible data is completely random and_ not _consistent over the same underlying values. Joining or indexing (for example) are thus completely meaningless._

### NoSQL

> Push events to a key/value in-memory database.

The company is expecting a lot more events than what we can observe here. To be able to handle them, a [pub/sub](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) architecture has been thought of. To replicate it at your scale, the in-memory `Redis` key/value database is of great help! Pull the last version from the `DockerHub` and dive in [some examples](https://kb.objectrocket.com/redis/basic-redis-usage-example-part-1-exploring-pub-sub-with-redis-python-583). The company is requesting here to publish each type of event in its own channel. Every 20 minutes (2 seconds), a subscribed script will check if new events occured and output a summary account of each (sum of events of each type), and issue a warning logging call in case a bike is totalled.

_You just built your first (?) event-driven infrastructure! And since you now have **four services** (both databases, and both scripts publishing and subscribed to the events), it would be time to organise all this in a tight_ `docker-compose.yaml`.

Note you could also decide to push this to an `Elasticsearch` database as well, and query/aggregate per bike/customer/date/_etc._ and expose a `Kibana` dashboard.

### Extras

#### Make the listening script into a simple dashboard

As you want to impress the client with your event-driven PoC readying them for `Kafka`, find the time to plot the number of events of each type on a quickly made frontend using your favourite `Python` dashboarding tool (`dash`, `streamlit`, `voila`, _etc._). You could even generate random latitude/longitude coordinates for each event and plot them on a map. Surprise them/me!

#### Organise the data using a graph database

The client company is starting a collaboration with a matchmaking/hookup startup that plans to have people meet based on the bikes they rented. Users who rent the same bike get a selfie (taken from the handlebar) and the ID of their most recent matches. To ease the organisation and especially querying of such data, the client requests you link customers and bikes in a graph database. Although they will use `ONgDB` in their own infrastructure, they suggested you use `RedisGraph` for your PoC as it is freely available on the `DockerHub`.

[Load](https://github.com/RedisGraph/redisgraph-py) the inital data in a first step -looping as before; can be done by your ingesting script- before linking the nodes (_e.g._, bikes and customers) as the renting events get fired -use the listener script.

_You should be able to visualise your graph using_ `RedisInsight` _pulled from the_ `DockerHub` _as always._
