import pandas as pd
import numpy as np
from pathlib import Path
import torch
from sklearn.preprocessing import StandardScaler
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


def entrenar_modelo():
    directorio_actual = Path(__file__).resolve().parent
    ruta_datos = directorio_actual / 'data' / 'gym_churn_us.csv'

    df = pd.read_csv(ruta_datos)

    caida_frecuencia = (df['Avg_class_frequency_total'] - df['Avg_class_frequency_current_month']) / df['Avg_class_frequency_total'].replace(0, np.nan)
    df['caida_frecuencia'] = caida_frecuencia.fillna(0)   
    X = df.drop(columns=['Churn', 'Avg_class_frequency_total', 'Phone', 'gender'])
    y = df['Churn']


    columnas_orden = list(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=100,
        stratify=y,
    )

    preprocesador = StandardScaler()
    X_train = preprocesador.fit_transform(X_train)
    X_test = preprocesador.transform(X_test)

    smote = SMOTE(random_state=42)
    X_balanceado, y_balanceado = smote.fit_resample(X_train, y_train)
    
    X_tensor = torch.tensor(X_balanceado, dtype=torch.float32)
    y_tensor = torch.tensor(y_balanceado.values, dtype=torch.long)  

    BATCH_SIZE = 64
    dataset     = TensorDataset(X_tensor, y_tensor)
    train_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    num_caracteristicas = X_tensor.shape[1]
    modelo      = RedPrediccionChurn(input_dim=num_caracteristicas)
    optimizador = optim.Adam(modelo.parameters(), lr=0.001)
    criterio    = nn.CrossEntropyLoss()

    EPOCHS = 45


    for epoch in range(EPOCHS):
        modelo.train() 
        loss_acumulada = 0.0
        for lote_X, lote_y in train_loader:
            optimizador.zero_grad()
            predicciones = modelo(lote_X)
            loss = criterio(predicciones, lote_y)
            loss.backward()
            optimizador.step()
            loss_acumulada += loss.item() * lote_X.size(0)
        
        loss_total_epoca = loss_acumulada / len(train_loader.dataset)

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:>3}/{EPOCHS} | Loss: {loss_total_epoca:.4f}")

    ruta_modelo = directorio_actual / 'modelo_churn.pth'
    torch.save({
        'model_state_dict':      modelo.state_dict(),
        'optimizer_state_dict':  optimizador.state_dict(),
        'input_dim':             num_caracteristicas,
        'preprocesador':         preprocesador,
        'columnas_orden':        columnas_orden,
    }, ruta_modelo)
    print(f"Modelo guardado en: {ruta_modelo}")

    return modelo, preprocesador


if __name__ == '__main__':
    entrenar_modelo()