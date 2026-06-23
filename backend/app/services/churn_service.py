from backend.app.services import model_service


def listar_clientes_en_riesgo(clientes: list[dict]) -> list[dict]:
    clientes_en_riesgo = []

    for cliente in clientes:
        cliente_id, nombre, _, _, prediccion = model_service.predecir_cliente(cliente)

        if prediccion == 1:
            clientes_en_riesgo.append(
                {
                    "cliente_id": int(cliente_id),
                    "nombre": nombre,
                }
            )

    return clientes_en_riesgo
