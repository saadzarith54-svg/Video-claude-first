"""ADEGAN 3 edit decision list (source: "AGEGAN 3", 107.6s, Zarith left + Amsyar right at a table).

Speakers (mouth-motion analysis + frames): Zarith (left, bucket hat): intro, equipment, levels, safety.
Amsyar (right): weekly schedule 49-75s and closing line 93-99s.
"""

L_XY, R_XY, C_XY = (517, 300), (783, 310), (650, 330)

# RAW-FOLLOW MODE (user request): original order, natural pauses kept ("nampak macam tengah berbincang").
# Earlier hook version used HOOK_RANGE = (26.42, 36.80) moved to the front; now disabled.
HOOK_RANGE = None  # "latihan yang tidak memerlukan peralatan yang mahal. Cukuplah ... kotak pasir"
# BODY ranges (pauses > GAP_MIN are tightened to GAP_KEEP automatically)
BODY_RANGES = [(0.0, 99.25)]   # whole raw take up to the last line
# Removed: 0-5.9 setup silence | 20.55-26.36 "Kami juga telah berbincang berkaitan untuk memilih" (hook covers it)
CUTS = []                        # nothing cut (repeat "dari segi keselamatan" kept, as in raw)
TAIL = (99.25, 107.60, 1.0)      # raw ending at normal speed: stand up, take equipment, walk off
GAP_MIN, GAP_KEEP = 999.0, 0.22  # no pause tightening
END_HOLD = 0.8
CARD_LEAD = 2.2                  # end card appears this long before the tail ends

# camera framing per source range: (from, to, focus, base zoom)  -- alternates +0.12 on each cut
FRAMING = [
    (0.0, 26.0, C_XY, 1.05),
    (26.0, 37.0, L_XY, 1.40),    # equipment line, on Zarith
    (36.8, 51.7, C_XY, 1.08),
    (51.7, 75.5, R_XY, 1.25),    # Amsyar
    (75.5, 93.3, (700, 300), 1.25),  # Zarith (kept left of centre), safety panel on the right
    (93.3, 99.3, R_XY, 1.25),    # Amsyar closing
    (99.3, 120, C_XY, 1.00),     # tail wide
]

# caption fixes (verified by re-transcribing each chunk separately)
DROP = [(59.10, 59.37), (89.00, 89.11)]   # hallucinated "Setiap setiap setiap hari", "Terima kasih kerana menonton!"
INSERT = [("sahaja", 89.06, 89.50)]
CORRECTIONS = {"kut": "kon", "Menegaklah": "Manakala", "sehat": "sehari", "rehatkan": "dihadkan",
               "realiti": "yang letih", "bandar": "padang", "Iaitu": "iaitu", "telahpun": "telah pun"}

# events in SOURCE time
EV = {
    # hook
    "intro": 0.6, "intro_out": 6.2, "hook_title": 26.50, "eq_kon": 30.86, "eq_kotak": 32.55, "eq_tali": 33.95, "eq_pasir": 35.95,
    # body
    "lt_zarith": 7.40, "lt_zarith_out": 9.85,
    "prinsip": 8.2, "pr_laksana": 27.0, "pr_sistematik": 12.98, "pr_tahap": 38.2, "pr_selamat": 76.6,
    "five": 9.95, "five_1": 18.24, "five_5": 19.62, "five_out": 20.55,
    "load": 38.2, "load_ringan": 42.14, "load_naik": 48.5, "load_out": 51.6,
    "lt_amsyar": 51.9, "lt_amsyar_out": 55.9,
    "week": 53.2, "week_2x": 54.14, "week_rest": 57.84, "week_out": 61.1,
    "table": 62.4, "table_m12": 62.6, "table_m34": 68.4, "table_out": 74.9,
    "safe": 76.6, "safe_1": 82.52, "safe_2": 84.38, "safe_3": 91.20, "safe_out": 93.3,
    "closing": 95.9,
}

EXERCISES = [  # (name, jenis) -- from "Parameter latihan" table
    ("Pecutan", "Kelajuan"),
    ("Bounding", "Kuasa kaki"),
    ("Hentakan melepasi tali getah", "Kuasa & koordinasi"),
    ("Litar squat, lunge, plank", "Kekuatan kaki & teras"),
    ("Lompat kotak ke pasir", "Keseimbangan & koordinasi"),
]

TABLE_HEAD = ["Latihan", "Jenis", "Intensiti", "Jarak / tempoh (anggaran)", "Ulangan & set", "Rehat", "Perkembangan beban"]
TABLE = [
    ["1. Pecutan", "Kelajuan", "90% usaha", "20–30 m, ~12 minit", "4–5 ulangan × 1 set", "2–3 minit, berjalan balik",
     "Minggu 1–2: 20 m, 3 ulangan. Minggu 3–4: 30 m, 4–5 ulangan"],
    ["2. Bounding", "Kuasa kaki", "Sederhana tinggi tetapi terkawal", "15–20 m, ~8 minit", "6–8 lompatan × 3 set", "1–2 minit",
     "Minggu 1–2: 2 set × 6. Minggu 3–4: 3 set × 8, kemudian 4 set"],
    ["3. Hentakan melepasi tali getah", "Kuasa & koordinasi", "Sederhana–tinggi, fokus teknik", "Larian 3–5 langkah, ~8 minit",
     "5 ulangan setiap kaki × 2 set", "90 saat", "Mula 3 langkah & tali rendah, naik ke 5 langkah & tali lebih tinggi"],
    ["4. Litar squat, lunge, plank", "Kekuatan kaki & teras", "Sederhana (berat badan sendiri)", "3 stesen, ~10 minit",
     "10–12 ulangan (plank 20–30 saat) × 3 set", "45–60 saat", "Mula 2 set, naik 3 set, kemudian tambah masa plank / lunge melompat"],
    ["5. Lompat kotak ke pasir", "Keseimbangan & koordinasi", "Rendah–sederhana", "Kotak 20–30 cm, ~8 minit", "5 ulangan × 2 set",
     "1–2 minit", "Kekal 20 cm sehingga stabil, kemudian 30 cm, tambah permainan lompat sasaran"],
]
