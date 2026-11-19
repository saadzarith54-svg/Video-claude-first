# Rancangan Suntingan — Promo PERAH LAB "Orange Blast" (PREVIEW v2)

Status: **PREVIEW sahaja (540×960, ada tanda "PREVIEW v2")**. Fail final 1080×1920 hanya akan dirender selepas anda luluskan.

**Arah baharu (v2):** Produk utama ialah **PERAH LAB, air oren segar**. Hari Terbuka Asrama dan Piala Pengarah Ragbi ialah **tempat anda berniaga**. Versi v1 (promo kejohanan) disimpan dalam `promo/v1/` sebagai rujukan.

## 1. Aset yang digunakan

| Aset | Sumber | Rawatan |
|---|---|---|
| Logo PERAH LAB | `IMG_6078.png` | Latar putih dibuang (cut-out) |
| Cawan + tangan "Orange Blast" | Poster `Orange Juice.png` | Langit biru dibuang, jadi cawan "terapung" dalam 3D |
| Logo HTK 26 (Hari Terbuka Asrama) | `IMG_6377.jpeg` | Resolusi rendah, jadi dipaparkan dalam jubin bersudut bulat (latar asal dikekalkan) |
| Logo Kejohanan Ragbi IPG Perlis 10s (Piala Pengarah Ragbi) | `IMG_6376.jpeg` | Latar kelabu dibuang |
| Peta | Tangkapan skrin Apple Maps | Rujukan susun atur sahaja (peta stilisasi) |
| Fon | Lilita One (≈ gaya poster), Bowlby One (ORANGE BLAST), Inter Display | Fon terbuka (OFL) |

## 2. Hook (0–3.0 s)
Penonton datang ke acara ragbi, jadi hook bermula di "dunia" mereka:
1. **0.2–0.9 s** Stadium gelap, 4 lampu limpah menyala dengan bunyi *CLUNK*.
2. **1.05–2.15 s** Bola ragbi meluncur berputar ke arah kamera.
3. **2.16 s** Kilat putih, **bola bertukar jadi buah oren** dengan percikan jus dan bunyi *SPLASH*, dan teks **"HAUS?"** muncul. Ini kejutan visual: penonton jangka ragbi, tapi dapat oren.
4. **2.7–3.0 s** Oren meluru ke kamera, kemudian **beat drop** dan dunia biru PERAH LAB muncul.

## 3. Garis masa (20.0 s, 30 fps)

| Masa | Babak | Visual | Muzik & SFX |
|---|---|---|---|
| 0.00–3.00 | **Hook stadium** | Lampu limpah, bola ragbi, bertukar jadi oren, "HAUS?" | Rumble, CLUNK ×4, whoosh, riser, **splash + hit**, clink |
| 3.00–3.50 | **Jenama** | Latar biru bersinar (warna poster), logo PERAH LAB "pop" ke tengah, buah oren 3D (separuh, hirisan, biji) & ais terapung masuk dari tepi | **BEAT DROP** (112 BPM), pop |
| 3.85–4.55 | | Logo naik ke atas, **cawan Orange Blast** naik dari bawah | Whoosh, clink ais |
| 4.30–4.75 | | Pil **MENU BARU**, kemudian **ORANGE BLAST** (merah, slam) | Hit |
| 5.00–6.30 | | **"MASAM MANIS, SEGAR SAMPAI HUJUNG TEGUKAN!"** + garisan, titisan jus naik | Swish |
| 6.30–6.85 | Transisi | Whip-blur | Whoosh |
| 6.60–7.10 | **Papan bento** | 4 kad 3D tersusun (header merah, kalendar oren, kad acara putih, peta biru) | Pop ×4, groove lebih ringan |
| 7.20–9.85 | **Kalendar** | Push-in, **NOVEMBER 2026** (I S R K J S A), lajur **Sabtu** menyala, **21** jadi bulatan hijau-limau bercahaya + gelombang, pil **SABTU · 21 NOVEMBER 2026** | Tick, **chime + shimmer** |
| 9.85–11.90 | **2 acara** | Arc ke kad: **JUMPA KAMI DI**, logo HTK 26 + **HARI TERBUKA ASRAMA**, logo IPG Perlis 10s + **PIALA PENGARAH RAGBI**, 21 NOVEMBER 2026 | Pop ×2, shimmer |
| 11.90–14.10 | **Peta** | Jalan muncul, **laluan oren dilukis**, **pin merah jatuh**, label **LOKASI · IPG KAMPUS PERLIS** | Riser, pop + ping |
| 14.10–15.00 | | Pull-out ke papan penuh, header: logo PERAH LAB + **JUMPA KAMI DI SINI!** | Whoosh, riser |
| 15.30–20.00 | **Kad penutup** | Logo PERAH LAB, **@PERAHLAB**, **MASAM MANIS, SEGAR SAMPAI HUJUNG TEGUKAN!**, kotak info (**21 NOVEMBER 2026 · SABTU / HARI TERBUKA ASRAMA & PIALA PENGARAH RAGBI / IPG KAMPUS PERLIS**), cawan besar, oren & ais terapung | Groove penuh, splash, hit, kord akhir |

## 4. Semakan fakta
- Maklumat yang dipaparkan hanya diambil daripada bahan anda: PERAH LAB, MENU BARU, ORANGE BLAST, tagline poster, @PERAHLAB, HARI TERBUKA ASRAMA, PIALA PENGARAH RAGBI, 21 NOVEMBER 2026 (SABTU), IPG KAMPUS PERLIS.
- Copy tambahan yang saya tulis: **"HAUS?"**, **"JUMPA KAMI DI"**, **"JUMPA KAMI DI SINI!"**, dan label **"LOKASI"**. Ini ayat promosi, bukan fakta acara. Boleh ditukar.
- **Tiada harga, nombor gerai, waktu jualan atau promosi** dipaparkan, kerana tiada dalam bahan. Jika ada, ia boleh ditambah (cadangan: pada kad penutup).
- Kalendar: 1 Nov 2026 = Ahad, jadi 21 Nov jatuh pada **Sabtu** ✔.
- **Andaian:** kedua-dua acara berlangsung pada **21 November 2026** di **IPG Kampus Perlis** (berdasarkan brief asal). Sila sahkan.

## 5. Teknik
Three.js (WebGL): stadium dengan lampu sorot & sinar volumetrik, buah oren 3D prosedural (kulit berbintik, hirisan ulas), kiub ais lut sinar, kad bento 3D (gaya video rujukan), bloom & tone mapping. Teks tajuk menggunakan HTML/CSS di atas kanvas supaya tajam. Muzik pop ceria 112 BPM dan semua SFX disintesis sendiri (`audio.py`), jadi bebas hak cipta. Render deterministik frame-demi-frame (`render.cjs`).
