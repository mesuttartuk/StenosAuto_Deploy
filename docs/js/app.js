"use strict";
/* =============================================================================
   STENOS AUTO × ODYSSEUS ARAŞTIRMA — statik HTML/JS sürümü
   Orijinal Streamlit (app.py) dashboard'unun birebir tarayıcı taşınmış hali.
   3 CSV taraycıda okunur, tüm istatistikler ve Plotly grafikleri istemci
   tarafında hesaplanır. Sunucu tarafı gerekmez.
============================================================================= */

/* ============================== MARKA / TEMA ============================== */
const BRAND = {
  blue:"#2800C8", navy:"#0F0F72", lagon:"#04B4FD", aqua:"#09BFAF",
  veget:"#0DCA61", solar:"#FD6221", coral:"#FF4533", coralD:"#C0241A",
  black:"#111111", gray:"#C7C7C7",
};

const THEMES = {
  "Açık": {
    zemin:"rgba(0,0,0,0)", sayfa:"#F4F4F6", kart:"#FFFFFF", kenar:"#E2E2E8",
    metin:BRAND.black, soluk:"#6B6B7B", vurgu:BRAND.blue, grid:"#EDEDF2", girdi:"#FFFFFF",
    kpi:[BRAND.blue, BRAND.navy, BRAND.black, BRAND.blue, BRAND.black],
    palet:[BRAND.blue, BRAND.lagon, BRAND.aqua, BRAND.veget, BRAND.solar, BRAND.navy, BRAND.gray],
    olcek:{
      ana:["#E6E1FA", BRAND.blue], ikincil:["#DFF7F5", BRAND.aqua], vurgu:["#DCF1FF", BRAND.lagon],
      negatif:["#FFE3DC", BRAND.coralD], pozitif:["#DDF8E9", BRAND.veget],
    },
  },
  "Koyu": {
    zemin:"rgba(0,0,0,0)", sayfa:BRAND.black, kart:"#1B1B1B", kenar:"#333333",
    metin:"#FFFFFF", soluk:"#9A9A9A", vurgu:BRAND.lagon, grid:"#2A2A2A", girdi:"#1F1F1F",
    kpi:[BRAND.lagon, BRAND.aqua, "#FFFFFF", BRAND.lagon, "#FFFFFF"],
    palet:[BRAND.lagon, BRAND.aqua, BRAND.veget, BRAND.solar, BRAND.gray, "#FFFFFF", BRAND.navy],
    olcek:{
      ana:["#14141E", BRAND.lagon], ikincil:["#0A2A28", BRAND.aqua], vurgu:["#14141E", BRAND.lagon],
      negatif:["#3A1410", BRAND.coralD], pozitif:["#0B2A1A", BRAND.veget],
    },
  },
};
const NPS_RENK = {Promoter:BRAND.veget, Passive:BRAND.solar, Detractor:BRAND.coralD};

let TEMA = "Açık";
function T() { return THEMES[TEMA]; }

const DOSYALAR = {
  kredi:"Stenos_CSI_KrediKullanan.csv",
  nakit:"Stenos_CSI_KrediKullanmayan.csv",
  dsi:"Stenos_DSI_BayiCalisanlari.csv",
};
const SEGMENT_ADLARI = {
  kredi:"Kredi Kullanan Müşteri", nakit:"Kredi Kullanmayan Müşteri", dsi:"Bayi Çalışanı / DSI",
};
const KOD_99_KOLONLARI = {
  kredi:["EO1x1_Acente_Satis_Danismani", "EO2x1_Stenos_Satis_Yoneticisi",
         "C1_Satis_Elemani_Yaklasimi", "C1a_Finansman_Kosullari_Bilgilendirme",
         "C2_Finansman_Secenekleri", "C8_Geri_Odeme_Kosullari",
         "C5_Surec_Kolaylik_Hiz", "E5a_Cagri_Merkezi_Memnuniyeti"],
  nakit:[],
  dsi:["S1_1_Ziyaret_Genel_Memnuniyet", "S1_2_Ziyaret_Sikligi_Memnuniyet"],
};
const MARKA_METRIKLERI_CSI = [
  ["EO0_Genel_Memnuniyet", "Genel Memnuniyet", "EO0 · Overall Satisfaction"],
  ["F1_Recommendation_NPS", "Tavsiye Etme", "F1 · Recommendation"],
  ["F1x_Brand_Importance", "Marka Önemi", "F1x · Brand Importance"],
  ["S44_Brand_Retention", "Tekrar Tercih", "S44 · Brand Retention"],
];

/* ============================== TEMEL YARDIMCILAR ============================== */
function saydam(hex, alfa) {
  if (alfa === undefined) alfa = 0.2;
  const h = hex.replace("#", "");
  const r = parseInt(h.substring(0, 2), 16), g = parseInt(h.substring(2, 4), 16), b = parseInt(h.substring(4, 6), 16);
  return `rgba(${r},${g},${b},${alfa})`;
}
function num(v) {
  if (v === undefined || v === null || v === "") return NaN;
  const n = parseFloat(v);
  return Number.isFinite(n) ? n : NaN;
}
function fmtInt(n) { return Number.isFinite(n) ? Math.round(n).toLocaleString("tr-TR") : "—"; }
function fmtNum2(v) { return Number.isFinite(v) ? v.toFixed(2) : "—"; }
function fmtPct1(v, d) { d = d === undefined ? 1 : d; return Number.isFinite(v) ? "%" + v.toFixed(d) : "—"; }
function fmtSigned(n, d) { d = d === undefined ? 0 : d; return Number.isFinite(n) ? (n >= 0 ? "+" : "") + n.toFixed(d) : "—"; }
function escapeHtml(s) {
  return String(s === undefined || s === null ? "" : s).replace(/[&<>"']/g, c => (
    {"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]
  ));
}
function linspace(a, b, n) {
  if (n <= 1) return [a];
  const step = (b - a) / (n - 1);
  return Array.from({length:n}, (_, i) => a + step * i);
}
function pearson(xs, ys) {
  const n = xs.length; if (n < 2) return NaN;
  const mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n;
  let sxy = 0, sx2 = 0, sy2 = 0;
  for (let i = 0; i < n; i++) { const dx = xs[i] - mx, dy = ys[i] - my; sxy += dx * dy; sx2 += dx * dx; sy2 += dy * dy; }
  const denom = Math.sqrt(sx2 * sy2);
  return denom ? sxy / denom : NaN;
}
function linreg(xs, ys) {
  const n = xs.length;
  const mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n;
  let sxy = 0, sx2 = 0;
  for (let i = 0; i < n; i++) { const dx = xs[i] - mx; sxy += dx * (ys[i] - my); sx2 += dx * dx; }
  const slope = sx2 ? sxy / sx2 : 0;
  return {slope, intercept: my - slope * mx};
}
function sizerefFor(sizes, sizeMax) {
  const finite = sizes.filter(Number.isFinite);
  const maxV = finite.length ? Math.max(...finite) : 1;
  return maxV > 0 ? (2 * maxV) / (sizeMax * sizeMax) : 1;
}
function rowMeanCols(row, cols) {
  const vals = cols.map(c => num(row[c])).filter(Number.isFinite);
  return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : NaN;
}
function guvenliOrt(arr) {
  const v = arr.filter(Number.isFinite);
  return v.length ? v.reduce((a, b) => a + b, 0) / v.length : NaN;
}
function npsHesapla(arr) {
  const v = arr.filter(Number.isFinite);
  if (!v.length) return {nps:NaN, p:0, pa:0, d:0};
  const p = v.filter(x => x >= 9).length / v.length * 100;
  const pa = v.filter(x => x >= 7 && x <= 8).length / v.length * 100;
  const d = v.filter(x => x <= 6).length / v.length * 100;
  return {nps:p - d, p, pa, d};
}
function _nps(arr) { return npsHesapla(arr).nps; }
function pct(arr, pred) { if (!arr.length) return NaN; return arr.filter(pred).length / arr.length * 100; }
function pctGE(arr, th) { return pct(arr, v => Number.isFinite(v) && v >= th); }
function pctLE(arr, th) { return pct(arr, v => Number.isFinite(v) && v <= th); }
function pctBetween(arr, lo, hi) { return pct(arr, v => Number.isFinite(v) && v >= lo && v <= hi); }
function pctEq(arr, val) { return pct(arr, v => v === val); }
function pctNotEq(arr, val) { return pct(arr, v => v !== val); }
function valueCounts(arr) {
  const m = new Map();
  arr.forEach(v => { if (v === undefined || v === null || v === "") return; m.set(v, (m.get(v) || 0) + 1); });
  return new Map(Array.from(m.entries()).sort((a, b) => b[1] - a[1]));
}
function cokluAc(arr, sep) {
  sep = sep || "; ";
  const out = [];
  arr.forEach(v => { if (!v) return; String(v).split(sep).forEach(s => { const t = s.trim(); if (t) out.push(t); }); });
  return out;
}
function pdCut(value, edges, labels) {
  if (!Number.isFinite(value)) return null;
  for (let i = 0; i < edges.length - 1; i++) if (value > edges[i] && value <= edges[i + 1]) return labels[i];
  return null;
}
const TR_MAP = {"ç":"c","ğ":"g","ı":"i","ö":"o","ş":"s","ü":"u","Ç":"C","Ğ":"G","İ":"I","Ö":"O","Ş":"S","Ü":"U"};
function slug(text, maxlen) {
  maxlen = maxlen || 28;
  let t = text.split("").map(ch => TR_MAP[ch] || ch).join("");
  t = t.replace(/[^a-zA-Z0-9]/g, "_");
  while (t.includes("__")) t = t.replace(/__/g, "_");
  t = t.replace(/^_+|_+$/g, "");
  return t.slice(0, maxlen);
}
function parseCSVText(text) {
  if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);
  const rows = [];
  let row = [], field = "", inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else inQuotes = false; }
      else field += c;
    } else {
      if (c === '"') inQuotes = true;
      else if (c === ",") { row.push(field); field = ""; }
      else if (c === "\r") { /* skip */ }
      else if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
      else field += c;
    }
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  const filtered = rows.filter(r => !(r.length === 1 && r[0] === ""));
  if (!filtered.length) return [];
  const header = filtered.shift();
  return filtered.map(r => {
    const obj = {};
    header.forEach((h, idx) => { obj[h] = r[idx] !== undefined ? r[idx] : ""; });
    return obj;
  });
}
function parseDateISO(s) {
  if (!s) return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(s).trim());
  if (!m) return null;
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  return isNaN(d.getTime()) ? null : d;
}
function toInputDate(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
function parseInputDate(s) {
  if (!s) return null;
  const p = s.split("-").map(Number);
  return new Date(p[0], p[1] - 1, p[2]);
}
function fmtDateTR(d) { return `${String(d.getDate()).padStart(2, "0")}.${String(d.getMonth() + 1).padStart(2, "0")}.${d.getFullYear()}`; }
function fmtDateCompact(d) { return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}`; }

let _idCounter = 0;
function uid() { return "c" + (_idCounter++); }
function newIdSet(names) { const o = {}; names.forEach(n => o[n] = uid()); return o; }

/* ============================== VERİ ============================== */
let VERI = {kredi:[], nakit:[], dsi:[]};
let HATALAR = [];
let SEHIR_BOLGE = {}, TUM_SEHIR = [], TUM_BOLGE = [];
let _yoneticiCache = null;

async function veriYukle() {
  const hatalar = [];
  for (const key of Object.keys(DOSYALAR)) {
    const dosya = DOSYALAR[key];
    try {
      const resp = await fetch("data/" + dosya);
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      const text = await resp.text();
      let rows = parseCSVText(text);
      if (!rows.length) throw new Error(`'${dosya}' boş.`);
      rows.forEach(r => {
        const d = parseDateISO(r.Anket_Tarihi);
        r._tarih = d;
        if (d) r.Yil_Ay = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
      });
      rows = rows.filter(r => r._tarih);
      (KOD_99_KOLONLARI[key] || []).forEach(col => {
        rows.forEach(r => { if (col in r) { const v = num(r[col]); if (v === 99) r[col] = ""; } });
      });
      rows.forEach(r => { if (!r.Segment) r.Segment = SEGMENT_ADLARI[key]; });
      VERI[key] = rows;
    } catch (e) {
      hatalar.push(`${dosya} → ${e.message}`);
      VERI[key] = [];
    }
  }
  HATALAR = hatalar;
}

function buildSehirBolge() {
  SEHIR_BOLGE = {};
  Object.values(VERI).forEach(rows => rows.forEach(r => {
    if (r.Sehir && r.Bolge && !(r.Sehir in SEHIR_BOLGE)) SEHIR_BOLGE[r.Sehir] = r.Bolge;
  }));
  TUM_SEHIR = Object.keys(SEHIR_BOLGE).sort((a, b) => a.localeCompare(b, "tr"));
  TUM_BOLGE = Array.from(new Set(Object.values(SEHIR_BOLGE))).sort((a, b) => a.localeCompare(b, "tr"));
}

/* ============================== FİLTRE ============================== */
const FILTRE = {bas:null, son:null, minT:null, maxT:null, bolge:[], sehir:[], bayi:[], segment:[]};

function filtrele(rows) {
  if (!rows.length) return rows;
  return rows.filter(r => {
    if (FILTRE.bas && FILTRE.son) { const t = r._tarih; if (!t || t < FILTRE.bas || t > FILTRE.son) return false; }
    if (FILTRE.sehir.length && !FILTRE.sehir.includes(r.Sehir)) return false;
    if (FILTRE.bolge.length && !FILTRE.bolge.includes(r.Bolge)) return false;
    if (FILTRE.bayi.length && !FILTRE.bayi.includes(r.Acente_Adi)) return false;
    if (FILTRE.segment.length && !FILTRE.segment.includes(r.Segment)) return false;
    return true;
  });
}
function activeFiltreText() {
  const parts = [`Tarih: ${fmtDateTR(FILTRE.bas)} – ${fmtDateTR(FILTRE.son)}`];
  if (FILTRE.sehir.length) parts.push("Şehir: " + FILTRE.sehir.join(", "));
  if (FILTRE.bolge.length) parts.push("Bölge: " + FILTRE.bolge.join(", "));
  if (FILTRE.bayi.length) parts.push("Bayi: " + FILTRE.bayi.join(", "));
  if (FILTRE.segment.length && FILTRE.segment.length < Object.keys(SEGMENT_ADLARI).length) parts.push("Segment: " + FILTRE.segment.join(", "));
  return "Aktif filtreler → " + parts.join("  ·  ");
}
function dosyaAdiEki() {
  const parts = [`${fmtDateCompact(FILTRE.bas)}-${fmtDateCompact(FILTRE.son)}`];
  if (FILTRE.bolge.length) parts.push("bolge-" + slug(FILTRE.bolge.map(b => b.replace(" Bölgesi", "")).join("-")));
  if (FILTRE.sehir.length) parts.push("sehir-" + slug(FILTRE.sehir.join("-")));
  if (FILTRE.bayi.length) parts.push(FILTRE.bayi.length > 1 ? `bayi-${FILTRE.bayi.length}adet` : "bayi-" + slug(FILTRE.bayi[0]));
  return parts.join("_");
}

/* ============================== ÇOKLU SEÇİM (multiselect) ============================== */
function createMultiSelect(wrapEl, opts) {
  const label = opts.label, placeholder = opts.placeholder || "Tümü", onChange = opts.onChange;
  wrapEl.innerHTML = `
    <label>${escapeHtml(label)}</label>
    <div class="multiselect">
      <div class="ms-button" tabindex="0">
        <div class="ms-chips"><span class="ms-placeholder">${escapeHtml(placeholder)}</span></div>
        <span class="ms-caret">▾</span>
      </div>
      <div class="ms-panel">
        <input class="ms-search" type="text" placeholder="Ara...">
        <div class="ms-options"></div>
        <div class="ms-clear">Temizle</div>
      </div>
    </div>`;
  const root = wrapEl.querySelector(".multiselect");
  const btn = root.querySelector(".ms-button");
  const chipsEl = root.querySelector(".ms-chips");
  const optionsEl = root.querySelector(".ms-options");
  const searchEl = root.querySelector(".ms-search");
  const clearEl = root.querySelector(".ms-clear");
  let options = [], value = [];

  function renderChips() {
    chipsEl.innerHTML = value.length
      ? value.map(v => `<span class="ms-chip">${escapeHtml(v)}</span>`).join("")
      : `<span class="ms-placeholder">${escapeHtml(placeholder)}</span>`;
  }
  function renderOptions(filterText) {
    const ft = (filterText || "").trim().toLocaleLowerCase("tr-TR");
    const filtered = options.filter(o => !ft || o.toLocaleLowerCase("tr-TR").includes(ft));
    optionsEl.innerHTML = filtered.length
      ? filtered.map(o => `<label class="ms-option"><input type="checkbox" value="${escapeHtml(o)}" ${value.includes(o) ? "checked" : ""}> ${escapeHtml(o)}</label>`).join("")
      : '<div class="ms-empty">Sonuç yok</div>';
  }
  optionsEl.addEventListener("change", e => {
    if (e.target.type !== "checkbox") return;
    const v = e.target.value;
    if (e.target.checked) { if (!value.includes(v)) value.push(v); } else { value = value.filter(x => x !== v); }
    renderChips();
    onChange(value.slice());
  });
  clearEl.addEventListener("click", () => {
    value = [];
    renderChips(); renderOptions(searchEl.value);
    onChange(value.slice());
  });
  btn.addEventListener("click", () => {
    const willOpen = !root.classList.contains("open");
    document.querySelectorAll(".multiselect.open").forEach(el => el.classList.remove("open"));
    if (willOpen) { root.classList.add("open"); renderOptions(searchEl.value); searchEl.value = ""; searchEl.focus(); }
  });
  searchEl.addEventListener("input", () => renderOptions(searchEl.value));
  document.addEventListener("click", e => { if (!root.contains(e.target)) root.classList.remove("open"); });

  return {
    setOptions(list) {
      options = list.slice();
      value = value.filter(v => options.includes(v));
      renderChips();
      if (root.classList.contains("open")) renderOptions(searchEl.value);
    },
    getValue() { return value.slice(); },
  };
}

/* ============================== HTML BİLEŞENLERİ ============================== */
function kpiHtml(baslik, deger, alt, renk, oran) {
  let bar = "";
  if (oran !== null && oran !== undefined && Number.isFinite(oran)) {
    const g = Math.min(Math.max(oran, 0), 1) * 100;
    bar = `<div class="kpi-bar"><div style="width:${g.toFixed(1)}%;background:${renk}"></div></div>`;
  }
  return `<div class="kpi"><div class="kpi-t">${escapeHtml(baslik)}</div>
    <div class="kpi-v" style="color:${renk}">${deger}</div>
    <div class="kpi-s">${alt}</div>${bar}</div>`;
}
function baslikHtml(metin, altyazi) {
  return `<div class="bolum">${metin}</div>` + (altyazi ? `<div class="bolum-alt">${altyazi}</div>` : "");
}
function bosUyariHtml(msg) {
  msg = msg || "Seçilen filtrelerle bu segmentte yanıt bulunmuyor.";
  return `<div class="st-info">ℹ️ ${msg} Yukarıdaki filtreleri genişletmeyi deneyin.</div>`;
}
function bulguHtml(deger, baslikMetni, altyazi, renk) {
  return `<div class="bulgu"><div class="bulgu-v" style="color:${renk}">${deger}</div>
    <div class="bulgu-t">${baslikMetni}</div><div class="bulgu-s">${altyazi}</div></div>`;
}
function aksiyonHtml(no, renk, baslikMetni, chipMetin, chipRenk, bulgu, aksiyon) {
  return `<div class="aksiyon">
    <div class="aksiyon-no" style="background:${renk}">${no}</div>
    <div class="aksiyon-govde">
      <div class="aksiyon-baslik">${baslikMetni}<span class="chip" style="background:${saydam(chipRenk, .16)};color:${chipRenk}">${chipMetin}</span></div>
      <div class="aksiyon-bulgu">📊 ${bulgu}</div>
      <div class="aksiyon-aksiyon">▸ <b>Aksiyon:</b> ${aksiyon}</div>
    </div>
  </div>`;
}

/* ============================== GRAFİK TEMEL DÜZENİ ============================== */
const PLOTLY_CONFIG = {displayModeBar:false, responsive:true};
function fontFamily() { return '"Poppins","Helvetica Neue",Helvetica,Arial,sans-serif'; }
function baseLayout(opts) {
  opts = opts || {};
  const t = T();
  const height = opts.height === undefined ? 380 : opts.height;
  const legendAlt = opts.legendAlt === undefined ? true : opts.legendAlt;
  const legendSatir = opts.legendSatir === undefined ? 1 : opts.legendSatir;
  const ustBosluk = legendAlt ? (58 + 24 * legendSatir) : 58;
  const layout = {
    height,
    margin:{l:50, r:20, t:ustBosluk, b:50},
    paper_bgcolor:t.zemin, plot_bgcolor:t.zemin,
    font:{family:fontFamily(), size:12, color:t.metin},
    hoverlabel:{font:{size:12}},
    xaxis:{gridcolor:t.grid, zeroline:false, title:{}, automargin:true},
    yaxis:{gridcolor:t.grid, zeroline:false, title:{}, automargin:true},
  };
  if (opts.title) layout.title = {text:opts.title, font:{size:14.5, color:t.metin}, x:0, xanchor:"left", y:0.97, yanchor:"top"};
  if (legendAlt) {
    layout.legend = {orientation:"h", yanchor:"bottom", y:1.015, xanchor:"left", x:0, title:{text:""}, font:{size:11}};
    layout.showlegend = true;
  } else {
    layout.showlegend = opts.showlegend === undefined ? false : opts.showlegend;
  }
  return layout;
}
function colorscaleOf(pair) { return [[0, pair[0]], [1, pair[1]]]; }

// Plotly, config.responsive:true iken konteynere kendi satır-içi height'ini
// YAZMAZ (CSS'e bırakır); .chart-box'ın min-height:220px'i tek referans kalınca
// SVG kutunun dışına taşıp bir alttaki bölüme biniyordu. Konteyner yüksekliğini
// grafiğin gerçek layout.height'ine sabitleyerek taşmayı önlüyoruz.
function plot(divId, data, layout, config) {
  Plotly.newPlot(divId, data, layout, config || PLOTLY_CONFIG);
  const el = document.getElementById(divId);
  if (el && layout && layout.height) el.style.height = layout.height + "px";
}

/* ============================== GRAFİKLER ============================== */
function donutRing(divId, deger, renk) {
  const t = T();
  deger = Number.isFinite(deger) ? deger : 0;
  const trace = {
    type:"pie", values:[deger, Math.max(10 - deger, 0)], hole:0.74, sort:false,
    direction:"clockwise", rotation:0,
    marker:{colors:[renk, saydam(t.soluk, .22)], line:{color:t.kart, width:0}},
    textinfo:"none", hoverinfo:"skip", showlegend:false,
  };
  const layout = baseLayout({height:210, legendAlt:false});
  layout.margin = {l:6, r:6, t:6, b:6};
  layout.annotations = [
    {text:`<b>${deger.toFixed(2)}</b>`, showarrow:false, font:{size:30, color:t.metin}, x:0.5, y:0.54, xref:"paper", yref:"paper"},
    {text:"10 üzerinden", showarrow:false, font:{size:10.5, color:t.soluk}, x:0.5, y:0.28, xref:"paper", yref:"paper"},
  ];
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function markaMetrikBloku(container, rows, metrikler, baslikMetni, altyazi) {
  container.insertAdjacentHTML("beforeend", baslikHtml(baslikMetni, altyazi));
  const mevcut = metrikler.filter(m => rows.length && (m[0] in rows[0]));
  if (!mevcut.length) { container.insertAdjacentHTML("beforeend", bosUyariHtml("Bu segmentte marka metrikleri bulunmuyor.")); return; }
  const t = T(), palet = t.palet;
  const renkler = [t.vurgu, NPS_RENK.Promoter, palet[1], t.vurgu];
  const gridId = uid();
  container.insertAdjacentHTML("beforeend", `<div class="row" style="grid-template-columns:repeat(${mevcut.length},1fr)" id="${gridId}"></div>`);
  const grid = document.getElementById(gridId);
  const dagilim = [];
  mevcut.forEach((m, i) => {
    const kolon = m[0], ad = m[1], alt = m[2];
    const vals = rows.map(r => num(r[kolon])).filter(v => Number.isFinite(v) && v !== 99);
    const mean = guvenliOrt(vals);
    const cid = uid();
    grid.insertAdjacentHTML("beforeend", `
      <div>
        <div class="metrik-baslik"><div class="ad">${ad}</div><div class="alt">${alt} · n=${vals.length}</div></div>
        <div id="${cid}" class="chart-box"></div>
      </div>`);
    donutRing(cid, mean, renkler[i % renkler.length]);
    if (vals.length) {
      dagilim.push({Metrik:ad, "Yüksek (9-10)":pctGE(vals, 9), "Orta (7-8)":pctBetween(vals, 7, 8), "Düşük (≤6)":pctLE(vals, 6)});
    }
  });
  if (!dagilim.length) return;
  const bandId = uid();
  container.insertAdjacentHTML("beforeend", `<div id="${bandId}" class="chart-box"></div>`);
  const bantlar = ["Yüksek (9-10)", "Orta (7-8)", "Düşük (≤6)"];
  const renkBant = {"Yüksek (9-10)":NPS_RENK.Promoter, "Orta (7-8)":NPS_RENK.Passive, "Düşük (≤6)":NPS_RENK.Detractor};
  const metrikAdlari = dagilim.map(d => d.Metrik);
  const traces = bantlar.map(b => ({
    type:"bar", orientation:"h", name:b, y:metrikAdlari, x:dagilim.map(d => d[b]),
    text:dagilim.map(d => d[b]), texttemplate:"%{text:.0f}%", textposition:"inside", insidetextanchor:"middle",
    marker:{color:renkBant[b]},
  }));
  const layout = baseLayout({height:300, title:"Metrik Bazında Puan Dağılımı (%)"});
  layout.barmode = "stack";
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:"Yanıt payı (%)"}, range:[0, 100], ticksuffix:"%"});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:""}, categoryorder:"array", categoryarray:metrikAdlari.slice().reverse()});
  plot(bandId, traces, layout, PLOTLY_CONFIG);
}

function eo0DagilimChart(divId, rows) {
  const vals = rows.map(r => num(r.EO0_Genel_Memnuniyet)).filter(Number.isFinite);
  const counts = new Map();
  vals.forEach(v => counts.set(v, (counts.get(v) || 0) + 1));
  const puanlar = Array.from(counts.keys()).sort((a, b) => a - b);
  const gruplar = ["Memnun (9-10)", "Nötr (7-8)", "Memnuniyetsiz (1-6)"];
  const renkMap = {"Memnun (9-10)":NPS_RENK.Promoter, "Nötr (7-8)":NPS_RENK.Passive, "Memnuniyetsiz (1-6)":NPS_RENK.Detractor};
  const grupAd = p => (p >= 9 ? "Memnun (9-10)" : (p >= 7 ? "Nötr (7-8)" : "Memnuniyetsiz (1-6)"));
  const traces = gruplar.map(g => {
    const xs = [], ys = [];
    puanlar.forEach(p => { if (grupAd(p) === g) { xs.push(p); ys.push(counts.get(p)); } });
    return {type:"bar", name:g, x:xs, y:ys, text:ys, textposition:"outside", cliponaxis:false, marker:{color:renkMap[g]}};
  });
  const layout = baseLayout({height:380, title:"EO0 — Genel Memnuniyet Puanı Dağılımı"});
  layout.xaxis = Object.assign(layout.xaxis, {dtick:1, title:{text:"Puan (1-10)"}});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:"Yanıt sayısı"}});
  layout.barmode = "group";
  plot(divId, traces, layout, PLOTLY_CONFIG);
}

function npsGaugeChart(divId, nps) {
  const t = T();
  const trace = {
    type:"indicator", mode:"gauge+number", value:Number.isFinite(nps) ? nps : 0,
    number:{suffix:"", font:{size:40}}, title:{text:"NPS (F1)", font:{size:14}},
    gauge:{
      axis:{range:[-100, 100], tickwidth:1}, bar:{color:t.vurgu, thickness:0.7}, borderwidth:0,
      steps:[
        {range:[-100, 0], color:saydam(NPS_RENK.Detractor, .20)},
        {range:[0, 50], color:saydam(NPS_RENK.Passive, .20)},
        {range:[50, 100], color:saydam(NPS_RENK.Promoter, .20)},
      ],
      threshold:{line:{color:t.metin, width:2}, thickness:0.8, value:Number.isFinite(nps) ? nps : 0},
    },
  };
  const layout = baseLayout({height:380, legendAlt:false});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function onaySureciScatterChart(divId, rows) {
  const t = T();
  const pts = rows.filter(r => Number.isFinite(num(r.Kredi_Onay_Suresi_Saat)) && Number.isFinite(num(r.C5_Surec_Kolaylik_Hiz)));
  if (pts.length <= 2) return false;
  const xs = pts.map(r => num(r.Kredi_Onay_Suresi_Saat)), ys = pts.map(r => num(r.C5_Surec_Kolaylik_Hiz));
  const r = pearson(xs, ys);
  const kategoriler = ["Promoter", "Passive", "Detractor"];
  const tumBoyut = pts.map(p => num(p.Kredi_Tutari_TL));
  const sref = sizerefFor(tumBoyut, 17);
  const traces = kategoriler.map(k => {
    const sub = pts.filter(p => p.NPS_Kategori === k);
    return {
      type:"scatter", mode:"markers", name:k,
      x:sub.map(p => num(p.Kredi_Onay_Suresi_Saat)), y:sub.map(p => num(p.C5_Surec_Kolaylik_Hiz)),
      marker:{color:NPS_RENK[k], opacity:0.72, size:sub.map(p => num(p.Kredi_Tutari_TL)), sizemode:"area", sizeref:sref, sizemin:4},
      text:sub.map(p => `Acente: ${escapeHtml(p.Acente_Adi)}<br>Vade: ${p.Vade_Ay} ay<br>Kredi: ${fmtInt(num(p.Kredi_Tutari_TL))} TL`),
      hovertemplate:"%{text}<br>Onay: %{x} sa<br>C5: %{y}<extra></extra>",
    };
  });
  const lr = linreg(xs, ys);
  const xmin = Math.min(...xs), xmax = Math.max(...xs);
  const trendXs = linspace(xmin, xmax, 60);
  traces.push({type:"scatter", mode:"lines", name:"Trend", x:trendXs, y:trendXs.map(x => lr.slope * x + lr.intercept), line:{color:t.vurgu, width:2.5, dash:"dash"}});
  const layout = baseLayout({height:430, title:`Onay Süresi (saat) × Süreç Memnuniyeti — r = ${r.toFixed(3)}`});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:"Kredi onay süresi (saat)"}});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:"C5 · Süreç kolaylık & hız puanı"}, dtick:1});
  plot(divId, traces, layout, PLOTLY_CONFIG);
  return true;
}

function onaySuresiEsikChart(divId, rows) {
  const t = T();
  const edges = [0, 4, 8, 12, 24, 48, 10000];
  const labels = ["0-4 sa", "4-8 sa", "8-12 sa", "12-24 sa", "24-48 sa", "48+ sa"];
  const pts = rows.filter(r => Number.isFinite(num(r.Kredi_Onay_Suresi_Saat)) && Number.isFinite(num(r.F1_Recommendation_NPS)));
  if (!pts.length) return false;
  const bands = labels.map(l => ({label:l, rows:[]}));
  pts.forEach(r => { const lbl = pdCut(num(r.Kredi_Onay_Suresi_Saat), edges, labels); if (lbl) bands.find(b => b.label === lbl).rows.push(r); });
  const ozet = bands.filter(b => b.rows.length).map(b => {
    const npsArr = b.rows.map(r => num(r.F1_Recommendation_NPS));
    return {label:b.label, n:b.rows.length, nps:_nps(npsArr), eo0:guvenliOrt(b.rows.map(r => num(r.EO0_Genel_Memnuniyet))), t2b:pctGE(b.rows.map(r => num(r.EO0_Genel_Memnuniyet)), 9)};
  });
  if (!ozet.length) return false;
  const colors = ozet.map(o => (o.nps >= 50 ? NPS_RENK.Promoter : (o.nps >= 0 ? NPS_RENK.Passive : NPS_RENK.Detractor)));
  const trace = {
    type:"bar", x:ozet.map(o => o.label), y:ozet.map(o => o.nps),
    text:ozet.map(o => Math.round(o.nps)), texttemplate:"%{text:.0f}", textposition:"outside", cliponaxis:false,
    marker:{color:colors}, customdata:ozet.map(o => [o.n, o.eo0, o.t2b]),
    hovertemplate:"<b>%{x}</b><br>NPS: %{y:.0f}<br>n: %{customdata[0]}<br>Ort. EO0: %{customdata[1]:.2f}<br>Top-2-Box: %%%{customdata[2]:.0f}<extra></extra>",
  };
  const layout = baseLayout({height:430, legendAlt:false, title:"Onay Süresi Eşiği — Banda Göre NPS"});
  layout.showlegend = false;
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:"NPS"}, range:[-105, 115], zeroline:false});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:"Kredi onay süresi bandı"}});
  layout.shapes = [{type:"line", xref:"paper", x0:0, x1:1, yref:"y", y0:0, y1:0, line:{width:1, color:t.soluk}}];
  const negIdx = ozet.findIndex(o => o.nps <= 0);
  if (negIdx >= 0) {
    layout.shapes.push({type:"line", xref:"x", x0:negIdx - 0.5, x1:negIdx - 0.5, yref:"paper", y0:0, y1:1, line:{width:2, dash:"dash", color:t.vurgu}});
    layout.annotations = [{x:negIdx - 0.5, xref:"x", y:1, yref:"paper", yanchor:"bottom", text:"kırılma eşiği", showarrow:false, font:{size:11, color:t.vurgu}}];
  }
  plot(divId, [trace], layout, PLOTLY_CONFIG);
  return true;
}

function surecMetrikleriChart(divId, rows) {
  const etiket = {
    EO1x1_Acente_Satis_Danismani:"Acente satış danışmanı", EO2x1_Stenos_Satis_Yoneticisi:"Stenos satış yöneticisi",
    C1_Satis_Elemani_Yaklasimi:"Satış elemanı yaklaşımı", C1a_Finansman_Kosullari_Bilgilendirme:"Finansman bilgilendirmesi",
    C2_Finansman_Secenekleri:"Finansman seçenekleri", C8_Geri_Odeme_Kosullari:"Geri ödeme koşulları",
    C5_Surec_Kolaylik_Hiz:"Süreç kolaylık & hız", E5a_Cagri_Merkezi_Memnuniyeti:"Çağrı merkezi",
  };
  const sat = Object.entries(etiket).map(([k, v]) => [v, guvenliOrt(rows.map(r => num(r[k])))]).filter(x => Number.isFinite(x[1]));
  sat.sort((a, b) => a[1] - b[1]);
  const sc = T().olcek.ikincil;
  const trace = {
    type:"bar", orientation:"h", y:sat.map(s => s[0]), x:sat.map(s => s[1]),
    text:sat.map(s => s[1].toFixed(2)), textposition:"outside", cliponaxis:false,
    marker:{color:sat.map(s => s[1]), colorscale:colorscaleOf(sc), showscale:false},
  };
  const layout = baseLayout({height:400, legendAlt:false, title:"Süreç Metrikleri — Ortalama Puanlar (10 üzerinden)"});
  layout.xaxis = Object.assign(layout.xaxis, {range:[0, 10.8], title:{text:""}});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:""}});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function aylikTrendChart(divId, rows) {
  const map = new Map();
  rows.forEach(r => {
    const key = r.Yil_Ay; if (!key) return;
    if (!map.has(key)) map.set(key, {sum:0, cnt:0, n:0});
    const o = map.get(key);
    const v = num(r.EO0_Genel_Memnuniyet);
    if (Number.isFinite(v)) { o.sum += v; o.cnt++; }
    o.n++;
  });
  const keys = Array.from(map.keys()).sort();
  const t = T(), palet = t.palet;
  const trace1 = {type:"bar", name:"Yanıt sayısı", x:keys, y:keys.map(k => map.get(k).n), marker:{color:t.kenar, opacity:.85}, yaxis:"y2"};
  const trace2 = {type:"scatter", mode:"lines+markers", name:"Ort. memnuniyet", x:keys, y:keys.map(k => { const o = map.get(k); return o.cnt ? o.sum / o.cnt : null; }), line:{color:palet[0], width:3}, marker:{size:7}};
  const layout = baseLayout({height:400, title:"Aylık Memnuniyet Trendi & Saha Hacmi"});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:"Ort. EO0"}, range:[0, 10.5]});
  layout.yaxis2 = {title:{text:"Yanıt"}, overlaying:"y", side:"right", showgrid:false, automargin:true};
  plot(divId, [trace1, trace2], layout, PLOTLY_CONFIG);
}

function nedenPieChart(divId, rows) {
  const t = T();
  const vc = valueCounts(rows.map(r => r.S3_Tercih_Etmeme_Nedeni));
  const labels = Array.from(vc.keys()), values = Array.from(vc.values());
  const trace = {
    type:"pie", labels, values, hole:.56, marker:{colors:t.palet}, textposition:"inside", textinfo:"percent",
    hovertemplate:"%{label}<br>%{value} yanıt (%{percent})<extra></extra>",
  };
  const layout = baseLayout({height:420, legendAlt:false, title:"Kredi Kullanmama Nedenleri"});
  layout.legend = {orientation:"v", x:1.02, y:.5, yanchor:"middle", font:{size:11}};
  layout.showlegend = true;
  layout.annotations = [{text:`<b>${rows.length}</b><br>yanıt`, showarrow:false, font:{size:17, color:t.metin}, x:0.5, y:0.5, xref:"paper", yref:"paper"}];
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function alternatifFinansmanChart(divId, rows) {
  const mapped = rows.map(r => (r.S5_Kredi_Kullanilan_Kurulus === "Henüz kredi kullanmadım" ? "Kredi kullanmadı (nakit)" : r.S5_Kredi_Kullanilan_Kurulus));
  const vc = valueCounts(mapped);
  const top10 = Array.from(vc.entries()).slice(0, 10).sort((a, b) => a[1] - b[1]);
  const sc = T().olcek.vurgu;
  const trace = {
    type:"bar", orientation:"h", y:top10.map(x => x[0]), x:top10.map(x => x[1]),
    text:top10.map(x => x[1]), textposition:"outside", cliponaxis:false,
    marker:{color:top10.map(x => x[1]), colorscale:colorscaleOf(sc), showscale:false},
  };
  const layout = baseLayout({height:420, legendAlt:false, title:"Alternatif Finansman Kaynağı (S5) — İlk 10"});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:""}});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:""}});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function nedenGelirHeatmap(divId, rows) {
  const gelirSira = ["25.000 TL altı", "25.001 - 50.000 TL", "50.001 - 85.000 TL", "85.001 - 150.000 TL", "150.000 TL üzeri"];
  const mevcutGelir = gelirSira.filter(g => rows.some(r => r.Gelir_Grubu === g));
  const nedenler = Array.from(new Set(rows.map(r => r.S3_Tercih_Etmeme_Nedeni).filter(Boolean))).sort();
  const z = nedenler.map(n => {
    const sub = rows.filter(r => r.S3_Tercih_Etmeme_Nedeni === n);
    const total = sub.length;
    return mevcutGelir.map(g => (total ? sub.filter(r => r.Gelir_Grubu === g).length / total * 100 : 0));
  });
  const sc = T().olcek.ana;
  const trace = {type:"heatmap", z, x:mevcutGelir, y:nedenler, colorscale:colorscaleOf(sc), texttemplate:"%{z:.0f}", showscale:false, hovertemplate:"%{y} × %{x}: %{z:.1f}%<extra></extra>"};
  const layout = baseLayout({height:430, legendAlt:false, title:"Isı Haritası — Neden × Gelir Grubu (satır %)"});
  layout.xaxis = Object.assign(layout.xaxis, {side:"bottom", tickangle:-20});
  layout.yaxis = Object.assign(layout.yaxis, {autorange:"reversed"});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function gelirNedenStackedChart(divId, rows) {
  const gelirSira = ["25.000 TL altı", "25.001 - 50.000 TL", "50.001 - 85.000 TL", "85.001 - 150.000 TL", "150.000 TL üzeri"];
  const mevcutGelir = gelirSira.filter(g => rows.some(r => r.Gelir_Grubu === g));
  const nedenler = Array.from(new Set(rows.map(r => r.S3_Tercih_Etmeme_Nedeni).filter(Boolean))).sort();
  const palet = T().palet;
  const traces = nedenler.map((n, i) => ({
    type:"bar", name:n, x:mevcutGelir,
    y:mevcutGelir.map(g => rows.filter(r => r.Gelir_Grubu === g && r.S3_Tercih_Etmeme_Nedeni === n).length),
    marker:{color:palet[i % palet.length]},
  }));
  const layout = baseLayout({height:430, title:"Gelir Grubuna Göre Neden Dağılımı"});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:""}, tickangle:-20});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:"Yanıt sayısı"}});
  layout.barmode = "stack";
  layout.legend = Object.assign(layout.legend, {orientation:"h", y:-0.35, font:{size:10}});
  plot(divId, traces, layout, PLOTLY_CONFIG);
}

function s11Chart(divId, rows) {
  const order = ["%0 -%25", "%26 - %50", "%51 - %75", "%76 - %100"];
  const counts = order.map(o => rows.filter(r => r.S11_Gelecekte_Tercih_Olasiligi === o).length);
  const colors = [NPS_RENK.Detractor, NPS_RENK.Passive, T().palet[1], NPS_RENK.Promoter];
  const trace = {type:"bar", x:order, y:counts, text:counts, textposition:"outside", cliponaxis:false, marker:{color:colors}};
  const layout = baseLayout({height:400, legendAlt:false, title:"S11 — Gelecekte Stenos Finans'ı Tercih Olasılığı"});
  layout.showlegend = false;
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:""}});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:"Yanıt sayısı"}});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function s9Chart(divId, rows) {
  const exploded = cokluAc(rows.map(r => r.S9_Onemli_Ek_Avantajlar));
  const vc = valueCounts(exploded);
  const arr = Array.from(vc.entries()).sort((a, b) => a[1] - b[1]);
  const sc = T().olcek.ikincil;
  const trace = {
    type:"bar", orientation:"h", y:arr.map(x => x[0]), x:arr.map(x => x[1]),
    text:arr.map(x => x[1]), textposition:"outside", cliponaxis:false,
    marker:{color:arr.map(x => x[1]), colorscale:colorscaleOf(sc), showscale:false},
  };
  const layout = baseLayout({height:400, legendAlt:false, title:"S9 — Faiz Dışında Önem Verilen Ek Avantajlar"});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:""}});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:""}});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function crmSatisScatterChart(divId, rows) {
  const t = T();
  const pts = rows.filter(r => Number.isFinite(num(r.CRM_Memnuniyeti_Birlesik)) && Number.isFinite(num(r.Acente_Satis_Basarisi_Endeks_100)));
  if (pts.length <= 2) return false;
  const r = pearson(pts.map(p => num(p.CRM_Memnuniyeti_Birlesik)), pts.map(p => num(p.Acente_Satis_Basarisi_Endeks_100)));
  const groups = new Map();
  pts.forEach(p => {
    const key = p.Acente_Adi + "||" + p.Bolge;
    if (!groups.has(key)) groups.set(key, {Acente_Adi:p.Acente_Adi, Bolge:p.Bolge, crmSum:0, satisSum:0, n:0});
    const g = groups.get(key);
    g.crmSum += num(p.CRM_Memnuniyeti_Birlesik); g.satisSum += num(p.Acente_Satis_Basarisi_Endeks_100); g.n++;
  });
  const ozet = Array.from(groups.values()).map(g => ({...g, CRM:g.crmSum / g.n, Satis:g.satisSum / g.n}));
  const bolgeler = Array.from(new Set(ozet.map(o => o.Bolge)));
  const palet = t.palet;
  const sref = sizerefFor(ozet.map(o => o.n), 42);
  const traces = bolgeler.map((b, i) => {
    const sub = ozet.filter(o => o.Bolge === b);
    return {
      type:"scatter", mode:"markers", name:b, x:sub.map(o => o.CRM), y:sub.map(o => o.Satis),
      marker:{size:sub.map(o => o.n), sizemode:"area", sizeref:sref, sizemin:6, color:palet[i % palet.length], opacity:.85},
      text:sub.map(o => escapeHtml(o.Acente_Adi)), hovertemplate:"%{text}<br>CRM: %{x:.2f}<br>Satış: %{y:.1f}<extra></extra>",
    };
  });
  if (ozet.length > 2) {
    const lr = linreg(ozet.map(o => o.CRM), ozet.map(o => o.Satis));
    const xmin = Math.min(...ozet.map(o => o.CRM)), xmax = Math.max(...ozet.map(o => o.CRM));
    const xs = linspace(xmin, xmax, 60);
    traces.push({type:"scatter", mode:"lines", name:"Trend", showlegend:false, x:xs, y:xs.map(x => lr.slope * x + lr.intercept), line:{color:t.vurgu, width:2.5, dash:"dash"}});
  }
  const layout = baseLayout({height:460, legendSatir:2, title:`Acente Bazında CRM × Satış Başarısı — birey düzeyi r = ${r.toFixed(3)}`});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:"Ort. Stenos CRM memnuniyeti (10 üzerinden)"}});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:"Acente satış başarısı endeksi (0-100)"}});
  layout.legend.font = {size:10};
  plot(divId, traces, layout, PLOTLY_CONFIG);
  return true;
}

function crmBandChart(divId, rows) {
  const edges = [0, 5, 6, 7, 8, 10], labels = ["≤5", "6", "7", "8", "9-10"];
  const pts = rows.filter(r => Number.isFinite(num(r.CRM_Memnuniyeti_Birlesik)));
  const bands = labels.map(l => ({label:l, rows:[]}));
  pts.forEach(r => { const lbl = pdCut(num(r.CRM_Memnuniyeti_Birlesik), edges, labels); if (lbl) bands.find(b => b.label === lbl).rows.push(r); });
  const ozet = bands.filter(b => b.rows.length).map(b => ({label:b.label, satis:guvenliOrt(b.rows.map(r => num(r.Acente_Satis_Basarisi_Endeks_100))), n:b.rows.length})).filter(o => Number.isFinite(o.satis));
  if (!ozet.length) return;
  const sc = T().olcek.ana;
  const trace = {
    type:"bar", x:ozet.map(o => o.label), y:ozet.map(o => o.satis), text:ozet.map(o => o.n),
    texttemplate:"n=%{text}", textposition:"outside", cliponaxis:false,
    marker:{color:ozet.map(o => o.satis), colorscale:colorscaleOf(sc), showscale:false},
  };
  const layout = baseLayout({height:440, legendAlt:false, title:"CRM Memnuniyet Bandına Göre Satış Başarısı"});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:"Ort. satış başarısı endeksi"}, range:[0, 105]});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:"CRM memnuniyet puanı"}});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function sistemAksakliklarChart(divId, rows) {
  const exploded = cokluAc(rows.map(r => r.M9_Iyilestirilecek_Konular));
  const vc = valueCounts(exploded);
  const top12 = Array.from(vc.entries()).slice(0, 12);
  const arr = top12.map(([k, v]) => ({konu:k, yanit:v, pay:v / rows.length * 100})).sort((a, b) => a.yanit - b.yanit);
  const sc = T().olcek.negatif;
  const trace = {
    type:"bar", orientation:"h", y:arr.map(a => a.konu), x:arr.map(a => a.yanit),
    text:arr.map(a => a.pay), texttemplate:"%{text:.0f}%", textposition:"outside", cliponaxis:false,
    marker:{color:arr.map(a => a.yanit), colorscale:colorscaleOf(sc), showscale:false},
  };
  const layout = baseLayout({height:470, legendAlt:false, title:"M9 — En Sık Bildirilen Sorun Alanları (İlk 12)"});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:"Yanıt sayısı"}});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:""}});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function mutluEdenChart(divId, rows) {
  const exploded = cokluAc(rows.map(r => r.M8_Mutlu_Eden_Etkenler));
  const vc = valueCounts(exploded);
  const top8 = Array.from(vc.entries()).slice(0, 8).sort((a, b) => a[1] - b[1]);
  const sc = T().olcek.pozitif;
  const trace = {
    type:"bar", orientation:"h", y:top8.map(x => x[0]), x:top8.map(x => x[1]),
    text:top8.map(x => x[1]), textposition:"outside", cliponaxis:false,
    marker:{color:top8.map(x => x[1]), colorscale:colorscaleOf(sc), showscale:false},
  };
  const layout = baseLayout({height:470, legendAlt:false, title:"M8 — Memnuniyet Yaratan Etkenler (İlk 8)"});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:""}});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:""}});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function dsiRadarChart(divId, rows) {
  const metrikler = {
    S3b_Stenos_CRM_Memnuniyeti:"CRM genel (Satış)", S3bx_Stenos_CRM_Memnuniyeti_Sigorta:"CRM genel (Sigorta)",
    S3b_1_CRM_Sistem_Hizi:"CRM sistem hızı", S3a_Kredilendirme_Sureci:"Kredilendirme süreci",
    S5c_Egitim_Memnuniyeti:"C-Sales eğitimleri", S1_1_Ziyaret_Genel_Memnuniyet:"Acente ziyaretleri",
    S1_2_Ziyaret_Sikligi_Memnuniyet:"Ziyaret sıklığı", M4a_Genel_Memnuniyet_Finans:"Genel memnuniyet (M4a)",
  };
  const sat = Object.entries(metrikler).map(([k, v]) => [v, guvenliOrt(rows.map(r => num(r[k])))]).filter(x => Number.isFinite(x[1]));
  if (!sat.length) return;
  const t = T(), palet = t.palet;
  const theta = sat.map(s => s[0]), r = sat.map(s => s[1]);
  const trace = {type:"scatterpolar", r:[...r, r[0]], theta:[...theta, theta[0]], fill:"toself", line:{color:palet[0], width:2}, fillcolor:saydam(palet[0], .28), name:"Ortalama"};
  const layout = baseLayout({height:430, legendAlt:false, title:"DSI Metrik Profili (10 üzerinden)"});
  layout.polar = {radialaxis:{visible:true, range:[0, 10], gridcolor:t.grid}, angularaxis:{gridcolor:t.grid}, bgcolor:t.zemin};
  delete layout.xaxis; delete layout.yaxis;
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

function bolgeCrmSatisChart(divId, rows) {
  const groups = new Map();
  rows.forEach(r => {
    const b = r.Bolge; if (!b) return;
    if (!groups.has(b)) groups.set(b, {crmSum:0, crmN:0, satisSum:0, satisN:0});
    const g = groups.get(b);
    const crm = num(r.CRM_Memnuniyeti_Birlesik); if (Number.isFinite(crm)) { g.crmSum += crm; g.crmN++; }
    const satis = num(r.Acente_Satis_Basarisi_Endeks_100); if (Number.isFinite(satis)) { g.satisSum += satis; g.satisN++; }
  });
  const bol = Array.from(groups.entries()).map(([b, g]) => ({Bolge:b, CRM:g.crmN ? g.crmSum / g.crmN : NaN, Satis:g.satisN ? g.satisSum / g.satisN : NaN})).filter(o => Number.isFinite(o.CRM)).sort((a, b) => a.CRM - b.CRM);
  if (!bol.length) return;
  const palet = T().palet;
  const trace1 = {type:"bar", orientation:"h", y:bol.map(o => o.Bolge), x:bol.map(o => o.CRM), name:"CRM memnuniyeti", marker:{color:palet[0]}, text:bol.map(o => o.CRM.toFixed(2)), textposition:"outside"};
  const trace2 = {type:"scatter", mode:"markers", y:bol.map(o => o.Bolge), x:bol.map(o => (Number.isFinite(o.Satis) ? o.Satis / 10 : null)), name:"Satış başarısı (÷10)", marker:{size:13, color:palet[3], symbol:"diamond"}};
  const layout = baseLayout({height:430, title:"Bölgeye Göre CRM Memnuniyeti & Satış Başarısı"});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:"Puan (10 üzerinden)"}, range:[0, 11]});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:""}});
  plot(divId, [trace1, trace2], layout, PLOTLY_CONFIG);
}

function csiDsiNpsChart(divId, M) {
  const t = T();
  const cmp = [{Segment:"Müşteri (CSI)", NPS:Math.round(M.csi_nps)}, {Segment:"Bayi (DSI)", NPS:Math.round(M.dsi_nps)}];
  const renk = v => (v >= 50 ? NPS_RENK.Promoter : (v >= 0 ? NPS_RENK.Passive : NPS_RENK.Detractor));
  const traces = cmp.map(c => ({
    type:"bar", orientation:"h", y:[c.Segment], x:[c.NPS], name:c.Segment, marker:{color:renk(c.NPS)},
    text:[fmtSigned(c.NPS, 0)], texttemplate:"%{text}", textposition:"outside", cliponaxis:false, showlegend:false,
  }));
  const layout = baseLayout({height:300, legendAlt:false, title:"Müşteri NPS ↔ Bayi NPS Makası"});
  layout.showlegend = false;
  layout.shapes = [{type:"line", xref:"x", x0:0, x1:0, yref:"paper", y0:0, y1:1, line:{width:1, color:t.soluk}}];
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:"NPS"}, range:[-60, 80]});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:""}});
  plot(divId, traces, layout, PLOTLY_CONFIG);
}

function sorunOnlemeChart(divId, M) {
  const nps3 = _nps(VERI.kredi.filter(r => num(r.I1_Sorun_Yasadi_mi) === 1 && num(r.I2_Sorun_Giderildi_mi) === 2).map(r => num(r.F1_Recommendation_NPS)));
  const sr = {
    "Sorun yaşamadı":Math.round(M.nps_sorunsuz), "Sorun çözüldü":Math.round(M.nps_cozuldu), "Sorun çözülmedi":Math.round(nps3),
  };
  const order = ["Sorun çözülmedi", "Sorun çözüldü", "Sorun yaşamadı"];
  const sc = T().olcek.ana;
  const trace = {
    type:"bar", orientation:"h", y:order, x:order.map(o => sr[o]),
    text:order.map(o => fmtSigned(sr[o], 0)), texttemplate:"%{text}", textposition:"outside", cliponaxis:false,
    marker:{color:order.map(o => sr[o]), colorscale:colorscaleOf(sc), showscale:false},
  };
  const layout = baseLayout({height:300, legendAlt:false, title:`Sorun Önlemenin Değeri (sorun oranı ${fmtPct1(M.sorun_oran, 0)})`});
  layout.xaxis = Object.assign(layout.xaxis, {title:{text:"NPS"}, range:[0, 75]});
  layout.yaxis = Object.assign(layout.yaxis, {title:{text:""}});
  plot(divId, [trace], layout, PLOTLY_CONFIG);
}

/* ============================== HAM VERİ / İNDİRME ============================== */
function downloadCsv(rows, filename) {
  if (!rows.length) return;
  const cols = Object.keys(rows[0]).filter(c => !c.startsWith("_"));
  const esc = v => { if (v === undefined || v === null) return ""; const s = String(v); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
  const lines = [cols.join(",")];
  rows.forEach(r => lines.push(cols.map(c => esc(r[c])).join(",")));
  const blob = new Blob(["﻿" + lines.join("\r\n")], {type:"text/csv;charset=utf-8;"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
}
function renderRawTable(container, rows) {
  if (!rows.length) { container.innerHTML = '<div class="bos-uyari">Satır yok.</div>'; return; }
  const cols = Object.keys(rows[0]).filter(c => !c.startsWith("_"));
  let html = '<table class="raw-table"><thead><tr>' + cols.map(c => `<th>${escapeHtml(c)}</th>`).join("") + "</tr></thead><tbody>";
  rows.forEach(r => { html += "<tr>" + cols.map(c => `<td>${escapeHtml(r[c])}</td>`).join("") + "</tr>"; });
  html += "</tbody></table>";
  container.innerHTML = html;
}
function hamVeriBolumu(container, filteredRows, allRows, dosyaKoku) {
  const n = filteredRows.length, N = allRows.length;
  const expId = uid();
  container.insertAdjacentHTML("beforeend", `
    <div class="expander" id="${expId}">
      <div class="expander-head"><span>🔎 Ham veriyi görüntüle / indir — ${fmtInt(n)} / ${fmtInt(N)} satır (filtre uygulanmış)</span><span class="arrow">▸</span></div>
      <div class="expander-body">
        <div class="expander-caption">${activeFiltreText()}</div>
        ${n < N ? `<div class="expander-caption">Toplam ${fmtInt(N)} kayıttan ${fmtInt(N - n)} tanesi filtre dışında kaldı.</div>` : ""}
        <div class="raw-table-wrap" id="${expId}-table"></div>
        <button class="dl-button" id="${expId}-dl">⬇️ Filtrelenmiş CSV'yi indir (${fmtInt(n)} satır)</button>
      </div>
    </div>`);
  const expEl = document.getElementById(expId);
  expEl.querySelector(".expander-head").addEventListener("click", () => {
    const wasOpen = expEl.classList.contains("open");
    expEl.classList.toggle("open");
    if (!wasOpen && !expEl.dataset.rendered) { renderRawTable(document.getElementById(expId + "-table"), filteredRows); expEl.dataset.rendered = "1"; }
  });
  document.getElementById(expId + "-dl").addEventListener("click", () => downloadCsv(filteredRows, `${dosyaKoku}_${dosyaAdiEki()}.csv`));
}

/* ============================== YÖNETİCİ METRİKLERİ ============================== */
function yoneticiMetrikleri() {
  if (_yoneticiCache) return _yoneticiCache;
  const k = VERI.kredi, n = VERI.nakit, d = VERI.dsi;
  const M = {n_kredi:k.length, n_nakit:n.length, n_dsi:d.length, toplam:k.length + n.length + d.length};

  M.csi_nps = _nps(k.map(r => num(r.F1_Recommendation_NPS)));
  M.dsi_nps = _nps(d.map(r => num(r.M6_Recommendation_NPS)));
  M.eo0 = guvenliOrt(k.map(r => num(r.EO0_Genel_Memnuniyet)));

  const cm = k.map(r => num(r.E5a_Cagri_Merkezi_Memnuniyeti));
  M.cagri_ort = guvenliOrt(cm);
  M.cagri_t2b = pctGE(cm, 9);
  M.e1_aradi = pctEq(k.map(r => num(r.E1_Musteri_Hizmetleri_Aradi_mi)), 1);
  M.e1_ulasamadi = pctEq(k.map(r => num(r.E1_Musteri_Hizmetleri_Aradi_mi)), 3);

  const edges = [0, 4, 8, 12, 24, 48, 1e4], labels = ["0-4 sa", "4-8 sa", "8-12 sa", "12-24 sa", "24-48 sa", "48+ sa"];
  const sc = k.filter(r => Number.isFinite(num(r.Kredi_Onay_Suresi_Saat)) && Number.isFinite(num(r.F1_Recommendation_NPS)));
  const bandNps = labels.map(lbl => {
    const rowsInBand = sc.filter(r => pdCut(num(r.Kredi_Onay_Suresi_Saat), edges, labels) === lbl);
    return rowsInBand.length ? {label:lbl, nps:_nps(rowsInBand.map(r => num(r.F1_Recommendation_NPS)))} : null;
  }).filter(Boolean);
  const negBand = bandNps.find(b => b.nps <= 0);
  M.esik = negBand ? negBand.label : "—";

  const rr = k.filter(row => row.Filo_Retail === "Retail");
  M.attach = pctEq(rr.map(row => num(row.K1_1_Kasko_Satin_Aldi_mi)), 1);
  const nb = rr.filter(row => num(row.K1_1_Kasko_Satin_Aldi_mi) === 2);
  M.kasko_teklifsiz = nb.length ? pctEq(nb.map(row => num(row.K1_2_Kasko_Teklifi_Verildi_mi)), 2) : NaN;
  const tv = nb.filter(row => num(row.K1_2_Kasko_Teklifi_Verildi_mi) === 1);
  M.kasko_avantajsiz = tv.length ? pctEq(tv.map(row => num(row.K8_Avantajlardan_Bahsedildi_mi)), 2) : NaN;

  M.sorun_oran = pctEq(k.map(row => num(row.I1_Sorun_Yasadi_mi)), 1);
  M.nps_sorunsuz = _nps(k.filter(row => num(row.I1_Sorun_Yasadi_mi) === 2).map(row => num(row.F1_Recommendation_NPS)));
  const s_ = k.filter(row => num(row.I1_Sorun_Yasadi_mi) === 1);
  M.nps_cozuldu = _nps(s_.filter(row => num(row.I2_Sorun_Giderildi_mi) === 1).map(row => num(row.F1_Recommendation_NPS)));
  M.cozum_oran = s_.length ? pctEq(s_.map(row => num(row.I2_Sorun_Giderildi_mi)), 1) : NaN;

  M.mobil_farkinda = pctEq(k.map(row => num(row.N3_Mobil_App_Bilinirlik)), 1);
  M.danisman_onermiyor = pctEq(d.map(row => num(row.S7_Mobil_App_Oneriyor_mu)), 2);

  const nedenMap = new Map();
  n.forEach(row => {
    const neden = row.S3_Tercih_Etmeme_Nedeni; if (!neden) return;
    if (!nedenMap.has(neden)) nedenMap.set(neden, {sum:0, n:0});
    const o = nedenMap.get(neden);
    o.sum += (num(row.S11_Yuksek_Egilim) === 1 ? 1 : 0); o.n++;
  });
  M.gk = Array.from(nedenMap.entries()).map(([label, v]) => [label, v.n ? v.sum / v.n * 100 : 0]).sort((a, b) => b[1] - a[1]);

  const dm = {
    S1_2_Ziyaret_Sikligi_Memnuniyet:"Ziyaret sıklığı", S3b_1_CRM_Sistem_Hizi:"CRM sistem hızı",
    CRM_Memnuniyeti_Birlesik:"CRM genel memnuniyeti", S5c_Egitim_Memnuniyeti:"C-Sales eğitimleri",
    M4a_Genel_Memnuniyet_Finans:"Genel memnuniyet",
  };
  const dv = {};
  Object.entries(dm).forEach(([col, label]) => { if (d.length && col in d[0]) dv[label] = guvenliOrt(d.map(row => num(row[col]))); });
  let minLabel = null, minVal = Infinity;
  Object.entries(dv).forEach(([label, val]) => { if (Number.isFinite(val) && val < minVal) { minVal = val; minLabel = label; } });
  M.dsi_min = minLabel; M.dsi_min_val = minVal;

  const bolgeMap = new Map();
  k.forEach(row => {
    const b = row.Bolge; if (!b) return;
    if (!bolgeMap.has(b)) bolgeMap.set(b, {npsArr:[], onaySum:0, onayN:0});
    const g = bolgeMap.get(b);
    g.npsArr.push(num(row.F1_Recommendation_NPS));
    const onay = num(row.Kredi_Onay_Suresi_Saat);
    if (Number.isFinite(onay)) { g.onaySum += onay; g.onayN++; }
  });
  const gb = Array.from(bolgeMap.entries()).map(([b, g]) => ({Bolge:b, nps:_nps(g.npsArr), onay:g.onayN ? g.onaySum / g.onayN : NaN})).sort((a, b) => a.nps - b.nps);
  M.bolge_dusuk = [gb[0].Bolge, gb[0].nps, gb[0].onay];
  M.bolge_yuksek = [gb[gb.length - 1].Bolge, gb[gb.length - 1].nps, gb[gb.length - 1].onay];

  _yoneticiCache = M;
  return M;
}

/* ============================== SEKME RENDER ============================== */
function renderGenelBakis(rows, toplam) {
  const t = T();
  document.getElementById("genel-bakis").innerHTML = [
    kpiHtml("Toplam Yanıt", fmtInt(toplam), `${fmtInt(VERI.kredi.length + VERI.nakit.length + VERI.dsi.length)} kayıt içinden`, t.vurgu, null),
    kpiHtml("Kredi Kullanan (CSI)", fmtInt(rows.kredi.length), "Müşteri anketi", t.kpi[0], null),
    kpiHtml("Kredi Kullanmayan (CSI)", fmtInt(rows.nakit.length), "Müşteri anketi", t.kpi[2], null),
    kpiHtml("Bayi Çalışanı (DSI)", fmtInt(rows.dsi.length), "Acente anketi", t.kpi[3], null),
  ].join("");
}

function renderTab1(container, rows) {
  if (!rows.length) { container.innerHTML = bosUyariHtml("Kredi Kullanan Müşteri segmentinde yanıt yok."); return; }
  const t = T();
  const eo0 = guvenliOrt(rows.map(r => num(r.EO0_Genel_Memnuniyet)));
  const npsInfo = npsHesapla(rows.map(r => num(r.F1_Recommendation_NPS)));
  const surecKolonlari = ["C1a_Finansman_Kosullari_Bilgilendirme", "C2_Finansman_Secenekleri", "C8_Geri_Odeme_Kosullari", "C5_Surec_Kolaylik_Hiz"].filter(c => c in rows[0]);
  const surec = surecKolonlari.length ? guvenliOrt(rows.map(r => rowMeanCols(r, surecKolonlari))) : NaN;
  const t2b = pctGE(rows.map(r => num(r.EO0_Genel_Memnuniyet)), 9);
  const npsRenk = npsInfo.nps >= 50 ? NPS_RENK.Promoter : (npsInfo.nps >= 0 ? NPS_RENK.Passive : NPS_RENK.Detractor);

  const ids = newIdSet(["eo0dist", "npsgauge", "onayScatter", "onayEsik", "surecMetrik", "aylikTrend"]);
  container.innerHTML = `
    <div class="kpi-row grid-4">
      ${kpiHtml("Genel Memnuniyet (EO0)", fmtNum2(eo0), "10 üzerinden ortalama", t.kpi[0], eo0 / 10)}
      ${kpiHtml("NPS · Net Tavsiye Skoru", fmtSigned(npsInfo.nps, 0), `Promoter ${fmtPct1(npsInfo.p, 0)} · Detractor ${fmtPct1(npsInfo.d, 0)}`, npsRenk, (npsInfo.nps + 100) / 200)}
      ${kpiHtml("Kredi Süreci Memnuniyeti", fmtNum2(surec), "C1a · C2 · C8 · C5 ortalaması", t.kpi[2], surec / 10)}
      ${kpiHtml("Memnuniyet Top-2-Box", fmtPct1(t2b), "9-10 puan verenler", t.kpi[4], t2b / 100)}
    </div>
    <div id="marka1"></div>
    ${baslikHtml("Memnuniyet Puanı Dağılımları", "EO0 genel memnuniyet dağılımı ve NPS kırılımı")}
    <div class="row c2-145">
      <div id="${ids.eo0dist}" class="chart-box"></div>
      <div id="${ids.npsgauge}" class="chart-box"></div>
    </div>
    ${baslikHtml("Kredi Onay Süresi — Korelasyon ve Eşik Analizi", "Solda süre ile süreç memnuniyeti (C5) ilişkisi, sağda NPS'in işareti değiştirdiği kırılma bandı")}
    <div class="row c2-13">
      <div id="${ids.onayScatter}" class="chart-box"></div>
      <div><div id="${ids.onayEsik}" class="chart-box"></div><div class="chart-caption" id="${ids.onayEsik}-cap"></div></div>
    </div>
    <div class="row c2">
      <div id="${ids.surecMetrik}" class="chart-box"></div>
      <div id="${ids.aylikTrend}" class="chart-box"></div>
    </div>
    <div id="hamveri1"></div>
  `;
  markaMetrikBloku(document.getElementById("marka1"), rows, MARKA_METRIKLERI_CSI, "Marka Metrikleri — 10'lu Skala",
    "Genel memnuniyet, tavsiye, marka önemi ve tekrar tercih puanları · F1 skalası 0-10, diğerleri 1-10");
  eo0DagilimChart(ids.eo0dist, rows);
  npsGaugeChart(ids.npsgauge, npsInfo.nps);
  if (!onaySureciScatterChart(ids.onayScatter, rows)) document.getElementById(ids.onayScatter).innerHTML = bosUyariHtml("Korelasyon için yeterli veri yok.");
  if (onaySuresiEsikChart(ids.onayEsik, rows)) document.getElementById(ids.onayEsik + "-cap").textContent = "Çubuk etiketleri NPS'tir; yanıt sayısı, ortalama memnuniyet ve Top-2-Box için imleci çubuğun üzerine getirin.";
  surecMetrikleriChart(ids.surecMetrik, rows);
  aylikTrendChart(ids.aylikTrend, rows);
  hamVeriBolumu(document.getElementById("hamveri1"), rows, VERI.kredi, "Stenos_CSI_KrediKullanan");
}

function renderTab2(container, rows) {
  if (!rows.length) { container.innerHTML = bosUyariHtml("Kredi Kullanmayan Müşteri segmentinde yanıt yok."); return; }
  const t = T();
  const vc = valueCounts(rows.map(r => r.S3_Tercih_Etmeme_Nedeni));
  const first = Array.from(vc.entries())[0];
  const enCok = first ? first[0] : "—", enCokPay = first ? first[1] / rows.length * 100 : NaN;
  const alternatif = pctNotEq(rows.map(r => r.S5_Kredi_Kullanilan_Kurulus), "Henüz kredi kullanmadım");
  const s6 = guvenliOrt(rows.map(r => num(r.S6_Bilgilendirme_Memnuniyeti)));
  const yuksekEgilim = guvenliOrt(rows.map(r => num(r.S11_Yuksek_Egilim))) * 100;

  const ids = newIdSet(["pie", "alt", "heat", "stack", "s11", "s9"]);
  container.innerHTML = `
    <div class="kpi-row grid-4">
      ${kpiHtml("Öne Çıkan Ret Nedeni", fmtPct1(enCokPay), enCok, NPS_RENK.Detractor, enCokPay / 100)}
      ${kpiHtml("Alternatif Finansman Oranı", fmtPct1(alternatif), "Rakip kuruluştan kredi kullananlar", t.kpi[4], alternatif / 100)}
      ${kpiHtml("Bilgilendirme Memnuniyeti (S6)", fmtNum2(s6), "10 üzerinden ortalama", t.kpi[1], s6 / 10)}
      ${kpiHtml("Yeniden Tercih Eğilimi", fmtPct1(yuksekEgilim), "S11 · %51+ olasılık verenler", t.kpi[2], yuksekEgilim / 100)}
    </div>
    ${baslikHtml('"Neden Kredi Kullanılmadı?" Kırılımı', "S3 — Stenos Auto Finans'ı tercih etmeme nedenleri")}
    <div class="row c2-125">
      <div id="${ids.pie}" class="chart-box"></div>
      <div id="${ids.alt}" class="chart-box"></div>
    </div>
    ${baslikHtml("Gelir Grubu × Kredi Kullanmama Nedeni — Çapraz Analiz", "Satır yüzdeleri: her nedenin gelir bantlarına dağılımı")}
    <div class="row c2-13">
      <div id="${ids.heat}" class="chart-box"></div>
      <div id="${ids.stack}" class="chart-box"></div>
    </div>
    <div class="row c2">
      <div id="${ids.s11}" class="chart-box"></div>
      <div id="${ids.s9}" class="chart-box"></div>
    </div>
    <div id="hamveri2"></div>
  `;
  nedenPieChart(ids.pie, rows);
  alternatifFinansmanChart(ids.alt, rows);
  nedenGelirHeatmap(ids.heat, rows);
  gelirNedenStackedChart(ids.stack, rows);
  s11Chart(ids.s11, rows);
  s9Chart(ids.s9, rows);
  hamVeriBolumu(document.getElementById("hamveri2"), rows, VERI.nakit, "Stenos_CSI_KrediKullanmayan");
}

function renderTab3(container, rows) {
  if (!rows.length) { container.innerHTML = bosUyariHtml("Bayi Çalışanı / DSI segmentinde yanıt yok."); return; }
  const t = T();
  const crm = guvenliOrt(rows.map(r => num(r.CRM_Memnuniyeti_Birlesik)));
  const hiz = guvenliOrt(rows.map(r => num(r.S3b_1_CRM_Sistem_Hizi)));
  const destek = guvenliOrt(rows.map(r => num(r.S1_1_Ziyaret_Genel_Memnuniyet)));
  const destekN = rows.map(r => num(r.S1_1_Ziyaret_Genel_Memnuniyet)).filter(Number.isFinite).length;
  const egitim = guvenliOrt(rows.map(r => num(r.S5c_Egitim_Memnuniyeti)));

  const ids = newIdSet(["scatter", "band", "sorun", "pozitif", "radar", "bolge"]);
  container.innerHTML = `
    <div class="kpi-row grid-4">
      ${kpiHtml("CRM Kullanım Memnuniyeti", fmtNum2(crm), "S3b / S3bx · 10 üzerinden", t.kpi[0], crm / 10)}
      ${kpiHtml("Sistem Hızı Puanı", fmtNum2(hiz), "Stenos CRM yanıt hızı", t.kpi[1], hiz / 10)}
      ${kpiHtml("Bayi Destek Puanı", fmtNum2(destek), `S1.1 acente ziyaretleri · baz n=${destekN}`, t.kpi[2], destek / 10)}
      ${kpiHtml("Eğitim Memnuniyeti", fmtNum2(egitim), "S5c · C-Sales eğitimleri", t.kpi[4], egitim / 10)}
    </div>
    ${baslikHtml("CRM Memnuniyetinin Satış Performansına Etkisi", "Acente bazında: CRM memnuniyeti yükseldikçe satış başarısı endeksi artıyor")}
    <div class="row c2-135">
      <div id="${ids.scatter}" class="chart-box"></div>
      <div id="${ids.band}" class="chart-box"></div>
    </div>
    ${baslikHtml("En Çok Yaşanan Sistemsel Aksaklıklar", "M9 — Bayi çalışanlarının iyileştirilmesini istediği konular (çoklu yanıt)")}
    <div class="row c2-14">
      <div id="${ids.sorun}" class="chart-box"></div>
      <div id="${ids.pozitif}" class="chart-box"></div>
    </div>
    <div class="row c2">
      <div id="${ids.radar}" class="chart-box"></div>
      <div id="${ids.bolge}" class="chart-box"></div>
    </div>
    <div id="hamveri3"></div>
  `;
  if (!crmSatisScatterChart(ids.scatter, rows)) document.getElementById(ids.scatter).innerHTML = bosUyariHtml("Korelasyon için yeterli veri yok.");
  crmBandChart(ids.band, rows);
  sistemAksakliklarChart(ids.sorun, rows);
  mutluEdenChart(ids.pozitif, rows);
  dsiRadarChart(ids.radar, rows);
  bolgeCrmSatisChart(ids.bolge, rows);
  hamVeriBolumu(document.getElementById("hamveri3"), rows, VERI.dsi, "Stenos_DSI_BayiCalisanlari");
}

function aksiyonKartlariHtml(M) {
  const KIRMIZI = NPS_RENK.Detractor, TURUNCU = NPS_RENK.Passive, MAVI = T().vurgu;
  let html = "";
  html += aksiyonHtml(1, KIRMIZI, "Ulaşılabilirlik krizi", "90 gün · kritik", KIRMIZI,
    `Üç kaynak aynı yeri işaret ediyor: çağrı merkezi en düşük CSI metriği (Top-2-Box <b>${fmtPct1(M.cagri_t2b, 0)}</b>), müşterilerin <b>${fmtPct1(M.e1_ulasamadi, 0)}</b>'i "aradım ama ulaşamadım" diyor ve DSI'da en sık üç şikâyetin üçü iletişimle ilgili.`,
    "Servis seviyesi (SL/ASA/abandon) ölçümünü haftalık yönetim gündemine almak, bayi hattını müşteri hattından ayırmak, geri arama taahhüdü koymak.");
  html += aksiyonHtml(2, TURUNCU, "Kasko — masada duran gelir", "60 gün · yüksek getiri", TURUNCU,
    `Kasko almayan Retail müşterilerin <b>${fmtPct1(M.kasko_teklifsiz, 0)}</b>'ine teklif hiç verilmemiş; teklif verilenlerin <b>${fmtPct1(M.kasko_avantajsiz, 0)}</b>'ine ürün avantajları anlatılmamış. Bu fiyat değil, uygulama kaybı (mevcut attach ${fmtPct1(M.attach, 0)}).`,
    "Teklif verme adımını CRM'de zorunlu alan yapmak, danışmana 3 maddelik avantaj kartı vermek.");
  html += aksiyonHtml(3, MAVI, "Onay süresini bölgesel yönetmek", "orta vade", MAVI,
    `Kırılma eşiği <b>${M.esik}</b>. Bölge uçları net: ${M.bolge_yuksek[0]} ${M.bolge_yuksek[2].toFixed(1)} sa / NPS ${fmtSigned(M.bolge_yuksek[1], 0)} ↔ ${M.bolge_dusuk[0]} ${M.bolge_dusuk[2].toFixed(1)} sa / NPS ${fmtSigned(M.bolge_dusuk[1], 0)}.`,
    "Onay süresi hedefini bölge müdürü karnesine koymak; 8 saati aşan dosyalarda otomatik eskalasyon. (Acente tabanları küçük — bölge düzeyinde konuşulmalı, acente sıralaması yayınlanmamalı.)");
  html += aksiyonHtml(4, MAVI, "Önleme, kurtarmadan değerli", "süreç", MAVI,
    `Sorunsuz müşteri NPS <b>${fmtSigned(M.nps_sorunsuz, 0)}</b>; sorun çözülünce yalnızca <b>${fmtSigned(M.nps_cozuldu, 0)}</b>'e çıkıyor. "Çözdük" dediğimiz şey müşteride çözülmüş hissi bırakmıyor (çözüm oranı ${fmtPct1(M.cozum_oran, 0)}).`,
    "Çözüm tanımını müşteri onayına bağlamak (kapanışta teyit); kök neden analizini ilk üç sorun tipiyle başlatmak.");
  html += aksiyonHtml(5, TURUNCU, "Dijitali maliyet kalemi olarak yönetmek", "60 gün", TURUNCU,
    `Mobil uygulamadan haberdar yalnızca <b>${fmtPct1(M.mobil_farkinda, 0)}</b>; aynı anda ${fmtPct1(M.e1_aradi, 0)} çağrı merkezini arıyor ve danışmanların <b>${fmtPct1(M.danisman_onermiyor, 0)}</b>'i uygulamayı hiç önermiyor.`,
    'Teslimat anında uygulama kurulumunu sürece gömmek; danışman primine "uygulama indirme" adımını eklemek.');
  const gk0 = M.gk[0] || ["—", NaN], gk1 = M.gk[1] || ["—", NaN];
  html += aksiyonHtml(6, MAVI, "Kredi kullanmayanlarda hedefli geri kazanım", "orta vade", MAVI,
    `Geri dönüş eğilimi en yüksek gruplar: "${gk0[0]}" ${fmtPct1(gk0[1], 0)}, "${gk1[0]}" ${fmtPct1(gk1[1], 0)}. Faiz dışında en çok istenenler vade, özel temsilci ve sigorta — üçü de indirim gerektirmiyor.`,
    'Bu iki gruba ürün/kampanya ayarıyla dönüş; "limit alamadım" grubuna ayrı ret iletişimi tasarlamak.');
  html += aksiyonHtml(7, MAVI, "Bayi ilişkisini onarmak", "sürekli", MAVI,
    `DSI'da en zayıf metrik <b>${M.dsi_min}</b> (${fmtNum2(M.dsi_min_val)}/10). M9'da eğitim ve CRM hızı öne çıkan şikâyetler.`,
    "Ziyaret takvimini penetrasyonu düşük acentelere ağırlıklandırmak; CRM hız şikâyetini IT backlog'unda önceliklendirmek.");
  return html;
}
function oneriBlok1Html() {
  return `<div>
    <div class="oneri-kutu"><h4>📐 Ölçüm ritmi ikiye ayrılmalı</h4>
      <p><b>İşlemsel CSI</b> — kredi kullanımından 7-10 gün sonra, sürekli. Süreç, onay süresi, ilk temas. ~4-5 dk.</p>
      <p><b>İlişkisel CSI</b> — yılda 1 dalga. NPS, marka, tekrar tercih, rakip karşılaştırma. ~8-10 dk.</p>
      <p class="neden">Tek uzun dalga yerine olaya yakın ölçüm, hatırlama hatasını düşürür.</p>
    </div>
    <div class="oneri-kutu"><h4>➕ Eklenecek sorular</h4>
      <ul>
        <li>Müşteri eforu (CES) — ulaşılabilirlik ana sorunumuz, eforu hiç ölçmüyoruz</li>
        <li>İlk temasta çözüm + çözüm süresi — +23/+61 uçurumunun nedeni burada</li>
        <li>Rakip teklifin oranı/vadesi (rakam) — kaç baz puan gerektiğini bilmiyoruz</li>
        <li>Kaybın hangi aşamada olduğu (huni) — "reddettik" ile "fiyat" ayrışmalı</li>
        <li>Uygulama kullanımı — farkındalık değil, son 3 aydaki işlem</li>
        <li>DSI'ya komisyon rekabetçiliği ve rakip NPS'i</li>
      </ul>
    </div>
  </div>`;
}
function oneriBlok2Html() {
  return `<div>
    <div class="oneri-kutu"><h4>🧪 Metodolojik düzeltmeler</h4>
      <ul>
        <li><b>Örneklem:</b> DSI'da acente başına ~13 kişi kalıyor; acente karnesi için minimum taban belirlenmeli, yoksa kırılım bölgede kalmalı</li>
        <li><b>Ağırlıklandırma:</b> portföyün bayi/bölge/ürün dağılımına göre</li>
        <li><b>Halo etkisi:</b> süreç sorularını genel memnuniyetin hemen ardından sormak hepsini birbirine korele ediyor — blok sırası randomize edilmeli</li>
        <li><b>Kredi kullanmayan çerçevesi:</b> bizim datamızdaki kişiler değil, bayi trafiğinden örneklenmeli</li>
        <li><b>Karşılaştırılabilirlik:</b> soru metinleri ve skalalar dondurulmalı (F1 0-10, diğerleri 1-10 ayrımı korunmalı)</li>
      </ul>
    </div>
    <div class="oneri-kutu"><h4>➖ Yer açmak için çıkarılabilecekler</h4>
      <p class="neden">Kasko K2 (nereden haberdar), pazarlama N2 (takip kanalı) düşük aksiyon değeri taşıyor; B5'teki 45 bankalık liste ilk 10'a indirilebilir.</p>
    </div>
  </div>`;
}
function renderTab4(container) {
  const M = yoneticiMetrikleri();
  const npsIsaret = v => (v >= 50 ? NPS_RENK.Promoter : (v >= 0 ? NPS_RENK.Passive : NPS_RENK.Detractor));
  const t = T();
  const fark = M.csi_nps - M.dsi_nps;
  const ids = newIdSet(["cmp", "sorun"]);

  container.innerHTML = `
    <div class="st-info">🎯 Yönetici özeti <b>tüm anketi</b> (${fmtInt(M.toplam)} yanıt) kapsar ve yukarıdaki filtrelerden etkilenmez. Segment detayları için ilgili sekmelere geçin.</div>
    ${baslikHtml("1 · Anket Özeti — Yönetici Bakışı", "2025-2026 CSI & DSI araştırmasının en çarpıcı sonuçları")}
    <div class="kpi-row grid-4">
      ${kpiHtml("Toplam Yanıt", fmtInt(M.toplam), `${M.n_kredi} kredili · ${M.n_nakit} kredisiz · ${M.n_dsi} bayi`, t.vurgu, null)}
      ${kpiHtml("Müşteri NPS (CSI)", fmtSigned(M.csi_nps, 0), "F1 · Net Tavsiye Skoru", npsIsaret(M.csi_nps), (M.csi_nps + 100) / 200)}
      ${kpiHtml("Bayi NPS (DSI)", fmtSigned(M.dsi_nps, 0), "M6 · Net Tavsiye Skoru", npsIsaret(M.dsi_nps), (M.dsi_nps + 100) / 200)}
      ${kpiHtml("Genel Memnuniyet", fmtNum2(M.eo0), "EO0 · 10 üzerinden", t.kpi[0], M.eo0 / 10)}
    </div>
    <div class="callout">
      <div class="callout-b">⚠️ Müşteri bizi tavsiye ediyor (NPS ${fmtSigned(M.csi_nps, 0)}), bizi satan kanal etmiyor (NPS ${fmtSigned(M.dsi_nps, 0)}) — ${fark.toFixed(0)} puanlık makas.</div>
      <div class="callout-s">Bayi danışmanı müşteriyle ilk teması yapan kişidir. CSI tarafındaki güçlü tablo değerli, ancak memnuniyetsiz bir satış kanalı bu tabloyu orta vadede aşındırır. Bu, bir memnuniyet farkı değil stratejik risktir.</div>
    </div>
    <div class="bolum-alt">Öne çıkan dört bulgu</div>
    <div class="bulgu-row">
      ${bulguHtml(M.esik, "Onay süresi kırılma eşiği", "Bu bandı geçen dosyalarda NPS negatife dönüyor", NPS_RENK.Detractor)}
      ${bulguHtml(fmtPct1(M.cagri_t2b, 0), "Çağrı merkezi Top-2-Box", `En zayıf temas noktası · müşterilerin ${fmtPct1(M.e1_aradi, 0)}'i arıyor`, NPS_RENK.Detractor)}
      ${bulguHtml(fmtPct1(M.kasko_teklifsiz, 0), "Kasko teklifi hiç verilmemiş", `Almayan Retail müşteriler içinde · attach ${fmtPct1(M.attach, 0)}`, NPS_RENK.Passive)}
      ${bulguHtml(fmtPct1(M.mobil_farkinda, 0), "Mobil uygulama farkındalığı", `Oysa müşterilerin ${fmtPct1(M.e1_aradi, 0)}'i çağrı merkezini arıyor`, NPS_RENK.Passive)}
    </div>
    <div class="row c2">
      <div id="${ids.cmp}" class="chart-box"></div>
      <div id="${ids.sorun}" class="chart-box"></div>
    </div>
    ${baslikHtml("2 · Aksiyon Planı", "Mevcut verideki bulgulara dayalı, önceliklendirilmiş öneriler")}
    ${aksiyonKartlariHtml(M)}
    ${baslikHtml("3 · Gelecek Yıl Anketi İçin Öneriler", "CEO geri bildirimi + bu yılın bulguları ışığında")}
    <div class="callout">
      <div class="callout-b">🔑 Tek en önemli değişiklik: ankete CRM/sözleşme kimliği bağlanmalı.</div>
      <div class="callout-s">Respondent_ID yerine müşteri/sözleşme numarası eklenirse penetrasyon, gerçek tekrar kullanım, kasko attach ekonomisi, erken kapama ve gecikme — hiç soru sormadan davranışsal olarak bağlanır. CEO'nun "anket para ölçmüyor" itirazının büyük kısmı tek alanla çözülür.</div>
    </div>
    <div class="oneri-grid">
      ${oneriBlok1Html()}
      ${oneriBlok2Html()}
    </div>
    <div class="footer-caption" style="margin-top:.4rem">Not: Yukarıdaki tüm sayılar mevcut sentetik dosyalardan canlı hesaplanır. Yöntem ve okuma biçimi gerçek veride birebir geçerlidir; sayıların kendisi demo niteliğindedir.</div>
  `;
  csiDsiNpsChart(ids.cmp, M);
  sorunOnlemeChart(ids.sorun, M);
}

/* ============================== ANA RENDER DÖNGÜSÜ ============================== */
function renderAll() {
  const rows = {kredi:filtrele(VERI.kredi), nakit:filtrele(VERI.nakit), dsi:filtrele(VERI.dsi)};
  const toplam = rows.kredi.length + rows.nakit.length + rows.dsi.length;
  renderGenelBakis(rows, toplam);
  const uyariEl = document.getElementById("uyari-alani");
  if (toplam === 0) {
    uyariEl.innerHTML = '<div class="st-warning">⚠️ Seçilen filtrelerle hiç yanıt kalmadı. Lütfen filtreleri genişletin.</div>';
    ["1", "2", "3", "4"].forEach(i => document.getElementById("tab-" + i).innerHTML = "");
    document.getElementById("footer-caption").innerHTML = "";
    return;
  }
  uyariEl.innerHTML = "";
  const t1 = document.getElementById("tab-1"); renderTab1(t1, rows.kredi);
  const t2 = document.getElementById("tab-2"); renderTab2(t2, rows.nakit);
  const t3 = document.getElementById("tab-3"); renderTab3(t3, rows.dsi);
  const t4 = document.getElementById("tab-4"); renderTab4(t4);
  document.getElementById("footer-caption").innerHTML =
    `<b>Odysseus Araştırma</b> × <b>Stenos Auto Finansman A.Ş.</b> · CSI &amp; DSI 2025-2026 · ` +
    `Aktif filtrelerle ${fmtInt(toplam)} yanıt görüntüleniyor · Veri: sentetik demo (gerçek saha verisi değildir)`;
  const activePanel = document.querySelector(".tab-panel.active");
  if (activePanel) requestAnimationFrame(() => {
    activePanel.querySelectorAll(".js-plotly-plot").forEach(el => { try { Plotly.Plots.resize(el); } catch (e) {} });
  });
}

function applyTheme() {
  document.documentElement.setAttribute("data-theme", TEMA);
  const btn = document.getElementById("tema-btn");
  btn.textContent = TEMA === "Açık" ? "🌙" : "☀️";
  btn.title = (TEMA === "Açık" ? "Koyu" : "Açık") + " temaya geç";
  renderAll();
}

/* ============================== BAŞLANGIÇ ============================== */
async function init() {
  await veriYukle();
  if (HATALAR.length) {
    document.getElementById("hata-alani").innerHTML =
      `<div class="st-error"><b>Veri dosyaları okunamadı</b><br>${HATALAR.map(h => "- " + escapeHtml(h)).join("<br>")}</div>`;
  }
  const hepsiBos = Object.values(VERI).every(v => v.length === 0);
  document.getElementById("loading-overlay").classList.add("hidden");
  if (hepsiBos) return;

  buildSehirBolge();

  const tumTarihler = Object.values(VERI).flat().map(r => r._tarih).filter(Boolean);
  const minT = new Date(Math.min(...tumTarihler.map(d => d.getTime())));
  const maxT = new Date(Math.max(...tumTarihler.map(d => d.getTime())));
  FILTRE.minT = minT; FILTRE.maxT = maxT; FILTRE.bas = minT; FILTRE.son = maxT;

  const basInput = document.getElementById("f-tarih-bas"), sonInput = document.getElementById("f-tarih-son");
  basInput.min = toInputDate(minT); basInput.max = toInputDate(maxT); basInput.value = toInputDate(minT);
  sonInput.min = toInputDate(minT); sonInput.max = toInputDate(maxT); sonInput.value = toInputDate(maxT);
  basInput.addEventListener("change", () => {
    FILTRE.bas = parseInputDate(basInput.value) || minT;
    if (FILTRE.bas > FILTRE.son) { FILTRE.son = FILTRE.bas; sonInput.value = toInputDate(FILTRE.son); }
    renderAll();
  });
  sonInput.addEventListener("change", () => {
    FILTRE.son = parseInputDate(sonInput.value) || maxT;
    if (FILTRE.son < FILTRE.bas) { FILTRE.bas = FILTRE.son; basInput.value = toInputDate(FILTRE.bas); }
    renderAll();
  });

  function refreshSehirPool() {
    const pool = FILTRE.bolge.length ? TUM_SEHIR.filter(s => FILTRE.bolge.includes(SEHIR_BOLGE[s])) : TUM_SEHIR;
    sehirMs.setOptions(pool);
    FILTRE.sehir = sehirMs.getValue();
  }
  function refreshBayiPool() {
    const set = new Set();
    Object.values(VERI).forEach(rowsArr => rowsArr.forEach(r => {
      if (!r.Acente_Adi) return;
      if (FILTRE.bolge.length && !FILTRE.bolge.includes(r.Bolge)) return;
      if (FILTRE.sehir.length && !FILTRE.sehir.includes(r.Sehir)) return;
      set.add(r.Acente_Adi);
    }));
    const pool = Array.from(set).sort((a, b) => a.localeCompare(b, "tr"));
    bayiMs.setOptions(pool);
    FILTRE.bayi = bayiMs.getValue();
  }

  const bolgeMs = createMultiSelect(document.getElementById("f-bolge-wrap"), {label:"Bölge", onChange:val => { FILTRE.bolge = val; refreshSehirPool(); refreshBayiPool(); renderAll(); }});
  bolgeMs.setOptions(TUM_BOLGE);
  const sehirMs = createMultiSelect(document.getElementById("f-sehir-wrap"), {label:"Şehir", onChange:val => { FILTRE.sehir = val; refreshBayiPool(); renderAll(); }});
  const bayiMs = createMultiSelect(document.getElementById("f-bayi-wrap"), {label:"Bayi / Acente", onChange:val => { FILTRE.bayi = val; renderAll(); }});
  const segmentMs = createMultiSelect(document.getElementById("f-segment-wrap"), {label:"Segment", onChange:val => { FILTRE.segment = val; renderAll(); }});
  segmentMs.setOptions(Object.values(SEGMENT_ADLARI));

  refreshSehirPool();
  refreshBayiPool();

  document.getElementById("tema-btn").addEventListener("click", () => { TEMA = TEMA === "Açık" ? "Koyu" : "Açık"; applyTheme(); });

  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const panel = document.getElementById("tab-" + btn.dataset.tab);
      panel.classList.add("active");
      requestAnimationFrame(() => { panel.querySelectorAll(".js-plotly-plot").forEach(el => { try { Plotly.Plots.resize(el); } catch (e) {} }); });
    });
  });

  window.addEventListener("resize", () => {
    document.querySelectorAll(".tab-panel.active .js-plotly-plot").forEach(el => { try { Plotly.Plots.resize(el); } catch (e) {} });
  });

  applyTheme();
}

document.addEventListener("DOMContentLoaded", init);
