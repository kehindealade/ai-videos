import random

VOICE = "af_river"
BASE = 0.94
MOOD_SP = {"surprised": 0.035, "curious": 0.015, "amused": 0.03, "calm": 0.0, "serious": -0.04, "warm": -0.015}
MOOD_GAP = {"surprised": (0.45, 0.60), "curious": (0.30, 0.45), "amused": (0.25, 0.40), "calm": (0.28, 0.42), "serious": (0.45, 0.60), "warm": (0.33, 0.48)}

CH = {1: "THE PLAYERS", 2: "THE SWIPE", 3: "THE SPLIT", 4: "THE REWARDS", 5: "WHO PAYS", 6: "THE OTHER MONEY", 7: "THE POINTS", 8: "A YEAR OF IT"}

_R = [
    ("hook", 0, None, "surprised", "Same jacket. Same price tag. One shopper taps a card, and gets a dollar fifty back.", "Same jacket. Same price tag. One shopper taps a card and gets $1.50 back."),
    ("hook", 1, None, "serious", "The shopper behind them pays cash... and gets nothing.", "The shopper behind them pays cash and gets nothing."),
    ("hook", 2, None, "curious", "So where does that dollar fifty come from?", "So where does that $1.50 come from?"),
    ("hook", 3, None, "warm", "Let's follow one hundred dollars through the city, and see who pays what.", "Let's follow $100 through the city and see who pays what."),

    ("play", 0, 1, "calm", "Five players are involved every time you swipe.", "Five players are involved every time you swipe."),
    ("play", 1, None, "calm", "You. The store. And the store's bank, called the acquirer.", "You. The store. And the store's bank, called the acquirer."),
    ("play", 2, None, "calm", "The card network, the company whose logo is on your card. And your own bank, called the issuer.", "The card network, whose logo is on your card. And your own bank, the issuer."),
    ("play", 3, None, "curious", "Here's the part most people miss. For most cards, the bank lends you the money, and the network just runs the roads between the banks.", "For most cards, the bank lends you the money. The network just runs the roads between the banks."),
    ("play", 4, None, "warm", "Okay. Let's buy something.", "Okay. Let's buy something."),

    ("swipe", 0, 2, "warm", "You tap your card for a hundred-dollar jacket.", "You tap your card for a $100 jacket."),
    ("swipe", 1, None, "curious", "In about two seconds, the store's bank asks the network, the network asks your bank, and your bank says yes.", "In about two seconds: the store's bank asks the network, the network asks your bank, your bank says yes."),
    ("swipe", 2, None, "serious", "But nothing has been paid yet. That yes is just a promise.", "But nothing has been paid yet. That yes is just a promise."),
    ("swipe", 3, None, "calm", "The real money moves later, usually within a day or two, in a batch with the store's other sales.", "The real money moves later, usually within a day or two, in a batch with the store's other sales."),

    ("split", 0, 3, "surprised", "And that's when the hundred dollars gets sliced.", "That's when the $100 gets sliced."),
    ("split", 1, None, "calm", "First slice, your bank. It keeps a fee called interchange. For a typical card, it's around one point nine percent, so about a dollar ninety.", "First slice, your bank: a fee called interchange. Typically around 1.9%, about $1.90."),
    ("split", 2, None, "curious", "The card networks publish those rates, and they depend on the card. A basic card, a rewards card, a premium card... the fancier the card, the higher the fee.", "Networks publish the rates, and they depend on the card. The fancier the card, the higher the fee."),
    ("split", 3, None, "calm", "Second slice, the network. Its own fee is much smaller. Around fourteen cents.", "Second slice, the network: a much smaller fee, around $0.14."),
    ("split", 4, None, "calm", "Third slice, the store's bank, or payment processor. Say, forty-eight cents.", "Third slice, the store's bank or processor: say $0.48."),
    ("split", 5, None, "serious", "Add it up, and the store receives about ninety-seven dollars and fifty cents, for a hundred-dollar sale.", "Add it up: the store gets about $97.50 for a $100 sale."),
    ("split", 6, None, "curious", "Rates differ by card and by store, so treat these as a typical example, not a receipt.", "Rates differ by card and store. Treat these as a typical example, not a receipt."),

    ("rew", 0, 4, "warm", "Now follow your bank's dollar ninety.", "Now follow your bank's $1.90."),
    ("rew", 1, None, "curious", "Say your card gives one and a half percent back. That's a dollar fifty, sent to you as points or cash.", "Say your card gives 1.5% back: $1.50, as points or cash."),
    ("rew", 2, None, "calm", "What's left, about forty cents, helps cover fraud, running the card, and profit.", "What's left, about $0.40, helps cover fraud, running the card, and profit."),
    ("rew", 3, None, "calm", "Part of that is protection. By federal law, you're liable for at most fifty dollars of unauthorized charges, and many issuers advertise zero.", "Part of it is protection. By federal law, you're liable for at most $50 of unauthorized charges, and many issuers advertise $0."),
    ("rew", 4, None, "curious", "That's also why the richest rewards usually sit on premium cards. Stores pay more to accept them, and cardholders often pay an annual fee too.", "That's why the richest rewards usually sit on premium cards: stores pay more to accept them, and cardholders often pay an annual fee."),
    ("rew", 5, None, "amused", "So your points are real money. They just don't come out of thin air.", "So your points are real money. They just don't come out of thin air."),

    ("pays", 0, 5, "curious", "Back at the store, someone has to cover those two and a half dollars.", "Back at the store, someone has to cover those $2.52."),
    ("pays", 1, None, "calm", "Most stores put one price on the jacket, no matter how you pay.", "Most stores put one price on the jacket, no matter how you pay."),
    ("pays", 2, None, "calm", "So a store can fold the cost of accepting cards into prices for everyone. That's the idea behind a July twenty twenty-six paper from the National Bureau of Economic Research.", "A store can fold the cost of accepting cards into prices for everyone. That's the idea behind a July 2026 paper from the NBER."),
    ("pays", 3, None, "serious", "Its economists estimate that about thirty billion dollars a year effectively moves from cash and debit shoppers to credit card users.", "Its economists estimate about $30 billion a year moves from cash and debit shoppers to credit card users."),
    ("pays", 4, None, "curious", "That estimate assumes stores pass the fees into every price. And it shrinks by about a quarter, because shoppers who pay different ways often shop at different stores.", "It assumes stores pass fees into every price, and shrinks by about a quarter, since shoppers often use different stores."),
    ("pays", 5, None, "calm", "Premium cards matter here. They grew from fifteen percent of credit card spending in two thousand six, to sixty percent in twenty twenty-two.", "Premium cards grew from 15% of credit card spending in 2006 to 60% in 2022."),
    ("pays", 6, None, "calm", "Some stores add a surcharge, or offer a cash discount, where the rules allow it. Either way, the fee gets paid by someone.", "Some stores add a surcharge or offer a cash discount, where the rules allow it. Either way, someone pays the fee."),

    ("other", 0, 6, "curious", "Swipe fees aren't the only way a card makes money.", "Swipe fees aren't the only way a card makes money."),
    ("other", 1, None, "calm", "A second stream is interest. The Federal Reserve puts the average rate at about twenty-two percent, on accounts that were charged interest.", "A second stream is interest. The Fed puts the average rate at about 22% on accounts charged interest."),
    ("other", 2, None, "calm", "Interest only applies if you carry a balance. Pay the full statement balance by the due date, and you generally pay none on purchases. Issuers have to send the bill at least twenty-one days before it's due.", "Interest only applies if you carry a balance. Pay the full statement balance by the due date and you generally pay none on purchases. Bills must go out at least 21 days before they're due."),
    ("other", 3, None, "serious", "In twenty twenty-four, the Consumer Financial Protection Bureau counted about a hundred sixty billion dollars in card interest charges.", "In 2024, the CFPB counted about $160 billion in card interest charges."),
    ("other", 4, None, "calm", "For scale, banks collected nearly sixty-six billion dollars in swipe fees in twenty twenty-five, credit and debit combined, according to the St. Louis Fed.", "For scale: banks collected nearly $66 billion in swipe fees in 2025, credit and debit combined (St. Louis Fed)."),
    ("other", 5, None, "calm", "A third stream is annual fees. Many cards charge nothing. The top premium cards charge seven ninety-five to eight ninety-five a year.", "A third stream: annual fees. Many cards charge $0. Top premium cards charge $795 to $895 a year."),
    ("other", 6, None, "curious", "Now, a labelled example. Spend one thousand dollars on a card paying two percent back, and you earn twenty dollars.", "Example: spend $1,000 on a card paying 2% back, and you earn $20."),
    ("other", 7, None, "surprised", "Carry that same thousand dollars for a whole year at twenty-two percent, and the interest is about two hundred twenty.", "Carry that $1,000 for a whole year at 22%, and the interest is about $220."),
    ("other", 8, None, "calm", "And to earn back a seven-ninety-five fee at three percent, you'd need about twenty-six thousand, five hundred dollars of spending, before counting any credits and perks.", "To earn back a $795 fee at 3%, you'd need about $26,500 of spending, before any credits and perks."),

    ("pts", 0, 7, "warm", "One last piece. Points aren't dollars.", "One last piece: points aren't dollars."),
    ("pts", 1, None, "curious", "A point can be worth about one cent as cash, and up to around two cents on travel, depending on how you redeem it.", "A point can be worth about 1 cent as cash, and up to around 2 cents on travel, depending on how you redeem it."),
    ("pts", 2, None, "serious", "And the bank sets the rules, and can change them.", "And the bank sets the rules, and can change them."),

    ("year", 0, 8, "warm", "Now put it together over a year. Say someone spends twenty thousand dollars on a one-and-a-half percent card.", "Put it together over a year. Say someone spends $20,000 on a 1.5% card."),
    ("year", 1, None, "curious", "They earn about three hundred dollars back. Meanwhile, the stores that took those payments paid about five hundred dollars in fees, in our example.", "They earn about $300 back. The stores that took those payments paid about $500 in fees, in our example."),
    ("year", 2, None, "calm", "Your bank's share of that, about three hundred eighty, covers the rewards, plus fraud losses, running the card, and profit.", "Your bank's share, about $380, covers the rewards, plus fraud losses, running the card, and profit."),

    ("recap", 0, None, "warm", "So here's the whole loop. You swipe. The store pays a slice.", "Here's the loop: you swipe, and the store pays a slice."),
    ("recap", 1, None, "calm", "Your bank keeps part of it to fund rewards and run the card. The network and the store's bank take smaller cuts.", "Your bank keeps part to fund rewards and run the card. The network and the store's bank take smaller cuts."),
    ("recap", 2, None, "calm", "The store can build that cost into prices. And if you carry a balance, interest is the bigger pile.", "The store can build that cost into prices. If you carry a balance, interest is the bigger pile."),
    ("recap", 3, None, "warm", "Rewards are real money. They're just not free money. How the math works out depends on how you use the card.", "Rewards are real money. They're just not free money. How the math works out depends on how you use the card."),
    ("end", 0, None, "warm", "Next on Money Map, how mortgage rates work. Follow the money.", "Next on Money Map: how mortgage rates work. Follow the money."),
]

_rng = random.Random(4417)
L = []
for sc, st, ch, mood, text, cap in _R:
    sp = round(min(1.08, max(0.85, BASE + MOOD_SP[mood] + _rng.uniform(-0.012, 0.012))), 3)
    if sc == "hook" and st == 0:
        sp = round(min(1.0, BASE + 0.02), 3)
    g = round(_rng.uniform(*MOOD_GAP[mood]), 2)
    p = {"step": st}
    if ch:
        p["ch"] = ch
    L.append(dict(scene=sc, p=p, mood=mood, text=text, cap=cap, voice=VOICE, speed=sp, gap=g))
VOICE_ = VOICE
SPEED = BASE

_CB = {0: "Same jacket. Same price tag. One shopper taps a card... and gets a dollar fifty back.",
       1: "The person right behind them pays cash. And gets... nothing.",
       2: "Huh. So where does that dollar fifty actually come from?",
       8: "Okay. [chuckle] Let's buy something."}
for _i, _t in _CB.items():
    L[_i]["cb"] = _t
