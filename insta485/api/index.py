"""REST API for index."""
import hashlib
import flask
import insta485
from insta485 import model


@insta485.app.route('/api/v1/', methods=["GET"])
def show_api():
    """Return some possible uses for the api.

    RETURNS as a JSON List.
    RETURNS with status code 200.
    """
    api_info = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"}
    return flask.jsonify(api_info), 200


@insta485.app.route('/api/v1/posts/', methods=["GET"])
def show_post_feed_api():
    """Return requested postURLs and postids as specified by querystring."""
    logname = ""
    if 'username' not in flask.session:
        if not flask.request.authorization:
            return flask.abort(403)
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        help_auth(logname, password)
    else:
        logname = flask.session['username']
    recent_id = model.get_recent_postid()

    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    postid_lte = flask.request.args.get(
        "postid_lte", default=recent_id, type=int)
    if size < 1 or page < 0:
        bad_file = {
            "message": "Bad Request",
            "status_code": 400
        }
        return bad_file, 400
    json_file = model.get_posts(logname, size, page, postid_lte)
    json_file['next'] = ""
    if len(json_file['results']) == size:
        next_page = page + 1
        print(next_page)
        json_file['next'] = f"/api/v1/posts/?size={size}" \
            + f"&page={next_page}&postid_lte={postid_lte}"
    json_file['url'] = "/api/v1/posts/"
    if str(flask.request.query_string.decode()):
        json_file['url'] += "?" + str(flask.request.query_string.decode())
    return flask.jsonify(json_file), 200


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=["GET"])
def show_post_api(postid_url_slug):
    """Return the details for one post."""
    logname = ""
    if 'username' not in flask.session:
        if not flask.request.authorization:
            return flask.abort(403)
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        help_auth(logname, password)
    else:
        logname = flask.session['username']
    recent_id = model.get_recent_postid()
    if postid_url_slug > recent_id:
        return flask.abort(404)
    json_file = model.get_post(postid_url_slug, logname)
    return flask.jsonify(json_file), 200


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def post_like_api():
    """Create like for a post and current user --> return 201.

    If post is already liked by user --> return like JSON object and 200
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
    recent_id = model.get_recent_postid()
    postid = flask.request.args['postid']
    if int(postid) > recent_id:
        return flask.abort(404)
    likeid_and_code = model.get_like(logname, postid)
    json_file = {
        'likeid': likeid_and_code[0],
        'url': f"/api/v1/likes/{likeid_and_code[0]}/"
    }
    return flask.jsonify(json_file), likeid_and_code[1]


@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
def delete_like_api(likeid):
    """Delete like <likeid> API."""
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
    if code in (403, 404):
        return flask.abort(code)
    return flask.jsonify(), code


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def post_comment_api():
    """Post comment API."""
    logname = ""
    if 'username' not in flask.session:
        if not flask.request.authorization:
            return flask.abort(403)
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        help_auth(logname, password)
    else:
        logname = flask.session['username']
    recent_id = model.get_recent_postid()
    postid = flask.request.args['postid']
    if int(postid) > recent_id:
        return flask.abort(404)
    text = flask.request.json.get('text', None)
    json_file = model.post_comment(logname, postid, text)
    return flask.jsonify(json_file), 201


@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
def delete_comment_api(commentid):
    """Delete comment <commentid> API."""
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
    if code in (403, 404):
        print("my error code is: ", code)
        return flask.abort(code)
    return flask.jsonify(), code


#
# Helper functions
#
def help_auth(cur_user, password):
    """Help authenticating users."""
    expression = cur_user == '' or password == ''
    if expression or cur_user is None or password is None:
        flask.abort(400)
    cntn = insta485.model.get_db()
    cur = cntn.execute(
        "SELECT COUNT(1) FROM users "
        "WHERE username = '" + cur_user + "'")
    val = cur.fetchall()
    if val[0]['COUNT(1)'] == 0:
        flask.abort(403)
    cur = cntn.execute(
        "SELECT password FROM users "
        "WHERE username = '" + cur_user + "'")
    password_db = cur.fetchall()
    password_db = password_db[0]['password']
    password_list_db = password_db.split('$')
    db_password_hash = password_list_db[2]
    algorithm = 'sha512'
    salt = password_list_db[1]
    hash_obj = hashlib.new(algorithm)
    salted = salt + password
    hash_obj.update(salted.encode('utf-8'))
    password_attempt_hash = hash_obj.hexdigest()
    if password_attempt_hash != db_password_hash:
        flask.abort(403)
