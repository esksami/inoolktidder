from application import db
from application.models import Base

from sqlalchemy.orm import relationship
from sqlalchemy.sql import text

from datetime import datetime


class Post(Base):
    title = db.Column(db.String(512), nullable=False)
    content = db.Column(db.String(8192), nullable=False)
    likes = db.Column(db.Integer, default=0)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
                           nullable=False)

    user = relationship("User", backref="Post")

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def time_since_posted(self):
        delta = datetime.now() - self.date_created

        unit, value = '', 0

        if not delta.days:
            if delta.seconds < 60:
                unit = 'second'
                value = delta.seconds
            elif delta.seconds < 3600:
                unit = 'minute'
                value = delta.seconds // 60
            else:
                unit = 'hour'
                value = delta.seconds // 3600
        else:
            if delta.days < 7:
                unit = 'day'
                value = delta.days
            elif delta.days < 30.44:
                unit = 'week'
                value = delta.days // 7
            elif delta.days < 365.24:
                unit = 'month'
                value = delta.days // 30.44
            else:
                unit = 'year'
                value = delta.days // 365.24

        plural = 's' if value > 1 else ''

        return f'{value} {unit}{plural} ago'

    @staticmethod
    def user_post_count(user_id):
        stmt = text(
            'SELECT count(*) FROM Post WHERE Post.account_id = :user_id'
        ).params(user_id=user_id)

        response = db.engine.execute(stmt)

        for row in response:
            return row[0]

        return 0