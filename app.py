# -*- coding: utf-8 -*-
"""
===============================================================================
 STENOS AUTO  ×  ODYSSEUS ARAŞTIRMA
 2025-2026 Müşteri & Bayi Memnuniyet Araştırması — İnteraktif Dashboard
===============================================================================
 Çalıştırma:   streamlit run app.py
 Gereksinim:   pip install streamlit pandas numpy plotly
===============================================================================
"""

import os
import inspect
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------------------------------- #
# SÜRÜM UYUMLULUĞU
# Streamlit, tam genişlik parametresini sürümler arasında değiştirdi:
#   eski  -> use_container_width=True
#   yeni  -> width="stretch"
# Yanlış olanı geçmek sessizce yok sayılır (grafik dar kalır), bu yüzden
# kurulu sürümün imzasına bakıp doğru olanı seçiyoruz.
# --------------------------------------------------------------------------- #
def _genislik_kwargs(fn):
    return ({"width": "stretch"} if "width" in inspect.signature(fn).parameters
            else {"use_container_width": True})


_PLOTLY_KW = _genislik_kwargs(st.plotly_chart)
_TABLO_KW = _genislik_kwargs(st.dataframe)


def cizdir(fig):
    """Plotly grafiğini kapsayıcı genişliğinde basar (sürümden bağımsız)."""
    st.plotly_chart(fig, **_PLOTLY_KW)


def tablo(df, yukseklik=300):
    """DataFrame'i tam genişlikte basar (sürümden bağımsız)."""
    st.dataframe(df, height=yukseklik, **_TABLO_KW)

# --------------------------------------------------------------------------- #
# SAYFA KONFİGÜRASYONU
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Stenos Auto | CSI & DSI Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOSYALAR = {
    "kredi":  "Stenos_CSI_KrediKullanan.csv",
    "nakit":  "Stenos_CSI_KrediKullanmayan.csv",
    "dsi":    "Stenos_DSI_BayiCalisanlari.csv",
}

SEGMENT_ADLARI = {
    "kredi": "Kredi Kullanan Müşteri",
    "nakit": "Kredi Kullanmayan Müşteri",
    "dsi":   "Bayi Çalışanı / DSI",
}

# 10'lu skalalarda 99 = "Fikrim Yok / Görüşmedim" -> analizde NaN sayılır
KOD_99_KOLONLARI = {
    "kredi": ["EO1x1_Acente_Satis_Danismani", "EO2x1_Stenos_Satis_Yoneticisi",
              "C1_Satis_Elemani_Yaklasimi", "C1a_Finansman_Kosullari_Bilgilendirme",
              "C2_Finansman_Secenekleri", "C8_Geri_Odeme_Kosullari",
              "C5_Surec_Kolaylik_Hiz", "E5a_Cagri_Merkezi_Memnuniyeti"],
    "nakit": [],
    "dsi":   ["S1_1_Ziyaret_Genel_Memnuniyet", "S1_2_Ziyaret_Sikligi_Memnuniyet"],
}

def saydam(hex_renk, alfa=0.2):
    """
    '#0078D6' -> 'rgba(0,120,214,0.2)'
    Plotly'nin renk doğrulayıcısı 8 haneli hex (#RRGGBBAA) kabul etmez;
    saydamlık her zaman rgba() ile verilmelidir.
    """
    h = hex_renk.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alfa})"


# =========================================================================== #
# TASARIM SETİ — Konecta brandbook
# ---------------------------------------------------------------------------
# Renkler (Konecta blue #2800C8 + Aqua/Solar/Vegetal/Navy/Lagon) ve tipografi
# (Poppins) 20260422 Konecta Brand Architecture Guidelines'tan ölçülmüştür.
# Yalnızca renk/tipografi DİLİ uygulanır; hiçbir marka varlığı (logo, isim)
# kullanılmaz. Koyu tema brandbook'un siyah zeminli "dark background" kuralını
# izler; aksan siyah üzerinde okunmadığı için Lagon'a döner.
# =========================================================================== #
OTOMOTIV_FONT = ('"Helvetica Neue", Helvetica, Arial, '
                 '-apple-system, "Segoe UI", sans-serif')
KLASIK_FONT = ('ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif')
# Poppins sistemde kurulu değilse Google Fonts'tan çekilir; internet yoksa
# fallback yığınına düşer (tasarım bozulmaz, yalnızca font değişir).
KONECTA_FONT = ('"Poppins", "Helvetica Neue", Helvetica, Arial, sans-serif')
KONECTA_FONT_IMPORT = ("@import url('https://fonts.googleapis.com/css2?"
                       "family=Poppins:wght@400;500;600;700&display=swap');")

# --- Konecta marka renkleri (brandbook s.43 + vektör ölçümü) --------------- #
K_BLUE   = "#2800C8"   # Konecta blue — ana marka rengi
K_NAVY   = "#0F0F72"   # Navy blue
K_LAGON  = "#04B4FD"   # Lagon
K_AQUA   = "#09BFAF"   # Aqua
K_VEGET  = "#0DCA61"   # Vegetal
K_SOLAR  = "#FD6221"   # Solar
K_CORAL  = "#FF4533"   # dokümanda kullanılan uyarı/vurgu kırmızısı
# Coral'in koyu tonu. Brandbook'ta ayrı bir kırmızı yok; Solar (#FD6221) ile
# Coral yan yana konduğunda ayırt edilemediği için memnuniyetsizlik bandında
# coral'in bir shade'i kullanılır (marka renginden türetilmiş ton).
K_CORAL_D = "#C0241A"
K_BLACK  = "#111111"
K_GRAY   = "#C7C7C7"

TASARIMLAR = {
    "Konecta": dict(
        etiket="Konecta · brandbook",
        font=KONECTA_FONT,
        font_import=KONECTA_FONT_IMPORT,
        radius="2px",             # brandbook bloklarında keskin dikdörtgenler
        golge="none",
        kart_kalinlik="1px",
        baslik_spacing=".08em",
        gradyan=False,
        akromatik_kpi=False,      # KPI renkleri tema içinde tanımlı
        baslik_vurgulu=True,      # brandbook başlıkları Konecta blue ile yazar
        # Varsayılan (açık tema) kategorik palet: Konecta blue + 5 ikincil renk
        palet=[K_BLUE, K_LAGON, K_AQUA, K_VEGET, K_SOLAR, K_NAVY, K_GRAY],
        nps={"Promoter": K_VEGET, "Passive": K_SOLAR, "Detractor": K_CORAL_D},
        olcek=dict(ana=["#E6E1FA", K_BLUE], ikincil=["#DFF7F5", K_AQUA],
                   vurgu=["#DCF1FF", K_LAGON], negatif=["#FFE3DC", K_CORAL_D],
                   pozitif=["#DDF8E9", K_VEGET]),
        temalar={
            # Açık tema brandbook'un kendi doküman stilidir: beyaz sayfa,
            # Konecta blue başlıklar, açık gri paneller.
            "Açık": dict(template="plotly_white", sayfa="#F4F4F6", kart="#FFFFFF",
                         kenar="#E2E2E8", metin=K_BLACK, soluk="#6B6B7B",
                         zemin="rgba(0,0,0,0)", vurgu=K_BLUE, grid="#EDEDF2",
                         girdi="#FFFFFF",
                         kpi=[K_BLUE, K_NAVY, K_BLACK, K_BLUE, K_BLACK]),
            # Koyu tema: brandbook s.33 "dark backgrounds" örneği SİYAH zemin
            # üzerine beyaz tipografidir (lacivert değil). Siyah üzerinde
            # Konecta blue okunmadığı için aksan Lagon'a döner — aynı sayfanın
            # "switch to white for readability" mantığı.
            "Koyu": dict(template="plotly_dark", sayfa=K_BLACK, kart="#1B1B1B",
                         kenar="#333333", metin="#FFFFFF", soluk="#9A9A9A",
                         zemin="rgba(0,0,0,0)", vurgu=K_LAGON, grid="#2A2A2A",
                         girdi="#1F1F1F",
                         kpi=[K_LAGON, K_AQUA, "#FFFFFF", K_LAGON, "#FFFFFF"],
                         palet=[K_LAGON, K_AQUA, K_VEGET, K_SOLAR,
                                K_GRAY, "#FFFFFF", K_NAVY],
                         olcek=dict(ana=["#14141E", K_LAGON], ikincil=["#0A2A28", K_AQUA],
                                    vurgu=["#14141E", K_LAGON], negatif=["#3A1410", K_CORAL_D],
                                    pozitif=["#0B2A1A", K_VEGET])),
        },
    ),
}

# Sidebar seçiminden sonra doldurulur (tab'lar bu değişkenleri kullanır)
D = TASARIMLAR["Konecta"]
PALET = D["palet"]
NPS_RENK = D["nps"]
KPI_RENK = list(D["palet"])
OLCEK = D["olcek"]


def stil_uygula(T, D):
    """Seçilen tasarım seti (D) + tema (T) için CSS enjekte eder."""
    R = D["radius"]
    # Brandbook bölüm başlıklarını marka rengiyle yazar; diğer tasarımlarda
    # başlık metin rengindedir.
    baslik_renk = T["vurgu"] if D.get("baslik_vurgulu") else T["metin"]
    if D["gradyan"]:
        bant_bg = (f"linear-gradient(135deg, {T['kart']} 0%, {T['kart']} 60%, "
                   f"{saydam(T['vurgu'], .10)} 100%)")
        rozet_bg = "linear-gradient(135deg,#1D4ED8,#0EA5E9)"
        rozet_ody_bg = "linear-gradient(135deg,#0F766E,#14B8A6)"
    else:
        # Otomotiv: düz yüzeyler, gradyan yok
        bant_bg = T["kart"]
        rozet_bg = T["vurgu"]
        rozet_ody_bg = T["metin"] if T["metin"] != "#FFFFFF" else "#333333"
    st.markdown(f"""
    <style>
      {D.get("font_import", "")}
      /* --- Tipografi: seçilen tasarımın font yığını ---------------------- */
      html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
      .stMarkdown, button, input, select, textarea {{
          font-family:{D['font']} !important;
      }}

      /* --- Streamlit arayüzünü seçilen temaya zorla ---------------------- */
      [data-testid="stAppViewContainer"], [data-testid="stHeader"],
      [data-testid="stBottom"] {{ background:{T['sayfa']} !important; }}
      [data-testid="stSidebar"] {{
          background:{T['kart']} !important;
          border-right:1px solid {T['kenar']};
      }}
      [data-testid="stSidebar"] *, [data-testid="stAppViewContainer"] .stMarkdown,
      .stMarkdown p, .stMarkdown li, label, .stRadio label, .stCaption {{
          color:{T['metin']} !important;
      }}
      /* DİKKAT: stToolbar'ın tamamını gizlemeyin — sidebar'ı açan buton onun
         içinde yaşar. Yalnızca Deploy butonu ve ana menü gizlenir. */
      [data-testid="stDecoration"] {{ display:none !important; }}
      [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] {{
          display:none !important;
      }}
      [data-testid="stToolbar"] {{
          display:flex !important; background:transparent !important;
      }}

      /* ------------------------------------------------------------------ *
       * FİLTRE AÇ/KAPA — hamburger buton
       * Streamlit'in sidebar açma kontrolü varsayılanda görünmez; yalnızca
       * fare tam üstüne gelince beliriyor. Burada her iki kontrolü de kalıcı
       * görünür, etiketli birer hamburger butona çeviriyoruz.
       * ------------------------------------------------------------------ */
      button[data-testid="stExpandSidebarButton"] {{
          opacity:1 !important; visibility:visible !important;
          pointer-events:auto !important; transform:none !important;
          display:inline-flex !important; align-items:center;
          justify-content:center;
          width:42px !important; min-width:42px !important; height:42px !important;
          padding:0 !important; margin:.35rem 0 0 .35rem !important;
          background:{T['kart']} !important;
          border:1px solid {T['kenar']} !important;
          border-radius:{R} !important;
          color:{T['metin']} !important;
      }}
      button[data-testid="stExpandSidebarButton"]:hover {{
          border-color:{T['vurgu']} !important;
      }}
      /* Varsayılan ok ikonunu gizle, yerine 3 çizgi çiz.
         DİKKAT: yalnızca ikonu gizlemek yetmez — ikonu saran <span> de flex
         satırında yer kaplar ve çizgileri kutunun soluna iter. Bu yüzden
         butonun TÜM element çocukları gizlenir; ::before bir element
         olmadığı için ayakta kalır ve tek flex öğesi olarak ortalanır. */
      button[data-testid="stExpandSidebarButton"] > *,
      [data-testid="stSidebarCollapseButton"] button > * {{
          display:none !important;
      }}

      button[data-testid="stExpandSidebarButton"]::before,
      [data-testid="stSidebarCollapseButton"] button::before {{
          content:""; flex:0 0 18px; width:18px; height:12px;
          background:
            linear-gradient({T['metin']},{T['metin']}) 0 0/100% 2px no-repeat,
            linear-gradient({T['metin']},{T['metin']}) 0 5px/100% 2px no-repeat,
            linear-gradient({T['metin']},{T['metin']}) 0 10px/100% 2px no-repeat;
      }}
      /* Sidebar açıkken kapatma kontrolü de görünür bir hamburger olsun */
      [data-testid="stSidebarCollapseButton"] {{
          opacity:1 !important; visibility:visible !important;
      }}
      [data-testid="stSidebarCollapseButton"] button {{
          display:inline-flex !important; align-items:center;
          justify-content:center;
          width:38px !important; height:38px !important;
          background:{T['girdi']} !important;
          border:1px solid {T['kenar']} !important;
          border-radius:{R} !important;
      }}
      [data-testid="stSidebarCollapseButton"] button:hover {{
          border-color:{T['vurgu']} !important;
      }}

      /* --- Tema butonu — sağ üst köşede sabit, hamburger ile aynı hizada --- */
      /* z-index, Streamlit toolbar'ının (999990) ÜSTÜNDE olmalı; aksi halde
         toolbar butonu kapatır ve tıklama alınamaz. */
      .st-key-tema_toggle {{
          position:fixed !important; top:.5rem; right:1rem; z-index:1000000;
          width:auto !important; margin:0 !important;
      }}
      .st-key-tema_toggle button {{
          display:inline-flex !important; align-items:center;
          justify-content:center;
          width:42px !important; min-width:42px !important;
          height:42px !important; min-height:42px !important;
          padding:0 !important;
          background:{T['kart']} !important;
          border:1px solid {T['kenar']} !important;
          border-radius:{R} !important;
          font-size:1.15rem !important; line-height:1 !important;
          box-shadow:0 1px 4px rgba(0,0,0,.12);
      }}
      .st-key-tema_toggle button:hover {{
          border-color:{T['vurgu']} !important;
      }}
      .st-key-tema_toggle button p {{ margin:0 !important; }}

      /* --- Filtre barı: geneline göre bir birim küçük font --- */
      .st-key-filtre_bar label p {{ font-size:.78rem !important; }}
      .st-key-filtre_bar [data-baseweb="select"] div,
      .st-key-filtre_bar [data-baseweb="tag"] span,
      .st-key-filtre_bar input {{ font-size:.82rem !important; }}

      /* Girdi alanları (multiselect, date input, expander) */
      [data-baseweb="select"] > div, [data-baseweb="input"] > div,
      .stDateInput input, [data-testid="stExpander"] details {{
          background:{T['girdi']} !important;
          border-color:{T['kenar']} !important;
          color:{T['metin']} !important;
      }}
      [data-baseweb="popover"] div, [role="listbox"] {{
          background:{T['kart']} !important; color:{T['metin']} !important;
      }}
      /* Multiselect etiketlerini kurumsal maviye çek */
      [data-baseweb="tag"] {{
          background:{T['vurgu']} !important; color:#fff !important;
          border-radius:{R} !important;
      }}
      [data-baseweb="tag"] span {{ color:#fff !important; }}

      /* Sekmeler */
      .stTabs [data-baseweb="tab-highlight"] {{ background:{T['vurgu']} !important; }}
      /* Pasif sekmeler varsayılanda fazla soluk kalıyor -> okunur tona çek */
      .stTabs [data-baseweb="tab"] {{ color:{T['soluk']} !important; }}
      .stTabs [aria-selected="true"] {{ color:{T['vurgu']} !important; }}
      .stTabs [data-baseweb="tab-border"] {{ background:{T['kenar']} !important; }}

      /* Tablo & indirme butonu */
      [data-testid="stDataFrame"] {{ border:1px solid {T['kenar']}; border-radius:{R}; }}
      .stDownloadButton button {{
          background:{T['vurgu']} !important; color:#fff !important;
          border:none !important; border-radius:{R} !important; font-weight:600;
          letter-spacing:{D["baslik_spacing"]};
      }}
      hr {{ border-color:{T['kenar']} !important; }}

      /* padding-top: hamburger butonu içerikle çakışmasın diye pay bırakılır */
      .block-container {{ padding-top: 2.3rem; padding-bottom: 2rem; max-width: 1500px; }}

      /* --- Üst marka bandı --- */
      .marka-bant {{
          display:flex; align-items:center; justify-content:space-between;
          gap:1rem; padding:1.1rem 1.5rem; margin-bottom:1.3rem;
          border:1px solid {T['kenar']}; border-radius:{R};
          background:{bant_bg};
      }}
      .marka-sol {{ display:flex; align-items:center; gap:.9rem; }}
      .logo-rozet {{
          width:46px; height:46px; border-radius:{R}; flex:0 0 46px;
          display:flex; align-items:center; justify-content:center;
          font-weight:800; font-size:1.15rem; letter-spacing:-.5px; color:#fff;
          background:{rozet_bg};
      }}
      .logo-rozet.ody {{ background:{rozet_ody_bg}; }}
      .marka-ad {{ font-size:1.32rem; font-weight:750; color:{T['metin']};
                   line-height:1.15; letter-spacing:-.3px; }}
      .marka-alt {{ font-size:.82rem; color:{T['soluk']}; margin-top:.15rem; }}
      .marka-sag {{ display:flex; align-items:center; gap:.75rem; }}
      .ody-kutu {{ text-align:right; }}
      .ody-ad {{ font-size:.95rem; font-weight:700; color:{T['metin']}; }}
      .ody-alt {{ font-size:.74rem; color:{T['soluk']}; }}

      /* --- KPI kartları --- */
      .kpi {{
          border:{D['kart_kalinlik']} solid {T['kenar']}; border-radius:{R};
          padding:1rem 1.15rem; background:{T['kart']}; height:100%;
          box-shadow:{D['golge']};
      }}
      /* min-height: iki satıra taşan başlıklarda kartların hizası bozulmasın */
      .kpi-t {{ font-size:.76rem; font-weight:650;
                text-transform:uppercase; color:{T['soluk']}; margin-bottom:.45rem;
                letter-spacing:{D['baslik_spacing']};
                min-height:2.3em; line-height:1.15; }}
      .kpi-v {{ font-size:2.0rem; font-weight:780; line-height:1.05;
                color:{T['metin']}; letter-spacing:-1px; }}
      .kpi-s {{ font-size:.78rem; color:{T['soluk']}; margin-top:.35rem;
                min-height:2.2em; line-height:1.25; }}
      .kpi-bar {{ height:4px; border-radius:3px; margin-top:.7rem;
                  background:{T['kenar']}; overflow:hidden; }}
      .kpi-bar > div {{ height:100%; border-radius:3px; }}

      /* --- Yönetici özeti bileşenleri --- */
      .callout {{
          border:1px solid {T['kenar']}; border-left:5px solid {T['vurgu']};
          border-radius:{R}; background:{T['kart']};
          padding:1.1rem 1.35rem; margin:.4rem 0 1rem 0;
      }}
      .callout-b {{ font-size:1.18rem; font-weight:750; color:{T['metin']};
                    line-height:1.3; letter-spacing:-.2px; }}
      .callout-s {{ font-size:.9rem; color:{T['soluk']}; margin-top:.4rem;
                    line-height:1.45; }}
      .bulgu {{
          border:1px solid {T['kenar']}; border-radius:{R}; background:{T['kart']};
          padding:.9rem 1rem; height:100%;
      }}
      .bulgu-v {{ font-size:1.6rem; font-weight:780; line-height:1;
                  letter-spacing:-.5px; }}
      .bulgu-t {{ font-size:.82rem; color:{T['metin']}; margin-top:.4rem;
                  font-weight:600; line-height:1.3; }}
      .bulgu-s {{ font-size:.74rem; color:{T['soluk']}; margin-top:.25rem;
                  line-height:1.35; }}
      .aksiyon {{
          display:flex; gap:.95rem; align-items:flex-start;
          border:1px solid {T['kenar']}; border-radius:{R}; background:{T['kart']};
          padding:1rem 1.2rem; margin-bottom:.7rem;
      }}
      .aksiyon-no {{ flex:0 0 34px; width:34px; height:34px; border-radius:{R};
                     display:flex; align-items:center; justify-content:center;
                     font-weight:800; font-size:1.05rem; color:#fff; margin-top:2px; }}
      .aksiyon-govde {{ flex:1; }}
      .aksiyon-baslik {{ font-size:1rem; font-weight:750; color:{T['metin']};
                         margin-bottom:.15rem; }}
      .aksiyon-bulgu {{ font-size:.86rem; color:{T['metin']}; line-height:1.5;
                        margin:.35rem 0; }}
      .aksiyon-bulgu b {{ color:{T['vurgu']}; }}
      .aksiyon-aksiyon {{ font-size:.86rem; color:{T['soluk']}; line-height:1.5; }}
      .chip {{ display:inline-block; font-size:.68rem; font-weight:700;
               letter-spacing:.03em; padding:.16rem .5rem; border-radius:{R};
               margin-left:.4rem; vertical-align:middle; }}
      .oneri-kutu {{ border:1px solid {T['kenar']}; border-radius:{R};
                     background:{T['kart']}; padding:1rem 1.2rem;
                     margin-bottom:.7rem; }}
      .oneri-kutu h4 {{ font-size:.95rem; font-weight:750; color:{T['metin']};
                        margin:0 0 .4rem 0; }}
      .oneri-kutu p, .oneri-kutu li {{ font-size:.86rem; color:{T['metin']};
                        line-height:1.55; }}
      .oneri-kutu .neden {{ color:{T['soluk']}; }}

      /* --- Bölüm başlıkları --- */
      .bolum {{ font-size:1.02rem; font-weight:700; color:{baslik_renk};
                margin:1.5rem 0 .2rem 0; padding-left:.6rem;
                border-left:3px solid {T['vurgu']}; }}
      .bolum-alt {{ font-size:.8rem; color:{T['soluk']};
                    margin:0 0 .8rem .65rem; }}

      .stTabs [data-baseweb="tab-list"] {{ gap:.35rem; }}
      .stTabs [data-baseweb="tab"] {{
          height:44px; padding:0 1.1rem; border-radius:{R} {R} 0 0;
          font-weight:600; font-size:.92rem;
      }}
      div[data-testid="stMetricValue"] {{ font-size:1.6rem; }}
      footer, #MainMenu {{ visibility:hidden; }}
    </style>
    """, unsafe_allow_html=True)


def grafik_duzen(fig, T, yukseklik=380, legend_alt=True, legend_satir=1):
    """
    Tüm grafiklere ortak kurumsal düzen uygular.
    legend_satir: legend kaç satıra sarıyorsa o kadar üst boşluk açılır —
    aksi halde çok öğeli legend başlığın üstüne biner.
    """
    ust_bosluk = (58 + 24 * legend_satir) if legend_alt else 58
    fig.update_layout(
        template=T["template"],
        height=yukseklik,
        margin=dict(l=10, r=10, t=ust_bosluk, b=10),
        paper_bgcolor=T["zemin"],
        plot_bgcolor=T["zemin"],
        font=dict(family=T.get("font", KLASIK_FONT), size=12, color=T["metin"]),
        hoverlabel=dict(font_size=12),
    )
    # Başlık stilini yalnızca gerçekten bir başlık metni varsa uygula —
    # aksi halde Plotly boş title nesnesini "undefined" olarak basar.
    if fig.layout.title.text:
        fig.update_layout(title=dict(font=dict(size=14.5, color=T["metin"]),
                                     x=0, xanchor="left", y=0.97, yanchor="top"))
    if legend_alt:
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.015,
                                      xanchor="left", x=0, title_text="",
                                      font=dict(size=11)))
    fig.update_xaxes(gridcolor=T["grid"], zeroline=False)
    fig.update_yaxes(gridcolor=T["grid"], zeroline=False)
    return fig


# --------------------------------------------------------------------------- #
# VERİ YÜKLEME  (try-except + cache)
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner="Anket verileri yükleniyor...")
def veri_yukle():
    """
    3 CSV'yi okur, tip dönüşümlerini ve 99 kodu temizliğini yapar.
    Dönüş: (veri_sozlugu, hata_listesi)
    """
    veri, hatalar = {}, []

    for anahtar, dosya_adi in DOSYALAR.items():
        yol = os.path.join(BASE_DIR, dosya_adi)
        try:
            if not os.path.exists(yol):
                raise FileNotFoundError(f"'{dosya_adi}' bulunamadı.")

            df = pd.read_csv(yol, encoding="utf-8-sig")
            if df.empty:
                raise ValueError(f"'{dosya_adi}' boş.")

            # Tarih
            if "Anket_Tarihi" in df.columns:
                df["Anket_Tarihi"] = pd.to_datetime(df["Anket_Tarihi"], errors="coerce")
                df = df.dropna(subset=["Anket_Tarihi"])
                df["Yil_Ay"] = df["Anket_Tarihi"].dt.to_period("M").astype(str)
                df["Ceyrek"] = df["Anket_Tarihi"].dt.to_period("Q").astype(str)

            # 99 = "Fikrim Yok" -> NaN
            for kol in KOD_99_KOLONLARI.get(anahtar, []):
                if kol in df.columns:
                    df[kol] = pd.to_numeric(df[kol], errors="coerce").replace(99, np.nan)

            # Segment garantisi
            if "Segment" not in df.columns:
                df["Segment"] = SEGMENT_ADLARI[anahtar]

            veri[anahtar] = df

        except Exception as e:
            hatalar.append(f"**{dosya_adi}** → {type(e).__name__}: {e}")
            veri[anahtar] = pd.DataFrame()

    return veri, hatalar


def guvenli_ort(seri):
    """NaN'a dayanıklı ortalama."""
    s = pd.to_numeric(seri, errors="coerce").dropna()
    return float(s.mean()) if len(s) else np.nan


def nps_hesapla(seri):
    """0-10 tavsiye skorundan NPS = %Promoter - %Detractor."""
    s = pd.to_numeric(seri, errors="coerce").dropna()
    if not len(s):
        return np.nan, 0, 0, 0
    p = (s >= 9).mean() * 100
    pa = ((s >= 7) & (s <= 8)).mean() * 100
    d = (s <= 6).mean() * 100
    return p - d, p, pa, d


def coklu_ac(seri, ayirac="; "):
    """'A; B; C' formatındaki çoklu seçim kolonunu tekil yanıtlara açar."""
    s = seri.dropna().astype(str)
    if not len(s):
        return pd.Series(dtype=str)
    return s.str.split(ayirac).explode().str.strip()


def kpi(sutun, baslik, deger, alt="", renk=None, oran=None, T=None):
    """Özel HTML KPI kartı."""
    renk = renk or T["metin"]
    bar = ""
    if oran is not None and not pd.isna(oran):
        genislik = float(np.clip(oran, 0, 1)) * 100
        bar = (f'<div class="kpi-bar"><div style="width:{genislik:.1f}%;'
               f'background:{renk}"></div></div>')
    sutun.markdown(
        f'<div class="kpi"><div class="kpi-t">{baslik}</div>'
        f'<div class="kpi-v" style="color:{renk}">{deger}</div>'
        f'<div class="kpi-s">{alt}</div>{bar}</div>',
        unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# MARKA METRİKLERİ (10'lu skala halka göstergesi)
# --------------------------------------------------------------------------- #
# CSI ve DSI formlarındaki dört ana marka metriği aynı 10'lu skalada ölçülür.
# Her biri, doluluğu ortalamayı gösteren bir halka (donut) ile sunulur.
MARKA_METRIKLERI_CSI = [
    ("EO0_Genel_Memnuniyet",   "Genel Memnuniyet",  "EO0 · Overall Satisfaction", 1),
    ("F1_Recommendation_NPS",  "Tavsiye Etme",      "F1 · Recommendation",        0),
    ("F1x_Brand_Importance",   "Marka Önemi",       "F1x · Brand Importance",     1),
    ("S44_Brand_Retention",    "Tekrar Tercih",     "S44 · Brand Retention",      1),
]
MARKA_METRIKLERI_DSI = [
    ("M4a_Genel_Memnuniyet_Finans", "Genel Memnuniyet", "M4a · Overall Satisfaction", 1),
    ("M6_Recommendation_NPS",       "Tavsiye Etme",     "M6 · Recommendation",        0),
    ("M6x_Brand_Importance",        "Marka Önemi",      "M6x · Brand Importance",     1),
    ("M3_Brand_Retention",          "Tekrar Tercih",    "M3 · Brand Retention",       1),
]


def marka_halkasi(deger, baslik_metni, altbaslik, T, renk, n):
    """
    10'lu skalada tek bir metriği halka (donut) göstergesi olarak çizer.
    Halkanın dolu kısmı ortalamayı, boş kısmı 10'a kalan mesafeyi temsil eder.
    """
    deger = 0.0 if pd.isna(deger) else float(deger)
    fig = go.Figure(go.Pie(
        values=[deger, max(10 - deger, 0)],
        hole=0.74, sort=False, direction="clockwise", rotation=0,
        marker=dict(colors=[renk, saydam(T["soluk"], .22)],
                    line=dict(color=T["kart"], width=0)),
        textinfo="none",
        hovertemplate=f"{baslik_metni}: {deger:.2f} / 10<extra></extra>",
        showlegend=False,
    ))
    fig.add_annotation(text=f"<b>{deger:.2f}</b>", showarrow=False,
                       font=dict(size=30, color=T["metin"]), y=0.54)
    fig.add_annotation(text="10 üzerinden", showarrow=False,
                       font=dict(size=10.5, color=T["soluk"]), y=0.28)
    # Başlık figüre KONMAZ; metrik adı halkanın üstünde Streamlit başlığı olarak
    # basılır (bkz. marka_metrik_bloku). İki satırlık Plotly başlığı figürün üst
    # kenarına çok yakın konumlanıp Türkçe büyük harfleri (Ö, İ) kırpıyordu.
    fig = grafik_duzen(fig, T, 210, legend_alt=False)
    fig.update_layout(margin=dict(l=6, r=6, t=6, b=6))
    return fig


def marka_metrik_bloku(df, metrikler, T, baslik_metni, altyazi):
    """Dört marka metriğini halka göstergeleri + dağılım kırılımı olarak basar."""
    baslik(baslik_metni, altyazi)

    mevcut = [(k, ad, alt, tab) for k, ad, alt, tab in metrikler if k in df.columns]
    if not mevcut:
        bos_uyari("Bu segmentte marka metrikleri bulunmuyor.")
        return

    # --- Halka göstergeler ---
    sutunlar = st.columns(len(mevcut))
    renkler = [T["vurgu"], NPS_RENK["Promoter"], PALET[1], T["vurgu"]]
    dagilim = []
    for i, (kolon, ad, alt, taban) in enumerate(mevcut):
        s = pd.to_numeric(df[kolon], errors="coerce").replace(99, np.nan).dropna()
        with sutunlar[i]:
            # Başlık, grafiğin ÜSTÜNDE — Plotly başlığı Türkçe büyük harfleri
            # kırptığı için metrik adını HTML olarak basıyoruz.
            st.markdown(
                f'<div style="text-align:center;line-height:1.25;'
                f'min-height:2.6em;margin-bottom:.2rem">'
                f'<div style="font-weight:750;font-size:.95rem;'
                f'color:{T["metin"]}">{ad}</div>'
                f'<div style="font-size:.72rem;color:{T["soluk"]}">'
                f'{alt} · n={len(s)}</div></div>', unsafe_allow_html=True)
            cizdir(marka_halkasi(s.mean() if len(s) else np.nan, ad, alt, T,
                                 renkler[i % len(renkler)], len(s)))
        if len(s):
            # Bant adları TÜM metriklerde aynı olmalı: F1'in tabanı 0, diğerleri 1
            # olduğu için ada taban yazılırsa ayrı bir kategori doğar ve yığılmış
            # barda hem renkler hem sıralama kayar.
            dagilim.append({
                "Metrik": ad,
                "Yüksek (9-10)": (s >= 9).mean() * 100,
                "Orta (7-8)": ((s >= 7) & (s <= 8)).mean() * 100,
                "Düşük (≤6)": (s <= 6).mean() * 100,
            })

    if not dagilim:
        return

    # --- Dağılım kırılımı: her metriğin yüksek/orta/düşük payı ---
    dd = pd.DataFrame(dagilim)
    bant_kolonlari = [c for c in dd.columns if c != "Metrik"]
    uzun = dd.melt(id_vars="Metrik", value_vars=bant_kolonlari,
                   var_name="Bant", value_name="Pay")
    fig = px.bar(uzun, x="Pay", y="Metrik", color="Bant", orientation="h",
                 text="Pay", color_discrete_sequence=[
                     NPS_RENK["Promoter"], NPS_RENK["Passive"], NPS_RENK["Detractor"]],
                 title="Metrik Bazında Puan Dağılımı (%)")
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="inside",
                      insidetextanchor="middle")
    fig.update_xaxes(title="Yanıt payı (%)", range=[0, 100], ticksuffix="%")
    fig.update_yaxes(title="", categoryorder="array",
                     categoryarray=list(dd["Metrik"])[::-1])
    fig.update_layout(barmode="stack")
    cizdir(grafik_duzen(fig, T, 300))


def baslik(metin, altyazi=""):
    st.markdown(f'<div class="bolum">{metin}</div>', unsafe_allow_html=True)
    if altyazi:
        st.markdown(f'<div class="bolum-alt">{altyazi}</div>', unsafe_allow_html=True)


def bos_uyari(baslik_metni="Seçilen filtrelerle bu segmentte yanıt bulunmuyor."):
    st.info(f"ℹ️  {baslik_metni}  Soldaki filtreleri genişletmeyi deneyin.")


# --------------------------------------------------------------------------- #
# HAM VERİ BÖLÜMÜ
# --------------------------------------------------------------------------- #
# Tabloya ve indirmeye beslenen veri sidebar filtrelerinden GEÇMİŞ olandır.
# Aşağıdaki yardımcılar bunu görünür kılar: satır sayısı başlıkta, aktif
# filtreler listede, seçim de indirilen dosyanın adında yer alır.
_TR_HARF = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


def _slug(metin, uzunluk=28):
    t = metin.translate(_TR_HARF)
    t = "".join(ch if ch.isalnum() else "_" for ch in t)
    while "__" in t:
        t = t.replace("__", "_")
    return t.strip("_")[:uzunluk]


def aktif_filtreler():
    """Sidebar'da seçili filtreleri okunur bir listeye çevirir."""
    p = [f"Tarih: {bas_t:%d.%m.%Y} – {son_t:%d.%m.%Y}"]
    if sec_sehir:
        p.append("Şehir: " + ", ".join(sec_sehir))
    if sec_bolge:
        p.append("Bölge: " + ", ".join(sec_bolge))
    if sec_bayi:
        p.append("Bayi: " + ", ".join(sec_bayi))
    if sec_segment and len(sec_segment) < len(SEGMENT_ADLARI):
        p.append("Segment: " + ", ".join(sec_segment))
    return p


def dosya_adi_eki():
    """Filtrelere göre dosya adı eki — farklı filtrelerle inen CSV'ler karışmasın."""
    parcalar = [f"{bas_t:%Y%m%d}-{son_t:%Y%m%d}"]
    if sec_sehir:
        parcalar.append("sehir-" + _slug("-".join(sec_sehir)))
    if sec_bolge:
        parcalar.append("bolge-" + _slug("-".join(b.replace(" Bölgesi", "")
                                                  for b in sec_bolge)))
    if sec_bayi:
        parcalar.append(f"bayi-{len(sec_bayi)}adet" if len(sec_bayi) > 1
                        else "bayi-" + _slug(sec_bayi[0]))
    return "_".join(parcalar)


def ham_veri_bolumu(df, tam_df, dosya_koku, anahtar):
    """Filtrelenmiş ham veriyi gösterir ve indirtir."""
    n, N = len(df), len(tam_df)
    nokta = lambda x: f"{x:,}".replace(",", ".")
    with st.expander(f"🔎  Ham veriyi görüntüle / indir "
                     f"— {nokta(n)} / {nokta(N)} satır (filtre uygulanmış)"):
        st.caption("Aktif filtreler → " + "  ·  ".join(aktif_filtreler()))
        if n < N:
            st.caption(f"Toplam {nokta(N)} kayıttan {nokta(N - n)} tanesi "
                       f"filtre dışında kaldı.")
        tablo(df, 300)
        st.download_button(
            f"⬇️  Filtrelenmiş CSV'yi indir ({nokta(n)} satır)",
            df.to_csv(index=False).encode("utf-8-sig"),
            f"{dosya_koku}_{dosya_adi_eki()}.csv", "text/csv", key=anahtar)


# --------------------------------------------------------------------------- #
# VERİYİ YÜKLE
# --------------------------------------------------------------------------- #
VERI, HATALAR = veri_yukle()

if HATALAR:
    st.error("### Veri dosyaları okunamadı\n\n" + "\n\n".join(f"- {h}" for h in HATALAR))
    st.caption(f"Beklenen konum: `{BASE_DIR}`")
    st.caption("CSV'leri üretmek için: `python3 stenos_sentetik_veri_uretici.py`")
    if all(d.empty for d in VERI.values()):
        st.stop()

# --- Şehir ↔ Bölge eşlemesi (Bölge→Şehir kademeli filtresi için) ----------- #
# Her şehir tek bir bölgeye aittir; eşlemeyi veriden türetiyoruz.
_sb = pd.concat(
    [d[["Sehir", "Bolge"]] for d in VERI.values()
     if not d.empty and {"Sehir", "Bolge"} <= set(d.columns)],
    ignore_index=True).dropna().drop_duplicates("Sehir")
SEHIR_BOLGE = dict(zip(_sb["Sehir"], _sb["Bolge"]))
TUM_SEHIR = sorted(SEHIR_BOLGE)
TUM_BOLGE = sorted(set(SEHIR_BOLGE.values()))

# --------------------------------------------------------------------------- #
# TASARIM & TEMA
# Tek tasarım (Konecta) vardır; tema (Açık/Koyu) ana sayfadaki butonla
# değiştirilir ve session_state'te tutulur. Renk globalleri stil ve tüm
# sekmelerden ÖNCE hesaplanır ki doğru temayla render olsun.
# --------------------------------------------------------------------------- #
if "tema" not in st.session_state:
    st.session_state.tema = "Açık"

D = TASARIMLAR["Konecta"]
T = dict(D["temalar"][st.session_state.tema])
T["font"] = D["font"]
PALET = T.get("palet") or D["palet"]
NPS_RENK = D["nps"]
OLCEK = T.get("olcek") or D["olcek"]
# KPI kart renkleri paletten AYRIDIR: kategorik palette yer alan koyu tonlar
# koyu kart üzerinde okunmaz; Konecta bunları temaya özel tanımlar.
KPI_RENK = T.get("kpi") or (
    [T["vurgu"], T["vurgu"], T["metin"], T["vurgu"], T["metin"]]
    if D["akromatik_kpi"] else list(PALET))

stil_uygula(T, D)

# --------------------------------------------------------------------------- #
# TEMA BUTONU — ana sayfa sağ üst, hamburger filtre butonuyla aynı hizada
# (CSS ile position:fixed olarak sağ üste sabitlenir; bkz. stil_uygula)
# --------------------------------------------------------------------------- #
_hedef_tema = "Koyu" if st.session_state.tema == "Açık" else "Açık"
_tema_ikon = "🌙" if st.session_state.tema == "Açık" else "☀️"
if st.button(_tema_ikon, key="tema_toggle",
             help=f"{_hedef_tema} temaya geç"):
    st.session_state.tema = _hedef_tema
    st.rerun()


# --------------------------------------------------------------------------- #
# ÜST MARKA BANDI
# --------------------------------------------------------------------------- #
st.markdown(f"""
<div class="marka-bant">
  <div class="marka-sol">
    <div class="logo-rozet">SA</div>
    <div>
      <div class="marka-ad">Stenos Auto Finansman A.Ş.</div>
      <div class="marka-alt">Müşteri &amp; Bayi Memnuniyet Araştırması · CSI &amp; DSI 2025-2026</div>
    </div>
  </div>
  <div class="marka-sag">
    <div class="ody-kutu">
      <div class="ody-ad">Odysseus Araştırma</div>
      <div class="ody-alt">Pazar Araştırma &amp; Analitik</div>
    </div>
    <div class="logo-rozet ody">OD</div>
  </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# ÜST FİLTRE BARI  (eski sol sidebar; yatay bara taşındı)
# Bölge → Şehir → Bayi kademeli daralır: bir üst seviye seçilince alt seviyenin
# seçenekleri o kapsamla sınırlanır ve geçersiz kalan seçimler otomatik budanır.
# --------------------------------------------------------------------------- #
tum_tarihler = pd.concat(
    [d["Anket_Tarihi"] for d in VERI.values()
     if not d.empty and "Anket_Tarihi" in d])
min_t, max_t = tum_tarihler.min().date(), tum_tarihler.max().date()


def _buda(anahtar, gecerli_secenekler):
    """Bir üst filtre değişince geçersiz kalan seçimleri state'ten çıkarır."""
    mevcut = st.session_state.get(anahtar, [])
    kalan = [x for x in mevcut if x in gecerli_secenekler]
    if kalan != mevcut:
        st.session_state[anahtar] = kalan


with st.container(border=True, key="filtre_bar"):
    fb = st.columns([1.6, 1.15, 1.15, 1.3, 1.35])

    with fb[0]:
        tarih_secim = st.date_input(
            "Tarih Aralığı", value=(min_t, max_t),
            min_value=min_t, max_value=max_t, format="DD.MM.YYYY",
            key="f_tarih")
        if isinstance(tarih_secim, (list, tuple)) and len(tarih_secim) == 2:
            bas_t, son_t = tarih_secim
        else:  # kullanıcı aralığın ilk tarihini seçtiyse (ara durum)
            bas_t = son_t = (tarih_secim[0] if isinstance(tarih_secim, (list, tuple))
                             else tarih_secim)

    with fb[1]:
        sec_bolge = st.multiselect("Bölge", TUM_BOLGE, key="f_bolge",
                                   placeholder="Tümü")

    with fb[2]:
        # Şehir seçenekleri seçili bölge(ler)e göre daralır
        sehir_havuz = ([c for c in TUM_SEHIR if SEHIR_BOLGE.get(c) in sec_bolge]
                       if sec_bolge else TUM_SEHIR)
        _buda("f_sehir", sehir_havuz)
        sec_sehir = st.multiselect("Şehir", sehir_havuz, key="f_sehir",
                                   placeholder="Tümü")

    with fb[3]:
        # Bayi seçenekleri bölge + şehir seçimine göre daralır
        bayi_havuz = set()
        for d in VERI.values():
            if d.empty or "Acente_Adi" not in d.columns:
                continue
            alt = d
            if sec_bolge and "Bolge" in alt.columns:
                alt = alt[alt["Bolge"].isin(sec_bolge)]
            if sec_sehir and "Sehir" in alt.columns:
                alt = alt[alt["Sehir"].isin(sec_sehir)]
            bayi_havuz |= set(alt["Acente_Adi"].dropna().unique())
        bayi_havuz = sorted(bayi_havuz)
        _buda("f_bayi", bayi_havuz)
        sec_bayi = st.multiselect("Bayi / Acente", bayi_havuz, key="f_bayi",
                                  placeholder="Tümü")

    with fb[4]:
        # Diğer filtreler gibi: boş = tümü. Baştan seçili chip göstermez,
        # "Tümü" placeholder'lı kapalı bir açılır menü olarak durur.
        sec_segment = st.multiselect(
            "Segment", list(SEGMENT_ADLARI.values()),
            key="f_segment", placeholder="Tümü")


# --------------------------------------------------------------------------- #
# FİLTRE UYGULAMA
# --------------------------------------------------------------------------- #
def filtrele(df):
    if df.empty:
        return df
    m = pd.Series(True, index=df.index)
    if "Anket_Tarihi" in df.columns:
        m &= df["Anket_Tarihi"].dt.date.between(bas_t, son_t)
    if sec_sehir and "Sehir" in df.columns:
        m &= df["Sehir"].isin(sec_sehir)
    if sec_bolge and "Bolge" in df.columns:
        m &= df["Bolge"].isin(sec_bolge)
    if sec_bayi and "Acente_Adi" in df.columns:
        m &= df["Acente_Adi"].isin(sec_bayi)
    if sec_segment and "Segment" in df.columns:
        m &= df["Segment"].isin(sec_segment)
    return df[m]


F = {k: filtrele(v) for k, v in VERI.items()}
df_kredi, df_nakit, df_dsi = F["kredi"], F["nakit"], F["dsi"]
toplam_n = sum(len(d) for d in F.values())

# --- Genel bakış şeridi ---
g1, g2, g3, g4 = st.columns(4)
kpi(g1, "Toplam Yanıt", f"{toplam_n:,}".replace(",", "."),
    f"{len(VERI['kredi']) + len(VERI['nakit']) + len(VERI['dsi']):,} kayıt içinden"
    .replace(",", "."), T["vurgu"], T=T)
kpi(g2, "Kredi Kullanan (CSI)", f"{len(df_kredi):,}".replace(",", "."),
    "Müşteri anketi", KPI_RENK[0], T=T)
kpi(g3, "Kredi Kullanmayan (CSI)", f"{len(df_nakit):,}".replace(",", "."),
    "Müşteri anketi", KPI_RENK[2], T=T)
kpi(g4, "Bayi Çalışanı (DSI)", f"{len(df_dsi):,}".replace(",", "."),
    "Acente anketi", KPI_RENK[3], T=T)

if toplam_n == 0:
    st.warning("Seçilen filtrelerle hiç yanıt kalmadı. Lütfen filtreleri genişletin.")
    st.stop()

st.write("")

# --------------------------------------------------------------------------- #
# YÖNETİCİ ÖZETİ — metrik hesaplama
# --------------------------------------------------------------------------- #
# NOT: Yönetici özeti TÜM anketi (900 yanıt) kapsar ve soldaki filtrelerden
# ETKİLENMEZ. Bir CEO özeti, biri şehir filtreledi diye değişmemelidir; ayrıca
# aksiyon planındaki alt kırılımlar (kasko hunisi, sorun çözümü) filtrelenince
# örneklem çok küçülür. Tüm sayılar VERI (ham, filtrelenmemiş) üzerinden gelir.
def _num99(seri):
    return pd.to_numeric(seri, errors="coerce").replace(99, np.nan)


def _nps(seri):
    return nps_hesapla(seri)[0]


@st.cache_data(show_spinner=False)
def yonetici_metrikleri():
    k, n, d = VERI["kredi"], VERI["nakit"], VERI["dsi"]
    M = {"n_kredi": len(k), "n_nakit": len(n), "n_dsi": len(d),
         "toplam": len(k) + len(n) + len(d)}

    M["csi_nps"] = _nps(k["F1_Recommendation_NPS"])
    M["dsi_nps"] = _nps(d["M6_Recommendation_NPS"])
    M["eo0"] = guvenli_ort(k["EO0_Genel_Memnuniyet"])

    # Çağrı merkezi — en zayıf CSI süreç metriği
    cm = _num99(k["E5a_Cagri_Merkezi_Memnuniyeti"])
    M["cagri_ort"] = cm.mean()
    M["cagri_t2b"] = (cm >= 9).mean() * 100
    M["e1_aradi"] = (k["E1_Musteri_Hizmetleri_Aradi_mi"] == 1).mean() * 100
    M["e1_ulasamadi"] = (k["E1_Musteri_Hizmetleri_Aradi_mi"] == 3).mean() * 100

    # Onay süresi eşiği — NPS'in negatife döndüğü ilk bant
    sc = k.dropna(subset=["Kredi_Onay_Suresi_Saat", "F1_Recommendation_NPS"]).copy()
    sc["b"] = pd.cut(sc["Kredi_Onay_Suresi_Saat"], [0, 4, 8, 12, 24, 48, 1e4],
                     labels=["0-4 sa", "4-8 sa", "8-12 sa", "12-24 sa",
                             "24-48 sa", "48+ sa"])
    bnps = sc.groupby("b", observed=True)["F1_Recommendation_NPS"].apply(_nps)
    neg = bnps[bnps <= 0]
    M["esik"] = str(neg.index[0]) if len(neg) else "—"

    # Kasko hunisi (Retail)
    r = k[k["Filo_Retail"] == "Retail"]
    M["attach"] = (r["K1_1_Kasko_Satin_Aldi_mi"] == 1).mean() * 100
    nb = r[r["K1_1_Kasko_Satin_Aldi_mi"] == 2]
    M["kasko_teklifsiz"] = ((nb["K1_2_Kasko_Teklifi_Verildi_mi"] == 2).mean() * 100
                            if len(nb) else np.nan)
    tv = nb[nb["K1_2_Kasko_Teklifi_Verildi_mi"] == 1]
    M["kasko_avantajsiz"] = ((tv["K8_Avantajlardan_Bahsedildi_mi"] == 2).mean() * 100
                             if len(tv) else np.nan)

    # Sorun yaşama & çözüm
    M["sorun_oran"] = (k["I1_Sorun_Yasadi_mi"] == 1).mean() * 100
    M["nps_sorunsuz"] = _nps(k[k["I1_Sorun_Yasadi_mi"] == 2]["F1_Recommendation_NPS"])
    s = k[k["I1_Sorun_Yasadi_mi"] == 1]
    M["nps_cozuldu"] = _nps(s[s["I2_Sorun_Giderildi_mi"] == 1]["F1_Recommendation_NPS"])
    M["cozum_oran"] = ((s["I2_Sorun_Giderildi_mi"] == 1).mean() * 100
                       if len(s) else np.nan)

    # Dijital
    M["mobil_farkinda"] = (k["N3_Mobil_App_Bilinirlik"] == 1).mean() * 100
    M["danisman_onermiyor"] = (d["S7_Mobil_App_Oneriyor_mu"] == 2).mean() * 100

    # Kredi kullanmayan — geri kazanım eğilimi
    gk = (n.assign(y=(n["S11_Yuksek_Egilim"] == 1))
          .groupby("S3_Tercih_Etmeme_Nedeni")["y"].mean().mul(100)
          .sort_values(ascending=False))
    M["gk"] = gk

    # DSI en zayıf metrik
    dm = {"S1_2_Ziyaret_Sikligi_Memnuniyet": "Ziyaret sıklığı",
          "S3b_1_CRM_Sistem_Hizi": "CRM sistem hızı",
          "CRM_Memnuniyeti_Birlesik": "CRM genel memnuniyeti",
          "S5c_Egitim_Memnuniyeti": "C-Sales eğitimleri",
          "M4a_Genel_Memnuniyet_Finans": "Genel memnuniyet"}
    dv = {v: guvenli_ort(_num99(d[c])) for c, v in dm.items() if c in d.columns}
    M["dsi_min"] = min(dv, key=dv.get)
    M["dsi_min_val"] = dv[M["dsi_min"]]

    # Bölge uçları
    gb = (k.groupby("Bolge")
          .agg(nps=("F1_Recommendation_NPS", _nps),
               onay=("Kredi_Onay_Suresi_Saat", "mean")).sort_values("nps"))
    M["bolge_dusuk"] = (gb.index[0], gb.iloc[0]["nps"], gb.iloc[0]["onay"])
    M["bolge_yuksek"] = (gb.index[-1], gb.iloc[-1]["nps"], gb.iloc[-1]["onay"])
    return M


def bulgu_karti(sutun, deger, baslik_metni, altyazi, renk):
    sutun.markdown(
        f'<div class="bulgu"><div class="bulgu-v" style="color:{renk}">{deger}</div>'
        f'<div class="bulgu-t">{baslik_metni}</div>'
        f'<div class="bulgu-s">{altyazi}</div></div>', unsafe_allow_html=True)


def aksiyon_karti(no, renk, baslik_metni, chip_metin, chip_renk, bulgu, aksiyon):
    st.markdown(
        f'<div class="aksiyon">'
        f'<div class="aksiyon-no" style="background:{renk}">{no}</div>'
        f'<div class="aksiyon-govde">'
        f'<div class="aksiyon-baslik">{baslik_metni}'
        f'<span class="chip" style="background:{saydam(chip_renk,.16)};'
        f'color:{chip_renk}">{chip_metin}</span></div>'
        f'<div class="aksiyon-bulgu">📊 {bulgu}</div>'
        f'<div class="aksiyon-aksiyon">▸ <b>Aksiyon:</b> {aksiyon}</div>'
        f'</div></div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# SEKMELER
# --------------------------------------------------------------------------- #
tab1, tab2, tab3, tab4 = st.tabs([
    "🚗  CSI · Kredi Kullananlar",
    "💵  CSI · Kredi Kullanmayanlar",
    "🏢  DSI · Bayi & CRM Deneyimi",
    "🎯  Yönetici Özeti",
])

# =========================================================================== #
# TAB 1 — CSI KREDİ KULLANANLAR
# =========================================================================== #
with tab1:
    d = df_kredi
    if d.empty:
        bos_uyari("Kredi Kullanan Müşteri segmentinde yanıt yok.")
    else:
        # ------------------------- KPI KARTLARI ------------------------- #
        eo0 = guvenli_ort(d["EO0_Genel_Memnuniyet"])
        nps, p_or, pa_or, d_or = nps_hesapla(d["F1_Recommendation_NPS"])

        surec_kolonlari = [c for c in ["C1a_Finansman_Kosullari_Bilgilendirme",
                                       "C2_Finansman_Secenekleri",
                                       "C8_Geri_Odeme_Kosullari",
                                       "C5_Surec_Kolaylik_Hiz"] if c in d.columns]
        surec = guvenli_ort(d[surec_kolonlari].mean(axis=1)) if surec_kolonlari else np.nan
        t2b = (pd.to_numeric(d["EO0_Genel_Memnuniyet"], errors="coerce") >= 9).mean() * 100

        k1, k2, k3, k4 = st.columns(4)
        kpi(k1, "Genel Memnuniyet (EO0)", f"{eo0:.2f}", "10 üzerinden ortalama",
            KPI_RENK[0], oran=eo0 / 10, T=T)
        kpi(k2, "NPS · Net Tavsiye Skoru", f"{nps:+.0f}",
            f"Promoter %{p_or:.0f} · Detractor %{d_or:.0f}",
            NPS_RENK["Promoter"] if nps >= 50 else
            (NPS_RENK["Passive"] if nps >= 0 else NPS_RENK["Detractor"]),
            oran=(nps + 100) / 200, T=T)
        kpi(k3, "Kredi Süreci Memnuniyeti", f"{surec:.2f}",
            "C1a · C2 · C8 · C5 ortalaması", KPI_RENK[2], oran=surec / 10, T=T)
        kpi(k4, "Memnuniyet Top-2-Box", f"%{t2b:.1f}", "9-10 puan verenler",
            KPI_RENK[4], oran=t2b / 100, T=T)

        # ------------------- MARKA METRİKLERİ (10'lu skala) ------------- #
        marka_metrik_bloku(
            d, MARKA_METRIKLERI_CSI, T,
            "Marka Metrikleri — 10'lu Skala",
            "Genel memnuniyet, tavsiye, marka önemi ve tekrar tercih "
            "puanları · F1 skalası 0-10, diğerleri 1-10")

        # ------------------------- DAĞILIMLAR --------------------------- #
        baslik("Memnuniyet Puanı Dağılımları",
               "EO0 genel memnuniyet dağılımı ve NPS kırılımı")
        c1, c2 = st.columns([1.45, 1])

        with c1:
            dag = (pd.to_numeric(d["EO0_Genel_Memnuniyet"], errors="coerce")
                   .value_counts().sort_index().reset_index())
            dag.columns = ["Puan", "Yanıt"]
            dag["Grup"] = np.where(dag["Puan"] >= 9, "Memnun (9-10)",
                          np.where(dag["Puan"] >= 7, "Nötr (7-8)", "Memnuniyetsiz (1-6)"))
            fig = px.bar(dag, x="Puan", y="Yanıt", color="Grup",
                         color_discrete_map={"Memnun (9-10)": NPS_RENK["Promoter"],
                                             "Nötr (7-8)": NPS_RENK["Passive"],
                                             "Memnuniyetsiz (1-6)": NPS_RENK["Detractor"]},
                         title="EO0 — Genel Memnuniyet Puanı Dağılımı", text="Yanıt")
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(dtick=1, title="Puan (1-10)")
            fig.update_yaxes(title="Yanıt sayısı")
            cizdir(grafik_duzen(fig, T))

        with c2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=nps,
                number={"suffix": "", "font": {"size": 40}},
                title={"text": "NPS (F1)", "font": {"size": 14}},
                gauge={
                    "axis": {"range": [-100, 100], "tickwidth": 1},
                    "bar": {"color": T["vurgu"], "thickness": 0.7},
                    "borderwidth": 0,
                    "steps": [
                        {"range": [-100, 0], "color": saydam(NPS_RENK["Detractor"], .20)},
                        {"range": [0, 50], "color": saydam(NPS_RENK["Passive"], .20)},
                        {"range": [50, 100], "color": saydam(NPS_RENK["Promoter"], .20)},
                    ],
                    "threshold": {"line": {"color": T["metin"], "width": 2},
                                  "thickness": 0.8, "value": nps},
                }))
            cizdir(grafik_duzen(fig, T, 380, legend_alt=False))

        # ---------------- ONAY SÜRESİ × SÜREÇ MEMNUNİYETİ --------------- #
        baslik("Kredi Onay Süresi — Korelasyon ve Eşik Analizi",
               "Solda süre ile süreç memnuniyeti (C5) ilişkisi, sağda NPS'in "
               "işareti değiştirdiği kırılma bandı")
        c1, c2 = st.columns([1.3, 1])

        with c1:
            sc = d.dropna(subset=["Kredi_Onay_Suresi_Saat", "C5_Surec_Kolaylik_Hiz"]).copy()
            if len(sc) > 2:
                r = sc["Kredi_Onay_Suresi_Saat"].corr(sc["C5_Surec_Kolaylik_Hiz"])
                fig = px.scatter(
                    sc, x="Kredi_Onay_Suresi_Saat", y="C5_Surec_Kolaylik_Hiz",
                    color="NPS_Kategori", color_discrete_map=NPS_RENK,
                    size="Kredi_Tutari_TL", size_max=17, opacity=.72,
                    hover_data={"Acente_Adi": True, "Vade_Ay": True,
                                "Kredi_Tutari_TL": ":,.0f"},
                    title=f"Onay Süresi (saat) × Süreç Memnuniyeti — r = {r:.3f}")
                # Trend çizgisi (statsmodels'e ihtiyaç duymadan)
                x, y = sc["Kredi_Onay_Suresi_Saat"], sc["C5_Surec_Kolaylik_Hiz"]
                egim, kesim = np.polyfit(x, y, 1)
                xs = np.linspace(x.min(), x.max(), 60)
                fig.add_trace(go.Scatter(x=xs, y=egim * xs + kesim, mode="lines",
                                         name="Trend", line=dict(color=T["vurgu"],
                                         width=2.5, dash="dash")))
                fig.update_xaxes(title="Kredi onay süresi (saat)")
                fig.update_yaxes(title="C5 · Süreç kolaylık & hız puanı", dtick=1)
                cizdir(grafik_duzen(fig, T, 430))
            else:
                bos_uyari("Korelasyon için yeterli veri yok.")

        with c2:
            # ---- ONAY SÜRESİ EŞİK ANALİZİ -------------------------------- #
            # Bantlar bilinçli olarak 4'er saatlik: kırılmanın hangi saatte
            # olduğunu görebilmek için ilk 12 saat detaylı bölünür.
            sc = d.dropna(subset=["Kredi_Onay_Suresi_Saat",
                                  "F1_Recommendation_NPS"]).copy()
            if len(sc):
                sc["Onay Bandı"] = pd.cut(
                    sc["Kredi_Onay_Suresi_Saat"], [0, 4, 8, 12, 24, 48, 10000],
                    labels=["0-4 sa", "4-8 sa", "8-12 sa",
                            "12-24 sa", "24-48 sa", "48+ sa"])
                ozet = (sc.groupby("Onay Bandı", observed=True)
                        .agg(n=("Respondent_ID", "count"),
                             EO0=("EO0_Genel_Memnuniyet", "mean"),
                             T2B=("EO0_Genel_Memnuniyet",
                                  lambda s: (s >= 9).mean() * 100),
                             NPS=("F1_Recommendation_NPS",
                                  lambda s: ((s >= 9).mean() - (s <= 6).mean()) * 100))
                        .reset_index().dropna(subset=["NPS"]))

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=ozet["Onay Bandı"], y=ozet["NPS"], name="NPS",
                    text=ozet["NPS"].round(0),
                    texttemplate="%{text:.0f}", textposition="outside",
                    cliponaxis=False,
                    marker_color=[NPS_RENK["Promoter"] if v >= 50 else
                                  (NPS_RENK["Passive"] if v >= 0 else
                                   NPS_RENK["Detractor"]) for v in ozet["NPS"]],
                    customdata=np.stack([ozet["n"], ozet["EO0"], ozet["T2B"]], -1),
                    hovertemplate=("<b>%{x}</b><br>NPS: %{y:.0f}<br>"
                                   "n: %{customdata[0]}<br>"
                                   "Ort. EO0: %{customdata[1]:.2f}<br>"
                                   "Top-2-Box: %%%{customdata[2]:.0f}<extra></extra>")))
                fig.add_hline(y=0, line_width=1, line_color=T["soluk"])
                # Kırılmanın gerçekleştiği ilk bandı işaretle
                negatif = ozet[ozet["NPS"] <= 0]
                if len(negatif):
                    fig.add_vline(
                        x=list(ozet["Onay Bandı"]).index(negatif.iloc[0]["Onay Bandı"]) - 0.5,
                        line_width=2, line_dash="dash", line_color=T["vurgu"],
                        annotation_text="kırılma eşiği",
                        annotation_position="top",
                        annotation_font=dict(size=11, color=T["vurgu"]))
                fig.update_yaxes(title="NPS", range=[-105, 115], zeroline=False)
                fig.update_xaxes(title="Kredi onay süresi bandı")
                fig.update_layout(
                    title="Onay Süresi Eşiği — Banda Göre NPS",
                    showlegend=False)
                cizdir(grafik_duzen(fig, T, 430, legend_alt=False))
                st.caption(
                    "Çubuk etiketleri NPS'tir; yanıt sayısı, ortalama memnuniyet "
                    "ve Top-2-Box için imleci çubuğun üzerine getirin.")

        # ---------------- SÜREÇ METRİKLERİ & ZAMAN TRENDİ --------------- #
        c1, c2 = st.columns(2)
        with c1:
            etiket = {
                "EO1x1_Acente_Satis_Danismani": "Acente satış danışmanı",
                "EO2x1_Stenos_Satis_Yoneticisi": "Stenos satış yöneticisi",
                "C1_Satis_Elemani_Yaklasimi": "Satış elemanı yaklaşımı",
                "C1a_Finansman_Kosullari_Bilgilendirme": "Finansman bilgilendirmesi",
                "C2_Finansman_Secenekleri": "Finansman seçenekleri",
                "C8_Geri_Odeme_Kosullari": "Geri ödeme koşulları",
                "C5_Surec_Kolaylik_Hiz": "Süreç kolaylık & hız",
                "E5a_Cagri_Merkezi_Memnuniyeti": "Çağrı merkezi",
            }
            sat = [(v, guvenli_ort(d[k])) for k, v in etiket.items() if k in d.columns]
            mdf = pd.DataFrame(sat, columns=["Metrik", "Puan"]).dropna().sort_values("Puan")
            fig = px.bar(mdf, x="Puan", y="Metrik", orientation="h", text="Puan",
                         color="Puan", color_continuous_scale=OLCEK["ikincil"],
                         title="Süreç Metrikleri — Ortalama Puanlar (10 üzerinden)")
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside",
                              cliponaxis=False)
            fig.update_xaxes(range=[0, 10.8], title="")
            fig.update_yaxes(title="")
            fig.update_layout(coloraxis_showscale=False)
            cizdir(grafik_duzen(fig, T, 400, legend_alt=False))

        with c2:
            trend = (d.groupby("Yil_Ay")
                     .agg(Memnuniyet=("EO0_Genel_Memnuniyet", "mean"),
                          Yanit=("Respondent_ID", "count")).reset_index())
            fig = go.Figure()
            fig.add_trace(go.Bar(x=trend["Yil_Ay"], y=trend["Yanit"], name="Yanıt sayısı",
                                 marker_color=T["kenar"], yaxis="y2", opacity=.85))
            fig.add_trace(go.Scatter(x=trend["Yil_Ay"], y=trend["Memnuniyet"],
                                     name="Ort. memnuniyet", mode="lines+markers",
                                     line=dict(color=PALET[0], width=3),
                                     marker=dict(size=7)))
            fig.update_layout(
                title="Aylık Memnuniyet Trendi & Saha Hacmi",
                yaxis=dict(title="Ort. EO0", range=[0, 10.5]),
                yaxis2=dict(title="Yanıt", overlaying="y", side="right",
                            showgrid=False),
            )
            cizdir(grafik_duzen(fig, T, 400))

        ham_veri_bolumu(d, VERI['kredi'], "Stenos_CSI_KrediKullanan", "dl_kredi")

# =========================================================================== #
# TAB 2 — CSI KREDİ KULLANMAYANLAR
# =========================================================================== #
with tab2:
    d = df_nakit
    if d.empty:
        bos_uyari("Kredi Kullanmayan Müşteri segmentinde yanıt yok.")
    else:
        neden_kol = "S3_Tercih_Etmeme_Nedeni"
        nedenler = d[neden_kol].value_counts()
        en_cok, en_cok_pay = nedenler.index[0], nedenler.iloc[0] / len(d) * 100

        alternatif = (d["S5_Kredi_Kullanilan_Kurulus"] != "Henüz kredi kullanmadım").mean() * 100
        s6 = guvenli_ort(d["S6_Bilgilendirme_Memnuniyeti"])
        yuksek_egilim = d["S11_Yuksek_Egilim"].mean() * 100 if "S11_Yuksek_Egilim" in d else np.nan

        k1, k2, k3, k4 = st.columns(4)
        kpi(k1, "Öne Çıkan Ret Nedeni", f"%{en_cok_pay:.1f}", en_cok,
            NPS_RENK["Detractor"], oran=en_cok_pay / 100, T=T)
        kpi(k2, "Alternatif Finansman Oranı", f"%{alternatif:.1f}",
            "Rakip kuruluştan kredi kullananlar", KPI_RENK[4], oran=alternatif / 100, T=T)
        kpi(k3, "Bilgilendirme Memnuniyeti (S6)", f"{s6:.2f}",
            "10 üzerinden ortalama", KPI_RENK[1], oran=s6 / 10, T=T)
        kpi(k4, "Yeniden Tercih Eğilimi", f"%{yuksek_egilim:.1f}",
            "S11 · %51+ olasılık verenler", KPI_RENK[2],
            oran=yuksek_egilim / 100, T=T)

        # --------------- NEDEN DAĞILIMI + ALTERNATİF FİNANSMAN ---------- #
        baslik("“Neden Kredi Kullanılmadı?” Kırılımı",
               "S3 — Stenos Auto Finans'ı tercih etmeme nedenleri")
        c1, c2 = st.columns([1.25, 1])

        with c1:
            nd = nedenler.reset_index()
            nd.columns = ["Neden", "Yanıt"]
            fig = px.pie(nd, names="Neden", values="Yanıt", hole=.56,
                         color_discrete_sequence=PALET,
                         title="Kredi Kullanmama Nedenleri")
            fig.update_traces(textposition="inside", textinfo="percent",
                              hovertemplate="%{label}<br>%{value} yanıt (%{percent})")
            fig.update_layout(legend=dict(orientation="v", x=1.02, y=.5,
                                          yanchor="middle", font=dict(size=11)))
            fig.add_annotation(text=f"<b>{len(d)}</b><br>yanıt", showarrow=False,
                               font=dict(size=17, color=T["metin"]))
            cizdir(grafik_duzen(fig, T, 420, legend_alt=False))

        with c2:
            alt_df = (d["S5_Kredi_Kullanilan_Kurulus"]
                      .replace("Henüz kredi kullanmadım", "Kredi kullanmadı (nakit)")
                      .value_counts().head(10).reset_index())
            alt_df.columns = ["Kuruluş", "Yanıt"]
            fig = px.bar(alt_df.sort_values("Yanıt"), x="Yanıt", y="Kuruluş",
                         orientation="h", text="Yanıt",
                         color="Yanıt", color_continuous_scale=OLCEK["vurgu"],
                         title="Alternatif Finansman Kaynağı (S5) — İlk 10")
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(title=""); fig.update_yaxes(title="")
            fig.update_layout(coloraxis_showscale=False)
            cizdir(grafik_duzen(fig, T, 420, legend_alt=False))

        # --------------- GELİR GRUBU × NEDEN ÇAPRAZ ANALİZ -------------- #
        baslik("Gelir Grubu × Kredi Kullanmama Nedeni — Çapraz Analiz",
               "Satır yüzdeleri: her nedenin gelir bantlarına dağılımı")
        c1, c2 = st.columns([1.3, 1])

        gelir_sira = ["25.000 TL altı", "25.001 - 50.000 TL", "50.001 - 85.000 TL",
                      "85.001 - 150.000 TL", "150.000 TL üzeri"]
        mevcut_gelir = [g for g in gelir_sira if g in d["Gelir_Grubu"].unique()]

        with c1:
            ct = pd.crosstab(d[neden_kol], d["Gelir_Grubu"], normalize="index") * 100
            ct = ct.reindex(columns=mevcut_gelir).fillna(0).round(1)
            fig = px.imshow(ct, text_auto=".0f", aspect="auto",
                            color_continuous_scale=OLCEK["ana"],
                            labels=dict(x="Gelir Grubu", y="", color="%"),
                            title="Isı Haritası — Neden × Gelir Grubu (satır %)")
            fig.update_xaxes(side="bottom", tickangle=-20)
            cizdir(grafik_duzen(fig, T, 430, legend_alt=False))

        with c2:
            ct2 = (pd.crosstab(d["Gelir_Grubu"], d[neden_kol])
                   .reindex(mevcut_gelir).fillna(0))
            uzun = ct2.reset_index().melt(id_vars="Gelir_Grubu",
                                          var_name="Neden", value_name="Yanıt")
            fig = px.bar(uzun, x="Gelir_Grubu", y="Yanıt", color="Neden",
                         color_discrete_sequence=PALET,
                         title="Gelir Grubuna Göre Neden Dağılımı")
            fig.update_xaxes(title="", tickangle=-20)
            fig.update_yaxes(title="Yanıt sayısı")
            fig.update_layout(legend=dict(orientation="h", y=-0.35, font=dict(size=10)))
            cizdir(grafik_duzen(fig, T, 430, legend_alt=False))

        # --------------- EK ANALİZLER ----------------------------------- #
        c1, c2 = st.columns(2)
        with c1:
            s11 = (d["S11_Gelecekte_Tercih_Olasiligi"].value_counts()
                   .reindex(["%0 -%25", "%26 - %50", "%51 - %75", "%76 - %100"])
                   .fillna(0).reset_index())
            s11.columns = ["Olasılık", "Yanıt"]
            fig = px.bar(s11, x="Olasılık", y="Yanıt", text="Yanıt",
                         color="Olasılık",
                         # Düşük -> yüksek eğilim sırası; ara tonlar seçili
                         # tasarımın paletinden gelir (sabit renk kullanılmaz)
                         color_discrete_sequence=[NPS_RENK["Detractor"],
                                                  NPS_RENK["Passive"],
                                                  PALET[1], NPS_RENK["Promoter"]],
                         title="S11 — Gelecekte Stenos Finans'ı Tercih Olasılığı")
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(title=""); fig.update_yaxes(title="Yanıt sayısı")
            fig.update_layout(showlegend=False)
            cizdir(grafik_duzen(fig, T, 400, legend_alt=False))

        with c2:
            avantaj = coklu_ac(d["S9_Onemli_Ek_Avantajlar"]).value_counts().reset_index()
            avantaj.columns = ["Avantaj", "Yanıt"]
            fig = px.bar(avantaj.sort_values("Yanıt"), x="Yanıt", y="Avantaj",
                         orientation="h", text="Yanıt", color="Yanıt",
                         color_continuous_scale=OLCEK["ikincil"],
                         title="S9 — Faiz Dışında Önem Verilen Ek Avantajlar")
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(title=""); fig.update_yaxes(title="")
            fig.update_layout(coloraxis_showscale=False)
            cizdir(grafik_duzen(fig, T, 400, legend_alt=False))

        ham_veri_bolumu(d, VERI['nakit'], "Stenos_CSI_KrediKullanmayan", "dl_nakit")

# =========================================================================== #
# TAB 3 — DSI BAYİ ÇALIŞANLARI / CRM
# =========================================================================== #
with tab3:
    d = df_dsi
    if d.empty:
        bos_uyari("Bayi Çalışanı / DSI segmentinde yanıt yok.")
    else:
        crm = guvenli_ort(d["CRM_Memnuniyeti_Birlesik"])
        hiz = guvenli_ort(d["S3b_1_CRM_Sistem_Hizi"])
        destek = guvenli_ort(d["S1_1_Ziyaret_Genel_Memnuniyet"])
        destek_n = pd.to_numeric(d["S1_1_Ziyaret_Genel_Memnuniyet"],
                                 errors="coerce").notna().sum()
        egitim = guvenli_ort(d["S5c_Egitim_Memnuniyeti"])

        k1, k2, k3, k4 = st.columns(4)
        kpi(k1, "CRM Kullanım Memnuniyeti", f"{crm:.2f}", "S3b / S3bx · 10 üzerinden",
            KPI_RENK[0], oran=crm / 10, T=T)
        kpi(k2, "Sistem Hızı Puanı", f"{hiz:.2f}", "Stenos CRM yanıt hızı",
            KPI_RENK[1], oran=hiz / 10, T=T)
        kpi(k3, "Bayi Destek Puanı", f"{destek:.2f}",
            f"S1.1 acente ziyaretleri · baz n={destek_n}", KPI_RENK[2],
            oran=destek / 10, T=T)
        kpi(k4, "Eğitim Memnuniyeti", f"{egitim:.2f}", "S5c · C-Sales eğitimleri",
            KPI_RENK[4], oran=egitim / 10, T=T)

        # --------------- CRM ↔ SATIŞ PERFORMANSI ------------------------ #
        baslik("CRM Memnuniyetinin Satış Performansına Etkisi",
               "Acente bazında: CRM memnuniyeti yükseldikçe satış başarısı endeksi artıyor")
        c1, c2 = st.columns([1.35, 1])

        with c1:
            sc = d.dropna(subset=["CRM_Memnuniyeti_Birlesik",
                                  "Acente_Satis_Basarisi_Endeks_100"])
            if len(sc) > 2:
                r = sc["CRM_Memnuniyeti_Birlesik"].corr(
                    sc["Acente_Satis_Basarisi_Endeks_100"])
                ozet = (sc.groupby(["Acente_Adi", "Bolge"])
                        .agg(CRM=("CRM_Memnuniyeti_Birlesik", "mean"),
                             Satis=("Acente_Satis_Basarisi_Endeks_100", "mean"),
                             Calisan=("Respondent_ID", "count")).reset_index())
                fig = px.scatter(ozet, x="CRM", y="Satis", size="Calisan",
                                 color="Bolge", size_max=42, opacity=.85,
                                 hover_name="Acente_Adi",
                                 color_discrete_sequence=PALET,
                                 title=f"Acente Bazında CRM × Satış Başarısı — "
                                       f"birey düzeyi r = {r:.3f}")
                x, y = ozet["CRM"], ozet["Satis"]
                if len(ozet) > 2:
                    egim, kesim = np.polyfit(x, y, 1)
                    xs = np.linspace(x.min(), x.max(), 60)
                    fig.add_trace(go.Scatter(x=xs, y=egim * xs + kesim, mode="lines",
                                             name="Trend", showlegend=False,
                                             line=dict(color=T["vurgu"], width=2.5,
                                                       dash="dash")))
                fig.update_xaxes(title="Ort. Stenos CRM memnuniyeti (10 üzerinden)")
                fig.update_yaxes(title="Acente satış başarısı endeksi (0-100)")
                fig.update_layout(legend=dict(font=dict(size=10)))
                # 7 bölge etiketi iki satıra sarıyor -> ekstra üst boşluk
                cizdir(grafik_duzen(fig, T, 460, legend_satir=2))
            else:
                bos_uyari("Korelasyon için yeterli veri yok.")

        with c2:
            band = d.dropna(subset=["CRM_Memnuniyeti_Birlesik"]).copy()
            if len(band):
                band["CRM Bandı"] = pd.cut(
                    band["CRM_Memnuniyeti_Birlesik"], [0, 5, 6, 7, 8, 10],
                    labels=["≤5", "6", "7", "8", "9-10"])
                ozet = (band.groupby("CRM Bandı", observed=True)
                        .agg(Satis=("Acente_Satis_Basarisi_Endeks_100", "mean"),
                             n=("Respondent_ID", "count")).reset_index().dropna())
                fig = px.bar(ozet, x="CRM Bandı", y="Satis", text="n",
                             color="Satis", color_continuous_scale=OLCEK["ana"],
                             title="CRM Memnuniyet Bandına Göre Satış Başarısı")
                fig.update_traces(texttemplate="n=%{text}", textposition="outside",
                                  cliponaxis=False)
                fig.update_yaxes(title="Ort. satış başarısı endeksi", range=[0, 105])
                fig.update_xaxes(title="CRM memnuniyet puanı")
                fig.update_layout(coloraxis_showscale=False)
                cizdir(grafik_duzen(fig, T, 440, legend_alt=False))

        # --------------- SİSTEMSEL AKSAKLIKLAR -------------------------- #
        baslik("En Çok Yaşanan Sistemsel Aksaklıklar",
               "M9 — Bayi çalışanlarının iyileştirilmesini istediği konular (çoklu yanıt)")
        c1, c2 = st.columns([1.4, 1])

        with c1:
            sorun = coklu_ac(d["M9_Iyilestirilecek_Konular"]).value_counts().head(12)
            sdf = sorun.reset_index()
            sdf.columns = ["Konu", "Yanıt"]
            sdf["Pay"] = sdf["Yanıt"] / len(d) * 100
            fig = px.bar(sdf.sort_values("Yanıt"), x="Yanıt", y="Konu",
                         orientation="h", text="Pay",
                         color="Yanıt", color_continuous_scale=OLCEK["negatif"],
                         title="M9 — En Sık Bildirilen Sorun Alanları (İlk 12)")
            fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside",
                              cliponaxis=False)
            fig.update_xaxes(title="Yanıt sayısı")
            fig.update_yaxes(title="")
            fig.update_layout(coloraxis_showscale=False)
            cizdir(grafik_duzen(fig, T, 470, legend_alt=False))

        with c2:
            pozitif = coklu_ac(d["M8_Mutlu_Eden_Etkenler"]).value_counts().head(8)
            pdf = pozitif.reset_index()
            pdf.columns = ["Etken", "Yanıt"]
            fig = px.bar(pdf.sort_values("Yanıt"), x="Yanıt", y="Etken",
                         orientation="h", text="Yanıt", color="Yanıt",
                         color_continuous_scale=OLCEK["pozitif"],
                         title="M8 — Memnuniyet Yaratan Etkenler (İlk 8)")
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(title=""); fig.update_yaxes(title="")
            fig.update_layout(coloraxis_showscale=False)
            cizdir(grafik_duzen(fig, T, 470, legend_alt=False))

        # --------------- CRM ALT METRİKLERİ & BÖLGE --------------------- #
        c1, c2 = st.columns(2)
        with c1:
            metrikler = {
                "S3b_Stenos_CRM_Memnuniyeti": "CRM genel (Satış)",
                "S3bx_Stenos_CRM_Memnuniyeti_Sigorta": "CRM genel (Sigorta)",
                "S3b_1_CRM_Sistem_Hizi": "CRM sistem hızı",
                "S3a_Kredilendirme_Sureci": "Kredilendirme süreci",
                "S5c_Egitim_Memnuniyeti": "C-Sales eğitimleri",
                "S1_1_Ziyaret_Genel_Memnuniyet": "Acente ziyaretleri",
                "S1_2_Ziyaret_Sikligi_Memnuniyet": "Ziyaret sıklığı",
                "M4a_Genel_Memnuniyet_Finans": "Genel memnuniyet (M4a)",
            }
            sat = [(v, guvenli_ort(d[k])) for k, v in metrikler.items() if k in d.columns]
            mdf = pd.DataFrame(sat, columns=["Metrik", "Puan"]).dropna()
            fig = go.Figure(go.Scatterpolar(
                r=mdf["Puan"], theta=mdf["Metrik"], fill="toself",
                line=dict(color=PALET[0], width=2),
                fillcolor=saydam(PALET[0], .28), name="Ortalama"))
            fig.update_layout(
                title="DSI Metrik Profili (10 üzerinden)",
                polar=dict(radialaxis=dict(visible=True, range=[0, 10],
                                           gridcolor=T["grid"]),
                           angularaxis=dict(gridcolor=T["grid"]),
                           bgcolor=T["zemin"]))
            cizdir(grafik_duzen(fig, T, 430, legend_alt=False))

        with c2:
            bol = (d.groupby("Bolge")
                   .agg(CRM=("CRM_Memnuniyeti_Birlesik", "mean"),
                        Satis=("Acente_Satis_Basarisi_Endeks_100", "mean"),
                        n=("Respondent_ID", "count"))
                   .reset_index().sort_values("CRM"))
            fig = go.Figure()
            fig.add_trace(go.Bar(y=bol["Bolge"], x=bol["CRM"], orientation="h",
                                 name="CRM memnuniyeti", marker_color=PALET[0],
                                 text=bol["CRM"].round(2), textposition="outside"))
            fig.add_trace(go.Scatter(y=bol["Bolge"], x=bol["Satis"] / 10,
                                     name="Satış başarısı (÷10)", mode="markers",
                                     marker=dict(size=13, color=PALET[3],
                                                 symbol="diamond")))
            fig.update_layout(title="Bölgeye Göre CRM Memnuniyeti & Satış Başarısı",
                              xaxis=dict(title="Puan (10 üzerinden)", range=[0, 11]),
                              yaxis=dict(title=""))
            cizdir(grafik_duzen(fig, T, 430))

        ham_veri_bolumu(d, VERI['dsi'], "Stenos_DSI_BayiCalisanlari", "dl_dsi")

# =========================================================================== #
# TAB 4 — YÖNETİCİ ÖZETİ
# =========================================================================== #
with tab4:
    M = yonetici_metrikleri()
    nps_isaret = lambda v: NPS_RENK["Promoter"] if v >= 50 else (
        NPS_RENK["Passive"] if v >= 0 else NPS_RENK["Detractor"])

    st.info("🎯  Yönetici özeti **tüm anketi** (900 yanıt) kapsar ve soldaki "
            "filtrelerden etkilenmez. Segment detayları için ilgili sekmelere geçin.")

    # ====================================================================== #
    # BÖLÜM 1 — ANKET ÖZETİ / ÖNE ÇIKANLAR
    # ====================================================================== #
    baslik("1 · Anket Özeti — Yönetici Bakışı",
           "2025-2026 CSI & DSI araştırmasının en çarpıcı sonuçları")

    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Toplam Yanıt", f"{M['toplam']}".replace(",", "."),
        f"{M['n_kredi']} kredili · {M['n_nakit']} kredisiz · {M['n_dsi']} bayi",
        T["vurgu"], T=T)
    kpi(k2, "Müşteri NPS (CSI)", f"{M['csi_nps']:+.0f}", "F1 · Net Tavsiye Skoru",
        nps_isaret(M["csi_nps"]), oran=(M["csi_nps"] + 100) / 200, T=T)
    kpi(k3, "Bayi NPS (DSI)", f"{M['dsi_nps']:+.0f}", "M6 · Net Tavsiye Skoru",
        nps_isaret(M["dsi_nps"]), oran=(M["dsi_nps"] + 100) / 200, T=T)
    kpi(k4, "Genel Memnuniyet", f"{M['eo0']:.2f}", "EO0 · 10 üzerinden",
        KPI_RENK[0] if 'KPI_RENK' in dir() else T["vurgu"], oran=M["eo0"] / 10, T=T)

    # En çarpıcı bulgu — NPS makası
    fark = M["csi_nps"] - M["dsi_nps"]
    st.markdown(
        f'<div class="callout"><div class="callout-b">'
        f'⚠️ Müşteri bizi tavsiye ediyor (NPS {M["csi_nps"]:+.0f}), bizi satan '
        f'kanal etmiyor (NPS {M["dsi_nps"]:+.0f}) — {fark:.0f} puanlık makas.'
        f'</div><div class="callout-s">'
        f'Bayi danışmanı müşteriyle ilk teması yapan kişidir. CSI tarafındaki '
        f'güçlü tablo değerli, ancak memnuniyetsiz bir satış kanalı bu tabloyu '
        f'orta vadede aşındırır. Bu, bir memnuniyet farkı değil stratejik risktir.'
        f'</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="bolum-alt">Öne çıkan dört bulgu</div>',
                unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    bulgu_karti(b1, M["esik"], "Onay süresi kırılma eşiği",
                "Bu bandı geçen dosyalarda NPS negatife dönüyor",
                NPS_RENK["Detractor"])
    bulgu_karti(b2, f"%{M['cagri_t2b']:.0f}", "Çağrı merkezi Top-2-Box",
                f"En zayıf temas noktası · müşterilerin %{M['e1_aradi']:.0f}'i arıyor",
                NPS_RENK["Detractor"])
    bulgu_karti(b3, f"%{M['kasko_teklifsiz']:.0f}",
                "Kasko teklifi hiç verilmemiş",
                f"Almayan Retail müşteriler içinde · attach %{M['attach']:.0f}",
                NPS_RENK["Passive"])
    bulgu_karti(b4, f"%{M['mobil_farkinda']:.0f}", "Mobil uygulama farkındalığı",
                f"Oysa müşterilerin %{M['e1_aradi']:.0f}'i çağrı merkezini arıyor",
                NPS_RENK["Passive"])

    st.write("")
    c1, c2 = st.columns([1, 1])
    with c1:
        # CSI vs DSI NPS karşılaştırması
        cmp = pd.DataFrame({"Segment": ["Müşteri (CSI)", "Bayi (DSI)"],
                            "NPS": [round(M["csi_nps"]), round(M["dsi_nps"])]})
        fig = px.bar(cmp, x="NPS", y="Segment", orientation="h",
                     color="Segment",
                     color_discrete_sequence=[nps_isaret(M["csi_nps"]),
                                              nps_isaret(M["dsi_nps"])],
                     title="Müşteri NPS ↔ Bayi NPS Makası")
        fig.update_traces(texttemplate="%{x:+.0f}", textposition="outside",
                          cliponaxis=False)
        fig.add_vline(x=0, line_width=1, line_color=T["soluk"])
        fig.update_xaxes(title="NPS", range=[-60, 80])
        fig.update_yaxes(title="")
        fig.update_layout(showlegend=False)
        cizdir(grafik_duzen(fig, T, 300, legend_alt=False))
    with c2:
        # Sorun yaşama etkisi
        sr = pd.DataFrame({
            "Durum": ["Sorun yaşamadı", "Sorun çözüldü", "Sorun çözülmedi"],
            "NPS": [round(M["nps_sorunsuz"]), round(M["nps_cozuldu"]),
                    round(_nps(VERI["kredi"].query(
                        "I1_Sorun_Yasadi_mi==1 and I2_Sorun_Giderildi_mi==2")
                        ["F1_Recommendation_NPS"]))]})
        fig = px.bar(sr, x="NPS", y="Durum", orientation="h",
                     color="NPS", color_continuous_scale=OLCEK["ana"],
                     title=f"Sorun Önlemenin Değeri (sorun oranı %{M['sorun_oran']:.0f})")
        fig.update_traces(texttemplate="%{x:+.0f}", textposition="outside",
                          cliponaxis=False)
        fig.update_xaxes(title="NPS", range=[0, 75])
        fig.update_yaxes(title="", categoryorder="array",
                         categoryarray=["Sorun çözülmedi", "Sorun çözüldü",
                                        "Sorun yaşamadı"])
        fig.update_layout(coloraxis_showscale=False)
        cizdir(grafik_duzen(fig, T, 300, legend_alt=False))

    # ====================================================================== #
    # BÖLÜM 2 — AKSİYON PLANI
    # ====================================================================== #
    baslik("2 · Aksiyon Planı",
           "Mevcut verideki bulgulara dayalı, önceliklendirilmiş öneriler")

    KIRMIZI, TURUNCU, MAVI = NPS_RENK["Detractor"], NPS_RENK["Passive"], T["vurgu"]

    aksiyon_karti(
        1, KIRMIZI, "Ulaşılabilirlik krizi", "90 gün · kritik", KIRMIZI,
        f"Üç kaynak aynı yeri işaret ediyor: çağrı merkezi en düşük CSI metriği "
        f"(Top-2-Box <b>%{M['cagri_t2b']:.0f}</b>), müşterilerin "
        f"<b>%{M['e1_ulasamadi']:.0f}</b>'i \"aradım ama ulaşamadım\" diyor ve "
        f"DSI'da en sık üç şikâyetin üçü iletişimle ilgili.",
        "Servis seviyesi (SL/ASA/abandon) ölçümünü haftalık yönetim gündemine "
        "almak, bayi hattını müşteri hattından ayırmak, geri arama taahhüdü koymak.")
    aksiyon_karti(
        2, TURUNCU, "Kasko — masada duran gelir", "60 gün · yüksek getiri", TURUNCU,
        f"Kasko almayan Retail müşterilerin <b>%{M['kasko_teklifsiz']:.0f}</b>'ine "
        f"teklif hiç verilmemiş; teklif verilenlerin "
        f"<b>%{M['kasko_avantajsiz']:.0f}</b>'ine ürün avantajları anlatılmamış. "
        f"Bu fiyat değil, uygulama kaybı (mevcut attach %{M['attach']:.0f}).",
        "Teklif verme adımını CRM'de zorunlu alan yapmak, danışmana 3 maddelik "
        "avantaj kartı vermek.")
    aksiyon_karti(
        3, MAVI, "Onay süresini bölgesel yönetmek", "orta vade", MAVI,
        f"Kırılma eşiği <b>{M['esik']}</b>. Bölge uçları net: "
        f"{M['bolge_yuksek'][0]} {M['bolge_yuksek'][2]:.1f} sa / NPS "
        f"{M['bolge_yuksek'][1]:+.0f} ↔ {M['bolge_dusuk'][0]} "
        f"{M['bolge_dusuk'][2]:.1f} sa / NPS {M['bolge_dusuk'][1]:+.0f}.",
        "Onay süresi hedefini bölge müdürü karnesine koymak; 8 saati aşan "
        "dosyalarda otomatik eskalasyon. (Acente tabanları küçük — bölge "
        "düzeyinde konuşulmalı, acente sıralaması yayınlanmamalı.)")
    aksiyon_karti(
        4, MAVI, "Önleme, kurtarmadan değerli", "süreç", MAVI,
        f"Sorunsuz müşteri NPS <b>{M['nps_sorunsuz']:+.0f}</b>; sorun çözülünce "
        f"yalnızca <b>{M['nps_cozuldu']:+.0f}</b>'e çıkıyor. \"Çözdük\" dediğimiz "
        f"şey müşteride çözülmüş hissi bırakmıyor (çözüm oranı "
        f"%{M['cozum_oran']:.0f}).",
        "Çözüm tanımını müşteri onayına bağlamak (kapanışta teyit); kök neden "
        "analizini ilk üç sorun tipiyle başlatmak.")
    aksiyon_karti(
        5, TURUNCU, "Dijitali maliyet kalemi olarak yönetmek", "60 gün", TURUNCU,
        f"Mobil uygulamadan haberdar yalnızca <b>%{M['mobil_farkinda']:.0f}</b>; "
        f"aynı anda %{M['e1_aradi']:.0f} çağrı merkezini arıyor ve danışmanların "
        f"<b>%{M['danisman_onermiyor']:.0f}</b>'i uygulamayı hiç önermiyor.",
        "Teslimat anında uygulama kurulumunu sürece gömmek; danışman primine "
        "\"uygulama indirme\" adımını eklemek.")
    aksiyon_karti(
        6, MAVI, "Kredi kullanmayanlarda hedefli geri kazanım", "orta vade", MAVI,
        f"Geri dönüş eğilimi en yüksek gruplar: "
        f"\"{M['gk'].index[0]}\" %{M['gk'].iloc[0]:.0f}, "
        f"\"{M['gk'].index[1]}\" %{M['gk'].iloc[1]:.0f}. Faiz dışında en çok "
        f"istenenler vade, özel temsilci ve sigorta — üçü de indirim gerektirmiyor.",
        "Bu iki gruba ürün/kampanya ayarıyla dönüş; \"limit alamadım\" grubuna "
        "ayrı ret iletişimi tasarlamak.")
    aksiyon_karti(
        7, MAVI, "Bayi ilişkisini onarmak", "sürekli", MAVI,
        f"DSI'da en zayıf metrik <b>{M['dsi_min']}</b> ({M['dsi_min_val']:.1f}/10). "
        f"M9'da eğitim ve CRM hızı öne çıkan şikâyetler.",
        "Ziyaret takvimini penetrasyonu düşük acentelere ağırlıklandırmak; CRM "
        "hız şikâyetini IT backlog'unda önceliklendirmek.")

    # ====================================================================== #
    # BÖLÜM 3 — GELECEK YIL ANKETİ ÖNERİLERİ
    # ====================================================================== #
    baslik("3 · Gelecek Yıl Anketi İçin Öneriler",
           "CEO geri bildirimi + bu yılın bulguları ışığında")

    st.markdown(
        f'<div class="callout"><div class="callout-b">'
        f'🔑 Tek en önemli değişiklik: ankete CRM/sözleşme kimliği bağlanmalı.'
        f'</div><div class="callout-s">'
        f'Respondent_ID yerine müşteri/sözleşme numarası eklenirse penetrasyon, '
        f'gerçek tekrar kullanım, kasko attach ekonomisi, erken kapama ve gecikme '
        f'— hiç soru sormadan davranışsal olarak bağlanır. CEO\'nun "anket para '
        f'ölçmüyor" itirazının büyük kısmı tek alanla çözülür.'
        f'</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(
            '<div class="oneri-kutu"><h4>📐 Ölçüm ritmi ikiye ayrılmalı</h4>'
            '<p><b>İşlemsel CSI</b> — kredi kullanımından 7-10 gün sonra, sürekli. '
            'Süreç, onay süresi, ilk temas. ~4-5 dk.</p>'
            '<p><b>İlişkisel CSI</b> — yılda 1 dalga. NPS, marka, tekrar tercih, '
            'rakip karşılaştırma. ~8-10 dk.</p>'
            '<p class="neden">Tek uzun dalga yerine olaya yakın ölçüm, hatırlama '
            'hatasını düşürür.</p></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="oneri-kutu"><h4>➕ Eklenecek sorular</h4>'
            '<li>Müşteri eforu (CES) — ulaşılabilirlik ana sorunumuz, eforu hiç ölçmüyoruz</li>'
            '<li>İlk temasta çözüm + çözüm süresi — +23/+61 uçurumunun nedeni burada</li>'
            '<li>Rakip teklifin oranı/vadesi (rakam) — kaç baz puan gerektiğini bilmiyoruz</li>'
            '<li>Kaybın hangi aşamada olduğu (huni) — "reddettik" ile "fiyat" ayrışmalı</li>'
            '<li>Uygulama kullanımı — farkındalık değil, son 3 aydaki işlem</li>'
            '<li>DSI\'ya komisyon rekabetçiliği ve rakip NPS\'i</li></div>',
            unsafe_allow_html=True)
    with c2:
        st.markdown(
            '<div class="oneri-kutu"><h4>🧪 Metodolojik düzeltmeler</h4>'
            '<li><b>Örneklem:</b> DSI\'da acente başına ~13 kişi kalıyor; acente '
            'karnesi için minimum taban belirlenmeli, yoksa kırılım bölgede kalmalı</li>'
            '<li><b>Ağırlıklandırma:</b> portföyün bayi/bölge/ürün dağılımına göre</li>'
            '<li><b>Halo etkisi:</b> süreç sorularını genel memnuniyetin hemen '
            'ardından sormak hepsini birbirine korele ediyor — blok sırası '
            'randomize edilmeli</li>'
            '<li><b>Kredi kullanmayan çerçevesi:</b> bizim datamızdaki kişiler değil, '
            'bayi trafiğinden örneklenmeli</li>'
            '<li><b>Karşılaştırılabilirlik:</b> soru metinleri ve skalalar '
            'dondurulmalı (F1 0-10, diğerleri 1-10 ayrımı korunmalı)</li></div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div class="oneri-kutu"><h4>➖ Yer açmak için çıkarılabilecekler</h4>'
            '<p class="neden">Kasko K2 (nereden haberdar), pazarlama N2 (takip '
            'kanalı) düşük aksiyon değeri taşıyor; B5\'teki 45 bankalık liste ilk '
            '10\'a indirilebilir.</p></div>', unsafe_allow_html=True)

    st.caption("Not: Yukarıdaki tüm sayılar mevcut sentetik dosyalardan canlı "
               "hesaplanır. Yöntem ve okuma biçimi gerçek veride birebir "
               "geçerlidir; sayıların kendisi demo niteliğindedir.")

# --------------------------------------------------------------------------- #
# ALT BİLGİ
# --------------------------------------------------------------------------- #
st.divider()
st.caption(
    f"**Odysseus Araştırma** × **Stenos Auto Finansman A.Ş.** · "
    f"CSI & DSI 2025-2026 · Aktif filtrelerle {toplam_n} yanıt görüntüleniyor · "
    f"Veri: sentetik demo (gerçek saha verisi değildir)")


# ===========================================================================
#  ÇALIŞTIRMA
#  ---------------------------------------------------------------------------
#  1) Gerekli paketler:
#         pip install streamlit pandas numpy plotly
#
#  2) Dashboard'u başlat (app.py ve 3 CSV aynı klasörde olmalı):
#         streamlit run app.py
#
#     Tarayıcı otomatik açılmazsa:  http://localhost:8501
#
#  3) Farklı port kullanmak için:
#         streamlit run app.py --server.port 8502
# ===========================================================================
