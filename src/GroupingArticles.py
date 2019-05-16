
from VotingArticles import *
def get_group_articles(conn, group):
    key = 'score:' + group
    if not conn.exists(key):
        conn.zinterstore(key, ['group:' + group, 'score:'], aggregate='max')
        conn.expire(key, 60)

    return get_articles_by_score(conn, 20, key)


def add_remove_groups(conn, article, to_add=[], to_remove=[]):

    for group in to_add:
        conn.sadd('group:' + group, article)

    for group in to_remove:
        conn.srem('group:' + group, article)

    pass
