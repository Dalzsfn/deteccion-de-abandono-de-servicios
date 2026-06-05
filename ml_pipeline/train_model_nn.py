import pandas as pd
from pathlib import Path
import torch
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from torch import nn, optim
from imblearn.over_sampling import SMOTE
from torch.utils.data import TensorDataset, DataLoader


class RedPrediccionChurn(nn.Module):
    def __init__(self, input_dim):
        super(RedPrediccionChurn, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 10),
            nn.ReLU(),
            nn.Dropout(0.1), 
            
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(5, 2),
            
        )
        
    def forward(self, x):
        return self.network(x)


num_caracteristicas = 11 
modelo = RedPrediccionChurn(input_dim=num_caracteristicas)

optimizador = optim.Adam(modelo.parameters(), lr=0.001)
criterio = nn.CrossEntropyLoss()

def entrenar_modelo():
    directorio_actual = Path(__file__).resolve().parent
    ruta_datos = directorio_actual / 'data' / 'gym_churn_us.csv'

    df = pd.read_csv(ruta_datos)
    
    caida_frecuencia = df['Avg_class_frequency_total'] - df['Avg_class_frequency_current_month']
    df['caida_frecuencia'] = caida_frecuencia
    X = df.drop(columns=['Churn', 'Avg_class_frequency_total', 'Phone', 'gender'])
    y = df['Churn']
    
    
    columnas_campana = ['Age','Avg_class_frequency_current_month', 'caida_frecuencia']
    columnas_sesgadas_o_fijas = ['Lifetime', 'Avg_additional_charges_total', 'Contract_period', 'Month_to_end_contract']
    
    preprocesador = ColumnTransformer(
    transformers=[
        ('estandarizacion', StandardScaler(), columnas_campana),
        ('normalizacion', MinMaxScaler(), columnas_sesgadas_o_fijas)
    ],
    remainder='passthrough' )
    
    X_escalado = preprocesador.fit_transform(X)
    
    smote = SMOTE()
    X_smote, y_smote = smote.fit_resample(X_escalado, y)
    y = pd.get_dummies(y_smote)
    
    X_train_tensor = torch.tensor(X_smote, dtype=torch.float32)
    y_train_tensor = torch.tensor(y.values, dtype=torch.long)
    
    BATCH_SIZE = 64
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    EPOCHS = 45

    for epoch in range(EPOCHS):
        modelo.train() 
        loss_acumulada = 0.0
        for lote_X, lote_y in train_loader:
            optimizador.zero_grad()
            predicciones = modelo(lote_X)
            loss = criterion(predicciones, lote_y)
            loss.backward()
            optimizador.step()
            loss_acumulada += loss.item() * lote_X.size(0)
        
        loss_total_epoca = loss_acumulada / len(train_loader.dataset)
        

        if (epoch + 1) % 5 == 0 or epoch == 0:
            modelo.eval() 
            with torch.no_grad():
                pred_val = modelo(X_val_tensor)
                clases_predichas = torch.argmax(pred_val, dim=1) 
                accuracy = (clases_predichas.float() == y_val_tensor.flatten()).float().mean()
    