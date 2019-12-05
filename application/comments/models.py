from application import db
from application.models import Base

from sqlalchemy.orm import relationship
from sqlalchemy.sql import text

from datetime import datetime


class Comment(Base):
    content = db.Column(db.String(4096))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    deleted = db.Column(db.Boolean, default=False)

    user = relationship("User", backref="Comment")
    comment = relationship("Comment")


    def __init__(self, content):
        self.content = content

    def time_since_created(self):
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