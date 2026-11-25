import random

VOICE = "af_nova"
SPEED = 0.98
MOOD_SP = {"surprised": 0.03, "curious": 0.015, "amused": 0.03, "calm": 0.0, "serious": -0.035, "warm": -0.015}
MOOD_GAP = {"surprised": (0.30, 0.42), "curious": (0.22, 0.32), "amused": (0.20, 0.30), "calm": (0.22, 0.32), "serious": (0.32, 0.45), "warm": (0.25, 0.35)}

_R = [
    ("curious", "Where does the six point two percent on your paycheck actually go?", "Where does the 6.2% on your paycheck actually go?"),
    ("calm", "On a sixty thousand dollar salary, that's three thousand, seven hundred twenty a year, from you.", "On a $60,000 salary, that's $3,720 a year from you."),
    ("surprised", "Your employer matches it. Seven thousand, four hundred forty in total.", "Your employer matches it: $7,440 in total."),
    ("serious", "And none of it goes into an account with your name on it.", "None of it goes into an account with your name on it."),
    ("calm", "It pays this month's checks... to nearly seventy-two million people.", "It pays this month's checks, to nearly 72 million people."),
    ("calm", "About eighty-five cents of each dollar funds retirement and survivor benefits. The rest, disability.", "About 85 cents of each dollar funds retirement and survivor benefits. The rest, disability."),
    ("curious", "So what do you get? Credits. One for every one thousand, nine hundred seventy dollars you earn, up to four a year.", "What do you get? Credits: one per $1,970 earned in 2027, up to 4 a year."),
    ("warm", "Forty credits, about ten years of work, and you qualify for your own check.", "40 credits, about ten years of work, and you qualify for your own check."),
    ("warm", "So your six point two pays for today's checks... and earns your spot for later.", "Your 6.2% pays today's checks and earns your spot for later."),
]

_rng = random.Random(915)
L = []
for i, (mood, text, cap) in enumerate(_R):
    sp = round(min(1.08, max(0.85, SPEED + MOOD_SP[mood] + _rng.uniform(-0.01, 0.01))), 3)
    if i == 0:
        sp = round(SPEED + 0.03, 3)
    L.append(dict(i=i, mood=mood, text=text, cap=cap, voice=VOICE, speed=sp, gap=round(_rng.uniform(*MOOD_GAP[mood]), 2)))
