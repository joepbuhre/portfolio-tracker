from sqlalchemy import DECIMAL, VARCHAR, Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(VARCHAR, primary_key=True, index=True)

class ShareUser(Base):
    __tablename__ = 'share_user'
    id = Column(VARCHAR(256), primary_key=True),
    share_id = Column(VARCHAR(256)),
    user_id = Column(VARCHAR(256), nullable=False),
    purchase_date = Column(DateTime),
    currency_date = Column(Date),
    product = Column(VARCHAR(500), nullable=True),
    isin = Column(VARCHAR(256)),
    description = Column(VARCHAR(500), nullable=True),
    fxrate = Column(DECIMAL(19,4), default=0),
    mutation_currency = Column(VARCHAR(20), nullable=True),
    mutation = Column(DECIMAL(19,4), default=0),
    balance_currency = Column(VARCHAR(20), nullable=True),
    balance = Column(DECIMAL(19,4), default=0),
    order_id = Column(VARCHAR(256), nullable=True),
    quantity = Column(DECIMAL(19,4), nullable=True),
    share_price = Column(DECIMAL(19,4), nullable=True),
    hash = Column(Numeric, unique=True),