# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import os

# DATABASE_URL = os.getenv("DATABASE_URL")

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# # Dependency to get a database session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# import pymysql
# import os

# DB_CONFIG = {
#     "host": os.getenv("DATABASE_HOST", "localhost"),
#     "user": os.getenv("DATABASE_USER", "docker"),
#     "password": os.getenv("DATABASE_PASSWORD", "docker"),
#     "database": os.getenv("DATABASE_NAME", "demo_db")
# }

# def get_db_connection():
#     return pymysql.connect(**DB_CONFIG)

import psycopg2
from psycopg2.extras import RealDictCursor
import os

# PostgreSQL configuration
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "user": os.getenv("DATABASE_USER", "docker"),
    "password": os.getenv("DATABASE_PASSWORD", "docker"),
    "dbname": os.getenv("DATABASE_NAME", "demo_db"),
}

# Function to connect to PostgreSQL
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")