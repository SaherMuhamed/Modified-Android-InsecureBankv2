from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool  # For SQLite in-memory if needed

# Configure database connection
engine = create_engine(
    'sqlite:///mydb.db',
    connect_args={'check_same_thread': False},  # Needed for SQLite with Flask
    poolclass=StaticPool,  # Optional for SQLite
    echo=True  # Set to False in production
)

db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Initialize the database and create tables."""
    # Import models here to ensure they're registered with SQLAlchemy
    from models import User, Account  # Import all your models
    Base.metadata.create_all(bind=engine)

    # Optional: Add initial test data
    if not User.query.first():
        test_user = User(username='admin', password='admin123')
        db_session.add(test_user)
        test_account1 = Account(user='admin', account_number='12345', type='from', balance=1000)
        test_account2 = Account(user='admin', account_number='67890', type='to', balance=500)
        db_session.add_all([test_account1, test_account2])
        db_session.commit()


# Close the session at app teardown
def shutdown_session(exception=None):
    db_session.remove()


# For Flask integration
def register_db(app):
    """Register database functions with Flask app."""
    app.teardown_appcontext(shutdown_session)
