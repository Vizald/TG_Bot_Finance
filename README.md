# TG_Bot_Finance

Telegram-бот для учёта личных финансов: расходы, доходы и статистика по периодам.

## Возможности

- Добавление расходов и доходов через команды и кнопки меню.
- Поддержка FSM-сценариев для пошагового ввода.
- Статистика за период: `day`, `week`, `month`, `all`.
- Хранение данных в SQLite (`finance.db`).

## Стек

- Python 3.11+
- [aiogram 3](https://docs.aiogram.dev/)
- SQLite
- python-dotenv

## Установка

1. Клонируйте репозиторий.
2. Создайте и активируйте виртуальное окружение.
3. Установите зависимости:

```bash
pip install -r requirements.txt
```

## Настройка окружения

1. Укажите токен бота в `.env`:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

## Запуск

```bash
python bot_main.py
```

При первом запуске автоматически создаётся база `finance.db` и необходимые индексы.

## Команды бота

- `/start` — старт и показ главного меню
- `/help` — подсказка по использованию
- `/expense <сумма> <описание>` — добавить расход
- `/income <сумма> <описание>` — добавить доход
- `/stats [day|week|month|all]` — статистика

Примеры:

- `/expense 1200 Кофе`
- `/income 50000 Зарплата`
- `/stats month`

## Структура проекта

```text
.
├── bot_main.py
├── database.py
├── requirements.txt
├── .gitignore
├── .env.example
├── config/
│   ├── __init__.py
│   └── settings.py
├── constants/
│   └── __init__.py
└── handlers/
    ├── __init__.py
    └── main_handlers.py
```

## Быстрая проверка

```bash
python -m compileall .
```
