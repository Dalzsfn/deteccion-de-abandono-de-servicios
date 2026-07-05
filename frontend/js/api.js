import { ENDPOINTS } from "./config.js";

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { Accept: "application/json", ...options.headers },
    ...options,
  });

  let payload = null;
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    payload = await response.json();
  } else {
    payload = await response.text();
  }

  if (!response.ok) {
    const detail =
      typeof payload === "object" && payload?.detail
        ? payload.detail
        : `Error ${response.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return payload;
}

export function fetchClientes() {
  return request(ENDPOINTS.clientes);
}

export function runPredicciones() {
  return request(ENDPOINTS.predicciones, { method: "POST" });
}

export function fetchDetallePrediccion(clienteId) {
  return request(ENDPOINTS.detalle(clienteId));
}

export function postEnviarSugerencia(clienteId, mensaje) {
  return request(ENDPOINTS.enviarSugerencia(clienteId), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mensaje }),
  });
}

export function fetchSugerenciasEnviadas() {
  return request(ENDPOINTS.sugerenciasEnviadas);
}
