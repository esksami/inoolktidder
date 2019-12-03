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

    @staticmethod
    def user_post_count(user_id):
        stmt = text(
            'SELECT count(*) FROM Post WHERE Post.account_id = :user_id'
        ).params(user_id=user_id)

        response = db.engine.execute(stmt)

        for row in response:
            return row[0]

        return 0