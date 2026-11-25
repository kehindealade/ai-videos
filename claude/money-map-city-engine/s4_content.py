import random

VOICE = "af_jessica"
SPEED = 0.99
MOOD_SP = {"surprised": 0.03, "curious": 0.015, "amused": 0.03, "calm": 0.0, "serious": -0.035, "warm": -0.015}
MOOD_GAP = {"surprised": (0.30, 0.42), "curious": (0.22, 0.32), "amused": (0.20, 0.30), "calm": (0.22, 0.32), "serious": (0.32, 0.45), "warm": (0.25, 0.35)}

_R = [
    ('curious', 'Your card gives you one and a half percent back. So who is actually paying for that?', '1.5% back. Who is actually paying for it?'),
    ('calm', 'Start with a hundred-dollar sale. The store pays about two dollars fifty-two in fees.', '$100 sale. The store pays about $2.52 in fees.'),
    ('curious', 'Your bank keeps about one ninety of that, and sends you a dollar fifty.', 'Your bank gets about $1.90 and sends you $1.50.'),
    ('serious', "The store has to cover that fee somewhere. Often, it's in the price tag.", 'The store has to cover that fee somewhere. Often, the price tag.'),
    ('surprised', 'A July twenty twenty-six working paper estimates that moves about thirty billion dollars a year from cash and debit shoppers to card users.', 'A July 2026 paper estimates about $30B a year moves from cash and debit shoppers to card users.'),
    ('calm', "It's one estimate, and it assumes stores pass the fees into every price.", 'One estimate. It assumes stores pass fees into every price.'),
    ('warm', 'Real money. Not free money. Follow the money.', 'Real money. Not free money.'),
]

_rng = random.Random(612)
L = []
for i, (mood, text, cap) in enumerate(_R):
    sp = round(min(1.08, max(0.85, SPEED + MOOD_SP[mood] + _rng.uniform(-0.01, 0.01))), 3)
    if i == 0:
        sp = round(SPEED + 0.03, 3)
    L.append(dict(i=i, mood=mood, text=text, cap=cap, voice=VOICE, speed=sp, gap=round(_rng.uniform(*MOOD_GAP[mood]), 2)))
