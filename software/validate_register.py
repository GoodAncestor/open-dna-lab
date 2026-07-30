#!/usr/bin/env python3
"""Validate data/items.yaml against the rules in BRIEF.md.

Run: make check
"""
import sys
import pathlib
import yaml

VALID_PRIORITY = {"critical", "high", "medium", "low"}
VALID_CONF = {"verified", "estimated"}

REG = pathlib.Path(__file__).resolve().parents[1] / "data" / "items.yaml"


# Fields a section may declare once and have every item inherit, so a run of
# identical vendor/source/confidence lines does not get repeated per item.
INHERITED = ("vendor", "source", "confidence")


def walk(node, out, inherited=None):
    """Collect every mapping carrying id and name, applying section defaults.

    A section may be a bare list, or a mapping of shared fields plus an `items`
    list. In the second form the shared fields are merged into each item unless
    the item sets its own.
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
            rest = {k: v for k, v in node.items() if k != "items"}
            for v in rest.values():
                walk(v, out, inherited)
            return
        for v in node.values():
            walk(v, out, inherited)
    elif isinstance(node, list):
        for v in node:
            walk(v, out, inherited)


def main():
    data = yaml.safe_load(REG.read_text())
    items = []
    walk(data, items)
    ids = {i["id"] for i in items}

    errors, warnings = [], []
    seen = {}

    for it in items:
        i = it["id"]
        if i in seen:
            errors.append(f"duplicate id: {i}")
        seen[i] = it

        pr = it.get("priority")
        if pr is not None and pr not in VALID_PRIORITY:
            errors.append(f"{i}: bad priority {pr!r}")

        if "price" in it:
            conf = it.get("confidence")
            if conf is None:
                errors.append(f"{i}: price with no confidence")
            elif conf not in VALID_CONF:
                errors.append(f"{i}: bad confidence {conf!r}")
            elif conf == "verified" and not it.get("source"):
                errors.append(f"{i}: verified price with no source")

        # A contingency is a fallback, not a purchase. Carrying a priority too
        # would put it on the buy list and in the total, which is the thing the
        # contingent_on field exists to prevent.
        if it.get("contingent_on") and pr is not None:
            errors.append(f"{i}: contingent item also carries priority {pr!r}")

        if it.get("contingent_on") and it["contingent_on"] not in ids:
            errors.append(f"{i}: contingent_on unknown id {it['contingent_on']!r}")

        if it.get("reusable_with") and it["reusable_with"] not in ids:
            errors.append(f"{i}: reusable_with unknown id {it['reusable_with']!r}")

        if it.get("included_in"):
            if it["included_in"] not in ids:
                errors.append(f"{i}: included_in unknown id {it['included_in']!r}")
            # Its price is already inside the parent's. Giving it a priority as
            # well would put a bundled item on the buy list and double-count it.
            if pr is not None:
                errors.append(f"{i}: included_in set but also carries priority {pr!r}")

    flags = [(i["id"], i["flag"]) for i in items if "flag" in i]
    questions = [i["id"] for i in items if "open_question" in i]
    blockers = [i["id"] for i in items if "blocker" in i]
    buy = [i for i in items if i.get("priority")]
    contingent = [i for i in items if i.get("contingent_on")]

    def line_total(it):
        """Per-unit price times quantity. Must match scripts/gen_pages.py."""
        price = it.get("price", 0)
        if it.get("unit") == "each" and it.get("quantity"):
            price *= it["quantity"]
        return price

    total = sum(line_total(i) for i in buy if not i.get("included_in"))

    print(f"{len(items)} items")
    print(f"{len(buy)} on the buy list, {total:,.0f} USD")
    if contingent:
        print(f"{len(contingent)} contingent (excluded from the total): "
              f"{', '.join(i['id'] for i in contingent)}")
    if flags:
        print(f"\n{len(flags)} flagged:")
        for i, f in flags:
            print(f"  {i:24s} {f}")
    if blockers:
        print(f"\n{len(blockers)} blocked: {', '.join(blockers)}")
    if questions:
        print(f"{len(questions)} open questions: {', '.join(questions)}")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if errors:
        print(f"\nFAILED — {len(errors)} error(s)")
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
