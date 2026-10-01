from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ExtractionQuality:
    character_count: int
    printable_ratio: float
    word_density: float
    malformed_ratio: float
    rendered_nonempty: bool
    score: float

    def as_dict(self) -> dict:
        return asdict(self)


def score_page(words: list[dict], rendered_nonempty: bool) -> ExtractionQuality:
    text = "".join(word["text"] for word in words)
    characters = len(text)
    printable = sum(character.isprintable() or character.isspace() for character in text)
    malformed = text.count("\ufffd")
    printable_ratio = printable / characters if characters else 0.0
    malformed_ratio = malformed / characters if characters else 0.0
    # Normalized page area is one, so density is expressed against a useful page-word target.
    word_density = min(1.0, len(words) / 80)
    character_score = min(1.0, characters / 400)
    text_score = 0.45 * character_score + 0.25 * printable_ratio + 0.20 * word_density + 0.10 * (1 - malformed_ratio)
    # A visually blank page is accepted without OCR; visible content plus sparse text is a strong OCR signal.
    score = text_score if rendered_nonempty else max(text_score, 0.65)
    # A short but clean native-text page (title, single-page note, or sparse appendix)
    # should not be needlessly OCRed.
    if characters >= 24 and printable_ratio >= 0.98 and malformed_ratio == 0:
        score = max(score, 0.65)
    return ExtractionQuality(characters, printable_ratio, word_density, malformed_ratio, rendered_nonempty, round(score, 4))
