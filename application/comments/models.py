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
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    user = relationship("User", backref="Comment")
    comment = relationship("Comment")

    def __init__(self, content):
        self.content = content