/* ============================================================
   main.js – Öğretmen Materyali Üretici
   ============================================================ */

"use strict";

// ── Loading overlay ──────────────────────────────────────────
function showLoading(message) {
  const overlay = document.getElementById("loading-overlay");
  if (!overlay) return;
  const txt = overlay.querySelector(".spinner-text");
  if (txt) txt.textContent = message || "Yükleniyor...";
  overlay.classList.add("active");
}

function hideLoading() {
  const overlay = document.getElementById("loading-overlay");
  if (overlay) overlay.classList.remove("active");
}

// ── Toast notifications ───────────────────────────────────────
function showToast(message, type) {
  type = type || "info";
  const container = document.getElementById("toast-container");
  if (!container) return;

  const colorMap = {
    success: "bg-success",
    error: "bg-danger",
    warning: "bg-warning text-dark",
    info: "bg-primary",
  };
  const bgClass = colorMap[type] || colorMap.info;

  const id = "toast-" + Date.now();
  const html = `
    <div id="${id}" class="toast align-items-center text-white ${bgClass} border-0 mb-2" role="alert" aria-live="assertive">
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>`;
  container.insertAdjacentHTML("beforeend", html);
  const toastEl = document.getElementById(id);
  const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
  toast.show();
  toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
}

// ── Today / Tomorrow detection ────────────────────────────────
const TR_DAYS = [
  "Pazar",
  "Pazartesi",
  "Salı",
  "Çarşamba",
  "Perşembe",
  "Cuma",
  "Cumartesi",
];

function getTodayTomorrow() {
  const now = new Date();
  const todayIdx = now.getDay(); // 0=Sun
  const tomorrowIdx = (todayIdx + 1) % 7;
  return { today: TR_DAYS[todayIdx], tomorrow: TR_DAYS[tomorrowIdx] };
}

function highlightScheduleDays() {
  const { today, tomorrow } = getTodayTomorrow();
  document.querySelectorAll("[data-day]").forEach((el) => {
    const day = el.getAttribute("data-day");
    if (day === today) {
      el.classList.add("col-today");
      const header = el.querySelector(".day-header");
      if (header) header.classList.add("today-header");
    } else if (day === tomorrow) {
      el.classList.add("col-tomorrow");
      const header = el.querySelector(".day-header");
      if (header) header.classList.add("tomorrow-header");
    }
  });
  // Also highlight table column headers
  document.querySelectorAll("th[data-day]").forEach((th) => {
    const day = th.getAttribute("data-day");
    if (day === today) th.classList.add("today-header");
    else if (day === tomorrow) th.classList.add("tomorrow-header");
  });
}

// ── Drag & Drop File Upload ───────────────────────────────────
function initDropZone(dropZoneId, fileInputId, labelId) {
  const dropZone = document.getElementById(dropZoneId);
  const fileInput = document.getElementById(fileInputId);
  if (!dropZone || !fileInput) return;

  dropZone.addEventListener("click", () => fileInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      updateFileLabel(labelId, files[0].name);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      updateFileLabel(labelId, fileInput.files[0].name);
    }
  });
}

function updateFileLabel(labelId, filename) {
  const label = document.getElementById(labelId);
  if (label) {
    label.textContent = filename;
    label.classList.add("text-success", "fw-semibold");
  }
}

// ── Plan Upload Form ──────────────────────────────────────────
function initUploadForm() {
  const form = document.getElementById("upload-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("plan-file");
    if (!fileInput || !fileInput.files.length) {
      showToast("Lütfen bir dosya seçin.", "warning");
      return;
    }
    const formData = new FormData(form);
    showLoading("Dosya yükleniyor ve işleniyor...");
    try {
      const resp = await fetch("/upload-plan", { method: "POST", body: formData });
      const data = await resp.json();
      if (data.success) {
        showToast(`✅ ${data.message}`, "success");
        setTimeout(() => location.reload(), 1500);
      } else {
        showToast("❌ " + (data.error || "Hata oluştu"), "error");
      }
    } catch (err) {
      showToast("❌ Sunucu hatası: " + err.message, "error");
    } finally {
      hideLoading();
    }
  });
}

// ── Schedule Management ───────────────────────────────────────
function initSchedule() {
  const addForm = document.getElementById("add-lesson-form");
  if (!addForm) return;

  addForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const day = document.getElementById("lesson-day").value;
    const timeSlot = document.getElementById("lesson-time").value.trim();
    const subject = document.getElementById("lesson-subject").value.trim();

    if (!day || !timeSlot || !subject) {
      showToast("Lütfen tüm alanları doldurun.", "warning");
      return;
    }

    showLoading("Kaydediliyor...");
    try {
      const resp = await fetch("/api/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ day_of_week: day, time_slot: timeSlot, subject_name: subject }),
      });
      const data = await resp.json();
      if (data.success) {
        showToast("✅ Ders eklendi", "success");
        addForm.reset();
        setTimeout(() => location.reload(), 800);
      } else {
        showToast("❌ " + (data.error || "Hata"), "error");
      }
    } catch (err) {
      showToast("❌ " + err.message, "error");
    } finally {
      hideLoading();
    }
  });
}

async function deleteScheduleEntry(entryId) {
  if (!confirm("Bu dersi silmek istiyor musunuz?")) return;
  showLoading("Siliniyor...");
  try {
    const resp = await fetch(`/api/schedule/${entryId}`, { method: "DELETE" });
    const data = await resp.json();
    if (data.success) {
      showToast("✅ Ders silindi", "success");
      setTimeout(() => location.reload(), 600);
    } else {
      showToast("❌ " + (data.error || "Hata"), "error");
    }
  } catch (err) {
    showToast("❌ " + err.message, "error");
  } finally {
    hideLoading();
  }
}

// ── Material Generation ───────────────────────────────────────
function initGenerateForm() {
  const form = document.getElementById("generate-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const subject = document.getElementById("gen-subject").value.trim();
    const topic = document.getElementById("gen-topic").value.trim();
    const outcomes = document.getElementById("gen-outcomes").value.trim();

    const types = [];
    document.querySelectorAll(".material-type-checkbox:checked").forEach((cb) => {
      types.push(cb.value);
    });

    if (!subject || !topic) {
      showToast("Lütfen ders adı ve konu giriniz.", "warning");
      return;
    }
    if (types.length === 0) {
      showToast("Lütfen en az bir materyal türü seçiniz.", "warning");
      return;
    }

    showLoading("Materyaller üretiliyor... Bu işlem biraz zaman alabilir.");

    try {
      const resp = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject,
          topic,
          learning_outcomes: outcomes,
          material_types: types,
        }),
      });
      const data = await resp.json();
      if (data.success) {
        showToast("✅ Materyaller başarıyla üretildi!", "success");
        renderGeneratedMaterials(data.materials);
      } else {
        showToast("❌ " + (data.error || "Hata"), "error");
      }
    } catch (err) {
      showToast("❌ " + err.message, "error");
    } finally {
      hideLoading();
    }
  });
}

function renderGeneratedMaterials(materials) {
  const container = document.getElementById("generated-results");
  if (!container) return;
  container.innerHTML = "";
  container.classList.remove("d-none");

  // All labels come from a hardcoded map (safe); id is always an integer from the server
  const typeLabels = {
    flashcards: "Bilgi Kartları",
    presentation: "Sunum",
    test: "Test",
    notes: "Öğretmen Notları",
  };

  for (const [mtype, info] of Object.entries(materials)) {
    const label = typeLabels[mtype] || mtype;
    const id = parseInt(info.id, 10); // Ensure integer, never a raw string
    const col = document.createElement("div");
    col.className = "col-md-6 mb-3";

    const card = document.createElement("div");
    card.className = "card h-100";
    const body = document.createElement("div");
    body.className = "card-body text-center py-4";

    const icon = document.createElement("i");
    icon.className = "bi bi-check-circle-fill text-success fs-2 mb-2 d-block";

    const title = document.createElement("h5");
    title.className = "card-title";
    title.textContent = label;

    const idPara = document.createElement("p");
    idPara.className = "text-muted small";
    idPara.textContent = `Materyal ID: ${id}`;

    const previewLink = document.createElement("a");
    previewLink.href = `/preview/${id}`;
    previewLink.className = "btn btn-primary btn-sm me-1";
    previewLink.innerHTML = '<i class="bi bi-eye"></i> Önizle';

    const pdfLink = document.createElement("a");
    pdfLink.href = `/download/${id}/pdf`;
    pdfLink.className = "btn btn-outline-danger btn-sm";
    pdfLink.innerHTML = '<i class="bi bi-file-earmark-pdf"></i> PDF';

    body.appendChild(icon);
    body.appendChild(title);
    body.appendChild(idPara);
    body.appendChild(previewLink);
    body.appendChild(pdfLink);
    card.appendChild(body);
    col.appendChild(card);
    container.appendChild(col);
  }
}

// ── Flashcard Flip ────────────────────────────────────────────
function initFlashcards() {
  document.querySelectorAll(".flashcard-scene").forEach((scene) => {
    scene.addEventListener("click", () => {
      scene.querySelector(".flashcard").classList.toggle("flipped");
    });
  });
}

// ── Material type checkbox styling ────────────────────────────
function initMaterialTypeChecks() {
  document.querySelectorAll(".material-type-checkbox").forEach((cb) => {
    const card = cb.closest(".material-type-check");
    if (!card) return;

    // Set initial state
    if (cb.checked) card.classList.add("checked");

    cb.addEventListener("change", () => {
      if (cb.checked) card.classList.add("checked");
      else card.classList.remove("checked");
    });

    // Allow clicking the card to toggle checkbox
    card.addEventListener("click", (e) => {
      if (e.target === cb) return;
      cb.checked = !cb.checked;
      cb.dispatchEvent(new Event("change"));
    });
  });
}

// ── Plan preview ──────────────────────────────────────────────
async function loadPlanPreview(planId) {
  const container = document.getElementById("plan-preview-container");
  if (!container) return;
  showLoading("Plan yükleniyor...");
  try {
    const resp = await fetch(`/api/plans/${planId}`);
    const plan = await resp.json();
    if (plan.error) {
      container.innerHTML = `<div class="alert alert-danger">${plan.error}</div>`;
      return;
    }
    renderPlanTable(container, plan);
  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Hata: ${err.message}</div>`;
  } finally {
    hideLoading();
  }
}

function renderPlanTable(container, plan) {
  const entries = plan.entries || [];
  if (!entries.length) {
    container.innerHTML = '<div class="alert alert-info">Bu planda kayıt bulunmuyor.</div>';
    return;
  }
  let html = `<h6>📋 ${plan.filename} - ${plan.subject} (${plan.year})</h6>
    <div class="table-responsive"><table class="table table-sm table-bordered plan-entry-table">
    <thead><tr>
      <th>Hafta</th><th>Ünite/Konu</th><th>Kazanımlar</th>
      <th>Öğretim Yönt.</th><th>Araç-Gereç</th><th>Değerlendirme</th><th>Özel Günler</th>
    </tr></thead><tbody>`;
  entries.forEach((e) => {
    html += `<tr>
      <td>${e.week_number || ""}</td>
      <td>${e.unit_topic || ""}</td>
      <td>${e.learning_outcomes || ""}</td>
      <td>${e.teaching_techniques || ""}</td>
      <td>${e.tools_equipment || ""}</td>
      <td>${e.assessment || ""}</td>
      <td>${e.special_days || ""}</td>
    </tr>`;
  });
  html += "</tbody></table></div>";
  container.innerHTML = html;
}

// ── DOM Ready ─────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  highlightScheduleDays();
  initDropZone("upload-dropzone", "plan-file", "file-name-label");
  initUploadForm();
  initSchedule();
  initGenerateForm();
  initFlashcards();
  initMaterialTypeChecks();

  // Auto-activate Bootstrap tooltips
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach((el) => new bootstrap.Tooltip(el));
});
