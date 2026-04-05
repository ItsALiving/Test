const STORAGE_KEY = "careNotesEntries";

const entryForm = document.getElementById("entry-form");
const timeInput = document.getElementById("entry-time");
const categoryInput = document.getElementById("entry-category");
const titleInput = document.getElementById("entry-title");
const noteInput = document.getElementById("entry-note");
const saveButton = document.getElementById("save-button");
const cancelEditButton = document.getElementById("cancel-edit");
const formMessage = document.getElementById("form-message");

const entriesList = document.getElementById("entries-list");
const emptyState = document.getElementById("empty-state");
const entryCount = document.getElementById("entry-count");

const summaryButton = document.getElementById("generate-summary");
const summaryOutput = document.getElementById("summary-output");

let entries = [];
let editingEntryId = null;

initializeApp();

function initializeApp() {
  entries = loadEntries();
  renderEntries();
  prefillCurrentTime();

  entryForm.addEventListener("submit", handleFormSubmit);
  cancelEditButton.addEventListener("click", resetForm);
  entriesList.addEventListener("click", handleEntryAction);
  summaryButton.addEventListener("click", generateSummary);
}

function loadEntries() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];

    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveEntries() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

function handleFormSubmit(event) {
  event.preventDefault();
  clearFormMessage();

  const time = timeInput.value;
  const category = categoryInput.value.trim();
  const title = titleInput.value.trim();
  const note = noteInput.value.trim();

  if (!time || !category || !title || !note) {
    showFormMessage("Please complete all fields before saving.", true);
    return;
  }

  if (editingEntryId) {
    const index = entries.findIndex((entry) => entry.id === editingEntryId);
    if (index === -1) {
      showFormMessage("Unable to find the entry being edited.", true);
      resetForm();
      return;
    }

    entries[index] = {
      ...entries[index],
      time,
      category,
      title,
      note,
      updatedAt: Date.now()
    };

    showFormMessage("Entry updated.");
  } else {
    entries.push({
      id: crypto.randomUUID(),
      time,
      category,
      title,
      note,
      createdAt: Date.now()
    });

    showFormMessage("Entry added.");
  }

  saveEntries();
  renderEntries();
  resetForm(false);
}

function handleEntryAction(event) {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const entryItem = button.closest("li[data-entry-id]");
  if (!entryItem) return;

  const entryId = entryItem.dataset.entryId;
  const action = button.dataset.action;

  if (action === "edit") {
    beginEdit(entryId);
  }

  if (action === "delete") {
    deleteEntry(entryId);
  }
}

function beginEdit(entryId) {
  const entry = entries.find((item) => item.id === entryId);
  if (!entry) return;

  editingEntryId = entryId;
  timeInput.value = entry.time;
  categoryInput.value = entry.category;
  titleInput.value = entry.title;
  noteInput.value = entry.note;

  saveButton.textContent = "Save Changes";
  cancelEditButton.hidden = false;
  titleInput.focus();
}

function deleteEntry(entryId) {
  const entry = entries.find((item) => item.id === entryId);
  if (!entry) return;

  const confirmed = window.confirm(`Delete this entry: "${entry.title}"?`);
  if (!confirmed) return;

  entries = entries.filter((item) => item.id !== entryId);

  if (editingEntryId === entryId) {
    resetForm();
  }

  saveEntries();
  renderEntries();
  showFormMessage("Entry deleted.");
}

function renderEntries() {
  const sortedEntries = [...entries].sort((a, b) => a.time.localeCompare(b.time));

  entriesList.innerHTML = "";

  sortedEntries.forEach((entry) => {
    const listItem = document.createElement("li");
    listItem.className = "entry-item";
    listItem.dataset.entryId = entry.id;

    listItem.innerHTML = `
      <div class="entry-top">
        <div class="entry-heading">
          <span class="entry-time">${escapeHtml(formatTime(entry.time))}</span>
          <span class="entry-category">${escapeHtml(entry.category)}</span>
          <span class="entry-title">${escapeHtml(entry.title)}</span>
        </div>
      </div>
      <p class="entry-note">${escapeHtml(entry.note)}</p>
      <div class="entry-actions">
        <button type="button" class="secondary" data-action="edit">Edit</button>
        <button type="button" class="delete" data-action="delete">Delete</button>
      </div>
    `;

    entriesList.appendChild(listItem);
  });

  entryCount.textContent = `${entries.length} ${entries.length === 1 ? "entry" : "entries"}`;
  emptyState.hidden = entries.length > 0;
}

function generateSummary() {
  const sortedEntries = [...entries].sort((a, b) => a.time.localeCompare(b.time));

  if (!sortedEntries.length) {
    summaryOutput.value = "No entries are available for summary generation.";
    return;
  }

  const summaryLines = sortedEntries.map((entry) => {
    const cleanNote = normalizeSentence(entry.note);
    return `${formatTime(entry.time)} - ${entry.category}: ${entry.title}. ${cleanNote}`;
  });

  const firstTime = formatTime(sortedEntries[0].time);
  const lastTime = formatTime(sortedEntries[sortedEntries.length - 1].time);

  const intro = `Care notes for the shift document ${sortedEntries.length} events from ${firstTime} to ${lastTime}.`;
  const closing = "All information above is based on documented entries recorded during care.";

  summaryOutput.value = `${intro}\n\n${summaryLines.join("\n")}\n\n${closing}`;
}

function prefillCurrentTime() {
  if (editingEntryId || timeInput.value) return;

  const now = new Date();
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  timeInput.value = `${hours}:${minutes}`;
}

function resetForm(shouldClearMessage = true) {
  entryForm.reset();
  editingEntryId = null;
  saveButton.textContent = "Add Entry";
  cancelEditButton.hidden = true;
  prefillCurrentTime();

  if (shouldClearMessage) {
    clearFormMessage();
  }
}

function showFormMessage(message, isError = false) {
  formMessage.textContent = message;
  formMessage.classList.toggle("error", isError);
}

function clearFormMessage() {
  showFormMessage("");
}

function formatTime(timeValue) {
  const [hourText, minuteText] = timeValue.split(":");
  const hour = Number(hourText);
  const minute = Number(minuteText);

  if (Number.isNaN(hour) || Number.isNaN(minute)) {
    return timeValue;
  }

  const date = new Date();
  date.setHours(hour, minute, 0, 0);
  return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function normalizeSentence(text) {
  const trimmed = text.trim();
  if (!trimmed) return "";

  return /[.!?]$/.test(trimmed) ? trimmed : `${trimmed}.`;
}

function escapeHtml(value) {
  const text = String(value);
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
