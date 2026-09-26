# The workflow

The tools are the easy part. This is the part that decides whether you
improve or just collect software.

## The mistake almost everyone makes

Treating English as a vocabulary problem. Opening Anki, grinding 200
cards a day, feeling productive.

That trains **recognition**. You get better at spotting the right answer
between two options. It does almost nothing for **production**, which is
what speaking and writing require.

Worse: it feels like work, so you stop, and nothing was retained.

The split that actually matters:

| | Skill | Built by |
|---|---|---|
| input | understanding what you read and hear | reading, listening |
| output | producing correct sentences yourself | writing, speaking |

Your deck trains neither well. It is a **reference manual** — use it to
look things up, not as the main event.

---

## The five phases

Order is not arbitrary. Warm up retrieval, then consume, then produce,
then listen, then consolidate.

```
1. anki     5 min      clear what is due, max 20 new
2. read     20-30 min  Lute, one-click dictionary     <- highest ROI
3. write    10-15 min  150-200 words, checked after
4. listen   15-20 min  subtitles delayed 0.4s
5. review   10 min     add only today's real failures
```

### 1. Anki warm-up — 5 min

Only due cards. Do reviews **before** new cards.

Cap new cards at 20. This feels absurdly low and it is the single biggest
retention factor in the whole deck.

**Never** add new cards in this phase. Phase 5 exists for that.

### 2. Reading — 20-30 min

The highest-return phase and the one people skip.

```bash
english-daily read
```

Lute gives you a dictionary one click away inside the text, plus TTS. That
sounds like a small thing. It is the difference between reading 3 pages
and reading 30.

How to read properly:

1. Read 2 minutes **without** looking anything up. Guess from context. This
   is the part that builds skill.
2. Then look words up. Double click, no context switch, keep going.
3. Understand under 90%? The book is too hard. Drop a level. A book you
   finish badly teaches less than one you finish comfortably.
4. Export the words you looked up. Those are your *real* vocabulary, from
   *your* reading, not a generic list.

### 3. Writing — 10-15 min

```bash
english-daily write        # opens today's file in Neovim
encheck ~/English/writing/2026-09-26.md
enlog -f ~/English/writing/2026-09-26.md --rule "describe the rule in your own words"
```

150-200 words. Any topic. The topic does not matter, the output does.

Neovim marks your errors as you type (`<leader>ld`). Then `encheck` gives
you the full list, and `enlog` files them so you can find the pattern.

**The rule that matters:** a correction you only read is a correction you
make again tomorrow. Write it down. Rewrite the sentence.

### 4. Listening — 15-20 min

```bash
enlisten "https://www.youtube.com/watch?v=..."
```

Three passes:

1. No subtitles. Just listen.
2. English subtitles, on time. Confirm what you heard.
3. English subtitles **delayed 0.4s**.

The delay is the entire trick. With subtitles on time you read. With them
late, your brain has to produce the word itself before it appears. That gap
is where listening actually happens.

Stop when the delay stops feeling hard. Then find something harder.

Never use Spanish or auto-translated subtitles. Worse than no subtitles.

### 5. Review — 10 min

Back to Anki. Add cards in this order and no other:

1. Words looked up in Lute today
2. Corrections from your writing you got wrong
3. Stop.

Then check what you keep breaking:

```bash
english-daily errors
```

**The top entry is your next card.** Not the top fifteen. The top one.

---

## The loop

```
Lute (read)      -> you meet real words
encheck/enpractice (write) -> you find your real mistakes
enlog            -> the pattern becomes visible
Anki (review)    -> only those mistakes become permanent
```

Anki is not where you learn. It is where you stop forgetting.

## Weekly rhythm

| Day | Focus |
|---|---|
| Mon | new cards allowed, reading heavy |
| Tue | writing heavy, one short video |
| Wed | reading heavy, review the week's errors |
| Thu | writing heavy, listening |
| Fri | reading + a longer piece of writing |
| Sat | catch-up reviews, or rest |
| Sun | look at `english-daily errors` and fix the top 3 |

## Rules that matter more than any tool

1. **The deck is the floor, not the ceiling.** Most time goes to reading
   and writing.
2. **Produce more than you consume.** If you do not write 150 words a day,
   you are not learning to speak.
3. **One error at a time.** Do not try to fix everything at once. Work the
   single most frequent mistake until it stops happening.
4. **Do not add cards you did not fail.** Most decks die from over-adding.
5. **Measure output, not input.** The test is whether you can produce 150
   correct words on Sunday. Not how many chapters you read.

## Measuring honestly

```bash
english-daily status    # what is done today, what is due
english-daily streak    # consistency
english-daily errors    # what you keep breaking
```

The real number is a sentence you can produce without translating. Test
it weekly, out loud, on a topic you did not prepare.

## If you fall off

The failure mode is not a missed day, it is a missed week. When it
happens, restart at phase 1 only, five minutes, no reading. The streak
rebuilds from a completed day, not a perfect one.
