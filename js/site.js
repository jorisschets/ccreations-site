import { translations } from "./translations.js";

/* Address that receives contact requests. */
const CONTACT_EMAIL = "jorisschets@ccreations.tools";
const STORAGE_KEY = "ccreations.lang";
const DEFAULT_LANG = "nl";
const FALLBACK_LANG = "en"; /* for visitors whose browser language the site does not offer */
const TRANSLATED_ATTRIBUTES = ["placeholder", "alt", "aria-label", "content"];

/* ---------- Language switch ---------- */

/* One binding per translatable spot: its key, and how to read and write the string there. */
function bind(selector, keyOf, read, write) {
  return [...document.querySelectorAll(selector)].map((node) => ({
    key: keyOf(node),
    read: () => read(node),
    write: (value) => write(node, value),
  }));
}

const bindings = [
  ...bind("[data-i18n]", (node) => node.dataset.i18n, (node) => node.textContent, (node, value) => { node.textContent = value; }),
  ...bind("[data-i18n-html]", (node) => node.dataset.i18nHtml, (node) => node.innerHTML, (node, value) => { node.innerHTML = value; }),
  ...TRANSLATED_ATTRIBUTES.flatMap((attribute) => bind(
    `[data-i18n-${attribute}]`,
    (node) => node.getAttribute(`data-i18n-${attribute}`),
    (node) => node.getAttribute(attribute),
    (node, value) => node.setAttribute(attribute, value),
  )),
];

/* Read the Dutch source strings from the markup once, so there is a single source of truth. */
const dutch = { "mail.subject": "Proces om te bekijken" };
bindings.forEach(({ key, read }) => { dutch[key] ??= read(); });

const dictionaries = { ...translations, [DEFAULT_LANG]: dutch };
const langButtons = document.querySelectorAll("[data-lang]");
let currentLang = DEFAULT_LANG;

const t = (key) => dictionaries[currentLang][key] ?? dutch[key];

function setLanguage(lang) {
  currentLang = lang in dictionaries ? lang : DEFAULT_LANG;
  document.documentElement.lang = currentLang;
  bindings.forEach(({ key, write }) => write(t(key)));
  langButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.lang === currentLang));
  });
}

function readStoredLanguage() {
  try { return localStorage.getItem(STORAGE_KEY); } catch { return null; }
}

function storeLanguage(lang) {
  try { localStorage.setItem(STORAGE_KEY, lang); } catch { /* storage unavailable: the choice lasts for this visit */ }
}

langButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setLanguage(button.dataset.lang);
    storeLanguage(currentLang);
  });
});

/* An earlier choice wins; otherwise follow the browser's language list, in the visitor's order of preference. */
function preferredLanguage() {
  const stored = readStoredLanguage();
  if (stored && stored in dictionaries) return stored;

  const browserLanguages = navigator.languages?.length ? navigator.languages : [navigator.language ?? ""];
  const match = browserLanguages
    .map((tag) => tag.toLowerCase().split("-")[0])
    .find((lang) => lang in dictionaries);
  return match ?? FALLBACK_LANG;
}

const initialLang = preferredLanguage();
if (initialLang !== DEFAULT_LANG) setLanguage(initialLang);

/* ---------- Mobile menu ---------- */
const nav = document.getElementById("site-nav");
const menuToggle = document.getElementById("menu-toggle");

function setMenuOpen(open) {
  nav.toggleAttribute("data-open", open);
  menuToggle.setAttribute("aria-expanded", String(open));
}

menuToggle.addEventListener("click", () => setMenuOpen(!nav.hasAttribute("data-open")));
nav.addEventListener("click", (event) => {
  if (event.target.closest("a")) setMenuOpen(false);
});

/* ---------- Contact form: prepares an email draft, sends nothing itself ---------- */
const form = document.getElementById("contact-form");

form?.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(form);
  const body = `${data.get("process")}\n\n${data.get("name")}\n${data.get("email")}`;
  const mailto = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(t("mail.subject"))}&body=${encodeURIComponent(body)}`;

  document.getElementById("contact-mailto").href = mailto;
  document.getElementById("contact-status").hidden = false;
  navigator.clipboard?.writeText(body).catch(() => { /* copying is a convenience only */ });
  window.location.href = mailto;
});

/* ---------- Decorative wave mesh behind the dark section ---------- */
const canvas = document.getElementById("waves");
const WAVE_LINES = 72;
const WAVE_COLORS = ["227 94 32", "239 160 55"]; /* brand orange, amber */

function drawWaves() {
  const { width, height } = canvas.getBoundingClientRect();
  if (!width || !height) return;

  const ratio = window.devicePixelRatio || 1;
  canvas.width = width * ratio;
  canvas.height = height * ratio;

  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  ctx.lineWidth = 1;

  /* Lines fade in from the left so they never compete with the statement. */
  const strokes = WAVE_COLORS.map((rgb) => {
    const gradient = ctx.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, `rgb(${rgb} / 0)`);
    gradient.addColorStop(0.4, `rgb(${rgb} / 0.1)`);
    gradient.addColorStop(1, `rgb(${rgb} / 0.3)`);
    return gradient;
  });

  for (let line = 0; line < WAVE_LINES; line += 1) {
    const offset = line - WAVE_LINES / 2;
    ctx.strokeStyle = strokes[line % 6 === 0 ? 1 : 0];
    ctx.beginPath();
    for (let x = 0; x <= width; x += 6) {
      const progress = x / width;
      const spread = offset * 7 * Math.sin(progress * Math.PI * 1.3 + 0.4);
      const swell = Math.sin(progress * 5 + line * 0.05) * height * 0.2 * progress;
      ctx.lineTo(x, height * 0.72 + spread + swell);
    }
    ctx.stroke();
  }
}

if (canvas) {
  drawWaves();
  window.addEventListener("resize", drawWaves);
}
