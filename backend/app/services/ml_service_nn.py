import pandas as pd
from sklearn.model_selection import train_test_split

def predecir_abandono(clientes):
    resultados = []
    
    df = pd.read_csv('../data/gym_churn_us.csv')
    df['caida_frecuencia'] = df['Avg_class_frequency_total'] - df['Avg_class_frequency_current_month']
    X = df.drop(columns=['Churn', 'Avg_class_frequency_total', 'Phone', 'gender'])
    y = df['Churn']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)