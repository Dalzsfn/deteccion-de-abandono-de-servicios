from sqlalchemy import text
from backend.database.connection import engine

def get_clientes():
    with engine.connect() as connection:
        query = text("SELECT * FROM vista_entrenamiento_ml;")  
        result = connection.execute(query)
        return [dict(row) for row in result.mappings()]
    
    