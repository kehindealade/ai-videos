import random

VOICE = "af_sky"
SPEED = 0.98
MOOD_SP = {"surprised": 0.03, "curious": 0.015, "amused": 0.03, "calm": 0.0, "serious": -0.035, "warm": -0.015}
MOOD_GAP = {"surprised": (0.30, 0.42), "curious": (0.22, 0.32), "amused": (0.20, 0.30), "calm": (0.22, 0.32), "serious": (0.32, 0.45), "warm": (0.25, 0.35)}

_R = [
    ('surprised', "Three thousand dollars on a credit card. Pay only the minimum. How long until it's gone?", '$3,000 on a card. Pay only the minimum. How long?'),
    ('calm', 'Month one, the minimum is about eighty-six dollars.', 'Month one, the minimum: about $86.'),
    ('curious', 'But about fifty-six of that is just interest. Only thirty dollars touches what you owe.', 'About $56 of it is interest. Only $30 reduces the debt.'),
    ('serious', 'So the tank drains slowly. After a full year, you have cleared only about three hundred forty dollars.', 'After a full year: only about $340 cleared.'),
    ('surprised', 'Pay only the minimum, and it takes about twelve years.', 'Minimum only: about 12 years.'),
    ('serious', "You'd pay roughly four thousand dollars in interest. On a three-thousand-dollar balance.", 'Roughly $4,000 in interest on a $3,000 balance.'),
    ('curious', 'About seven thousand dollars, for three thousand dollars of stuff.', 'About $7,000 paid for $3,000 of stuff.'),
    ('calm', "Rough example. Twenty-two percent interest, no new purchases. Your card's rules will differ.", 'Rough example: 22% APR, no new purchases. Your card differs.'),
    ('warm', 'Anything above the minimum goes straight at what you owe. Follow the money.', 'Anything above the minimum goes straight at the debt.'),
]

_rng = random.Random(611)
L = []
for i, (mood, text, cap) in enumerate(_R):
    sp = round(min(1.08, max(0.85, SPEED + MOOD_SP[mood] + _rng.uniform(-0.01, 0.01))), 3)
    if i == 0:
        sp = round(SPEED + 0.03, 3)
    L.append(dict(i=i, mood=mood, text=text, cap=cap, voice=VOICE, speed=sp, gap=round(_rng.uniform(*MOOD_GAP[mood]), 2)))
