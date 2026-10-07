/**
 * Dr. Eezy — modern embeddable chat widget for Medics Online.
 *
 * Usage:
 *   <script src="dr-eezy-widget.js" data-api-base="http://localhost:8000"></script>
 */
(function () {
  "use strict";

  var currentScript = document.currentScript;
  var API_BASE = (currentScript && currentScript.getAttribute("data-api-base")) || "http://localhost:8000";

  var STYLE = `
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    #dr-eezy-launcher {
      position: fixed;
      bottom: 28px;
      right: 28px;
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background: linear-gradient(135deg, #0f4c81 0%, #1a6bb5 100%);
      color: #fff;
      border: none;
      box-shadow: 0 8px 24px rgba(15, 76, 129, 0.35);
      cursor: pointer;
      z-index: 999999;
      font-size: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    #dr-eezy-launcher:hover {
      transform: scale(1.08);
      box-shadow: 0 12px 28px rgba(15, 76, 129, 0.45);
    }
    #dr-eezy-launcher::after {
      content: '';
      position: absolute;
      inset: -4px;
      border-radius: 50%;
      border: 2px solid rgba(26, 107, 181, 0.4);
      animation: dr-eezy-pulse 2s infinite;
    }
    @keyframes dr-eezy-pulse {
      0% { transform: scale(1); opacity: 0.7; }
      70% { transform: scale(1.25); opacity: 0; }
      100% { transform: scale(1.25); opacity: 0; }
    }

    #dr-eezy-panel {
      position: fixed;
      bottom: 108px;
      right: 28px;
      width: 400px;
      max-width: calc(100vw - 32px);
      height: 580px;
      max-height: 80vh;
      background: #ffffff;
      border-radius: 20px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.18);
      display: none;
      flex-direction: column;
      overflow: hidden;
      z-index: 999999;
      font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      border: 1px solid rgba(0,0,0,0.06);
    }
    #dr-eezy-panel.open {
      display: flex;
      animation: dr-eezy-slide-up 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes dr-eezy-slide-up {
      from { opacity: 0; transform: translateY(16px) scale(0.97); }
      to   { opacity: 1; transform: translateY(0) scale(1); }
    }

    #dr-eezy-header {
      background: linear-gradient(135deg, #0f4c81 0%, #1a6bb5 100%);
      color: #fff;
      padding: 16px 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    #dr-eezy-header .title {
      font-weight: 600;
      font-size: 16px;
      letter-spacing: -0.01em;
    }
    #dr-eezy-header small {
      display: block;
      font-weight: 400;
      opacity: 0.85;
      font-size: 12px;
      margin-top: 2px;
    }
    #dr-eezy-close {
      background: rgba(255,255,255,0.15);
      border: none;
      color: #fff;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      font-size: 16px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s;
    }
    #dr-eezy-close:hover { background: rgba(255,255,255,0.25); }

    #dr-eezy-toolbar {
      padding: 12px 16px;
      background: #f8fafc;
      border-bottom: 1px solid #e2e8f0;
      font-size: 13px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    #dr-eezy-profession {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #475569;
      font-weight: 500;
    }
    #dr-eezy-profession select {
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 6px 10px;
      font-size: 13px;
      background: #fff;
      color: #1e293b;
      outline: none;
      cursor: pointer;
    }
    #dr-eezy-profession select:focus {
      border-color: #1a6bb5;
      box-shadow: 0 0 0 3px rgba(26, 107, 181, 0.15);
    }
    #dr-eezy-upload-label {
      cursor: pointer;
      color: #1a6bb5;
      font-weight: 500;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 10px;
      border-radius: 8px;
      transition: background 0.15s;
    }
    #dr-eezy-upload-label:hover { background: #e0f2fe; }

    #dr-eezy-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      background: #f1f5f9;
      scroll-behavior: smooth;
    }
    #dr-eezy-messages::-webkit-scrollbar { width: 6px; }
    #dr-eezy-messages::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 3px;
    }

    .dr-eezy-msg {
      margin-bottom: 14px;
      line-height: 1.5;
      display: flex;
      flex-direction: column;
    }
    .dr-eezy-msg.user { align-items: flex-end; }
    .dr-eezy-msg.bot  { align-items: flex-start; }

    .dr-eezy-msg .bubble {
      display: inline-block;
      padding: 11px 15px;
      border-radius: 16px;
      max-width: 88%;
      white-space: pre-wrap;
      text-align: left;
      font-size: 14px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .dr-eezy-msg.user .bubble {
      background: linear-gradient(135deg, #0f4c81 0%, #1a6bb5 100%);
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .dr-eezy-msg.bot .bubble {
      background: #ffffff;
      color: #1e293b;
      border: 1px solid #e2e8f0;
      border-bottom-left-radius: 4px;
    }

    .dr-eezy-sources {
      font-size: 11px;
      color: #64748b;
      margin-top: 6px;
      padding-left: 4px;
    }

    .dr-eezy-action-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-top: 10px;
      background: linear-gradient(135deg, #15803d 0%, #16a34a 100%);
      color: #fff;
      padding: 8px 16px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 500;
      text-decoration: none;
      box-shadow: 0 2px 8px rgba(22, 163, 74, 0.25);
      transition: transform 0.15s, box-shadow 0.15s;
    }
    .dr-eezy-action-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(22, 163, 74, 0.35);
    }

    .dr-eezy-match-list {
      margin: 8px 0 0 0;
      padding-left: 18px;
      color: #334155;
    }
    .dr-eezy-match-list li {
      margin-bottom: 6px;
      font-size: 13.5px;
    }

    .dr-eezy-typing {
      display: inline-flex;
      gap: 4px;
      padding: 12px 16px;
    }
    .dr-eezy-typing span {
      width: 7px;
      height: 7px;
      background: #94a3b8;
      border-radius: 50%;
      animation: dr-eezy-bounce 1.2s infinite ease-in-out;
    }
    .dr-eezy-typing span:nth-child(2) { animation-delay: 0.15s; }
    .dr-eezy-typing span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes dr-eezy-bounce {
      0%, 80%, 100% { transform: scale(0.7); opacity: 0.5; }
      40% { transform: scale(1); opacity: 1; }
    }

    #dr-eezy-inputrow {
      display: flex;
      gap: 8px;
      padding: 14px 16px;
      background: #fff;
      border-top: 1px solid #e2e8f0;
    }
    #dr-eezy-input {
      flex: 1;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 11px 14px;
      font-size: 14px;
      outline: none;
      transition: border-color 0.15s, box-shadow 0.15s;
      font-family: inherit;
    }
    #dr-eezy-input:focus {
      border-color: #1a6bb5;
      box-shadow: 0 0 0 3px rgba(26, 107, 181, 0.12);
    }
    #dr-eezy-send {
      background: linear-gradient(135deg, #0f4c81 0%, #1a6bb5 100%);
      color: #fff;
      border: none;
      border-radius: 12px;
      padding: 0 18px;
      font-weight: 500;
      font-size: 14px;
      cursor: pointer;
      transition: opacity 0.15s, transform 0.15s;
    }
    #dr-eezy-send:hover { opacity: 0.92; }
    #dr-eezy-send:active { transform: scale(0.97); }
  `;

  function injectStyle() {
    var tag = document.createElement("style");
    tag.textContent = STYLE;
    document.head.appendChild(tag);
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    attrs = attrs || {};
    Object.keys(attrs).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else if (k === "html") node.innerHTML = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { node.appendChild(c); });
    return node;
  }

  function buildWidget() {
    var launcher = el("button", { id: "dr-eezy-launcher", title: "Chat with Dr. Eezy" });
    launcher.textContent = "🩺";

    var panel = el("div", { id: "dr-eezy-panel" });

    var header = el("div", { id: "dr-eezy-header" });
    var headerText = el("div");
    headerText.innerHTML = '<div class="title">Dr. Eezy</div><small>Medics Online AI Assistant</small>';
    var closeBtn = el("button", { id: "dr-eezy-close", text: "✕" });
    header.appendChild(headerText);
    header.appendChild(closeBtn);

    var toolbar = el("div", { id: "dr-eezy-toolbar" });
    var professionDiv = el("div", { id: "dr-eezy-profession" });
    professionDiv.innerHTML =
      'I am a: <select id="dr-eezy-profession-select">' +
      '<option value="">Just browsing</option>' +
      '<option value="Doctor">Doctor</option>' +
      '<option value="Nurse">Nurse</option>' +
      "</select>";
    var uploadLabel = el("label", { id: "dr-eezy-upload-label", html: "📎 Upload CV" });
    var uploadInput = el("input", {
      type: "file",
      accept: "application/pdf",
      id: "dr-eezy-upload-input",
      style: "display:none",
    });
    uploadLabel.appendChild(uploadInput);
    toolbar.appendChild(professionDiv);
    toolbar.appendChild(uploadLabel);

    var messages = el("div", { id: "dr-eezy-messages" });

    var inputRow = el("div", { id: "dr-eezy-inputrow" });
    var input = el("input", {
      id: "dr-eezy-input",
      type: "text",
      placeholder: "Ask about jobs, rosters, or applications…",
    });
    var sendBtn = el("button", { id: "dr-eezy-send", text: "Send" });
    inputRow.appendChild(input);
    inputRow.appendChild(sendBtn);

    panel.appendChild(header);
    panel.appendChild(toolbar);
    panel.appendChild(messages);
    panel.appendChild(inputRow);

    document.body.appendChild(launcher);
    document.body.appendChild(panel);

    launcher.addEventListener("click", function () {
      panel.classList.toggle("open");
      if (panel.classList.contains("open") && messages.children.length === 0) {
        addBotMessage(
          "Hi, I'm Dr. Eezy 👋\n\nI can help you find doctor or nurse jobs on Medics Online, answer questions about the application process, match your CV to open roles, or generate a staff roster if you're an admin.\n\nWhat can I help with?"
        );
      }
    });
    closeBtn.addEventListener("click", function () {
      panel.classList.remove("open");
    });

    function addUserMessage(text) {
      var msg = el("div", { class: "dr-eezy-msg user" });
      var bubble = el("div", { class: "bubble", text: text });
      msg.appendChild(bubble);
      messages.appendChild(msg);
      messages.scrollTop = messages.scrollHeight;
      return msg;
    }

    function addBotMessage(text, sources, action) {
      var msg = el("div", { class: "dr-eezy-msg bot" });
      var bubble = el("div", { class: "bubble", text: text });
      msg.appendChild(bubble);

      if (action && action.url) {
        var link = el("a", {
          class: "dr-eezy-action-btn",
          href: API_BASE + action.url,
          target: "_blank",
          text: action.label || "Download",
        });
        msg.appendChild(link);
      }

      if (sources && sources.length) {
        var labels = sources.map(function (s) { return s.label; }).filter(Boolean);
        if (labels.length) {
          var srcLine = el("div", {
            class: "dr-eezy-sources",
            text: "Sources: " + labels.join(", "),
          });
          msg.appendChild(srcLine);
        }
      }

      messages.appendChild(msg);
      messages.scrollTop = messages.scrollHeight;
      return msg;
    }

    function addTyping() {
      var msg = el("div", { class: "dr-eezy-msg bot" });
      var bubble = el("div", { class: "bubble" });
      bubble.innerHTML =
        '<div class="dr-eezy-typing"><span></span><span></span><span></span></div>';
      msg.appendChild(bubble);
      messages.appendChild(msg);
      messages.scrollTop = messages.scrollHeight;
      return msg;
    }

    function sendMessage() {
      var text = input.value.trim();
      if (!text) return;
      var profession = document.getElementById("dr-eezy-profession-select").value || null;

      addUserMessage(text);
      input.value = "";
      var thinkingMsg = addTyping();

      fetch(API_BASE + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, profession: profession }),
      })
        .then(function (r) {
          if (!r.ok) throw new Error("Request failed: " + r.status);
          return r.json();
        })
        .then(function (data) {
          messages.removeChild(thinkingMsg);
          addBotMessage(data.answer, data.sources, data.action);
        })
        .catch(function (err) {
          messages.removeChild(thinkingMsg);
          addBotMessage(
            "Sorry, I couldn't reach the Dr. Eezy backend (" +
              err.message +
              ").\nMake sure the API server is running at " +
              API_BASE +
              "."
          );
        });
    }

    function formatCvSummary(data) {
      var lines = [
        "I've reviewed your CV, " + (data.candidate_name || "there") + " 👋",
        "",
        "Profession: " + data.profession,
        "Role: " + data.job_title,
        "Experience: " + data.experience_years + " years",
        "Skills detected: " +
          (data.skills.length ? data.skills.join(", ") : "none detected"),
      ];
      if (data.matches && data.matches.length) {
        lines.push("", "Here are your top matching open roles:");
      } else {
        lines.push("", "I couldn't find any open roles matching your profile right now.");
      }
      return lines.join("\n");
    }

    function addMatchList(matches) {
      if (!matches || !matches.length) return;
      var msg = el("div", { class: "dr-eezy-msg bot" });
      var bubble = el("div", { class: "bubble" });
      var list = el("ul", { class: "dr-eezy-match-list" });
      matches.forEach(function (m) {
        var scoreText =
          m.match_score !== null && m.match_score !== undefined
            ? " (" + m.match_score + "% match)"
            : "";
        var li = el("li", { text: m.title + " — " + m.specialty + scoreText });
        list.appendChild(li);
      });
      bubble.appendChild(list);
      msg.appendChild(bubble);
      messages.appendChild(msg);
      messages.scrollTop = messages.scrollHeight;
    }

    function uploadCV(file) {
      addUserMessage("📎 Uploaded: " + file.name);
      var thinkingMsg = addTyping();

      var formData = new FormData();
      formData.append("file", file);

      fetch(API_BASE + "/cv/upload", { method: "POST", body: formData })
        .then(function (r) {
          return r.json().then(function (data) {
            return { ok: r.ok, data: data };
          });
        })
        .then(function (result) {
          messages.removeChild(thinkingMsg);
          if (!result.ok) {
            addBotMessage(
              "I couldn't process that CV: " + (result.data.detail || "unknown error")
            );
            return;
          }
          addBotMessage(formatCvSummary(result.data));
          addMatchList(result.data.matches);

          if (result.data.profession) {
            document.getElementById("dr-eezy-profession-select").value =
              result.data.profession;
          }
        })
        .catch(function (err) {
          messages.removeChild(thinkingMsg);
          addBotMessage(
            "Sorry, I couldn't reach the Dr. Eezy backend (" + err.message + ")."
          );
        });
    }

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") sendMessage();
    });

    uploadLabel.addEventListener("click", function (e) {
      e.stopPropagation();
    });
    uploadInput.addEventListener("change", function () {
      if (uploadInput.files && uploadInput.files.length) {
        uploadCV(uploadInput.files[0]);
        uploadInput.value = "";
      }
    });
  }

  function init() {
    injectStyle();
    buildWidget();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();