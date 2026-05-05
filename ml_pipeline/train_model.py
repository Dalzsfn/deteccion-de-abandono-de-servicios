import pandas as pd
import joblib 
from sklearn.ensemble import RandomForestClassifier

def entrenar_modelo():
    df = pd.read_csv('data/gym_churn_us.csv')
    caida_frecuencia = df['Avg_class_frequency_total'] - df['Avg_class_frequency_current_month']
    df['caida_frecuencia'] = caida_frecuencia
    X = df.drop(columns=['Churn', 'Age', 'Avg_class_frequency_total'])
    y = df['Churn']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)