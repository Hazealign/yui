import datetime
import unicodedata
from typing import Dict

from babel.dates import get_timezone

from fuzzywuzzy import fuzz

from sqlalchemy.sql.expression import func

__all__ = (
    'KOREAN_END',
    'KOREAN_START',
    'KST',
    'TRUNCATE_QUERY',
    'UTC',
    'bold',
    'bool2str',
    'code',
    'fuzzy_korean_ratio',
    'get_count',
    'italics',
    'normalize_korean_nfc_to_nfd',
    'preformatted',
    'quote',
    'strike',
    'truncate_table',
    'tz_none_to_kst',
    'tz_none_to_utc',
)

KST = get_timezone('Asia/Seoul')
UTC = get_timezone('UTC')

TRUNCATE_QUERY = {
    'mysql': 'TRUNCATE TABLE {};',
    'postgresql': 'TRUNCATE TABLE {} RESTART IDENTITY CASCADE;',
    'sqlite': 'DELETE FROM {};',
}

KOREAN_START = ord('가')
KOREAN_END = ord('힣')
KOREAN_ALPHABETS_FIRST_MAP: Dict[str, str] = {
    'ㄱ': chr(4352+0),
    'ㄲ': chr(4352+1),
    'ㄴ': chr(4352+2),
    'ㄷ': chr(4352+3),
    'ㄸ': chr(4352+4),
    'ㄹ': chr(4352+5),
    'ㅁ': chr(4352+6),
    'ㅂ': chr(4352+7),
    'ㅃ': chr(4352+8),
    'ㅅ': chr(4352+9),
    'ㅆ': chr(4352+10),
    'ㅇ': chr(4352+11),
    'ㅈ': chr(4352+12),
    'ㅉ': chr(4352+13),
    'ㅊ': chr(4352+14),
    'ㅋ': chr(4352+15),
    'ㅌ': chr(4352+16),
    'ㅍ': chr(4352+17),
    'ㅎ': chr(4352+18),
}

KOREAN_ALPHABETS_MIDDLE_MAP: Dict[str, str] = {
    chr(x+12623): chr(x+4449) for x in range(21+1)
}


def normalize_korean_nfc_to_nfd(value: str) -> str:
    """Normalize Korean string to NFD."""

    for from_, to_ in KOREAN_ALPHABETS_FIRST_MAP.items():
        value = value.replace(from_, to_)

    for from_, to_ in KOREAN_ALPHABETS_MIDDLE_MAP.items():
        value = value.replace(from_, to_)

    return ''.join(
        unicodedata.normalize('NFD', x) if KOREAN_START <= ord(x) <= KOREAN_END
        else x for x in list(value)
    )


def fuzzy_korean_ratio(str1: str, str2: str) -> int:
    """Fuzzy Search with Korean."""

    return fuzz.ratio(
        normalize_korean_nfc_to_nfd(str1),
        normalize_korean_nfc_to_nfd(str2),
    )


def tz_none_to_kst(dt: datetime.datetime) -> datetime.datetime:
    """Convert non tz datetime to KST."""

    return UTC.localize(dt).astimezone(KST)


def tz_none_to_utc(dt: datetime.datetime) -> datetime.datetime:
    """Convert non tz datetime to UTC."""

    return dt.astimezone(UTC)


def bold(text: str) -> str:
    """Make text to bold."""

    return f'*{text}*'


def italics(text: str) -> str:
    """Make text to italics."""

    return f'_{text}_'


def strike(text: str) -> str:
    """Make text to strike."""

    return f'~{text}~'


def code(text: str) -> str:
    """Make text to code."""

    return f'`{text}`'


def preformatted(text: str) -> str:
    """Make text to pre-formatted text."""

    return f'```{text}```'


def quote(text: str) -> str:
    """Make text to qoute."""

    return f'>{text}'


def bool2str(value: bool) -> str:
    """Return bool as str."""

    if value:
        return 'true'
    return 'false'


def truncate_table(engine, table_cls):
    """Truncate given table."""

    table_name = table_cls.__table__.name
    engine_name = engine.name

    with engine.begin() as conn:
        conn.execute(TRUNCATE_QUERY[engine_name].format(table_name))


def get_count(q) -> int:
    """
    Get count of record.

    https://gist.github.com/hest/8798884

    """

    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count
