import re

from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from extensions.db import db
from models.user import User
from utils.auth import get_current_user, login_required_user
from utils.response import fail, success


auth_bp = Blueprint("auth", __name__)


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_password(password):
    has_letter = re.search(r"[A-Za-z]", password)
    has_number = re.search(r"\d", password)
    return bool(has_letter and has_number)


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""
    confirm_password = payload.get("confirmPassword") or ""

    if not email:
        return fail("邮箱不能为空")
    if not EMAIL_PATTERN.match(email):
        return fail("邮箱格式不正确")
    if User.query.filter(or_(User.email == email, User.username == email)).first():
        return fail("邮箱已注册")
    if not password:
        return fail("密码不能为空")
    if len(password) < 6:
        return fail("密码长度不能少于 6 位")
    if not is_valid_password(password):
        return fail("密码必须同时包含字母和数字")
    if confirm_password != password:
        return fail("两次输入的密码不一致")

    nickname = email.split("@", 1)[0]
    user = User(
        username=email,
        email=email,
        password_hash=generate_password_hash(password),
        role="user",
        nickname=nickname,
        status="启用",
    )
    db.session.add(user)
    db.session.commit()

    return success(
        {
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "nickname": user.nickname,
        },
        "注册成功",
    )


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username:
        return fail("用户名或邮箱不能为空")
    if not password:
        return fail("密码不能为空")

    user = User.query.filter(
        or_(User.username == username, User.email == username)
    ).first()
    if not user:
        return fail("用户不存在", 401)
    if not check_password_hash(user.password_hash, password):
        return fail("账号或密码错误", 401)
    if user.status != "启用":
        return fail("用户已停用", 403)

    token = create_access_token(identity=str(user.id))

    return success(
        {
            "token": token,
            "role": user.role,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
        },
        "登录成功",
    )


@auth_bp.get("/profile")
@login_required_user
def profile():
    user = get_current_user()
    return success(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "nickname": user.nickname,
        },
        "查询成功",
    )
