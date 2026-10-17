package recipes

import (
	"path/filepath"
	"testing"

	"github.com/xuri/excelize/v2"
)

func TestInspectWorkbook(t *testing.T) {
	path := filepath.Join(t.TempDir(), "sample.xlsx")
	book := excelize.NewFile()
	if err := book.SetCellValue("Sheet1", "A1", "Item"); err != nil {
		t.Fatal(err)
	}
	if err := book.SetCellValue("Sheet1", "A2", 4); err != nil {
		t.Fatal(err)
	}
	if err := book.SetCellFormula("Sheet1", "B2", "A2*2"); err != nil {
		t.Fatal(err)
	}
	if err := book.MergeCell("Sheet1", "C1", "D1"); err != nil {
		t.Fatal(err)
	}
	if err := book.SaveAs(path); err != nil {
		t.Fatal(err)
	}
	if err := book.Close(); err != nil {
		t.Fatal(err)
	}

	summaries, err := InspectWorkbook(path, 2)
	if err != nil {
		t.Fatal(err)
	}
	if len(summaries) != 1 {
		t.Fatalf("got %d sheets", len(summaries))
	}
	got := summaries[0]
	if got.FormulaCells["B2"] != "A2*2" {
		t.Fatalf("formula = %q", got.FormulaCells["B2"])
	}
	if len(got.MergedRanges) != 1 || got.MergedRanges[0] != "C1:D1" {
		t.Fatalf("merged = %#v", got.MergedRanges)
	}
	if got.Representative["A1"] != "Item" {
		t.Fatalf("A1 = %q", got.Representative["A1"])
	}
}
