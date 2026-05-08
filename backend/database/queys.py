from sqlalchemy import text
from database.connection import engine
from urllib.parse import unquote

def get_clientes():
    with engine.connect() as connection:
        query = text("SELECT * FROM vista_entrenamiento_ml;")  
        result = connection.execute(query)
        return [dict(row) for row in result]
    
    