# pyrefly: ignore [missing-import]
from sqlalchemy import Column, String, Float, Integer
from src.etl.database import Base

class Company(Base):
    """Table storing static Nifty 100 company metadata."""
    __tablename__ = "companies"

    company_id = Column(String, primary_key=True, index=True)
    company_name = Column(String, index=True)
    sector = Column(String)
    industry = Column(String)

class FinancialData(Base):
    """Table storing yearly financial metrics for all companies."""
    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True)
    year = Column(String, index=True)
    
    # Core Financial Metrics (Mapped from our Excel files)
    sales = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)
    total_assets = Column(Float, nullable=True)
    cash_from_operating_activity = Column(Float, nullable=True)