import shap
import torch
import numpy as np
import pandas as pd
from pathlib import Path
from backend.app.services import llm_service
from ml_pipeline.train_model_nn import RedPrediccionChurn  

BASE_DIR   = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = BASE_DIR / "ml_pipeline" / "modelo_churn.pth"

checkpoint    = torch.load(MODEL_PATH, weights_only=False)
preprocesador = checkpoint['preprocesador']

modelo = RedPrediccionChurn(input_dim=checkpoint['input_dim'])
modelo.load_state_dict(checkpoint['model_state_dict'])
modelo.eval() 

def modelo_para_shap(X_numpy: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        tensor = torch.tensor(X_numpy, dtype=torch.float32)
        logits = modelo(tensor)
        probs  = torch.softmax(logits, dim=1)
    return probs.numpy()  


_background_path = BASE_DIR / "ml_pipeline" / "data" / "gym_churn_us.csv"
_df_background   = pd.read_csv(_background_path)
_df_background['caida_frecuencia'] = (_df_background['Avg_class_frequency_total'] -_df_background['Avg_class_frequency_current_month'])
_df_background = _df_background.drop(columns=['Churn', 'Avg_class_frequency_total', 'Phone', 'gender', 'Contract_period'])
_background_procesado = preprocesador.transform(_df_background)

explainer = shap.KernelExplainer(modelo_para_shap,shap.sample(_background_procesado, 100))


def predecir_abandono(clientes: list[dict]) -> list[dict]:
    resultados = []
    for cliente in clientes:
        cliente_id = cliente.pop("cliente_id", None)
        df_cliente = pd.DataFrame([cliente])
        X_procesado = preprocesador.transform(df_cliente)

        with torch.no_grad():
            tensor  = torch.tensor(X_procesado, dtype=torch.float32)
            logits  = modelo(tensor)
            probs   = torch.softmax(logits, dim=1)
            prediccion   = int(torch.argmax(probs, dim=1).item())
            probabilidad = float(probs[0][1].item())

        if prediccion == 1:
            shap_values = explainer.shap_values(X_procesado)
            if isinstance(shap_values, list) and len(shap_values) == 2:
                shap_churn = shap_values[1][0]
            else:
                shap_churn = np.array(shap_values)[0]

            shap_positivos = np.where(shap_churn > 0, shap_churn, 0)
            indice_motivo  = int(np.argmax(shap_positivos))
            motivo         = df_cliente.columns[indice_motivo]

            sugerencia = llm_service.generar_sugerencia(motivo)

            resultados.append({
                "cliente_id":            int(cliente_id),
                "prediccion":            prediccion,
                "probabilidad_abandono": probabilidad,
                "motivo":                motivo,
                "sugerencia":            sugerencia,
            })

    return resultados