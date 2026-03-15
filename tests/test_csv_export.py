from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from src.expense_tracker.reports.csv_export import generate_csv


def test_generate_csv():
    cat = MagicMock()
    cat.name = "Food"

    exp1 = MagicMock()
    exp1.created_at = datetime(2025, 1, 15, 12, 30)
    exp1.category = cat
    exp1.amount = Decimal("25.50")
    exp1.description = "Lunch at cafe"

    exp2 = MagicMock()
    exp2.created_at = datetime(2025, 1, 16, 9, 0)
    exp2.category = cat
    exp2.amount = Decimal("5.00")
    exp2.description = None

    result = generate_csv([exp1, exp2])

    assert "Date,Category,Amount,Description" in result
    assert "2025-01-15 12:30" in result
    assert "Food" in result
    assert "25.50" in result
    assert "Lunch at cafe" in result
    assert "5.00" in result
