export const API_BASE = "http://127.0.0.1:8000";

export const ENDPOINTS = {
  clientes:          `${API_BASE}/api/clientes/clientes`,
  predicciones:      `${API_BASE}/api/ml/predicciones`,
  detalle:           (clienteId) => `${API_BASE}/api/ml/predicciones/${clienteId}`,

  enviarSugerencia:  (clienteId) => `${API_BASE}/api/telegram/enviar-sugerencia/${clienteId}`,
  sugerenciasEnviadas: `${API_BASE}/api/telegram/sugerencias-enviadas`,
};
