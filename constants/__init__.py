"""Константы и сообщения бота."""

from typing import Final

BTN_ADD_EXPENSE: Final[str] = "➕ Добавить расход"
BTN_ADD_INCOME: Final[str] = "💰 Добавить доход"
BTN_STATS: Final[str] = "📊 Статистика"
BTN_HELP: Final[str] = "❓ Помощь"
BTN_MENU: Final[str] = "🏠 Главное меню"

START_MESSAGE: Final[str] = (
    "👋 <b>Добро пожаловать в Finance Bot</b>\n\n"
    "Я помогаю быстро фиксировать расходы и доходы и смотреть статистику.\n\n"
    "<b>Что я умею:</b>\n"
    "• сохранять расходы командой <code>/expense сумма описание</code>;\n"
    "• сохранять доходы командой <code>/income сумма описание</code>;\n"
    "• показывать статистику (расходы/доходы/баланс) за день, неделю, месяц и за всё время;\n"
    "• подсказывать формат ввода и доступные действия.\n\n"
    "<b>Примеры:</b>\n"
    "• <code>/expense 1200 Кофе</code>\n"
    "• <code>/expense 1290 Продукты</code>\n"
    "• <code>/income 50000 Зарплата</code>\n\n"
    "Выберите действие в меню ниже 👇"
)

HELP_MESSAGE: Final[str] = (
    "❓ <b>Как пользоваться ботом</b>\n\n"
    "<b>1. Добавить расход</b>\n"
    f"Нажмите «{BTN_ADD_EXPENSE}» и отправьте в следующем сообщении:\n"
    "<code>сумма описание</code>\n"
    "Пример: <code>350 Обед</code>\n"
    "Также работает команда: <code>/expense 350 Обед</code>\n\n"
    "<b>2. Добавить доход</b>\n"
    f"Нажмите «{BTN_ADD_INCOME}» и отправьте в следующем сообщении:\n"
    "<code>сумма описание</code>\n"
    "Пример: <code>50000 Зарплата</code>\n"
    "Также работает команда: <code>/income 50000 Зарплата</code>\n\n"
    "<b>3. Посмотреть статистику</b>\n"
    f"Нажмите «{BTN_STATS}» и выберите период кнопкой.\n"
    "Также можно командой: <code>/stats day|week|month|all</code>\n\n"
    "<b>Команды:</b>\n"
    "• /start — старт и главное меню\n"
    "• /expense — добавить расход\n"
    "• /income — добавить доход\n"
    "• /help — эта подсказка\n"
    "• /stats — статистика (по умолчанию за всё время)"
)

MSG_ADD_EXPENSE_HINT: Final[str] = (
    "Введите расход в формате <code>сумма описание</code>\n"
    "Например: <code>250 Кофе</code>"
)

MSG_ADD_INCOME_HINT: Final[str] = (
    "Введите доход в формате <code>сумма описание</code>\n"
    "Например: <code>50000 Зарплата</code>"
)

MSG_FLOW_NEXT_ACTIONS: Final[str] = "Можно добавить ещё запись кнопками ниже или посмотреть статистику."

MSG_MENU_HINT: Final[str] = "Вы в главном меню. Выберите действие 👇"

ERR_INVALID_FORMAT_EXPENSE: Final[str] = (
    "Не удалось распознать расход. Введите в формате:\n"
    "<code>сумма описание</code>\n"
    "Пример: <code>1200 Кофе</code>"
)
ERR_INVALID_FORMAT_INCOME: Final[str] = (
    "Не удалось распознать доход. Введите в формате:\n"
    "<code>сумма описание</code>\n"
    "Пример: <code>50000 Зарплата</code>"
)
ERR_INVALID_AMOUNT: Final[str] = "Некорректная сумма. Пожалуйста, введите число."
ERR_AMOUNT_MUST_BE_POSITIVE: Final[str] = "Сумма должна быть больше 0."
ERR_PRODUCT_TOO_LONG: Final[str] = "Название товара слишком длинное. Максимум 100 символов."
ERR_INVALID_STATS_PERIOD: Final[str] = "Некорректный период"
ERR_INTERNAL: Final[str] = "Произошла ошибка при обработке запроса. Попробуйте позже."
ERR_DB_UNAVAILABLE: Final[str] = "Не удалось сохранить данные. Попробуйте повторить позже."
MSG_EXPENSE_SAVED: Final[str] = "✅ Расход записан: {product} — {amount:.2f}"
MSG_INCOME_SAVED: Final[str] = "✅ Доход записан: {product} — {amount:.2f}"
MSG_CHOOSE_PERIOD: Final[str] = "Выберите период для статистики:"
MSG_TEXT_FALLBACK: Final[str] = (
    "Для записи операций используйте команды:\n"
    "• <code>/expense сумма описание</code>\n"
    "• <code>/income сумма описание</code>"
)

MAX_PRODUCT_LENGTH: Final[int] = 100
STATS_PERIOD_LABELS: Final[dict[str, str]] = {
    "day": "за сегодня",
    "week": "за неделю",
    "month": "за месяц",
    "all": "за все время",
}
ALLOWED_STATS_PERIODS: Final[tuple[str, ...]] = tuple(STATS_PERIOD_LABELS.keys())
STATS_USAGE_HINT: Final[str] = "Используйте: /stats [day|week|month|all]"
