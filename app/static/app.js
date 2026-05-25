const uploadForm = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const uploadResult = document.getElementById("uploadResult");

const chatForm = document.getElementById("chatForm");
const queryInput = document.getElementById("queryInput");
const chatWindow = document.getElementById("chatWindow");

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadResult.classList.remove("hidden");
    uploadResult.textContent = "Uploading and processing document...";

    try {
        const response = await fetch("/api/v1/ingest", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            uploadResult.textContent = `Upload failed: ${data.detail}`;
            return;
        }

        uploadResult.textContent =
            `Upload successful\n\n` +
            `Filename: ${data.filename}\n` +
            `Characters: ${data.total_characters}\n` +
            `Chunks: ${data.total_chunks}\n` +
            `Stored chunks: ${data.stored_chunks}\n` +
            `Vectors in store: ${data.total_vectors_in_store}`;

    } catch (error) {
        uploadResult.textContent = `Upload failed: ${error.message}`;
    }
});

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = queryInput.value.trim();

    if (!query) {
        return;
    }

    addMessage(query, "user");
    queryInput.value = "";

    const loadingMessage = addMessage("Thinking...", "assistant");

    try {
        const response = await fetch("/api/v1/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();

        if (!response.ok) {
            loadingMessage.innerHTML = `Error: ${data.detail}`;
            return;
        }

        loadingMessage.innerHTML = formatAssistantResponse(data);

    } catch (error) {
        loadingMessage.innerHTML = `Request failed: ${error.message}`;
    }
});

document.querySelectorAll(".examples button").forEach((button) => {
    button.addEventListener("click", () => {
        queryInput.value = button.dataset.query;
        chatForm.requestSubmit();
    });
});

function addMessage(text, role) {
    const message = document.createElement("div");
    message.className = `message ${role}`;
    message.textContent = text;
    chatWindow.appendChild(message);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return message;
}

function formatAssistantResponse(data) {
    let html = `<div class="route-label">${data.route}</div>`;
    html += `<div>${escapeHtml(data.answer)}</div>`;

    if (data.retrieved_chunks && data.retrieved_chunks.length > 0) {
        html += `<hr>`;
        html += `<strong>Sources used:</strong>`;

        data.retrieved_chunks.forEach((chunk, index) => {
            html += `
                <details>
                    <summary>Chunk ${index + 1} | Source: ${escapeHtml(chunk.source || "unknown")}</summary>
                    <p>${escapeHtml(chunk.text || "")}</p>
                </details>
            `;
        });
    }

    return html;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}