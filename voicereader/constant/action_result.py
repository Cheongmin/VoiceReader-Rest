def ok(res):
    return res, 200


def created(res):
    return res, 201


def no_content(res):
    return res, 204


def bad_request(res):
    return res, 400


def unauthorized(res):
    return res, 401


def not_found(res):
    return res, 404


def conflict(res):
    return res, 409


def internal_server_error(res):
    return res, 500
