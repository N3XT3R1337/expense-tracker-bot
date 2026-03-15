from aiogram.fsm.state import State, StatesGroup


class ExpenseStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_amount = State()
    waiting_for_description = State()


class BudgetStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_amount = State()


class CategoryStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_emoji = State()
