import joblib
from pathlib import Path
import pandas as pd
import shap
from backend.app.services import llm_service

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = BASE_DIR / "ml_pipeline" / "modelo_rf.pkl"
modelo = joblib.load(MODEL_PATH)
X_background = joblib.load(BASE_DIR / "ml_pipeline" / "features.pkl")
scaler = joblib.load(BASE_DIR / "ml_pipeline" / "scaler.pkl")
explainer = shap.LinearExplainer(modelo, X_background)

def predecir_abandono(clientes):
    resultados = []
    for cliente in clientes:
        cliente_id = cliente.pop("cliente_id", None)
        df_cliente = pd.DataFrame([cliente])
        df_cliente_escalado = scaler.transform(df_cliente)
        prediccion = modelo.predict(df_cliente_escalado)[0]
        if prediccion == 1:
            probabilidad = modelo.predict_proba(df_cliente_escalado)[0][1]
            valores_shap = explainer.shap_values(df_cliente_escalado)
            indice_motivo = int(valores_shap[0].argmax())
            motivo = df_cliente.columns[indice_motivo]
            sugerencia = llm_service.generar_sugerencia(motivo)
            resultados.append(
                {
                    "cliente_id": int(cliente_id),
                    "prediccion": int(prediccion),
                    "probabilidad_abandono": float(probabilidad),
                    "motivo": motivo,
                    "sugerencia": sugerencia
                }
            )
    return resultados