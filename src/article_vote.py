import article_service
import common_constants


def vote_up(redis_conn, user, article_key):
    if article_service.is_article_expired(redis_conn, article_key):
        print(article_key + ' is expired')
        return False
    article_id = article_key.partition(':')[-1]
    if redis_conn.smove('voted:down:' + article_id, 'voted:up:' + article_id, user) or redis_conn.sadd(
            'voted:up:' + article_id,
            user):
        redis_conn.zincrby('score:', common_constants.VOTE_SCORE, article_key)
        redis_conn.hincrby(article_key, 'votes', 1)
        return True
    else:
        print(user + ' already votes up on ' + article_key)
    return False


def vote_down(redis_conn, user, article_key):
    if article_service.is_article_expired(redis_conn, article_key):
        print(article_key + ' is expired')
        return False
    article_id = article_key.partition(':')[-1]
    if redis_conn.smove('voted:up' + article_id, 'voted:down:' + article_id, user) or redis_conn.sadd(
            'voted:down:' + article_id,
            user):
        redis_conn.zincrby('score:', -common_constants.VOTE_SCORE, article_key)
        redis_conn.hincrby(article_key, 'votes', -1)
        return True
    else:
        print(user + ' already votes down on ' + article_key)
    return False
