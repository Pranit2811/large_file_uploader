from sqlalchemy import create_engine, Column, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from config.development import DATABASE_URL

Base = declarative_base()


#SQLAlchemy engine
engine = create_engine(DATABASE_URL)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
        Session.remove() 

#Company model
class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, autoincrement=True)  # SERIAL PRIMARY KEY
    name = Column(String(255), index=True, nullable=False, default="")
    domain = Column(String(255), index=True, nullable=False, default="")
    year_founded = Column(String(255), index=True, nullable=False, default="")
    industry = Column(String(100), index=True, nullable=False, default="")
    size_range = Column(String(50), nullable=False, default="")
    locality = Column(String(100), nullable=False, default="")
    country = Column(String(100), index=True, nullable=False, default="")
    linkedin_url = Column(String(255), default="")
    current_employee_estimate = Column(Integer, default=0)  # If you want to set a default of 0
    total_employee_estimate = Column(Integer, default=0) 

    __table_args__ = (
        Index('idx_industry_city', 'industry'),
        Index('idx_country_year_founded', 'country', 'year_founded'),
    )


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

#Database tables
Base.metadata.create_all(bind=engine)
