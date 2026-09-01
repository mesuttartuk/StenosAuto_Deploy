# Stenos Auto CSI/DSI Dashboard — Statik HTML/JS Sürümü

Orijinal Streamlit uygulamasının birebir HTML/JS karşılığı. Python veya başka
bir sunucu runtime'ı gerekmez; tüm veri okuma, filtreleme, metrik hesaplama
(NPS, ortalama, korelasyon vb.) ve grafik çizimi tarayıcıda çalışır.

## Dosya yapısı

```
index.html          Sayfa iskeleti
css/style.css        Konecta marka teması (açık/koyu), tüm bileşen stilleri
js/app.js            Veri yükleme, filtreleme, hesaplamalar, grafik çizimleri
vendor/plotly.min.js Plotly.js — gömülü, internet gerekmez
data/*.csv           3 anket verisi (CSI kredi/nakit, DSI bayi)
Dockerfile / docker-compose.yml   Nginx tabanlı statik deploy
```

## Çalıştırma

`index.html`'i çift tıklayıp doğrudan açmayın — tarayıcılar `file://`
üzerinden CSV okumayı (fetch) güvenlik gereği engeller. Bir HTTP sunucusu
üzerinden servis edin:

```
python -m http.server 8080
# -> http://localhost:8080
```

veya Docker ile:

```
docker build -t stenos-auto-html .
docker run -p 8080:80 stenos-auto-html
```

Detaylı deploy talimatları (reverse proxy, gerçek veri değişimi vb.) için
[`DEPLOY.txt`](DEPLOY.txt).

## GitHub Pages ile canlı link

Bu klasör tamamen statik olduğu için doğrudan GitHub Pages ile yayınlanabilir:

1. GitHub'da repo → **Settings → Pages**
2. Source: `Deploy from a branch`, Branch: `main`, klasör: `/StenosAuto_Deploy/html` (Pages kök dizin dışını desteklemiyorsa bu klasörü ayrı bir `gh-pages` branch'ine veya repoya taşımak gerekir)
3. Yayınlanan URL üzerinden dashboard doğrudan açılır.

## Gerçek veri

`data/` klasöründeki 3 CSV'yi aynı isim ve kolon yapısıyla değiştirin; kod
kolon adlarına göre çalışır (`Anket_Tarihi`, `Sehir`, `Bolge`, `Acente_Adi`,
`Segment` vb.).
