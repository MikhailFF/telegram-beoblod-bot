from types import SimpleNamespace

from morale_bot.bot import (
    BotReply,
    JOKES,
    build_reply,
    choose_emoji,
    choose_rhyme_answer,
    is_mentioned,
    normalize_username,
)


def make_message(text: str):
    return SimpleNamespace(text=text, entities=None)


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


def test_reply_render_contains_greeting_joke_and_advice():
    reply = BotReply(
        greeting="Привет, салага",
        emoji="🫡",
        reaction="Реакция",
        joke="Шутка",
        advice="Совет",
        closing="Добивка",
    )
    rendered = reply.render()

    assert "Привет, салага" in rendered
    assert "Реакция" in rendered
    assert "Шутка" in rendered
    assert "Совет" in rendered
    assert "Добивка" in rendered
    assert "<b>Шутка:</b>" not in rendered
    assert "<b>Совет:</b>" not in rendered


def test_joke_bank_has_book_inspired_variety():
    assert len(JOKES) >= 80


def test_choose_emoji_matches_topic():
    assert choose_emoji("подлодка и море") == "⚓"
    assert choose_emoji("летчик и самолет") == "✈️"


def test_build_reply_has_can_answer_for_mozhno():
    reply = build_reply("@MoraleBot можно?")
    assert reply.joke


def test_choose_rhyme_answer_for_trigger_word():
    answer = choose_rhyme_answer("@MoraleBot триста")
    assert answer is not None
    assert "тракториста" in answer
