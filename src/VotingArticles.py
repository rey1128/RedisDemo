import time
import redis
from GroupingArticles import *

ONE_WEEK_IN_SECOND = 7 * 86400
VOTE_SCORE = 420


def article_vote(conn, user, article):
    cutoff = time.time() - ONE_WEEK_IN_SECOND
    if conn.zscore('time:', article) < cutoff:
        print(article + ' is expired')
        return False
    article_id = article.partition(':')[-1]
    if conn.sadd('voted:' + article_id, user):
        conn.zincrby('score:', VOTE_SCORE, article)
        conn.hincrby(article, 'votes', 1)
        return True
    else:
        print(user + ' already votes on ' + article)
    return False


def post_article(conn, user, title, link):
    article_id = str(conn.incr('article:'))
    print('generated article_id: ' + article_id)
    voted = 'voted:' + article_id
    conn.sadd(voted, user)
    conn.expire(voted, ONE_WEEK_IN_SECOND)
    article = 'article:' + article_id
    now = time.time()
    conn.hmset(article, {
        'title': title,
        'link': link,
        'poster': user,
        'time': now,
        'votes': 1
    })
    score = now + VOTE_SCORE

    print('score is: ' + str(score))
    conn.zadd('score:', {article: score})
    conn.zadd('time:', {article: now})

    return article


def get_articles_by_score(conn, num, key='score:'):
    articles_rt = []
    articles = conn.zrevrange(key, 0, num)
    for article in articles:
        article_info = conn.hgetall(article)
        article_info['id'] = article
        articles_rt.append(article_info)

    return articles_rt
    pass


def cleanup(conn):
    keys = conn.keys('*')
    for key in keys:
        conn.delete(key)

    keys_after = conn.keys('*')
    if len(keys_after) == 0:
        print('redis has been cleaned up')
    pass


def main(conn):
    group_to_add = ['test_group1', 'test_group2']
    for i in range(1, 10):
        # generate article and post
        user = 'user:' + str(i)
        title = 'test_title_' + str(i)
        link = 'http://test_link_' + str(i)
        article = post_article(conn, user, title, link)
        if i % 2 == 0:
            add_remove_groups(conn, article, to_add=group_to_add)
        print(article + " is post")

    ''' get articles from redis '''
    articles = get_articles_by_score(conn, 20)
    for article in articles:
        print(article)

    ''' vote on articles '''
    rt = article_vote(conn, 'user:2', 'article:4')
    print('user:2 votes on article:4 is successful: ' + str(rt))
    rt = article_vote(conn, 'user:2', 'article:2')
    print('user:2 votes on article:2 is successful: ' + str(rt))

    ''' group articles '''
    grouped_articles = get_group_articles(conn, 'test_group1')
    print("articles in test_group1")
    for article in grouped_articles:
        print(article)

    ''' clean up '''
    cleanup(conn)
    pass


if __name__ == "__main__":
    print('===== program starts =====')
    conn = redis.Redis(
        host='localhost',
        port=6379)
    main(conn)
    print('===== program ends =====')
    pass
