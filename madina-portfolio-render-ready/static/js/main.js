(function () {
  "use strict";

  const LANG_KEY = "madina-portfolio-language";
  const DEFAULT_LANG = "x-hinglish";
  const SUPPORTED = new Set([DEFAULT_LANG, "en", "hi"]);
  const catalogs = {};
  let originalsCaptured = false;

  async function loadCatalog(lang) {
    if (catalogs[lang]) return catalogs[lang];
    if (lang === DEFAULT_LANG) return {};
    const response = await fetch(`/static/translations/${lang}.json`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Could not load ${lang} translations`);
    catalogs[lang] = await response.json();
    return catalogs[lang];
  }

  function captureOriginals(root = document) {
    root.querySelectorAll?.("[data-i18n], [data-i18n-placeholder], [data-i18n-title], [data-i18n-aria-label], [data-i18n-alt]").forEach((el) => {
      if (el.dataset.i18n && el.dataset.i18nOriginal === undefined) el.dataset.i18nOriginal = el.textContent;
      if (el.dataset.i18nPlaceholder && el.dataset.i18nOriginalPlaceholder === undefined) el.dataset.i18nOriginalPlaceholder = el.getAttribute("placeholder") || "";
      if (el.dataset.i18nTitle && el.dataset.i18nOriginalTitle === undefined) el.dataset.i18nOriginalTitle = el.getAttribute("title") || "";
      if (el.dataset.i18nAriaLabel && el.dataset.i18nOriginalAriaLabel === undefined) el.dataset.i18nOriginalAriaLabel = el.getAttribute("aria-label") || "";
      if (el.dataset.i18nAlt && el.dataset.i18nOriginalAlt === undefined) el.dataset.i18nOriginalAlt = el.getAttribute("alt") || "";
    });
    originalsCaptured = true;
  }

  function translateElement(el, catalog, lang) {
    const key = el.dataset.i18n;
    if (key) el.textContent = lang === DEFAULT_LANG ? (el.dataset.i18nOriginal ?? "") : (catalog[key] ?? el.dataset.i18nOriginal ?? "");
    const placeholderKey = el.dataset.i18nPlaceholder;
    if (placeholderKey) el.setAttribute("placeholder", lang === DEFAULT_LANG ? (el.dataset.i18nOriginalPlaceholder ?? "") : (catalog[placeholderKey] ?? el.dataset.i18nOriginalPlaceholder ?? ""));
    const titleKey = el.dataset.i18nTitle;
    if (titleKey) el.setAttribute("title", lang === DEFAULT_LANG ? (el.dataset.i18nOriginalTitle ?? "") : (catalog[titleKey] ?? el.dataset.i18nOriginalTitle ?? ""));
    const ariaKey = el.dataset.i18nAriaLabel;
    if (ariaKey) el.setAttribute("aria-label", lang === DEFAULT_LANG ? (el.dataset.i18nOriginalAriaLabel ?? "") : (catalog[ariaKey] ?? el.dataset.i18nOriginalAriaLabel ?? ""));
    const altKey = el.dataset.i18nAlt;
    if (altKey) el.setAttribute("alt", lang === DEFAULT_LANG ? (el.dataset.i18nOriginalAlt ?? "") : (catalog[altKey] ?? el.dataset.i18nOriginalAlt ?? ""));
  }

  async function applyLanguage(lang, persist = true) {
    if (!SUPPORTED.has(lang)) lang = DEFAULT_LANG;
    captureOriginals();
    const catalog = await loadCatalog(lang);
    document.querySelectorAll("[data-i18n], [data-i18n-placeholder], [data-i18n-title], [data-i18n-aria-label], [data-i18n-alt]").forEach((el) => translateElement(el, catalog, lang));
    if (lang === DEFAULT_LANG) document.title = document.documentElement.dataset.originalTitle || document.title;
    else if (catalog["site.title"]) document.title = catalog["site.title"];
    document.documentElement.lang = lang === DEFAULT_LANG ? "en-IN" : lang;
    document.documentElement.dir = "ltr";
    document.body.dataset.language = lang;
    const selector = document.getElementById("site-language");
    if (selector) selector.value = lang;
    if (persist) localStorage.setItem(LANG_KEY, lang);
    window.dispatchEvent(new CustomEvent("portfolio:languagechange", { detail: { language: lang, catalog } }));
  }

  function initLanguageSwitcher() {
    captureOriginals();
    if (!document.documentElement.dataset.originalTitle) document.documentElement.dataset.originalTitle = document.title;
    const selector = document.getElementById("site-language");
    if (!selector) return;
    selector.addEventListener("change", () => applyLanguage(selector.value));
    const saved = localStorage.getItem(LANG_KEY);
    applyLanguage(SUPPORTED.has(saved) ? saved : DEFAULT_LANG, false).catch(console.error);
  }

  function initUI() {
    const observer = "IntersectionObserver" in window ? new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("is-visible"); observer.unobserve(e.target); }
    }), { threshold: 0.08 }) : null;
    document.querySelectorAll(".reveal").forEach((el) => observer ? observer.observe(el) : el.classList.add("is-visible"));

    const ps = document.getElementById("productSearch"), cf = document.getElementById("categoryFilter");
    const items = [...document.querySelectorAll(".product-item")], empty = document.getElementById("noProducts");
    function filterProducts() {
      if (!items.length) return;
      const q = (ps?.value || "").toLowerCase().trim(), c = cf?.value || "";
      let shown = 0;
      items.forEach((el) => { const ok = (!q || el.dataset.name.includes(q)) && (!c || el.dataset.category === c); el.classList.toggle("d-none", !ok); if (ok) shown++; });
      empty?.classList.toggle("d-none", shown !== 0);
    }
    ps?.addEventListener("input", filterProducts); cf?.addEventListener("change", filterProducts);

    const bs = document.getElementById("blogSearch"), bc = document.getElementById("blogCategory"), bi = [...document.querySelectorAll(".blog-item")];
    function filterBlogs() {
      const q = (bs?.value || "").toLowerCase().trim(), c = bc?.value || "";
      bi.forEach((el) => el.classList.toggle("d-none", !!(q && !el.dataset.title.includes(q)) || (!!c && el.dataset.category !== c)));
    }
    bs?.addEventListener("input", filterBlogs); bc?.addEventListener("change", filterBlogs);
  }

  document.addEventListener("DOMContentLoaded", () => { initUI(); initLanguageSwitcher(); });
  window.MadinaI18n = { applyLanguage, loadCatalog, captureOriginals, DEFAULT_LANG, LANG_KEY };
})();
