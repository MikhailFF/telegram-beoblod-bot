# Telegram Beoblod Bot

Бот для Telegram-чата в образе дерзкого армейского прапорщика: отвечает одной короткой фразой, если его тегнули или если пользователь ответил на его сообщение.

Фразы написаны оригинально, без дословных цитат из книг и фильмов. Банк реплик держит настроение флотских, армейских, медицинских и авиационных баек, но не хранит чужой текст как источник.

## Что умеет

- Работает только в группах и супергруппах, личку игнорирует.
- Отвечает на упоминание `@BeoblodBot`.
- Отвечает, когда в чате делают reply на сообщение бота.
- Приветствует каждого пользователя только один раз в день.
- По умолчанию выбирает фразу из локального банка по словам сообщения.
- При включенном LLM докручивает локальный черновик финальным ответом под контекст вопроса.
- Если LLM недоступна, бот не падает и отвечает локальной фразой.

## Установка

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Скопируйте `.env.example` в `.env` и вставьте токен Telegram:

```powershell
Copy-Item .env.example .env
```

Минимальная настройка:

```dotenv
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
LLM_ENABLED=auto
```

Запуск:

```powershell
python -m morale_bot.bot
```

## LLM

LLM-слой опциональный. Бот закреплен на бесплатной Qwen-модели OpenRouter, но API-ключ все равно нужен.

```dotenv
LLM_ENABLED=auto
LLM_API_BASE=https://openrouter.ai/api/v1
LLM_MODEL=qwen/qwen3-next-80b-a3b-instruct:free
LLM_API_KEY=your_openrouter_key
LLM_TIMEOUT_SECONDS=12
GREETING_STATE_PATH=.state/daily_greetings.json
```

Можно также использовать переменную `OPENROUTER_API_KEY` вместо `LLM_API_KEY`.

## Проверка

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Использование

Добавьте бота в групповой чат и напишите:

```text
@BeoblodBot я устал
```

Или ответьте обычным reply на любое сообщение бота. Для групп можно оставить BotFather privacy mode включенным: Telegram доставляет боту команды, упоминания и ответы на его сообщения.
