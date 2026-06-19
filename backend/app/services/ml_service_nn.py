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

modelo = RedPrediccionChurn(input_dim=checkpoint['input_dim'])
modelo.load_state_dict(checkpoint['model_state_dict'])
modelo.eval() 

def modelo_para_shap(X_numpy: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        tensor = torch.tensor(X_numpy, dtype=torch.float32)
        logits = modelo(tensor)
        probs  = torch.softmax(logits, dim=1)
    return probs.numpy()  


def _obtener_shap_clase_abandono(shap_values):
    if isinstance(shap_values, list):
        if len(shap_values) > 1:
            return shap_values[1][0]
        return shap_values[0][0]

    shap_array = np.array(shap_values)

    if shap_array.ndim == 3:
        if shap_array.shape[2] > 1:
            return shap_array[0, :, 1]
        return shap_array[0, :, 0]

    if shap_array.ndim == 2:
        return shap_array[0]

    return shap_array


# Cargar y preparar background data para SHAP
_background_path = BASE_DIR / "ml_pipeline" / "data" / "gym_churn_us.csv"
_df_background   = pd.read_csv(_background_path)

# Calcular caida_frecuencia con la nueva lógica normalizada
_caida_frecuencia = (_df_background['Avg_class_frequency_total'] - _df_background['Avg_class_frequency_current_month']) / _df_background['Avg_class_frequency_total'].replace(0, np.nan)
_df_background['caida_frecuencia'] = _caida_frecuencia.fillna(0)

# Preparar columnas iguales a entrenamiento
_X_background = _df_background.drop(columns=['Churn', 'Avg_class_frequency_total', 'Phone', 'gender'])
_background_procesado = preprocesador.transform(_X_background)
_columnas_features = list(_X_background.columns)

# Crear explainer con muestra del background
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

        # Calcular caida_frecuencia con manejo de división por cero
        if 'Avg_class_frequency_total' in cliente_limpio and 'Avg_class_frequency_current_month' in cliente_limpio:
            total_freq = cliente_limpio['Avg_class_frequency_total']
            if total_freq != 0:
                cliente_limpio['caida_frecuencia'] = (total_freq - cliente_limpio['Avg_class_frequency_current_month']) / total_freq
            else:
                cliente_limpio['caida_frecuencia'] = 0

        df_cliente = pd.DataFrame([cliente_limpio])
        df_cliente = df_cliente[columnas_orden]
        datos_procesados = preprocesador.transform(df_cliente)

        input_tensor = torch.tensor(datos_procesados, dtype=torch.float32)

        modelo.eval()
        with torch.no_grad():
            output = modelo(input_tensor)
            prediccion = torch.argmax(output, dim=1)
            probabilidad = torch.softmax(output, dim=1).squeeze()
            prob_abandono = probabilidad[1].item()
        
        if prediccion == 1:
            # Calcular SHAP values para este cliente
            shap_values = explainer.shap_values(datos_procesados)

            # Tomar de forma robusta la explicación de la clase abandono
            shap_clase_1 = _obtener_shap_clase_abandono(shap_values)
            
            # Obtener índices de los 2 features con mayor impacto (valor absoluto)
            top_2_indices = np.argsort(np.abs(shap_clase_1))[-2:][::-1]  # descending
            
            features_principales = [
                {
                    "feature": _columnas_features[idx],
                    "impacto": float(shap_clase_1[idx]),
                    "valor": float(datos_procesados[0, idx])
                }
                for idx in top_2_indices
            ]
            
            resultados.append({
                "cliente_id":              int(cliente_id),
                "prediccion":              int(prediccion.item()),
                "probabilidad_abandono":   prob_abandono,
                "features_principales":    features_principales,
            })

    return resultados