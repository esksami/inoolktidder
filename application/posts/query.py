from application import db

from application.posts.models import Post, PostLike, PostLikeValue
from application.auth.models import User
from application.comments.models import Comment

from sqlalchemy import and_
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import bindparam

__all__ = ('posts_with_aggregates',)

postLikes = aliased(PostLike, name='post_likes')
postDislikes = aliased(PostLike, name='post_dislikes')
userLike = aliased(PostLike, name='user_like')

_posts_with_comment_count = (db.session()
    .query(Post.id.label('post_id'),
           db.func.count(Comment.post_id).label('comments'))
    .outerjoin(Comment, Comment.post_id == Post.id)
    .group_by(Post.id)
    .with_session(None)).subquery()

_posts_with_aggregates = (db.session()
    .query(Post,
           db.func.max(_posts_with_comment_count.c.comments).label('comments'),
           db.func.count(postLikes.value).label('likes'),
           db.func.count(postDislikes.value).label('dislikes'),
           (db.func.count(postLikes.value).label('likes') - 
            db.func.count(postDislikes.value).label('dislikes')).label('popularity'),
           db.func.max(userLike.value).label('userLike'))
    .outerjoin(User, User.id == Post.account_id)
    .outerjoin(_posts_with_comment_count, _posts_with_comment_count.c.post_id == Post.id)
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


def posts_with_aggregates(session, user_id=None):
    return (_posts_with_aggregates
        .with_session(session)
        .params(user_id=user_id))