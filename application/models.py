from sqlalchemy.orm import column_property
from sqlalchemy.ext.declarative import declared_attr

from application import db


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)


class TimestampMixin:
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    @declared_attr
    def seconds_since_created(cls):
        return column_property(
            db.extract('epoch', db.func.current_timestamp()) - 
            db.extract('epoch', cls.date_created)
        )

    def time_since_created_str(self):
        seconds = self.seconds_since_created

        unitValuePairs = (
            ('year', seconds // (60*60*24*365.24)),
            ('month', seconds // (60*60*24*30.44)),
            ('week', seconds // (60*60*24*7)),
            ('day', seconds // (60*60*24)),
            ('hour', seconds // (60*60)),
            ('minute', seconds // 60),
            ('second', seconds)
        )

        try:
            unit, value = next(
                (unit, int(value)) for unit, value in unitValuePairs if int(value) > 0
            )
        except StopIteration:
            return 'Just now'

        plural = 's' if value > 1 else ''

        return f'{value} {unit}{plural} ago'