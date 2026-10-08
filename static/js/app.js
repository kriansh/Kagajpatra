/* Nagarik Sewa — frontend behaviour: voice input, AI ask, read-aloud, checklist. */
(function () {
  "use strict";

  const lang = document.body.dataset.lang || "en";
  const speechLang = lang === "ne" ? "ne-NP" : "en-US";
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  /* ---------- CSRF (for fetch POSTs) ---------- */
  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[2]) : "";
  }

  /* ---------- i18n strings embedded by the template ---------- */
  const _stringsEl = document.getElementById("ui-strings");
  const strings = _stringsEl ? JSON.parse(_stringsEl.textContent) : {};

  /* =========================================================
     1. AI ask box
     ========================================================= */
  const askForm = $("#ask-form");
  if (askForm) {
    const input = $("#ask-input", askForm);
    const status = $("#ask-status");
    const answerCard = $("#answer-card");
    const answerText = $("#answer-text");
    const providerBadge = $("#provider-badge");
    let abortCtrl = null;

    askForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const question = (input.value || "").trim();
      if (!question) return;

      if (abortCtrl) abortCtrl.abort();
      abortCtrl = new AbortController();

      answerCard.classList.add("hidden");
      status.textContent = strings.thinking || "Thinking…";

      try {
        const body = new URLSearchParams({ question });
        const resp = await fetch("/api/ask/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body,
          signal: abortCtrl.signal,
        });
        const data = await resp.json();
        if (!resp.ok || data.error) {
          throw new Error(data.error || resp.statusText);
        }
        status.textContent = "";
        answerText.textContent = data.answer;
        providerBadge.textContent =
          data.provider === "ollama"
            ? strings.provider_ollama || "Local Gemma"
            : strings.provider_gemini || "Gemma (Gemini API)";
        answerCard.classList.remove("hidden");
        answerCard.dataset.answer = data.answer;
      } catch (err) {
        if (err.name === "AbortError") return;
        status.textContent = "";
        answerText.textContent = strings.no_answer || "Sorry, could not answer.";
        providerBadge.textContent = "⚠";
        answerCard.classList.remove("hidden");
      }
    });

    /* mic button lives near the form */
    const micBtn = $("#mic-btn");
    if (micBtn) setupVoiceInput(micBtn, input, askForm);

    const readBtn = $("#read-answer");
    if (readBtn) {
      readBtn.addEventListener("click", () => {
        const text = answerCard.dataset.answer || answerText.textContent;
        speak(text, readBtn);
      });
    }
  }

  /* =========================================================
     2. Voice input (Web Speech API)
     ========================================================= */
  function setupVoiceInput(btn, input, form) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      btn.title = strings.voiceUnsupported || "Voice input not supported in this browser";
      btn.addEventListener("click", () => {
        alert(strings.voiceUnsupported || "Voice input works best in Chrome.");
      });
      return;
    }
    const rec = new SR();
    rec.lang = speechLang;
    rec.interimResults = false;
    rec.maxAlternatives = 1;

    let listening = false;
    btn.addEventListener("click", () => {
      if (listening) {
        rec.stop();
        return;
      }
      try {
        rec.start();
      } catch (_) {
        /* already started */
      }
    });

    rec.onstart = () => {
      listening = true;
      btn.classList.add("is-listening");
      const st = $("#ask-status");
      if (st) st.textContent = strings.listening || "Listening…";
    };
    rec.onend = () => {
      listening = false;
      btn.classList.remove("is-listening");
    };
    rec.onerror = () => {
      listening = false;
      btn.classList.remove("is-listening");
    };
    rec.onresult = (e) => {
      const text = e.results[0][0].transcript;
      input.value = text;
      form.requestSubmit();
    };
  }

  /* =========================================================
     3. Read aloud (speechSynthesis)
     ========================================================= */
  let voices = [];
  let activeReading = null; // { btn, token }

  function loadVoices() {
    voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
  }
  function pickVoice() {
    // Prefer the active language, then any Devanagari-capable voice, else first.
    return (
      voices.find((v) => v.lang && v.lang.toLowerCase().startsWith(lang === "ne" ? "ne" : "en")) ||
      voices.find((v) => v.lang && /^(hi|bn|mr)/.test(v.lang)) ||
      voices[0] ||
      null
    );
  }

  if (window.speechSynthesis) {
    loadVoices();
    /* Chrome loads voices asynchronously — refresh whenever they change. */
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }

  /* Break long text into short utterances — Chrome's speechSynthesis silently
     stops after ~15 seconds on a single long utterance, which made whole-page
     read-aloud appear "not working". */
  function chunkText(text) {
    const sentences = text.match(/[^।.!?…]+[।.!?…]+|[^।.!?…]+$/g) || [text];
    const out = [];
    let buf = "";
    for (const s of sentences) {
      let piece = (s || "").trim();
      if (!piece) continue;
      if (buf.length + piece.length <= 180) {
        buf += (buf ? " " : "") + piece;
      } else {
        if (buf) out.push(buf);
        while (piece.length > 180) {
          out.push(piece.slice(0, 180));
          piece = piece.slice(180);
        }
        buf = piece;
      }
    }
    if (buf) out.push(buf);
    return out;
  }

  function speak(text, btn) {
    if (!text || !text.trim()) return;
    if (!window.speechSynthesis) {
      const st = $("#ask-status");
      if (st) st.textContent = strings.voiceUnsupported || "Voice is not supported in this browser.";
      return;
    }
    /* Clicking again while reading stops it. */
    if (activeReading && activeReading.btn === btn) {
      window.speechSynthesis.cancel();
      finishReading(btn);
      return;
    }
    window.speechSynthesis.cancel();
    const chunks = chunkText(text);
    if (!chunks.length) return;

    setSpeaking(btn);
    const token = {};
    activeReading = { btn, token };
    const voice = pickVoice();
    let i = 0;
    const next = () => {
      if (!activeReading || activeReading.btn !== btn || activeReading.token !== token) return;
      if (i >= chunks.length) {
        finishReading(btn);
        return;
      }
      const utter = new SpeechSynthesisUtterance(chunks[i++]);
      utter.lang = speechLang;
      if (voice) utter.voice = voice;
      utter.rate = 0.95;
      utter.onend = next;
      utter.onerror = next;
      try {
        window.speechSynthesis.speak(utter);
      } catch (_) {
        next();
      }
    };
    next();
  }

  function setSpeaking(btn) {
    btn.dataset.origText = btn.textContent;
    btn.textContent = strings.stop || "■ Stop";
    btn.classList.add("is-speaking");
  }
  function resetBtn(btn) {
    if (btn.dataset.origText) btn.textContent = btn.dataset.origText;
    btn.classList.remove("is-speaking");
  }
  function finishReading(btn) {
    activeReading = null;
    resetBtn(btn);
  }

  /* "Read this page aloud" buttons (speak the matched element's text) */
  $$("[data-read-selector]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const el = $(btn.dataset.readSelector);
      if (!el) return;
      speak(el.innerText, btn);
    });
  });

  /* =========================================================
     4. Checklist tick-off (persisted per service)
     ========================================================= */
  const slug = document.body.dataset.serviceSlug || "";
  const storeKey = "checklist:" + (slug || "global");
  let saved = {};
  try {
    saved = JSON.parse(localStorage.getItem(storeKey) || "{}");
  } catch (_) {
    saved = {};
  }

  $$(".check-item").forEach((item) => {
    const id = item.dataset.id;
    if (saved[id]) item.classList.add("is-checked");
    item.setAttribute("role", "checkbox");
    item.setAttribute("tabindex", "0");
    item.setAttribute("aria-checked", saved[id] ? "true" : "false");
    const toggle = () => {
      const checked = item.classList.toggle("is-checked");
      item.setAttribute("aria-checked", checked ? "true" : "false");
      saved[id] = checked;
      try {
        localStorage.setItem(storeKey, JSON.stringify(saved));
      } catch (_) {
        /* private mode */
      }
      updateProgress();
    };
    item.addEventListener("click", toggle);
    item.addEventListener("keydown", (e) => {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        toggle();
      }
    });
  });

  function updateProgress() {
    const bar = $("#check-progress");
    if (!bar) return;
    const total = $$(".check-item").length;
    const done = $$(".check-item.is-checked").length;
    bar.textContent = done + " / " + total;
  }
  updateProgress();

  /* =========================================================
     5. "Ask about this service" prefill
     ========================================================= */
  $$("[data-ask-prefill]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = $("#ask-input");
      if (!input) return;
      input.value = btn.dataset.askPrefill;
      input.focus();
      window.scrollTo({ top: 0, behavior: "smooth" });
      $("#ask-form").requestSubmit();
    });
  });
})();
