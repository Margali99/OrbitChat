let currentConversationId = null;
let currentDocumentId = null;

document.addEventListener("DOMContentLoaded", () => {
  initSession();
  setupEventListeners();
});

async function initSession() {
  try {
    const res = await fetch("/session");
    const data = await res.json();
    console.log("Session initialized:", data.session_id);
  } catch (err) {
    console.error("Session init failed:", err);
  }
}

function setupEventListeners() {
  // Chat actions
  document.getElementById("send-btn").addEventListener("click", sendMessage);
  document.getElementById("message-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  // Sidebar toggle
  const sidebar = document.getElementById("sidebar");
  document.getElementById("sidebar-toggle").addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
  });

  // New Chat
  document.getElementById("new-chat-btn").addEventListener("click", resetChat);

  // Modal actions
  const modal = document.getElementById("keys-modal");
  document.getElementById("gear-btn").addEventListener("click", openKeysModal);
  document.getElementById("sidebar-keys-btn").addEventListener("click", openKeysModal);
  document.getElementById("close-modal-btn").addEventListener("click", () => modal.style.display = "none");
  document.getElementById("close-modal-x").addEventListener("click", () => modal.style.display = "none");
  document.getElementById("save-keys-btn").addEventListener("click", saveKeys);

  // File Upload
  const fileInput = document.getElementById("file-input");
  document.getElementById("attach-btn").addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleFileUpload);

  // Starter prompts
  document.querySelectorAll(".prompt-card").forEach(card => {
    card.addEventListener("click", () => {
      const promptText = card.getAttribute("data-prompt");
      if (promptText) {
        document.getElementById("message-input").value = promptText;
        sendMessage();
      }
    });
  });
}

function resetChat() {
  currentConversationId = null;
  currentDocumentId = null;
  const container = document.getElementById("chat-container");
  container.innerHTML = `
    <div id="welcome-screen" class="welcome-screen">
      <div class="cat-avatar">🐱‍🚀</div>
      <h2>Welcome to Margali's Orbit!</h2>
      <p class="funny-subtitle">"Purr-fect AI assistance powered by Gemini & friends. No laser pointers required!" 🐾✨</p>
      
      <div class="starter-prompts">
        <div class="prompt-card" data-prompt="Explain quantum physics like I am a curious cat.">
          <span class="prompt-icon">🐾</span>
          <span class="prompt-text">Explain quantum physics like I'm a curious cat</span>
        </div>
        <div class="prompt-card" data-prompt="Search the web for the latest AI tech breakthroughs today.">
          <span class="prompt-icon">🌐</span>
          <span class="prompt-text">Search the web for today's AI breakthroughs</span>
        </div>
        <div class="prompt-card" data-prompt="Write a funny adventure story about Margali the space cat orbiting Mars.">
          <span class="prompt-icon">🚀</span>
          <span class="prompt-text">Story about Margali the space cat orbiting Mars</span>
        </div>
        <div class="prompt-card" data-prompt="Help me brainstorm creative ideas for a new project.">
          <span class="prompt-icon">💡</span>
          <span class="prompt-text">Brainstorm creative project ideas</span>
        </div>
      </div>
    </div>
  `;

  document.querySelectorAll(".prompt-card").forEach(card => {
    card.addEventListener("click", () => {
      const promptText = card.getAttribute("data-prompt");
      if (promptText) {
        document.getElementById("message-input").value = promptText;
        sendMessage();
      }
    });
  });

  const indicator = document.getElementById("file-indicator");
  indicator.style.display = "none";
  indicator.textContent = "";
}

async function openKeysModal() {
  const modal = document.getElementById("keys-modal");
  modal.style.display = "flex";

  try {
    const res = await fetch("/keys");
    if (res.ok) {
      const data = await res.json();
      const providers = data.configured_providers || [];
      const desc = document.querySelector(".modal-desc");
      if (providers.length > 0) {
        desc.textContent = `Configured keys: ${providers.join(", ")}. Enter a new key below to update.`;
      } else {
        desc.textContent = "Keys are encrypted at rest with Fernet and used only for your chat sessions.";
      }
    }
  } catch (err) {}
}

async function saveKeys() {
  const gemini = document.getElementById("gemini-key").value.trim();
  const anthropic = document.getElementById("anthropic-key").value.trim();
  const grok = document.getElementById("grok-key").value.trim();

  const pairs = [
    { provider: "gemini", key: gemini },
    { provider: "anthropic", key: anthropic },
    { provider: "xai", key: grok }
  ];

  let savedCount = 0;
  let errors = [];

  for (const item of pairs) {
    if (item.key) {
      try {
        const res = await fetch("/keys", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ provider: item.provider, api_key: item.key })
        });
        if (res.ok) {
          savedCount++;
        } else {
          const errData = await res.json();
          errors.push(`${item.provider}: ${errData.detail || "Error"}`);
        }
      } catch (e) {
        errors.push(`${item.provider}: Network error`);
      }
    }
  }

  if (errors.length > 0) {
    alert("Error saving key(s):\n" + errors.join("\n"));
  } else if (savedCount > 0) {
    document.getElementById("keys-modal").style.display = "none";
    alert(`Successfully saved ${savedCount} API key(s).`);
    document.getElementById("gemini-key").value = "";
    document.getElementById("anthropic-key").value = "";
    document.getElementById("grok-key").value = "";
  } else {
    alert("Please enter at least one API key to save.");
  }
}

async function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  const indicator = document.getElementById("file-indicator");
  indicator.textContent = `Uploading ${file.name}...`;
  indicator.style.display = "inline-block";

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (res.ok) {
      currentDocumentId = data.document_id;
      indicator.textContent = `📄 ${data.filename}`;
    } else {
      alert(`Upload error: ${data.detail || "Failed"}`);
      indicator.style.display = "none";
    }
  } catch (err) {
    alert("Upload failed.");
    indicator.style.display = "none";
  }
}

async function sendMessage() {
  const input = document.getElementById("message-input");
  const text = input.value.trim();
  if (!text) return;

  const welcome = document.getElementById("welcome-screen");
  if (welcome) welcome.remove();

  const model = document.getElementById("model-select").value;

  appendMessage("user", text);
  input.value = "";

  showThinkingIndicator(true);

  const assistantMsgUI = appendMessage("assistant", "");
  const bubble = assistantMsgUI.querySelector(".message-bubble");
  
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: currentConversationId,
        message: text,
        model: model,
        document_id: currentDocumentId
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let accumulatedText = "";
    let isFirstToken = true;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data:")) {
          try {
            const payload = JSON.parse(line.replace("data:", "").trim());
            if (payload.conversation_id) {
              currentConversationId = payload.conversation_id;
            }
            if (payload.tool_used) {
              showToolTag(assistantMsgUI, payload.tool_used);
            }
            if (payload.token) {
              if (isFirstToken) {
                showThinkingIndicator(false);
                isFirstToken = false;
              }
              accumulatedText += payload.token;
              bubble.textContent = accumulatedText;
              scrollToBottom();
            }
            if (payload.error) {
              showThinkingIndicator(false);
              accumulatedText += (accumulatedText ? "\n" : "") + `⚠️ Error: ${payload.error}`;
              bubble.textContent = accumulatedText;
              scrollToBottom();
            }
          } catch (e) {}
        }
      }
    }

    showThinkingIndicator(false);
    addFeedbackButtons(assistantMsgUI);

  } catch (err) {
    showThinkingIndicator(false);
    bubble.textContent = "Error receiving streamed response.";
  }
}

function showThinkingIndicator(show) {
  const indicator = document.getElementById("thinking-indicator");
  indicator.style.display = show ? "flex" : "none";
  if (show) scrollToBottom();
}

function appendMessage(role, text) {
  const container = document.getElementById("chat-container");
  
  const wrapper = document.createElement("div");
  wrapper.className = `message-wrapper ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
  scrollToBottom();
  return wrapper;
}

function showToolTag(wrapper, toolName) {
  let tag = wrapper.querySelector(".tool-tag");
  if (!tag) {
    tag = document.createElement("div");
    tag.className = "tool-tag";
    wrapper.insertBefore(tag, wrapper.firstChild);
  }
  tag.textContent = `🔍 Used tool: ${toolName}`;
}

function addFeedbackButtons(wrapper) {
  if (wrapper.querySelector(".message-actions")) return;

  const actions = document.createElement("div");
  actions.className = "message-actions";

  const upBtn = document.createElement("button");
  upBtn.className = "feedback-btn";
  upBtn.innerHTML = "👍";
  upBtn.title = "Good response";

  const downBtn = document.createElement("button");
  downBtn.className = "feedback-btn";
  downBtn.innerHTML = "👎";
  downBtn.title = "Bad response";

  upBtn.addEventListener("click", () => {
    upBtn.classList.toggle("active");
    upBtn.classList.toggle("liked");
    downBtn.classList.remove("active", "disliked");
  });

  downBtn.addEventListener("click", () => {
    downBtn.classList.toggle("active");
    downBtn.classList.toggle("disliked");
    upBtn.classList.remove("active", "liked");
  });

  actions.appendChild(upBtn);
  actions.appendChild(downBtn);
  wrapper.appendChild(actions);
}

function scrollToBottom() {
  const container = document.getElementById("chat-container");
  container.scrollTop = container.scrollHeight;
}
