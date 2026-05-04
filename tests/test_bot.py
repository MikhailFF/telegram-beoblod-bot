from types import SimpleNamespace

from morale_bot.bot import (
    BotReply,
    JOKES,
    build_reply,
    choose_emoji,
    choose_rhyme_answer,
    is_private_update,
    is_mentioned,
    normalize_username,
)


def make_message(text: str):
    return SimpleNamespace(text=text, entities=None)


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


def test_joke_bank_has_warrant_officer_variety():
    assert len(JOKES) >= 30


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
