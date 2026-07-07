from src.etl.database import engine, Base
# Import models so the Base knows about them before creating tables
from src.etl import models  # noqa: F401


def create_tables():
    print("\u23f3 Building Database Architecture...")
    # This command creates all tables defined in models.py
    Base.metadata.create_all(bind=engine)
    print("\u2705 Schema created successfully! data/nifty100.db is ready.")


if __name__ == "__main__":
    create_tables()
