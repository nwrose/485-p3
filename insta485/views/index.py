"""
Insta485 index (main) view.

URLs include:
/
"""


import pathlib
import uuid
import os
import hashlib
import flask
import arrow
import insta485

insta485.app.secret_key = b'\xabm\x80\xc4BaL\xabr\x19\xf3w\xf2:.\xbc\xafd\
    \x92\\n\x8f\x98\xca\xa1'


@insta485.app.route('/uploads/<path:filename>')
def serve_image(filename):
    """Docstring."""
    if 'username' not in flask.session:
        flask.abort(403)
    obj = insta485.app.config['UPLOAD_FOLDER']
    check_file = pathlib.Path(obj, filename)
    if not check_file.exists:
        return flask.abort(404)
    return flask.send_from_directory(obj, filename, as_attachment=True)


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT posts.postid, posts.filename, posts.owner, posts.created "
        "FROM posts WHERE posts.owner = '" + logname + "' "
        "OR posts.owner IN ("
        "SELECT following.username2 FROM following "
        "WHERE following.username1 = '" + logname + "' ) "
        "ORDER BY posts.postid DESC")
    posts = cur.fetchall()
    for post in posts:
        val = arrow.get(post['created'], 'YYYY-MM-DD HH:mm:ss').humanize()
        post['created'] = val
        q_s = (
            "SELECT COUNT(likes.likeid) FROM likes "
            "WHERE likes.postid = '" + str(post['postid']) + "'")
        cur = connection.execute(q_s)
        count = cur.fetchall()
        count = count[0]['COUNT(likes.likeid)']
        post['likes'] = count
        comcur = connection.execute(
            "SELECT comments.owner, comments.text FROM comments "
            "WHERE comments.postid = '" + str(post['postid']) + "' "
            "ORDER BY comments.commentid ASC")
        comments = comcur.fetchall()
        post['comments'] = comments
        cur = connection.execute(
            "SELECT users.filename FROM users WHERE "
            "users.username = '" + post['owner'] + "'")
        pfp = cur.fetchall()
        pfp = pfp[0]['filename']
        post['pfp'] = pfp
        cur = connection.execute(
            "SELECT COUNT(likes.likeid) FROM likes "
            "WHERE likes.postid = '" + str(post['postid']) + "' "
            "AND likes.owner = '" + logname + "'")
        is_liked = cur.fetchall()
        is_liked = is_liked[0]['COUNT(likes.likeid)']
        post['is_liked'] = is_liked
    context = {"posts": posts, "logname": logname}
    return flask.render_template("index.html", **context)


@insta485.app.route('/accounts/auth/')
def auth_user():
    """Docstring."""
    if 'username' not in flask.session:
        return flask.abort(403)
    resp = flask.jsonify(success=True)
    return resp


@insta485.app.route('/explore/')
def show_explore():
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    connection = insta485.model.get_db()
    nf_query = (
        "SELECT users.username, users.filename FROM users "
        "WHERE users.username !='" + logname + "' "
        "AND users.username NOT IN (SELECT following.username2 "
        "FROM following WHERE following.username1 = '" + logname + "' )")
    nf_cur = connection.execute(nf_query)
    not_following = nf_cur.fetchall()
    context = {"logname": logname, "not_following": not_following}
    return flask.render_template("explore.html", **context)


@insta485.app.route('/users/<user>/followers/')
def show_followers(user):
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    connection = insta485.model.get_db()
    check_query = (
        "SELECT COUNT(1) FROM users "
        "WHERE username='" + user + "'")
    cur = connection.execute(check_query)
    res = cur.fetchall()
    if res[0]['COUNT(1)'] == 0:
        flask.abort(404)
    usr = user
    logname = flask.session['username']
    followers_query = (
        "SELECT users.username, users.filename FROM users "
        "WHERE users.username IN (SELECT following.username1 "
        "FROM following WHERE following.username2 = '" + user + "' )")
    followers_cur = connection.execute(followers_query)
    followers = followers_cur.fetchall()
    for follower in followers:
        is_following_query = (
            "SELECT COUNT(following.username1) "
            "FROM following WHERE following.username2="
            "'" + follower['username'] + "' "
            "AND following.username1 = '" + logname + "'")
        is_following_cur = connection.execute(is_following_query)
        is_following = is_following_cur.fetchall()
        is_following = is_following[0]['COUNT(following.username1)']
        follower['is_following'] = is_following
    context = {"logname": logname, "followers": followers, "usr": usr}
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<user>/following/')
def show_following(user):
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    connection = insta485.model.get_db()
    c_q = "SELECT COUNT(1) FROM users WHERE username='" + user + "'"
    cur = connection.execute(c_q)
    res = cur.fetchall()
    if res[0]['COUNT(1)'] == 0:
        flask.abort(404)
    logname = flask.session['username']
    usr = user
    following_query = (
        "SELECT users.username, users.filename FROM users "
        "WHERE users.username IN (SELECT following.username2 "
        "FROM following WHERE following.username1='" + user + "')")
    following_cur = connection.execute(following_query)
    followees = following_cur.fetchall()
    for followee in followees:
        is_following_query = (
            "SELECT COUNT(following.username1) "
            "FROM following "
            "WHERE following.username2 = '" + followee['username'] + "' "
            "AND following.username1 = '" + logname + "'")
        is_following_cur = connection.execute(is_following_query)
        is_following = is_following_cur.fetchall()
        is_following = is_following[0]['COUNT(following.username1)']
        followee['is_following'] = is_following
    context = {"logname": logname, "followees": followees, "usr": usr}
    return flask.render_template("following.html", **context)


@insta485.app.route('/users/<user>/')
def show_user(user):
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT COUNT(1) FROM users WHERE username='" + user + "'")
    res = cur.fetchall()

    if res[0]['COUNT(1)'] == 0:
        flask.abort(404)
    logname = flask.session['username']
    cur = connection.execute(
        "SELECT users.username, users.fullname, users.filename "
        "FROM users WHERE users.username = '" + user + "'")
    page_owner = cur.fetchall()
    page_owner = page_owner[0]
    cur = connection.execute(
        "SELECT COUNT(posts.postid) FROM posts "
        "WHERE posts.owner = '" + page_owner['username'] + "'")
    num_posts = cur.fetchall()
    num_posts = num_posts[0]['COUNT(posts.postid)']
    page_owner['num_posts'] = num_posts
    cur = connection.execute(
        "SELECT posts.postid, posts.filename FROM posts "
        "WHERE posts.owner = '" + page_owner['username'] + "' "
        "ORDER BY posts.postid ASC")
    posts = cur.fetchall()
    page_owner['posts'] = posts
    cur = connection.execute(
        "SELECT COUNT(following.username1) "
        "FROM following "
        "WHERE following.username2='"+page_owner['username']+"'")
    num_followers = cur.fetchall()
    num_followers = num_followers[0]['COUNT(following.username1)']
    page_owner['num_followers'] = num_followers
    cur = connection.execute(
        "SELECT COUNT(following.username2) "
        "FROM following "
        "WHERE following.username1 = '" + page_owner['username'] + "'")
    num_following = cur.fetchall()
    num_following = num_following[0]['COUNT(following.username2)']
    page_owner['num_following'] = num_following
    cur = connection.execute(
        "SELECT COUNT(following.username2) "
        "FROM following WHERE following.username1 = '" + logname + "' "
        "AND following.username2 = '" + page_owner['username'] + "'")
    is_following = cur.fetchall()
    is_following = is_following[0]['COUNT(following.username2)']
    page_owner['is_following'] = is_following
    context = {"logname": logname, "page_owner": page_owner}
    return flask.render_template("users.html", **context)


@insta485.app.route('/posts/<postid>/')
def show_post(postid):
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    connection = insta485.model.get_db()
    postscur = connection.execute(
        "SELECT posts.postid, posts.filename, posts.owner, "
        "posts.created "
        "FROM posts WHERE posts.postid = '" + postid + "' ")
    post = postscur.fetchall()
    post = post[0]
    likecur = connection.execute(
        "SELECT COUNT(likes.likeid) FROM likes "
        "WHERE likes.postid = '" + str(postid) + "'")
    count = likecur.fetchall()
    count = count[0]['COUNT(likes.likeid)']
    post['likes'] = count
    comcur = connection.execute(
        "SELECT comments.commentid, comments.owner, comments.text "
        "FROM comments WHERE comments.postid = '" + str(postid) + "' "
        "ORDER BY comments.commentid ASC")
    comments = comcur.fetchall()
    post['comments'] = comments
    pfpcur = connection.execute(
        "SELECT users.filename FROM users "
        "WHERE users.username = '" + post['owner'] + "'")
    pfp = pfpcur.fetchall()
    pfp = pfp[0]['filename']
    post['pfp'] = pfp
    is_liked_query = (
        "SELECT COUNT(likes.likeid) FROM likes "
        "WHERE likes.postid = '" + str(post['postid']) + "' "
        "AND likes.owner = '" + logname + "'")
    is_liked_cur = connection.execute(is_liked_query)
    is_liked = is_liked_cur.fetchall()
    is_liked = is_liked[0]['COUNT(likes.likeid)']
    post['is_liked'] = is_liked
    if post['is_liked'] > 1:
        post['is_liked'] = 1
    post['created'] = arrow.get(post['created'],
                                'YYYY-MM-DD HH:mm:ss').humanize()
    context = {"logname": logname, "post": post}
    return flask.render_template("posts.html", **context)


@insta485.app.route('/accounts/login/')
def show_login():
    """Docstring."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")


@insta485.app.route('/accounts/edit/')
def show_acc_edit():
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    connection = insta485.model.get_db()
    usrquery = (
        "SELECT users.filename, users.fullname, users.email "
        "FROM users WHERE users.username = '" + logname + "'")
    usrcur = connection.execute(usrquery)
    usr = usrcur.fetchall()
    usr = usr[0]
    context = {"logname": logname, "usr": usr}
    return flask.render_template("acc_edit.html", **context)


@insta485.app.route('/accounts/password/')
def show_password():
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('show_password.html', **context)


@insta485.app.route('/accounts/create/')
def show_create():
    """Docstring."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_acc_edit'))
    return flask.render_template('show_create.html')


@insta485.app.route('/accounts/delete/')
def show_delete():
    """Docstring."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('acc_delete.html', **context)


@insta485.app.route('/accounts/', methods=['POST'])
def account_ops():
    """Docstring."""
    if flask.request.form['operation'] == "login":
        help_login(
            flask.request.form['username'],
            flask.request.form['password'])
        target = flask.request.args.get('target')
    elif flask.request.form['operation'] == "create":
        help_create_account(
            flask.request.files["file"],
            flask.request.form['username'],
            flask.request.form['password'],
            flask.request.form['fullname'],
            flask.request.form['email'])
        target = flask.request.args.get('target')
    elif flask.request.form['operation'] == "delete":
        if 'username' not in flask.session:
            flask.abort(403)
        logname = flask.session['username']
        help_delete_account(logname)
        target = flask.request.args.get('target')
    elif flask.request.form['operation'] == "edit_account":
        if 'username' not in flask.session:
            flask.abort(403)
        help_edit_account(
            flask.request.files["file"],
            flask.request.form['fullname'],
            flask.request.form['email'],
            flask.session['username'])
        target = flask.request.args.get('target')
    elif flask.request.form['operation'] == "update_password":
        if 'username' not in flask.session:
            flask.abort(403)
        help_update_password(
            flask.request.form['password'],
            flask.request.form['new_password1'],
            flask.request.form['new_password2'],
            flask.session['username'])
        target = flask.request.args.get('target')
    if target == '' or target is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Docstring."""
    flask.session.clear()
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/likes/', methods=['POST'])
def like_ops():
    """Docstring."""
    logname = flask.session['username']
    postid = flask.request.form["postid"]
    operation = flask.request.form["operation"]
    connection = insta485.model.get_db()
    if operation == "unlike":
        check_query = (
            "SELECT COUNT(1) FROM likes "
            "WHERE owner = '" + logname + "' "
            "AND postid = '" + str(postid) + "'")
        cur = connection.execute(check_query)
        res = cur.fetchall()
        if res[0]['COUNT(1)'] == 0:
            flask.abort(409)
        like_sql = (
            "DELETE FROM likes "
            "WHERE likes.owner = '" + logname + "' "
            "AND likes.postid = '" + str(postid) + "'")
        connection.execute(like_sql)
    else:
        check_query = (
            "SELECT COUNT(1) FROM likes "
            "WHERE owner = '" + logname + "' "
            "AND postid = '" + str(postid) + "'")
        cur = connection.execute(check_query)
        res = cur.fetchall()
        if res[0]['COUNT(1)'] != 0:
            flask.abort(409)
        like_sql = (
            "INSERT INTO likes(owner, postid) "
            "VALUES ('" + logname + "'," + str(postid) + ")")
        connection.execute(like_sql)
    target = flask.request.args.get('target')
    if target == '' or target is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


@insta485.app.route('/comments/', methods={'POST'})
def comment_ops():
    """Docstring."""
    logname = flask.session['username']
    operation = flask.request.form["operation"]
    connection = insta485.model.get_db()
    if operation == "create":
        postid = flask.request.form["postid"]
        text = flask.request.form["text"]
        if text == "" or text is None:
            flask.abort(400)
        com_sql = (
            "INSERT INTO comments(owner, postid, text) "
            "VALUES ('" + logname + "', '" + str(postid) + "', "
            "'" + text + "')")
        connection.execute(com_sql)
    else:
        commentid = flask.request.form['commentid']
        check_sql = (
            "SELECT owner FROM comments "
            "WHERE commentid = '" + str(commentid) + "'")
        cur = connection.execute(check_sql)
        uname = cur.fetchall()
        if uname[0]['owner'] != logname:
            flask.abort(403)
        com_sql = (
            "DELETE FROM comments "
            "WHERE commentid = '" + str(commentid) + "'")
        connection.execute(com_sql)
    target = flask.request.args.get('target')
    if target == '' or target is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


@insta485.app.route('/following/', methods={'POST'})
def follow_ops():
    """Docstring."""
    logname = flask.session['username']
    operation = flask.request.form["operation"]
    connection = insta485.model.get_db()
    if operation == "unfollow":
        check_query = (
            "SELECT COUNT(1) FROM following "
            "WHERE username1 = '" + logname + "' "
            "AND username2 = '" + flask.request.form["username"] + "'")
        cur = connection.execute(check_query)
        res = cur.fetchall()
        if res[0]['COUNT(1)'] == 0:
            flask.abort(409)
        unfollow_sql = (
            "DELETE FROM following "
            "WHERE username1 = '" + logname + "' "
            "AND username2 = '" + flask.request.form["username"] + "'")
        connection.execute(unfollow_sql)
    else:
        check_query = (
            "SELECT COUNT(1) FROM following "
            "WHERE username1 = '" + logname + "' "
            "AND username2 = '" + flask.request.form["username"] + "'")
        cur = connection.execute(check_query)
        res = cur.fetchall()
        if res[0]['COUNT(1)'] != 0:
            flask.abort(409)
        follow_sql = (
            "INSERT INTO following(username1, username2) "
            "VALUES ('" + logname + "', "
            "'" + flask.request.form["username"] + "')")
        connection.execute(follow_sql)
    target = flask.request.args.get('target')
    if target == '' or target is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


@insta485.app.route('/posts/', methods={'POST'})
def post_ops():
    """Docstring."""
    logname = flask.session['username']
    connection = insta485.model.get_db()
    operation = flask.request.form["operation"]
    if operation == "delete":
        postid = flask.request.form["postid"]
        del_po_cur = connection.execute(
            "SELECT filename, owner FROM posts "
            "WHERE postid = '" + postid + "'")
        delete_filename = del_po_cur.fetchall()
        if delete_filename[0]['owner'] != logname:
            flask.abort(403)
        delete_filename = delete_filename[0]['filename']
        delete_path = insta485.app.config["UPLOAD_FOLDER"]/delete_filename
        os.remove(delete_path)
        connection.execute(
            "DELETE FROM posts WHERE postid = '" + postid + "'")
    else:
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        if filename == '' or filename is None:
            flask.abort(400)
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        new_post_sql = (
            "INSERT INTO posts(filename, owner) "
            "VALUES ('" + uuid_basename + "', '" + logname + "')")
        connection.execute(new_post_sql)
    target = flask.request.args.get('target')
    if target == '' or target is None:
        return flask.redirect(flask.url_for('show_user', user=logname))
    return flask.redirect(flask.request.args.get('target'))


def help_update_password(input_pass, new_pass_1, new_pass_2, logname):
    """Docstring."""
    is_white = input_pass == '' or new_pass_1 == '' or new_pass_2 == ''
    is_no = input_pass is None or new_pass_1 is None or new_pass_2 is None
    if is_white or is_no:
        flask.abort(400)
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password FROM users "
        "WHERE username = '" + logname + "'")
    db_password_string = cur.fetchall()
    db_password_string = db_password_string[0]['password']
    db_password_list = db_password_string.split('$')
    hash_obj = hashlib.new('sha512')
    password_salted = db_password_list[1] + input_pass
    hash_obj.update(password_salted.encode('utf-8'))
    if hash_obj.hexdigest() != db_password_list[2]:
        flask.abort(403)
    if new_pass_1 != new_pass_2:
        flask.abort(401)
    new_salt = uuid.uuid4().hex
    hash_obj = hashlib.new('sha512')
    password_salted = new_salt + new_pass_1
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join(['sha512', new_salt, password_hash])
    connection.execute(
        "UPDATE users "
        "SET password = '" + password_db_string + "' "
        "WHERE username = '" + logname + "'")


def help_edit_account(fileobj, fullname, email, logname):
    """Docstring."""
    filename = fileobj.filename
    file_exists = filename != ''
    is_white = fullname == '' or email == ''
    is_none = fullname is None or email is None
    if is_white or is_none:
        flask.abort(400)
    if file_exists:
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
    help_edit_account_2(fullname, email, logname, file_exists, uuid_basename)


def help_edit_account_2(fullname, email, logname, file_exists, uuid_basename):
    """Docstring."""
    connection = insta485.model.get_db()
    edit_sql = (
        "UPDATE users SET fullname = '" + fullname + "', "
        "email = '" + email + "' WHERE username = '" + logname + "'")
    if file_exists:
        edit_sql = (
            "UPDATE users SET fullname = '" + fullname + "', "
            "email = '" + email + "', filename = '" + uuid_basename + "' "
            "WHERE username = '" + logname + "'")
        old_name_sql = (
            "SELECT filename FROM users "
            "WHERE username = '" + logname + "'")
        cur = connection.execute(old_name_sql)
        delete_filename = cur.fetchall()
        delete_filename = delete_filename[0]['filename']
        delete_path = insta485.app.config["UPLOAD_FOLDER"]/delete_filename
        os.remove(delete_path)
    connection.execute(edit_sql)


def help_delete_account(logname):
    """Docstring."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT filename FROM posts "
        "WHERE owner = '" + logname + "'")
    del_posts = cur.fetchall()
    for del_post in del_posts:
        delete_filename = del_post['filename']
        delete_path = insta485.app.config["UPLOAD_FOLDER"]/delete_filename
        os.remove(delete_path)
    cur = connection.execute(
        "SELECT filename FROM users "
        "WHERE username = '" + logname + "'")
    delpfp = cur.fetchall()
    delete_filename = delpfp[0]['filename']
    delete_path = insta485.app.config["UPLOAD_FOLDER"]/delete_filename
    os.remove(delete_path)
    connection.execute(
        "DELETE FROM users WHERE username = '" + logname + "'")
    flask.session.clear()


def help_create_account(fileobj, username, password, fullname, email):
    """Docstring."""
    filename = fileobj.filename
    c_1 = username == '' or password == '' or fullname == ''
    c_2 = email == '' or filename == '' or username is None
    c_3 = password is None or fullname is None or email is None
    if c_1 or c_2 or c_3 or filename is None:
        flask.abort(400)
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT COUNT(1) FROM users WHERE username='"+username+"'")
    val = cur.fetchall()
    if val[0]['COUNT(1)'] != 0:
        flask.abort(409)
    help_create_account_2(fileobj, username, password, fullname, email)


def help_create_account_2(fileobj, username, password, fullname, email):
    """Docstring."""
    suffix = pathlib.Path(fileobj.filename).suffix.lower()
    uuid_basename = f"{uuid.uuid4().hex}{suffix}"
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    connection = insta485.model.get_db()
    connection.execute(
        "INSERT INTO users(username, fullname, "
        "email, filename, password) "
        "VALUES ('" + username + "','" + fullname + "','" + email + "', "
        "'" + uuid_basename + "','" + password_db_string + "')")
    flask.session['username'] = username


def help_login(username, password):
    """Docstring."""
    c_1 = username == '' or password == ''
    if c_1 or username is None or password is None:
        flask.abort(400)
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT COUNT(1) FROM users "
        "WHERE username = '" + username + "'")
    val = cur.fetchall()
    if val[0]['COUNT(1)'] == 0:
        flask.abort(403)
    cur = connection.execute(
        "SELECT password FROM users "
        "WHERE username = '" + username + "'")
    db_password_string = cur.fetchall()
    db_password_string = db_password_string[0]['password']
    db_password_list = db_password_string.split('$')
    db_password_hash = db_password_list[2]
    algorithm = 'sha512'
    salt = db_password_list[1]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    input_password_hash = hash_obj.hexdigest()
    if input_password_hash != db_password_hash:
        flask.abort(403)
    flask.session['username'] = username
