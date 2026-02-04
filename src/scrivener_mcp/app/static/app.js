// === State ===
let currentDocument = null;
let originalContent = "";
let originalSynopsis = "";
let originalNotes = "";

// === Elements ===
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// === API Helpers ===
async function api(endpoint, options = {}) {
    const response = await fetch(endpoint, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || "Request failed");
    }
    return response.json();
}

// === Initialization ===
document.addEventListener("DOMContentLoaded", async () => {
    // Check project status
    try {
        const status = await api("/api/project/status");
        if (status.loaded) {
            updateProjectStatus(status);
            await loadBinder();
        }
    } catch (e) {
        console.log("No project loaded yet");
    }

    // Check LLM config
    try {
        const config = await api("/api/llm/config");
        updateLLMStatus(config);
    } catch (e) {
        console.log("LLM not configured");
    }

    // Event listeners
    setupEventListeners();
});

function setupEventListeners() {
    // Open project modal
    $("#btn-open-project").addEventListener("click", openProjectModal);
    $("#btn-close-modal").addEventListener("click", () => $("#modal-projects").classList.remove("active"));
    $("#btn-open-custom").addEventListener("click", openCustomPath);

    // Modal tabs
    $$(".modal-tab").forEach(tab => {
        tab.addEventListener("click", () => switchModalTab(tab.dataset.modalTab));
    });

    // Browse navigation
    $("#btn-browse-up").addEventListener("click", browseUp);

    // Settings modal
    $("#btn-settings").addEventListener("click", openSettingsModal);
    $("#btn-close-settings").addEventListener("click", () => $("#modal-settings").classList.remove("active"));
    $("#btn-save-settings").addEventListener("click", saveSettings);

    // Tabs
    $$(".tab").forEach(tab => {
        tab.addEventListener("click", () => switchTab(tab.dataset.tab));
    });

    // Content editing
    $("#editor-content").addEventListener("input", () => {
        $("#btn-save-content").disabled = $("#editor-content").value === originalContent;
    });
    $("#editor-synopsis").addEventListener("input", () => {
        $("#btn-save-synopsis").disabled = $("#editor-synopsis").value === originalSynopsis;
    });
    $("#editor-notes").addEventListener("input", () => {
        $("#btn-save-notes").disabled = $("#editor-notes").value === originalNotes;
    });

    // Save buttons
    $("#btn-save-content").addEventListener("click", saveContent);
    $("#btn-save-synopsis").addEventListener("click", saveSynopsis);
    $("#btn-save-notes").addEventListener("click", saveNotes);

    // AI buttons
    $("#btn-send-to-ai").addEventListener("click", sendSelectionToAI);
    $("#btn-send-chat").addEventListener("click", sendChatMessage);
    $("#chat-input").addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });

    // Binder search
    $("#binder-search").addEventListener("input", filterBinder);

    // Close modals on background click
    $$(".modal").forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) modal.classList.remove("active");
        });
    });
}

// === Project Management ===
async function openProjectModal() {
    $("#modal-projects").classList.add("active");
    $("#project-list").innerHTML = "<p>Searching for projects...</p>";

    try {
        const data = await api("/api/projects");
        if (data.projects.length === 0) {
            $("#project-list").innerHTML = "<p>No projects found. Enter a path below.</p>";
        } else {
            $("#project-list").innerHTML = data.projects.map(p => `
                <div class="project-item" data-path="${p.path}">
                    <div class="name">${p.name}</div>
                    <div class="path">${p.path}</div>
                </div>
            `).join("");

            $$(".project-item").forEach(item => {
                item.addEventListener("click", () => openProject(item.dataset.path));
            });
        }
    } catch (e) {
        $("#project-list").innerHTML = `<p>Error: ${e.message}</p>`;
    }
}

async function openProject(path) {
    try {
        const data = await api("/api/project/open", {
            method: "POST",
            body: JSON.stringify({ path }),
        });
        updateProjectStatus(data);
        await loadBinder();
        $("#modal-projects").classList.remove("active");
    } catch (e) {
        alert(`Failed to open project: ${e.message}`);
    }
}

async function openCustomPath() {
    const path = $("#custom-path").value.trim();
    if (path) {
        await openProject(path);
    }
}

function updateProjectStatus(data) {
    $("#project-name").textContent = data.name;
    if (data.is_locked) {
        $("#lock-status").textContent = "🔒 Locked (Scrivener open)";
        $("#lock-status").className = "locked";
    } else {
        $("#lock-status").textContent = "✓ Unlocked";
        $("#lock-status").className = "unlocked";
    }
}

// === Binder ===
async function loadBinder() {
    try {
        const data = await api("/api/binder");
        renderBinder(data.items);
    } catch (e) {
        $("#binder-tree").innerHTML = `<p class="placeholder">Error: ${e.message}</p>`;
    }
}

function renderBinder(items, container = null) {
    if (!container) {
        container = $("#binder-tree");
        container.innerHTML = "";
    }

    items.forEach(item => {
        const div = document.createElement("div");
        div.className = `binder-item ${item.is_folder ? "folder" : "document"}`;
        div.dataset.uuid = item.uuid;
        div.dataset.path = item.path;
        div.innerHTML = `<span class="icon"></span><span class="title">${item.title}</span>`;
        div.addEventListener("click", (e) => {
            e.stopPropagation();
            selectDocument(item.uuid);
        });
        container.appendChild(div);

        if (item.children && item.children.length > 0) {
            const children = document.createElement("div");
            children.className = "binder-children";
            container.appendChild(children);
            renderBinder(item.children, children);
        }
    });
}

function filterBinder() {
    const query = $("#binder-search").value.toLowerCase();
    $$(".binder-item").forEach(item => {
        const title = item.querySelector(".title").textContent.toLowerCase();
        const matches = title.includes(query);
        item.style.display = matches || !query ? "flex" : "none";
    });
}

// === Document Handling ===
async function selectDocument(uuid) {
    // Update selection
    $$(".binder-item").forEach(el => el.classList.remove("selected"));
    const item = $(`.binder-item[data-uuid="${uuid}"]`);
    if (item) item.classList.add("selected");

    try {
        const doc = await api(`/api/document/${uuid}`);
        currentDocument = doc;
        displayDocument(doc);
    } catch (e) {
        alert(`Error loading document: ${e.message}`);
    }
}

function displayDocument(doc) {
    $("#doc-title").textContent = doc.title;
    $("#doc-words").textContent = `${doc.word_count.toLocaleString()} words`;
    $("#doc-path").textContent = doc.path;

    if (doc.is_folder) {
        $("#editor-content").value = "(Folder - select a document to edit)";
        $("#editor-content").disabled = true;
        $("#editor-synopsis").value = "";
        $("#editor-notes").value = "";
    } else {
        $("#editor-content").value = doc.content || "";
        $("#editor-content").disabled = false;
        $("#editor-synopsis").value = doc.synopsis || "";
        $("#editor-notes").value = doc.notes || "";

        originalContent = doc.content || "";
        originalSynopsis = doc.synopsis || "";
        originalNotes = doc.notes || "";
    }

    // Reset save buttons
    $("#btn-save-content").disabled = true;
    $("#btn-save-synopsis").disabled = true;
    $("#btn-save-notes").disabled = true;

    // Switch to content tab
    switchTab("content");
}

// === Saving ===
async function saveContent() {
    if (!currentDocument) return;

    try {
        await api("/api/document/write", {
            method: "POST",
            body: JSON.stringify({
                identifier: currentDocument.uuid,
                content: $("#editor-content").value,
            }),
        });
        originalContent = $("#editor-content").value;
        $("#btn-save-content").disabled = true;
        showToast("Content saved (snapshot created)");
    } catch (e) {
        alert(`Error saving: ${e.message}`);
    }
}

async function saveSynopsis() {
    if (!currentDocument) return;

    try {
        await api("/api/synopsis/write", {
            method: "POST",
            body: JSON.stringify({
                identifier: currentDocument.uuid,
                synopsis: $("#editor-synopsis").value,
            }),
        });
        originalSynopsis = $("#editor-synopsis").value;
        $("#btn-save-synopsis").disabled = true;
        showToast("Synopsis saved");
    } catch (e) {
        alert(`Error saving: ${e.message}`);
    }
}

async function saveNotes() {
    if (!currentDocument) return;

    try {
        await api("/api/notes/write", {
            method: "POST",
            body: JSON.stringify({
                identifier: currentDocument.uuid,
                notes: $("#editor-notes").value,
            }),
        });
        originalNotes = $("#editor-notes").value;
        $("#btn-save-notes").disabled = true;
        showToast("Notes saved");
    } catch (e) {
        alert(`Error saving: ${e.message}`);
    }
}

// === Tabs ===
function switchTab(tabName) {
    $$(".tab").forEach(t => t.classList.toggle("active", t.dataset.tab === tabName));
    $$(".tab-content").forEach(c => c.classList.toggle("active", c.id === `tab-${tabName}`));
}

// === AI Chat ===
function updateLLMStatus(config) {
    if (config.has_api_key) {
        $("#llm-model").textContent = config.model.split("/").pop();
        clearSystemMessage();
    } else {
        $("#llm-model").textContent = "Not configured";
    }
}

function clearSystemMessage() {
    const systemMsg = $(".chat-message.system");
    if (systemMsg) systemMsg.remove();
}

function addChatMessage(role, content) {
    const messages = $("#chat-messages");
    const div = document.createElement("div");
    div.className = `chat-message ${role}`;
    div.textContent = content;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

async function sendChatMessage() {
    const input = $("#chat-input");
    const message = input.value.trim();
    if (!message) return;

    input.value = "";
    addChatMessage("user", message);

    // Include current document as context
    let context = "";
    if (currentDocument && !currentDocument.is_folder) {
        context = `Document: ${currentDocument.title}\n\n${currentDocument.content}`;
    }

    try {
        const data = await api("/api/chat", {
            method: "POST",
            body: JSON.stringify({ message, context }),
        });
        addChatMessage("assistant", data.response);
    } catch (e) {
        addChatMessage("system", `Error: ${e.message}`);
    }
}

function sendSelectionToAI() {
    const textarea = $("#editor-content");
    const selection = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
    const text = selection || textarea.value;

    if (!text) {
        alert("No content to send");
        return;
    }

    // Pre-fill chat with the selection
    $("#chat-input").value = `Help me improve this:\n\n${text.substring(0, 500)}${text.length > 500 ? "..." : ""}`;
    $("#chat-input").focus();
}

// === Settings ===
function openSettingsModal() {
    $("#modal-settings").classList.add("active");

    // Load current config
    api("/api/llm/config").then(config => {
        $("#setting-provider").value = config.provider;
        $("#setting-model").value = config.model;
    });
}

async function saveSettings() {
    try {
        await api("/api/llm/config", {
            method: "POST",
            body: JSON.stringify({
                provider: $("#setting-provider").value,
                model: $("#setting-model").value,
                api_key: $("#setting-api-key").value,
            }),
        });
        const config = await api("/api/llm/config");
        updateLLMStatus(config);
        $("#modal-settings").classList.remove("active");
        showToast("Settings saved");
    } catch (e) {
        alert(`Error saving settings: ${e.message}`);
    }
}

// === Toast ===
function showToast(message) {
    // Simple toast - could be improved
    const existing = $(".toast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.style.cssText = `
        position: fixed;
        bottom: 1rem;
        left: 50%;
        transform: translateX(-50%);
        background: var(--success);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        z-index: 200;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

// === File Browser ===
let currentBrowsePath = null;

function switchModalTab(tabName) {
    $$(".modal-tab").forEach(t => t.classList.toggle("active", t.dataset.modalTab === tabName));
    $$(".modal-tab-content").forEach(c => c.classList.toggle("active", c.id === `modal-tab-${tabName}`));

    if (tabName === "browse" && !currentBrowsePath) {
        browseTo(null); // Start at home
    }
}

async function browseTo(path) {
    try {
        const url = path ? `/api/browse?path=${encodeURIComponent(path)}` : "/api/browse";
        const data = await api(url);

        currentBrowsePath = data.current;
        $("#browse-path").textContent = data.current;
        $("#btn-browse-up").disabled = !data.parent;

        if (data.items.length === 0) {
            $("#browse-list").innerHTML = "<p class='placeholder'>No folders found</p>";
        } else {
            $("#browse-list").innerHTML = data.items.map(item => `
                <div class="browse-item ${item.is_scriv ? 'scriv' : ''}"
                     data-path="${item.path}"
                     data-is-scriv="${item.is_scriv}">
                    <span class="icon">${item.is_scriv ? '📚' : '📁'}</span>
                    <span class="name">${item.name}</span>
                </div>
            `).join("");

            $$(".browse-item").forEach(item => {
                item.addEventListener("click", () => {
                    if (item.dataset.isScriv === "true") {
                        openProject(item.dataset.path);
                    } else {
                        browseTo(item.dataset.path);
                    }
                });
            });
        }
    } catch (e) {
        $("#browse-list").innerHTML = `<p class="placeholder">Error: ${e.message}</p>`;
    }
}

function browseUp() {
    if (currentBrowsePath) {
        const parent = currentBrowsePath.split("/").slice(0, -1).join("/") || "/";
        browseTo(parent);
    }
}
