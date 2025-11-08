import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db") 
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
ECHO_SQL = os.getenv("DEBUG_SQL", "0") == "1"  # set DEBUG_SQL=1 to echo SQL
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=ECHO_SQL)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)