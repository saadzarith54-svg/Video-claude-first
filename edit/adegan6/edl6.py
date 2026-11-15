"""ADEGAN 6 -- penyejukan (cool-down).
Sources: 6.0 = "ADEGAN 6 ( penyejukan )" Hatim talk (jersey "HATIM") | 6.1 = IMG_4104 "adegan 6.1 _ penyejukan" silent demo,
wide static shot of three students: jogging 17-35s, sit down 35-46s, seated stretches 46-112s, standing 113-120s.
User: remove disturbing background sound, show every movement example 2x. Pass 2 = close-up (stretches are static, so a
close view helps more than slow-mo); jogging pass 2 = slow-mo.
"""
PEOPLE = {"Hatim": ("Ahmad Hatim", "JURULATIH LAPANGAN 2")}
LT_CLIPS = ("6.0",)
PAUSE_MIN, PAUSE_KEEP = 0.9, 0.45
GROUP = (555, 470)   # seated group centre in the source frame

FRAME = {"6.1": None}           # tracked unless a segment gives "fixed"
TRACK_ZOOM = {"6.1": 1.5}

# hook montage shots: (clip, a, b, rate, (x, y, zoom))
HOOK = [
    ("6.1", 66.0, 69.5, 1.0, (555, 470, 2.6)),
    ("6.1", 116.0, 118.6, 1.0, (600, 430, 2.0)),
    ("6.1", 22.0, 24.6, 0.5, (930, 370, 1.8)),
    ("6.1", 98.0, 101.0, 1.0, (555, 470, 2.6)),
]
HOOK_TITLE_HOLD = 1.8

SEQ = [
    ("hook",),
    ("card", None, "PENYEJUKAN BADAN", "Selepas semua latihan", "ADEGAN PENUTUP LATIHAN"),
    ("talk", "6.0", 0.0, 49.2, "Hatim", [(13.10, 14.40)]),   # repeated "penyejukan badan" removed
    ("demo", "6.1", 17.5, 35.0, 1.0, "JOGGING RINGAN", 1, {"track": True, "zoom": 1.4}),
    ("demo", "6.1", 19.5, 27.5, 0.5, "JOGGING RINGAN", 2, {"track": True, "zoom": 1.9}),
    ("demo", "6.1", 46.0, 64.0, 1.0, "REGANGAN STATIK · DUDUK", 1, {"fixed": (555, 470, 1.7)}),
    ("demo", "6.1", 49.0, 61.0, 1.0, "REGANGAN STATIK · DUDUK", 2, {"fixed": (555, 470, 2.6), "close": True}),
    ("demo", "6.1", 64.0, 77.5, 1.0, "REGANGAN PAHA BELAKANG", 1, {"fixed": (555, 470, 1.7)}),
    ("demo", "6.1", 64.5, 77.0, 1.0, "REGANGAN PAHA BELAKANG", 2, {"fixed": (555, 470, 2.6), "close": True}),
    ("demo", "6.1", 78.0, 112.0, 1.0, "REGANGAN PAHA DEPAN & PINGGUL", 1, {"fixed": (555, 470, 1.7)}),
    ("demo", "6.1", 94.0, 110.0, 1.0, "REGANGAN PAHA DEPAN & PINGGUL", 2, {"fixed": (555, 470, 2.6), "close": True}),
    ("demo", "6.1", 112.5, 120.2, 1.0, "REGANGAN BERDIRI · BETIS", 1, {"fixed": (600, 430, 1.6)}),
    ("demo", "6.1", 113.5, 119.5, 1.0, "REGANGAN BERDIRI · BETIS", 2, {"fixed": (600, 430, 2.2), "close": True}),
    ("card", None, "MINUM AIR KOSONG", "dengan secukupnya", "PALING PENTING"),
    ("recap",),
    ("end",),
]
CARD_DUR, RECAP_DUR, END_DUR = 2.8, 9.0, 3.0

DEMO_CUES = {   # only what is said (1 minit) or plainly visible
    "JOGGING RINGAN": ["1 minit"],
    "REGANGAN STATIK · DUDUK": ["Regangan statik", "Tahan posisi"],
    "REGANGAN PAHA BELAKANG": ["Capai hujung kaki", "Tahan posisi"],
    "REGANGAN PAHA DEPAN & PINGGUL": ["Regangan statik", "Tahan posisi"],
    "REGANGAN BERDIRI · BETIS": ["Regangan statik", "Tahan posisi"],
}

PANELS = {
    "6.0": [
        (1.0, 18.3, "KENAPA?", [("selesai", 1.5, "Selepas semua latihan selesai"), ("Penyujukan", 10, "Lakukan penyejukan badan"),
                                ("Kekerjangan", 16, "Elak kekejangan otot")], None),
        (18.3, 37.8, "LANGKAH", [("Jogging", 22.5, "1. Jogging ringan · 1 minit"), ("regangan", 31, "2. Regangan statik:"),
                                 ("paha", 33, "   paha depan · paha belakang"), ("petis", 35, "   betis · pinggul")], ("6.1", 66.0, 72.0, (555, 470, 2.4))),
        (37.8, 49.2, "PALING PENTING", [("Minum", 44.5, "Minum air kosong secukupnya")], None),
    ],
}

RECAP_ROWS = [("1", "Jogging ringan", "1 minit"), ("2", "Regangan statik", "Paha depan · paha belakang · betis · pinggul"),
              ("3", "Minum air kosong", "Secukupnya")]
END_TEXT = "PENUTUP →"

CORRECTIONS = {"Penyujukan": "Penyejukan", "Kekerjangan": "kekejangan", "petis": "betis", "Petis": "Betis"}
DROP = {"6.0": [(13.05, 14.45), (56.0, 58.0)]}
OVERRIDE = {}
