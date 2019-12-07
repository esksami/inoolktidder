from application import db
from application.models import Base, TimestampMixin

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text

import enum


class Post(Base, TimestampMixin):
    title = db.Column(db.String(512), nullable=False)
    content = db.Column(db.String(8192), nullable=False)

    account_id = db.Column(
        db.Integer,
        db.ForeignKey('account.id'),
        nullable=False
    )

    user = relationship("User", backref="post")

    def __init__(self, title, content):
        self.title = title
        self.content = content

class PostLikeValue(enum.Enum):
    dislike = -1
    like = 1

class PostLike(Base):
    value = db.Column(db.Enum(PostLikeValue), nullable=False)

    post_id = db.Column(
        db.Integer,
        db.ForeignKey('post.id'),
        nullable=False
    )
    account_id = db.Column(
        db.Integer,
        db.ForeignKey('account.id'),
        nullable=False
    )

    post = relationship("Post", backref="post_like")
    user = relationship("User", backref="post_like")

    __table_args__ = (
        UniqueConstraint('post_id', 'account_id'),
    )