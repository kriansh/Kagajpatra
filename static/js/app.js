/**
 * Sathi — frontend behaviour
 *
 * Modules (all IIFE, no bundler needed):
 *   1. Utilities
 *   2. Mode toggle (Simple / Detailed) — persisted
 *   3. Text size control — persisted
 *   4. Voice adapter — abstraction layer, Web Speech API implementation
 *   5. Search bar with voice
 *   6. AI ask box with voice + read-aloud
 *   7. Checklist tick-off — persisted per service
 *   8. Accordion (steps + FAQs)
 *   9. Toast notifications
 *  10. Checklist copy / share / print
 *  11. Prefill ask box from service page
 *  12. Service worker registration
 */
(function () {
  "use strict";

  /* ============================================================
     1. Utilities
     ============================================================ */
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[2]) : "";
  }

  const lang = document.body.dataset.lang || "en";

  /* i18n strings embedded by Django template as a JSON script tag */
  let strings = {};
  try {
    const el = document.getElementById("ui-strings");
    if (el) strings = JSON.parse(el.textContent);
  } catch (_) {}

  function t(key) { return strings[key] || key; }

  /* Announce to screen readers via aria-live */
  function announce(msg) {
    const el = document.getElementById("sr-announce");
    if (!el) return;
    el.textContent = "";
    requestAnimationFrame(() => { el.textContent = msg; });
  }

  /* ============================================================
     2. Mode toggle (Simple / Detailed)
     ============================================================ */
  const MODE_KEY = "sathi:mode";

  function applyMode(mode) {
    document.body.dataset.mode = mode;
    $$("[data-mode-btn]").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.modeBtn === mode ? "true" : "false");
    });
  }

  function initModeToggle() {
    const saved = localStorage.getItem(MODE_KEY) || "simple";
    applyMode(saved);

    $$("[data-mode-btn]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const m = btn.dataset.modeBtn;
        applyMode(m);
        try { localStorage.setItem(MODE_KEY, m); } catch (_) {}
      });
    });
  }

  /* ============================================================
     3. Text size control
     ============================================================ */
  const SIZE_KEY = "sathi:textSize";
  const SIZES = ["normal", "large", "xlarge"];

  function applyTextSize(size) {
    document.documentElement.dataset.textSize = size;
    $$("[data-size-btn]").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.sizeBtn === size ? "true" : "false");
    });
  }

  function initTextSize() {
    const saved = localStorage.getItem(SIZE_KEY) || "normal";
    applyTextSize(saved);

    $$("[data-size-btn]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const s = btn.dataset.sizeBtn;
        applyTextSize(s);
        try { localStorage.setItem(SIZE_KEY, s); } catch (_) {}
      });
    });
  }

  /* ============================================================
     4. Voice adapter — abstraction layer
     The public interface:
       adapter.start(onTranscript, onFinal, onError, onStateChange)
       adapter.stop()
       adapter.state  — "idle" | "requesting" | "listening" | "processing"
     Plug-in point: swap the WebSpeechVoiceAdapter for a
     WebAssembly/Whisper adapter without changing any consumer code.
     ============================================================ */
  const speechLang = lang === "ne" ? "ne-NP" : "en-US";

  class WebSpeechVoiceAdapter {
    constructor() {
      this.state = "idle";
      this._rec = null;
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) {
        this.supported = false;
        return;
      }
      this.supported = true;
      this._SR = SR;
    }

    start(onTranscript, onFinal, onError, onStateChange) {
      if (!this.supported) {
        onError("unsupported");
        return;
      }
      if (this.state !== "idle") return;

      const rec = new this._SR();
      this._rec = rec;
      rec.lang = speechLang;
      rec.interimResults = true;
      rec.maxAlternatives = 1;
      rec.continuous = false;

      this._setstate("requesting", onStateChange);

      rec.onstart = () => this._setstate("listening", onStateChange);

      rec.onresult = (e) => {
        let interim = "";
        let final = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
          const r = e.results[i];
          if (r.isFinal) final += r[0].transcript;
          else interim += r[0].transcript;
        }
        if (interim) onTranscript(interim, false);
        if (final)   onTranscript(final, true);
      };

      rec.onend = () => {
        this._setstate("idle", onStateChange);
        onFinal();
      };

      rec.onerror = (e) => {
        this._setstate("idle", onStateChange);
        const code = e.error || "unknown";
        if (code === "no-speech")                   onError("no_speech");
        else if (code === "not-allowed")            onError("permission_denied");
        else if (code === "aborted")                return; // user-initiated stop
        else if (code === "network")                onError("network_error");
        else if (code === "language-not-supported") onError("lang_unsupported");
        else                                        onError("voice_unsupported");
      };

      try { rec.start(); } catch (_) { /* already started */ }
    }

    stop() {
      if (this._rec) {
        try { this._rec.stop(); } catch (_) {}
        this._rec = null;
      }
      this.state = "idle";
    }

    _setstate(s, cb) {
      this.state = s;
      if (cb) cb(s);
    }
  }

  /* Active voice adapter (swap here for Whisper/WASM) */
  const voiceAdapter = new WebSpeechVoiceAdapter();

  /* ============================================================
     5. VoiceButton component
     Wires any button[data-voice] to the voice adapter.
     data-voice="search" | "ask"
     ============================================================ */
  function setupVoiceButton(btn, inputEl, onFinalText) {
    if (!voiceAdapter.supported) {
      btn.setAttribute("data-state", "unsupported");
      btn.title = t("voice_unsupported");
      btn.addEventListener("click", () => {
        showToast(t("voice_unsupported"), "warning");
        if (inputEl) inputEl.focus();
      });
      return;
    }

    const waveform = $(".voice-waveform", btn);
    const labelEl  = $(".voice-btn__label", btn) || $("[data-voice-label]", btn);
    let   origLabel = labelEl ? labelEl.textContent : "";
    let   liveTranscript = null;

    /* Find associated transcript display (sibling or data attr) */
    const transcriptId = btn.dataset.transcriptTarget;
    if (transcriptId) liveTranscript = document.getElementById(transcriptId);

    const statusId = btn.dataset.statusTarget;
    const statusEl = statusId ? document.getElementById(statusId) : null;

    function setStatus(msg, cls) {
      if (!statusEl) return;
      statusEl.textContent = msg;
      statusEl.className = "voice-status" + (cls ? " voice-status--" + cls : "");
      announce(msg);
    }

    let errorShown = false;

    function onStateChange(state) {
      btn.setAttribute("data-state", state);
      if (waveform) waveform.style.display = state === "listening" ? "flex" : "none";
      if (labelEl) {
        if (state === "listening")  labelEl.textContent = t("listening");
        else if (state === "processing") labelEl.textContent = t("processing");
        else labelEl.textContent = origLabel;
      }
      if (state === "listening") { errorShown = false; setStatus(t("listening"), ""); }
      /* Recognition errors fire onerror immediately followed by onend; the
         resulting idle transition must NOT wipe the error message — only
         clear status when no error is being shown. */
      if (state === "idle" && !errorShown) setStatus("", "");
    }

    function onTranscript(text, isFinal) {
      if (liveTranscript) {
        liveTranscript.textContent = text;
        liveTranscript.dataset.visible = "true";
      }
      if (inputEl && !isFinal) {
        /* Show interim transcript in input */
        inputEl.value = text;
      }
    }

    function onFinal() {
      if (liveTranscript) liveTranscript.dataset.visible = "false";
    }

    function onError(code) {
      /* t() falls back to the raw key when a string is missing — resolve
         unknown codes to the friendly browser-support message instead. */
      const msg = strings[code] || t("voice_unsupported");
      errorShown = true;
      setStatus(msg, "error");
      announce(msg);
      if (liveTranscript) liveTranscript.dataset.visible = "false";
      btn.setAttribute("data-state", code === "unsupported" ? "unsupported" : "idle");
    }

    let autoSearchTimer = null;

    btn.addEventListener("click", () => {
      if (voiceAdapter.state !== "idle") {
        voiceAdapter.stop();
        return;
      }
      errorShown = false;
      setStatus("", "");
      voiceAdapter.start(
        (text, isFinal) => {
          onTranscript(text, isFinal);
          if (isFinal && text.trim()) {
            /* Assign final text and auto-search after short pause */
            if (inputEl) inputEl.value = text.trim();
            clearTimeout(autoSearchTimer);
            autoSearchTimer = setTimeout(() => {
              onFinalText(text.trim());
            }, 800);
          }
        },
        onFinal,
        onError,
        onStateChange
      );
    });
  }

  /* ============================================================
     6. Search bar
     ============================================================ */
  function initSearchBar() {
    const form = document.getElementById("search-form");
    if (!form) return;

    const input   = document.getElementById("search-input");
    const micBtn  = document.getElementById("search-mic-btn");
    const results = document.getElementById("search-results");

    if (micBtn && input) {
      setupVoiceButton(micBtn, input, (text) => {
        if (input) input.value = text;
        if (form) form.requestSubmit();
      });
    }

    /* Live search on keyup */
    if (input && results) {
      input.addEventListener("input", () => {
        const q = input.value.trim();
        if (q.length < 2) {
          results.innerHTML = "";
          results.hidden = true;
          return;
        }
        fetchSearch(q, results);
      });

      /* Close results on outside click */
      document.addEventListener("click", (e) => {
        if (!form.contains(e.target)) {
          results.innerHTML = "";
          results.hidden = true;
        }
      });
    }
  }

  function fetchSearch(q, resultsEl) {
    /* Client-side fuzzy match against the service tiles on the page */
    const tiles = $$("[data-service-name]");
    const ql = q.toLowerCase();
    const matches = tiles.filter((el) => {
      const name = (el.dataset.serviceName || "").toLowerCase();
      const tags = (el.dataset.serviceTags || "").toLowerCase();
      return name.includes(ql) || tags.includes(ql) || fuzzyMatch(name, ql) || fuzzyMatch(tags, ql);
    });

    if (!resultsEl) return;
    if (!matches.length) {
      resultsEl.innerHTML = `<div class="search-empty">
        <p>${t("search_no_results")} "<strong>${escHtml(q)}</strong>"</p>
      </div>`;
      resultsEl.hidden = false;
      return;
    }

    resultsEl.innerHTML = matches.map((el) => {
      const href  = el.href || el.dataset.href || "#";
      const name  = el.dataset.serviceName || "";
      const icon  = el.dataset.serviceIconHtml || "";
      const sub   = el.dataset.serviceTagline || "";
      const hl    = highlight(name, q);
      return `<a class="search-result" href="${escHtml(href)}">
        <span class="search-result__icon">${icon}</span>
        <span class="search-result__body">
          <span class="search-result__name">${hl}</span>
          <span class="search-result__sub">${escHtml(sub)}</span>
        </span>
      </a>`;
    }).join("");
    resultsEl.hidden = false;
  }

  /* Very lightweight fuzzy: checks if all chars of needle appear in order in haystack */
  function fuzzyMatch(haystack, needle) {
    let hi = 0;
    for (let ni = 0; ni < needle.length; ni++) {
      const idx = haystack.indexOf(needle[ni], hi);
      if (idx === -1) return false;
      hi = idx + 1;
    }
    return true;
  }

  function highlight(text, q) {
    const re = new RegExp("(" + escRegex(q) + ")", "gi");
    return escHtml(text).replace(re, "<mark>$1</mark>");
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escRegex(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  /* ============================================================
     7. AI ask box — streaming via SSE
     Uses /api/ask/stream/ (Server-Sent Events).
     Falls back to /api/ask/ (blocking JSON) if fetch streaming is
     not available (e.g. very old browsers).
     ============================================================ */
  function initAskBox() {
    const form = document.getElementById("ask-form");
    if (!form) return;

    const input         = document.getElementById("ask-input");
    const statusEl      = document.getElementById("ask-status");
    const answerCard    = document.getElementById("answer-card");
    const answerText    = document.getElementById("answer-text");
    const providerBadge = document.getElementById("provider-badge");
    const micBtn        = document.getElementById("ask-mic-btn");
    const readBtn       = document.getElementById("read-answer-btn");
    let abortCtrl       = null;

    if (micBtn && input) {
      setupVoiceButton(micBtn, input, (text) => {
        input.value = text;
        form.requestSubmit();
      });
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const question = (input.value || "").trim();
      if (!question) return;

      /* Cancel any in-flight request */
      if (abortCtrl) abortCtrl.abort();
      abortCtrl = new AbortController();

      /* Reset UI */
      answerCard.classList.add("is-hidden");
      answerText.textContent = "";
      answerCard.dataset.answer = "";
      setAskStatus("thinking");

      /* ── Streaming path ─────────────────────────────────────── */
      try {
        const resp = await fetch("/api/ask/stream/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: new URLSearchParams({ question }),
          signal: abortCtrl.signal,
        });

        if (!resp.ok) throw new Error("HTTP " + resp.status);

        /* Show the answer card immediately so text appears as it streams in */
        setAskStatus("");
        answerCard.classList.remove("is-hidden");

        const reader = resp.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let provider = "gemini";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          /* SSE lines: "data: {...}\n\n" */
          const lines = buffer.split("\n");
          buffer = lines.pop(); /* keep incomplete last line */

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith("data:")) continue;
            const jsonStr = trimmed.slice(5).trim();
            if (!jsonStr || jsonStr === "[DONE]") continue;

            let event;
            try { event = JSON.parse(jsonStr); } catch (_) { continue; }

            if (event.type === "chunk") {
              /* Append streamed token to the display */
              provider = event.provider || provider;
              answerText.textContent += event.text;
              answerCard.dataset.answer = answerText.textContent;
              providerBadge.textContent =
                provider === "ollama" ? t("provider_ollama") : t("provider_gemini");
            } else if (event.type === "done") {
              provider = event.provider || provider;
              providerBadge.textContent =
                provider === "ollama" ? t("provider_ollama") : t("provider_gemini");
              /* Announce first sentence to screen readers */
              const full = answerText.textContent;
              if (full) announce(full.slice(0, 120));
            } else if (event.type === "error") {
              answerText.textContent = t("no_answer");
              providerBadge.textContent = "—";
            }
          }
        }
        return; /* streaming finished cleanly */

      } catch (err) {
        if (err.name === "AbortError") return;
        /* Streaming failed — fall through to blocking fallback */
        console.warn("Streaming failed, falling back to blocking JSON:", err.message);
      }

      /* ── Non-streaming fallback ─────────────────────────────── */
      try {
        const resp = await fetch("/api/ask/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: new URLSearchParams({ question }),
          signal: abortCtrl.signal,
        });
        const data = await resp.json();
        if (!resp.ok || data.error) throw new Error(data.error || resp.statusText);

        setAskStatus("");
        answerText.textContent = data.answer;
        answerCard.dataset.answer = data.answer;
        providerBadge.textContent =
          data.provider === "ollama" ? t("provider_ollama") : t("provider_gemini");
        answerCard.classList.remove("is-hidden");
        announce(data.answer.slice(0, 120));
      } catch (err) {
        if (err.name === "AbortError") return;
        setAskStatus("");
        answerText.textContent = t("no_answer");
        providerBadge.textContent = "—";
        answerCard.classList.remove("is-hidden");
        answerCard.dataset.answer = "";
      }
    });

    function setAskStatus(state) {
      if (!statusEl) return;
      if (state === "thinking") {
        statusEl.innerHTML = `<span class="thinking-dots" aria-label="${t("thinking")}">
          <span>.</span><span>.</span><span>.</span>
        </span> ${escHtml(t("thinking"))}`;
        announce(t("thinking"));
      } else {
        statusEl.innerHTML = "";
      }
    }

    /* Read aloud */
    if (readBtn) {
      readBtn.addEventListener("click", () => {
        const text = answerCard.dataset.answer || (answerText ? answerText.textContent : "");
        speak(text, readBtn);
      });
    }

    /* Read page aloud */
    $$("[data-read-selector]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const el = $(btn.dataset.readSelector);
        if (!el) return;
        speak(el.innerText, btn);
      });
    });
  }

  /* ============================================================
     7b. Unified bar (home page)
     One input for both service search and AI questions.
     Submit flow: best (partial, case-insensitive) service match →
     open that service, otherwise fall back to the AI answer.
     ============================================================ */
  function initUnified() {
    const form = document.getElementById("unified-form");
    if (!form) return;

    const input         = document.getElementById("unified-input");
    const micBtn        = document.getElementById("unified-mic-btn");
    const results       = document.getElementById("unified-results");
    const statusEl      = document.getElementById("unified-status");
    const answerCard    = document.getElementById("answer-card");
    const answerText    = document.getElementById("answer-text");
    const providerBadge = document.getElementById("provider-badge");
    const readBtn       = document.getElementById("read-answer-btn");
    let abortCtrl       = null;

    /* Voice input → submit with the transcript */
    if (micBtn && input) {
      setupVoiceButton(micBtn, input, (text) => {
        input.value = text;
        form.requestSubmit();
      });
    }

    /* Live service dropdown while typing */
    if (input && results) {
      input.addEventListener("input", () => {
        const q = input.value.trim();
        if (q.length < 2) {
          results.innerHTML = "";
          results.hidden = true;
          return;
        }
        fetchSearch(q, results);
      });

      /* Close results on outside click */
      document.addEventListener("click", (e) => {
        if (!form.contains(e.target)) {
          results.innerHTML = "";
          results.hidden = true;
        }
      });
    }

    /* Quick service chips */
    $$("#service-chips [data-href]").forEach((chip) => {
      chip.addEventListener("click", () => {
        window.location.href = chip.dataset.href;
      });
    });

    /* Submit: open the best partial service match, else ask the AI */
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const question = (input.value || "").trim();
      if (!question) return;

      const match = bestServiceMatch(question);
      if (match) {
        window.location.href = match;
        return;
      }

      /* No service match → AI answer (services-first fallback) */
      if (abortCtrl) abortCtrl.abort();
      abortCtrl = new AbortController();

      /* Reset UI */
      answerCard.classList.add("is-hidden");
      answerText.textContent = "";
      answerCard.dataset.answer = "";
      setUnifiedStatus("thinking");

      /* ── Streaming path ─────────────────────────────────────── */
      try {
        const resp = await fetch("/api/ask/stream/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: new URLSearchParams({ question }),
          signal: abortCtrl.signal,
        });

        if (!resp.ok) throw new Error("HTTP " + resp.status);

        /* Show the answer card immediately so text appears as it streams in */
        setUnifiedStatus("");
        answerCard.classList.remove("is-hidden");

        const reader = resp.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let provider = "gemini";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          /* SSE lines: "data: {...}\n\n" */
          const lines = buffer.split("\n");
          buffer = lines.pop(); /* keep incomplete last line */

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith("data:")) continue;
            const jsonStr = trimmed.slice(5).trim();
            if (!jsonStr || jsonStr === "[DONE]") continue;

            let event;
            try { event = JSON.parse(jsonStr); } catch (_) { continue; }

            if (event.type === "chunk") {
              /* Append streamed token to the display */
              provider = event.provider || provider;
              answerText.textContent += event.text;
              answerCard.dataset.answer = answerText.textContent;
              providerBadge.textContent =
                provider === "ollama" ? t("provider_ollama") : t("provider_gemini");
            } else if (event.type === "done") {
              provider = event.provider || provider;
              providerBadge.textContent =
                provider === "ollama" ? t("provider_ollama") : t("provider_gemini");
              const full = answerText.textContent;
              if (full) announce(full.slice(0, 120));
            } else if (event.type === "error") {
              answerText.textContent = t("no_answer");
              providerBadge.textContent = "—";
            }
          }
        }
        return; /* streaming finished cleanly */

      } catch (err) {
        if (err.name === "AbortError") return;
        console.warn("Streaming failed, falling back to blocking JSON:", err.message);
      }

      /* ── Non-streaming fallback ─────────────────────────────── */
      try {
        const resp = await fetch("/api/ask/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: new URLSearchParams({ question }),
          signal: abortCtrl.signal,
        });
        const data = await resp.json();
        if (!resp.ok || data.error) throw new Error(data.error || resp.statusText);

        setUnifiedStatus("");
        answerText.textContent = data.answer;
        answerCard.dataset.answer = data.answer;
        providerBadge.textContent =
          data.provider === "ollama" ? t("provider_ollama") : t("provider_gemini");
        answerCard.classList.remove("is-hidden");
        announce(data.answer.slice(0, 120));
      } catch (err) {
        if (err.name === "AbortError") return;
        setUnifiedStatus("");
        answerText.textContent = t("no_answer");
        providerBadge.textContent = "—";
        answerCard.classList.remove("is-hidden");
        answerCard.dataset.answer = "";
      }
    });

    function setUnifiedStatus(state) {
      if (!statusEl) return;
      if (state === "thinking") {
        statusEl.innerHTML = `<span class="thinking-dots" aria-label="${t("thinking")}">
          <span>.</span><span>.</span><span>.</span>
        </span> ${t("thinking")}`;
        announce(t("thinking"));
      } else {
        statusEl.innerHTML = "";
      }
    }

    /* Read the answer aloud */
    if (readBtn && answerCard) {
      readBtn.addEventListener("click", () => {
        const text = answerCard.dataset.answer || (answerText ? answerText.textContent : "");
        speak(text, readBtn);
      });
    }
  }

  /* Best partial (case-insensitive) service match for a query.
     Ranking: exact name > name contains query > tags contain query >
     fuzzy (chars in order). Returns the service URL or null. */
  function bestServiceMatch(q) {
    const ql = q.toLowerCase().trim();
    if (ql.length < 2) return null;

    let best = null;
    let bestScore = 0;

    $$("[data-service-name]").forEach((el) => {
      const name = (el.dataset.serviceName || "").toLowerCase();
      const tags = (el.dataset.serviceTags || "").toLowerCase();

      let score = 0;
      if (name === ql) score = 100;
      else if (name.includes(ql)) score = 80;
      else if (tags.includes(ql)) score = 60;
      else if (fuzzyMatch(name, ql) || fuzzyMatch(tags, ql)) score = 40;

      if (score > bestScore) {
        bestScore = score;
        best = el.href || el.dataset.href || null;
      }
    });

    return best;
  }

  /* ============================================================
     8. Read-aloud (text-to-speech)
     Two engines:
       1. Web Speech API speechSynthesis — used when the browser
          exposes usable voices (Google Chrome ships Google cloud
          voices: en + Devanagari-capable voices for Nepali).
       2. Offline server fallback GET /api/tts/ (espeak-ng) — used
          when speechSynthesis has no voices. Brave strips Google's
          voices and systems without speech-dispatcher report zero
          voices, so every utterance would fail with
          "synthesis-failed". espeak-ng covers en + ne locally.
     ============================================================ */
  let voices = [];
  let activeReading = null;

  function loadVoices() {
    voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
  }

  function pickVoice(forLang) {
    /* forLang: "ne" or "en" (or undefined — uses page lang) */
    const target = forLang || lang;
    if (target === "ne") {
      return (
        voices.find((v) => v.lang && v.lang.toLowerCase().startsWith("ne")) ||
        voices.find((v) => v.lang && /^(hi|bn|mr|ur)/.test(v.lang.toLowerCase())) ||
        voices[0] || null
      );
    }
    return (
      voices.find((v) => v.lang && v.lang.toLowerCase().startsWith("en")) ||
      voices[0] || null
    );
  }

  function ttsLangCode(forLang) {
    const target = forLang || lang;
    if (target === "ne") return "ne-NP";
    return "en-US";
  }

  if (window.speechSynthesis) {
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }

  /* Web Speech is usable only when a voice that can actually read the
     target language exists — otherwise speak() would silently pick an
     unrelated language voice (or fail outright) and produce nothing. */
  function canUseWebSpeech(forLang) {
    if (!window.speechSynthesis || !voices.length) return false;
    const target = forLang || lang;
    if (target === "ne") {
      return voices.some((v) => /^(ne|hi|bn|mr|ur)/.test((v.lang || "").toLowerCase()));
    }
    return true;
  }

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
        while (piece.length > 180) { out.push(piece.slice(0, 180)); piece = piece.slice(180); }
        buf = piece;
      }
    }
    if (buf) out.push(buf);
    return out;
  }

  function isActiveReading(btn, token) {
    return !!(activeReading && activeReading.btn === btn && activeReading.token === token);
  }

  function prepareReading(btn) {
    if (!btn.dataset.origText) btn.dataset.origText = btn.textContent.trim();
    btn.textContent = t("stop_reading");
    btn.classList.add("is-speaking");
  }

  function finishReading(btn) {
    activeReading = null;
    btn.classList.remove("is-speaking");
    if (btn.dataset.origText) {
      btn.textContent = btn.dataset.origText;
      delete btn.dataset.origText;
    }
  }

  function stopReading() {
    if (!activeReading) return;
    const { btn, kind, audio } = activeReading;
    activeReading = null; /* invalidate tokens before touching the engine */
    if (kind === "web" && window.speechSynthesis) {
      try { window.speechSynthesis.cancel(); } catch (_) {}
    }
    if (kind === "server" && audio) {
      audio.onended = audio.onerror = null;
      try { audio.pause(); audio.removeAttribute("src"); } catch (_) {}
    }
    finishReading(btn);
  }

  function speak(text, btn, forLang) {
    if (!text || !text.trim()) return;
    /* Clicking the button while it is reading toggles to stop. */
    if (activeReading && activeReading.btn === btn) { stopReading(); return; }
    stopReading(); /* one reading at a time */
    const trimmed = text.trim();
    if (canUseWebSpeech(forLang)) speakWithWebSpeech(trimmed, btn, forLang);
    else speakWithServer(trimmed, btn, forLang);
  }

  function speakWithWebSpeech(text, btn, forLang) {
    const chunks = chunkText(text);
    if (!chunks.length) return;
    prepareReading(btn);
    const token = {};
    activeReading = { btn, token, kind: "web" };
    const voice = pickVoice(forLang);
    const langCode = ttsLangCode(forLang);
    let i = 0;
    let serverRetried = false;

    const next = () => {
      if (!isActiveReading(btn, token)) return;
      if (i >= chunks.length) { finishReading(btn); return; }
      const u = new SpeechSynthesisUtterance(chunks[i++]);
      u.lang = langCode;
      if (voice) u.voice = voice;
      u.rate = 0.92;
      u.onend = next;
      u.onerror = () => {
        /* synthesis-failed (stale or vanished voices) — retry the remaining
           text once with the offline server engine instead of silently
           skipping to the end. */
        if (!serverRetried) {
          serverRetried = true;
          speakWithServer(chunks.slice(i - 1).join(" "), btn, forLang, true);
          return;
        }
        next();
      };
      try { window.speechSynthesis.speak(u); } catch (_) { next(); }
    };
    next();
  }

  function speakWithServer(text, btn, forLang, alreadyPrepared) {
    const target = forLang || lang;
    const chunks = chunkText(text); /* ≤180 chars — safe to put in a URL */
    if (!chunks.length) return;
    if (!alreadyPrepared) prepareReading(btn);
    const token = {};
    const audio = new Audio();
    activeReading = { btn, token, kind: "server", audio };
    let i = 0;

    const fail = () => {
      if (!isActiveReading(btn, token)) return;
      finishReading(btn);
      showToast(t("tts_failed"), "warning");
    };

    const playNext = () => {
      if (!isActiveReading(btn, token)) return;
      if (i >= chunks.length) { finishReading(btn); return; }
      audio.src = "/api/tts/?lang=" + encodeURIComponent(target) +
                  "&text=" + encodeURIComponent(chunks[i++]);
      const p = audio.play();
      if (p && p.catch) p.catch(fail);
    };

    audio.onended = playNext;
    audio.onerror = fail;
    playNext();
  }

  /* ============================================================
     9. Checklist
     ============================================================ */
  function initChecklist() {
    const slug = document.body.dataset.serviceSlug || "";
    const STORE = "sathi:checklist:" + (slug || "global");
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem(STORE) || "{}"); } catch (_) {}

    const items = $$(".check-item");

    items.forEach((item) => {
      const id = item.dataset.id;
      if (saved[id]) {
        item.classList.add("is-checked");
        item.setAttribute("aria-checked", "true");
      }

      const toggle = () => {
        const checked = item.classList.toggle("is-checked");
        item.setAttribute("aria-checked", checked ? "true" : "false");
        saved[id] = checked;
        try { localStorage.setItem(STORE, JSON.stringify(saved)); } catch (_) {}
        updateProgress();
      };

      item.addEventListener("click", toggle);
      item.addEventListener("keydown", (e) => {
        if (e.key === " " || e.key === "Enter") { e.preventDefault(); toggle(); }
      });
    });

    updateProgress();

    function updateProgress() {
      const total = items.length;
      const done  = $$(".check-item.is-checked").length;
      const countEl = document.getElementById("check-count");
      const barFill = document.getElementById("progress-bar-fill");
      const barLabel= document.getElementById("progress-bar-label");
      if (countEl)  countEl.textContent = done + " / " + total + " " + t("progress");
      if (barFill)  barFill.style.width = (total ? Math.round(done / total * 100) : 0) + "%";
      if (barLabel) barLabel.textContent = done + " / " + total;
    }
  }

  /* ============================================================
     10. Accordion (steps + FAQs)
     ============================================================ */
  function initAccordion() {
    $$(".accordion__trigger").forEach((trigger) => {
      const panel   = document.getElementById(trigger.getAttribute("aria-controls"));
      const content = panel ? $(".accordion__content", panel) : null;
      if (!panel) return;

      /* Set initial max-height */
      const expanded = trigger.getAttribute("aria-expanded") === "true";
      panel.style.maxHeight = expanded ? panel.scrollHeight + "px" : "0";
      panel.style.overflow = "hidden";

      trigger.addEventListener("click", () => {
        const isOpen = trigger.getAttribute("aria-expanded") === "true";
        /* Close all siblings in the same accordion */
        const parent = trigger.closest(".accordion");
        if (parent) {
          $$(".accordion__trigger", parent).forEach((t2) => {
            if (t2 !== trigger) {
              t2.setAttribute("aria-expanded", "false");
              const p2 = document.getElementById(t2.getAttribute("aria-controls"));
              if (p2) p2.style.maxHeight = "0";
            }
          });
        }
        const next = !isOpen;
        trigger.setAttribute("aria-expanded", next ? "true" : "false");
        panel.style.maxHeight = next ? panel.scrollHeight + "px" : "0";
      });
    });
  }

  /* Expandable step details */
  function initStepToggles() {
    $$(".step__toggle").forEach((btn) => {
      const targetId = btn.getAttribute("aria-controls");
      const target   = targetId ? document.getElementById(targetId) : null;
      if (!target) return;

      const expanded = btn.getAttribute("aria-expanded") === "true";
      target.style.maxHeight = expanded ? target.scrollHeight + "px" : "0";
      target.style.overflow  = "hidden";
      target.style.transition = "max-height 0.2s ease-out";

      btn.addEventListener("click", () => {
        const isOpen = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", isOpen ? "false" : "true");
        target.style.maxHeight = isOpen ? "0" : target.scrollHeight + "px";
      });
    });
  }

  /* ============================================================
     11. Toast notifications
     ============================================================ */
  function showToast(msg, type, duration) {
    const region = document.getElementById("toast-region");
    if (!region) return;

    const toast = document.createElement("div");
    toast.className = "toast" + (type ? " toast--" + type : "");
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");

    const text = document.createElement("span");
    text.textContent = msg;
    toast.appendChild(text);

    const dismiss = document.createElement("button");
    dismiss.className = "toast__dismiss";
    dismiss.setAttribute("aria-label", "Dismiss");
    dismiss.textContent = "×";
    dismiss.addEventListener("click", () => removeToast(toast));
    toast.appendChild(dismiss);

    region.appendChild(toast);

    const ms = duration || 6000;
    setTimeout(() => removeToast(toast), ms);
  }

  function removeToast(toast) {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    toast.style.transition = "opacity 0.2s, transform 0.2s";
    setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 220);
  }

  /* ============================================================
     12. Checklist actions: copy, print, share
     ============================================================ */
  function initChecklistActions() {
    const copyBtn  = document.getElementById("checklist-copy");
    const shareBtn = document.getElementById("checklist-share");

    if (copyBtn) {
      copyBtn.addEventListener("click", () => {
        const lines = $$(".check-item").map((item) => {
          const checked = item.classList.contains("is-checked") ? "[x]" : "[ ]";
          const label   = ($(".check-item__label", item) || item).textContent.trim();
          const note    = $(".check-item__note", item);
          return checked + " " + label + (note ? " — " + note.textContent.trim() : "");
        });
        navigator.clipboard.writeText(lines.join("\n"))
          .then(() => showToast(t("copied"), "success"))
          .catch(() => showToast("Copy failed", "danger"));
      });
    }

    if (shareBtn) {
      shareBtn.addEventListener("click", async () => {
        const title    = document.title;
        const lines    = $$(".check-item").map((item) => {
          const label = ($(".check-item__label", item) || item).textContent.trim();
          return "• " + label;
        });
        const text = title + "\n\n" + lines.join("\n") + "\n\nsathi.app";
        if (navigator.share) {
          try { await navigator.share({ title, text }); } catch (_) {}
        } else {
          navigator.clipboard.writeText(text)
            .then(() => showToast(t("copied"), "success"))
            .catch(() => {});
        }
      });
    }
  }

  /* ============================================================
     13. "Ask about this service" prefill
     ============================================================ */
  function initAskPrefill() {
    $$("[data-ask-prefill]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const input = document.getElementById("ask-input");
        if (!input) return;
        input.value = btn.dataset.askPrefill;
        input.focus();
        const askSection = document.getElementById("ask");
        if (askSection) askSection.scrollIntoView({ behavior: "smooth", block: "start" });
        const form = document.getElementById("ask-form");
        if (form) setTimeout(() => form.requestSubmit(), 300);
      });
    });
  }

  /* ============================================================
     14. Service worker
     ============================================================ */
  function registerSW() {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/static/js/sw.js", { scope: "/" })
        .catch(() => {}); /* silently fail — offline is a bonus, not a requirement */
    }
  }

  /* ============================================================
     Boot
     ============================================================ */
  document.addEventListener("DOMContentLoaded", () => {
    initModeToggle();
    initTextSize();
    initSearchBar();
    initAskBox();
    initUnified();
    initChecklist();
    initAccordion();
    initStepToggles();
    initChecklistActions();
    initAskPrefill();
    registerSW();

    /* Expose showToast globally for inline use if needed */
    window.sathiToast = showToast;
  });

})();
