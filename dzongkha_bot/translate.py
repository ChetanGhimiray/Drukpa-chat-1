"""Small script-check helper for Dzongkha output validation."""

_TIBETAN_PUNCT = set("་།༎༏༐༑༔")


def dzongkha_script_ratio(text: str) -> float:
    """Share of letters in the Tibetan script, used as a basic output check.

    Dzongkha and Tibetan share this script, so this cannot verify grammar or
    distinguish the two languages. It only catches output in the wrong script.
    """
    tibetan = sum(1 for char in text if "ༀ" <= char <= "࿿" and char not in _TIBETAN_PUNCT)
    latin = sum(1 for char in text if char.isascii() and char.isalpha())
    total = tibetan + latin
    return 1.0 if total == 0 else tibetan / total
