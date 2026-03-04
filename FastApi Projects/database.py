from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

database_url="sqlite:///./test.db"

engine= create_engine(database_url,connect_args={"check_same_thread":False})

sessionlocal= sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base= declarative_base()