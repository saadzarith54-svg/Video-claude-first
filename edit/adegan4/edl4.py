"""ADEGAN 4 edit decision list -- follows the user's order 4.1 -> 4.12, raw lengths kept.

Clips (Drive names): 4.1 IMG_4059 | 4.2 IMG_4060 | 4.3 IMG_4061 | 4.4 IMG_4065 | 4.5 IMG_4072 jogging ringan |
4.6 IMG_4073 ayunan kaki | 4.7 lunges berjalan | 4.8 regangan pinggul | 4.9 IMG_4075 A-skip | 4.10 IMG_4076 B-skip |
4.11 IMG_4077 high knees | 4.12 IMG_4079 pecutan progresif
People: 4.2/4.3 Hatim (jersey "HATIM", pegawai keselamatan) | 4.4 Zarith (bucket hat) | demos: unnamed ("DEMONSTRASI").
Only removed: 4.4 0-8.8 (setup chatter "...rangan lah. Tak ada pun.") and 4.4 133.4-139 (walking to stop the camera).
Long pauses in 4.4 are KEPT and filled with section banners.
"""

CLIP = {f"4.{i}": f"c{i:02d}.bin" for i in range(1, 13)}

# hook teaser shots: (clip, a, b, rate, zoom, track)
HOOK = [
    ("4.12", 0.9, 2.7, 1.0, 1.0, False),
    ("4.11", 7.20, 7.85, 0.30, 1.75, True),
    ("4.9", 5.85, 6.50, 0.30, 1.75, True),
    ("4.7", 2.40, 3.10, 0.45, 1.60, True),
    ("4.1", 15.0, 16.6, 1.0, 1.25, False),
]
HOOK_TITLE_HOLD = 1.6   # last hook shot is extended by a freeze for the title

# main sequence (key, clip, a, b, rate, kind, zoom)
ITEMS = [
    ("4.1", "4.1", 0.00, 35.35, 1.0, "broll", 1.00),
    ("4.2", "4.2", 0.80, 38.90, 1.0, "speech", 1.00),
    ("4.3", "4.3", 0.00, 17.55, 1.0, "speech", 1.00),
    ("4.4", "4.4", 8.80, 133.40, 1.0, "speech", 1.00),
    ("4.5", "4.5", 0.00, 23.35, 1.0, "demo", 1.30),
    ("4.6", "4.6", 0.00, 11.60, 1.0, "demo", 1.35),
    ("r4.6", "4.6", 5.00, 6.60, 0.30, "replay", 1.75),
    ("4.7", "4.7", 0.00, 16.95, 1.0, "demo", 1.35),
    ("r4.7", "4.7", 2.00, 3.60, 0.30, "replay", 1.75),
    ("4.8", "4.8", 0.00, 25.25, 1.0, "demo", 1.35),
    ("4.9", "4.9", 0.00, 35.35, 1.0, "demo", 1.30),
    ("r4.9", "4.9", 5.50, 7.30, 0.30, "replay", 1.75),
    ("4.10", "4.10", 0.00, 15.10, 1.0, "demo", 1.30),
    ("r4.10", "4.10", 4.00, 5.60, 0.30, "replay", 1.75),
    ("4.11", "4.11", 0.00, 19.95, 1.0, "demo", 1.30),
    ("r4.11", "4.11", 7.00, 8.60, 0.30, "replay", 1.75),
    ("4.12", "4.12", 0.00, 13.85, 1.0, "demo", 1.00),
]
TRACKED = {"4.5", "4.6", "4.7", "4.8", "4.9", "4.10", "4.11"}
RECAP_HOLD = 11.0
END_HOLD = 3.0

# 4.4 framing per section (local time from, zoom)
ZOOM_44 = [(0, 1.00), (28.1, 1.10), (43.9, 1.00), (64.6, 1.10), (99.1, 1.00)]

# demo info: (title, dose, purpose, cue)
DEMO = {
    "4.5": ("JOGGING RINGAN", "2 minit", "Naikkan suhu badan", None),
    "4.6": ("AYUNAN KAKI", "10 kali setiap set", "Lenturkan pinggul & kaki", None),
    "4.7": ("LUNGES BERJALAN", "10 kali setiap set", "Lenturkan pinggul & kaki", None),
    "4.8": ("REGANGAN / PUTARAN PINGGUL", "10 kali setiap set", "Lenturkan pinggul & kaki", None),
    "4.9": ("A-SKIP", "2 set × 30 m", "Postur badan & ritma larian", "Lutut diangkat tinggi · ayunan tangan aktif"),
    "4.10": ("B-SKIP", "2 set × 30 m", "Postur badan & ritma larian", "Lutut diangkat tinggi · ayunan tangan aktif"),
    "4.11": ("HIGH KNEES", "2 set × 30 m", "Postur badan & ritma larian", "Lutut diangkat tinggi · ayunan tangan aktif"),
    "4.12": ("PECUTAN PROGRESIF", "2 ulangan × 30 m", "Sediakan sistem saraf untuk kelajuan", None),
}
DEMO_GROUP = {"4.5": "JOGGING RINGAN", "4.6": "REGANGAN DINAMIK", "4.7": "REGANGAN DINAMIK", "4.8": "REGANGAN DINAMIK",
              "4.9": "DRILL LARIAN", "4.10": "DRILL LARIAN", "4.11": "DRILL LARIAN", "4.12": "PECUTAN PROGRESIF"}

# events in LOCAL clip time: key -> (item, t)
EV = {
    # 4.1 silent area check (timed to what he does on screen)
    "a1_tag": ("4.1", 0.6), "a1_kotak": ("4.1", 6.2), "a1_pasir": ("4.1", 14.8), "a1_objek": ("4.1", 23.5),
    # 4.2 Hatim
    "lt_hatim": ("4.2", 2.0), "lt_hatim_out": ("4.2", 7.5),
    "h_check": ("4.2", 14.0), "h_pasir": ("4.2", 21.6), "h_objek": ("4.2", 24.3), "h_kotak": ("4.2", 33.5),
    # 4.3
    "pem_title": ("4.3", 11.1),
    # 4.4 Zarith
    "lt_zarith": ("4.4", 9.2), "lt_zarith_out": ("4.4", 13.6),
    "why": ("4.4", 13.9), "why_out": ("4.4", 26.8), "why_otot": ("4.4", 21.9), "why_cedera": ("4.4", 24.0),
    "sec1": ("4.4", 26.9), "c1": ("4.4", 29.5), "c1_dose": ("4.4", 35.4), "c1_goal": ("4.4", 39.7),
    "sec2": ("4.4", 41.4), "c2": ("4.4", 45.5), "c2_ex": ("4.4", 49.5), "c2_dose": ("4.4", 55.0), "c2_goal": ("4.4", 59.4),
    "sec3": ("4.4", 61.5), "c3": ("4.4", 65.5), "c3_ex": ("4.4", 67.4), "c3_dose": ("4.4", 75.2), "c3_goal": ("4.4", 79.6),
    "c3_cue": ("4.4", 87.3),
    "sec4": ("4.4", 96.6), "c4": ("4.4", 100.6), "c4_ex": ("4.4", 106.4), "c4_dose": ("4.4", 119.4), "c4_int": ("4.4", 129.5),
}
SEC_BANNERS = [("sec1", 1, "JOGGING RINGAN", 2.1), ("sec2", 2, "REGANGAN DINAMIK", 2.9),
               ("sec3", 3, "DRILL LARIAN", 3.2), ("sec4", 4, "PECUTAN PROGRESIF", 2.5)]

# picture-in-picture demo previews while Zarith explains: (local from, local to, clip, a, b, label)
PIP = [
    (31.2, 43.0, "4.5", 7.0, 11.0, "Jogging ringan"),
    (49.5, 51.8, "4.6", 4.0, 8.0, "Ayunan kaki"),
    (51.8, 53.4, "4.7", 1.5, 5.5, "Lunges berjalan"),
    (53.4, 62.0, "4.8", 12.0, 16.0, "Putaran pinggul"),
    (67.4, 69.4, "4.9", 5.0, 9.0, "A-skip"),
    (69.4, 70.6, "4.10", 3.5, 7.5, "B-skip"),
    (70.6, 97.0, "4.11", 6.0, 10.0, "High knees"),
    (100.6, 133.4, "4.12", 1.0, 7.0, "Pecutan progresif"),
]

DROP = []
CORRECTIONS = {"otak": "otot", "suku": "suhu", "rengangan": "regangan", "height": "high", "knee.": "knees.",
               "positi": "postur", "menyeragangkan": "menyeragamkan", "diatasi.": "diangkat", "Angkat": "",
               "hayunan": "ayunan", "Drill": "Drill"}

RECAP = [  # komponen, contoh, dos, tujuan
    ("Jogging ringan", "–", "2 minit", "Naikkan suhu badan"),
    ("Regangan dinamik", "Ayunan kaki, lunges berjalan, putaran pinggul", "10 kali setiap set", "Lenturkan pinggul & kaki"),
    ("Drill larian", "A-skip, B-skip, high knees", "2 set × 30 m", "Postur badan & ritma larian"),
    ("Pecutan progresif", "Perlahan → hampir laju penuh", "2 ulangan × 30 m, 60–70%", "Sediakan sistem saraf untuk kelajuan"),
]
