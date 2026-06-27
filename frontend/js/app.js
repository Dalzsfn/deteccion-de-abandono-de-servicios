import { fetchClientes, runPredicciones, fetchDetallePrediccion } from "./api.js";
import {
  renderClientsGrid,
  renderDetalleContent,
  renderStableContent,
  setAlert,
  withViewTransition,
  bindTelegramButton,
} from "./ui.js";

const state = {
  clientes: [],
  riskMap: new Map(),
  modelExecuted: false,
  searchQuery: "",
  isRunningModel: false,
};

const els = {
  clientsGrid: document.getElementById("clientsGrid"),
  clientsPanel: document.getElementById("clientsPanel"),
  panelLoading: document.getElementById("panelLoading"),
  emptyState: document.getElementById("emptyState"),
  searchInput: document.getElementById("searchInput"),
  runModelBtn: document.getElementById("runModelBtn"),
  modelStatus: document.getElementById("modelStatus"),
  clientCount: document.getElementById("clientCount"),
  riskCount: document.getElementById("riskCount"),
  detailDialog: document.getElementById("detailDialog"),
  closeDialogBtn: document.getElementById("closeDialogBtn"),
  dialogTitle: document.getElementById("dialogTitle"),
  dialogLoading: document.getElementById("dialogLoading"),
  dialogContent: document.getElementById("dialogContent"),
};

function updateMeta() {
  const atRisk = [...state.riskMap.values()].filter((r) => r === "alto").length;
  const displayed = state.modelExecuted ? atRisk : state.clientes.length;
  els.clientCount.textContent = state.modelExecuted
    ? `${displayed} socios en riesgo`
    : `${displayed} socios`;
  els.riskCount.textContent = state.modelExecuted
    ? `de ${state.clientes.length} totales`
    : "— en riesgo";
}

function updateModelStatus(mode) {
  const dot = els.modelStatus.querySelector(".status-dot");
  const label = els.modelStatus.querySelector("span:last-child");

  dot.className = "status-dot";
  els.runModelBtn.classList.remove("is-running");

  if (mode === "running") {
    dot.classList.add("is-running");
    label.textContent = "Ejecutando modelo…";
    els.runModelBtn.classList.add("is-running");
    els.runModelBtn.disabled = true;
    els.runModelBtn.innerHTML = `
      <span class="loader-bars" aria-hidden="true"><span></span><span></span><span></span><span></span></span>
      Analizando…
    `;
    return;
  }

  els.runModelBtn.disabled = false;
  els.runModelBtn.innerHTML = `
    <span class="btn-icon" aria-hidden="true">▶</span>
    Ejecutar modelo
  `;

  if (mode === "ready") {
    dot.classList.add("is-ready");
    label.textContent = "Modelo ejecutado";
  } else {
    label.textContent = "Modelo sin ejecutar";
  }
}

function getDisplayedClients() {
  if (!state.modelExecuted) return state.clientes;
  return state.clientes.filter(
    (c) => state.riskMap.get(c.cliente_id) === "alto"
  );
}

function paintGrid() {
  const displayClients = getDisplayedClients();
  const { html, visible } = renderClientsGrid(
    displayClients,
    state.riskMap,
    state.searchQuery
  );

  const render = () => {
    if (visible === 0 && displayClients.length > 0) {
      els.clientsGrid.hidden = true;
      els.emptyState.hidden = false;
    } else if (displayClients.length === 0 && state.modelExecuted) {
      els.clientsGrid.hidden = true;
      els.emptyState.hidden = false;
      els.emptyState.textContent = "No se detectaron socios en riesgo de abandono.";
    } else {
      els.emptyState.hidden = true;
      els.clientsGrid.hidden = false;
      els.clientsGrid.innerHTML = html;
    }
    updateMeta();
  };

  withViewTransition(render);
}

async function loadClientes() {
  els.panelLoading.hidden = false;
  els.clientsGrid.hidden = true;
  els.emptyState.hidden = true;
  setAlert(null);

  try {
    state.clientes = await fetchClientes();
    els.panelLoading.hidden = true;
    paintGrid();
  } catch (error) {
    els.panelLoading.hidden = true;
    setAlert(`No se pudieron cargar los socios: ${error.message}`);
  }
}

async function handleRunModel() {
  if (state.isRunningModel) return;

  state.isRunningModel = true;
  setAlert(null);
  updateModelStatus("running");

  try {
    const result = await runPredicciones();
    const atRiskIds = new Set(
      (result.clientes_en_riesgo ?? []).map((c) => c.cliente_id)
    );

    state.riskMap.clear();
    for (const cliente of state.clientes) {
      state.riskMap.set(
        cliente.cliente_id,
        atRiskIds.has(cliente.cliente_id) ? "alto" : "bajo"
      );
    }

    state.modelExecuted = true;
    updateModelStatus("ready");
    paintGrid();
    setAlert(
      `Modelo completado: ${atRiskIds.size} socio(s) en riesgo de abandono.`,
      "info"
    );
  } catch (error) {
    updateModelStatus(state.modelExecuted ? "ready" : "idle");
    setAlert(`Error al ejecutar el modelo: ${error.message}`);
  } finally {
    state.isRunningModel = false;
  }
}

function showDialogLoading(title) {
  els.dialogTitle.textContent = title;
  els.dialogLoading.hidden = false;
  els.dialogContent.hidden = true;
  els.dialogContent.innerHTML = "";
}

function showDialogContent(title, html) {
  els.dialogTitle.textContent = title;
  els.dialogLoading.hidden = true;
  els.dialogContent.hidden = false;
  els.dialogContent.innerHTML = html;
  bindTelegramButton();
}

async function openClientDetail(clienteId) {
  const cliente = state.clientes.find((c) => c.cliente_id === clienteId);
  if (!cliente) return;

  const risk = state.riskMap.get(clienteId) ?? "pendiente";
  const open = () => els.detailDialog.showModal();

  if (
    document.startViewTransition &&
    !window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    document.startViewTransition(open);
  } else {
    open();
  }

  showDialogLoading(cliente.nombre);

  if (!state.modelExecuted) {
    showDialogContent(
      cliente.nombre,
      `<div class="stable-notice">Ejecuta el modelo primero para evaluar el riesgo de abandono de este socio.</div>`
    );
    return;
  }

  if (risk !== "alto") {
    showDialogContent(cliente.nombre, renderStableContent(cliente));
    return;
  }

  try {
    const detalle = await fetchDetallePrediccion(clienteId);
    showDialogContent(cliente.nombre, renderDetalleContent(cliente, detalle));
  } catch (error) {
    showDialogContent(
      cliente.nombre,
      `<div class="stable-notice">No se pudo cargar el detalle: ${error.message}</div>`
    );
  }
}

function bindEvents() {
  els.runModelBtn.addEventListener("click", handleRunModel);

  els.searchInput.addEventListener("input", (event) => {
    state.searchQuery = event.target.value;
    paintGrid();
  });

  els.clientsGrid.addEventListener("click", (event) => {
    const card = event.target.closest(".client-card");
    if (!card) return;
    openClientDetail(Number(card.dataset.clientId));
  });

  els.closeDialogBtn.addEventListener("click", () => els.detailDialog.close());

  els.detailDialog.addEventListener("click", (event) => {
    const rect = els.detailDialog.getBoundingClientRect();
    const inDialog =
      event.clientX >= rect.left &&
      event.clientX <= rect.right &&
      event.clientY >= rect.top &&
      event.clientY <= rect.bottom;
    if (!inDialog) els.detailDialog.close();
  });

  els.detailDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    els.detailDialog.close();
  });
}

bindEvents();
loadClientes();
