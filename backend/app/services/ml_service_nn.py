import shap
import torch
import numpy as np
import pandas as pd
from pathlib import Path
from backend.app.services import llm_service
from ml_pipeline.train_model_nn import RedPrediccionChurn  

BASE_DIR   = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = BASE_DIR / "ml_pipeline" / "modelo_churn.pth"

checkpoint     = torch.load(MODEL_PATH, weights_only=False)
preprocesador  = checkpoint['preprocesador']
#columnas_orden = checkpoint['columnas_orden']  # ← cargar orden de columnas

modelo = RedPrediccionChurn(input_dim=checkpoint['input_dim'])
modelo.load_state_dict(checkpoint['model_state_dict'])
modelo.eval() 

def modelo_para_shap(X_numpy: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        tensor = torch.tensor(X_numpy, dtype=torch.float32)
        logits = modelo(tensor)
        probs  = torch.softmax(logits, dim=1)
    return probs.numpy()  


#_background_path = BASE_DIR / "ml_pipeline" / "data" / "gym_churn_us.csv"
#_df_background   = pd.read_csv(_background_path)
#_df_background['caida_frecuencia'] = (
   # _df_background['Avg_class_frequency_total'] - _df_background['Avg_class_frequency_current_month']
#)
#_df_background = _df_background.drop(columns=['Churn', 'Avg_class_frequency_total', 'Phone', 'gender'])
#_df_background = _df_background[columnas_orden]          # ← alinear columnas del background
#_background_procesado = preprocesador.transform(_df_background)

#explainer = shap.KernelExplainer(modelo_para_shap, shap.sample(_background_procesado, 100))


def predecir_abandono(clientes: list[dict]) -> list[dict]:
    resultados = []
    for cliente in clientes:
        cliente_id = cliente.pop("cliente_id", None)
        
        cliente_limpio = {
            k: float(v) if hasattr(v, '__float__') else v
            for k, v in cliente.items()
        }

        df_cliente = pd.DataFrame([cliente_limpio])
        datos_procesados = preprocesador.transform(df_cliente)

        input_tensor = torch.tensor(datos_procesados, dtype=torch.float32)

        modelo.eval()
        with torch.no_grad():
            output = modelo(input_tensor)
            prediccion = torch.argmax(output, dim=1)
            probabilidad = torch.softmax(output, dim=1).squeeze()
            prob_abandono = probabilidad[1].item()
        if prediccion == 1:
            resultados.append({
                "cliente_id":            int(cliente_id),
                "prediccion":            prediccion,
                "probabilidad_abandono": prob_abandono,
            })

    return resultados