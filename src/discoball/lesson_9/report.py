from datetime import UTC, datetime

import polars as pl
import xlsxwriter

from discoball.const import ROOT_DIR
from discoball.lesson_7.affinity import calculate_affinity, load_basket_categories


def main() -> None:
    baskets = load_basket_categories()
    affinity = calculate_affinity(baskets)
    candidates = affinity.filter(
        (pl.col("pair_baskets") >= 10)
        & (pl.col("a_baskets") >= 50)
        & (pl.col("b_baskets") >= 50)
    )
    categories = (
        baskets.group_by("category_name")
        .agg(pl.len().alias("category_baskets"))
        .sort(["category_baskets", "category_name"], descending=[True, False])
    )
    output = ROOT_DIR / ".data" / "lesson_9" / "affinity_review.xlsx"
    output.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(UTC).isoformat()
    with xlsxwriter.Workbook(
        str(output), {"strings_to_formulas": False, "strings_to_urls": False}
    ) as workbook:
        notes = workbook.add_worksheet("Read me")
        notes.set_column("A:A", 24)
        notes.set_column("B:B", 100)
        wrap = workbook.add_format({"text_wrap": True, "valign": "top"})
        entries = [
            ("Purpose", "Historical category-pair review, not a recommendation model."),
            ("Population", "Delivered orders with at least one usable category."),
            (
                "Period",
                "All available historical source data; not a current sales feed.",
            ),
            (
                "Grain",
                "One row per unordered category pair; categories are original keys.",
            ),
            ("Thresholds", "At least 10 shared baskets and 50 baskets per category."),
            (
                "Missing data",
                "Uncategorized items excluded; partial baskets may remain.",
            ),
            (
                "Limitations",
                "Association is not causation, sequence, or incremental profit.",
            ),
            ("Owner", "Learning exercise; no operational service owner assigned."),
            (
                "Review workflow",
                "Workbook annotations do not update the source or code.",
            ),
        ]
        for row, (label, value) in enumerate(entries):
            notes.write_string(row, 0, label)
            notes.write_string(row, 1, value, wrap)
            notes.set_row(row, 42)
        summary = pl.DataFrame(
            {
                "check": [
                    "Generated UTC",
                    "Eligible baskets",
                    "Observed pairs",
                    "Candidate pairs",
                    "Validation",
                ],
                "value": [
                    generated,
                    str(baskets["order_id"].n_unique()),
                    str(affinity.height),
                    str(candidates.height),
                    "Join cardinalities, basket grain, nulls, and count bounds passed",
                ],
            }
        )
        summary.write_excel(
            workbook=workbook, worksheet="Run summary", autofit=True, freeze_panes="A2"
        )
        if candidates.is_empty():
            sheet = workbook.add_worksheet("Candidate pairs")
            sheet.write_string(0, 0, "No pairs passed the evidence thresholds.")
            sheet.set_column("A:A", 65)
        else:
            candidates.write_excel(
                workbook=workbook,
                worksheet="Candidate pairs",
                autofit=True,
                freeze_panes="C2",
                column_formats={
                    "support": "0.00%",
                    "confidence_a_to_b": "0.00%",
                    "confidence_b_to_a": "0.00%",
                    "lift": "0.00",
                },
            )
        categories.write_excel(
            workbook=workbook,
            worksheet="Category summary",
            autofit=True,
            freeze_panes="A2",
        )
    print(f"Wrote {candidates.height} candidate pairs to {output}")
    print("This replaces the previous workbook at the same path. Review it in Excel.")


if __name__ == "__main__":
    main()
