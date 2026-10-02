# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** Not 5 of 5, because `search_listings` is a plain keyword
overlap over a small listings file: a phrasing like "band tee" may not share a
word with a listing tagged "graphic tee", and two of the three steps call a
model that can be rate-limited. Not 3 of 5, because for the example queries in
`python app.py examples` the listing titles and tags contain the keywords, so a
miss would mean a real bug.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** This path never calls a model. It is a single
`if not results` check in `agent.py::run_agent` on the empty list that
`search_listings` returns, so nothing random or rate-limited can interfere.
A miss would be a logic bug, not bad luck, which is why 5 of 5 is fair here and
isn't for criterion 1.

---

## 3. Something about state

For 5 queries that each match at least one listing, the `id` of
`session["search_results"][0]` equals the `id` of `session["selected_item"]`,
and also equals the `id` of the `new_item` dict that `suggest_outfit` received
(check by wrapping `suggest_outfit` to record its argument) — 5 of 5 queries.

**Why this target:** State passing is plain dict assignment inside `run_agent`,
with no model involved, so it should be exact. A wrong item here would look like
a bad outfit suggestion, not a state bug, so the check compares ids rather than
reading the output. The loop always picks the first result, which makes the
expected id known in advance.

---

## 4. Something about the fit card

For 5 different listings, each fit card is 2 to 4 sentences long, contains the
listing's price (e.g. "$24") and its platform name (e.g. "depop") — in at least
4 of 5 cards — and no two of the 5 cards start with the same first sentence.

**Why this target:** The words vary by design, so I can't check exact text, only
facts that must appear. Price and platform come straight from the listing dict,
so a card without them ignored its input. 4 of 5 rather than 5 of 5 because the
model sometimes writes "under thirty bucks" instead of "$24", which a string
check would count as a miss. The distinct-opening rule is there because with
`TEMPERATURE` low or `CACHE_ENABLED` on, different items can get near-identical
captions.

---

## 5. Your choice

For 5 queries that include a price ceiling (e.g. "under $30", "under $20"),
every listing `search_listings` returns has `price` less than or equal to that
ceiling — 5 of 5 queries, with zero over-ceiling listings in any result list.

**Why this target:** Price is a float field on every listing, and the filter is
a single numeric comparison with no model involved, so there is no excuse for a
miss. The risk is in parsing: `agent.py` has to pull "$30" out of the query, and
in PowerShell a double-quoted "$30" silently becomes no ceiling at all. An
over-budget item shown to a thrifter is the most visible failure this agent can
have, so I'm not allowing any exceptions.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
