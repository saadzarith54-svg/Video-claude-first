"""ADEGAN 7 -- penutup (closing). Source 7.0 = "Adegan 7 ( penutup )" 82s: Zarith (left, hat), Amsyar (middle),
Hatim (right) side by side. Speaker turns are not reliable from the footage, so all three are named together instead
of per-speaker lower-thirds. Hook + PiP reuse earlier scenes (5.0c pecutan, 5.1c bounding betul, 5.4d squat, 5.5b lompat kotak).
"""
PEOPLE = {}
LT_CLIPS = ()
PAUSE_MIN, PAUSE_KEEP = 0.9, 0.45
TALK_ZOOMS = (1.0, 1.06)
PANEL_Y = 16                      # info panel at top-left over the building (faces start ~y 190-300)
PANEL_MAX_ROWS = 3
PIP_BOX = (900, 318, 352, 198)    # x, y, w, h (over Hatim's torso)

FRAME = {"5.0c": None, "5.1c": None, "5.4d": None, "5.5b": (680, 380, 1.0), "7.0": (640, 360, 1.0)}
TRACK_ZOOM = {"5.0c": 1.9, "5.1c": 1.7, "5.4d": 1.9}

HOOK = [   # (clip, a, b, rate, view)
    ("5.0c", 2.0, 4.2, 1.0, {"track": True, "zoom": 1.9}),
    ("5.1c", 1.6, 3.4, 0.5, {"track": True, "zoom": 1.7}),
    ("5.4d", 3.0, 5.2, 1.0, {"track": True, "zoom": 1.9}),
    ("5.5b", 5.0, 6.7, 0.4, {"fixed": (640, 420, 1.25)}),
]
HOOK_TITLE_HOLD = 1.9
HOOK_TOP = "PECUTAN · BOUNDING · LITAR · LOMPAT KOTAK"
HOOK_SMALL = "5 LATIHAN · 1 MATLAMAT"
HOOK_BIG = "LOMPAT LEBIH JAUH"

SEQ = [
    ("hook",),
    ("card", None, "PENUTUP", "Kesimpulan tugasan", "TUGASAN 3 · LOMPAT JAUH"),
    ("talk", "7.0", 6.0, 78.6, "", []),
    ("recap",),     # credits card with long-jump animation
]
CARD_DUR, RECAP_DUR, END_DUR = 2.6, 9.5, 0.0

TEAM = [("Zarith", 330), ("Amsyar", 690), ("Hatim", 990)]     # name chip x positions (source == output, zoom 1.0)
CREDITS = [("Muhammad Amsyar Rasif", "Penganalisis"), ("Muhammad Zarith Ridzuan", "Jurulatih Lapangan 1"),
           ("Ahmad Hatim", "Jurulatih Lapangan 2 · Pegawai Keselamatan")]
MAPPING = [("Pecutan", "Kelajuan"), ("Bounding", "Kuasa kaki"), ("Hentakan tali getah", "Kuasa & koordinasi"),
           ("Litar squat/lunge/plank", "Kekuatan kaki & teras"), ("Lompat kotak ke pasir", "Keseimbangan & koordinasi")]
MAPPING_T = (23.8, 31.6)   # source time window ("melatih komponen kecergasan tertentu...")

PANELS = {
    "7.0": [
        (6.3, 20.9, "5 LATIHAN", [("percutan", 11, "1. Pecutan"), ("bonding", 13, "2. Bounding"), ("hentakan", 15, "3. Hentakan melepasi tali getah"),
                                  ("litar", 17, "4. Litar kekuatan"), ("pendaratan", 19, "5. Lompat kotak · pendaratan")], None),
        (20.9, 31.6, "SETIAP LATIHAN MELATIH", [("komponen", 24, "Satu komponen kecergasan"), ("memperbaiki", 26.5, "Satu fasa teknik lompat jauh")], None),
        (31.6, 41.0, "PRINSIP", [("diubah", 34, "Parameter boleh diubah ikut tahap pelajar"), ("menekankan", 37.5, "Keselamatan pada setiap langkah")], None),
        (41.0, 63.3, "KERJA BERPASUKAN", [("berbincang", 48.5, "Berbincang bersama"), ("berkongsi", 51.5, "Berkongsi pendapat"),
                                          ("semoga", 57.5, "Semoga video ini memberi manfaat")], None),
        (63.4, 72.3, "MATLAMAT", [("membantu", 66, "Bantu pelajar lompat lebih jauh"), ("memperbaiki", 70, "Perbaiki kekurangan yang ada")], None),
    ],
}
# PiP clips while each exercise is named (talk source times): (from, to, (clip, a, b, view))
PIP_TIMED = [
    (11.9, 13.9, ("5.0c", 2.0, 5.0, {"track": True, "zoom": 1.9}), "Pecutan"),
    (13.9, 15.5, ("5.1c", 1.4, 4.6, {"track": True, "zoom": 1.7}), "Bounding"),
    (17.2, 19.9, ("5.4d", 2.5, 6.5, {"track": True, "zoom": 1.9}), "Litar kekuatan"),
    (19.9, 21.6, ("5.5b", 4.3, 7.9, {"fixed": (640, 420, 1.25)}), "Lompat kotak"),
]
RECAP_ROWS = []
END_TEXT = ""
DEMO_CUES = {}
CORRECTIONS = {"percutan": "pecutan", "bonding": "bounding", "kecegasan": "kecergasan"}
DROP = {"7.0": [(80.0, 83.0)]}
OVERRIDE = {}
