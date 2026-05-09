import pandas as pd
import joblib 
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

def entrenar_modelo():
    directorio_actual = Path(__file__).resolve().parent
    ruta_datos = directorio_actual / 'data' / 'gym_churn_us.csv'
    
    # Cargar los datos
    df = pd.read_csv(ruta_datos)
    
    caida_frecuencia = df['Avg_class_frequency_total'] - df['Avg_class_frequency_current_month']
    df['caida_frecuencia'] = caida_frecuencia
    X = df.drop(columns=['Churn', 'Avg_class_frequency_total', 'Phone', 'gender'])
    y = df['Churn']
    
    # Entrenamiento del modelo 
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Guardar el modelo entrenado
    ruta_modelo = directorio_actual / 'modelo_rf.pkl'
    joblib.dump(model, ruta_modelo)
    
if __name__ == "__main__":   
    entrenar_modelo()