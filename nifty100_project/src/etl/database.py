# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the path to our SQLite database inside the data folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/nifty100.db"

# Create the engine (check_same_thread=False is needed for SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a customized Session class for future data insertion
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This Base class will be inherited by all our database models
Base = declarative_base()