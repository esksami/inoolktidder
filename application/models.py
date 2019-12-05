from application import db

from datetime import datetime


class Base(db.Model):
    __abstract__ = True
  
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def time_since_created(self):
        delta = datetime.utcnow() - self.date_created

        unitValuePairs = (
            ('year', delta.days // 265.24),
            ('month', delta.days // 30.44),
            ('week', delta.days // 7),
            ('day', delta.days),
            ('hour', delta.seconds // 3600),
            ('minute', delta.seconds // 60),
            ('second', delta.seconds)
        )

        unit, value = next(
            (unit, int(value)) for unit, value in unitValuePairs if value > 0
        )

        plural = 's' if value > 1 else ''

        return f'{value} {unit}{plural} ago'