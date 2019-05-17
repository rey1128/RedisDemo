import time
import redis
import common_constants
import article_vote
import article_group


def post_article(redis_conn, user, title, link):
    article_id = str(redis_conn.incr('article:'))
    print('generated article_id: ' + article_id)
    voted = 'voted:up:' + article_id
    redis_conn.sadd(voted, user)
    redis_conn.expire(voted, common_constants.ONE_WEEK_IN_SECOND)
    article = 'article:' + article_id
    now = time.time()
    redis_conn.hmset(article, {
        'title': title,
        'link': link,
        'poster': user,
        'time': now,
        'votes': 1,
        'id': article_id
    })
    score = now + common_constants.VOTE_SCORE

    redis_conn.zadd('score:', {article: score})
    redis_conn.zadd('time:', {article: now})

    return article


def is_article_expired(redis_conn, article):
    cutoff = time.time() - common_constants.ONE_WEEK_IN_SECOND
    if redis_conn.zscore('time:', article) < cutoff:
        return True
    return False
    pass


def get_articles_by_score(redis_conn, num, key='score:'):
    articles_rt = []
    articles = redis_conn.zrevrange(key, 0, num)
    for article in articles:
        article_info = redis_conn.hgetall(article)
        # article_info['id'] = article
        articles_rt.append(article_info)

    return articles_rt
    pass


def show_article_scores(redis_conn):
    members = redis_conn.zrange('score:', 0, -1, withscores=True)
    for member in members:
        print(member)
    pass


def cleanup(redis_conn):
    keys = conn.keys('*')
    for key in keys:
        redis_conn.delete(key)

    keys_after = redis_conn.keys('*')
    if len(keys_after) == 0:
        print('redis has been cleaned up')
    pass


def main(redis_conn):
    group_to_add = ['test_group1', 'test_group2']
    for i in range(1, 10):
        # generate article and post
        user = 'user:' + str(i)
        title = 'test_title_' + str(i)
        link = 'http://test_link_' + str(i)
        article = post_article(redis_conn, user, title, link)
        # add into groups
        if i % 2 == 0:
            article_group.add_groups(redis_conn, article, to_add=group_to_add)
        print(article + " is post")

    ''' get articles from redis '''
    articles = get_articles_by_score(redis_conn, 20)
    for article in articles:
        print(article)

    show_article_scores(redis_conn)

    ''' vote up on articles '''
    rt = article_vote.vote_up(redis_conn, 'user:2', 'article:4')
    print('user:2 votes up on article:4 is successful: ' + str(rt))
    rt = article_vote.vote_up(redis_conn, 'user:2', 'article:4')
    print('user:2 votes up on article:4 is successful: ' + str(rt))
    rt = article_vote.vote_up(redis_conn, 'user:2', 'article:2')
    print('user:2 votes up on article:2 is successful: ' + str(rt))
    print(redis_conn.hgetall('article:2'))
    print(redis_conn.hgetall('article:4'))

    show_article_scores(redis_conn)

    ''' vote down on articles'''
    rt = article_vote.vote_down(redis_conn, 'user:4', 'article:2')
    print('user:4 votes down on article:2 is successful: ' + str(rt))
    rt = article_vote.vote_down(redis_conn, 'user:4', 'article:4')
    print('user:4 votes down on article:4 is successful: ' + str(rt))
    rt = article_vote.vote_down(redis_conn, 'user:4', 'article:4')
    print('user:4 votes down on article:4 is successful: ' + str(rt))
    print(redis_conn.hgetall('article:2'))
    print(redis_conn.hgetall('article:4'))

    show_article_scores(redis_conn)

    ''' group articles '''
    group_key = article_group.get_group_key(redis_conn, 'test_group1')
    grouped_articles = get_articles_by_score(redis_conn, 20, group_key)
    print("articles in test_group1")
    for article in grouped_articles:
        print(article)

    pass


if __name__ == "__main__":
    print('===== program starts =====')
    conn = redis.Redis(
        host='localhost',
        port=6379)
    try:
        main(conn)
    finally:
        ''' clean up '''
        cleanup(conn)
        pass

    print('===== program ends =====')
    pass
