import logging
import os
import sqlalchemy
import sqlalchemy.ext.declarative

logging.basicConfig(datefmt='%Y/%m/%d %X', format='%(asctime)s: %(message)s', level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

Base = sqlalchemy.ext.declarative.declarative_base()

class Data(Base):
    __tablename__ = 'data'
    id_ = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.BigInteger)
    message = sqlalchemy.Column(sqlalchemy.String)

def connect(func):
    def wrapper(*args, **kwargs):
        try:
            engine = kwargs.pop('engine')
            session = kwargs.pop('session')
        except KeyError:
            try:
                user = os.environ['POSTGRES_USER']
                pssw = os.environ['POSTGRES_PASSWORD']
                host = os.environ['POSTGRES_HOST']
                port = os.environ['POSTGRES_PORT']
                db = os.environ['POSTGRES_DB']
                engine = sqlalchemy.create_engine(f'postgresql://{user}:{pssw}@{host}:{port}/{db}')
                session = sqlalchemy.orm.sessionmaker(engine)()
            except:
                return False
        return func(*args, engine=engine, session=session, **kwargs)
    return wrapper

@connect
def create_tables_if_not_existing(base=Base, engine=None, session=None):
    base.metadata.create_all(engine)

@connect
def insert(mapping, engine=None, session=None):
    session.add(mapping)
    session.commit()
    logger.debug('Just wrote a new record to the database.')

@connect
def query(mapping, since, until, engine=None, session=None):
    return session.query(mapping) \
                  .filter(mapping.timestamp >= since) \
                  .filter(mapping.timestamp <= until) \
                  .all()
