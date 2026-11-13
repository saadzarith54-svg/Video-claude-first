"""Edit decision list for FIRST FOOTAGE.MP4 (source times in seconds).

Speakers (from frames): Zarif = left (bucket hat), Amsyar = middle, Hatim = right.
Source person centre x (1280 wide): left 317, middle 617, right 933.
"""

FOCUS_X = {"left": 317, "mid": 617, "right": 933, "wide": 640}
FOCUS_Y = 330  # roughly chest/face area; keeps heads in frame when zoomed

# (label, src_in, src_out, focus, zoom_start, zoom_end)
SEGMENTS = [
    ("HOOK: soalan utama",            28.55, 34.85, "mid",   1.38, 1.52),
    ("Salam",                          5.10,  7.30, "wide",  1.00, 1.04),
    ("Intro Amsyar",                   7.85, 10.65, "mid",   1.30, 1.34),
    ("Intro Zarif",                   11.50, 14.10, "left",  1.30, 1.34),
    ("Intro Hatim",                   14.10, 16.40, "right", 1.30, 1.34),
    ("Topik: Tugasan 3",              16.85, 25.80, "wide",  1.00, 1.08),
    ("Objektif 1",                    36.05, 42.55, "left",  1.22, 1.26),
    ("Objektif 2",                    42.55, 49.35, "left",  1.32, 1.36),
    ("Objektif 3",                    49.35, 56.70, "left",  1.22, 1.27),
    ("Peranan (a)",                   58.45, 63.50, "right", 1.22, 1.25),
    ("Peranan (b)",                   63.95, 72.20, "right", 1.30, 1.34),
    ("Outro: mari kita mulakan",      74.35, 75.90, "wide",  1.00, 1.10),
]

# Removed from source:
#   0.00-5.10   pre-roll (setting up, silence)
#   25.80-28.55 "Persoalan kami mudah" -> question moved to the front as the hook
#   28.55-34.85 question itself is used ONCE (as hook), not repeated in the body
#   34.85-36.05 / 56.70-58.45 / 72.20-74.35  dead air between lines
#   63.50-63.95 pause before "Dan Zarif..."
#   75.90-92.17 retakes ("Mari mulakan", "Amsyar tak ingat ayat", 3x "Mari kita mulakan")

# Caption spelling fixes for Whisper mishears
CORRECTIONS = {
    "Jawa": "Jauh",
    "Pesaalan": "Persoalan",
    "mengenalpasti": "mengenal pasti",
    "Uzdik": "",  # surname uncertain -> left out of captions until confirmed
    "Iaitu": "iaitu",  # capital I looks like "l" in Inter
}

# Overlay events, in SOURCE time (mapped to output time by the renderer)
EVENTS = {
    "hook_tag": 28.70,
    "flash_after_hook": 34.85,
    "lt_amsyar": 8.00,
    "lt_zarif": 11.60,
    "lt_hatim": 14.20,
    "title_card": 21.00,
    "obj_header": 36.30,
    "obj_1": 38.20,
    "obj_2": 42.60,
    "obj_3": 49.40,
    "roles_header": 58.60,
    "role_amsyar": 61.50,
    "role_zarif": 64.20,
    "role_hatim": 67.80,
    "role_safety": 70.50,
    "outro": 74.60,
}
