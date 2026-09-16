---
name: excelize-spreadsheets
description: Create, inspect, transform, and validate Excel workbooks with Go and github.com/xuri/excelize/v2. Use for XLSX/XLSM spreadsheet tasks where the implementation should be written in Go; do not use for Google Sheets API automation or non-Go spreadsheet libraries.
---

# Excelize Spreadsheets

Use `github.com/xuri/excelize/v2` and preserve the user's requested file format, layout, and output location.

## Workflow

1. Clarify only choices that materially affect the workbook, such as an ambiguous source file, output path, or whether formulas or values are desired. Otherwise infer sensible defaults from the request.
2. Inspect an existing workbook before changing it. Check sheet names, dimensions, representative values, formulas, merged cells, tables, and styles relevant to the requested edit. Do not rebuild a workbook from scratch when a targeted edit will preserve more of it.
3. Work in the user's existing Go module when present. Otherwise create the smallest temporary or task-local Go module needed and add the dependency with `go get github.com/xuri/excelize/v2`.
4. Implement the transformation with checked errors. Open existing files with `excelize.OpenFile`; create new ones with `excelize.NewFile`; always close the workbook and handle close errors.
5. Save to the requested destination. Do not overwrite the source unless the user requested an in-place edit or the surrounding workflow clearly requires it.
6. Reopen the saved workbook and verify the requested sheets, key cell values, formulas, and structural changes. Run the relevant Go tests or the program that produces the workbook.

## Implementation guidance

- Use typed Go values with `SetCellValue`; apply explicit number formats for dates, currency, percentages, and identifiers whose leading zeros must be preserved.
- Build cell references with `CoordinatesToCellName` instead of hand-rolled column arithmetic.
- Create styles once with `NewStyle` and reuse their IDs across ranges.
- Use formulas without a leading `=` when calling `SetCellFormula`. Preserve existing formulas unless the task asks to replace them.
- Treat `CalcCellValue` as a convenience check, not a complete Excel calculation engine. It does not support every formula feature; when necessary, save formulas and state that Excel or another compatible application will recalculate them.
- Use `GetRows` for ordinary worksheets. For large datasets, prefer row iterators for reading and `NewStreamWriter` for writing. Streaming rows must be written in ascending order; call `Flush`, and do not mix stream and normal writes on the same worksheet.
- Preserve macro-enabled extensions when editing XLSM or XLTM files. Do not silently convert them to XLSX.
- Avoid logging cell contents when the workbook may contain sensitive data. Keep temporary copies scoped to the task and remove them when no longer needed.

## Verification

Verification should exercise the artifact, not merely confirm that the Go code compiled. Reopen the output with excelize, assert the expected sheet names and representative cells, and confirm formulas with `GetCellFormula`. For large or highly formatted workbooks, also report any feature that excelize could not faithfully inspect or calculate.
