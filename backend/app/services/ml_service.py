import joblib

modelo = joblib.load("modelo_rf.pkl")

def predecir_abandono(clientes):
    resultados = []
    for cliente in clientes:
        modelo.predict(cliente)
        probabilidad = modelo.predict_proba(cliente)[0][1]
        resultados.append(
            {
                "cliente_id": cliente["cliente_id"],
                "probabilidad_abandono": probabilidad
            }
        )
    return resultados