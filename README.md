# Telegram Beoblod Bot

Бот для Telegram-чата в образе дерзкого армейского прапорщика: отвечает одной короткой фразой, если его тегнули или если пользователь ответил на его сообщение.

Фразы написаны оригинально, без дословных цитат из книг и фильмов. Банк реплик держит настроение флотских, армейских, медицинских и авиационных баек, но не хранит чужой текст как источник.

## Что умеет

- Работает только в группах и супергруппах, личку игнорирует.
- Отвечает на упоминание `@BeoblodBot`.
- Отвечает, когда в чате делают reply на сообщение бота.
- Приветствует каждого пользователя только один раз в день.
- По умолчанию выбирает фразу из локального банка по словам сообщения.
- При включенном LLM отвечает по смыслу вопроса, а локальную базу использует только как стиль.
- Запоминает ответы пользователей на свои реплики и использует их как живые подсказки по тону.
- Дает короткий совет, когда его прямо просят совета.
- На `можно` отвечает отдельными казарменными рифмами.
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

LLM-слой опциональный. Бот настроен на OpenAI-compatible DeepSeek API.

```dotenv
LLM_ENABLED=auto
LLM_API_BASE=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_FALLBACK_MODELS=
LLM_API_KEY=your_deepseek_key
LLM_TIMEOUT_SECONDS=12
GREETING_STATE_PATH=.state/daily_greetings.json
USER_MEMORY_PATH=.state/user_reply_memory.json
USER_MEMORY_MAX_ITEMS=120
```

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
