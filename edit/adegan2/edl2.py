"""ADEGAN 2 edit decision list.

Sources:  talk = "ADEGAN 2 .MP4" (97s, Amsyar to camera)   jump = "ADEGAN 2 .MP4" (5.9s long-jump attempt)
Jump clip phases (jump seconds): run-up ..3.6 | takeoff ~3.73 | flight 3.78-4.2 | landing ~4.27
Slow-mo uses a motion-interpolated 120fps copy of the jump clip (rate 0.25 = 4x slower).
"""

# talk range kept (everything else removed):
#   0.00-5.58  "Okey, kita kembali lagi berdasarkan segmen tadi"  (weak opener -> replaced by hook)
#   93.45-95.25  pause, looking at phone
TALK_IN, TALK_OUT = 5.58, 93.45
# raw ending kept as-is (silent): hand gesture toward the pit + walk-off. The pause at 93.45-95.25
# (looking down at phone) is removed.
TAIL = (95.25, 97.20)
# hard cuts inside speech: stumble "kuasa letupan, letusan kaki" -> "kuasa letusan kaki"
CUTS = [(74.45, 75.42)]
GAP_MIN = 0.35      # pauses longer than this are tightened
GAP_KEEP = 0.22     # ...down to this much silence

TALK_FOCUS = (600, 330)
TALK_ZOOMS = (1.00, 1.15)   # alternate on every cut to hide jump cuts

# Programs on the jump clip: ("play", a, b, rate, zoom) / ("freeze", t, seconds, zoom)
HOOK = [
    ("play", 2.60, 3.55, 1.00, 1.45),
    ("play", 3.55, 3.85, 0.25, 1.70),
    ("freeze", 3.85, 1.00, 1.70),
    ("play", 3.85, 4.42, 0.30, 1.70),
]

# B-roll over Amsyar's voice: (key, talk source time where it starts, program)
BROLL = [
    ("b1_run", 27.60, [("play", 2.55, 3.62, 0.40, 1.45)]),
    ("b2_takeoff", 40.90, [("play", 3.45, 3.74, 0.25, 1.70), ("freeze", 3.74, 3.0, 1.70),
                           ("play", 3.74, 4.00, 0.25, 1.70)]),
    ("b3_flight", 49.30, [("play", 3.76, 4.20, 0.25, 1.70), ("freeze", 4.20, 0.6, 1.70)]),
    ("b4_landing", 55.30, [("play", 4.12, 4.27, 0.25, 1.70), ("freeze", 4.27, 2.4, 1.70),
                           ("play", 4.27, 4.60, 0.30, 1.70)]),
]

END_HOLD = 1.6
CARD_LEAD = 1.1   # end card appears this long before the raw footage ends (over the walk-off)

# Caption fixes. Whisper hallucinated "Dan yang ketiga, kekuatan kaki / Dan yang ketiga," at 83.4-84.9;
# a re-check of that chunk gives "...keseimbangan serta kelenturan pinggul".
DROP_WORDS = (83.35, 84.89)
INSERT_WORDS = [("serta", 84.45, 84.85)]
CORRECTIONS = {"kesimbangan": "keseimbangan", "Yaitu": "iaitu", "Iaitu": "iaitu"}

# Overlay events in TALK source time
EV = {
    "lt_amsyar": 5.70, "lt_out": 9.30,
    "fasa_header": 9.48,
    "fasa_1": 12.42, "fasa_2": 15.10, "fasa_3": 17.50, "fasa_4": 19.56, "fasa_out": 26.78,
    "p1": 23.36, "p1_chip": 32.40, "p2": 34.86, "p3": 49.30, "p4": 52.90,
    "p4_chip": 56.58, "p4_safe": 61.88, "phase_out": 63.18,
    "need_header": 67.70,
    "need_1": 72.16, "need_2": 74.06, "need_3": 78.10, "need_4": 80.54, "need_5": 82.80,
    "need_5b": 84.90, "closing_chip": 89.32,
}
