# Laporan Analisis Frame-by-Frame — Video "Hari Anugerah Kecemerlangan" (3D Bento Card Motion)

> Fail sumber: `ScreenRecording_11-19-2026_21-27-40_1.mov`
> Kaedah: semua 737 frame rakaman dinyahkod; perbezaan piksel dikira antara **setiap** frame berturutan (kawasan video sahaja, overlay aplikasi dibuang) untuk mengesan fasa pergerakan, kemudian frame diperiksa secara visual pada sela 0.075–0.17 s (lebih rapat semasa pergerakan pantas). Helaian rujukan (contact sheet) bertimestamp ada dalam folder `analisis/rujukan/`.
> Nilai yang ditanda **(anggaran)** ialah inferens daripada imej 2D — tidak boleh diukur secara mutlak.

---

## A. VIDEO TECHNICAL BREAKDOWN

### A1. Data fail rakaman

| Perkara | Nilai |
|---|---|
| Jenis fail | Rakaman skrin iPhone (.mov, HEVC + AAC) |
| Resolusi rakaman | 1170 × 2532 (portrait) |
| Tempoh rakaman | 16.07 s |
| Kadar frame | Timebase 60 fps, kadar sebenar berubah (VFR), purata ≈ 44.8 fps, 737 frame |
| Kadar frame video asal (dalam aplikasi) | **≈ 30 fps** — frame rakaman berselang-seli "sama / berubah", menunjukkan setiap frame sumber dipaparkan 2× |
| Audio | Ada (mean −15.5 dB, peak −1.1 dB) — kemungkinan muzik latar; tidak dianalisis kerana skop visual |
| Kawasan video sebenar | Kira-kira 1170 × 2080 px bermula y ≈ 225 px → nisbah **9:16** (sasaran output: 1080 × 1920) |

### A2. Struktur LOOP — penemuan penting

Rakaman **tidak bermula pada awal video asal**. Video asal sedang dimainkan secara berulang (loop) dalam aplikasi:

| Timestamp rakaman | Frame rakaman (#, timebase 60) | Peristiwa |
|---|---|---|
| 0.000 – 0.200 s | #0 – #11 | Hujung loop sebelumnya — komposisi akhir lengkap (bar kemajuan pemain hampir penuh) |
| **0.217 s** | **#12** | **POTONGAN KERAS (hard cut)** → latar kosong. Ini permulaan video asal (T = 0) |
| 0.217 – 15.268 s | #12 – #688 | Satu kitaran penuh video asal |
| **15.285 s** | **#689** | **Potongan keras kedua** → latar kosong, loop bermula semula |
| 15.285 – 16.07 s | #689 – #736 | Permulaan kitaran kedua (identik dengan 0.217 – 1.0 s) |

➡ **Tempoh video asal ≈ 15.07 s (≈ 452 frame @30 fps).**
➡ Dalam laporan ini: **"Rak"** = timestamp dalam fail rakaman; **"T"** = masa dalam video asal (`T = Rak − 0.217`). Untuk membina semula, gunakan **T**.
➡ Frame terakhir video asal = komposisi penuh; frame pertama = latar kosong. Peralihan loop ialah potongan terus (tiada fade) — secara visual ia berfungsi sebagai "reset".

### A3. Elemen overlay (BUKAN sebahagian video) — mesti diabaikan

| Elemen | Lokasi | Bukti ia overlay |
|---|---|---|
| Jalur hitam atas & bawah | y 0–225 px dan y > 2305 px | Di luar kawasan 9:16 |
| Butang "X" (tutup) | Kiri atas | UI pemain aplikasi media sosial |
| Butang bulat kelabu bercincin | Kanan atas | Butang terapung sistem iOS (AssistiveTouch). Ia **lut sinar** — bertukar kebiruan apabila kad biru berada di bawahnya (cth. Rak 2.93–4.6 s), membuktikan ia bukan objek dalam video |
| Butang pause, bar scrubber, ikon pembesar suara | Bawah kawasan video | Kawalan pemain; bar scrubber malap/terang mengikut sentuhan |
| Baris interaksi ♥ 312 · 💬 25 · 🔁 89 · ➤ 63 | Bawah sekali | UI aplikasi (gaya Threads/Instagram) |

---

## B. FRAME-BY-FRAME BREAKDOWN

**Graf tenaga pergerakan** (purata beza piksel antara frame berturutan, setiap 0.1 s; nilai tinggi = pergerakan kamera besar):

```
Rak   T      Tenaga  Fasa
0.2  0.0    ███████ (cut)   Potongan loop
0.4–1.7 0.2–1.5  ▂▂▃▂▂▃▅▂     Kad muncul satu demi satu (staggered build)
2.2–3.0 2.0–2.8  ▃▅▇██▇       Kamera push-in ke Kad Kalendar
3.0–4.6 2.8–4.4  ▂▂▂▂▁▁       Isi kalendar + float perlahan
4.7–5.4 4.5–5.2  ▅█▆▆▅▆▅▃     Kamera bergerak ke Kad Statistik (2 bonggol: tarik-keluar → tolak-masuk)
5.4–6.6 5.2–6.4  ▃▃▂▂▂▂▂▂     Kaunter 29%→100% + bar
6.7–7.4 6.5–7.2  ▅▇███▇▅      Kamera ke Kad Logo (pergerakan terbesar)
7.4–8.6 7.2–8.4  ▂▂▂▂▂▁▁      Kilauan logo + float
8.7–9.4 8.5–9.2  ▅████▇▆▄     Kamera ke Kad Peta
9.5–10.6 9.3–10.4 ▁▂▂▂▂▂       Laluan dilukis + pin jatuh
10.7–11.4 10.5–11.2 ▅▇████▆   Kamera ke Kad Perasmi
11.4–12.7 11.2–12.5 ▂▁▁▁▁▁    Teks perasmi + hold
12.8–14.0 12.6–13.8 ▄▆█▆▆▆▅▄▄▂ Pull-out panjang ke overview
14.0–15.27 13.8–15.05 ▁        Hold akhir (hampir statik)
15.285 15.07      ███ (cut)    Loop semula
```

### B1. Jadual frame-by-frame

Lajur: **#** = frame rakaman (timebase 60); **F30** = anggaran frame video asal @30 fps. Kedudukan diberi dalam peratus lebar (W) / tinggi (H) kawasan video 9:16. Untuk fasa "hold" yang hampir statik, frame dikumpulkan dalam julat (semua frame dalam julat telah diperiksa dan tidak menunjukkan perubahan selain yang dicatat).

#### Fasa 0 — Hujung loop sebelumnya
| # | Rak (s) | T | Objek kelihatan | Kedudukan / saiz / perspektif | Pergerakan | Perubahan vs frame sebelum | Jenis animasi | Kamera | Kesan & cahaya |
|---|---|---|---|---|---|---|---|---|---|
| 0–11 | 0.000–0.200 | (≈15.0) | Komposisi lengkap: header + 6 kad berisi | Papan di tengah, lebar ≈ 66% W di atas → ≈ 85% W di bawah (trapezium: atas lebih sempit = condong ke belakang); papan berputar ≈ −3° (naik ke kanan) | Tiada | Tiada | Hold | Statik | Latar kelabu radial; bayang lembut di bawah setiap kad |
| 12 | 0.217 | 0.00 (F0) | **Latar kosong sahaja** | — | — | Semua kad hilang serta-merta | Hard cut (loop) | — | Latar: pusat #DEDEDE → tepi #B6B6B6 (vignette radial) |

#### Fasa 1 — Pembinaan papan (Staggered Build) · T 0.00–2.00
| # | Rak (s) | T | F30 | Objek kelihatan | Kedudukan / saiz / perspektif | Pergerakan | Perubahan vs frame sebelum | Jenis animasi | Kamera | Kesan & cahaya |
|---|---|---|---|---|---|---|---|---|---|---|
| 12–20 | 0.22–0.33 | 0.00–0.12 | 0–3 | Latar kosong | — | — | Tiada | — | Statik (sudut overview) | Vignette |
| 21–23 | 0.35–0.38 | 0.13–0.17 | 4–5 | **Header slab** (biru, tiada teks) muncul | Atas-tengah, y ≈ 7–9% H; lebih kecil & sedikit lebih tinggi daripada posisi akhir | Turun & membesar ke posisi | Muncul pada ~40% opacity, berwarna biru pudar keabuan | Fade-in + scale-up (≈0.85→1, anggaran) + translate-Y kecil | Statik | Belum ada bayang penuh |
| 24–30 | 0.40–0.50 | 0.18–0.28 | 6–8 | Header slab | Mencapai posisi akhir: x 22–76% W, y 9–14% H | Settle | Opacity → 100%, warna biru tepu, bayang muncul di bawah | Ease-out | Statik | Gradien biru (terang kiri-atas → gelap kanan-bawah) |
| 31–35 | 0.52–0.58 | 0.30–0.37 | 9–11 | Header sahaja | Tetap | Tiada | — | Hold | Statik | — |
| 36–40 | 0.60–0.67 | 0.38–0.45 | 11–14 | **Kad Kalendar** (biru kosong) | Kiri, bawah header (x 21–45% W) | Muncul dari saiz lebih kecil | Kad separa lut sinar, biru pudar | Fade + scale (staggered #2) | Statik | — |
| 41–47 | 0.68–0.78 | 0.47–0.57 | 14–17 | Header + Kalendar | Kalendar di posisi akhir | Settle | Opacity penuh + bayang | Ease-out | Statik | Bayang lembut ke bawah |
| 48–52 | 0.80–0.87 | 0.58–0.65 | 17–20 | **Kad Statistik** (putih kosong) | Kanan, bawah header (x 48–75% W) | Muncul | Kelabu lut sinar pada mulanya | Fade + scale (staggered #3) | Statik | — |
| 53–60 | 0.88–1.00 | 0.67–0.78 | 20–23 | Kad Statistik | Posisi akhir | Settle | Putih penuh (#F8F8F8), bayang | Ease-out | Statik | Sorotan putih lembut di tepi atas |
| 61–65 | 1.02–1.08 | 0.80–0.87 | 24–26 | 3 objek | Tetap | Tiada | — | Hold | Statik | — |
| 66–72 | 1.10–1.20 | 0.88–0.98 | 26–29 | **Kad Logo** (putih kosong) | Kiri, baris ke-2 (x 15–40% W) | Muncul | Kelabu lut sinar → putih | Fade + scale (staggered #4) | Statik | — |
| 73–78 | 1.22–1.30 | 1.00–1.08 | 30–32 | Kad Logo | Posisi akhir | Settle | Opacity penuh | Ease-out | Statik | — |
| 79–84 | 1.32–1.40 | 1.10–1.18 | 33–35 | **Kad Peta** (biru, tinggi) | Kanan, merangkumi baris 2 & 3 (x 47–78% W) | Muncul | Biru pudar lut sinar | Fade + scale (staggered #5) | Statik | — |
| 85–90 | 1.42–1.50 | 1.20–1.28 | 36–38 | Kad Peta | Posisi akhir | Settle | Biru tepu + bayang | Ease-out | Statik | — |
| 91–96 | 1.52–1.60 | 1.30–1.38 | 39–41 | **Kad Perasmi** (putih, lebar rendah) | Kiri-bawah (x 12–40% W) | Muncul | Kelabu pudar | Fade + scale (staggered #6) | Statik | — |
| 97–102 | 1.62–1.70 | 1.40–1.48 | 42–44 | Kad Perasmi | Posisi akhir | Settle | Putih penuh | Ease-out | Statik | — |
| 103–132 | 1.72–2.20 | 1.50–1.98 | 45–59 | Papan lengkap (semua kad **kosong tanpa kandungan**) | Grid 2 lajur lengkap | Hampir statik | Perubahan sangat kecil (beza piksel 0.4–0.6) | Hold | Mungkin drift sangat perlahan **(anggaran)** | — |

> **Nota:** Selang (stagger) antara kad ≈ **0.20 s**, tempoh setiap kemasukan ≈ **0.30–0.35 s**, urutan: Header → Kalendar → Statistik → Logo → Peta → Perasmi (atas→bawah, kiri→kanan). Semua kad masuk **kosong**; kandungan hanya muncul apabila kamera fokus pada kad tersebut.

#### Fasa 2 — Kamera push-in ke Kad Kalendar · T 2.00–2.80
| # | Rak (s) | T | F30 | Objek kelihatan | Kedudukan / saiz / perspektif | Pergerakan | Perubahan vs frame sebelum | Jenis animasi | Kamera | Kesan & cahaya |
|---|---|---|---|---|---|---|---|---|---|---|
| 126–131 | 2.10–2.18 | 1.88–1.97 | 56–59 | Papan penuh | Seperti overview | Mula bergerak | Sangat kecil | — | Mula dolly-in (ease-in) | — |
| 136 | 2.27 | 2.05 | 62 | Papan penuh | Papan sedikit membesar & turun | Zoom-in perlahan | Kecil | — | Dolly-in + tilt (sudut condong berkurang) | — |
| 141 | 2.35 | 2.13 | 64 | Papan | Membesar ±10% | Zoom-in | Sederhana | — | Dolly-in dipercepat | — |
| 146 | 2.43 | 2.22 | 67 | Papan | Membesar ±20%, kad bawah keluar bingkai | Zoom-in | Jelas | — | Dolly-in | — |
| 151 | 2.52 | 2.30 | 69 | Papan | Kad Peta & Perasmi mula keluar bingkai kanan/bawah | Zoom-in | Besar | — | Dolly-in + pan sedikit ke kiri | — |
| 156 | 2.60 | 2.38 | 71 | Header, Kalendar, Statistik, Logo | Kalendar ≈ 45% W; **"November 2026" & titik emas muncul samar** | Zoom-in | Besar | Fade-in teks (kandungan Kalendar) | Dolly-in | Teks pudar |
| 161 | 2.68 | 2.47 | 74 | Sama | Kalendar ≈ 55% W; garis pemisah muncul | Zoom-in | Besar | Fade-in | Dolly-in | — |
| 166 | 2.77 | 2.55 | 76 | Sama | Kalendar ≈ 70% W; **baris hari I S R K J S A** muncul pudar | Zoom-in | Sangat besar | Fade-in | Dolly-in (kelajuan puncak) | — |
| 171 | 2.85 | 2.63 | 79 | Kalendar mendominasi | Kalendar ≈ 72% W, x 5–77%; tepi kanan surut (perspektif rotateY kecil) | Zoom-in | Sangat besar | — | Dolly-in + orbit kecil | — |
| 176 | 2.93 | 2.72 | 81 | Kalendar | ≈ 90% W; **nombor 1–14 muncul**, 9–13 masih pudar | Settle | Besar | Fade-in nombor berperingkat (stagger baris demi baris) | Deceleration | — |
| 181 | 3.02 | 2.80 | 84 | Kalendar | ≈ 93% W; 15–30 sedang muncul (pudar) | Settle | Sederhana | Fade-in stagger | Hampir berhenti | — |

#### Fasa 3 — Fokus Kalendar · T 2.80–4.43
| # | Rak (s) | T | F30 | Objek / kandungan | Kedudukan | Pergerakan | Perubahan vs sebelum | Jenis animasi | Kamera | Kesan |
|---|---|---|---|---|---|---|---|---|---|---|
| 180 | 3.00 | 2.78 | 83 | Kalendar: 23–28 masih pudar | Kalendar x 3–97% W, y 25–68% H | — | Nombor terakhir masih fade | Fade-in | Float perlahan | — |
| 189 | 3.15 | 2.93 | 88 | Semua nombor kelihatan; **bulatan emas kecil muncul pada "24"** | — | — | Badge baru | **Pop-in (scale 0 → 1)** | Float | Bulatan emas |
| 198 | 3.30 | 3.08 | 92 | Badge "24" saiz penuh (emas, nombor gelap tebal) | — | — | Badge membesar penuh | Pop + overshoot kecil **(anggaran)** | Float | Glow emas lembut |
| 207–216 | 3.45–3.60 | 3.23–3.38 | 97–101 | 24 aktif; 25 belum | — | — | Tiada | Hold | Float | — |
| 225 | 3.75 | 3.53 | 106 | **Badge "25" muncul** | — | — | Badge kedua | Pop-in (stagger ≈0.45 s selepas 24) | Float | — |
| 234–252 | 3.90–4.20 | 3.68–3.98 | 110–119 | 24 & 25 aktif | Kalendar beranjak sedikit | Drift sangat perlahan | Sangat kecil | Hold | **Float/drift perlahan** (beza 0.3–0.5) | — |
| 261 | 4.35 | 4.13 | 124 | Badge 24 & 25 menunjukkan **sorotan putih** di sisi kiri | — | — | Sorotan | **Shine/glint sweep** pada badge **(anggaran: kilauan lalu)** | Float | Specular highlight |
| 270–276 | 4.50–4.60 | 4.28–4.38 | 128–131 | Kalendar lengkap | — | — | Kecil | Hold | Mula bergerak | — |

#### Fasa 4 — Peralihan ke Kad Statistik · T 4.43–5.13
| # | Rak (s) | T | F30 | Objek | Kedudukan / saiz | Pergerakan | Perubahan | Animasi | Kamera | Kesan |
|---|---|---|---|---|---|---|---|---|---|---|
| 276 | 4.60 | 4.38 | 131 | Kalendar penuh skrin | ≈ 95% W | — | — | — | Mula | — |
| 281 | 4.68 | 4.47 | 134 | Kalendar | ≈ 88% W | Mengecil | Besar | — | **Pull-back (dolly-out)** ease-in | — |
| 286 | 4.77 | 4.55 | 137 | Kalendar + tepi kad Statistik | Kalendar ≈ 75% W | Mengecil + anjak kiri | Sangat besar | — | Dolly-out + truck kanan | — |
| 291 | 4.85 | 4.63 | 139 | Header, Kalendar (x 30–72%), Statistik kosong | Kalendar ≈ 60% W | — | Sangat besar | — | Dolly-out maksimum (≈1.6× overview, anggaran) + truck kanan | — |
| 296 | 4.93 | 4.72 | 142 | Kalendar kiri (keluar bingkai), Statistik di tengah | Statistik ≈ 40% W | Anjak kiri | Besar | — | Truck kanan + mula dolly-in | — |
| 301 | 5.02 | 4.80 | 144 | Statistik ≈ 45% W | — | — | Besar | — | Dolly-in | — |
| 306 | 5.10 | 4.88 | 147 | Statistik ≈ 60% W; **ikon trofi muncul samar** | — | — | Besar | Fade + scale ikon | Dolly-in | — |
| 311 | 5.18 | 4.97 | 149 | Statistik ≈ 70% W; trofi dalam bulatan emas pucat; **"Anugerah"** pudar | — | — | Sederhana | Fade-in teks | Dolly-in | — |
| 316 | 5.27 | 5.05 | 152 | ≈ 80% W; "Anugerah" jelas, "Kecemerlangan" pudar; **"29%"** + bar mula | — | — | Sederhana | Fade-in stagger | Deceleration | — |
| 321 | 5.35 | 5.13 | 154 | ≈ 85% W; "36%" | Statistik x 8–92% W | — | — | Kaunter | Settle | — |

#### Fasa 5 — Kaunter & bar kemajuan · T 5.13–6.51
| # | Rak (s) | T | F30 | Nilai kaunter | Bar kemajuan | Animasi | Kamera | Kesan |
|---|---|---|---|---|---|---|---|---|
| ≈315 | 5.25 | 5.03 | 151 | 29% | ≈29% | Count-up bermula | Settle | Bar emas, trek kelabu |
| 324 | 5.40 | 5.18 | 155 | 48% | ≈48% | Count-up | Float | — |
| 331 | 5.51 | 5.29 | 159 | 59% | ≈59% | Count-up | Float | — |
| 337 | 5.62 | 5.40 | 162 | 76% | ≈76% | Count-up | Float | — |
| 344 | 5.73 | 5.51 | 165 | 85% | ≈85% | Count-up (melambat) | Float | — |
| 350 | 5.84 | 5.62 | 169 | 92% | ≈92% | Ease-out | Float | — |
| 357 | 5.94 | 5.73 | 172 | 96% | ≈96% | Ease-out | Float | — |
| 363 | 6.05 | 5.84 | 175 | 99% | ≈99% | Ease-out | Float | — |
| 370 | 6.16 | 5.94 | 178 | **100%** | penuh | Selesai | Float | — |
| 376–383 | 6.27–6.38 | 6.05–6.16 | 182–185 | 100% | penuh | Hold | Float | — |
| 389 | 6.49 | 6.27 | 188 | 100% | **Jalur cahaya putih di hujung kiri bar** | **Shine sweep** kiri→kanan | Float | Specular |
| 396–405 | 6.60–6.75 | 6.38–6.53 | 191–196 | 100% | Kilauan bergerak ke tengah→kanan | Shine sweep (≈0.35 s) | Mula bergerak | — |

> Kaunter dan bar **disegerakkan** (nilai bar = nilai nombor). Lengkung: ease-out (cubic/quart), tempoh ≈ 0.9 s (T 5.03→5.94).

#### Fasa 6 — Peralihan ke Kad Logo · T 6.51–7.15
| # | Rak (s) | T | F30 | Objek | Kedudukan / saiz | Animasi | Kamera | Kesan |
|---|---|---|---|---|---|---|---|---|
| 396 | 6.60 | 6.38 | 191 | Statistik penuh | ≈85% W | — | Statik | Shine pada bar |
| 405 | 6.75 | 6.53 | 196 | Statistik ≈ 75% W, kalendar tepi kiri | — | — | Dolly-out bermula | — |
| 410 | 6.83 | 6.61 | 198 | Statistik ≈ 62% W, Peta (kosong) muncul bawah | — | — | Dolly-out + tilt-down | — |
| 414 | 6.90 | 6.68 | 200 | Kalendar, Statistik, Logo (kosong), Peta | Statistik ≈ 50% W | — | Dolly-out maksimum + pan ke kiri-bawah | — |
| 419 | 6.98 | 6.76 | 203 | 4 kad; Kad Logo di kiri-bawah | — | — | Pan/truck kiri-bawah | — |
| 423 | 7.05 | 6.83 | 205 | **Logo muncul kabur & pudar** dalam kad | Logo card ≈ 45% W | **Blur → tajam + fade-in** | Dolly-in | — |
| 428 | 7.13 | 6.91 | 207 | Logo separa jelas | ≈ 60% W | Defocus → focus | Dolly-in | — |
| 432 | 7.20 | 6.98 | 209 | Logo jelas | ≈ 72% W | Selesai | Dolly-in | — |
| 437 | 7.28 | 7.06 | 212 | Logo, kalendar di atas | ≈ 80% W | — | Deceleration | — |
| 441–446 | 7.35–7.43 | 7.13–7.21 | 214–216 | Logo card x 2–98% W | ≈ 90% W | — | Settle | — |

#### Fasa 7 — Fokus Logo · T 7.15–8.50
| # | Rak (s) | T | Kandungan | Animasi | Kamera | Kesan |
|---|---|---|---|---|---|---|
| 444–450 | 7.40–7.51 | 7.18–7.29 | Logo statik | Hold | Float | Kad condong (penjuru kanan-atas lebih tinggi ≈ −4°) |
| 457 | 7.62 | 7.40 | Kilauan putih di penjuru kiri-atas perisai | **Glare/shine sweep diagonal** mula | Float | Specular |
| 464 | 7.73 | 7.51 | Kilauan di tengah perisai | Sweep | Float | — |
| 470 | 7.84 | 7.62 | Kilauan di tengah-kanan / bawah | Sweep | Float | — |
| 477 | 7.94 | 7.73 | Kilauan di riben bawah, memudar | Sweep tamat | Float | — |
| 483–515 | 8.05–8.60 | 7.83–8.38 | Logo statik | Hold | Float sangat perlahan | — |

#### Fasa 8 — Peralihan ke Kad Peta · T 8.50–9.20
| # | Rak (s) | T | F30 | Objek | Kedudukan / saiz | Animasi | Kamera |
|---|---|---|---|---|---|---|---|
| 516 | 8.60 | 8.38 | 251 | Logo penuh | ≈ 95% W | — | Statik |
| 525 | 8.75 | 8.53 | 256 | Kalendar, Statistik, Logo, Perasmi | Logo ≈ 70% W | — | Dolly-out + pan kanan |
| 530 | 8.83 | 8.61 | 258 | + Peta (kosong) muncul kanan | Logo ≈ 55% W | — | Dolly-out |
| 535 | 8.90 | 8.68 | 261 | 5 kad kelihatan | — | — | Dolly-out maksimum + truck kanan |
| 539 | 8.98 | 8.76 | 263 | **Garis jalan biru muda muncul** dalam Peta | Peta ≈ 40% W | Fade-in grid jalan | Truck kanan + dolly-in |
| 543 | 9.05 | 8.83 | 265 | Peta ≈ 45% W, jalur pantai/sungai (biru lebih terang) di tepi kanan | — | Fade-in | Dolly-in |
| 548 | 9.13 | 8.91 | 267 | Peta ≈ 52% W | — | — | Dolly-in |
| 552 | 9.20 | 8.98 | 269 | Peta ≈ 58% W | — | — | Dolly-in |
| 557 | 9.28 | 9.06 | 272 | Peta ≈ 62% W; **titik permulaan putih (kiri-bawah)** muncul | — | Pop titik | Deceleration |

#### Fasa 9 — Laluan peta & pin · T 9.06–10.50
| # | Rak (s) | T | Kandungan | Animasi | Kamera | Kesan |
|---|---|---|---|---|---|---|
| 561 | 9.35 | 9.13 | Garisan emas pendek dari titik permulaan | **Path drawing (stroke reveal)** | Settle | — |
| 566 | 9.43 | 9.21 | Laluan ≈ 10% | Path draw | Settle | — |
| 571 | 9.51 | 9.29 | Laluan ≈ 25% | Path draw | Float | — |
| 577 | 9.62 | 9.40 | Laluan ≈ 40%, membelok ke atas | Path draw | Float | — |
| 584 | 9.73 | 9.51 | Laluan ≈ 55%; **"Dewan Sri Kuala"** muncul pudar | Path draw + fade-in teks | Float | — |
| 590 | 9.84 | 9.62 | Laluan ≈ 70%; "Dewan Sri Kuala" jelas; subtajuk pudar | Path draw + fade-in | Float | — |
| 597 | 9.94 | 9.73 | Laluan ≈ 85% (belok kiri di atas); "SK Kuala Dungun" | Path draw | Float | — |
| 603 | 10.05 | 9.84 | Laluan ≈ 100% sampai ke atas | Path draw tamat | Float | — |
| 610 | 10.16 | 9.94 | **Pin muncul kelabu/lut sinar** di hujung laluan | **Pin drop** (fade + jatuh dari atas, anggaran) | Float | — |
| 616 | 10.27 | 10.05 | Pin emas penuh | Pin settle | Float | — |
| 623 | 10.38 | 10.16 | **Cincin elips** di bawah pin | **Ripple/pulse** | Float | — |
| 629–636 | 10.49–10.60 | 10.27–10.38 | Cincin membesar & pudar | Pulse tamat | Mula bergerak | — |

#### Fasa 10 — Peralihan ke Kad Perasmi · T 10.50–11.13
| # | Rak (s) | T | F30 | Objek | Animasi | Kamera |
|---|---|---|---|---|---|---|
| 636 | 10.60 | 10.38 | 311 | Peta penuh (≈ 85% W) | — | Statik |
| 645 | 10.75 | 10.53 | 316 | Peta ≈ 75% W, Statistik atas | — | Dolly-out |
| 650 | 10.83 | 10.61 | 318 | Peta ≈ 62% W | — | Dolly-out + pan kiri-bawah |
| 654 | 10.90 | 10.68 | 320 | Logo, Peta, Perasmi (kosong) | — | Dolly-out maksimum |
| 659 | 10.98 | 10.76 | 323 | Peta di kanan; **bulatan foto perasmi** muncul kecil & kabur | Scale-in + blur → tajam | Truck kiri + dolly-in |
| 663 | 11.05 | 10.83 | 325 | 4 kad; bulatan masih kecil | Scale-in | Dolly-in |
| 668 | 11.13 | 10.91 | 327 | Logo ≈ 55% W; bulatan krim membesar | Scale-in | Dolly-in |
| 672 | 11.20 | 10.98 | 329 | Bulatan dengan cincin emas jelas | Scale-in + glow | Dolly-in |
| 677 | 11.28 | 11.06 | 332 | **"Dirasmikan oleh"** pudar | Fade-in | Deceleration |
| 681 | 11.35 | 11.13 | 334 | Garis emas pendek di bawah "Dirasmikan oleh" | Line grow (scaleX) | Settle |

#### Fasa 11 — Fokus Perasmi · T 11.13–12.60
| # | Rak (s) | T | Kandungan | Animasi | Kamera |
|---|---|---|---|---|---|
| 686 | 11.43 | 11.21 | **"Pengurus"** muncul pudar (ungu-kelabu) | Fade-in | Float |
| 693 | 11.47 | 11.25 | "Pengurus" separa | Fade-in | Float |
| 700 | 11.58 | 11.36 | "Pengurus" biru tua penuh; **"PTPTN Dungun"** pudar | Fade-in stagger | Float |
| 707 | 11.70 | 11.48 | Semua teks penuh | Selesai | Float |
| 714–758 | 11.82–12.63 | 11.60–12.41 | Kad statik; foto **kosong** (placeholder) dengan cincin emas bercahaya | Hold | Float sangat perlahan (beza ≈0.4) |

#### Fasa 12 — Pull-out ke overview · T 12.60–13.80
| # | Rak (s) | T | F30 | Objek | Kedudukan / saiz | Animasi | Kamera |
|---|---|---|---|---|---|---|---|
| 756 | 12.60 | 12.38 | 371 | Perasmi + Logo | Perasmi ≈ 100% W | — | Statik |
| 764 | 12.73 | 12.52 | 375 | Sama | ≈ 95% W | — | Dolly-out bermula |
| 772 | 12.87 | 12.65 | 380 | + Peta di kanan | ≈ 85% W | — | Dolly-out |
| 780 | 13.00 | 12.78 | 383 | Kalendar, Statistik, Logo, Perasmi, Peta | Perasmi ≈ 70% W | — | Dolly-out + tilt-up |
| 788 | 13.13 | 12.92 | 388 | Semua kad kecuali header penuh | Board ≈ 90% W | — | Dolly-out |
| 796 | 13.27 | 13.05 | 392 | **Header kelihatan; teks "Hari Anugerah Kecemerlangan" mula muncul (pudar)** | Board ≈ 80% W | Fade-in tajuk | Dolly-out |
| 804 | 13.40 | 13.18 | 395 | Tajuk jelas; "SK Kuala Dungun" pudar | ≈ 78% W | Fade-in subtajuk | Dolly-out melambat |
| 812 | 13.53 | 13.32 | 400 | Semua jelas | ≈ 76% W | — | Ease-out |
| 820–844 | 13.67–14.07 | 13.45–13.85 | 404–416 | Board ke posisi overview akhir | ≈ 74% W | — | Settle (ease-out panjang) |

#### Fasa 13 — Hold akhir & loop · T 13.80–15.07
| # | Rak (s) | T | Kandungan | Animasi | Kamera |
|---|---|---|---|---|---|
| 844–866 | 14.07–14.43 | 13.85–14.22 | Komposisi lengkap | Settle mikro (beza 0.1–0.3) | Hampir statik |
| 866–916 | 14.43–15.27 | 14.22–15.05 | Komposisi lengkap (sama seperti frame #0) | Hold mutlak | Statik |
| 917 (#689 dalam indeks frame sebenar) | 15.285 | 15.07 → 0 | Latar kosong | **Hard cut / loop** | — |
| — | 15.29–16.07 | 0.00–0.78 | Ulangan Fasa 1 (header 15.55, kalendar 15.72, statistik 15.90) | Sama seperti 0.22–1.0 s | — |

> Nota indeks: rakaman adalah VFR, jadi "#" dalam jadual dikira sebagai `round(Rak × 60)` (posisi pada timebase 60). Indeks frame sebenar yang dinyahkod (737 frame) berbeza sedikit; contoh potongan loop: indeks sebenar #12 (0.217 s) dan #689 (15.285 s).

---

## C. 3D OBJECT BREAKDOWN

### C1. Susun atur akhir (overview) — grid "bento" 2 lajur

```
┌──────────────────────────────┐   ← HEADER SLAB (penuh lebar, rendah)
│   Hari Anugerah Kecemerlangan│
│        SK Kuala Dungun       │
└──────────────────────────────┘
┌─────────────┐ ┌──────────────┐
│ KALENDAR    │ │ STATISTIK    │   ← baris 1 (≈ segi empat sama)
│ (biru)      │ │ (putih)      │
└─────────────┘ └──────────────┘
┌─────────────┐ ┌──────────────┐
│ LOGO        │ │ PETA         │
│ (putih)     │ │ (biru,       │   ← kad Peta tinggi: merentas 2 baris
└─────────────┘ │  tinggi)     │
┌─────────────┐ │              │
│ PERASMI     │ │              │
│ (putih,     │ │              │
│  lebar)     │ │              │
└─────────────┘ └──────────────┘
```

Corak warna **papan dam (checkerboard)** biru/putih: Header biru → Kalendar biru / Statistik putih → Logo putih / Peta biru → Perasmi putih. Ini memberi irama visual.

Nisbah anggaran (unit = lebar papan 100):

| Kad | Lajur | Lebar | Tinggi | Nisbah |
|---|---|---|---|---|
| Header | Penuh | 100 | ≈ 22 | ≈ 4.5:1 |
| Kalendar | Kiri | ≈ 48 | ≈ 50 | ≈ 1:1.05 |
| Statistik | Kanan | ≈ 48 | ≈ 50 | ≈ 1:1.05 |
| Logo | Kiri | ≈ 48 | ≈ 48 | 1:1 |
| Perasmi | Kiri | ≈ 48 | ≈ 32 | ≈ 3:2 |
| Peta | Kanan | ≈ 48 | ≈ 84 | ≈ 1:1.75 |
| Jarak (gap) | — | ≈ 2.5–3 | — | — |

### C2. Bentuk 3D setiap kad
- **Slab bulat (rounded slab)** dengan ketebalan kecil (≈ 2–3% lebar kad, kelihatan sebagai tepi lebih cerah/gelap di sisi bawah apabila dekat — cth. Rak 7.4 s, 11.5 s).
- Jejari bucu ≈ 8–10% lebar kad (anggaran).
- Kad **terapung** di atas latar — bayang lembut (soft shadow) jatuh ke bawah, tidak bersentuhan dengan lantai.

### C3. Perspektif papan (overview)
Diukur daripada frame Rak 14.5 s (skrin 585 px lebar):
- Tepi atas header: lebar ≈ 378 px; tepi bawah papan: lebar ≈ 496 px → nisbah ≈ **0.76** → papan **condong ke belakang di bahagian atas** (rotateX positif).
- Paksi tengah atas (x≈293) = paksi tengah bawah (x≈293) → **rotateY ≈ 0°** pada overview.
- Tepi atas header cerun ≈ **−3°** (naik ke kanan); tepi bawah ≈ +0.7° → gabungan **rotateZ ≈ −1.5° hingga −2°** dengan rotateX.
- Anggaran: **rotateX ≈ 20–28°, rotateZ ≈ −2°, kamera FOV ≈ 35–45°** (anggaran).

### C4. Setiap objek — kemunculan, kandungan & animasi

| Objek | Muncul (T) | Kandungan & reka bentuk | Animasi kandungan (T) |
|---|---|---|---|
| **Latar** | 0.00 | Kelabu cerah, gradien radial (pusat #DEDEDE → tepi #B6B6B6), studio infinite/cyclorama, tiada tekstur | Statik sepanjang video |
| **Header slab** | 0.13–0.28 | Biru (gradien #0E3CB1 → #002073); tajuk 2 baris "Hari Anugerah / Kecemerlangan" emas tebal dengan bayang gelap; subtajuk "SK Kuala Dungun" putih kecil | Teks **hanya muncul semasa pull-out akhir**: tajuk 13.05–13.2, subtajuk 13.2–13.35 (fade-in) |
| **Kad Kalendar** | 0.38–0.57 | Biru; "November 2026" putih; titik emas kanan-atas; baris hari **I S R K J S A** (Isnin→Ahad); garis pemisah nipis; nombor putih ringan; 1 Nov jatuh pada Ahad (betul untuk 2026); **24 & 25 dalam bulatan emas** dengan nombor biru tua tebal | Kepala 2.38; hari 2.55; nombor fade berperingkat 2.72–2.95; badge 24 pop 2.93–3.08; badge 25 pop 3.38–3.53; glint ≈ 4.13 |
| **Kad Statistik** | 0.58–0.78 | Putih (#F8F8F8); ikon trofi emas dalam bulatan emas pucat; "Anugerah" (kelabu gelap) + "Kecemerlangan" (kecil kelabu); **"100%"** besar, berat nipis (light), biru tua; bar kemajuan emas bergradien atas trek kelabu; label "0" dan "100" kecil | Trofi 4.88; tajuk 4.97–5.05; kaunter 29→100% 5.03–5.94; shine bar 6.27–6.53 |
| **Kad Logo** | 0.88–1.08 | Putih; lencana sekolah 3D (perisai biru, obor, buku, riben emas "USAHA ITU JAYA", tulisan "SK KUALA DUNGUN") dengan bayang | Logo blur→tajam + fade 6.83–6.98; glare diagonal 7.40–7.73 |
| **Kad Peta** | 1.10–1.28 | Biru; rangkaian jalan garis biru muda nipis; jalur pantai/sungai biru lebih terang di sisi kanan; laluan emas; titik putih permulaan; pin lokasi emas; "Dewan Sri Kuala" putih + "SK Kuala Dungun" biru muda | Grid jalan 8.76–8.83; titik 9.06; laluan dilukis 9.13–9.84; label 9.51–9.73; pin drop 9.94–10.05; ripple 10.16–10.38 |
| **Kad Perasmi** | 1.30–1.48 | Putih lebar; bulatan foto **kosong** (krim/kelabu) dengan cincin emas + glow; "Dirasmikan oleh" kecil kelabu; garis emas pendek; **"Pengurus"** biru tua tebal; "PTPTN Dungun" kelabu | Bulatan scale+blur-in 10.76–10.98; label 11.06; garis 11.13; "Pengurus" 11.21–11.36; "PTPTN Dungun" 11.36–11.48 |

### C5. Bayang-bayang & pantulan cahaya
- **Key light dari kiri-atas** (anggaran): permukaan biru lebih cerah di kiri-atas, gelap di kanan-bawah; kad putih ada sorotan nipis di tepi atas.
- **Drop shadow lembut** di bawah setiap kad (offset ke bawah, blur besar, opacity rendah ≈ 15–25%).
- **Contact/ambient occlusion** gelap kecil di celah antara kad.
- **Specular sweeps** (kilauan bergerak) digunakan 3 kali: badge kalendar (≈4.1), bar kemajuan (6.27–6.53), logo (7.40–7.73).
- **Glow emas** pada badge kalendar dan cincin foto perasmi.

---

## D. CAMERA MOVEMENT BREAKDOWN

Pola utama: **"Overview → Fokus kad satu demi satu → Overview"**. Setiap peralihan antara kad ialah **gerakan lengkung (arc)**: *dolly-out → truck/pan → dolly-in*, bukan pan lurus. Ini nampak jelas daripada graf tenaga dengan bonggol berkembar (4.7 & 5.2 s Rak).

| # | T mula–tamat | Tempoh | Dari → Ke | Jenis pergerakan | Easing | Perincian |
|---|---|---|---|---|---|---|
| Cam 0 | 0.00–1.98 | 1.98 s | Overview | Statik (drift mikro, anggaran) | — | Papan lengkap ≈ 66–85% W |
| Cam 1 | 1.98–2.80 | 0.82 s | Overview → Kalendar | **Dolly-in** besar (≈ ×2.2 skala) + pan ke kiri-atas + **tilt mengurang** (papan kelihatan lebih frontal) + orbit kecil (tepi kanan kalendar surut) | Ease-in-out (lambat mula, laju 2.3–2.7, berhenti lembut) | Kalendar akhir ≈ 93–95% W |
| Cam 2 | 2.80–4.38 | 1.58 s | Kalendar | **Float/drift** perlahan | Linear | Pergerakan sangat kecil — memberi rasa "hidup" |
| Cam 3 | 4.43–5.13 | 0.70 s | Kalendar → Statistik | Dolly-out (≈ ×0.6) → **truck kanan** → dolly-in | Ease-in-out | Puncak zoom-out T≈4.63 |
| Cam 4 | 5.13–6.38 | 1.25 s | Statistik | Float | Linear | — |
| Cam 5 | 6.51–7.15 | 0.64 s | Statistik → Logo | Dolly-out → **pan/truck kiri-bawah (pedestal down)** → dolly-in | Ease-in-out | Pergerakan paling laju dalam video (puncak T≈6.9) |
| Cam 6 | 7.15–8.38 | 1.23 s | Logo | Float | Linear | Kad kelihatan condong ≈ −4° (roll) |
| Cam 7 | 8.50–9.20 | 0.70 s | Logo → Peta | Dolly-out → **truck kanan** → dolly-in | Ease-in-out | — |
| Cam 8 | 9.20–10.38 | 1.18 s | Peta | Float | Linear | — |
| Cam 9 | 10.50–11.13 | 0.63 s | Peta → Perasmi | Dolly-out → **truck kiri + pedestal down** → dolly-in | Ease-in-out | — |
| Cam 10 | 11.13–12.41 | 1.28 s | Perasmi | Float | Linear | Perasmi berada di separuh atas-tengah, ruang kosong di bawah |
| Cam 11 | 12.52–13.85 | ≈ 1.3 s | Perasmi → Overview | **Dolly-out panjang** + tilt-up + kembali ke sudut overview asal | Ease-out panjang (expo/quart) | Posisi akhir = posisi frame pertama (loop serasi) |
| Cam 12 | 13.85–15.07 | 1.2 s | Overview | Statik | — | Hold |

**Peralihan fokus** (focus shift) dibuat sepenuhnya oleh kamera + pemunculan kandungan, **bukan** oleh cut. Tiada jump cut dalam video selain potongan loop.

**Kedalaman medan (DoF):** semasa close-up, kad di tepi bingkai kelihatan sedikit lembut **(anggaran — mungkin DoF ringan atau hanya kesan resolusi rakaman)**. Kabur paling jelas ialah pada kandungan yang sedang fade-in (logo T 6.83, bulatan perasmi T 10.76) — itu **blur animasi kandungan**, bukan DoF kamera.

---

## E. ANIMATION & TRANSITION BREAKDOWN

| Jenis | Wujud? | Di mana (T) | Spesifikasi anggaran |
|---|---|---|---|
| **Staggered card animation** | ✅ | 0.13–1.48 | 6 kad, stagger 0.20 s, setiap satu 0.30–0.35 s |
| **Fade in** | ✅ | Kemasukan kad; semua teks; grid jalan | Opacity 0→1, 0.15–0.25 s |
| **Scale animation** | ✅ | Kemasukan kad (≈0.85→1); badge (0→1); bulatan perasmi | Ease-out / back-out kecil |
| **Blur-to-sharp reveal** | ✅ | Logo (6.83–6.98), bulatan perasmi (10.76–10.98) | Blur ≈ 10–20 px → 0 |
| **Count-up number** | ✅ | 5.03–5.94 | 29→100, ease-out |
| **Progress bar fill** | ✅ | 5.03–5.94 | Disegerak dengan nombor |
| **Path/stroke drawing** | ✅ | 9.13–9.84 | stroke-dashoffset, linear→ease-out |
| **Pin drop + ripple** | ✅ | 9.94–10.38 | Pin jatuh/fade, cincin elips membesar & pudar |
| **Line grow** | ✅ | 11.13 | Garis emas scaleX 0→1 |
| **Shine / glint sweep** | ✅ | ≈4.13, 6.27–6.53, 7.40–7.73 | Jalur gradien putih bergerak |
| **Floating (camera drift)** | ✅ | Setiap hold | Gerakan mikro perlahan |
| **Camera dolly / arc transitions** | ✅ | 5 peralihan | Lihat bahagian D |
| **Smooth sliding (kad bergerak sendiri)** | ❌ | — | Kad **tidak** bergeser posisi selepas tersusun; semua gerakan selepas T 1.5 ialah kamera |
| **3D card rotation (kad berputar individu)** | ❌ | — | Tiada flip/rotate kad individu; perubahan sudut datang daripada kamera |
| **Parallax** | ⚠️ separa | Semasa pergerakan kamera | Hanya parallax semula jadi perspektif 3D (semua kad pada satah sama, jadi parallax minimum) |
| **Morphing transition** | ❌ | — | Tiada |
| **Fade out / crossfade antara babak** | ❌ | — | Tiada; satu shot berterusan (one-take) |

**Bagaimana babak bertukar:** setiap babak = satu kad. Tamat babak ditandai oleh pemberhentian animasi kandungan (hold ≈ 0.4–1.2 s), kemudian kamera **zoom-out sedikit untuk menunjukkan konteks**, beralih, dan **zoom-in ke kad seterusnya**; kandungan kad baharu mula fade-in **semasa kamera masih tiba** (≈ 0.25–0.35 s sebelum kamera berhenti). Overlap ini yang menjadikan aliran terasa licin.

---

## F. VISUAL DESIGN BREAKDOWN

### F1. Palet warna (disampel daripada frame)

| Peranan | Hex (anggaran) | Penggunaan |
|---|---|---|
| Biru utama (terang) | `#0E3CB1` – `#03288A` | Kad biru, bahagian kiri-atas |
| Biru gelap | `#012684` – `#002073` | Kad biru, bahagian bawah/kanan |
| Biru tua teks | `#1B2F7A` – `#0A2380` | "100%", "Pengurus", nombor badge |
| Putih kad | `#F8F8F8` → `#F1F0F2` | Kad putih (gradien sangat halus) |
| Emas | ≈ `#F5B400` – `#FFC83A` | Tajuk header, badge, bar, laluan, pin, cincin |
| Emas pucat | ≈ `#FCEBB0` | Latar ikon trofi |
| Latar | `#DEDEDE` (pusat) → `#B6B6B6` (tepi) | Studio radial |
| Garis peta | biru muda ≈ `#7FA0E8` (lut sinar) | Jalan |
| Teks sekunder | kelabu ≈ `#8A8A8A` | Subtajuk |

Skema: **2 warna utama (biru royal + putih) + 1 aksen (emas)** atas latar neutral kelabu — konsisten dengan identiti sekolah.

### F2. Tipografi & hierarki
| Tahap | Contoh | Gaya (anggaran) |
|---|---|---|
| H1 | "Hari Anugerah Kecemerlangan" | Sans geometri ExtraBold/Black (gaya Poppins/Montserrat), emas, bayang gelap, 2 baris tengah |
| Display number | "100%" | Sans geometri **Light/Thin**, sangat besar, biru tua — kontras berat yang moden |
| H2 | "November 2026", "Dewan Sri Kuala", "Pengurus" | Sans Medium–SemiBold |
| Label | "Anugerah", "Dirasmikan oleh" | Regular, kelabu/gelap |
| Caption | "Kecemerlangan", "SK Kuala Dungun", "0", "100", I S R K J S A | Sangat kecil, kelabu/lut sinar |

### F3. Ciri yang menjadikannya moden, minimalis & profesional
1. **Bento grid** — tren UI 2024–2026 (gaya Apple/iOS widget).
2. **Kad seperti widget iOS** — bucu bulat besar, ruang kosong (whitespace) banyak, satu maklumat per kad.
3. **Latar neutral tanpa tekstur** — semua perhatian pada kad.
4. **Pencahayaan lembut + bayang terapung** — rasa 3D premium tanpa realisme berlebihan (gaya "clay/soft UI render").
5. **Kontras berat font** (Black vs Light) dan **aksen emas terhad**.
6. **Satu shot berterusan** dengan kamera beralih lembut — rasa sinematik.
7. **Progressive disclosure** — kad kosong dahulu, kandungan diisi apabila difokus, tajuk utama didedahkan terakhir sebagai "kemuncak".

---

## G. COMPLETE ANIMATION TIMELINE (untuk pembinaan semula)

Masa dalam **T (video asal, 15.07 s, 30 fps)**.

### Babak 1 — Build (T 0.00 → 2.00)
1. **Keadaan awal:** latar kelabu radial kosong. Kamera di sudut overview.
2. **Animasi:** 6 kad masuk berturutan (stagger 0.20 s): Header 0.13, Kalendar 0.38, Statistik 0.58, Logo 0.88, Peta 1.10, Perasmi 1.30. Setiap kad: opacity 0→1, scale 0.85→1, translateY −3%→0 (atau translateZ ke hadapan sedikit), 0.30–0.35 s, ease-out.
3. **Posisi akhir:** grid bento lengkap, semua kad kosong.
4. **Kamera:** statik.
5. **Keadaan akhir:** hold 0.5 s (T 1.48–1.98).

### Babak 2 — Kalendar (T 1.98 → 4.43)
1. **Awal:** overview kosong.
2. **Animasi:** kamera dolly-in ke kalendar (1.98–2.80). Kandungan: kepala 2.38 → baris hari 2.55 → nombor (stagger per baris) 2.72–2.95 → badge 24 pop 2.93–3.08 → badge 25 pop 3.38–3.53 → glint badge ≈4.13.
3. **Posisi akhir:** kalendar memenuhi ≈ 93% lebar, header slab terpotong di atas, tepi kad Statistik di kanan, Logo di bawah.
4. **Kamera:** dolly-in + tilt + orbit kecil, kemudian float.
5. **Akhir:** kalendar lengkap dengan 2 tarikh emas.

### Babak 3 — Statistik (T 4.43 → 6.51)
1. **Awal:** close-up kalendar.
2. **Animasi:** kamera arc ke kanan (4.43–5.13). Trofi 4.88 → tajuk 4.97 → subtajuk 5.05 → kaunter + bar 29→100% (5.03–5.94, ease-out) → shine bar 6.27–6.53.
3. **Posisi akhir:** kad Statistik ≈ 85% W di tengah.
4. **Kamera:** dolly-out → truck kanan → dolly-in, kemudian float.
5. **Akhir:** "100%" dengan bar penuh.

### Babak 4 — Logo (T 6.51 → 8.50)
1. **Awal:** close-up Statistik.
2. **Animasi:** kamera arc ke kiri-bawah (6.51–7.15). Logo blur+fade-in 6.83–6.98. Glare diagonal 7.40–7.73.
3. **Posisi akhir:** kad Logo ≈ 90–95% W, kalendar terpotong di atas.
4. **Kamera:** dolly-out → pan kiri-bawah → dolly-in, float.
5. **Akhir:** logo statik.

### Babak 5 — Peta (T 8.50 → 10.50)
1. **Awal:** close-up Logo.
2. **Animasi:** kamera arc ke kanan (8.50–9.20). Grid jalan 8.76; titik mula 9.06; laluan dilukis 9.13–9.84; "Dewan Sri Kuala" 9.51; "SK Kuala Dungun" 9.73; pin drop 9.94–10.05; ripple 10.16–10.38.
3. **Posisi akhir:** Peta ≈ 85% W, Statistik terpotong di atas.
4. **Kamera:** arc, float.
5. **Akhir:** laluan lengkap dengan pin.

### Babak 6 — Perasmi (T 10.50 → 12.52)
1. **Awal:** close-up Peta.
2. **Animasi:** kamera arc ke kiri-bawah (10.50–11.13). Bulatan foto scale+blur-in 10.76–10.98; "Dirasmikan oleh" 11.06; garis emas 11.13; "Pengurus" 11.21–11.36; "PTPTN Dungun" 11.36–11.48.
3. **Posisi akhir:** kad Perasmi ≈ 100% W di separuh atas, Logo terpotong di atas, latar kosong di bawah.
4. **Kamera:** arc, float.
5. **Akhir:** hold ≈ 1 s.

### Babak 7 — Finale (T 12.52 → 15.07)
1. **Awal:** close-up Perasmi.
2. **Animasi:** dolly-out panjang ke overview (12.52–13.85, ease-out). Tajuk header fade-in 13.05–13.2; subtajuk 13.2–13.35.
3. **Posisi akhir:** overview lengkap — identik dengan sudut Babak 1.
4. **Kamera:** dolly-out + tilt-up, settle.
5. **Akhir:** hold 1.2 s → hard cut ke latar kosong (loop).

### Ringkasan kadar masa (pacing)
| Komponen | Tempoh |
|---|---|
| Build | 2.0 s |
| Setiap babak kad | ≈ 2.0 s (0.65–0.8 s pergerakan kamera + 1.2–1.5 s kandungan/hold) |
| Finale | ≈ 2.5 s (1.3 s pull-out + 1.2 s hold) |
| Jumlah | **15.07 s** |

---

## H. RECOMMENDED PRODUCTION WORKFLOW

### H1. Pilihan teknologi

| Kaedah | Kesesuaian | Catatan |
|---|---|---|
| **Three.js (WebGL) + GSAP** | ⭐ Terbaik untuk tiruan tepat & tema berubah | Kad = `RoundedBoxGeometry` + tekstur kanvas/HTML; kamera sebenar; render ke MP4 melalui CCapture/Puppeteer frame capture |
| **HTML/CSS 3D (`perspective` + `transform-style: preserve-3d`) + GSAP** | ⭐ Paling cepat | Papan = satu `div` dengan rotateX/rotateZ; "kamera" = transform pada pembungkus (scale + translate + rotate). Kandungan teks/SVG kekal tajam. Render dengan Remotion atau Puppeteer screenshot per frame |
| **Remotion (React)** | ⭐ Bagus untuk template berulang | Masa deterministik per frame (`useCurrentFrame`), eksport MP4 1080×1920@30 terus |
| **Blender** | Kualiti render tertinggi | Kad = Cube + Bevel; kamera dengan Bezier path; Eevee/Cycles untuk bayang lembut; teks sebagai plane bertekstur |
| **After Effects** | Biasa untuk motion designer | Lapisan 3D + kamera 3D + Element/Cineware jika mahu ketebalan |
| AI video generator | ❌ Tidak sesuai untuk tiruan tepat | Teks, nombor & tarikh tidak boleh dikawal; guna hanya untuk aset (cth. logo) |

### H2. Teknik 3D yang diperlukan
- **Satah papan tunggal** (board group) dengan semua kad sebagai anak — rotateX ≈ 22°, rotateZ ≈ −2°.
- **Kamera perspektif** FOV ≈ 35–40° (Three.js) / `perspective: 1400–1800px` pada lebar 1080 (CSS) — anggaran, laraskan sehingga nisbah atas:bawah papan ≈ 0.76.
- **Ketebalan kad**: RoundedBox depth ≈ 2–3% lebar, bevel/radius ≈ 8–10%.
- **Pencahayaan**: 1 directional key light kiri-atas (lembut), 1 hemisphere/ambient, bayang lembut (PCFSoft / contact shadow), atau `box-shadow` berlapis di CSS: `0 30px 60px rgba(0,0,0,.18), 0 8px 16px rgba(0,0,0,.10)`.
- **Latar**: plane besar / `radial-gradient(ellipse at 50% 45%, #E0E0E0 0%, #CFCFCF 50%, #B4B4B4 100%)`.

### H3. Cara menghasilkan kad terapung
- Setiap kad = objek berasingan dengan bayang lembut tidak bersentuhan (offset Z kecil daripada latar).
- Kemasukan: `gsap.from(card, {opacity:0, scale:0.85, y:-30, duration:0.33, ease:"power3.out", stagger:0.2})`.
- Rasa "terapung" semasa hold datang daripada **kamera drift** (contoh: skala kamera +2–3% secara linear sepanjang hold), bukan kad berayun.

### H4. Cara menghasilkan perspektif & pergerakan kamera
- Tentukan **6 keyframe kamera** (Overview, Kalendar, Statistik, Logo, Peta, Perasmi). Setiap keyframe: posisi (x,y,z), sasaran lookAt (pusat kad), roll kecil.
- Setiap peralihan kad→kad = **3 titik**: mula → titik tengah (ditarik ke belakang ≈ 1.6–1.8× jarak) → akhir. Interpolasi melalui `CatmullRomCurve3` atau GSAP MotionPath dengan satu `ease: "power2.inOut"` untuk seluruh laluan; tempoh 0.65–0.80 s.
- Push-in pertama (overview→kalendar) dan pull-out terakhir boleh lurus (tanpa titik tengah); pull-out guna `expo.out` 1.3 s.
- Close-up: kamera lebih frontal (kurangkan sudut relatif kepada papan ≈ 10–15° berbanding overview) — inilah yang membuat perspektif berubah semasa zoom.

### H5. Cara menghasilkan transisi kandungan
| Kesan | Three.js / CSS |
|---|---|
| Fade teks berperingkat | GSAP `stagger: 0.04–0.08` pada elemen teks |
| Badge pop | `scale 0→1, ease: "back.out(2)"`, 0.15 s |
| Count-up | `gsap.to(obj,{val:100, duration:0.9, ease:"power3.out", onUpdate})`, lebar bar = val% |
| Shine sweep | Gradien linear putih 30% opacity, `background-position` / plane bertopeng bergerak 0.35 s |
| Blur reveal | CSS `filter: blur(16px)→0` + opacity; Three.js: shader atau dua tekstur crossfade |
| Path drawing | SVG `stroke-dasharray` = panjang laluan, animasi `stroke-dashoffset` → 0, 0.7 s |
| Pin drop | translateY −20px→0 + opacity, `back.out`; ripple = elips scale 0.5→1.6, opacity 0.8→0 |
| Line grow | `scaleX 0→1, transform-origin: left` |

### H6. Cara memastikan animasi lancar
- Render **deterministik per frame** (Remotion / CCapture / Blender) — jangan rakam skrin secara langsung.
- 30 fps (sama dengan asal) atau 60 fps untuk lebih licin; 1080×1920.
- Gunakan **satu timeline induk** (GSAP timeline / Remotion sequence) dengan masa dalam jadual G.
- Overlap: mulakan fade kandungan ≈ 0.3 s **sebelum** kamera berhenti.
- Tambah motion blur ringan semasa peralihan kamera (Blender/AE: shutter 180°; Three.js: pilihan) **(asal tidak menunjukkan motion blur yang jelas — pilihan sahaja)**.
- Elakkan easing linear untuk kamera; guna `power2/3.inOut` untuk arc dan `expo.out` untuk finale.
- Teks: gunakan tekstur resolusi tinggi (2× DPR) atau HTML/SVG supaya tajam ketika close-up penuh.

### H7. Templat tema baharu (tukar kandungan, kekal struktur)
| Slot | Asal | Contoh tema lain |
|---|---|---|
| Header | Nama acara | Nama produk / acara |
| Kad A (biru) | Kalendar + tarikh disorot | Tarikh pelancaran / jadual |
| Kad B (putih) | Statistik % + bar | KPI / harga / rating |
| Kad C (putih) | Logo | Logo jenama / imej produk |
| Kad D (biru, tinggi) | Peta + laluan + pin | Lokasi / carta garis / langkah proses |
| Kad E (putih, lebar) | Perasmi (foto + nama) | Penceramah / testimoni / CTA |

Kekalkan: checkerboard 2 warna + 1 aksen, urutan stagger atas→bawah, kamera fokus mengikut urutan bacaan (Z-pattern: kiri-atas → kanan-atas → kiri-tengah → kanan → kiri-bawah), dan tajuk didedahkan terakhir.

### H8. Aliran kerja yang dicadangkan
1. **Reka kad 2D** dahulu (Figma/HTML) pada 1080 px lebar — ikut nisbah C1.
2. **Bina papan 3D** (CSS 3D atau Three.js) dan laraskan rotateX/Z + FOV sehingga overview sepadan dengan frame rujukan `13_akhir_loop`.
3. **Tetapkan 6 keyframe kamera** dan semak setiap close-up dengan helaian rujukan 02–12.
4. **Bina timeline induk** mengikut Jadual G.
5. **Animasi kandungan** setiap kad (H5).
6. **Render** 1080×1920 @30 fps, H.264, 15.07 s, frame akhir = komposisi penuh untuk loop.
7. **Bandingkan** bersebelahan dengan rakaman asal (overlay 50%) pada timestamp utama: 2.0, 2.8, 4.6, 5.1, 6.9, 7.2, 8.9, 9.2, 10.9, 11.1, 13.0, 14.0.

---

### Lampiran — Helaian rujukan (`analisis/rujukan/`)
Timestamp dalam helaian = **Rak** (rakaman). Tolak 0.217 s untuk T.

| Fail | Julat Rak |
|---|---|
| 01_build_0.15-2.25s.png | Build kad |
| 02_push_kalendar_2.1-3.0s.png | Push-in kalendar |
| 03_kalendar_3.0-4.7s.png | Badge 24/25 |
| 04_ke_statistik_4.6-5.5s.png | Arc ke statistik |
| 05_kaunter_5.4-6.6s.png | Count-up |
| 06_ke_logo_6.6-7.4s.png | Arc ke logo |
| 07_logo_kilauan_7.4-8.6s.png | Glare logo |
| 08_ke_peta_8.6-9.4s.png | Arc ke peta |
| 09_laluan_peta_9.4-10.6s.png | Path draw + pin |
| 10_ke_perasmi_10.6-11.4s.png | Arc ke perasmi |
| 11_perasmi_teks_11.35-12.7s.png | Teks perasmi |
| 12_pullout_12.6-14.1s.png | Pull-out finale |
| 13_akhir_loop_14.0-16.07s.png | Hold akhir + loop |
