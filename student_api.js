/**
 * Студенческие методы лабораторных работ 1 и 7.
 * Основную логику реализует студент. Инфраструктура уже подключена.
 */
(function initStudentApi(global) {
  /**
   * Загружает модель из выбранного источника.
   *
   * TODO:
   * 1. Определить источник.
   * 2. Получить данные модели.
   * 3. Проверить корректность данных.
   * 4. Обработать ошибки.
   * 5. Передать модель в механизм отображения.
   *
   * Рекомендуемые утилиты:
   * - getConfiguredSourceBaseUrl()
   * - fetchModelResource()
   * - validateModelData()
   * - normalizeModelData()
   * - renderLoadedModel()
   * - showModelLoadError()
   */
  async function loadModel(sourceType, modelId) {
    // TODO: Реализовать загрузку.
    throw new Error("Not implemented");
  }

  /**
   * Поиск фонового изображения.
   *
   * TODO:
   * 1. Получить параметры поиска.
   * 2. Получить каталог фонов.
   * 3. Выполнить поиск.
   * 4. Обработать несколько совпадений.
   * 5. Проверить доступность изображения.
   * 6. Вернуть результат или отсутствие результата.
   *
   * Рекомендуемые утилиты:
   * - getBackgroundCatalog()
   * - filterCatalogItems()
   * - checkImageAvailability()
   * - applyStageBackground()
   */

   async function searchVisualAsset(query, options, catalogGetter, applyAsset) {
    const normalizedQuery = String(query ?? "").trim();

    if (!normalizedQuery) return null;

    const {
      fields = ["name", "tags", "id"],
      apply = true,
      timeoutMs,
    } = options || {};

    if (typeof catalogGetter !== "function") {
      throw new Error("Функция получения каталога недоступна");
    }

    if (typeof global.filterCatalogItems !== "function") {
      throw new Error("Фильтр каталога недоступен");
    }

    if (typeof global.checkImageAvailability !== "function") {
      throw new Error("Проверка изображений недоступна");
    }

    const catalog = await catalogGetter();

    if (!Array.isArray(catalog)) {
      return null;
    }

    const candidates = global.filterCatalogItems(
      catalog,
      normalizedQuery,
      fields,
    );

    if (!candidates.length) {
      return null;
    }

    // Проверяем все совпадения, сохраняя исходный порядок каталога.
    const availability = await Promise.all(
      candidates.map(async (item) => {
        if (!item || !item.url) return false;

        try {
          return await global.checkImageAvailability(item.url, {
            timeoutMs,
          });
        } catch {
          return false;
        }
      }),
    );

    const validResults = candidates.filter(
      (_, index) => availability[index],
    );

    if (!validResults.length) {
      return null;
    }

    // Возвращаем все валидные результаты.
    // На сцене одновременно отображается первое совпадение.
    if (apply !== false && typeof applyAsset === "function") {
      applyAsset(validResults[0].url);
    }

    return validResults;
  }

  async function findBackground(query, options = {}) {
    return searchVisualAsset(
      query,
      options,
      global.getBackgroundCatalog,
      global.applyStageBackground,
    );
  }

  async function findScreensaver(query, options = {}) {
    return searchVisualAsset(
      query,
      options,
      global.getScreensaverCatalog,
      global.applyScreensaver,
    );
  }

  function setStatus(id, text, ok) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    el.classList.toggle("online", Boolean(ok));
    el.classList.toggle("offline", ok === false);
  }

  async function onLoadModelClick() {
    const sourceType = document.getElementById("modelSourceSelect")?.value;
    const modelId = document.getElementById("modelIdInput")?.value?.trim();
    setStatus("modelLoadStatus", "Загрузка…", false);
    try {
      const model = await loadModel(sourceType, modelId);
      setStatus("modelLoadStatus", `Модель: ${model?.name || modelId}`, true);
    } catch (err) {
      if (typeof global.showModelLoadError === "function") {
        global.showModelLoadError(err.message || String(err));
      } else {
        setStatus("modelLoadStatus", err.message || String(err), false);
      }
    }
  }

async function onFindBackgroundClick() {
  const query = document.getElementById("backgroundQuery")?.value || "";

  setStatus("backgroundStatus", "Поиск фона…", false);

  try {
    const results = await findBackground(query, {});

    if (!results) {
      setStatus("backgroundStatus", "Фон не найден", false);
      return;
    }

    const first = results[0];

    setStatus(
      "backgroundStatus",
      `Найдено фонов: ${results.length}. Применён: ${first.name || first.id}`,
      true,
    );
  } catch (err) {
    setStatus("backgroundStatus", err.message || String(err), false);
  }
}

async function onFindScreensaverClick() {
  const query = document.getElementById("screensaverQuery")?.value || "";

  setStatus("screensaverStatus", "Поиск заставки…", false);

  try {
    const results = await findScreensaver(query, {});

    if (!results) {
      setStatus("screensaverStatus", "Заставка не найдена", false);
      return;
    }

    const first = results[0];

    setStatus(
      "screensaverStatus",
      `Найдено заставок: ${results.length}. Применена: ${first.name || first.id}`,
      true,
    );
  } catch (err) {
    setStatus("screensaverStatus", err.message || String(err), false);
  }
}

  function bindStudentControls() {
    document.getElementById("loadModelBtn")?.addEventListener("click", (event) => {
      event.preventDefault();
      onLoadModelClick();
    });
    document.getElementById("findBackgroundBtn")?.addEventListener("click", (event) => {
      event.preventDefault();
      onFindBackgroundClick();
    });
    document.getElementById("findScreensaverBtn")?.addEventListener("click", (event) => {
      event.preventDefault();
      onFindScreensaverClick();
    });
    document.getElementById("clearScreensaverBtn")?.addEventListener("click", (event) => {
      event.preventDefault();
      if (typeof global.applyScreensaver === "function") global.applyScreensaver("");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindStudentControls);
  } else {
    bindStudentControls();
  }

  global.loadModel = loadModel;
  global.findBackground = findBackground;
  global.findScreensaver = findScreensaver;
})(window);
