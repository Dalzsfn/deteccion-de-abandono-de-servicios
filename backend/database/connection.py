import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")
print(env_path)
print(env_path.exists())


URL_DATABASE = f"postgresql://{user}:{password}@{host}:{port}/{database}"

print("USER:", user)
print("PASSWORD:", password)
print("HOST:", host)
print("PORT:", port)
print("DATABASE:", database)
print("URL:", URL_DATABASE)

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()