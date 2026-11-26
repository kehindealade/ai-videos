import stmt
from banks import S, MARKS

stmt.set_portrait(["dep", "int", "cc"])

T = "THE GAP"


def scenes():
    return [
        S("num", T, ["Put a thousand dollars in a savings account for a year.", "Your bank pays you about three dollars and eighty cents."],
          items=[{"v": 3.80, "pre": "$", "dec": 2, "label": "what the bank pays you in a year", "cue": "1:three", "col": "green"}],
          ledger=[{"row": "dep", "cue": "0:thousand"}, {"row": "int", "cue": "1:three"}],
          src="FDIC average savings rate, Nov 2026"),
        S("num", T, ["Lend that same thousand dollars on a credit card, and the bank charges about two hundred and ten."],
          items=[{"v": 3.80, "pre": "$", "dec": 2, "label": "what it pays you", "cue": -1, "col": "green", "count": False},
                 {"v": 210, "pre": "$", "label": "what it charges a borrower", "cue": "0:two hundred", "col": "red"}],
          ledger=[{"row": "cc", "cue": "0:two hundred"}], src="Federal Reserve G.19, Q2 2026"),
        S("rates", T, ["Home loans, around seven percent.", "Credit cards, about twenty one.", "Your savings? Less than half of one percent."],
          marks=[dict(MARKS[0], cue="0"), dict(MARKS[1], cue="0:seven"), dict(MARKS[2], cue="1"), dict(MARKS[3], cue="2:Less")]),
        S("rates", T, ["That gap is called the spread.", "It's the oldest way banks make money, and it's still the biggest."],
          cont=True, marks=[dict(m, cue=-1) for m in MARKS],
          bracket={"t": "THE SPREAD", "lo": 0.38, "hi": 20.94, "cue": "0:gap"}),
        S("text", T, ["Some online banks pay about ten times the average, on the very same money.",
                      "Your bank is counting on you not to check."],
          lines=[{"t": "Some banks pay about 10x more.", "cue": "0"},
                 {"t": "Yours is counting on you not to check.", "cue": "1", "hl": True, "col": "red"}]),
        S("end", "", ["That's one of four ways banks make money. The full breakdown is on the channel.", "Follow the money."],
          cue="1", cue2="0", label="FULL VIDEO", next="How Banks Make Money From Your Savings"),
    ]


def get():
    return scenes(), "bf_emma", 0.95
