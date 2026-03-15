```
 ███████╗██╗  ██╗██████╗ ███████╗███╗   ██╗███████╗███████╗
 ██╔════╝╚██╗██╔╝██╔══██╗██╔════╝████╗  ██║██╔════╝██╔════╝
 █████╗   ╚███╔╝ ██████╔╝█████╗  ██╔██╗ ██║███████╗█████╗
 ██╔══╝   ██╔██╗ ██╔═══╝ ██╔══╝  ██║╚██╗██║╚════██║██╔══╝
 ███████╗██╔╝ ██╗██║     ███████╗██║ ╚████║███████║███████╗
 ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝
 ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗
 ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
    ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
    ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
    ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
    ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                    ____        _
                   | __ )  ___ | |_
                   |  _ \ / _ \| __|
                   | |_) | (_) | |_
                   |____/ \___/ \__|
```

<div align="center">

![Build](https://img.shields.io/github/actions/workflow/status/N3XT3R1337/expense-tracker-bot/ci.yml?style=for-the-badge&logo=github)
![License](https://img.shields.io/github/license/N3XT3R1337/expense-tracker-bot?style=for-the-badge&color=blue)
![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)

**Personal finance Telegram bot with expense categories, monthly PDF reports, CSV export, inline keyboards for quick entry, and budget limits with alerts.**

[Features](#features) · [Tech Stack](#tech-stack) · [Installation](#installation) · [Usage](#usage) · [Project Structure](#project-structure) · [License](#license)

</div>

---

## Features

- **Expense Tracking** — Add, view, and delete expenses with categories via inline keyboards
- **10 Default Categories** — Food, Transport, Housing, Entertainment, Shopping, Health, Education, Utilities, Clothing, Travel
- **Custom Categories** — Create your own categories with custom emoji
- **Budget Limits** — Set monthly spending limits per category with automatic alerts
- **Budget Alerts** — Get notified when spending reaches 80% of your budget
- **Monthly Reports** — Visual text-based reports with category breakdowns and progress bars
- **PDF Reports** — Professional PDF reports with pie charts, tables, and transaction history via ReportLab
- **CSV Export** — Export all expenses as CSV for external analysis
- **Inline Keyboards** — Fast, tap-based navigation without typing commands
- **Paginated History** — Browse through expense history with pagination
- **Statistics** — Quick overview of monthly spending with `/stats`
- **Async Architecture** — Built on aiogram 3.x with SQLAlchemy async for high performance

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Runtime |
| **aiogram 3.x** | Telegram Bot framework (async) |
| **SQLAlchemy 2.0** | ORM & database layer (async) |
| **aiosqlite** | Async SQLite driver |
| **ReportLab** | PDF report generation |
| **matplotlib** | Chart generation (pie & bar charts) |
| **pytest** | Testing framework |
| **pytest-asyncio** | Async test support |

## Installation

### Prerequisites

- Python 3.11 or higher
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Setup

```bash
git clone https://github.com/N3XT3R1337/expense-tracker-bot.git
cd expense-tracker-bot
```

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

```bash
pip install -r requirements.txt
```

```bash
cp .env.example .env
```

Edit `.env` and set your bot token:

```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///expenses.db
DEFAULT_CURRENCY=USD
```

### Run

```bash
python -m expense_tracker
```

Or via the entry point:

```bash
pip install -e .
expense-tracker-bot
```

### Run Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Usage

### Bot Commands

| Command | Description |
|---|---|
| `/start` | Open main menu with inline keyboard |
| `/help` | Show all available commands |
| `/add` | Quick add an expense |
| `/stats` | View monthly spending statistics |
| `/report` | Generate monthly text report |
| `/budget` | Manage budget limits |
| `/export` | Export expenses as CSV |
| `/categories` | View and manage categories |

### Adding an Expense

1. Tap **"Add Expense"** or send `/add`
2. Select a category from the inline keyboard
3. Enter the amount (e.g., `25.50`)
4. Enter a description or send `/skip`
5. Expense is saved and budget alerts are shown if applicable

### Setting a Budget

1. Tap **"Budgets"** from the main menu
2. Select a category
3. Enter the monthly limit (e.g., `500`)
4. You'll receive alerts when spending reaches 80% of the limit

### Generating Reports

**Text Report:**
```
📊 Report for January 2025

💰 Total: $1,234.56

Breakdown:
  🍔 Food: $450.00 (36.4%)
  █████████░░░░░░░░░░░
  🚗 Transport: $200.00 (16.2%)
  ███░░░░░░░░░░░░░░░░░
```

**PDF Report:**
- Tap **"PDF Report"** to receive a professional PDF with charts and tables

**CSV Export:**
- Tap **"Export CSV"** to download all expenses as a spreadsheet-ready file

## Project Structure

```
expense-tracker-bot/
├── src/
│   └── expense_tracker/
│       ├── __init__.py
│       ├── __main__.py
│       ├── bot.py
│       ├── config.py
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── callbacks.py
│       │   ├── commands.py
│       │   ├── keyboards.py
│       │   └── states.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── expense.py
│       ├── reports/
│       │   ├── __init__.py
│       │   ├── charts.py
│       │   ├── csv_export.py
│       │   └── pdf_report.py
│       └── services/
│           ├── __init__.py
│           ├── budget_service.py
│           ├── category_service.py
│           ├── expense_service.py
│           └── user_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_budget_service.py
│   ├── test_category_service.py
│   ├── test_csv_export.py
│   └── test_expense_service.py
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── requirements-dev.txt
└── requirements.txt
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 panaceya (N3XT3R1337)
