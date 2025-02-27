"""Insta485 model (database) API."""
import sqlite3
import flask
import insta485


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if 'sqlite_db' not in flask.g:
        db_filename = insta485.app.config['DATABASE_FILENAME']
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory

        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")
    return flask.g.sqlite_db


def get_recent_postid():
    """Return the id of the most recent post.

    Return as an Integer
    """
    connection = get_db()
    cur = connection.execute(
        "SELECT MAX(postid) FROM posts"
    )
    id_recent = cur.fetchall()
    return id_recent[0]['MAX(postid)']


def get_posts(username, size, page, postid_lte):
    """Return dictionary of posts and their URLs.

    Return as a JSON dictionary with status code 200 OK
    """
    offset = size * page
    connection = get_db()
    cur = connection.execute(
        "SELECT posts.postid "
        "FROM posts WHERE (posts.owner = '" + username + "' "
        "OR posts.owner IN ("
        "SELECT following.username2 FROM following "
        "WHERE following.username1 = '" + username + "' )) "
        "AND posts.postid <= " + str(postid_lte) + " "
        "ORDER BY posts.postid DESC "
        "LIMIT " + str(size) + " OFFSET " + str(offset) + " "
        )
    queried_posts = cur.fetchall()
    for queried_post in queried_posts:
        queried_post['url'] = "/api/v1/posts/" + \
            str(queried_post['postid']) + "/"
    json_dict = {
        'next': "",
        'results': queried_posts,
        'url': ""
    }
    return json_dict


def get_post(postid, logname):
    """Get post information for post <postid>."""
    connection = get_db()
    cur = connection.execute(
        "SELECT posts.postid, posts.filename, posts.owner, "
        "posts.created "
        "FROM posts WHERE posts.postid = " + str(postid) + " ")
    post = cur.fetchall()
    post = post[0]
    post['imgUrl'] = f"/uploads/{post['filename']}"
    post['url'] = f"/api/v1/posts/{postid}/"
    post['postShowUrl'] = f"/posts/{postid}/"
    post['ownerShowUrl'] = f"/users/{post['owner']}/"

    cur = connection.execute(
        "SELECT users.filename FROM users "
        "WHERE users.username = '" + post['owner'] + "'")
    pfp = cur.fetchall()
    pfp = pfp[0]['filename']
    post['ownerImgUrl'] = f"/uploads/{pfp}"

    cur = connection.execute(
        "SELECT comments.commentid, comments.owner, comments.text "
        "FROM comments WHERE comments.postid = " + str(postid) + " "
        "ORDER BY comments.commentid ASC")
    comments = cur.fetchall()
    for comment in comments:
        comment['lognameOwnsThis'] = comment['owner'] == logname
        comment['ownerShowUrl'] = f"/users/{comment['owner']}/"
        comment['url'] = f"/api/v1/comments/{comment['commentid']}/"
    post['comments'] = comments
    post['comments_url'] = f"/api/v1/comments/?postid={postid}"

    cur = connection.execute(
        "SELECT COUNT(likes.likeid) FROM likes "
        "WHERE likes.postid = " + str(postid) + "")
    count = cur.fetchall()
    count = count[0]['COUNT(likes.likeid)']
    likes = {'numLikes': count}
    cur = connection.execute(
        "SELECT likes.likeid FROM likes "
        "WHERE likes.postid = " + str(postid) + " "
        "AND likes.owner = '" + logname + "'")
    mylike = cur.fetchall()
    if len(mylike) == 0:
        likes['lognameLikesThis'] = False
        likes['url'] = None
    else:
        mylike = mylike[0]
        likes['lognameLikesThis'] = True
        likes['url'] = f"/api/v1/likes/{mylike['likeid']}/"
    post['likes'] = likes
    post.pop('filename')
    return post


def get_like(logname, postid):
    """Get the like information for post <postid>."""
    connection = get_db()
    cur = connection.execute(
        "SELECT likeid FROM likes "
        "WHERE likes.owner = '" + logname + "' "
        "AND likes.postid = " + str(postid) + ""
    )
    likeid = cur.fetchall()
    if len(likeid) == 0:
        cur = connection.execute(
            "INSERT INTO likes(owner, postid) "
            "VALUES ('" + logname + "', " + str(postid) + ")"
        )
        cur = connection.execute(
            "SELECT likeid FROM likes "
            "WHERE likes.owner = '" + logname + "' "
            "AND likes.postid = " + str(postid) + ""
        )
        likeid = cur.fetchall()
        likeid = likeid[0]['likeid']
        return (likeid, 201)
    likeid = likeid[0]['likeid']
    return (likeid, 200)


def delete_like(logname, likeid):
    """Delete like <likeid>."""
    connection = get_db()
    cur = connection.execute(
        "SELECT owner FROM likes "
        "WHERE likeid = " + str(likeid) + " "
    )
    like = cur.fetchall()
    if len(like) == 0:
        return 404
    if like[0]['owner'] != logname:
        return 403
    cur = connection.execute(
        "DELETE FROM likes WHERE likeid = " + likeid + " "
    )
    return 204


def post_comment(logname, postid, text):
    """Post comment  <text> on post <postid>."""
    connection = get_db()
    cur = connection.execute(
        "INSERT INTO comments(owner, postid, text) "
        "VALUES ('" + logname + "', " + str(postid) + ", '" + text + "')"
    )
    cur = connection.execute("SELECT last_insert_rowid()")
    commentid = cur.fetchall()
    commentid = commentid[0]['last_insert_rowid()']
    json_file = {
        'commentid': commentid,
        'logNameOwnsThis': True,
        'owner': logname,
        'ownerShowUrl': f"/users/{logname}/",
        'text': text,
        'url': f"/api/v1/comments/{commentid}/"
    }
    return json_file


@insta485.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()


def delete_comment(logname, commentid):
    """Delete comment <commentid>."""
    connection = get_db()
    cur = connection.execute(
        "SELECT owner FROM comments "
        "WHERE commentid = " + str(commentid) + " "
    )
    comment = cur.fetchall()
    if len(comment) == 0:
        return 404
    if comment[0]['owner'] != logname:
        return 403
    cur = connection.execute(
        "DELETE FROM comments WHERE commentid = " + commentid + " "
    )
    return 204
