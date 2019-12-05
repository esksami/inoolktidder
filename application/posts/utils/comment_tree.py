from itertools import groupby

def create_comment_tree(comments):
    commentsByParentId = _comments_by_parent_id(comments)
    roots = [c for c in comments if c.parent_id is None]

    for root in roots:
        root.children = _populate(root, commentsByParentId)

    return roots

def _populate(comment, commentsByParentId):
    try:
        children = commentsByParentId[comment.id]
    except KeyError:
        return []

    for child in children:
        child.children = _populate(child, commentsByParentId)

    return children

def _comments_by_parent_id(comments):
    getParentId = lambda c: c.parent_id

    childComments = [c for c in comments if c.parent_id is not None]
    sortedComments = sorted(childComments, key=getParentId)
    groups = groupby(sortedComments, key=getParentId)

    return {parent_id: list(children) for parent_id, children in groups}