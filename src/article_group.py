def get_group_key(redis_conn, group):
    key = 'score:' + group
    if not redis_conn.exists(key):
        redis_conn.zinterstore(key, ['group:' + group, 'score:'], aggregate='max')
        redis_conn.expire(key, 60)

    return key


def add_groups(redis_conn, article, to_add=[]):
    for group in to_add:
        redis_conn.sadd('group:' + group, article)

    pass
