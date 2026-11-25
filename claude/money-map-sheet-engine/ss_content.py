import random

VOICE = "bf_alice"
BASE = 0.90
MOOD_SP = {"surprised": 0.035, "curious": 0.015, "amused": 0.03, "calm": 0.0, "serious": -0.035, "warm": -0.015}
MOOD_GAP = {"surprised": (0.45, 0.60), "curious": (0.30, 0.45), "amused": (0.25, 0.40), "calm": (0.30, 0.45), "serious": (0.45, 0.60), "warm": (0.35, 0.50)}

CH = {1: "MONEY IN", 2: "YOUR RECORD", 3: "THE FORMULA", 4: "YOUR AGE", 5: "RAISES", 6: "THE DEPOSIT"}

_R = [
    ("hook", 0, None, "surprised", "Some of the dollars you earn count six times more than others.", "Some dollars you earn count six times more than others."),
    ("hook", 1, None, "curious", "Not on your paycheck... in your Social Security check.", "Not on your paycheck. In your Social Security check."),
    ("hook", 2, None, "serious", "Nearly seventy-two million people get one, and every one of them comes out of the same formula.", "Nearly 72 million people get one, and every one comes out of the same formula."),
    ("hook", 3, None, "warm", "So let's build one, cell by cell. From your first paycheck to the money that actually lands in your account.", "So let's build one, cell by cell, from your first paycheck to the money that lands in your account."),

    ("pay", 0, 1, "calm", "Start with the paycheck. Six point two percent of your pay goes to Social Security.", "Start with the paycheck. 6.2% of your pay goes to Social Security."),
    ("pay", 1, None, "curious", "Your employer pays another six point two on top. That's twelve point four percent in total, and if you're self-employed, you pay both halves.", "Your employer pays another 6.2% on top: 12.4% in total. Self-employed people pay both halves."),
    ("pay", 2, None, "calm", "Medicare takes one point four five percent from each side too, and that one has no ceiling.", "Medicare takes 1.45% from each side too, and that one has no ceiling."),
    ("pay", 3, None, "surprised", "Social Security does have a ceiling. In twenty twenty-seven, pay above one hundred ninety-two thousand, three hundred dollars isn't taxed for it at all.", "Social Security does have a ceiling. In 2027, pay above $192,300 isn't taxed for it at all."),
    ("pay", 4, None, "curious", "Here's the thing, though... that money doesn't sit in an account with your name on it.", "Here's the thing: that money doesn't sit in an account with your name on it."),
    ("pay", 5, None, "calm", "It's pay as you go. Today's workers pay today's checks, and anything extra is lent to the Treasury, inside two trust funds.", "It's pay as you go. Today's workers pay today's checks, and any extra is lent to the Treasury inside two trust funds."),
    ("pay", 6, None, "calm", "About eighty-five cents of each tax dollar goes to the retirement and survivors fund. The rest goes to disability.", "About 85 cents of each tax dollar goes to the retirement and survivors fund. The rest goes to disability."),
    ("pay", 7, None, "serious", "In twenty twenty-five, payroll taxes were about ninety-one percent of the program's income. Interest, and taxes on benefits, made up the rest.", "In 2025, payroll taxes were about 91% of the program's income. Interest and taxes on benefits made up the rest."),

    ("rec", 0, 2, "warm", "While you pay, you're also earning credits. In twenty twenty-seven, every one thousand, nine hundred seventy dollars you earn is one credit.", "While you pay, you also earn credits. In 2027, every $1,970 you earn is one credit."),
    ("rec", 1, None, "curious", "You can earn four a year, and you need forty. So, about ten years of work, and you qualify.", "You can earn 4 a year, and you need 40. About ten years of work, and you qualify."),
    ("rec", 2, None, "calm", "Qualifying gets you in. How much you get depends on your earnings record.", "Qualifying gets you in. How much you get depends on your earnings record."),
    ("rec", 3, None, "calm", "Social Security looks at every year you worked... and keeps your thirty-five highest.", "Social Security looks at every year you worked and keeps your 35 highest."),
    ("rec", 4, None, "curious", "Older years get scaled up for wage growth, so a salary from the nineties isn't judged in nineties dollars.", "Older years are scaled up for wage growth, so a 1990s salary isn't judged in 1990s dollars."),
    ("rec", 5, None, "serious", "Worked fewer than thirty-five years? The missing years count as zeros.", "Worked fewer than 35 years? The missing years count as zeros."),
    ("rec", 6, None, "calm", "Add up those thirty-five years, divide by four hundred twenty months, and you get one number. Your average indexed monthly earnings.", "Add up the 35 years, divide by 420 months, and you get one number: your average indexed monthly earnings."),
    ("rec", 7, None, "warm", "Let's use an example. Say that number is five thousand dollars a month. Roughly sixty thousand a year, in today's money.", "Example: say that number is $5,000 a month. Roughly $60,000 a year in today's money."),
    ("rec", 8, None, "warm", "And you can see your own record, year by year, in a free my Social Security account at S S A dot gov.", "You can see your own record, year by year, in a free my Social Security account at ssa.gov."),

    ("form", 0, 3, "surprised", "Now the part that surprises people. The formula doesn't take one flat percentage.", "Now the part that surprises people. The formula doesn't take one flat percentage."),
    ("form", 1, None, "curious", "It cuts your average into three slices.", "It cuts your average into three slices."),
    ("form", 2, None, "calm", "On the first one thousand, three hundred forty dollars, you get ninety percent.", "On the first $1,340, you get 90%."),
    ("form", 3, None, "calm", "From there, up to eight thousand and seventy-seven, you get thirty-two percent.", "From there up to $8,077, you get 32%."),
    ("form", 4, None, "serious", "And above that? Just fifteen percent.", "And above that? Just 15%."),
    ("form", 5, None, "amused", "That's the six times from the start. Ninety cents, against fifteen.", "That's the six times from the start: 90 cents against 15."),
    ("form", 6, None, "calm", "For our example, ninety percent of the first slice is one thousand, two hundred six dollars. Thirty-two percent of the next three thousand, six hundred sixty is one thousand, one hundred seventy-one.", "For our example: 90% of the first slice is $1,206. 32% of the next $3,660 is $1,171."),
    ("form", 7, None, "warm", "Add them up. Two thousand, three hundred seventy-seven dollars a month. That's the primary insurance amount... the check at full retirement age.", "Add them up: $2,377 a month. That's the primary insurance amount, the check at full retirement age."),
    ("form", 8, None, "curious", "Run three different earners through the same formula, and you can see why it was built this way.", "Run three different earners through the same formula and you can see why it was built this way."),
    ("form", 9, None, "calm", "A lower earner gets back about ninety percent of their average. Our example, about forty-eight. A high earner, about thirty-seven.", "A lower earner gets back about 90% of their average. Our example, about 48%. A high earner, about 37%."),
    ("form", 10, None, "serious", "And there's a ceiling here too. Even with top earnings for thirty-five years, the most anyone gets at full retirement age in twenty twenty-seven is four thousand, one hundred eighty-eight dollars.", "There's a ceiling here too. The most anyone gets at full retirement age in 2027 is $4,188 a month."),

    ("age", 0, 4, "calm", "Next cell. When you claim. For anyone born in nineteen sixty or later, full retirement age is sixty-seven.", "Next cell: when you claim. For anyone born in 1960 or later, full retirement age is 67."),
    ("age", 1, None, "serious", "Claim at sixty-two, and the check is cut by thirty percent... for life.", "Claim at 62, and the check is cut by 30%, for life."),
    ("age", 2, None, "curious", "Wait past sixty-seven, and it grows eight percent for every year, up to age seventy.", "Wait past 67 and it grows 8% for every year, up to age 70."),
    ("age", 3, None, "calm", "Same person, same record. One thousand, six hundred sixty-four at sixty-two. Two thousand, nine hundred forty-seven at seventy.", "Same person, same record: $1,664 at 62. $2,947 at 70."),
    ("age", 4, None, "calm", "Claim early and keep working? In twenty twenty-seven, above twenty-five thousand, five hundred sixty dollars, one dollar is held back for every two you earn, until the year you reach full retirement age.", "Claim early and keep working? In 2027, above $25,560, $1 is held back for every $2 you earn, until the year you reach full retirement age."),
    ("age", 5, None, "warm", "None of this is one right answer for everyone. It's a trade. A bigger check, or more years of checks.", "There's no one right answer for everyone. It's a trade: a bigger check, or more years of checks."),
    ("age", 6, None, "calm", "One more row for couples. A spouse can get up to half of the worker's full amount, based on that worker's record.", "One more row for couples: a spouse can get up to half of the worker's full amount, based on that worker's record."),

    ("cola", 0, 5, "warm", "Once the checks start, they get a raise every January. The cost of living adjustment.", "Once checks start, they get a raise every January: the cost-of-living adjustment."),
    ("cola", 1, None, "calm", "It follows an inflation index for workers. And for twenty twenty-seven, it's three point six percent.", "It follows an inflation index for workers. For 2027, it's 3.6%."),
    ("cola", 2, None, "curious", "Huh... it moves around a lot. Eight point seven percent in twenty twenty-three. Two point eight this year.", "It moves around a lot: 8.7% in 2023, 2.8% in 2026."),
    ("cola", 3, None, "calm", "For the average retired worker, two thousand ninety-five dollars becomes two thousand, one hundred seventy. About seventy-five dollars more.", "For the average retired worker, $2,095 becomes $2,170. About $75 more."),
    ("cola", 4, None, "curious", "And because it's a percentage, bigger checks get bigger raises in dollars.", "Because it's a percentage, bigger checks get bigger raises in dollars."),

    ("dep", 0, 6, "surprised", "But the check still isn't what lands in the bank.", "But the check still isn't what lands in the bank."),
    ("dep", 1, None, "calm", "For most people on Medicare who also get Social Security, the Part B premium comes straight out of the check.", "For most people on Medicare who also get Social Security, the Part B premium comes straight out of the check."),
    ("dep", 2, None, "serious", "In twenty twenty-seven, that's two hundred nine dollars and forty cents a month. Six fifty more than this year.", "In 2027 that's $209.40 a month, $6.50 more than this year."),
    ("dep", 3, None, "warm", "So the average check of two thousand, one hundred seventy turns into a deposit of about one thousand, nine hundred sixty.", "So the average check of $2,170 turns into a deposit of about $1,960."),
    ("dep", 4, None, "calm", "And depending on your other income, up to eighty-five percent of the benefit can count as taxable income.", "And depending on your other income, up to 85% of the benefit can count as taxable income."),
    ("dep", 5, None, "calm", "Some higher-income people pay more for Part B, based on their income from two years earlier.", "Some higher-income people pay more for Part B, based on their income from two years earlier."),

    ("recap", 0, None, "warm", "So that's the whole sheet. Pay in. Earn credits. Average your best thirty-five years. Run the three-slice formula. Adjust for age. Add the yearly raise. Take out Part B.", "That's the whole sheet: pay in, earn credits, average your best 35 years, run the three-slice formula, adjust for age, add the raise, take out Part B."),
    ("recap", 1, None, "serious", "Nearly seventy-two million checks... and they all come from those few rows.", "Nearly 72 million checks, and they all come from those few rows."),
    ("end", 0, None, "warm", "Next on Money Map, who really pays for your credit card points. Follow the money.", "Next on Money Map: who really pays for your credit card points. Follow the money."),
]

_rng = random.Random(2711)
L = []
for sc, st, ch, mood, text, cap in _R:
    sp = round(min(1.08, max(0.85, BASE + MOOD_SP[mood] + _rng.uniform(-0.012, 0.012))), 3)
    if sc == "hook" and st == 0:
        sp = round(BASE + 0.05, 3)
    g = round(_rng.uniform(*MOOD_GAP[mood]), 2)
    p = {"step": st}
    if ch:
        p["ch"] = ch
    L.append(dict(scene=sc, p=p, mood=mood, text=text, cap=cap, voice=VOICE, speed=sp, gap=g))
VOICE_ = VOICE
SPEED = BASE
