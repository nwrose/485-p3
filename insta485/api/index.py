"""REST API for index."""
import flask
import insta485
import insta485.model as model
import hashlib

@insta485.app.route('/api/v1/', methods=["GET"])
def show_api(): 
    """Returns some possible uses for the api.

    RETURNS as a JSON List.
    RETURNS with status code 200.
    """
    api_info = {"comments": "/api/v1/comments/", "likes": "/api/v1/likes/",
                 "posts": "/api/v1/posts/", "url": "/api/v1/"}
    return flask.jsonify(api_info), 200


@insta485.app.route('/api/v1/posts/', methods = ["GET"])
def show_post_feed_api():
    """Returns requested postURLs and postids as specified by querystring.
    """
    logname = ""
    if 'username' not in flask.session:
        if not flask.request.authorization:
            return flask.abort(403)
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        help_auth(logname, password)
    else:
        logname = flask.session['username']
    recentID = model.get_recent_postid()

    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    postid_lte = flask.request.args.get(
        "postid_lte", default=recentID, type=int)
    
    json_file = model.get_posts(logname, size, page, postid_lte)
    json_file['next'] = ""
    if len(json_file['results']) == size:
        nextPage = page + 1
        json_file['next'] = f"/api/v1/posts/?size={size}&page={nextPage}&postid_lte={postid_lte}"
    json_file['url'] = str(flask.request.url)
    return flask.jsonify(json_file), 200


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods = ["GET"])
def show_post_api(postid_url_slug):
    """Return the details for one post. 
    """
    logname = ""
    if 'username' not in flask.session:
        if not flask.request.authorization:
            return flask.abort(403)
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        help_auth(logname, password)
    else:
        logname = flask.session['username']
    recentID = model.get_recent_postid()
    if postid_url_slug > recentID:
        return flask.abort(404)
    json_file = model.get_post(postid_url_slug, logname)
    return flask.jsonify(json_file), 200


@insta485.app.route('/api/v1/likes/', methods = ['POST'])
def post_like_api():
    """Create like for a post and current user --> returns 201

    if post is already liked by user --> return like JSON object and 200
    """
    logname = ""
    if 'username' not in flask.session:
        if not flask.request.authorization:
            return flask.abort(403)
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        help_auth(logname, password)
    else:
        logname = flask.session['username']
    recentID = model.get_recent_postid()
    postid = flask.request.args['postid']
    if int(postid) > recentID:
        return flask.abort(404)
    likeid_and_code = model.get_like(logname, postid)
    json_file = {
        'likeid': likeid_and_code[0],
        'url': f"/api/v1/likes/{likeid_and_code[0]}/"
    }
    return flask.jsonify(json_file), likeid_and_code[1]


@insta485.app.route('/api/v1/likes/<likeid>/', methods = ['DELETE'])
def delete_like_api(likeid):
    logname = ""
    if 'username' not in flask.session:
        if not flask.request.authorization:
            return flask.abort(403)
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        help_auth(logname, password)
    else:
        logname = flask.session['username']
    code = model.delete_like(logname, likeid)
    if code == 404 or code == 403:
        return flask.abort(code)
    return flask.jsonify(), code


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def post_comment_api():
    logname = ""
    if 'username' not in flask.session:
        if not flask.request.authorization:
            return flask.abort(403)
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        help_auth(logname, password)
    else:
        logname = flask.session['username']
    recentID = model.get_recent_postid()
    postid = flask.request.args['postid']
    if int(postid) > recentID:
        return flask.abort(404)
    text = flask.request.json.get('text', None)
    json_file = model.post_comment(logname, postid, text)
    return flask.jsonify(json_file), 201


@insta485.app.route('/api/v1/comments/<commentid>/', methods = ['DELETE'])
def delete_comment_api(commentid):
    logname = ""
    if 'username' not in flask.session:
        if not flask.request.authorization:
            return flask.abort(403)
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        help_auth(logname, password)
    else:
        logname = flask.session['username']
    code = model.delete_comment(logname, commentid)
    if code == 404 or code == 403:
        return flask.abort(code)
    return flask.jsonify(), code









################################
####### HELPER FUNCTIONS #######
################################

def help_auth(username, password):
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
