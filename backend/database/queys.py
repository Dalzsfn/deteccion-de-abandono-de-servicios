from sqlalchemy import text
from database.connection import engine
from urllib.parse import unquote

def get_clientes():
    with engine.connect() as connection:
        query = text("SELECT * FROM clientes")  
        result = connection.execute(text("SELECT * FROM clientes"))
        return [dict(row) for row in result]