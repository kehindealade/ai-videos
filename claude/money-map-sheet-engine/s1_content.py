import random

VOICE = "af_alloy"
SPEED = 0.99
MOOD_SP = {"surprised": 0.03, "curious": 0.015, "amused": 0.03, "calm": 0.0, "serious": -0.035, "warm": -0.015}
MOOD_GAP = {"surprised": (0.30, 0.42), "curious": (0.22, 0.32), "amused": (0.20, 0.30), "calm": (0.22, 0.32), "serious": (0.32, 0.45), "warm": (0.25, 0.35)}

_R = [
    ("serious", "Social Security just gave everyone a raise. Medicare took some of it back.", "Social Security gave a raise. Medicare took some back."),
    ("calm", "In twenty twenty-seven, checks go up three point six percent.", "In 2027, checks go up 3.6%."),
    ("curious", "For the average retiree, that's two thousand ninety-five... to two thousand, one hundred seventy.", "Average retiree: $2,095 to $2,170."),
    ("warm", "Seventy-five dollars more a month.", "$75 more a month."),
    ("surprised", "But Medicare Part B went up too. Six dollars and fifty cents.", "But Medicare Part B went up too: $6.50."),
    ("calm", "And for most people, that premium comes straight out of the check.", "For most people, it comes straight out of the check."),
    ("serious", "So the raise you actually see is about sixty-eight fifty.", "So the raise you actually see: about $68.50."),
    ("curious", "And the whole premium? Two hundred nine dollars and forty cents. Every month.", "And the whole premium? $209.40, every month."),
    ("calm", "Two thousand, one hundred seventy goes in. About one thousand, nine hundred sixty lands.", "$2,170 goes in. About $1,960 lands."),
    ("warm", "That's the real raise... and the real check.", "That's the real raise, and the real check."),
]

_rng = random.Random(408)
L = []
for i, (mood, text, cap) in enumerate(_R):
    sp = round(min(1.08, max(0.85, SPEED + MOOD_SP[mood] + _rng.uniform(-0.01, 0.01))), 3)
    if i == 0:
        sp = round(SPEED + 0.03, 3)
    L.append(dict(i=i, mood=mood, text=text, cap=cap, voice=VOICE, speed=sp, gap=round(_rng.uniform(*MOOD_GAP[mood]), 2)))
