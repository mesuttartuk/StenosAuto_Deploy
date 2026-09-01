# Stenos Auto CSI/DSI Dashboard

Stenos Auto Finansman A.Ş. için 2025-2026 Müşteri & Bayi Memnuniyet Araştırması
dashboard'u. İki eşdeğer sürüm olarak sunulur:

| Sürüm | Klasör | Runtime | Kullanım |
|---|---|---|---|
| **Statik HTML/JS** (önerilen) | [`html/`](html/) | Yok — herhangi bir statik dosya sunucusu | Basit deploy, Docker/Nginx, GitHub Pages |
| Python / Streamlit (orijinal) | bu klasörün kökü (`app.py`) | Python 3.10-3.12 + Streamlit | pandas ile sunucu taraflı işlem gerekiyorsa |

Her iki sürüm de aynı 3 CSV dosyasını okur ve aynı filtreleme/metrik mantığını
uygular; aralarındaki fark yalnızca çalışma ortamıdır.

## Statik HTML sürümü (`html/`)

Tüm hesaplama ve grafik çizimi tarayıcıda yapılır (Plotly.js gömülü, internet
gerekmez). Çalıştırmak için:

```
cd html
python -m http.server 8080
# -> http://localhost:8080
```

veya Docker ile:

```
cd html
docker build -t stenos-auto-html .
docker run -p 8080:80 stenos-auto-html
```

Ayrıntılar için [`html/README.md`](html/README.md) ve [`html/DEPLOY.txt`](html/DEPLOY.txt).

## Python / Streamlit sürümü (kök)

```
pip install -r requirements.txt
streamlit run app.py
```

Ayrıntılar için [`DEPLOY.txt`](DEPLOY.txt).

## Veri

Üç CSV demo/sentetik veridir: `Stenos_CSI_KrediKullanan.csv`,
`Stenos_CSI_KrediKullanmayan.csv`, `Stenos_DSI_BayiCalisanlari.csv`. Gerçek
veri geldiğinde aynı isim ve kolon yapısıyla değiştirilmesi yeterlidir — hem
Python hem HTML sürümü kök dizindeki (`html/` için `html/data/` altındaki)
dosyaları aynı isimlerle bekler.
