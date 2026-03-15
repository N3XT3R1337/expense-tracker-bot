import csv
import io

from ..models.expense import Expense


def generate_csv(expenses: list[Expense]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Category", "Amount", "Description"])
    for exp in expenses:
        writer.writerow([
            exp.created_at.strftime("%Y-%m-%d %H:%M"),
            exp.category.name if exp.category else "Unknown",
            f"{exp.amount:.2f}",
            exp.description or "",
        ])
    return output.getvalue()
