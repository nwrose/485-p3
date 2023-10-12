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
def show_posts_api():
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


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
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
