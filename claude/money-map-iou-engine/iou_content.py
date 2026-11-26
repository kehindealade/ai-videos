VOICE = "bm_lewis"
SPEED = 0.92

CH = {
    0: "WHO DOES AMERICA OWE?",
    1: "THE BIGGEST LENDER IS AMERICA ITSELF",
    2: "THE FEDERAL RESERVE",
    3: "FOREIGN COUNTRIES",
    4: "EVERYONE ELSE",
    5: "HOW THE MONEY GETS PAID BACK",
    6: "SO WHO DOES AMERICA OWE?",
}


def ln(scene, step, text, cap=None, **kw):
    d = dict(scene=scene, p=dict(step=step, **kw), text=text, cap=cap or text)
    return d


L = [
    # ---------- chapter 0
    ln("hook", 0, "America owes more than forty trillion dollars. Most people think China holds most of it. China holds about one point four percent. Most of this debt is owed right here at home.", ch=0),
    ln("wall", 0, "Treasury data shows the total crossed forty trillion dollars in August 2026. Every dollar of it is an I O U. A promise to pay money back. Somebody holds every one of those promises. So who?",
       cap="Treasury data shows the total crossed forty trillion dollars in August 2026. Every dollar of it is an IOU. A promise to pay money back. Somebody holds every one of those promises. So who?"),
    ln("tsy", 0, "A Treasury security is just a loan to the government. You hand over money today. The government promises to pay it back on a set date, plus interest."),
    ln("deficit", 0, "First, one distinction. The deficit is what the government borrows in a single year. The debt is every year of borrowing added together, minus any surpluses."),
    ln("deficit", 1, "Spread across every person living in the United States, forty trillion dollars works out to roughly one hundred and nineteen thousand dollars each."),
    ln("frames", 0, "Treasury and Federal Reserve data sort the holders of that debt into four groups. Government trust funds. The Federal Reserve. Foreign governments and investors. And everyone else."),
    ln("frames", 1, "Let's open the vault. The first group surprises most people, because it's the government itself."),
    # ---------- chapter 1
    ln("trust", 0, "About a fifth of the debt, roughly seven point eight trillion dollars, is owed by one part of the government to another. It sits in trust funds.", ch=1, reveal=0),
    ln("trust", 1, "Social Security is the biggest. Its main retirement fund holds about two point three trillion dollars of that."),
    ln("trust", 2, "Here's how it works. Payroll taxes come in, and benefits go out. If more comes in than goes out, the law says the extra must be lent to the Treasury, in exchange for a special government security."),
    ln("trust", 3, "So the trust fund isn't a vault of cash. It holds I O Us from the Treasury, and those I O Us earn interest, paid in more I O Us.",
       cap="So the trust fund isn't a vault of cash. It holds IOUs from the Treasury, and those IOUs earn interest, paid in more IOUs."),
    ln("trust", 4, "When benefits are paid from a trust fund, it cashes in some of those I O Us, and the Treasury has to find the money. Usually, that means borrowing it from the public.",
       cap="When benefits are paid from a trust fund, it cashes in some of those IOUs, and the Treasury has to find the money. Usually, that means borrowing it from the public."),
    ln("trust", 5, "Other government accounts hold the rest, including federal and military retirement funds. Economists call all of this intragovernmental debt: one part of the government owing another."),
    ln("twobars", 0, "That's why you'll hear two different numbers. Gross debt, about forty point seven trillion dollars, includes it. Debt held by the public, about thirty-two point nine trillion, leaves it out."),
    ln("twobars", 1, "To size it up: debt held by the public is roughly equal to the whole country's economic output for one year."),
    # ---------- chapter 2
    ln("fed", 0, "Next, the Federal Reserve, America's central bank. It holds about four point six trillion dollars of Treasury debt, around eleven percent of the total.", ch=2, reveal=1),
    ln("fed", 1, "Why would a central bank own government debt? Because buying and selling Treasuries is one of the main ways it influences interest rates and the supply of money."),
    ln("fed", 2, "Its holdings grew after the 2008 financial crisis, and again in 2020, when it bought Treasuries in large amounts to support the economy. They peaked in 2022."),
    ln("fed", 3, "When the Fed earns interest on those bonds and pays its own costs, any profit left over is sent back to the Treasury."),
    # ---------- chapter 3
    ln("foreign", 0, "Now the part everyone asks about: foreign countries. Foreign governments and investors hold about nine point two trillion dollars of Treasury debt. That's roughly twenty-three percent.", ch=3, reveal=2),
    ln("foreign", 1, "The biggest foreign holder is Japan, with about one point oh six trillion dollars. The United Kingdom is second, just under one trillion. China is third, with about five hundred and sixty-four billion."),
    ln("foreign", 2, "And China's pile has been shrinking. It peaked at about one point three trillion dollars in 2013, and it's now at its lowest level in more than eighteen years."),
    ln("foreign", 2.5, "Part of why the myth stuck: for much of the 2010s, China really was the largest foreign holder. Today, Japan is first and China is third."),
    ln("foreign", 3, "One caution. These numbers show where the bonds are held, not always who ultimately owns them. Belgium and the Cayman Islands also rank near the top, and they are mostly financial centers. Some economists think China's true holdings are higher than the reported number."),
    ln("foreign", 4, "So why do other countries buy American I O Us? Countries that sell a lot to America earn dollars. They need somewhere safe to keep them, and Treasuries are among the easiest bonds in the world to buy and sell.",
       cap="So why do other countries buy American IOUs? Countries that sell a lot to America earn dollars. They need somewhere safe to keep them, and Treasuries are among the easiest bonds in the world to buy and sell."),
    ln("foreign", 5, "About two fifths of foreign holdings belong to foreign governments and central banks, which keep reserves of foreign currency to steady their own money. The rest belong to private investors: banks, pension funds and companies."),
    ln("foreign", 6, "Total foreign holdings hit a record of about nine point five trillion dollars in February 2026, and have slipped a little since."),
    # ---------- chapter 4
    ln("other", 0, "The biggest group is also the least talked about. Almost half of the debt, about nineteen trillion dollars, is held by everyone else.", ch=4, reveal=3),
    ln("other", 1, "That means American banks, mutual funds, pension funds and insurance companies. It also includes state and local governments, and ordinary people who buy Treasury bonds or savings bonds directly."),
    ln("other", 2, "If you have a retirement account, a money market fund or a bond fund, there's a good chance it owns a slice of this debt, even if you never bought a Treasury yourself."),
    ln("other", 3, "Why do they like Treasuries? They can be sold quickly, and their payments come from the government. To a bank or a fund, that makes them close to cash that earns interest."),
    # ---------- chapter 5
    ln("pay", 0, "So how does the debt get paid back? Mostly, it doesn't get paid off. It gets rolled over.", ch=5),
    ln("pay", 1, "Treasuries come in different lengths. Bills last a year or less. Notes last two to ten years. Bonds last twenty or thirty."),
    ln("pay", 2, "The Treasury sells them at auctions, every week. Big banks bid first, then sell them on to investors around the world."),
    ln("pay", 3, "When a Treasury comes due, the holder gets their money back. To find that money, the Treasury usually sells a new I O U to someone else.",
       cap="When a Treasury comes due, the holder gets their money back. To find that money, the Treasury usually sells a new IOU to someone else."),
    ln("pay", 4, "In between, the government pays interest to every holder. In July 2026, the average interest rate on its marketable debt was about three point four percent. And each time an old I O U is replaced, the new one carries the interest rate of the day.",
       cap="In between, the government pays interest to every holder. In July 2026, the average interest rate on its marketable debt was about three point four percent. And each time an old IOU is replaced, the new one carries the interest rate of the day."),
    ln("pay", 5, "That interest flows to all four groups. To trust funds, which are paid in more I O Us. To the Fed. To foreign holders. And to American savers, banks and funds.",
       cap="That interest flows to all four groups. To trust funds, which are paid in more IOUs. To the Fed. To foreign holders. And to American savers, banks and funds."),
    # ---------- chapter 6
    ln("pie", 0, "So who does America owe forty trillion dollars? Put the four groups together. About a fifth is government trust funds. About eleven percent is the Federal Reserve. About twenty-three percent is foreign. And nearly half is everyone else.", ch=6),
    ln("pie", 1, "That means more than three quarters of the debt sits inside the United States: in government accounts, at the central bank, and with American banks, funds and savers. About a quarter is held abroad, and the biggest foreign holder is Japan, not China."),
    ln("pie", 2, "The certificate from the start of this video, the one with China's name on it, is the small one in the corner."),
    ln("data", 0, "You can check all of this yourself. Treasury publishes the total every business day, in a dataset called Debt to the Penny, and the foreign holdings every month, in its T I C reports.",
       cap="You can check all of this yourself. Treasury publishes the total every business day, in a dataset called Debt to the Penny, and the foreign holdings every month, in its TIC reports."),
    ln("plain", 0, "This video isn't saying the debt is good or bad. It only answers one question: who is owed."),
    ln("end", 0, "Next on Money Map: where the interest on this debt actually goes. If you want that one, follow. Follow the money."),
]
