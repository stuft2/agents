# Recipe format

Each recipe consists of a Go source file in `scripts/recipes/` and one catalog object in `references/catalog.json`.

Required catalog fields are `id`, `title`, `summary`, `file`, `tags`, `status`, `uses`, `successes`, and `failures`. IDs use stable lowercase kebab-case. Status is `active` or `superseded`. Counters are non-negative and successes cannot exceed uses. Failures contain an ISO-8601 UTC `at` timestamp and concise `note`.

Use `superseded_by` only for superseded entries and point it to an active recipe. Let the catalog tool update counters and failure history; use `apply_patch` for source and metadata edits so changes remain reviewable.

Recipes use package `recipes`, expose focused functions, parameterize varying inputs, return useful errors, close workbooks, and include synthetic tests that verify saved artifacts. Document easy-to-violate assumptions such as streaming order, recalculation, macro preservation, and overwrite behavior.

Do not add a recipe solely because it is possible. It should remove repeated effort or encode a subtle correctness constraint.
