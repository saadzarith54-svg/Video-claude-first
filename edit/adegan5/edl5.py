"""ADEGAN 5 -- the 5 main exercises. Source keys = Drive files:
5.0a pecutan (Zarith talk) | 5.0b/5.0c simulation pecutan | 5.1a bounding | 5.1b bounding (Zarith talk) | 5.1c bounding yang betul |
5.1d bounding yang SALAH | 5.2a larian 3-5 langkah (Zarith talk) | 5.4a litar kekuatan (Hatim talk) | 5.4b lunges | 5.4c plank |
5.4d squat | 5.5a simulasi 2 (lompat sasaran) | 5.5b simulasi pendaratan dan lompatan | 5.5c tambah kreativiti (Hatim) |
5.5d lompat kotak (Hatim talk) | 5.5e IMG_4068 (Hatim talk)
User asks: remove disturbing background sound (demo clips muted -> music + SFX; speech denoised),
every simulation/movement example shown 2x (pass 2 = slow-mo where it helps).
Order: 5.0 simulations come BEFORE the 5.0a talk because Zarith opens with "Itu tadi ialah merupakan simulasi...".
No 5.3 in Drive; 5.2a refers to a demo ("sebentar tadi kita baru sahaja melihat") that is not in the folder.
"""

PEOPLE = {"Zarith": ("Muhammad Zarith Ridzuan", "JURULATIH LAPANGAN 1"), "Hatim": ("Ahmad Hatim", "JURULATIH LAPANGAN 2")}
PAUSE_MIN, PAUSE_KEEP = 0.9, 0.45   # speech pauses longer than 0.9s -> 0.45s

# demo framing: None = tracked (static camera) ; (x, y, zoom) fixed
FRAME = {
    "5.0b": (640, 360, 1.0), "5.0c": None, "5.1a": (640, 380, 1.0), "5.1c": None, "5.1d": None,
    "5.4b": None, "5.4c": (600, 390, 1.0), "5.4d": None, "5.5a": (640, 380, 1.0), "5.5b": (680, 380, 1.0),
}
TRACK_ZOOM = {"5.0c": 1.9, "5.1c": 1.7, "5.1d": 2.2, "5.4b": 1.9, "5.4d": 1.9}

# sequence. card: (kind, num, name, jenis) | talk: (kind, clip, a, b, who, cuts) | demo: (kind, clip, a, b, rate, label, pass, extra)
SEQ = [
    ("hook",),
    ("card", 1, "PECUTAN", "Kelajuan"),
    ("demo", "5.0b", 0.0, 7.5, 1.0, "SIMULASI PECUTAN (A)", 1, {}),
    ("demo", "5.0b", 0.4, 5.0, 0.5, "SIMULASI PECUTAN (A)", 2, {}),
    ("demo", "5.0c", 0.0, 12.4, 1.0, "SIMULASI PECUTAN (B)", 1, {}),
    ("demo", "5.0c", 1.0, 7.0, 0.5, "SIMULASI PECUTAN (B)", 2, {"zoom": 2.3}),
    ("talk", "5.0a", 8.0, 122.9, "Zarith", []),
    ("card", 2, "BOUNDING", "Kuasa kaki"),
    ("talk", "5.1b", 11.6, 86.0, "Zarith", []),
    ("demo", "5.1a", 0.0, 5.53, 1.0, "BOUNDING", 1, {}),
    ("demo", "5.1a", 0.6, 5.4, 0.4, "BOUNDING", 2, {}),
    ("demo", "5.1c", 0.0, 6.4, 1.0, "BOUNDING YANG BETUL", 1, {"stamp": "BETUL"}),
    ("demo", "5.1c", 1.4, 4.8, 0.35, "BOUNDING YANG BETUL", 2, {"stamp": "BETUL"}),
    ("demo", "5.1d", 0.0, 10.7, 1.0, "BOUNDING YANG SALAH", 1, {"stamp": "SALAH"}),
    ("demo", "5.1d", 0.8, 6.8, 0.5, "BOUNDING YANG SALAH", 2, {"stamp": "SALAH"}),
    ("card", 3, "HENTAKAN MELEPASI TALI GETAH", "Kuasa & koordinasi"),
    ("talk", "5.2a", 0.0, 90.8, "Zarith", []),
    ("card", 4, "LITAR SQUAT, LUNGE, PLANK", "Kekuatan kaki & teras"),
    ("talk", "5.4a", 1.3, 112.3, "Hatim", [(89.55, 94.25)]),   # cut false start "kita akan mulakan dengan dua set iaitu"
    ("demo", "5.4d", 0.0, 12.0, 1.0, "SQUAT", 1, {}),
    ("demo", "5.4d", 1.8, 9.0, 0.6, "SQUAT", 2, {}),
    ("demo", "5.4b", 0.0, 12.0, 1.0, "LUNGES", 1, {}),
    ("demo", "5.4b", 1.2, 9.6, 0.6, "LUNGES", 2, {}),
    ("demo", "5.4c", 0.0, 28.5, 1.0, "PLANK", 1, {}),
    ("demo", "5.4c", 4.0, 16.0, 1.0, "PLANK", 2, {"fixed": (600, 395, 2.1), "line": True}),
    ("card", 5, "LOMPAT KOTAK KE PASIR", "Keseimbangan & koordinasi"),
    ("talk", "5.5d", 0.8, 37.6, "Hatim", []),
    ("talk", "5.5e", 1.6, 28.6, "Hatim", []),                   # 30.8-32.2 repeat "Kekalkan ketinggian..." removed
    ("demo", "5.5b", 0.0, 9.3, 1.0, "SIMULASI PENDARATAN & LOMPATAN", 1, {}),
    ("demo", "5.5b", 4.3, 7.9, 0.3, "SIMULASI PENDARATAN & LOMPATAN", 2, {"fixed": (640, 420, 1.25)}),
    ("talk", "5.5c", 1.0, 33.4, "Hatim", []),
    ("demo", "5.5a", 0.0, 22.1, 1.0, "LOMPAT SASARAN", 1, {}),
    ("demo", "5.5a", 13.0, 18.6, 0.4, "LOMPAT SASARAN", 2, {"fixed": (700, 380, 1.2)}),
    ("recap",),
    ("end",),
]
CARD_DUR, RECAP_DUR, END_DUR = 2.6, 15.0, 3.0

HOOK_LEFT = ("5.1c", 1.5, 4.5, 0.42)     # betul
HOOK_RIGHT = ("5.1d", 2.2, 6.0, 0.55)    # salah
HOOK_TITLE_HOLD = 1.6

DEMO_CUES = {
    "5.0b": ["Badan condong", "Tolak kuat 10 langkah", "Tegakkan badan"],
    "5.0c": ["Badan condong", "Tolak kuat 10 langkah", "Tegakkan badan"],
    "5.1a": ["Lutut hadapan naik", "Tolak kuat kaki belakang", "Tangan berlawanan kaki"],
    "5.1c": ["Lutut hadapan naik", "Tolak kuat kaki belakang", "Tangan berlawanan kaki"],
    "5.1d": ["Langkah pendek", "Lutut tidak dinaikkan", "Tiada tolakan kuat"],
    "5.4d": ["Lutut sejajar jari kaki", "Belakang tegak"],
    "5.4b": ["Lutut sejajar jari kaki", "Belakang tegak"],
    "5.4c": ["Badan lurus kepala → tumit", "20–30 saat"],
    "5.5b": ["Kotak 20–30 cm", "Hulur kaki ke hadapan", "Mendarat seimbang"],
    "5.5a": ["Lompat melepasi garis sasaran", "Mendarat stabil"],
}

# talk panels: clip -> [(t_in, t_out, title, [(keyword_or_time, after, text)], pip)]  keyword resolves to word start time
PANELS = {
    "5.0a": [
        (16.4, 30.5, "PECUTAN", [("sejarah", 16, "Jarak 20–30 m"), ("meningkatkan", 21, "Tujuan: tingkatkan kelajuan"),
                                 ("Kelajuan", 27, "Laju ke hadapan semasa hentakan")], None),
        (30.5, 54.0, "CARA", [("Caranya", 30, "1. Badan condong sedikit ke hadapan"), ("Tolak", 34, "2. Tolak kuat 10 langkah pertama"),
                              ("menegakkan", 37, "3. Tegakkan badan berangsur-angsur"), ("Lakukan", 41, "4–5 ulangan · intensiti 90%"),
                              ("berehat", 47, "Rehat 2–3 minit, berjalan balik")], ("5.0c", 1.0, 7.0)),
        (54.0, 62.5, "KENAPA PILIH?", [("penyumbang", 54, "Kelajuan = penyumbang utama jarak"), ("seminggu", 59, "Dibuat 2× seminggu")], None),
        (62.5, 82.5, "PERKEMBANGAN BEBAN", [(67.7, 0, "Minggu 1–2: 20 m × 3 ulangan"), (74.1, 0, "Minggu 3–4: 30 m × 4–5 ulangan")], None),
        (82.5, 96.4, "KESELAMATAN", [("keselamatan,", 82, "Trek rata"), ("ruang", 87, "Ruang perlahankan badan selepas garisan penamat")], None),
        (97.0, 122.9, "KREATIVITI", [(108.3, 0, "Kon: ZON TOLAK (condong)"), (110.8, 0, "Kon kuning: ZON TEGAK")], ("5.0b", 0.4, 5.0)),
    ],
    "5.1b": [
        (13.9, 30.2, "BOUNDING", [("Bounding", 14, "Lompatan bersilih kaki kiri & kanan"), ("panjang", 19, "Langkah panjang"),
                                  ("melatih", 21, "Tujuan: kuasa letupan kaki")], None),
        (30.2, 40.2, "TEKNIK", [("lutut", 30, "Lutut hadapan dinaikkan"), ("Tolak", 33, "Tolak kuat dengan kaki belakang"),
                                ("tangan", 35, "Tangan berayun berlawanan kaki")], ("5.1c", 1.4, 4.8)),
        (40.2, 54.8, "DOS", [("Lakukan", 40, "3 set × 6–8 lompatan"), ("Lompatan", 44, "Jarak 15–20 m"), ("rehat", 47, "Rehat 1–2 minit"),
                             ("usaha", 50, "Usaha sederhana tinggi, terkawal")], None),
        (54.8, 76.3, "PERKEMBANGAN BEBAN", [(60.1, 0, "Minggu 1–2: 2 set × 6"), (67.6, 0, "Minggu 3–4: 3 set × 8"), (72.6, 0, "Kemudian 4 set")], None),
        (76.2, 86.0, "KESELAMATAN", [("permukaan", 78, "Permukaan rata & tidak licin")], None),
    ],
    "5.2a": [
        (0.5, 15.0, "LATIHAN 3", [(4.0, 0, "Larian 3–5 langkah"), (10.0, 0, "Hentak & lompat melepasi halangan")], None),
        (15.1, 39.7, "FOKUS TEKNIK", [(16.5, 0, "Simulasi hentakan sebenar"), ("lutut", 25, "Lutut bebas diangkat tinggi"),
                                      ("badan", 30, "Badan tegak semasa kaki bertolak"), ("sudut", 33, "Sudut lepas yang betul")], None),
        (39.7, 51.8, "DOS", [(40.0, 0, "2 set × 5 ulangan setiap kaki"), (45.3, 0, "Rehat 90 saat"), (48.0, 0, "Sederhana–tinggi, fokus teknik")], None),
        (51.8, 72.3, "PERKEMBANGAN BEBAN", [(58.5, 0, "Mula: 3 langkah, halangan rendah"), (65.5, 0, "Kemudian: 5 langkah, sedikit tinggi"),
                                            (69.5, 0, "…apabila hentakan sudah tepat")], None),
        (72.3, 83.5, "KESELAMATAN", [(78.0, 0, "Halangan tidak cederakan kaki jika tersangkut")], None),
        (83.5, 90.8, "SIKAP", [(84.5, 0, "Beri semangat kepada rakan"), (87.5, 0, "Saling menyokong dalam kumpulan")], None),
    ],
    "5.4a": [
        (1.5, 14.8, "LITAR KEKUATAN", [(6.5, 0, "Guna berat badan sendiri"), (10.5, 0, "Squat · Lunges · Plank")], None),
        (14.8, 28.0, "TUJUAN", [(17.5, 0, "Bina otot kaki & teras"), (21.5, 0, "Badan stabil semasa hentakan"), (25.0, 0, "Tidak goyah ketika mendarat")], None),
        (28.0, 52.9, "TEKNIK", [(29.5, 0, "Squat & lunges: lutut sejajar jari kaki"), (38.0, 0, "Belakang tegak"),
                                (43.5, 0, "Plank: badan lurus kepala → tumit")], ("5.4d", 1.8, 9.0)),
        (53.0, 84.0, "DOS", [(59.0, 0, "3 set × 10–12 ulangan"), (62.5, 0, "Plank 20–30 saat"), (67.0, 0, "Rehat 45–60 saat"),
                             (74.0, 0, "Intensiti sederhana (berat badan)")], None),
        (85.4, 112.3, "PERKEMBANGAN BEBAN", [(95.5, 0, "Mula 2 set → naik 3 set"), (100.0, 0, "Tambah masa plank"),
                                             (106.0, 0, "…atau lunges melompat bila teknik mantap")], None),
    ],
    "5.5d": [
        (1.0, 14.6, "LATIHAN 5", [(8.0, 0, "Latih fasa pendaratan")], None),
        (14.7, 37.6, "CARA", [(16.5, 0, "Lompat dari kotak 20–30 cm ke pasir"), (25.5, 0, "Mendarat seimbang & selamat"),
                              (31.0, 0, "Hulur kaki ke hadapan (fasa penerbangan)")], ("5.5b", 4.3, 7.9)),
    ],
    "5.5e": [
        (1.6, 11.8, "DOS", [(3.0, 0, "2 set × 5 ulangan"), (8.0, 0, "Intensiti rendah–sederhana")], None),
        (11.8, 28.6, "PERKEMBANGAN BEBAN", [(15.5, 0, "Kekal 20 cm hingga stabil → 30 cm"), (23.2, 0, "Pendaratan lebih stabil")], None),
    ],
    "5.5c": [
        (1.0, 33.4, "KREATIVITI: LOMPAT SASARAN", [(4.0, 0, "Permainan lompat sasaran"), (9.0, 0, "Lompat melepasi garis pada pasir"),
                                                   (18.3, 0, "Mendarat dengan stabil"), (23.0, 0, "Hubungkan latihan dengan pencapaian jarak")], ("5.5a", 13.0, 18.6)),
    ],
}

# caption fixes (verified chunk by chunk)
CORRECTIONS = {"pencucian": "pecutan", "sejarah": "sejarak", "beransur-ansur": "berangsur-angsur", "Bersenang": "bersilih",
               "nerima": "", "maka": "palang", "baka": "palang", "gerudukan": "", "ketindian": "ketinggian", "Lakuan": "Lakukan",
               "Lihat": "", "tumik": "tumit", "berantisiti": "berintensiti", "tinggal": "hingga", "Ujuannya": "Tujuannya",
               "poster": "postur", "mensimulasikan": "mensimulasikan"}
DROP = {"5.1b": [(91.0, 95.0)], "5.4a": [(89.55, 94.25)], "5.5e": [(30.5, 33.0)], "5.2a": [(93.0, 96.0)]}
