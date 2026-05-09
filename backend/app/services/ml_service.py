import joblib
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

MODEL_PATH = BASE_DIR / "ml_pipeline" / "modelo_rf.pkl"
modelo = joblib.load(MODEL_PATH)

def predecir_abandono(clientes):
    resultados = []
    
    for cliente in clientes:
        cliente_id = cliente.pop("cliente_id", None)
        df_cliente = pd.DataFrame([cliente])
        prediccion = modelo.predict(df_cliente)[0]
        probabilidad = modelo.predict_proba(df_cliente)[0][1]
        resultados.append(
            {
                "cliente_id": int(cliente_id),
                "prediccion": int(prediccion),
                "probabilidad_abandono": float(probabilidad)
            }
        )
    return resultados