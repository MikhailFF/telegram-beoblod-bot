from types import SimpleNamespace
from pathlib import Path
import asyncio

from morale_bot.bot import (
    ADVICES,
    BotReply,
    CAN_ANSWERS,
    EXTERNAL_GREETINGS,
    EXTERNAL_PHRASES,
    GREETINGS,
    JOKES,
    DEFAULT_LLM_MODEL,
    MAX_REPLY_WORDS,
    build_response_text,
    build_message_context,
    build_llm_messages,
    build_local_reply_text,
    build_reply,
    clean_phrase_line,
    choose_emoji,
    choose_contextual_line,
    choose_rhyme_answer,
    compact_reply,
    finalize_llm_reply,
    limit_reply_words,
    looks_like_bad_llm_reply,
    llm_models,
    is_reply_to_bot,
    is_private_update,
    is_mentioned,
    is_advice_request,
    load_user_memory,
    normalize_username,
    relevant_user_memory,
    remember_user_reply,
    save_user_memory,
    should_greet_today,
)


def make_message(text: str, user_id=7, username="User"):
    user = SimpleNamespace(id=user_id, username=username)
    return SimpleNamespace(text=text, entities=None, from_user=user, chat_id=-100)


def make_reply_message(reply_user_id=42, reply_username="MoraleBot", reply_text="Предыдущий ответ бота"):
    reply_user = SimpleNamespace(id=reply_user_id, username=reply_username)
    reply_to = SimpleNamespace(from_user=reply_user, text=reply_text, caption=None)
    return SimpleNamespace(text="ну что", entities=None, reply_to_message=reply_to)


def make_update(chat_type: str):
    return SimpleNamespace(effective_chat=SimpleNamespace(type=chat_type))


def test_normalize_username():
    assert normalize_username("@MoraleBot") == "moralebot"
    assert normalize_username("MoraleBot") == "moralebot"
    assert normalize_username(None) is None


def test_is_mentioned_matches_exact_bot_name():
    assert is_mentioned(make_message("эй @MoraleBot подскажи"), "moralebot")
    assert is_mentioned(make_message("@moralebot"), "@MoraleBot")


def test_is_mentioned_does_not_match_prefix_only():
    assert not is_mentioned(make_message("@MoraleBotExtra привет"), "moralebot")
    assert not is_mentioned(make_message("без тега"), "moralebot")


def test_private_updates_are_blocked():
    assert is_private_update(make_update("private"))
    assert not is_private_update(make_update("group"))


def test_reply_render_is_short_and_has_no_labels():
    reply = BotReply(
        greeting="Так, боец",
        emoji="🫡",
        reaction="Мысль стоит криво. Поправим.",
        joke="Армия, сынок, это климат.",
        advice="Сначала чай. Потом решение.",
        closing="Свободен. Но недалеко.",
    )
    rendered = reply.render()

    assert "Так, боец" in rendered
    assert "Армия, сынок" in rendered
    assert "<b>Шутка:</b>" not in rendered
    assert "<b>Совет:</b>" not in rendered
    assert rendered.count("\n\n") <= 2


def test_compact_reply_is_single_line():
    rendered = compact_reply("  one\n\n two  ", max_chars=20)
    assert rendered == "one two"
    assert "\n" not in rendered


def test_limit_reply_words_truncates_long_answer():
    rendered = limit_reply_words(" ".join(f"word{i}" for i in range(MAX_REPLY_WORDS + 5)))
    assert len(rendered.split()) <= MAX_REPLY_WORDS
    assert rendered.endswith("…")


def test_contextual_reply_uses_message_tokens():
    line = choose_contextual_line("я устал")
    assert "устал" in line.lower()


def test_advice_request_uses_advice_bank():
    assert is_advice_request("дай совет по делу")
    assert choose_contextual_line("дай совет по делу") in ADVICES


def test_local_reply_is_one_short_line():
    rendered = build_local_reply_text("@MoraleBot я устал")
    assert "\n" not in rendered
    assert len(rendered) <= 280


def test_local_reply_can_skip_daily_greeting():
    rendered = build_local_reply_text("@MoraleBot СЏ СѓСЃС‚Р°Р»", include_greeting=False)
    assert "\n" not in rendered
    assert len(rendered) <= 280
    assert not any(greeting in rendered for greeting in GREETINGS[:20])


def test_should_greet_today_only_once_per_user():
    state_path = Path("tests") / ".daily_greetings_test.json"
    message = make_message("@MoraleBot РїРѕРјРѕРіРё", user_id=123, username="soldier")

    try:
        assert should_greet_today(message, today="2026-05-07", state_path=state_path)
        assert not should_greet_today(message, today="2026-05-07", state_path=state_path)
        assert should_greet_today(message, today="2026-05-08", state_path=state_path)
    finally:
        state_path.unlink(missing_ok=True)
        state_path.with_suffix(f"{state_path.suffix}.tmp").unlink(missing_ok=True)


def test_user_reply_memory_records_replies_to_bot():
    state_path = Path("tests") / ".user_memory_test.json"
    message = make_reply_message(reply_user_id=42, reply_username="MoraleBot")
    message.chat_id = -100
    message.from_user = SimpleNamespace(id=123, username="soldier")
    message.text = "short field reaction"

    try:
        assert remember_user_reply(message, 42, "MoraleBot", state_path)
        memory = load_user_memory(state_path)

        assert memory[-1]["chat_id"] == "-100"
        assert memory[-1]["user_id"] == "123"
        assert memory[-1]["text"] == "short field reaction"
        assert relevant_user_memory(-100, state_path) == ["short field reaction"]
    finally:
        state_path.unlink(missing_ok=True)
        state_path.with_suffix(f"{state_path.suffix}.tmp").unlink(missing_ok=True)


def test_user_reply_memory_trims_and_deduplicates(monkeypatch):
    state_path = Path("tests") / ".user_memory_trim_test.json"
    monkeypatch.setenv("USER_MEMORY_MAX_ITEMS", "2")
    memory = [
        {"chat_id": "-100", "user_id": "1", "text": "first"},
        {"chat_id": "-100", "user_id": "2", "text": "second"},
        {"chat_id": "-100", "user_id": "3", "text": "second"},
        {"chat_id": "-100", "user_id": "4", "text": "third"},
    ]

    try:
        save_user_memory(memory, state_path)

        assert [item["text"] for item in load_user_memory(state_path)] == ["second", "third"]
        assert relevant_user_memory(-100, state_path) == ["second", "third"]
    finally:
        state_path.unlink(missing_ok=True)
        state_path.with_suffix(f"{state_path.suffix}.tmp").unlink(missing_ok=True)


def test_llm_prompt_controls_daily_greeting():
    first_messages = build_llm_messages("СЏ СѓСЃС‚Р°Р»", "draft", include_greeting=True)
    repeat_messages = build_llm_messages("СЏ СѓСЃС‚Р°Р»", "draft", include_greeting=False)

    assert "еще не здоровались" in first_messages[0]["content"]
    assert "НЕ здоровайся" in repeat_messages[0]["content"]
    assert "строго в контексте" in repeat_messages[1]["content"]
    assert "Не придумывай кнопки" in repeat_messages[0]["content"]


def test_llm_prompt_includes_user_memory():
    messages = build_llm_messages("give advice", "draft", include_greeting=False, memory_lines=["user liked short answers"])

    assert "user liked short answers" in messages[1]["content"]


def test_llm_uses_deepseek_chat_model(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_FALLBACK_MODELS", raising=False)

    assert DEFAULT_LLM_MODEL == "deepseek-chat"
    assert llm_models() == ["deepseek-chat"]


def test_bad_llm_reply_is_rejected():
    assert looks_like_bad_llm_reply("Sorry, as an AI I cannot help.")
    assert not looks_like_bad_llm_reply("Так, боец, сначала сядь и выдохни.")


def test_final_llm_reply_cleans_thinking_and_adds_bite():
    rendered = finalize_llm_reply("<think>secret</think>Так, боец, сначала выдохни.", "Запасной ответ.")
    lowered = rendered.lower()

    assert "think" not in lowered
    assert any(marker in lowered for marker in ("бляд", "хер", "мать", "пельмень"))
    assert len(rendered.split()) <= MAX_REPLY_WORDS


def test_response_fallback_keeps_role_bite(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "false")
    rendered = asyncio.run(build_response_text("@MoraleBot я устал", "MoraleBot", None, include_greeting=False))
    lowered = rendered.lower()

    assert any(marker in lowered for marker in ("бляд", "хер", "мать", "пельмень"))


def test_message_context_includes_reply_text():
    message = make_reply_message(reply_text="Сначала проверь ключ API.")
    message.text = "почему не работает?"

    context = build_message_context(message, "MoraleBot")

    assert "Сначала проверь ключ API" in context
    assert "почему не работает" in context


def test_reply_to_bot_is_triggered_by_bot_id_or_username():
    assert is_reply_to_bot(make_reply_message(reply_user_id=42), 42, "OtherBot")
    assert is_reply_to_bot(make_reply_message(reply_user_id=7, reply_username="MoraleBot"), 42, "@MoraleBot")
    assert not is_reply_to_bot(make_reply_message(reply_user_id=7, reply_username="OtherBot"), 42, "@MoraleBot")


def test_joke_bank_has_warrant_officer_variety():
    assert len(JOKES) >= 30


def test_external_phrase_files_are_loaded():
    assert len(EXTERNAL_PHRASES) >= 100


def test_external_greetings_are_loaded():
    assert len(EXTERNAL_GREETINGS) >= 100
    assert any(greeting in GREETINGS for greeting in EXTERNAL_GREETINGS)


def test_clean_phrase_line_skips_headers():
    assert clean_phrase_line("1. Боец, мысль стоит криво.") == "Боец, мысль стоит криво."
    assert clean_phrase_line("1. РУССКИЙ И СОВЕТСКИЙ АРМЕЙСКИЙ АБСУРД") is None
    assert clean_phrase_line("Оригинальные реплики прапорщика") is None


def test_choose_emoji_matches_topic():
    assert choose_emoji("подлодка и море") == "⚓"
    assert choose_emoji("летчик и самолет") == "✈️"


def test_build_reply_has_content_for_mozhno():
    reply = build_reply("@MoraleBot можно?")
    assert reply.joke
    assert len(reply.greeting) > 0


def test_mozhno_bank_has_expanded_rhymes():
    assert any("Машку" in answer for answer in CAN_ANSWERS)
    assert any("Телегу" in answer or "телегу" in answer for answer in CAN_ANSWERS)


def test_choose_rhyme_answer_for_trigger_word():
    answer = choose_rhyme_answer("@MoraleBot триста")
    assert answer is not None
    assert "тракторист" in answer
