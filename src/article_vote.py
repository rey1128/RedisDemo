import article_service
import common_constants


def vote_up(redis_conn, user, article):
    if article_service.is_article_expired(redis_conn, article):
        print(article + ' is expired')
        return False
    article_id = article.partition(':')[-1]
    if redis_conn.smove('voted:down:' + article_id, 'voted:up:' + article_id, user) or redis_conn.sadd(
            'voted:up:' + article_id,
            user):
        redis_conn.zincrby('score:', common_constants.VOTE_SCORE, article)
        redis_conn.hincrby(article, 'votes', 1)
        return True
    else:
        print(user + ' already votes up on ' + article)
    return False


def vote_down(redis_conn, user, article):
    if article_service.is_article_expired(redis_conn, article):
        print(article + ' is expired')
        return False
    article_id = article.partition(':')[-1]
    if redis_conn.smove('voted:up' + article_id, 'voted:down:' + article_id, user) or redis_conn.sadd(
            'voted:down:' + article_id,
            user):
        redis_conn.zincrby('score:', -common_constants.VOTE_SCORE, article)
        redis_conn.hincrby(article, 'votes', -1)
        return True
    else:
        print(user + ' already votes down on ' + article)
    return False
