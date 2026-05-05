from functools import wraps

from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions.db import db
from models.user import User
from utils.response import fail


def get_current_user():
    user_id = get_jwt_identity()
    if not user_id:
        return None
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def login_required_user(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return fail("请先登录", 401)
        if user.status != "启用":
            return fail("用户已停用", 403)
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return fail("请先登录", 401)
        if user.status != "启用":
            return fail("用户已停用", 403)
        if user.role != "admin":
            return fail("需要管理员权限", 403)
        return fn(*args, **kwargs)

    return wrapper
