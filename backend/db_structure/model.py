from calendar import c
from sqlalchemy import DECIMAL, VARCHAR, Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from db_structure import get_db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = get_db()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(VARCHAR, primary_key=True, index=True)

class ShareActions(Base):
    __tablename__ = 'share_actions'
    id = Column(VARCHAR(256), primary_key=True)
    user_id = Column(VARCHAR(256), nullable=False)
    share_id = Column(VARCHAR(256))
    purchase_date = Column(DateTime)
    currency_date = Column(Date)
    product = Column(VARCHAR(500), nullable=True)
    fxrate = Column(DECIMAL(19,4), default=0)
    isin = Column(VARCHAR(256))
    mutation_currency = Column(VARCHAR(20), nullable=True)
    mutation = Column(DECIMAL(19,4), default=0)
    order_id = Column(VARCHAR(256), nullable=True)
    action = Column(Numeric)
    hash = Column(Numeric, unique=True)
    quantity = Column(DECIMAL(19,4), nullable=True)
    share_price = Column(DECIMAL(19,4), nullable=True)
    testCol = Column(Numeric)


class ShareInfo(Base):
    __tablename__ = "share_info"
    id = Column('id', VARCHAR(256), primary_key=True)
    isin = Column('isin', VARCHAR(256))
    description = Column('description', VARCHAR(256))
    market = Column('market', VARCHAR(256))
    ticker = Column('ticker', VARCHAR(256))

class ShareHistory(Base):
    __tablename__ = "share_history"
    id = Column('id', VARCHAR(256), primary_key=True)
    share_id = Column('share_id', VARCHAR(256))
    open = Column('open', DECIMAL(19,4))
    close = Column('close', DECIMAL(19,4))
    low = Column('low', DECIMAL(19,4))
    high = Column('high', DECIMAL(19,4))
    volume = Column('volume', DECIMAL(19,4))
    dividends = Column('dividends', DECIMAL(19,4))
    stock_splits = Column('stock_splits', DECIMAL(19,4))
    date = Column('date', DateTime)

class Config(Base):
    __tablename__ = "config"
    key = Column('key', VARCHAR(256), primary_key=True)
    value = Column('value', VARCHAR(None))