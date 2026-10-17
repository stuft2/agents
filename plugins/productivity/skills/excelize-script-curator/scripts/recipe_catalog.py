#!/usr/bin/env python3
"""Search, update, and validate the Excelize recipe catalog."""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "references" / "catalog.json"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load():
    with CATALOG.open(encoding="utf-8") as handle:
        return json.load(handle)


def save(catalog):
    temporary = CATALOG.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CATALOG)


def find(catalog, recipe_id):
    for recipe in catalog["recipes"]:
        if recipe["id"] == recipe_id:
            return recipe
    raise ValueError(f"unknown recipe: {recipe_id}")


def search(catalog, terms):
    needles = [term.casefold() for term in terms]
    matches = []
    for recipe in catalog["recipes"]:
        haystack = " ".join([recipe["id"], recipe["title"], recipe["summary"], *recipe["tags"]]).casefold()
        score = sum(needle in haystack for needle in needles)
        if not needles or score:
            matches.append((score, recipe))
    for _, recipe in sorted(matches, key=lambda item: (-item[0], item[1]["id"])):
        print(f"{recipe['id']} [{recipe['status']}] - {recipe['summary']}")
        print(f"  {recipe['file']} | tags: {', '.join(recipe['tags'])}")
    return 0 if matches else 1


def validate(catalog):
    errors = []
    recipes = catalog.get("recipes", [])
    if catalog.get("version") != 1 or not isinstance(recipes, list):
        errors.append("catalog must have version 1 and a recipes list")
    ids = [recipe.get("id") for recipe in recipes]
    if len(ids) != len(set(ids)):
        errors.append("recipe IDs must be unique")
    active = {r.get("id") for r in recipes if r.get("status") == "active"}
    required = {"id", "title", "summary", "file", "tags", "status", "uses", "successes", "failures"}
    for recipe in recipes:
        recipe_id = recipe.get("id", "<missing>")
        if missing := required - recipe.keys():
            errors.append(f"{recipe_id}: missing {', '.join(sorted(missing))}")
            continue
        if not ID_RE.fullmatch(recipe_id):
            errors.append(f"{recipe_id}: invalid ID")
        if recipe["status"] not in {"active", "superseded"}:
            errors.append(f"{recipe_id}: invalid status")
        path = (ROOT / recipe["file"]).resolve()
        if ROOT not in path.parents or not path.is_file():
            errors.append(f"{recipe_id}: recipe file missing or outside skill")
        if not isinstance(recipe["tags"], list) or not all(isinstance(t, str) and t == t.lower() for t in recipe["tags"]):
            errors.append(f"{recipe_id}: tags must be lowercase strings")
        if not isinstance(recipe["uses"], int) or not isinstance(recipe["successes"], int) or not 0 <= recipe["successes"] <= recipe["uses"]:
            errors.append(f"{recipe_id}: invalid counters")
        if recipe["status"] == "superseded" and recipe.get("superseded_by") not in active:
            errors.append(f"{recipe_id}: superseded_by must identify an active recipe")
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Validated {len(recipes)} recipe(s).")
    return 0


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    finder = commands.add_parser("search")
    finder.add_argument("terms", nargs="*")
    recorder = commands.add_parser("record")
    recorder.add_argument("recipe_id")
    outcome = recorder.add_mutually_exclusive_group(required=True)
    outcome.add_argument("--success", action="store_true")
    outcome.add_argument("--failure", action="store_true")
    recorder.add_argument("--note", default="")
    commands.add_parser("validate")
    args = parser.parse_args()
    try:
        catalog = load()
        if args.command == "search":
            return search(catalog, args.terms)
        if args.command == "validate":
            return validate(catalog)
        if args.failure and not args.note.strip():
            raise ValueError("--note is required with --failure")
        recipe = find(catalog, args.recipe_id)
        recipe["uses"] += 1
        if args.success:
            recipe["successes"] += 1
        else:
            recipe["failures"].append({"at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(), "note": args.note.strip()})
        save(catalog)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
