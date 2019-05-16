import time
import redis

ONE_WEEK_IN_SECOND = 7 * 86400
VOTE_SCORE = 420

conn = redis.Redis(
    host='localhost',
    port=6379)


def article_vote(user, article):
    cutoff = time.time() - ONE_WEEK_IN_SECOND
    if conn.zscore('time', article) < cutoff:
        return
    article_id = article.partition(':')[-1]
    if conn.sadd('voted:' + article_id, user):
        conn.zincrby('score:', article, VOTE_SCORE)
        conn.hincrby(article, 'votes', 1)
    pass


def post_article(user, title, link):
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


def get_articles_by_score(num):
    articles_rt = []
    articles = conn.zrevrange('score:', 0, num)
    for article in articles:
        article_info = conn.hgetall(article)
        article_info['id'] = article
        articles_rt.append(article_info)

    return articles_rt
    pass


def cleanup():
    keys = conn.keys('*')
    for key in keys:
        conn.delete(key)

    keys_after = conn.keys('*')
    if len(keys_after) == 0:
        print('redis has been cleaned up')
    pass


def main():
    for i in range(10):
        # generate article and post
        user = 'user:' + str(i)
        title = 'test_title_' + str(i)
        link = 'http://test_link_' + str(i)
        article = post_article(user, title, link)
        print(article + " is post")

    # get articles from redis
    articles = get_articles_by_score(20)
    for article in articles:
        print(article)
    # clean up
    cleanup()
    pass


if __name__ == "__main__":
    print('===== program starts =====')
    main()
    print('===== program ends =====')
    pass
