/* Campus Latina · comportamiento del frontend (Alpine.js + Lucide). */
(function () {
  "use strict";

  // ---------- Utilidades ----------
  function csrf() {
    const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  function postJSON(url, data, opts) {
    return fetch(url, Object.assign({
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf(), "Accept": "application/json" },
      body: JSON.stringify(data || {}),
      credentials: "same-origin",
    }, opts || {})).then(function (r) { return r.ok ? r.json() : Promise.reject(r); });
  }

  function storage(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      if (value === null) localStorage.removeItem(key); else localStorage.setItem(key, value);
    } catch (e) { return null; }
  }

  function icons() { if (window.lucide) window.lucide.createIcons(); }

  function toast(text, kind) {
    let box = document.querySelector(".toasts");
    if (!box) { box = document.createElement("div"); box.className = "toasts"; document.body.appendChild(box); }
    const el = document.createElement("div");
    el.className = "toast " + (kind || "info");
    el.innerHTML = '<i data-lucide="' + (kind === "success" ? "check-circle-2" : kind === "error" ? "alert-circle" : "info") + '" class="icon"></i><p></p>';
    el.querySelector("p").textContent = text;
    box.appendChild(el);
    icons();
    setTimeout(function () { el.remove(); }, 5000);
  }

  function celebrate() {
    if (!window.confetti) return;
    const colors = ["#0A1C40", "#E3000F", "#FACC00", "#ffffff"];
    window.confetti({ particleCount: 140, spread: 80, origin: { y: .6 }, colors: colors });
    setTimeout(function () { window.confetti({ particleCount: 90, angle: 60, spread: 60, origin: { x: 0 }, colors: colors }); }, 250);
    setTimeout(function () { window.confetti({ particleCount: 90, angle: 120, spread: 60, origin: { x: 1 }, colors: colors }); }, 400);
  }

  window.Campus = { csrf: csrf, postJSON: postJSON, toast: toast, celebrate: celebrate, icons: icons };

  // ---------- Tema ----------
  function applyTheme(mode) {
    const root = document.documentElement;
    if (mode === "light" || mode === "dark") root.setAttribute("data-theme", mode);
    else root.removeAttribute("data-theme");
  }

  document.addEventListener("alpine:init", function () {
    const Alpine = window.Alpine;

    Alpine.data("themeToggle", function () {
      return {
        mode: storage("campus-theme") || "system",
        get isDark() {
          if (this.mode === "system") return window.matchMedia("(prefers-color-scheme: dark)").matches;
          return this.mode === "dark";
        },
        toggle() {
          this.mode = this.isDark ? "light" : "dark";
          storage("campus-theme", this.mode);
          applyTheme(this.mode);
        },
      };
    });

    // ---------- Reproductor de lecciones ----------
    Alpine.data("lessonPlayer", function (cfg) {
      return {
        completed: !!cfg.completed,
        canSkip: !!cfg.canSkip,
        percent: cfg.percent || 0,
        watched: 0,
        duration: 0,
        maxTime: cfg.maxTime || 0,
        busy: false,
        lastSave: 0,
        sideOpen: false,
        lessonsDone: !!cfg.lessonsDone,
        init() {
          const video = this.$refs.video;
          if (video) this.bindVideo(video);
          if (cfg.kind === "youtube" && cfg.youtubeId) this.bindYouTube();
          window.addEventListener("beforeunload", () => this.savePosition(true));
        },
        get watchPercent() { return this.duration ? Math.min(100, Math.round(this.maxTime * 100 / this.duration)) : 0; },
        bindVideo(video) {
          const self = this;
          video.addEventListener("loadedmetadata", function () {
            self.duration = video.duration || 0;
            if (cfg.startAt && cfg.startAt < video.duration - 3) video.currentTime = cfg.startAt;
          });
          video.addEventListener("timeupdate", function () {
            if (!video.seeking && video.currentTime > self.maxTime) self.maxTime = video.currentTime;
            if (Date.now() - self.lastSave > 10000) self.savePosition();
          });
          video.addEventListener("seeking", function () {
            if (self.canSkip || self.completed) return;
            if (video.currentTime > self.maxTime + 1.5) {
              video.currentTime = self.maxTime;
              toast("Debes ver el video completo antes de adelantarlo.", "warning");
            }
          });
          video.addEventListener("ratechange", function () {
            if (!self.canSkip && !self.completed && video.playbackRate > 2) video.playbackRate = 2;
          });
          video.addEventListener("ended", function () { self.maxTime = video.duration; self.complete(true); });
          video.addEventListener("pause", function () { self.savePosition(); });
        },
        bindYouTube() {
          const self = this;
          window.onYouTubeIframeAPIReady = function () {
            // eslint-disable-next-line no-new
            new window.YT.Player("yt-player", {
              videoId: cfg.youtubeId,
              playerVars: { rel: 0, modestbranding: 1 },
              events: {
                onStateChange: function (e) { if (e.data === window.YT.PlayerState.ENDED) self.complete(true); },
              },
            });
          };
          const tag = document.createElement("script");
          tag.src = "https://www.youtube.com/iframe_api";
          document.head.appendChild(tag);
        },
        savePosition(onUnload) {
          const video = this.$refs.video;
          if (!video || !cfg.positionUrl) return;
          this.lastSave = Date.now();
          const payload = { position: video.currentTime || 0, max: this.maxTime || 0 };
          // keepalive permite que el guardado termine aunque se cierre la página.
          postJSON(cfg.positionUrl, payload, { keepalive: !!onUnload }).catch(function () {});
        },
        get mustWatch() { return cfg.kind === "video" && !this.canSkip && !this.completed; },
        complete(auto) {
          if (this.busy) return;
          if (this.completed && auto) return;
          this.busy = true;
          postJSON(cfg.completeUrl, {}, { keepalive: true }).then((data) => {
            const first = !this.completed;
            this.completed = true;
            this.percent = data.percent;
            this.lessonsDone = data.lessons_done;
            const mark = document.querySelector('[data-lesson-status="' + cfg.lessonId + '"]');
            if (mark) { mark.classList.add("done"); mark.innerHTML = '<i data-lucide="check" class="icon" style="width:13px;height:13px"></i>'; icons(); }
            if (first) toast(auto ? "¡Lección completada! +10 puntos" : "Lección marcada como completada. +10 puntos", "success");
            if (data.certificate_url && first) { celebrate(); setTimeout(function () { window.location = data.certificate_url; }, 1800); }
          }).catch(function () { toast("No se pudo guardar tu avance. Revisa tu conexión.", "error"); })
            .finally(() => { this.busy = false; });
        },
      };
    });

    // ---------- Evaluación ----------
    Alpine.data("quizRunner", function (cfg) {
      return {
        current: 0,
        total: cfg.total,
        remaining: cfg.remaining,
        answers: Object.assign({}, cfg.answers || {}),
        submitting: false,
        timer: null,
        init() {
          const self = this;
          const deadline = Date.now() + this.remaining * 1000;
          this.timer = setInterval(function () {
            self.remaining = Math.max(0, Math.round((deadline - Date.now()) / 1000));
            if (self.remaining <= 0) { clearInterval(self.timer); self.timeUp(); }
          }, 500);
          window.addEventListener("beforeunload", function (e) {
            if (!self.submitting) { e.preventDefault(); e.returnValue = ""; }
          });
          document.addEventListener("contextmenu", function (e) { e.preventDefault(); });
          document.addEventListener("copy", function (e) { e.preventDefault(); });
        },
        get clock() {
          const m = Math.floor(this.remaining / 60), s = this.remaining % 60;
          return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
        },
        get answeredCount() { return Object.keys(this.answers).length; },
        get timerClass() { return this.remaining <= 30 ? "danger" : this.remaining <= 60 ? "warn" : ""; },
        pick(qid, cid) {
          this.answers[qid] = cid;
          const payload = {}; payload[qid] = cid;
          postJSON(cfg.autosaveUrl, { answers: payload }).catch(function () {});
          if (this.current < this.total - 1) setTimeout(() => { this.current++; }, 260);
        },
        go(i) { this.current = Math.max(0, Math.min(this.total - 1, i)); },
        submit() {
          const missing = this.total - this.answeredCount;
          if (missing > 0 && !window.confirm("Te faltan " + missing + " pregunta(s) por responder. ¿Enviar de todas formas?")) return;
          this.submitting = true;
          this.$refs.form.submit();
        },
        timeUp() {
          this.submitting = true;
          this.$refs.timeout.value = "1";
          this.$refs.timeupModal.style.display = "flex";
          setTimeout(() => this.$refs.form.submit(), 2500);
        },
      };
    });

    // ---------- Guardar curso ----------
    Alpine.data("saveToggle", function (cfg) {
      return {
        saved: !!cfg.saved,
        toggle() {
          postJSON(cfg.url, {}).then((d) => {
            this.saved = d.saved;
            toast(d.saved ? "Curso guardado en Mi aprendizaje." : "Curso quitado de guardados.", "success");
          });
        },
      };
    });
  });

  // ---------- Al cargar ----------
  document.addEventListener("DOMContentLoaded", function () {
    icons();
    document.querySelectorAll(".toast").forEach(function (el, i) {
      setTimeout(function () { el.style.transition = "opacity .4s"; el.style.opacity = "0"; setTimeout(function () { el.remove(); }, 400); }, 5000 + i * 600);
    });
    document.addEventListener("submit", function (e) {
      const msg = e.target.getAttribute("data-confirm");
      if (msg && !window.confirm(msg)) e.preventDefault();
    });
    document.addEventListener("click", function (e) {
      const btn = e.target.closest("[data-copy]");
      if (!btn) return;
      navigator.clipboard.writeText(btn.getAttribute("data-copy")).then(function () { toast("Enlace copiado.", "success"); });
    });
    if (document.body.dataset.celebrate) celebrate();

    // Editor enriquecido (Quill) para el contenido de lecciones
    document.querySelectorAll("textarea[data-rich-editor]").forEach(function (area) {
      if (!window.Quill) return;
      const holder = document.createElement("div");
      area.style.display = "none";
      area.removeAttribute("required");
      area.parentNode.insertBefore(holder, area.nextSibling);
      const quill = new window.Quill(holder, {
        theme: "snow",
        placeholder: "Escribe el contenido de la lección…",
        modules: { toolbar: [[{ header: [2, 3, false] }], ["bold", "italic", "underline"], [{ list: "ordered" }, { list: "bullet" }], ["blockquote", "link", "image"], [{ align: [] }], ["clean"]] },
      });
      quill.clipboard.dangerouslyPasteHTML(area.value || "");
      area.form.addEventListener("submit", function () {
        area.value = quill.getText().trim() ? quill.root.innerHTML : "";
      });
    });
  });
})();
