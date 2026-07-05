const RISK_ICONS = {
  pendiente: `<svg class="risk-badge__icon" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="3 2"/></svg>`,
  bajo: `<svg class="risk-badge__icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 9l3.5 3.5L13 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  medio: `<svg class="risk-badge__icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>`,
  alto: `<svg class="risk-badge__icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3v6M8 12v1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`,
};

const RISK_LABELS = {
  pendiente: "Sin evaluar",
  bajo: "Riesgo bajo",
  medio: "Riesgo medio",
  alto: "Riesgo alto",
};

const TELEGRAM_SVG = `<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">
  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/>
</svg>`;

const CHECK_SVG = `<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor" width="20" height="20">
  <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
</svg>`;

export function deriveMembership(cliente) {
  const monthsLeft = Number(cliente.Month_to_end_contract ?? 0);
  const contractMonths = Number(cliente.Contract_period ?? 0);

  if (monthsLeft <= 0) {
    return { label: "Por vencer", expiring: true, detail: "Contrato al límite" };
  }

  if (monthsLeft <= 1) {
    return {
      label: "Activa",
      expiring: true,
      detail: `${monthsLeft} mes restante · plan ${contractMonths}m`,
    };
  }

  return {
    label: "Activa",
    expiring: false,
    detail: `${monthsLeft} meses restantes · plan ${contractMonths}m`,
  };
}

export function renderRiskBadge(level) {
  return `
    <div class="risk-badge" data-level="${level}">
      <span class="risk-badge__label">
        ${RISK_ICONS[level] ?? RISK_ICONS.pendiente}
        ${RISK_LABELS[level] ?? RISK_LABELS.pendiente}
      </span>
      <div class="risk-badge__track" aria-hidden="true">
        <span class="risk-badge__segment"></span>
        <span class="risk-badge__segment"></span>
        <span class="risk-badge__segment"></span>
      </div>
    </div>
  `;
}

export function renderClientCard(cliente, riskLevel = "pendiente") {
  const membership = deriveMembership(cliente);
  const expiringClass = membership.expiring ? " is-expiring" : "";

  return `
    <button
      type="button"
      class="client-card"
      data-client-id="${cliente.cliente_id}"
      data-risk="${riskLevel}"
      aria-label="Ver detalle de ${cliente.nombre}"
    >
      <div class="client-card__head">
        <div>
          <h3 class="client-card__name">${cliente.nombre}</h3>
          <p class="client-card__meta">${membership.detail}</p>
        </div>
        <span class="membership-tag${expiringClass}">${membership.label}</span>
      </div>
      ${renderRiskBadge(riskLevel)}
    </button>
  `;
}

export function renderClientsGrid(clientes, riskMap, query = "") {
  const normalizedQuery = query.trim().toLowerCase();

  const filtered = clientes.filter((c) =>
    c.nombre.toLowerCase().includes(normalizedQuery)
  );

  if (filtered.length === 0) {
    return { html: "", count: 0, visible: 0 };
  }

  const html = filtered
    .map((cliente) => {
      const risk = riskMap.get(cliente.cliente_id) ?? "pendiente";
      return renderClientCard(cliente, risk);
    })
    .join("");

  return { html, count: clientes.length, visible: filtered.length };
}

function formatBool(value) {
  return value ? "Sí" : "No";
}

function formatNumber(value, suffix = "") {
  const num = Number(value);
  if (Number.isNaN(num)) return "—";
  return `${num}${suffix}`;
}

/** Escapa caracteres especiales para uso seguro dentro de atributos HTML. */
function escapeAttr(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

/**
 * Renderiza el contenido del modal para un cliente en riesgo.
 * @param {object} cliente   - Datos completos del cliente desde la vista
 * @param {object} detalle   - Respuesta de GET /api/ml/predicciones/{id}
 * @param {boolean} yaEnviada - True si ya hay una sugerencia enviada para este cliente
 */
export function renderDetalleContent(cliente, detalle, yaEnviada = false) {
  const membership = deriveMembership(cliente);
  const probPct = Math.round(detalle.probabilidad_abandono * 100);
  const features = detalle.features_principales ?? [];

  const featuresHtml = features
    .map((f) => `<li class="feature-chip">${f.feature_legible}</li>`)
    .join("");

  const telegramBtnHtml = yaEnviada
    ? `<button type="button" class="btn btn-telegram is-sent" id="telegramBtn" disabled>
        ${CHECK_SVG}
        ✓ Ya enviada
       </button>`
    : `<button type="button" class="btn btn-telegram" id="telegramBtn"
          data-cliente-id="${cliente.cliente_id}"
          data-mensaje="${escapeAttr(detalle.sugerencia_retencion)}">
        ${TELEGRAM_SVG}
        Enviar promoción por Telegram
       </button>`;

  return `
    <div class="score-block">
      <div class="score-block__header">
        <span class="dialog-kicker">Probabilidad de abandono</span>
        <span class="score-value">${probPct}%</span>
      </div>
      <div class="score-bar" role="meter" aria-valuenow="${probPct}" aria-valuemin="0" aria-valuemax="100">
        <div class="score-bar__fill" style="width: ${probPct}%"></div>
      </div>
      ${renderRiskBadge("alto")}
    </div>

    <dl class="info-grid">
      <div class="info-item">
        <dt>Membresía</dt>
        <dd>${membership.label} — ${membership.detail}</dd>
      </div>
      <div class="info-item">
        <dt>Edad</dt>
        <dd>${formatNumber(cliente.Age, " años")}</dd>
      </div>
      <div class="info-item">
        <dt>Antigüedad</dt>
        <dd>${formatNumber(cliente.Lifetime, " meses")}</dd>
      </div>
      <div class="info-item">
        <dt>Frecuencia (mes)</dt>
        <dd>${formatNumber(cliente.Avg_class_frequency_current_month, " /sem")}</dd>
      </div>
      <div class="info-item">
        <dt>Cerca del gym</dt>
        <dd>${formatBool(cliente.Near_Location)}</dd>
      </div>
      <div class="info-item">
        <dt>Clases grupales</dt>
        <dd>${formatBool(cliente.Group_visits)}</dd>
      </div>
    </dl>

    <section class="features-list">
      <h3>Factores principales</h3>
      <ul>${featuresHtml || "<li class='feature-chip'>Sin datos SHAP</li>"}</ul>
    </section>

    <section class="action-block">
      <h3>Acción recomendada</h3>
      <p>${detalle.sugerencia_retencion}</p>
      ${telegramBtnHtml}
    </section>
  `;
}

export function renderStableContent(cliente) {
  const membership = deriveMembership(cliente);

  return `
    <div class="stable-notice">
      <strong>${cliente.nombre}</strong> no fue clasificado en riesgo de abandono tras la última ejecución del modelo.
      No se requieren acciones de retención por ahora.
    </div>

    <dl class="info-grid">
      <div class="info-item">
        <dt>Membresía</dt>
        <dd>${membership.label} — ${membership.detail}</dd>
      </div>
      <div class="info-item">
        <dt>Edad</dt>
        <dd>${formatNumber(cliente.Age, " años")}</dd>
      </div>
      <div class="info-item">
        <dt>Antigüedad</dt>
        <dd>${formatNumber(cliente.Lifetime, " meses")}</dd>
      </div>
      <div class="info-item">
        <dt>Frecuencia (mes)</dt>
        <dd>${formatNumber(cliente.Avg_class_frequency_current_month, " /sem")}</dd>
      </div>
    </dl>

    ${renderRiskBadge("bajo")}
  `;
}

export function renderSugerenciasEnviadas(sugerencias) {
  if (sugerencias.length === 0) {
    return `<p class="sent-empty">Todavía no se ha enviado ninguna sugerencia.</p>`;
  }

  const rows = sugerencias
    .map((s) => {
      const fecha = new Date(s.fecha_envio).toLocaleString("es-EC", {
        dateStyle: "short",
        timeStyle: "short",
      });
      return `
        <li class="sent-row">
          <div class="sent-row__name">${s.nombre}</div>
          <div class="sent-row__msg">${s.mensaje_enviado}</div>
          <time class="sent-row__date" datetime="${s.fecha_envio}">${fecha}</time>
        </li>
      `;
    })
    .join("");

  return `<ul class="sent-list">${rows}</ul>`;
}

export function showToast(message, durationMs = 2400) {
  const stack = document.getElementById("toastStack");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  stack.appendChild(toast);
  setTimeout(() => toast.remove(), durationMs);
}

export function setAlert(message, type = "error") {
  const banner = document.getElementById("alertBanner");
  if (!message) {
    banner.hidden = true;
    banner.textContent = "";
    return;
  }
  banner.hidden = false;
  banner.textContent = message;
  banner.dataset.type = type;
}

export function withViewTransition(callback) {
  if (
    document.startViewTransition &&
    !window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    document.startViewTransition(callback);
    return;
  }
  callback();
}
