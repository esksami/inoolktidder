from application import db

from application.posts.models import Post, PostLike, PostLikeValue
from application.auth.models import User
from application.comments.models import Comment

from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import bindparam


class PostQuery():
    postLikes = aliased(PostLike)
    postDislikes = aliased(PostLike)
    userLike = aliased(PostLike)

    comment_count_query = (db.session()
        .query(Post.id.label('post_id'),
               db.func.count(Comment.post_id).label('comments'))
        .outerjoin(Comment, Comment.post_id == Post.id)
        .group_by(Post.id)
        .with_session(None)).subquery()

    base_query = (db.session()
        .query(Post,
               comment_count_query.c.comments.label('comments'),
               db.func.count(postLikes.value).label('likes'),
               db.func.count(postDislikes.value).label('dislikes'),
               userLike.value.label('userLike'))
        .outerjoin(User, User.id == Post.account_id)
        .outerjoin(comment_count_query, comment_count_query.c.post_id == Post.id)
        .outerjoin(postLikes,
                   and_(postLikes.post_id == Post.id,
                        postLikes.value == PostLikeValue.like))
        .outerjoin(postDislikes,
                   and_(postDislikes.post_id == Post.id,
                        postDislikes.value == PostLikeValue.dislike))
        .outerjoin(userLike,
                   and_(userLike.post_id == Post.id,
                        userLike.account_id == bindparam('user_id')))
        .group_by(Post.id)
        .with_session(None))

    @classmethod
    def all(cls, session, user_id=None):
        return (cls.base_query
            .with_session(session)
            .params(user_id=user_id))