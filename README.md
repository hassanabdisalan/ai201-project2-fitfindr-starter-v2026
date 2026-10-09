# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

A user types a plain-language request for a secondhand clothing item, such as "vintage graphic tee under $30" or "90s track jacket in size M". FitFindr searches a file of listings from Depop, Poshmark and thredUp, picks the best match, and returns that listing, one or two outfit ideas that use pieces from the user's own wardrobe (or general styling advice if the wardrobe is empty), and a short social-post-style fit card about the find. If nothing in the listings matches, it stops early and tells the user which part of the request to loosen (price, size, or keywords) instead of inventing an outfit.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches `data/listings.json` for secondhand items matching a keyword description, optionally filtered by size and a price ceiling, and ranks them by keyword overlap.
- **Inputs:** `description` (str) — keywords such as "vintage graphic tee"; `size` (str | None) — e.g. "M", None skips size filtering; `max_price` (float | None) — inclusive ceiling, None skips price filtering.
- **Returns:** A `list[dict]` of listing dicts, best match first, at most `config.SEARCH_RESULT_LIMIT` long. Each dict has `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None), `platform`. Listings scoring zero keyword overlap are dropped.
- **Size match rule:** the listing's `size` is split into tokens on spaces, `/`, and parentheses, lowercased; the query size matches only if it equals a whole token. "M" matches "S/M" and "M"; "W30" matches "W30 L30"; "S" does not match "US 9" or "XL (oversized)".
- **When it has nothing:** returns an empty list `[]` — never None, never an exception.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfit ideas built around the found item, using pieces from the user's wardrobe when there are any.
- **Inputs:** `new_item` (dict) — one listing dict from `search_listings`; `wardrobe` (dict) — has an `items` key holding a list of wardrobe item dicts (`id`, `name`, `category`, `colors`, `style_tags`, `notes`).
- **Returns:** A non-empty `str` of outfit suggestions. With a non-empty wardrobe it names specific pieces the user owns.
- **When it has nothing:** If `wardrobe["items"]` is empty, it returns general styling advice for the item (still a non-empty string) rather than raising or returning "".

### `create_fit_card`

- **What it does:** Writes a short social-post-style caption about the find.
- **Inputs:** `outfit` (str) — the string from `suggest_outfit`; `new_item` (dict) — the listing dict, used for title, price, and platform.
- **Returns:** A `str` of two to four sentences that mentions the item, its price, and its platform once each, and reads like a post rather than a product description.
- **When it has nothing:** If `outfit` is empty or whitespace, it returns a descriptive message string (e.g. "No outfit to write a caption for.") instead of raising or calling the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` telling the user what to change (loosen the price, drop the size, use fewer keywords) and return the session without calling `suggest_outfit` or `create_fit_card`. Otherwise take the first result as `session["selected_item"]`, call `suggest_outfit`, then `create_fit_card`, and return the session.

**Where it lives:** `agent.py::run_agent` (the `if not session["search_results"]` check in the `search` step)

**How the query is parsed:** regexes in `agent.py::parse_query`, no model call. A price after "under / below / less than / max / up to" or a `$`; a size after "size" or "in" (e.g. "size M", "in M"); the rest is the description.

**What moves through the session:** `query` → `parsed` (description, size, max_price) → `search_results` → `selected_item` (the first result) → `outfit_suggestion` → `fit_card`. `error` is set only when the search is empty, and then the later fields stay `None`. Each tool reads its input back out of the session rather than receiving the previous return value directly.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Casual Y2K Contrast**
Pair the baby tee with your **Baggy straight-leg jeans, dark wash** for classic 2000s proportions. Add the **Brown leather belt**, **Chunky white sneakers**, and throw on the **Vintage black denim jacket** for a cool, effortless finish. 

**Outfit 2: Soft & Structured**
Tuck the tee into your **Wide-leg khaki trousers** to balance the slim fit with relaxed tailoring. Layer the **Black cropped zip hoodie** unzipped over top, and ground the look with your **Black combat boots** for an easy mix of sweet and edgy.

  Fit card: scored this butterfly print Y2K baby tee on depop for eighteen bucks and honestly I'm obsessed. been living for that whole baggy jeans meets tiny top proportion lately. definitely throwing a black zip hoodie over it for that effortless soft-meets-edgy vibe.

0 model calls this session, 2 served from cache
```

**The empty-search path**

```
$ python app.py ask 'designer ballgown size XXS under $5'

  Nothing matched "designer ballgown". Try to raise the price limit above $5; or drop the size (XXS) or try a neighbouring one; or use fewer or more general keywords (e.g. 'jacket' instead of a specific style).

0 model calls this session
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings as s; print([(l['id'],l['title'],l['price']) for l in s('graphic tee', max_price=30)])"
[('lst_002', 'Y2K Baby Tee — Butterfly Print', 18.0), ('lst_006', 'Graphic Tee — 2003 Tour Bootleg Style', 24.0), ('lst_033', 'Vintage Band Tee — Faded Grey', 19.0), ('lst_015', 'Vintage Graphic Hoodie — Faded Black', 26.0), ('lst_017', 'Mesh Long-Sleeve Top — Black', 15.0), ('lst_011', 'Low-Rise Cargo Pants — Khaki', 27.0), ('lst_012', 'Oversized Crewneck Sweatshirt — Vintage Navy', 20.0)]

$ python -c "from tools import search_listings as s; print(s('designer ballgown', size='XXS', max_price=5)); print([l['size'] for l in s('top', size='S')])"
[]
['S/M', 'S/M', 'S/M']
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe())); print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
**Outfit 1: Casual Streetwear**
Pair the vintage Levi's with the **white ribbed tank top** tucked in, layered under the **black cropped zip hoodie**. Add the **chunky white sneakers** and accessorize with the **black crossbody bag**.

**Outfit 2: Relaxed Layers**
Wear the jeans with the **white ribbed tank top**, thrown over with the **oversized grey crewneck sweatshirt**. Cinch the waist using the **brown leather belt** and ground the look with the **black combat boots**.
--- empty wardrobe (general advice, not an error) ---
Vintage 501s are a goldmine—they instantly ground an outfit with classic texture.

**Look 1: Effortless Casual**
Pair the jeans with a tucked-in white ribbed tank or a vintage band tee. Layer with an oversized black leather biker jacket and retro canvas sneakers (like Converse or Vans) for a timeless, streetwear-leaning vibe.
...
```

```
$ AI201_CACHE=0 python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"   # run 3 times
Finally tracked down the holy grail vintage Levi's 501 jeans on depop for $38 and they fit like an absolute dream. The wash has that perfectly broken-in, 90s off-duty model vibe without trying too hard. ...
Scored these vintage Levi's 501 jeans on Depop for $38 and I am never taking them off. They’ve got that perfectly broken-in, effortless 90s slouch that’s impossible to fake. ...
scored these vintage Levi's 501 jeans on depop for $38 and my effortless-cool era is officially locked in. obsessed with the medium wash and how they look just a little beat up in the best way possible. ...

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(repr(create_fit_card('   ', load_listings()[0])))"
'No outfit to write a caption for — suggest_outfit returned nothing.'
```

With the cache on, the same three runs printed one word-for-word identical caption; `TEMPERATURE` was already 0.9, so the cache was the cause.

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* `create_fit_card`, then I ran it three times on the same item as the brief suggested.
- *What came back:* Three word-for-word identical captions. `TEMPERATURE` in `config.py` was already 0.9, so it wasn't that; each run was a separate process with the response cache on and an identical prompt. Running again with `AI201_CACHE=0` gave three different captions. Those captions also said "posting them on depop later today", treating the platform as where the user would sell the item.
- *What I changed:* Nothing in the code for the cache, since it is a build-time feature that the evaluation runs switch off; I recorded the finding under Sample Run. I changed the prompt label from "Platform:" to "Found on:" and asked for "the platform it was found on", and the captions then said "found ... on Depop".

**Moment 2**

- *What I asked for:* The query parser in `agent.py` (`parse_query`) to pull a size, a price ceiling and a description out of a sentence.
- *What came back:* The price worked but the size was `None` for "90s track jacket in size M" and "platform sneakers size 8". The size regex used `\b` inside a normal (non-raw) string, so Python turned it into a backspace character and the pattern could never match. Without a size, `search_listings` skips size filtering, so the agent would have shown wrong-size items with no error.
- *What I changed:* I printed `parse_query` for six example queries, saw the `None` sizes, and replaced the backspace characters with a real `\b`. All six then parsed correctly, for example `{'description': 'platform sneakers', 'size': '8', 'max_price': None}`.


**Moment 3 (unit 4)**

- *What I asked for:* the MCP move, the trace calls and the model-unavailable handler, then a before/after test of one fix.
- *What came back:* it worked, but the first bad-key test used a query that matched nothing, so it hit the empty-search branch and never reached the model; I had to rerun with a query that has results. Later, the tokenizer fix came back with a backspace character in the regex again (the same bug as Moment 2), so my first "after" run was a no-op that still scored 2/5.
- *What I changed:* I checked the file for the 0x08 character, replaced it with a real `\b`, and only then ran the after log, which scored 5/5.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. search_results[0] id = selected_item id = id passed to suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card: 2-4 sentences, price + platform (4 of 5), distinct openings | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5, openings distinct) |
| 5. No result over the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Produced by `score_criteria.py` (one check per criterion, written from the wording in criteria.md, cache off, five tries each; criteria 3 and 5 use five different queries, criterion 4 five different listings). Full output is in `results/criteria_before.md`.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

**Criterion 1** — produced by `agent.py::run_agent`, scored in `score_criteria.py::c1`:
```
- try 1: PASS — error=None fit_card='Scored this butterfly print Y2K baby tee on Depop for $18 and I am fully locked into my 20'
```
**Criterion 2** — `agent.py::run_agent` (the `if not session["search_results"]` branch), scored in `score_criteria.py::c2`:
```
- try 1: PASS — suggest_outfit calls=0 message='Nothing matched "designer ballgown". Try to raise the price limit above $5; or drop the size (XXS) o'
```
**Criterion 3** — `agent.py::run_agent`, scored in `score_criteria.py::c3`:
```
- try 1: PASS — q='vintage graphic tee under $30' first=lst_002 selected=lst_002 suggest_outfit got=['lst_002']
```
**Criterion 4** — `tools.py::create_fit_card`, scored in `score_criteria.py::c4`:
```
- try 4: PASS — lst_005 brand=None sentences=3 price $32:True platform depop:True card='Copped these rust corduroy wide-leg pants on Depop for $32 and they are giving major off-duty skater energy. Honestly obsessed with how they hang. Just gonna throw them on with a beat-up black zip hoodie, some chunky white sneakers, and call it a day.'
```
**Criterion 5** — `tools.py::search_listings` called over MCP, scored in `score_criteria.py::c5`:
```
- try 1: PASS — q='vintage graphic tee under $30' ceiling=30.0 results=10 over=[]
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | MET | 5 passes in 5 tries: no early stop, an outfit and a fit card every time. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET | 5 of 5: `suggest_outfit` was called 0 times and `fit_card` stayed None, with the "Try to raise the price limit…" message each time. |
| 3 | `search_results[0]` id = `selected_item` id = id passed to `suggest_outfit` | 5 of 5 | MET | 5 queries, and the three ids matched on every one (e.g. lst_002 / lst_002 / [lst_002]). |
| 4 | Fit card: 2-4 sentences, price + platform, distinct openings | 4 of 5 | MET | All 5 cards had 3 sentences, the price and the platform, and 5 different first sentences. That includes the two `brand=None` listings. |
| 5 | No result over the price ceiling | 5 of 5 | MET | 5 queries with a parsed ceiling, 0 over-ceiling listings in any result list. |

No criterion was revised.

**Diagnoses**

The original run missed nothing, so I looked at which targets were too easy and tightened one. That tighter check did produce a miss, diagnosed below.

- **Criterion 1 is set too low.** The target was 4 of 5, but the five tries all ran the same query, `vintage graphic tee under $30`, whose words appear in the listing titles and tags. That can't show the phrasing weakness the criterion's own "why" names. A quick check on `search_listings` with other phrasings found one: `graphic t-shirt` ranks "Y2K Baby Tee" and "Oversized Flannel Shirt" first, because the tokenizer in `tools.py::_tokens` splits "t-shirt" into `t` and `shirt`, so it matches any "shirt". The tighter target is **5 of 5 across 5 different phrasings of the same item** ("graphic tee", "band tee", "graphic t-shirt", "vintage tour shirt", "90s tee"), where the top result must be a tee. I ran this tighter check before making any fix and it **MISSED (2/5)** (`results/criteria_before_phrasings.md`). Place: the tool, `tools.py::_tokens` inside `search_listings`. Mechanism: it split "t-shirt" into the letter `t` plus `shirt`, so `t-shirt` and `vintage t-shirt` ranked "Oversized Flannel Shirt" first (a keyword hit on "shirt" only), and `tshirt` became one unknown word that matched no listing, so the loop stopped at the empty-search branch. The model was not involved. The fix and its measurement are under The Improvement.
- **Criterion 4 is too easy to meet with 4 of 5.** All 5 cards passed, including the two with `brand=None`, so the allowance for one miss wasn't needed. The tighter target is 5 of 5 cards over 10 listings, with no two sharing an opening.
- **Criteria 2, 3 and 5 are fine at 5 of 5.** They are deterministic code paths with no model involved, so no tighter number exists.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] branch
      →    results found -> selected the top one
[4] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: **Outfit 1: Casual Y2K Contrast** Pair the baby tee with your **Baggy straight-leg jeans, dark wash** for clas…
[5] create_fit_card
      in:  dict with keys: item
      out: scored this butterfly print Y2K baby tee on depop for eighteen bucks and honestly I'm obsessed. been living fo…
```

**Empty search**

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch
      →    search empty -> stopping, no outfit or card
```

**Failure modes triggered on purpose**

- **Empty search** (`ballgown size XXS under $5`): stops at the branch with "Nothing matched "designer ballgown". Try to raise the price limit above $5; or drop the size (XXS) or try a neighbouring one; or use fewer or more general keywords…". No model call.
- **Empty wardrobe** (`denim jacket under $50 --empty-wardrobe`): no crash, no empty string. suggest_outfit returned general styling ideas (cargo pants, slip dress, sneakers) instead of wardrobe items.
- **Model unavailable** (bad key set via the environment, `denim jacket under $50`): the loop catches ModelUnavailable in agent.py and the user sees: "The model couldn't be reached, so I couldn't write the outfit or fit card. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Then run the same query again." Before this handler the exception was uncaught in run_agent().


**On the MCP move:** search_listings is registered in mcp_server.py and agent.py's run_agent() calls it through mcp_client.call_tool; the other two tools are still direct calls. The return value was the same list of dicts, including `[]` for the empty case, so the branch still works. Nothing broke.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** one line in `tools.py::_tokens`: before splitting a query or a listing into words, `re.sub(r"\bt[\s-]?shirts?\b", "tee", ...)` turns "t-shirt", "t shirt" and "tshirt" into "tee". Nothing else in the agent changed.

**Which failure it was meant to fix:** the weakness named under Diagnoses for criterion 1. My original criterion-1 runs all used one query (`vintage graphic tee under $30`), so I added a tighter measurement: five phrasings of the same item, each of which must complete all three tools and select a tee. Run before the fix, that measurement was MISSED (2/5): `t-shirt` and `vintage t-shirt` selected "Oversized Flannel Shirt" because the tokenizer read "t-shirt" as the letter `t` plus `shirt`, and `tshirt` matched nothing, so the agent stopped at the empty-search branch. The place was the tool (`search_listings`, in its tokenizer); the model was not involved.

This tighter criterion-1 measurement is an addition, not a lowered target: the original line in criteria.md is untouched and the target is still 4 of 5.

### Run Log — Before (criterion 1 measured with five phrasings)

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools, top result is a tee (5 phrasings) | 4 of 5 | PASS | PASS | FAIL | FAIL | FAIL | MISSED (2/5) |
| 2. Impossible query stops before suggest_outfit | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. search_results[0] = selected_item = id passed to suggest_outfit | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card: 2-4 sentences, price + platform, distinct openings | ≥4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5 openings distinct=True) |
| 5. No result over the price ceiling | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Source: `results/criteria_before_phrasings.md`. Criteria 2-5 are the same checks as the first Before log, so they came out the same (5/5 each).

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools, top result is a tee (5 phrasings) | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. search_results[0] = selected_item = id passed to suggest_outfit | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card: 2-4 sentences, price + platform, distinct openings | ≥4/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5 openings distinct=True) |
| 5. No result over the price ceiling | 5/5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Source: `results/criteria_after.md`.

**Did it help, and how do I know:** Yes, for criterion 1: 2/5 before, 5/5 after, with the same five queries, same agent, cache off. In the after log `t-shirt`, `vintage t-shirt` and `tshirt` all selected "Y2K Baby Tee — Butterfly Print", and `tshirt` no longer hit the empty-search branch. Criteria 2-5 stayed 5/5, so nothing else regressed.

Two caveats. My first "after" run was invalid: the regex I had written contained a stray backspace character instead of `\b` (the same bug as How I Used AI, Moment 2, and I had made it again by writing the file from a script), so the pattern never matched and criterion 1 stayed 2/5. I only trusted the second run, after checking the pattern in the file. And the improved "tee" top result for "t-shirt" is a baby tee, not necessarily the best match, since scoring is still plain keyword overlap.

---

## What's Still Broken

Nothing is currently missed against my criteria, but that is partly because the checks are narrow.

- **Search ranking is plain keyword overlap.** "vintage tour shirt" ranks "Oversized Flannel Shirt" above the tour tee, since "shirt" matches the flannel and "tour" only a description. I'd add synonym handling and weight rarer words, but the data has about 40 listings and I stopped at the one failure my tests actually showed (the t-shirt spelling).
- **Criterion 4 is checked on a fixed outfit string.** `score_criteria.py::c4` passes the same outfit text to `create_fit_card` for all 5 listings, so it never tests card quality against a real `suggest_outfit` output. I ran out of time to chain them.
- **Fit-card price check is a string match.** A card that wrote "twenty-four bucks" would count as a miss, which the criterion allows for with 4 of 5.
- **Only `search_listings` is on MCP.** The other two tools are still direct calls, and each MCP call starts a new server process, so it is slower than a held connection.
- **Retry without the size filter was not built**, so an empty search with a size set still just stops and tells the user to loosen it.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
