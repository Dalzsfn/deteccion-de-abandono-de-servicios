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
        probs  = torch.sigmoid(logits).squeeze(1)  
    return probs.numpy()


def _obtener_shap_clase_abandono(shap_values):

    shap_array = np.array(shap_values)
    
    if shap_array.ndim == 2:
        return shap_array[0]

    if shap_array.ndim == 3:
        return shap_array[0, :, 0]

    return shap_array

_background_path = BASE_DIR / "ml_pipeline" / "data" / "gym_churn_us.csv"
_df_background    = pd.read_csv(_background_path)

_X_background = _df_background.drop(columns=['Churn', 'Phone', 'gender'])
_background_procesado = preprocesador.transform(_X_background)
_columnas_features = [nombre.split('__', 1)[-1] for nombre in preprocesador.get_feature_names_out()]
_background_muestra = shap.sample(_background_procesado, min(100, len(_background_procesado)))
explainer = shap.KernelExplainer(modelo_para_shap, _background_muestra)

def predecir_abandono(clientes: list[dict]) -> list[dict]:
    resultados = []
    for cliente in clientes:
        cliente_id = cliente.pop("cliente_id", None)

        cliente_limpio = {
            k: float(v) if hasattr(v, '__float__') else v
            for k, v in cliente.items()
        }

        df_cliente = pd.DataFrame([cliente_limpio])
        df_cliente = df_cliente[_X_background.columns]

        datos_procesados = preprocesador.transform(df_cliente)
        input_tensor = torch.tensor(datos_procesados, dtype=torch.float32)

        with torch.no_grad():
            logits = modelo(input_tensor)
            prob_abandono = torch.sigmoid(logits).item()
            prediccion = int(prob_abandono >= 0.5)

        if prediccion == 1:
            shap_values = explainer.shap_values(datos_procesados)
            shap_clase_abandono = _obtener_shap_clase_abandono(shap_values)

            top_2_indices = np.argsort(np.abs(shap_clase_abandono))[-2:][::-1]

            features_principales = [
                {
                    "feature": _columnas_features[idx],
                    "impacto": float(shap_clase_abandono[idx]),
                    "valor": float(datos_procesados[0, idx])
                }
                for idx in top_2_indices
            ]

            resultados.append({
                "cliente_id":            int(cliente_id),
                "prediccion":            prediccion,
                "probabilidad_abandono": prob_abandono,
                "features_principales":  features_principales,
            })

    return resultados