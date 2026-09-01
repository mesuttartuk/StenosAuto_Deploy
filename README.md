# Stenos Auto CSI/DSI Dashboard

Stenos Auto Finansman A.Ş. için 2025-2026 Müşteri & Bayi Memnuniyet Araştırması
dashboard'u. İki eşdeğer sürüm olarak sunulur:

| Sürüm | Klasör | Runtime | Kullanım |
|---|---|---|---|
| **Statik HTML/JS** (önerilen) | [`docs/`](docs/) | Yok — herhangi bir statik dosya sunucusu | Basit deploy, Docker/Nginx, GitHub Pages |
| Python / Streamlit (orijinal) | bu klasörün kökü (`app.py`) | Python 3.10-3.12 + Streamlit | pandas ile sunucu taraflı işlem gerekiyorsa |

Her iki sürüm de aynı 3 CSV dosyasını okur ve aynı filtreleme/metrik mantığını
uygular; aralarındaki fark yalnızca çalışma ortamıdır.

Klasörün adı bilinçli olarak `docs/` — GitHub Pages "Deploy from a branch"
seçeneği yalnızca `/ (root)` veya `/docs` klasörünü statik site olarak
yayınlayabiliyor; bu repo `/docs` ile Pages üzerinden canlı yayınlanacak
şekilde ayarlı.

## Statik HTML sürümü (`docs/`)

Tüm hesaplama ve grafik çizimi tarayıcıda yapılır (Plotly.js gömülü, internet
gerekmez). Çalıştırmak için:

```
cd docs
python -m http.server 8080
# -> http://localhost:8080
```

veya Docker ile:

```
cd docs
docker build -t stenos-auto-html .
docker run -p 8080:80 stenos-auto-html
```

GitHub Pages ile canlı yayın için: repo **Settings → Pages → Build and
deployment → Branch**: `main` / `/docs`, kaydet. Birkaç dakika sonra
`https://<kullanıcı-adı>.github.io/<repo-adı>/` adresinden açılır.

Ayrıntılar için [`docs/README.md`](docs/README.md) ve [`docs/DEPLOY.txt`](docs/DEPLOY.txt).

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
Python hem HTML sürümü kök dizindeki (`docs/` için `docs/data/` altındaki)
dosyaları aynı isimlerle bekler.
