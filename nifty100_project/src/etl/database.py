# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine, event
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the path to our SQLite database inside the data folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/nifty100.db"

# Create the engine (check_same_thread=False is needed for SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


# Day 04 (1.6): SQLite does not enforce foreign keys unless explicitly
# switched on per-connection. Enable it so FK constraints are active
# for every session, satisfying AC-03 (PRAGMA foreign_key_check == 0 rows).
@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create a customized Session class for future data insertion
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This Base class will be inherited by all our database models
Base = declarative_base()