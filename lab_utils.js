/**
 * Готовые технические утилиты для лабораторных работ.
 * Здесь нет алгоритма загрузки модели и нет алгоритма поиска фона/заставки.
 */
(function initLabUtils(global) {
  const DEFAULT_LAB_CONFIG = {
    catalogs: {
      backgrounds: "/test_assets/manifests/backgrounds.json",
      screensavers: "/test_assets/manifests/screensavers.json",
      models: "/test_assets/manifests/models.json",
    },
    sources: {
      local: "/test_assets/models",
      http: "/test_assets/models",
      cdn: "/test_assets/models",
      delayed: "/test_assets/models",
      errors: "/test_assets/missing",
    },
  };

  if (!global.MOTION_LAB_CONFIG) {
    global.MOTION_LAB_CONFIG = JSON.parse(JSON.stringify(DEFAULT_LAB_CONFIG));
  }
  if (!Array.isArray(global.motionBrowserEvents)) {
    global.motionBrowserEvents = [];
  }

  function recordBrowserEvent(name, detail) {
    const entry = {
      name,
      detail: detail ?? null,
      ts: global.performance ? performance.now() : Date.now(),
      wallTs: Date.now(),
    };
    global.motionBrowserEvents.push(entry);
    return entry;
  }

  function getLabConfig() {
    return global.MOTION_LAB_CONFIG || DEFAULT_LAB_CONFIG;
  }

  function getConfiguredSourceBaseUrl(sourceType) {
    const sources = getLabConfig().sources || {};
    return String(sources[sourceType] || "");
  }

  async function fetchModelResource(url, options = {}) {
    const timeoutMs = Number(options.timeoutMs || 8000);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, {
        cache: "no-store",
        signal: controller.signal,
        headers: options.headers || {},
      });
      if (!response.ok) {
        const error = new Error(`HTTP ${response.status}`);
        error.status = response.status;
        error.url = url;
        throw error;
      }
      const contentType = response.headers.get("content-type") || "";
      if (contentType.includes("application/json") || url.endsWith(".json")) {
        return response.json();
      }
      return response.text();
    } finally {
      clearTimeout(timer);
    }
  }

  function validateModelData(data) {
    if (!data || typeof data !== "object") return false;
    if (!data.id || !data.name || !data.type) return false;
    if (data.type !== "css") return false;
    const shape = data.shape || "circle";
    if (!["circle", "square", "cube"].includes(shape)) return false;
    return true;
  }

  function normalizeModelData(data) {
    return {
      id: String(data.id),
      name: String(data.name),
      type: "css",
      shape: data.shape === "square" || data.shape === "cube" ? data.shape : "circle",
      previewColor: data.previewColor || "#38BDF8",
      stageBackground: data.stageBackground || "#0EA5E9",
      use3d: Boolean(data.use3d || data.shape === "cube"),
      source: data.source || "",
    };
  }

  function renderLoadedModel(model) {
    if (!global.motionState) {
      throw new Error("Приложение ещё не готово");
    }
    global.motionState.loadedModel = model;
    recordBrowserEvent("model-loaded", { id: model?.id, name: model?.name });
    global.dispatchEvent(new CustomEvent("motion:model-loaded", { detail: model }));
    if (typeof global.motionApplyLoadedModel === "function") {
      global.motionApplyLoadedModel();
    }
    const nameEl = document.getElementById("loadedModelName");
    if (nameEl) nameEl.textContent = model?.name || "";
    const statusEl = document.getElementById("modelLoadStatus");
    if (statusEl) {
      statusEl.textContent = model?.name ? `Модель: ${model.name}` : "";
      statusEl.classList.add("online");
      statusEl.classList.remove("offline");
    }
    const errorEl = document.getElementById("modelLoadError");
    if (errorEl) {
      errorEl.hidden = true;
      errorEl.textContent = "";
    }
    return model;
  }

  function showModelLoadError(message) {
    recordBrowserEvent("model-load-error", { message });
    global.dispatchEvent(new CustomEvent("motion:model-load-error", { detail: { message } }));
    const statusEl = document.getElementById("modelLoadStatus");
    if (statusEl) {
      statusEl.textContent = "Ошибка загрузки модели";
      statusEl.classList.add("offline");
      statusEl.classList.remove("online");
    }
    const errorEl = document.getElementById("modelLoadError");
    if (errorEl) {
      errorEl.hidden = false;
      errorEl.textContent = message;
    }
  }

  async function fetchJsonResource(url, options = {}) {
    const data = await fetchModelResource(url, options);
    if (typeof data === "string") return JSON.parse(data);
    return data;
  }

  async function getBackgroundCatalog() {
    const url = getLabConfig().catalogs?.backgrounds;
    const payload = await fetchJsonResource(url);
    return Array.isArray(payload) ? payload : payload.items || [];
  }

  async function getScreensaverCatalog() {
    const url = getLabConfig().catalogs?.screensavers;
    const payload = await fetchJsonResource(url);
    return Array.isArray(payload) ? payload : payload.items || [];
  }

  /**
   * Технический фильтр по подстроке. Это не готовый поиск:
   * стратегию совпадений, коллизии и проверку доступности пишет студент.
   */
  function filterCatalogItems(items, query, fields = ["name", "tags", "id"]) {
    const needle = String(query || "").trim().toLowerCase();
    if (!needle) return [];
    return (items || []).filter((item) =>
      fields.some((field) => {
        const value = item?.[field];
        if (Array.isArray(value)) {
          return value.some((part) => String(part).toLowerCase().includes(needle));
        }
        return String(value || "").toLowerCase().includes(needle);
      }),
    );
  }

  async function checkImageAvailability(url, options = {}) {
    if (!url) return false;
    const timeoutMs = Number(options.timeoutMs || 5000);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, { method: "GET", cache: "no-store", signal: controller.signal });
      if (!response.ok) return false;
      const buffer = await response.arrayBuffer();
      if (!buffer || buffer.byteLength < 8) return false;
      const bytes = new Uint8Array(buffer);
      const isPng = bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47;
      const isSvg = new TextDecoder().decode(bytes.slice(0, 64)).includes("<svg");
      const isJpeg = bytes[0] === 0xff && bytes[1] === 0xd8;
      return isPng || isSvg || isJpeg;
    } catch {
      return false;
    } finally {
      clearTimeout(timer);
    }
  }

  async function measureOperationTime(operation) {
    const started = performance.now();
    const result = await operation();
    return { result, durationMs: performance.now() - started };
  }

  function applyStageBackground(url) {
    const stage = document.getElementById("stage");
    const backdrop = document.getElementById("stageBackdrop");
    if (backdrop) {
      if (url) {
        backdrop.hidden = false;
        backdrop.style.backgroundImage = `url("${url}")`;
      } else {
        backdrop.hidden = true;
        backdrop.style.backgroundImage = "";
      }
    } else if (stage) {
      stage.style.backgroundImage = url ? `url("${url}")` : "";
    }
    const status = document.getElementById("backgroundStatus");
    if (status) status.textContent = url ? "Фон применён" : "Фон не выбран";
    recordBrowserEvent("background-applied", { url: url || "" });
  }

  function applyScreensaver(url) {
    const overlay = document.getElementById("screensaverOverlay");
    const image = document.getElementById("screensaverImage");
    if (overlay) overlay.hidden = !url;
    if (image) image.src = url || "";
    const status = document.getElementById("screensaverStatus");
    if (status) status.textContent = url ? "Заставка показана" : "Заставка не выбрана";
    recordBrowserEvent("screensaver-applied", { url: url || "" });
  }

  function motionGetAnimationsInfo() {
    const actor = document.getElementById("actor");
    if (!actor || typeof actor.getAnimations !== "function") return [];
    return actor.getAnimations().map((animation) => {
      const timing = animation.effect?.getComputedTiming?.() || {};
      return {
        playState: animation.playState,
        currentTime: animation.currentTime,
        duration: timing.duration,
        iterations: timing.iterations,
        delay: timing.delay,
      };
    });
  }

  function motionGetComputedTransform(selector) {
    const el = document.querySelector(selector);
    if (!el) return null;
    const style = getComputedStyle(el);
    return {
      transform: style.transform,
      opacity: style.opacity,
      display: style.display,
      visibility: style.visibility,
      perspective: style.perspective,
      transformStyle: style.transformStyle,
    };
  }

  global.recordBrowserEvent = recordBrowserEvent;
  global.getLabConfig = getLabConfig;
  global.getConfiguredSourceBaseUrl = getConfiguredSourceBaseUrl;
  global.fetchModelResource = fetchModelResource;
  global.validateModelData = validateModelData;
  global.normalizeModelData = normalizeModelData;
  global.renderLoadedModel = renderLoadedModel;
  global.showModelLoadError = showModelLoadError;
  global.getBackgroundCatalog = getBackgroundCatalog;
  global.getScreensaverCatalog = getScreensaverCatalog;
  global.filterCatalogItems = filterCatalogItems;
  global.checkImageAvailability = checkImageAvailability;
  global.measureOperationTime = measureOperationTime;
  global.applyStageBackground = applyStageBackground;
  global.applyScreensaver = applyScreensaver;
  global.motionGetAnimationsInfo = motionGetAnimationsInfo;
  global.motionGetComputedTransform = motionGetComputedTransform;
})(window);
