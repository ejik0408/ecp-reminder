# Этап 1: Telegram бот для напоминаний об ЭЦП

## Структура папки
```
telegram-bot/
├── bot.py           # Основной код бота
├── config.py        # Токены и настройки
├── spreadsheet.py   # Работа с Google Sheets
├── scheduler.py     # Проверка сроков
└── requirements.txt # Зависимости
```

## Что делает бот
1. Читает данные из Google Sheets
2. Проверяет у кого ЭЦП истекает через 30, 14, 7, 3, 1 день
3. Отправляет уведомления в Telegram

## Запуск
```bash
cd telegram-bot
pip install -r requirements.txt
python bot.py
```
