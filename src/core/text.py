"""
文字列の正規化と、読みの並び順

表記の揺れの照合(normalize_for_match)と、Song List の五十音・ABC 順
(reading_sort_key)の決まりを1か所にまとめます。仕様は docs/specs/data-model.md。
"""

import re
import unicodedata
from typing import Tuple

_SPACES = re.compile(r"\s+")


def to_hiragana(text: str) -> str:
    """カタカナをひらがなにする(長音記号などはそのまま)"""
    return "".join(
        chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch
        for ch in text
    )


def remove_invisible(text: str) -> str:
    """
    見えない書式文字(Unicode のカテゴリ Cf)を取り除く

    ゼロ幅スペース(U+200B)・単語結合子(U+2060)・BOM(U+FEFF)など。
    コメントに混じると、見た目は同じでも既存の曲に当たらなくなる。
    """
    if not text:
        return ""
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cf")


def normalize_for_match(text: str) -> str:
    """
    表記の揺れを照合するための正規化

    NFKC(全角英数 → 半角など)、見えない文字の除去、小文字化、空白の除去、カタカナ → ひらがな。
    """
    if not text:
        return ""
    text = remove_invisible(unicodedata.normalize("NFKC", text)).lower()
    text = _SPACES.sub("", text)
    return to_hiragana(text)


def _char_group(ch: str) -> int:
    """並びのグループ: 0=記号・数字、1=英字、2=かな、3=その他"""
    if ch.isascii():
        return 1 if ch.isalpha() else 0
    if "ぁ" <= ch <= "ゖ" or ch == "ー":
        return 2
    return 3


def reading_sort_key(reading: str, fallback: str = "") -> Tuple[int, str]:
    """
    読みで並べるときのキー

    「記号・数字 → 英字(A-Z、大文字小文字を区別しない) → かな(五十音) → その他」の順。
    読みが空なら fallback(表示名)で並べる。
    """
    text = normalize_for_match(reading) or normalize_for_match(fallback)
    if not text:
        return (9, "")
    return (_char_group(text[0]), text)
