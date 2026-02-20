import logging
import sqlite3
from math import isfinite

from aiogram import Router, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types.error_event import ErrorEvent
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from constants import (
    ALLOWED_STATS_PERIODS,
    BTN_ADD_INCOME,
    BTN_ADD_EXPENSE,
    BTN_HELP,
    BTN_MENU,
    BTN_STATS,
    ERR_AMOUNT_MUST_BE_POSITIVE,
    ERR_DB_UNAVAILABLE,
    ERR_INTERNAL,
    ERR_INVALID_AMOUNT,
    ERR_INVALID_FORMAT_EXPENSE,
    ERR_INVALID_FORMAT_INCOME,
    ERR_INVALID_STATS_PERIOD,
    ERR_PRODUCT_TOO_LONG,
    HELP_MESSAGE,
    MAX_PRODUCT_LENGTH,
    MSG_ADD_INCOME_HINT,
    MSG_ADD_EXPENSE_HINT,
    MSG_CHOOSE_PERIOD,
    MSG_FLOW_NEXT_ACTIONS,
    MSG_INCOME_SAVED,
    MSG_EXPENSE_SAVED,
    MSG_MENU_HINT,
    MSG_TEXT_FALLBACK,
    START_MESSAGE,
    STATS_PERIOD_LABELS,
    STATS_USAGE_HINT,
)
from database import add_operation, get_operations_summary

router = Router()
logger = logging.getLogger(__name__)


class AddOperationState(StatesGroup):
    waiting_expense_input = State()
    waiting_income_input = State()


class StatsCallback(CallbackData, prefix="stats"):
    period: str


class MenuCallback(CallbackData, prefix="menu"):
    action: str

kb_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_ADD_EXPENSE), KeyboardButton(text=BTN_ADD_INCOME)],
        [KeyboardButton(text=BTN_STATS)],
        [KeyboardButton(text=BTN_HELP)],
    ],
    resize_keyboard=True,
)

kb_stats_period = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="За день", callback_data=StatsCallback(period="day").pack()),
            InlineKeyboardButton(text="За неделю", callback_data=StatsCallback(period="week").pack()),
        ],
        [
            InlineKeyboardButton(text="За месяц", callback_data=StatsCallback(period="month").pack()),
            InlineKeyboardButton(text="За все время", callback_data=StatsCallback(period="all").pack()),
        ],
        [
            InlineKeyboardButton(text=BTN_MENU, callback_data=MenuCallback(action="main").pack()),
        ],
    ],
)


def _format_stats_message(summary: dict[str, float], period: str) -> str:
    return (
        f"Статистика {STATS_PERIOD_LABELS.get(period)}:\n"
        f"• Расходы: {summary['expense']:.2f}\n"
        f"• Доходы: {summary['income']:.2f}\n"
        f"• Баланс: {summary['balance']:.2f}"
    )

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(START_MESSAGE, reply_markup=kb_menu, parse_mode="HTML")


@router.message(F.text == BTN_ADD_EXPENSE)
async def on_add_expense_btn(message: Message, state: FSMContext) -> None:
    await state.set_state(AddOperationState.waiting_expense_input)
    await message.answer(MSG_ADD_EXPENSE_HINT, parse_mode="HTML")


@router.message(F.text == BTN_ADD_INCOME)
async def on_add_income_btn(message: Message, state: FSMContext) -> None:
    await state.set_state(AddOperationState.waiting_income_input)
    await message.answer(MSG_ADD_INCOME_HINT, parse_mode="HTML")


@router.message(F.text == BTN_STATS)
async def on_stats_btn(message: Message) -> None:
    await message.answer(MSG_CHOOSE_PERIOD, reply_markup=kb_stats_period)


@router.callback_query(MenuCallback.filter(F.action == "main"))
async def on_back_to_menu_click(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer(ERR_INTERNAL, show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(MSG_MENU_HINT, reply_markup=kb_menu)
    await callback.answer()


@router.callback_query(StatsCallback.filter())
async def on_stats_period_click(callback: CallbackQuery, callback_data: StatsCallback) -> None:
    if callback.message is None:
        await callback.answer(ERR_INTERNAL, show_alert=True)
        return

    period = callback_data.period
    if period not in ALLOWED_STATS_PERIODS:
        await callback.answer(ERR_INVALID_STATS_PERIOD, show_alert=True)
        return

    try:
        summary = get_operations_summary(callback.from_user.id, period)
    except sqlite3.Error:
        logger.exception("stats_query_failed user_id=%s period=%s", callback.from_user.id, period)
        await callback.answer(ERR_DB_UNAVAILABLE, show_alert=True)
        return

    text = _format_stats_message(summary, period)

    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BTN_MENU, callback_data=MenuCallback(action="main").pack())]
        ]
    )

    await callback.message.edit_text(text, reply_markup=back_kb)
    await callback.answer()


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def on_help_btn(message: Message) -> None:
    await message.answer(HELP_MESSAGE, parse_mode="HTML")


def _parse_amount_and_product(args: str | None) -> tuple[float | None, str | None]:
    if not args:
        return None, None

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        return None, None

    amount_str, product = parts
    try:
        amount = float(amount_str.replace(",", "."))
    except ValueError:
        return None, None

    return amount, product.strip()


async def _save_operation_from_command(
    message: Message,
    command: CommandObject,
    operation_type: str,
) -> None:
    amount, product = _parse_amount_and_product(command.args)

    await _save_operation_from_parsed_data(
        message=message,
        amount=amount,
        product=product,
        operation_type=operation_type,
    )


async def _save_operation_from_parsed_data(
    message: Message,
    amount: float | None,
    product: str | None,
    operation_type: str,
) -> bool:

    if amount is None or not product:
        await message.answer(
            ERR_INVALID_FORMAT_EXPENSE if operation_type == "expense" else ERR_INVALID_FORMAT_INCOME,
            parse_mode="HTML",
        )
        return False

    if not isfinite(amount):
        await message.answer(ERR_INVALID_AMOUNT)
        return False

    if amount <= 0:
        await message.answer(ERR_AMOUNT_MUST_BE_POSITIVE)
        return False

    if len(product) > MAX_PRODUCT_LENGTH:
        await message.answer(ERR_PRODUCT_TOO_LONG)
        return False

    try:
        add_operation(message.from_user.id, amount, product, operation_type)
    except (sqlite3.Error, ValueError):
        logger.exception("operation_save_failed user_id=%s type=%s", message.from_user.id, operation_type)
        await message.answer(ERR_DB_UNAVAILABLE)
        return False

    result_text = MSG_EXPENSE_SAVED if operation_type == "expense" else MSG_INCOME_SAVED
    await message.answer(result_text.format(product=product, amount=amount))
    return True


@router.message(AddOperationState.waiting_expense_input, F.text, ~F.text.startswith("/"))
async def on_expense_input(message: Message, state: FSMContext) -> None:
    amount, product = _parse_amount_and_product(message.text)
    is_saved = await _save_operation_from_parsed_data(
        message=message,
        amount=amount,
        product=product,
        operation_type="expense",
    )
    if not is_saved:
        return

    await state.clear()
    await message.answer(MSG_FLOW_NEXT_ACTIONS, reply_markup=kb_menu)


@router.message(AddOperationState.waiting_income_input, F.text, ~F.text.startswith("/"))
async def on_income_input(message: Message, state: FSMContext) -> None:
    amount, product = _parse_amount_and_product(message.text)
    is_saved = await _save_operation_from_parsed_data(
        message=message,
        amount=amount,
        product=product,
        operation_type="income",
    )
    if not is_saved:
        return

    await state.clear()
    await message.answer(MSG_FLOW_NEXT_ACTIONS, reply_markup=kb_menu)


@router.message(Command("expense"))
async def cmd_expense(message: Message, command: CommandObject) -> None:
    await _save_operation_from_command(message, command, operation_type="expense")


@router.message(Command("income"))
async def cmd_income(message: Message, command: CommandObject) -> None:
    await _save_operation_from_command(message, command, operation_type="income")


@router.message(Command("stats"))
async def cmd_stats(message: Message, command: CommandObject) -> None:
    period = command.args
    if not period:
        period = "all"

    period = period.lower()
    if period not in ALLOWED_STATS_PERIODS:
        await message.answer(f"{STATS_USAGE_HINT}\nДоступно: {', '.join(ALLOWED_STATS_PERIODS)}")
        return

    try:
        summary = get_operations_summary(message.from_user.id, period)
    except sqlite3.Error:
        logger.exception("stats_query_failed user_id=%s period=%s", message.from_user.id, period)
        await message.answer(ERR_DB_UNAVAILABLE)
        return

    await message.answer(
        _format_stats_message(summary, period)
    )


@router.message(F.text)
async def on_text_message(message: Message) -> None:
    await message.answer(MSG_TEXT_FALLBACK, parse_mode="HTML")


@router.error()
async def on_router_error(event: ErrorEvent) -> None:
    logger.exception("router_unhandled_error", exc_info=event.exception)
    if event.update and event.update.message:
        await event.update.message.answer(ERR_INTERNAL)
