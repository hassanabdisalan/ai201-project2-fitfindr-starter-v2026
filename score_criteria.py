"""Score the five criteria in criteria.md, five tries each, caching off.

    python score_criteria.py --label before

Each check below is the criterion's own wording turned into code, so PASS/FAIL is
decided the same way every try. Writes results/criteria_<label>.md.
"""
import argparse
import datetime as dt
import re

import config
import agent
from tools import create_fit_card
from utils.data_loader import get_example_wardrobe, load_listings

config.CACHE_ENABLED = False

C1_QUERY = "vintage graphic tee under $30"
C2_QUERY = "designer ballgown size XXS under $5"
C3_QUERIES = ["vintage graphic tee under $30", "90s track jacket in size M",
              "denim jacket under $50", "platform sneakers size 8",
              "silk slip dress under $40"]
C5_QUERIES = ["vintage graphic tee under $30", "denim jacket under $50",
              "silk slip dress under $40", "tee under $20", "jacket under $60"]
OUTFIT = "Pair it with baggy jeans, chunky white sneakers and a black zip hoodie."


def c1(i):
    s = agent.run_agent(C1_QUERY, get_example_wardrobe(), trace_on=False)
    ok = not s["error"] and bool(s["outfit_suggestion"]) and bool(s["fit_card"])
    return ok, f"error={s['error']!r} fit_card={(s['fit_card'] or '')[:90]!r}"


def c2(i):
    calls = []
    real = agent.suggest_outfit
    agent.suggest_outfit = lambda *a, **k: calls.append(a) or real(*a, **k)
    try:
        s = agent.run_agent(C2_QUERY, get_example_wardrobe())
    finally:
        agent.suggest_outfit = real
    msg = s["error"] or ""
    ok = not calls and bool(msg) and "Try" in msg and s["fit_card"] is None
    return ok, f"suggest_outfit calls={len(calls)} message={msg[:100]!r}"


def c3(i):
    seen = []
    real = agent.suggest_outfit
    agent.suggest_outfit = lambda item, w: seen.append(item["id"]) or real(item, w)
    try:
        s = agent.run_agent(C3_QUERIES[i], get_example_wardrobe())
    finally:
        agent.suggest_outfit = real
    first = s["search_results"][0]["id"] if s["search_results"] else None
    sel = (s["selected_item"] or {}).get("id")
    ok = first is not None and first == sel and seen == [first]
    return ok, f"q={C3_QUERIES[i]!r} first={first} selected={sel} suggest_outfit got={seen}"


def _listings():
    out, plats = [], set()
    for l in load_listings():
        if l["platform"] not in plats or len(out) < 5 and len(plats) >= 3:
            out.append(l); plats.add(l["platform"])
        if len(out) == 5:
            break
    return out


CARD_ITEMS = _listings()
CARDS = {}


def c4(i):
    l = CARD_ITEMS[i]
    card = create_fit_card(OUTFIT, l)
    CARDS[i] = card
    sentences = [x for x in re.split(r"(?<=[.!?])\s+", card.strip()) if x]
    price = f"${int(l['price'])}" if float(l["price"]).is_integer() else f"${l['price']}"
    has_price = price in card
    has_plat = l["platform"].lower() in card.lower()
    ok = 2 <= len(sentences) <= 4 and has_price and has_plat
    return ok, (f"{l['id']} brand={l['brand']!r} sentences={len(sentences)} "
                f"price {price}:{has_price} platform {l['platform']}:{has_plat} card={card!r}")


def c5(i):
    q = C5_QUERIES[i]
    parsed = agent.parse_query(q)
    from mcp_client import call_tool
    res = call_tool("search_listings", {"description": parsed["description"],
                                        "size": parsed["size"], "max_price": parsed["max_price"]})
    cap = parsed["max_price"]
    over = [r["id"] for r in res if cap is None or r["price"] > cap]
    ok = cap is not None and bool(res) and not over
    return ok, f"q={q!r} ceiling={cap} results={len(res)} over={over}"


CRITERIA = [
    (1, "Matching query completes all three tools", "≥4/5", 4, c1),
    (2, "Impossible query stops before suggest_outfit", "5/5", 5, c2),
    (3, "search_results[0] = selected_item = id passed to suggest_outfit", "5/5", 5, c3),
    (4, "Fit card: 2-4 sentences, price + platform, distinct openings", "≥4/5", 4, c4),
    (5, "No result over the price ceiling", "5/5", 5, c5),
]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--label", default="run")
    label = ap.parse_args().label
    table = ["| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |",
             "|---|---|---|---|---|---|---|---|"]
    detail = []
    for n, name, target, need, fn in CRITERIA:
        marks = []
        detail.append(f"### Criterion {n}: {name}\n")
        for i in range(5):
            try:
                ok, info = fn(i)
            except Exception as exc:  # noqa: BLE001
                ok, info = False, f"CRASHED {type(exc).__name__}: {exc}"
            marks.append(ok)
            detail.append(f"- try {i+1}: {'PASS' if ok else 'FAIL'} — {info}")
            print(f"c{n} try {i+1}: {'PASS' if ok else 'FAIL'}", flush=True)
        extra = ""
        if n == 4:
            firsts = [re.split(r"(?<=[.!?])\s+", CARDS.get(i, "").strip())[0].lower() for i in range(5)]
            distinct = len(set(firsts)) == 5
            extra = f" openings distinct={distinct}"
            detail.append(f"- first sentences: {firsts}")
            met = sum(marks) >= need and distinct
        else:
            met = sum(marks) >= need
        verdict = f"{'MET' if met else 'MISSED'} ({sum(marks)}/5{extra})"
        table.append(f"| {n}. {name} | {target} | " + " | ".join("PASS" if m else "FAIL" for m in marks) + f" | {verdict} |")
        detail.append("")
    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"criteria_{label}.md"
    path.write_text(f"# Criteria run — {label} ({dt.datetime.now():%Y-%m-%d %H:%M}, cache off)\n\n"
                    + "\n".join(table) + "\n\n## Output\n\n" + "\n".join(detail), encoding="utf-8")
    print("\n".join(table)); print("wrote", path)
