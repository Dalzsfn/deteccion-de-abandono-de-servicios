from sqlalchemy import text
from backend.database.connection import engine

def get_clientes():
    with engine.connect() as connection:
        query = text(
            """
            SELECT v.*, c.nombre
            FROM vista_clientes v
            JOIN clientes c ON c.cliente_id = v.cliente_id;
            """
        )
        result = connection.execute(query)
        return [dict(row) for row in result.mappings()]


def get_cliente(cliente_id: int):
    with engine.connect() as connection:
        query = text(
            """
            SELECT v.*, c.nombre
            FROM vista_clientes v
            JOIN clientes c ON c.cliente_id = v.cliente_id
            WHERE v.cliente_id = :cliente_id;
            """
        )
        result = connection.execute(query, {"cliente_id": cliente_id})
        row = result.mappings().first()
        if row is None:
            raise ValueError(f"No se encontró un cliente con ID {cliente_id}")
        return dict(row)
    