package recipes

import (
	"errors"
	"fmt"

	"github.com/xuri/excelize/v2"
)

type SheetSummary struct {
	Name, Dimension              string
	MergedRanges                 []string
	FormulaCells, Representative map[string]string
}

// InspectWorkbook reads workbook structure and at most sampleLimit non-empty
// values per sheet. A non-positive limit omits representative values.
func InspectWorkbook(path string, sampleLimit int) (summaries []SheetSummary, err error) {
	book, err := excelize.OpenFile(path)
	if err != nil {
		return nil, fmt.Errorf("open workbook: %w", err)
	}
	defer func() {
		if closeErr := book.Close(); closeErr != nil && err == nil {
			err = fmt.Errorf("close workbook: %w", closeErr)
		}
	}()
	for _, sheet := range book.GetSheetList() {
		dimension, err := book.GetSheetDimension(sheet)
		if err != nil {
			return nil, fmt.Errorf("get dimension for %q: %w", sheet, err)
		}
		merged, err := book.GetMergeCells(sheet)
		if err != nil {
			return nil, fmt.Errorf("get merged cells for %q: %w", sheet, err)
		}
		summary := SheetSummary{Name: sheet, Dimension: dimension, FormulaCells: map[string]string{}, Representative: map[string]string{}}
		for _, merge := range merged {
			summary.MergedRanges = append(summary.MergedRanges, merge.GetStartAxis()+":"+merge.GetEndAxis())
		}
		rows, err := book.Rows(sheet)
		if err != nil {
			return nil, fmt.Errorf("iterate rows for %q: %w", sheet, err)
		}
		rowNumber := 0
		for rows.Next() {
			rowNumber++
			columns, rowErr := rows.Columns()
			if rowErr != nil {
				_ = rows.Close()
				return nil, fmt.Errorf("read row %d in %q: %w", rowNumber, sheet, rowErr)
			}
			for columnIndex, value := range columns {
				cell, cellErr := excelize.CoordinatesToCellName(columnIndex+1, rowNumber)
				if cellErr != nil {
					_ = rows.Close()
					return nil, fmt.Errorf("build cell name: %w", cellErr)
				}
				formula, formulaErr := book.GetCellFormula(sheet, cell)
				if formulaErr != nil {
					_ = rows.Close()
					return nil, fmt.Errorf("get formula for %s!%s: %w", sheet, cell, formulaErr)
				}
				if formula != "" {
					summary.FormulaCells[cell] = formula
				}
				if value != "" && len(summary.Representative) < sampleLimit {
					summary.Representative[cell] = value
				}
			}
		}
		if closeErr := errors.Join(rows.Error(), rows.Close()); closeErr != nil {
			return nil, fmt.Errorf("finish rows for %q: %w", sheet, closeErr)
		}
		summaries = append(summaries, summary)
	}
	return summaries, nil
}
