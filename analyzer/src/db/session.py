from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from models.base import Base

# Create the engine
engine = create_engine(config["database"]["url"])

Base.metadata.create_all(engine)
# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
