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

    @staticmethod
    def user_post_count(user_id):
        stmt = text(
            'SELECT count(*) FROM Post WHERE Post.account_id = :user_id'
        ).params(user_id=user_id)

        response = db.engine.execute(stmt)

        for row in response:
            return row[0]

        return 0