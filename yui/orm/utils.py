import calendar
import datetime

import pytz

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.sql.expression import func
from sqlalchemy.types import DateTime

import tzlocal

from .type import TimezoneType

__all__ = (
    'TRUNCATE_QUERY',
    'get_count',
    'insert_datetime_field',
    'truncate_table',
)

TRUNCATE_QUERY = {
    'mysql': 'TRUNCATE TABLE {};',
    'postgresql': 'TRUNCATE TABLE {} RESTART IDENTITY CASCADE;',
    'sqlite': 'DELETE FROM {};',
}


def insert_datetime_field(name, locals_, nullable: bool = True):
    datetime_key = f'{name}_datetime'
    timezone_key = f'{name}_timezone'
    locals_[datetime_key] = Column(
        DateTime(timezone=False),
        nullable=nullable,
    )
    locals_[timezone_key] = Column(TimezoneType())

    def getter(self):
        if getattr(self, timezone_key):
            return getattr(self, timezone_key).localize(
                getattr(self, datetime_key)
            )
        else:
            return getattr(self, datetime_key)

    def setter(self, dt: datetime.datetime):
        if dt.tzinfo is pytz.UTC:
            d = datetime.datetime.fromtimestamp(
                calendar.timegm(dt.timetuple())
            )
            setattr(self, datetime_key,
                    d - tzlocal.get_localzone().utcoffset(d))
            setattr(self, timezone_key, pytz.UTC)
        else:
            setattr(self, timezone_key, dt.tzinfo)
            setattr(self, datetime_key, dt.replace(tzinfo=None))

    locals_[f'{name}_at'] = hybrid_property(fget=getter, fset=setter)


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
