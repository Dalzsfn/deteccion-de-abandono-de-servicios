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


# ── Telegram ─────────────────────────────────────────────────────────────────

def buscar_cliente_por_celular(celular_normalizado: str) -> int | None:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT cliente_id FROM clientes WHERE celular = :celular;"),
            {"celular": celular_normalizado},
        )
        row = result.mappings().first()
        return row["cliente_id"] if row else None


def upsert_telegram_link(cliente_id: int, chat_id: int) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO telegram_links (cliente_id, chat_id, fecha_vinculacion)
                VALUES (:cliente_id, :chat_id, NOW())
                ON CONFLICT (cliente_id)
                DO UPDATE SET chat_id = EXCLUDED.chat_id,
                              fecha_vinculacion = NOW();
                """
            ),
            {"cliente_id": cliente_id, "chat_id": chat_id},
        )


def get_chat_id(cliente_id: int) -> int | None:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT chat_id FROM telegram_links WHERE cliente_id = :cid;"),
            {"cid": cliente_id},
        )
        row = result.mappings().first()
        return row["chat_id"] if row else None


def get_sugerencia_enviada(cliente_id: int) -> dict | None:
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT * FROM sugerencias_enviadas WHERE cliente_id = :cid;"
            ),
            {"cid": cliente_id},
        )
        row = result.mappings().first()
        return dict(row) if row else None


def insertar_sugerencia_enviada(cliente_id: int, mensaje: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO sugerencias_enviadas (cliente_id, mensaje_enviado, fecha_envio)
                VALUES (:cliente_id, :mensaje, NOW());
                """
            ),
            {"cliente_id": cliente_id, "mensaje": mensaje},
        )


def listar_sugerencias_enviadas() -> list[dict]:
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    s.id,
                    s.cliente_id,
                    c.nombre,
                    s.mensaje_enviado,
                    s.fecha_envio
                FROM sugerencias_enviadas s
                JOIN clientes c ON c.cliente_id = s.cliente_id
                ORDER BY s.fecha_envio DESC;
                """
            )
        )
        return [dict(row) for row in result.mappings()]
    