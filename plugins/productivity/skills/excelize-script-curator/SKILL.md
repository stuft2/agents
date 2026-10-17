---
name: excelize-script-curator
description: Track, reuse, and improve common Go scripts built with excelize for Excel workbook tasks. Use alongside excelize-spreadsheets when an operation may match a reusable recipe, or after a verified task reveals a broadly useful improvement; do not collect one-off business logic or unverified code.
---

# Excelize Script Curator

Maintain a small library of proven Excelize recipes. Pair this skill with `$excelize-spreadsheets`; that skill governs workbook correctness, while this one governs reuse and curation.

## Before implementing

1. Run `python3 scripts/recipe_catalog.py search <terms>` from this skill's directory. Search by operation, Excel feature, and constraint.
2. Reuse the closest active recipe when its assumptions match. Copy it into the task workspace and adapt it there; never edit the library copy merely to satisfy one workbook.
3. If no recipe matches, complete the task normally. A missing recipe is not a reason to broaden the user's task.

## After verification

The workbook must first pass the artifact-level checks required by `$excelize-spreadsheets`.

- Record successful reuse with `python3 scripts/recipe_catalog.py record <recipe-id> --success`.
- Record a recipe-related failure with `python3 scripts/recipe_catalog.py record <recipe-id> --failure --note '<concise cause>'`. Exclude unrelated input and environment failures.
- Change the library only when its directory is writable and the operation has appeared at least twice, an active recipe needs a generalizable fix, or the change materially improves safety, preservation, scalability, or verification.

Do not promote workbook paths, customer data, secrets, proprietary formulas, or domain-specific column names. Generalize names and use synthetic inputs.

## Curating a recipe

Read [references/recipe-format.md](references/recipe-format.md), then:

1. Add or update a focused, compilable Go file under `scripts/recipes/`.
2. Add or update its entry in `references/catalog.json`. Prefer improving an existing recipe to creating a near-duplicate.
3. Preserve the recipe ID. For a breaking replacement, add a new recipe and mark the old one `superseded` with `superseded_by`.
4. Test with synthetic data and verify the produced workbook by reopening it.
5. Run `python3 scripts/recipe_catalog.py validate` and `go test ./...` from `scripts/recipes`.
6. Report any durable recipe added, improved, or superseded. If the installed skill is read-only, report the candidate improvement without modifying another location.

Keep recipes narrow enough to copy safely and complete enough to demonstrate error handling, save/close behavior, and output verification.
