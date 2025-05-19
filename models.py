from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)  # Store hashed passwords
    first_name = Column(String(50))
    last_name = Column(String(50))
    accounts = relationship('Account', backref='owner', lazy=True)

    def __init__(self, username=None, password=None, first_name=None, last_name=None):
        self.username = username
        self.password = password  # This uses the setter method below
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Store password as hash instead of plaintext"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check password against stored hash"""
        return check_password_hash(self.password_hash, password)

    @property
    def values(self):
        return {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "accounts": [account.values for account in self.accounts]
        }


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    account_number = Column(String(20), unique=True, nullable=False)  # Changed to String to handle leading zeros
    type = Column(String(50), nullable=False)
    balance = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self, account_number=None, type=None, balance=0, user_id=None):
        self.account_number = account_number
        self.type = type
        self.balance = balance
        self.user_id = user_id

    def __repr__(self):
        return f'<Account {self.account_number}>'

    @property
    def values(self):
        return {
            "account_number": self.account_number,
            "type": self.type,
            "balance": self.balance,
            "owner": self.owner.username if self.owner else None
        }
