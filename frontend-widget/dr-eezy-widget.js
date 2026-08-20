/**
 * Dr. Eezy — embeddable chat widget for Medics Online.
 *
 * Usage: drop this ONE line before </body> on any page:
 *
 *   <script src="https://your-cdn-or-server/dr-eezy-widget.js"
 *           data-api-base="http://localhost:8000"></script>
 *
 * No build step, no framework, no dependencies — plain vanilla JS + CSS
 * injected at runtime, so it can be embedded on any website.
 */
(function () {
  "use strict";

  var currentScript = document.currentScript;
  var API_BASE = (currentScript && currentScript.getAttribute("data-api-base")) || "http://localhost:8000";

  var STYLE = "\
    #dr-eezy-launcher {\
      position: fixed; bottom: 24px; right: 24px; width: 60px; height: 60px;\
      border-radius: 50%; background: #1f4e79; color: #fff; border: none;\
      box-shadow: 0 4px 14px rgba(0,0,0,0.25); cursor: pointer; z-index: 999999;\
      font-size: 26px; display: flex; align-items: center; justify-content: center;\
    }\
    #dr-eezy-panel {\
      position: fixed; bottom: 96px; right: 24px; width: 360px; max-width: 90vw;\
      height: 500px; max-height: 78vh; background: #fff; border-radius: 12px;\
      box-shadow: 0 8px 30px rgba(0,0,0,0.3); display: none; flex-direction: column;\
      overflow: hidden; z-index: 999999; font-family: Arial, Helvetica, sans-serif;\
    }\
    #dr-eezy-panel.open { display: flex; }\
    #dr-eezy-header {\
      background: #1f4e79; color: #fff; padding: 12px 14px; font-weight: bold;\
      display: flex; justify-content: space-between; align-items: center;\
    }\
    #dr-eezy-header small { display: block; font-weight: normal; opacity: 0.85; font-size: 11px; }\
    #dr-eezy-close { background: none; border: none; color: #fff; font-size: 18px; cursor: pointer; }\
    #dr-eezy-toolbar { padding: 8px 10px; border-bottom: 1px solid #eee; font-size: 12px; display: flex; align-items: center; justify-content: space-between; }\
    #dr-eezy-profession select { margin-left: 6px; }\
    #dr-eezy-upload-label { cursor: pointer; color: #1f4e79; text-decoration: underline; white-space: nowrap; margin-left: 10px; }\
    #dr-eezy-messages { flex: 1; overflow-y: auto; padding: 10px; font-size: 13px; background: #f7f9fb; }\
    .dr-eezy-msg { margin-bottom: 10px; line-height: 1.4; }\
    .dr-eezy-msg.user { text-align: right; }\
    .dr-eezy-msg .bubble { display: inline-block; padding: 8px 12px; border-radius: 10px; max-width: 90%; white-space: pre-wrap; text-align: left; }\
    .dr-eezy-msg.user .bubble { background: #1f4e79; color: #fff; }\
    .dr-eezy-msg.bot .bubble { background: #e7edf3; color: #1a1a1a; }\
    .dr-eezy-sources { font-size: 11px; color: #666; margin-top: 3px; }\
    .dr-eezy-action-btn {\
      display: inline-block; margin-top: 8px; background: #548235; color: #fff;\
      padding: 6px 12px; border-radius: 6px; font-size: 12px; text-decoration: none;\
    }\
    .dr-eezy-match-list { margin: 6px 0 0 0; padding-left: 18px; }\
    .dr-eezy-match-list li { margin-bottom: 4px; }\
    #dr-eezy-inputrow { display: flex; border-top: 1px solid #eee; padding: 8px; }\
    #dr-eezy-input { flex: 1; border: 1px solid #ccc; border-radius: 6px; padding: 8px; font-size: 13px; }\
    #dr-eezy-send { margin-left: 6px; background: #1f4e79; color: #fff; border: none; border-radius: 6px; padding: 0 14px; cursor: pointer; }\
  ";

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
    headerText.innerHTML = "Dr. Eezy<br><small>Medics Online AI Assistant</small>";
    var closeBtn = el("button", { id: "dr-eezy-close", text: "✕" });
    header.appendChild(headerText);
    header.appendChild(closeBtn);

    var toolbar = el("div", { id: "dr-eezy-toolbar" });
    var professionDiv = el("div", { id: "dr-eezy-profession" });
    professionDiv.innerHTML = 'I am a: <select id="dr-eezy-profession-select">' +
      '<option value="">Just browsing</option>' +
      '<option value="Doctor">Doctor</option>' +
      '<option value="Nurse">Nurse</option>' +
      "</select>";
    var uploadLabel = el("label", { id: "dr-eezy-upload-label", text: "📎 Upload your CV" });
    var uploadInput = el("input", { type: "file", accept: "application/pdf", id: "dr-eezy-upload-input", style: "display:none" });
    uploadLabel.appendChild(uploadInput);
    toolbar.appendChild(professionDiv);
    toolbar.appendChild(uploadLabel);

    var messages = el("div", { id: "dr-eezy-messages" });

    var inputRow = el("div", { id: "dr-eezy-inputrow" });
    var input = el("input", { id: "dr-eezy-input", type: "text", placeholder: "Ask about jobs, rosters, or the application..." });
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
          "Hi, I'm Dr. Eezy 👋 I can help you find doctor or nurse jobs on Medics Online, " +
          "answer questions about the application process, upload your CV for instant job " +
          "matching (📎 above), or generate a staff roster if you're an admin. " +
          "What can I help with?"
        );
      }
    });
    closeBtn.addEventListener("click", function () { panel.classList.remove("open"); });

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
        msg.appendChild(document.createElement("br"));
        msg.appendChild(link);
      }

      if (sources && sources.length) {
        var labels = sources.map(function (s) { return s.label; }).filter(Boolean);
        if (labels.length) {
          var srcLine = el("div", { class: "dr-eezy-sources", text: "Sources: " + labels.join(", ") });
          msg.appendChild(srcLine);
        }
      }

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
      var thinkingMsg = addBotMessage("Thinking...");

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
            "Sorry, I couldn't reach the Dr. Eezy backend (" + err.message + "). " +
            "Make sure the API server is running at " + API_BASE + "."
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
        "Skills detected: " + (data.skills.length ? data.skills.join(", ") : "none detected"),
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
        var scoreText = (m.match_score !== null && m.match_score !== undefined)
          ? " (" + m.match_score + "% match)" : "";
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
      var thinkingMsg = addBotMessage("Analyzing your CV...");

      var formData = new FormData();
      formData.append("file", file);

      fetch(API_BASE + "/cv/upload", { method: "POST", body: formData })
        .then(function (r) {
          return r.json().then(function (data) { return { ok: r.ok, data: data }; });
        })
        .then(function (result) {
          messages.removeChild(thinkingMsg);
          if (!result.ok) {
            addBotMessage("I couldn't process that CV: " + (result.data.detail || "unknown error"));
            return;
          }
          addBotMessage(formatCvSummary(result.data));
          addMatchList(result.data.matches);

          // Auto-set the profession dropdown to match the uploaded CV, so
          // any follow-up chat questions are filtered correctly too.
          if (result.data.profession) {
            document.getElementById("dr-eezy-profession-select").value = result.data.profession;
          }
        })
        .catch(function (err) {
          messages.removeChild(thinkingMsg);
          addBotMessage("Sorry, I couldn't reach the Dr. Eezy backend (" + err.message + ").");
        });
    }

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") sendMessage();
    });

    uploadLabel.addEventListener("click", function (e) {
      // clicking the label already opens the file picker via the nested
      // input, but stop propagation so it doesn't double-fire.
      e.stopPropagation();
    });
    uploadInput.addEventListener("change", function () {
      if (uploadInput.files && uploadInput.files.length) {
        uploadCV(uploadInput.files[0]);
        uploadInput.value = ""; // allow re-uploading the same file later
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