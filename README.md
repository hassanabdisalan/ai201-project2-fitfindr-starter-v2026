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

<!-- Three or four sentences: what a user asks for, and what they get back. -->



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

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



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

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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
