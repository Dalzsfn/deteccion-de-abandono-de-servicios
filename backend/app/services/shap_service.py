import numpy as np
from backend.app.services import llm_service, model_service


def _obtener_shap_clase_abandono(shap_values):
    shap_array = np.array(shap_values)

    if shap_array.ndim == 2:
        return shap_array[0]

    if shap_array.ndim == 3:
        return shap_array[0, :, 0]

    return shap_array


def obtener_detalle_abandono(cliente: dict) -> dict:
    cliente_id, nombre, datos_procesados, prob_abandono, prediccion = (
        model_service.predecir_cliente(cliente)
    )

    if prediccion != 1:
        raise ValueError(
            f"El cliente {cliente_id} no está clasificado en riesgo de abandono"
        )

    shap_values = model_service.explainer.shap_values(datos_procesados)
    shap_clase_abandono = _obtener_shap_clase_abandono(shap_values)

    top_2_indices = np.argsort(np.abs(shap_clase_abandono))[-2:][::-1]

    features_principales = [
        {
            "feature_legible": model_service.obtener_nombre_legible(
                model_service.columnas_features[idx]
            ),
        }
        for idx in top_2_indices
    ]

    motivo_principal = model_service.columnas_features[top_2_indices[0]]
    sugerencia = llm_service.generar_sugerencia(motivo_principal)

    return {
        "cliente_id": int(cliente_id),
        "nombre": nombre,
        "probabilidad_abandono": round(prob_abandono, 4),
        "features_principales": features_principales,
        "sugerencia_retencion": sugerencia,
    }
