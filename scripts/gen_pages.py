#!/usr/bin/env python3
"""Generate the register site pages from data/items.yaml.

data/items.yaml is the single source of truth. These pages are build products:
they are written to site/_generated/ and are gitignored. Editing them by hand
has no effect, because the next build overwrites them. Change the register.

    python3 scripts/gen_pages.py

Emits, in build_site.py's markdown dialect:

    inventory.md       owned items, grouped by bench function
    buy-list.md        priority order, running total, confidence, contingencies
    open-questions.md  every open_question and blocker field, collected

There is no status field in the register. An item carrying a `priority` is on
the buy list; anything else is owned. `contingent_on` marks a fallback that is
neither, and `included_in` marks a price already counted inside its parent's.
"""
import pathlib
import re
import sys
from urllib.parse import urlparse

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "items.yaml"
SOFT = ROOT / "data" / "software.yaml"
OUT = ROOT / "site" / "_generated"

# Register sections, in bench order, with the labels the site uses.
# (register key, page heading, optional lead paragraph)
SECTIONS = [
    ("instruments", "Instruments", ""),
    ("emitters", "Emitters", ""),
    ("sequencing", "Sequencing", ""),
    ("library_prep", "Library prep", ""),
    ("extraction", "Extraction", ""),
    ("qc", "Quality control", ""),
    ("bench_equipment", "Bench equipment", ""),
    ("bench", "Bench", ""),
    ("consumables", "Consumables", ""),
    ("colorimetry", "Colorimetry reagents",
     "Standards and reagents for the caffeine and vitamin C assays on the "
     "[colorimetry page](/colorimetry). These sit outside the sequencing path. "
     "They check the instruments against a known answer first."),
    ("compute", "Compute and storage",
     "Live host state, capacity, and uptime are on the "
     "[fleet dashboard](https://status.goodancestor.com/). Listed here is only "
     "what the sequencing path depends on."),
    ("gaps", "Gaps", ""),
]

# Nested item lists, rendered as a sub-group under their parent rather than as
# a section of their own: optics belong to the microscope, consumables to the
# sequencer.
CHILD_KEYS = (("optics", "optics"), ("consumables", "consumables and kits"))

# Section-level fields every item in that section inherits.
INHERITED = ("vendor", "source", "confidence")

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# id -> display name, populated in main(). Used to render cross-references
# (included_in, contingent_on) as names rather than raw ids.
NAMES = {}

# child id -> parent id, from the nested CHILD_KEYS lists. The buy list is
# ordered by priority, which scatters a kit's parts across it; this is what
# lets each line still say what it belongs to.
PARENTS = {}

# build_site.py's inline() HTML-escapes before it does anything else, so raw
# tags in generated markdown render as visible text. Its explicit line break is
# a literal backslash-n in the source.
BREAK = "\\n"

FOOTER = {
    "org": "Good Ancestor Foundation",
    "line": "Open lab equipment register. Generated from data/items.yaml.",
    "note": "Prices in USD. Estimated figures are marked and have not been "
            "checked against a vendor.",
}


def walk(node, out, inherited=None):
    """Collect every mapping carrying id and name, applying section defaults.

    Mirrors software/validate_register.py. Section defaults are merged into the
    item dicts in place, so callers that iterate the raw tree afterwards see
    resolved vendor/source/confidence too.
    """
    inherited = inherited or {}
    if isinstance(node, dict):
        if "id" in node and "name" in node:
            for k, v in inherited.items():
                node.setdefault(k, v)
            out.append(node)
        if "items" in node and isinstance(node["items"], list):
            defaults = {**inherited,
                        **{k: node[k] for k in INHERITED if k in node}}
            walk(node["items"], out, defaults)
            for k, v in node.items():
                if k != "items":
                    walk(v, out, inherited)
            return
        for v in node.values():
            walk(v, out, inherited)
    elif isinstance(node, list):
        for v in node:
            walk(v, out, inherited)


def index_parents(node, parent_id=None):
    """Record child -> parent for every nested CHILD_KEYS list."""
    if isinstance(node, dict):
        me = node.get("id", parent_id)
        for ckey, _ in CHILD_KEYS:
            for child in node.get(ckey, []) or []:
                if isinstance(child, dict) and "id" in child:
                    PARENTS[child["id"]] = node.get("id")
                    index_parents(child, child["id"])
        for k, v in node.items():
            if k not in dict(CHILD_KEYS):
                index_parents(v, me)
    elif isinstance(node, list):
        for v in node:
            index_parents(v, parent_id)


def section_items(data, key):
    """Top-level items of a section, in either the bare-list or defaults form."""
    node = data.get(key)
    if isinstance(node, dict):
        node = node.get("items", [])
    return [i for i in (node or []) if isinstance(i, dict) and "id" in i]


def is_kit_item(item):
    """Comes with its parent kit, so it never appears as its own buy line."""
    return bool(item.get("kit_item"))


def is_optional(item):
    """Wanted, but not ordered. Kept off the buy list and out of the total."""
    return bool(item.get("optional"))


def is_buy(item):
    """On the buy list. There is no status field: a priority puts it there."""
    return (bool(item.get("priority"))
            and not item.get("contingent_on")
            and not is_optional(item)
            and not is_kit_item(item))


def is_owned(item):
    return (not is_buy(item)
            and not item.get("contingent_on")
            and not is_optional(item)
            and not is_kit_item(item))


def clean(text):
    """Collapse a folded YAML scalar to one line of inline markdown.

    Tildes become subscript spans in the renderer, so approximation is spelled
    out rather than punctuated.
    """
    if text is None:
        return ""
    s = " ".join(str(text).split())
    return s.replace("~", "about ")


def money(n):
    return f"${n:,.0f}" if n == int(n) else f"${n:,.2f}"


def price_cell(item):
    """Price, marked only when the figure is an estimate.

    A verified price is shown bare. Annotating it as verified would put a label
    on the majority of lines to say nothing, and the validator already refuses
    a price that carries no confidence at all, so silence here means checked.
    """
    if "price" not in item:
        return "—"
    qty = item.get("quantity")
    if qty and item.get("unit") == "each":
        p = f"{money(line_total(item))}{BREAK}{money(item['price'])} × {qty}"
    else:
        p = money(item["price"])
    return f"{p} *(est.)*" if item.get("confidence") == "estimated" else p


def name_cell(item):
    name = clean(item.get("name", item["id"]))
    bits = []
    if item.get("variant"):
        bits.append(clean(item["variant"]))
    if item.get("part"):
        bits.append(f"`{clean(item['part'])}`")
    # BREAK, not <br>: inline() escapes angle brackets before anything else, so
    # a literal tag renders as text. Backslash-n is the renderer's own escape.
    return f"**{name}**" + (f"{BREAK}{' · '.join(bits)}" if bits else "")


def is_url(s):
    return str(s).startswith(("http://", "https://"))


def vendor_cell(item):
    """Vendor, linked only when the source is an actual URL.

    Roughly a quarter of source fields are order references rather than links
    ('amazon-order-2026-01-26', 'eBay listing observed 2026-07'). Those are
    provenance for the price and render as text; wrapping them in markdown link
    syntax would produce a dead link.
    """
    v = clean(item.get("vendor", ""))
    src = item.get("source") or item.get("link")
    if item.get("asin") and not src:
        src = f"https://www.amazon.com/dp/{item['asin']}"

    if src and is_url(src):
        # No vendor recorded: label the link with its host rather than "link",
        # which tells the reader nothing about who sells it.
        host = re.sub(r"^www\.", "", urlparse(src).netloc)
        return f"[{v or host}]({src})"
    if src:
        return f"{v + BREAK if v else ''}*{clean(src)}*"
    return v or "—"


def component(ctype, payload):
    """A ::: fenced component block.

    build_site.py parses the payload with a single yaml.safe_load, so it has to
    be dumped as one document — dumping each field separately emits a stream of
    documents and the parser rejects it.
    """
    body = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=10_000).rstrip()
    return f"::: {ctype}\n{body}\n:::"


def frontmatter(title, tagline, badge, stats, status=None, updated=None,
                description=None, toc=False):
    """Front matter. `tagline` is the visible hero line and may be empty;
    `description` is the invisible meta tag and falls back to it."""
    fm = {
        "title": title,
        "description": description or tagline,
        "badge": badge,
        "tagline": tagline,
        "hero_stats": [{"val": v, "lbl": l} for v, l in stats],
        "footer": dict(FOOTER),
    }
    if toc:
        fm["toc"] = True
    if status:
        fm["status"] = status
    if updated:
        fm["updated"] = str(updated)
        fm["footer"]["copyright"] = f"Register updated {updated}."
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n"


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def item_row(r, note_cap=260):
    note = clean(r.get("notes") or r.get("note") or "")
    if r.get("flag"):
        # These are known limitations on kit that has been accepted for use, so
        # the note is a caveat rather than a warning. Rendering it as an alarm
        # overstated it on every line it appeared.
        label = clean(r["flag"]).replace("-", " ")
        prefix = f"*{label}, approved.*" if r.get("approved") else f"*{label}.*"
        note = f"{prefix} {note}".strip()
    if r.get("consumable"):
        tag = "Consumable, reusable." if r.get("reusable_with") else "Consumable."
        note = f"*{tag}* {note}".strip()
    if r.get("included_in"):
        parent = NAMES.get(r["included_in"], r["included_in"])
        note = f"*Included in the {parent} price.* {note}".strip()
    elif is_kit_item(r):
        parent = NAMES.get(PARENTS.get(r["id"], ""), "the kit")
        note = f"*Ordered with {parent}.* {note}".strip()
    elif is_buy(r):
        note = f"**On the buy list — {r['priority']} priority.** {note}".strip()
    if len(note) > note_cap:
        note = note[:note_cap - 3].rstrip() + "…"
    return (f"| {name_cell(r)} | {vendor_cell(r)} | {price_cell(r)} "
            f"| {note or '—'} |")


def line_total(item):
    """What the line actually costs.

    A per-unit price with a quantity has to be multiplied out — six Flongle
    cells at $90 is $540, not $90 — otherwise the displayed price and the
    running total disagree.
    """
    price = item.get("price", 0)
    if item.get("unit") == "each" and item.get("quantity"):
        price *= item["quantity"]
    return price


def countable(items):
    """Prices that add up. A bundled item's price sits inside its parent's."""
    return sum(line_total(i) for i in items if not i.get("included_in"))


def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def item_table(rows):
    out = ["| Item | Vendor | Price | Notes |", "|---|---|---|---|"]
    out += [item_row(r) for r in rows]
    out.append("")
    return out


def emitter_table(rows):
    """Wavelength is the id; what it is for is the reason to read the row."""
    out = ["| Emitter | Format | Goes in | For |", "|---|---|---|---|"]
    for r in rows:
        out.append(f"| **{r.get('wavelength_nm')} nm**{BREAK}{price_cell(r)} "
                   f"| {r.get('format', '—')} | {clean(r.get('goes_in', '—'))} "
                   f"| {clean(r.get('for', '—'))} |")
    out.append("")
    return out


def page_inventory(data, items, updated):
    owned = [i for i in items if is_owned(i)]
    total = countable(owned)

    out = [frontmatter(
        "Inventory",
        "",
        "Equipment register",
        [(str(len(owned)), "items"), (money(total), "total")],
        updated=updated,
        description="Every instrument, consumable, and machine on the Good "
                    "Ancestor open lab bench.",
        toc=True,
    )]

    for key, label, lead in SECTIONS:
        tops = [i for i in section_items(data, key) if is_owned(i)]
        # Child groups render in full, including parts still to buy. Splitting a
        # kit across two pages by ownership hides what the kit actually needs —
        # the point of the group is to show everything that goes with the parent
        # in one place. Each row says which state it is in.
        kids = {}
        for parent in section_items(data, key):
            for ckey, clabel in CHILD_KEYS:
                group = [c for c in parent.get(ckey, []) if not is_optional(c)]
                if group:
                    kids[(parent["id"], clabel)] = (parent, group)
        if not tops and not kids:
            continue

        all_rows = tops + [c for _, ks in kids.values() for c in ks]
        held = [r for r in all_rows if is_owned(r)]
        pending = [r for r in all_rows if is_buy(r)]
        # The total is what is owned. Parts of a group still to buy are shown
        # in the group but counted on the buy list, never in both.
        out.append(f"## {label}\n")
        # A running total is only worth a line when there are prices to total.
        # Sections like compute hold owned kit with no recorded cost, where the
        # subtitle would read "$0" and say nothing.
        if countable(held):
            sub = f"{plural(len(held), 'item')}, {money(countable(held))} total"
            if pending:
                sub += (f". {len(pending)} more on the buy list, "
                        f"{money(countable(pending))}")
            out.append(f"sub: {sub}.\n")
        if lead:
            out.append(lead + "\n")

        if tops:
            out += emitter_table(tops) if key == "emitters" else item_table(tops)

        for (_, clabel), (parent, ks) in kids.items():
            out.append(f"### {clean(parent['name'])} — {clabel}\n")
            out += item_table(ks)
    return "\n".join(out)


def page_buylist(items, updated):
    buy = [i for i in items if is_buy(i)]
    buy.sort(key=lambda i: (PRIORITY_ORDER.get(i.get("priority"), 9),
                            -i.get("price", 0)))
    contingent = [i for i in items if i.get("contingent_on")]
    total = countable(buy)
    est = sum(line_total(i) for i in buy if i.get("confidence") == "estimated")

    out = [frontmatter(
        "Buy list",
        "",
        "Equipment register",
        [(money(total), "outstanding"), (str(len(buy)), "items"),
         (money(est), "estimated")],
        updated=updated,
        description="Outstanding purchases for the Good Ancestor open lab, in "
                    "priority order.",
    )]

    out.append("## Priority order\n")
    out.append("| Priority | Item | Vendor | Price | Confidence | Running total |")
    out.append("|---|---|---|---|---|---|")
    running = 0
    for i in buy:
        running += line_total(i)
        cell = name_cell(i)
        parent = PARENTS.get(i["id"])
        if parent:
            cell += f"{BREAK}*for {NAMES.get(parent, parent)}*"
        out.append(
            f"| {i.get('priority', '—')} | {cell} | {vendor_cell(i)} "
            f"| {price_cell(i)} | {i.get('confidence', '—')} | {money(running)} |")
    out.append("")

    optional = [i for i in items if is_optional(i)]
    if optional:
        out.append("## Optional\n")
        out.append("| Item | Vendor | Price | Why |")
        out.append("|---|---|---|---|")
        for i in optional:
            why = clean(i.get("rationale") or i.get("notes") or i.get("note") or "")
            if len(why) > 240:
                why = why[:237].rstrip() + "…"
            out.append(f"| {name_cell(i)} | {vendor_cell(i)} | {price_cell(i)} "
                       f"| {why or '—'} |")
        out.append("")

    if contingent:
        out.append("## Contingencies\n")
        out.append("| Item | Price | Backs up | Buy it when |")
        out.append("|---|---|---|---|")
        for i in contingent:
            out.append(f"| {name_cell(i)} | {price_cell(i)} "
                       f"| `{i['contingent_on']}` | {clean(i.get('contingency', ''))} |")
        out.append("")

    blocked = [i for i in buy if i.get("blocker")]
    if blocked:
        out.append("## Blocked\n")
        out.append(component("cards", {
            "variant": "why",
            "items": [{"title": clean(i["name"]), "desc": clean(i["blocker"])}
                      for i in blocked],
        }))
        out.append("")

    rationale = [i for i in buy if i.get("rationale") or i.get("source_advice")]
    if rationale:
        out.append("## Reasoning\n")
        for i in rationale:
            out.append(f"### {clean(i['name'])}\n")
            if i.get("spec"):
                out.append(f"Spec: {clean(i['spec'])}\n")
            if i.get("rationale"):
                out.append(clean(i["rationale"]) + "\n")
            if i.get("source_advice"):
                out.append(f"Sourcing: {clean(i['source_advice'])}\n")

    # Flagged kit sits at the end of the buy list rather than with the open
    # questions: each limitation is a known, accepted one, and the only decision
    # left on it is whether to spend money replacing it.
    flags = [i for i in items if i.get("flag")]
    if flags:
        out.append("## Flagged equipment\n")
        out.append("Owned and in use, with a known limitation. All accepted; "
                   "listed here because replacing any of them is a purchase "
                   "decision.\n")
        out.append("| Item | Limitation | Detail |")
        out.append("|---|---|---|")
        for i in flags:
            detail = clean(i.get("notes") or i.get("note") or "")
            if len(detail) > 240:
                detail = detail[:237].rstrip() + "…"
            label = clean(i["flag"]).replace("-", " ")
            out.append(f"| {name_cell(i)} | {label} | {detail or '—'} |")
        out.append("")
    return "\n".join(out)



def page_questions(items, updated):
    questions = [i for i in items if i.get("open_question")]
    blockers = [i for i in items if i.get("blocker")]
    out = [frontmatter(
        "Open questions",
        "Unresolved questions and blockers collected from the register.",
        "Equipment register",
        [(str(len(questions)), "questions"), (str(len(blockers)), "blockers")],
        updated=updated,
    )]

    if blockers:
        out.append("## Blockers\n")
        for i in blockers:
            out.append(f"### {clean(i['name'])}\n")
            out.append(clean(i["blocker"]) + "\n")

    if questions:
        out.append("## Open questions\n")
        for i in questions:
            out.append(f"### {clean(i['name'])}\n")
            out.append(clean(i["open_question"]) + "\n")

    return "\n".join(out)


def page_software():
    """The software stack, from data/software.yaml."""
    data = yaml.safe_load(SOFT.read_text())
    groups = data.get("groups", [])
    n = sum(len(g.get("items", [])) for g in groups)
    ours = next((g for g in groups if g["id"] == "ours"), {"items": []})

    out = [frontmatter(
        "Software",
        "",
        "Open lab",
        [(str(n), "tools"), (str(len(ours["items"])), "ours"), ("Free", "all of it")],
        updated=(data.get("meta") or {}).get("updated", ""),
        description="Every piece of software the Good Ancestor open lab runs, "
                    "from flow cell to report.",
        toc=True,
    )]

    out.append("Everything here is free, and all of it installs while the "
               "hardware is still shipping. One command covers most of it:\n")
    out.append("```")
    out.append("conda env create -f software/environment.yml")
    out.append("```\n")

    for g in groups:
        out.append(f"## {clean(g['name'])}\n")
        if g.get("lead"):
            out.append(clean(g["lead"]) + "\n")
        out.append("| Tool | What it does | Install |")
        out.append("|---|---|---|")
        for i in g.get("items", []):
            name = clean(i["name"])
            cell = f"[**{name}**]({i['link']})" if i.get("link") else f"**{name}**"
            role = clean(i.get("role", ""))
            if i.get("note"):
                role += f" {BREAK}*{clean(i['note'])}*"
            inst = clean(i.get("install", ""))
            if inst == "vendor":
                inst = "*manual download*"
            elif inst in ("on-device", "preinstalled on macOS and Linux"):
                inst = f"*{inst}*"
            else:
                inst = f"`{inst}`"
            out.append(f"| {cell} | {role} | {inst} |")
        out.append("")
    return "\n".join(out)


def main():
    data = yaml.safe_load(REG.read_text())
    items = []
    walk(data, items)
    NAMES.update({i["id"]: clean(i["name"]) for i in items})
    index_parents(data)
    updated = (data.get("meta") or {}).get("updated", "")

    OUT.mkdir(parents=True, exist_ok=True)
    pages = {
        "inventory.md": page_inventory(data, items, updated),
        "buy-list.md": page_buylist(items, updated),
        "open-questions.md": page_questions(items, updated),
        "software.md": page_software(),
    }
    for name, text in pages.items():
        if "~" in text:
            print(f"ERROR {name}: tilde present, renderer would emit a subscript span")
            return 1
        (OUT / name).write_text(text, encoding="utf-8")
        print(f"  wrote site/_generated/{name} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
