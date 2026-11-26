import stmt
from banks import S

stmt.set_portrait(["dep", "int", "od"])

T = "THE $39 COFFEE"


def scenes():
    return [
        S("text", T, ["This coffee cost thirty nine dollars.", "Here's how your bank did it."],
          lines=[{"t": "This coffee cost $39.", "cue": "0", "hl": True}, {"t": "Here's how your bank did it.", "cue": "1", "scale": 0.6, "col": "muted"}]),
        S("receipt", T, ["You buy a four dollar coffee with three dollars in your account.",
                         "The bank covers the dollar you're missing.", "Then it charges you for the favour. About thirty five dollars."],
          title="ONE COFFEE", w=760,
          rows=[{"t": "COFFEE", "amt": "$4.00", "cue": "0:four"}, {"t": "OVERDRAFT FEE", "amt": "$35.00", "cue": "2:charges", "col": "red", "acue": "2:thirty"}],
          total={"label": "TOTAL", "t": "$39.00", "cue": "2:thirty+0.6"}, ledger=[{"row": "od", "cue": "2:thirty"}]),
        S("num", T, ["On a thousand dollars in an average savings account, that one fee wipes out about nine years of interest."],
          items=[{"s": "9 years", "label": "of interest on $1,000, gone in one fee", "cue": "0:nine", "col": "red"}],
          ledger=[{"row": "dep", "cue": "0:thousand"}, {"row": "int", "cue": "0:average"}],
          src="$35 fee ÷ $3.80 a year at the FDIC average rate"),
        S("num", T, ["In the first half of this year, larger American banks collected nearly three billion dollars in fees like this."],
          items=[{"v": 2.96, "pre": "$", "suf": "B", "dec": 2, "label": "overdraft and similar fees, larger US banks, Jan to Jun 2026", "cue": "0:nearly", "col": "red"}],
          src="US bank regulatory filings, first half of 2026"),
        S("text", T, ["And it falls mostly on people who are already short of money.", "A few banks have dropped the fee. Many have not."],
          lines=[{"t": "It falls mostly on people already short of money.", "cue": "0", "hl": True},
                 {"t": "A few banks dropped it. Many have not.", "cue": "1", "scale": 0.6, "col": "muted"}]),
        S("end", "", ["That's just one of four ways banks make money. The full video is on the channel.", "Follow the money."],
          cue="1", cue2="0", label="FULL VIDEO", next="How Banks Make Money From Your Savings"),
    ]


def get():
    return scenes(), "am_eric", 0.98
