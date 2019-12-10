from application import db

from application.posts.models import Post, PostLike, PostLikeValue
from application.auth.models import User
from application.comments.models import Comment

from sqlalchemy import case
from sqlalchemy.sql.expression import bindparam


__all__ = ('posts_with_aggregates',)

_posts_with_comment_count = (db.session()
    .query(Post.id.label('post_id'),
           db.func.count(Comment.post_id).label('comments'))
    .outerjoin(Comment, Comment.post_id == Post.id)
    .group_by(Post.id)
    .with_session(None)).subquery()

_posts_with_aggregates = (db.session()
    .query(Post,
           db.func.max(_posts_with_comment_count.c.comments).label('comments'),
           db.func.count(
                case([((PostLike.value == PostLikeValue.like), PostLike.value)])
           ).label('likes'),
           db.func.count(
                case([((PostLike.value == PostLikeValue.dislike), PostLike.value)])
           ).label('dislikes'),
           db.func.sum(
                case([((PostLike.value == PostLikeValue.like), 1)], else_=-1)
           ).label('popularity'),
           db.func.max(
                case([((PostLike.account_id == bindparam('user_id')), PostLike.value)])
           ).label('userLike'))
    .outerjoin(User, User.id == Post.account_id)
    .outerjoin(_posts_with_comment_count, _posts_with_comment_count.c.post_id == Post.id)
    .outerjoin(PostLike, PostLike.post_id == Post.id)
    .group_by(Post.id)
    .with_session(None))


def posts_with_aggregates(session, user_id=None):
    return (_posts_with_aggregates
        .with_session(session)
        .params(user_id=user_id))