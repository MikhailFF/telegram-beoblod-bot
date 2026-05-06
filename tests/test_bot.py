from types import SimpleNamespace

from morale_bot.bot import (
    BotReply,
    EXTERNAL_GREETINGS,
    EXTERNAL_PHRASES,
    GREETINGS,
    JOKES,
    build_local_reply_text,
    build_reply,
    clean_phrase_line,
    choose_emoji,
    choose_contextual_line,
    choose_rhyme_answer,
    compact_reply,
    is_reply_to_bot,
    is_private_update,
    is_mentioned,
    normalize_username,
)


def make_message(text: str):
    return SimpleNamespace(text=text, entities=None)


def make_reply_message(reply_user_id=42, reply_username="MoraleBot"):
    reply_user = SimpleNamespace(id=reply_user_id, username=reply_username)
    reply_to = SimpleNamespace(from_user=reply_user)
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


def test_contextual_reply_uses_message_tokens():
    line = choose_contextual_line("я устал")
    assert "устал" in line.lower()


def test_local_reply_is_one_short_line():
    rendered = build_local_reply_text("@MoraleBot я устал")
    assert "\n" not in rendered
    assert len(rendered) <= 280


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


def test_choose_rhyme_answer_for_trigger_word():
    answer = choose_rhyme_answer("@MoraleBot триста")
    assert answer is not None
    assert "тракторист" in answer
