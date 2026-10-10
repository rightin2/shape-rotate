"""shape-rotate benchmark: Haiku with the skill vs Haiku without it, judged blind by Opus.

Steps (each saves to evals/data/ and skips work already saved):
  uv run --with anthropic python evals/bench.py gen            # 100 test prompts (Opus 5.5)
  uv run --with anthropic python evals/bench.py pilot N        # run + judge the first N cases live
  uv run --with anthropic python evals/bench.py runs           # batch: 200 Haiku answers
  uv run --with anthropic python evals/bench.py judges         # batch: 2 blind judgements per case
  uv run --with anthropic python evals/bench.py report         # results.md + results.json

The API key is read from ~/.config/anthropic/key (never from ANTHROPIC_API_KEY).
"""
import collections
import concurrent.futures as cf
import json
import os
import re
import sys
import time
from pathlib import Path


import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get("DATA_DIR", ROOT / "data"))
# VARIANT names a later skill version tested against the same cases and baseline answers,
# e.g. VARIANT=v1_1 (shown as v1.1; batch IDs allow no dots) reads skills/shape-rotate. Unset means the v1.0 snapshot in evals/skill-v1.0.
VARIANT = os.environ.get("VARIANT", "")
SKILL_DIR = ROOT.parent / "skills" / "shape-rotate" if VARIANT else ROOT / "skill-v1.0"
SKILL_ARM = f"skill_{VARIANT}" if VARIANT else "skill"
JTAG = f"{VARIANT}_" if VARIANT else ""
KEY = Path("~/.config/anthropic/key").expanduser()

# Knowledge work (writing test prompts, judging answers): Opus 5.5 at high effort
OPUS, OPUS_EFFORT = "claude-opus-5-5", "high"
# Simple per-item work (the model under test): Haiku 4.5
HAIKU = "claude-haiku-4-5-20251001"

# Prices per million tokens (input, output); batch is half.
PRICE = {OPUS: (4.0, 20.0), HAIKU: (1.0, 5.0)}

CATEGORIES = {
    "oped": "an op-ed, essay or blog post draft that doesn't land",
    "business-decision": "a business decision the person keeps going round in circles on (hiring, pricing, raising, pivoting, partnerships)",
    "talk": "research findings or data for a talk or presentation that feel like a pile of facts with no through-line",
    "pitch": "a startup pitch, fundraising narrative or sales pitch whose story isn't working",
    "academic": "a thesis chapter, paper introduction, literature review or discussion section whose argument doesn't hang together",
    "strategy": "a product strategy, roadmap or go-to-market plan with too many competing priorities",
    "life-decision": "a personal decision (career change, moving city, going back to study, family trade-offs) with many factors",
    "proposal": "a grant application, policy memo or budget proposal that reviewers or bosses won't buy",
    "positioning": "marketing copy, a landing page or brand positioning that feels generic or muddled",
    "team": "a team or organisational problem (a reorg memo, postmortem, culture issue, conflicting stakeholder needs) that needs a clear narrative",
}

GEN_SCHEMA = {
    "type": "object",
    "properties": {"cases": {"type": "array", "items": {
        "type": "object",
        "properties": {"title": {"type": "string"}, "prompt": {"type": "string"}},
        "required": ["title", "prompt"], "additionalProperties": False}}},
    "required": ["cases"], "additionalProperties": False,
}

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        **{c: {"type": "object", "properties": {"A": {"type": "integer"}, "B": {"type": "integer"}},
               "required": ["A", "B"], "additionalProperties": False}
           for c in ("through_line", "structure", "usefulness", "fidelity", "concision", "overall")},
        "winner": {"type": "string", "enum": ["A", "B", "tie"]},
        "reason": {"type": "string"},
    },
    "required": ["through_line", "structure", "usefulness", "fidelity", "concision", "overall", "winner", "reason"],
    "additionalProperties": False,
}

JUDGE_SYSTEM = """You are a blind judge comparing two assistants' answers to the same request. The person's work (a draft, plan, talk, decision or pitch) feels stuck: the pieces are there but it doesn't come together. Judge which answer better solves their actual problem.

Score each answer 1 to 10 on:
- through_line: does it find a clear central idea or angle that makes the material cohere?
- structure: is the proposed arrangement of the pieces genuinely better, so the work now "clicks"?
- usefulness: is the result concrete and ready to use (a rebuilt draft, outline, decision rule), not just generic advice?
- fidelity: does it keep and use the person's own material and voice, without inventing facts?
- concision: is it as long as it needs to be and no longer? Penalise process clutter and padding.
- overall: your holistic judgement of which answer helps this person more.

Length is not quality. Do not favour an answer because it is longer, has more headings or shows more working. Then pick a winner (A, B, or tie only if truly equal) and give a reason in under 60 words."""


def client():
    return anthropic.Anthropic(api_key=KEY.read_text().strip(), max_retries=4)


def load(name, default=None):
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else default


def save(name, obj):
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False))


def text_of(msg):
    return "".join(b.text for b in msg.content if b.type == "text")


def cost(model, usage, batch):
    pin, pout = PRICE[model]
    tin = usage.input_tokens + (usage.cache_creation_input_tokens or 0) * 1.25 + (usage.cache_read_input_tokens or 0) * 0.1
    c = tin / 1e6 * pin + usage.output_tokens / 1e6 * pout
    return c / 2 if batch else c


def live(c, params, attempts=6):
    """Messages API call with our own retry for overloads that slip past the SDK's retries."""
    for i in range(attempts):
        try:
            with c.messages.stream(**params) as s:
                return s.get_final_message()
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as e:
            if isinstance(e, anthropic.APIStatusError) and e.status_code < 500 and e.status_code != 429:
                raise
            time.sleep(30 * (i + 1))
    raise RuntimeError("gave up after retries")


# ---------- step 1: test prompts ----------

def gen_params(cat, desc):
    return {
        "model": OPUS, "max_tokens": 32000,
        "output_config": {"effort": OPUS_EFFORT, "format": {"type": "json_schema", "schema": GEN_SCHEMA}},
        "messages": [{"role": "user", "content": f"""Write 10 realistic messages that different people might send to an AI assistant about {desc}.

These are test cases for a benchmark of how well assistants help when work is stuck. Requirements:
- Each message contains the person's actual material: a draft (a few paragraphs), notes, bullet points, numbers, findings or options. 150 to 400 words per message, so there is real substance to rearrange.
- The material should have a genuine structural problem (buried lead, no spine, two arguments fighting, a decision framed wrong, strong evidence hiding in the middle, a weak claim doing the heavy lifting), not just bad grammar.
- Vary the people, domains, countries, voices and asks. Some are polished, some casual or rushed with small typos. Some ask for a rewrite, some for help deciding, some just say it feels off.
- Do not use the words "rotate", "rotation" or "shape". Use a phrase like "doesn't land" or "isn't clicking" in at most 3 of the 10; the rest describe the problem in their own words.
- All people, companies and data are fictional. No real private individuals.
- Give each a short title (under 8 words)."""}],
    }


def cmd_gen():
    cases = load("cases.json", [])
    done = {c["category"] for c in cases}
    todo = [(k, v) for k, v in CATEGORIES.items() if k not in done]
    c = client()
    spent = 0.0
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {ex.submit(live, c, gen_params(k, v)): k for k, v in todo}
        for f in cf.as_completed(futs):
            k = futs[f]
            msg = f.result()
            spent += cost(OPUS, msg.usage, False)
            got = json.loads(text_of(msg))["cases"][:10]
            for i, g in enumerate(got):
                cases.append({"id": f"{k}-{i + 1:02d}", "category": k, **g})
            save("cases.json", sorted(cases, key=lambda x: x["id"]))
            print(f"{k}: {len(got)} cases (${spent:.2f} so far)", flush=True)
    print(f"{len(load('cases.json'))} cases total; generation cost ${spent:.2f}")


# ---------- step 2: Haiku answers ----------

def skill_system():
    parts = [(SKILL_DIR / "SKILL.md").read_text()]
    for ref in sorted((SKILL_DIR / "references").glob("*.md")):
        parts.append(f"\n\n--- references/{ref.name} ---\n\n{ref.read_text()}")
    return ("The following skill is loaded. It applies to this request, so follow it. "
            "Subagents are not available here, so do the solo pass.\n\n" + "".join(parts))


def run_params(case, arm):
    p = {"model": HAIKU, "max_tokens": 8000, "messages": [{"role": "user", "content": case["prompt"]}]}
    if arm.startswith("skill"):
        p["system"] = [{"type": "text", "text": skill_system(), "cache_control": {"type": "ephemeral"}}]
    else:
        p["system"] = "You are Claude, a helpful AI assistant."
    return p


# ---------- step 3: blind judges ----------

def judge_params(case, ans_skill, ans_base, order):
    # order 0: A = skill, B = baseline. order 1: swapped.
    a, b = (ans_skill, ans_base) if order == 0 else (ans_base, ans_skill)
    return {
        "model": OPUS, "max_tokens": 16000,
        "output_config": {"effort": OPUS_EFFORT, "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
        "system": [{"type": "text", "text": JUDGE_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content":
                      f"THE REQUEST:\n{case['prompt']}\n\n=== ANSWER A ===\n{a}\n\n=== ANSWER B ===\n{b}"}],
    }


def run_batch(c, requests, label):
    """Submit, wait, return {custom_id: message}. Saves the batch id so a restart can resume."""
    ids = load("batches.json", {})
    if label not in ids:
        b = c.messages.batches.create(requests=[
            Request(custom_id=cid, params=MessageCreateParamsNonStreaming(**p)) for cid, p in requests])
        ids[label] = b.id
        save("batches.json", ids)
        print(f"submitted {label}: {b.id} ({len(requests)} requests)", flush=True)
    bid = ids[label]
    while True:
        b = c.messages.batches.retrieve(bid)
        rc = b.request_counts
        print(f"{label}: {rc.succeeded} ok, {rc.errored} errored, {rc.processing} processing", flush=True)
        if b.processing_status == "ended":
            break
        time.sleep(60)
    out, failed = {}, []
    for r in c.messages.batches.results(bid):
        if r.result.type == "succeeded" and r.result.message.stop_reason in ("end_turn", "max_tokens"):
            out[r.custom_id] = r.result.message
        else:
            failed.append(r.custom_id)
    if failed:
        print(f"{label}: {len(failed)} failed: {failed[:10]}")
    return out


def cmd_runs(cases, batch=True):
    answers = load("answers.json", {})
    c = client()
    arms = (SKILL_ARM,) if VARIANT else ("skill", "base")
    todo = [(f"{cs['id']}__{arm}", run_params(cs, arm)) for cs in cases for arm in arms
            if f"{cs['id']}__{arm}" not in answers]
    if not todo:
        return answers
    spent = 0.0
    if batch:
        msgs = run_batch(c, todo, f"runs{VARIANT}")
    else:
        with cf.ThreadPoolExecutor(6) as ex:
            msgs = dict(zip([t[0] for t in todo], ex.map(lambda t: live(c, t[1]), todo)))
    for cid, m in msgs.items():
        spent += cost(HAIKU, m.usage, batch)
        answers[cid] = {"text": text_of(m), "stop": m.stop_reason,
                        "in": m.usage.input_tokens, "out": m.usage.output_tokens}
    save("answers.json", answers)
    log_cost(f"haiku_runs{VARIANT}", spent)
    print(f"{len(msgs)} answers, cost ${spent:.2f}")
    return answers


def cmd_judges(cases, batch=True):
    answers = load("answers.json", {})
    verdicts = load("verdicts.json", {})
    c = client()
    todo = []
    for cs in cases:
        s, b = answers.get(f"{cs['id']}__{SKILL_ARM}"), answers.get(f"{cs['id']}__base")
        if not s or not b:
            continue
        for order in (0, 1):
            cid = f"{cs['id']}__{JTAG}j{order}"
            if cid not in verdicts:
                todo.append((cid, judge_params(cs, s["text"], b["text"], order)))
    if not todo:
        return verdicts
    spent = 0.0
    if batch:
        msgs = run_batch(c, todo, f"judges{VARIANT}")
    else:
        with cf.ThreadPoolExecutor(6) as ex:
            msgs = dict(zip([t[0] for t in todo], ex.map(lambda t: live(c, t[1]), todo)))
    for cid, m in msgs.items():
        spent += cost(OPUS, m.usage, batch)
        try:
            verdicts[cid] = json.loads(text_of(m))
        except json.JSONDecodeError:
            print("unparseable verdict:", cid)
    save("verdicts.json", verdicts)
    log_cost(f"opus_judges{VARIANT}", spent)
    print(f"{len(msgs)} verdicts, cost ${spent:.2f}")
    return verdicts


def log_cost(step, amount):
    costs = load("costs.json", {})
    costs[step] = round(costs.get(step, 0) + amount, 4)
    save("costs.json", costs)


# ---------- step 4: report ----------

def unblind(v, order):
    """Map a verdict's A/B onto skill/base."""
    sk, bs = ("A", "B") if order == 0 else ("B", "A")
    w = {"tie": "tie", sk: "skill", bs: "base"}[v["winner"]]
    scores = {c: (v[c][sk], v[c][bs]) for c in ("through_line", "structure", "usefulness", "fidelity", "concision", "overall")}
    return w, scores


def words(t):
    return len(re.findall(r"\S+", t))


def cmd_report():
    cases = load("cases.json")
    answers, verdicts = load("answers.json", {}), load("verdicts.json", {})
    per_case, judgements = [], collections.Counter()
    crit = collections.defaultdict(lambda: [0, 0, 0])  # sum skill, sum base, n
    by_cat = collections.defaultdict(collections.Counter)
    consistent = 0
    for cs in cases:
        vs = [(verdicts.get(f"{cs['id']}__{JTAG}j{o}"), o) for o in (0, 1)]
        if not all(v for v, _ in vs):
            continue
        wins = []
        for v, o in vs:
            w, sc = unblind(v, o)
            wins.append(w)
            judgements[w] += 1
            for k, (a, b) in sc.items():
                crit[k][0] += a; crit[k][1] += b; crit[k][2] += 1
        if wins[0] == wins[1]:
            consistent += 1
        if wins.count("skill") > wins.count("base"):
            case_w = "skill"
        elif wins.count("base") > wins.count("skill"):
            case_w = "base"
        else:
            case_w = "tie"
        by_cat[cs["category"]][case_w] += 1
        per_case.append({"id": cs["id"], "category": cs["category"], "title": cs["title"], "winner": case_w,
                         "judges": wins,
                         "words_skill": words(answers[f"{cs['id']}__{SKILL_ARM}"]["text"]),
                         "words_base": words(answers[f"{cs['id']}__base"]["text"]),
                         "reasons": [v["reason"] for v, _ in vs]})
    n = len(per_case)
    cw = collections.Counter(p["winner"] for p in per_case)
    nj = sum(judgements.values())
    avg = {k: (round(s / m, 2), round(b / m, 2)) for k, (s, b, m) in crit.items()}
    med = lambda xs: sorted(xs)[len(xs) // 2]
    ws, wb = med([p["words_skill"] for p in per_case]), med([p["words_base"] for p in per_case])

    # Exact two-sided sign test on decisive cases.
    from math import comb
    k, m = cw["skill"], cw["skill"] + cw["base"]
    tail = sum(comb(m, i) for i in range(max(k, m - k), m + 1)) / 2 ** m
    p_value = min(1.0, 2 * tail)

    costs = load("costs.json", {})
    res = {"cases": n, "case_wins": dict(cw), "judgements": dict(judgements), "judge_agreement": consistent,
           "criteria_avg": avg, "median_words": {"skill": ws, "base": wb}, "sign_test_p": p_value,
           "by_category": {k: dict(v) for k, v in by_cat.items()}, "cost_usd": costs,
           "models": {"tested": HAIKU, "judge": f"{OPUS} (effort {OPUS_EFFORT})"}, "per_case": per_case}
    tag = f"_{VARIANT.replace('_', '.')}" if VARIANT else "_v1.0"
    shown = VARIANT.replace("_", ".") if VARIANT else "v1.0"
    res["skill_version"] = shown
    save(f"results{tag}.json", res)

    lines = [f"# shape-rotate {shown} benchmark results\n",
             f"{n} test cases. Model under test: `{HAIKU}`. Judges: `{OPUS}` at {OPUS_EFFORT} effort, blind, two per case with A/B order swapped.\n",
             "| | Skill wins | Baseline wins | Ties |", "|---|---|---|---|",
             f"| Cases (both judges' votes combined) | **{cw['skill']}** | {cw['base']} | {cw['tie']} |",
             f"| Individual judgements | **{judgements['skill']}** | {judgements['base']} | {judgements['tie']} |\n",
             f"Win rate on decisive cases: **{cw['skill'] / max(1, m):.0%}** (sign test p = {p_value:.2g}). "
             f"Both judges agreed on {consistent} of {n} cases.\n",
             "## Average scores (1 to 10)\n", "| Criterion | With skill | Without |", "|---|---|---|"]
    for k in ("through_line", "structure", "usefulness", "fidelity", "concision", "overall"):
        lines.append(f"| {k.replace('_', ' ')} | {avg[k][0]} | {avg[k][1]} |")
    lines += [f"\nMedian answer length: {ws} words with the skill, {wb} without.\n",
              "## By category\n", "| Category | Skill | Baseline | Tie |", "|---|---|---|---|"]
    for k in CATEGORIES:
        v = by_cat.get(k, {})
        lines.append(f"| {k} | {v.get('skill', 0)} | {v.get('base', 0)} | {v.get('tie', 0)} |")
    lines.append(f"\nAPI cost: " + ", ".join(f"{k} ${v:.2f}" for k, v in costs.items())
                 + f" (total ${sum(costs.values()):.2f}).")
    (ROOT / f"results{tag}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    cmd = sys.argv[1:2]
    if cmd == ["gen"]:
        cmd_gen()
    elif cmd == ["pilot"]:
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        cases = load("cases.json")[:n]
        cmd_runs(cases, batch=False)
        cmd_judges(cases, batch=False)
        print(json.dumps(load("costs.json"), indent=1))
    elif cmd == ["runs"]:
        cmd_runs(load("cases.json"))
    elif cmd == ["judges"]:
        cmd_judges(load("cases.json"))
    elif cmd == ["report"]:
        cmd_report()
    else:
        print(__doc__)
