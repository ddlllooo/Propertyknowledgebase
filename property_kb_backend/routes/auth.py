import base64
import io
import random
import re
import time
from datetime import timedelta

from captcha.image import ImageCaptcha
from flask import Blueprint, current_app, request, session
from flask_jwt_extended import create_access_token, jwt_required
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from extensions.limiter import limiter
from extensions.db import db
from models.password_reset_request import PasswordResetRequest
from models.user import User
from utils.auth import get_current_user, login_required_user
from utils.response import fail, success


auth_bp = Blueprint("auth", __name__)


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
EMAIL_MAX_LENGTH = 100
PASSWORD_MAX_LENGTH = 50


def is_valid_password(password):
    has_letter = re.search(r"[A-Za-z]", password)
    has_number = re.search(r"\d", password)
    return bool(has_letter and has_number)


@auth_bp.get("/captcha")
def get_captcha():
    image = ImageCaptcha(width=160, height=60)
    code = str(random.randint(1000, 9999))
    session["captcha_code"] = code
    session["captcha_expire"] = time.time() + 300
    buf = io.BytesIO()
    image.write(code, buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return success({"image": f"data:image/png;base64,{b64}"})


@auth_bp.post("/register")
@limiter.limit("5/minute")
def register():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""
    confirm_password = payload.get("confirmPassword") or ""
    captcha_code = (payload.get("captchaCode") or "").strip()

    if not captcha_code:
        return fail("请输入验证码")
    expected = session.pop("captcha_code", None)
    expire = session.pop("captcha_expire", None)
    if not expected or not expire:
        return fail("验证码已失效，请重新获取")
    if time.time() > expire:
        return fail("验证码已过期，请重新获取")
    if captcha_code != expected:
        return fail("验证码错误")

    if not name:
        return fail("姓名不能为空")
    if len(name) > 50:
        return fail("姓名长度不能超过 50 个字符")
    if not email:
        return fail("邮箱不能为空")
    if len(email) > EMAIL_MAX_LENGTH:
        return fail(f"邮箱长度不能超过 {EMAIL_MAX_LENGTH} 个字符")
    if not EMAIL_PATTERN.match(email):
        return fail("邮箱格式不正确")
    if User.query.filter(User.username == name).first():
        return fail("该姓名已被注册")
    if User.query.filter(User.email == email).first():
        return fail("邮箱已注册")
    if not password:
        return fail("密码不能为空")
    if len(password) < 6:
        return fail("密码长度不能少于 6 位")
    if len(password) > PASSWORD_MAX_LENGTH:
        return fail(f"密码长度不能超过 {PASSWORD_MAX_LENGTH} 个字符")
    if not is_valid_password(password):
        return fail("密码必须同时包含字母和数字")
    if confirm_password != password:
        return fail("两次输入的密码不一致")

    nickname = email.split("@", 1)[0]
    user = User(
        username=name,
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
@limiter.limit("10/minute")
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

    remember_me = (request.json or {}).get("rememberMe", False)
    if remember_me:
        expires = current_app.config.get(
            "JWT_REMEMBER_ME_TOKEN_EXPIRES", timedelta(days=30)
        )
    else:
        expires = current_app.config.get(
            "JWT_ACCESS_TOKEN_EXPIRES", timedelta(hours=12)
        )
    token = create_access_token(identity=str(user.id), expires_delta=expires)

    return success(
        {
            "token": token,
            "role": user.role,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "mustChangePassword": user.must_change_password,
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


@auth_bp.post("/password-reset/request")
def request_password_reset():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()

    if not username:
        return fail("用户名或邮箱不能为空")

    user = User.query.filter(
        or_(User.username == username, User.email == username)
    ).first()
    if not user:
        return fail("用户不存在")

    existing = PasswordResetRequest.query.filter_by(
        user_id=user.id, status="待处理"
    ).first()
    if existing:
        return fail("已存在待处理的密码重置请求，请等待管理员处理")

    req = PasswordResetRequest(
        user_id=user.id,
        username=user.username,
        email=user.email,
        status="待处理",
    )
    db.session.add(req)
    db.session.commit()

    return success(None, "密码重置请求已提交，请等待管理员处理")


@auth_bp.get("/password-reset/status")
def password_reset_status():
    username = (request.args.get("username") or "").strip()

    if not username:
        return fail("用户名或邮箱不能为空")

    user = User.query.filter(
        or_(User.username == username, User.email == username)
    ).first()
    if not user:
        return fail("用户不存在")

    processed = PasswordResetRequest.query.filter_by(
        user_id=user.id, status="已处理"
    ).filter(
        PasswordResetRequest.temp_password_plain.isnot(None)
    ).order_by(
        PasswordResetRequest.handled_at.desc()
    ).first()

    if processed:
        return success(
            {"status": "已处理", "tempPassword": processed.temp_password_plain},
            "查询成功",
        )

    pending = PasswordResetRequest.query.filter_by(
        user_id=user.id, status="待处理"
    ).first()
    if pending:
        return success({"status": "待处理"}, "查询成功")

    return success({"status": "无请求"}, "查询成功")


@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    user = get_current_user()
    if not user or user.status != "启用":
        return fail("请先登录", 401)

    payload = request.get_json(silent=True) or {}
    new_password = payload.get("newPassword") or ""

    if not new_password:
        return fail("新密码不能为空")
    if len(new_password) < 6:
        return fail("密码长度不能少于 6 位")
    if not is_valid_password(new_password):
        return fail("密码必须同时包含字母和数字")

    user.password_hash = generate_password_hash(new_password)
    user.must_change_password = False

    PasswordResetRequest.query.filter_by(
        user_id=user.id, status="已处理"
    ).filter(
        PasswordResetRequest.temp_password_plain.isnot(None)
    ).update({"temp_password_plain": None})

    db.session.commit()
    return success(None, "密码修改成功")
