import secrets
import string
from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash

from extensions.db import db
from models.password_reset_request import PasswordResetRequest
from models.user import User
from utils.auth import admin_required
from utils.response import fail, success


admin_password_reset_bp = Blueprint("admin_password_reset", __name__)


def _generate_temp_password(length=8):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@admin_password_reset_bp.get("/list")
@admin_required
def list_requests():
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("pageSize", 10)), 1), 200)
    status = request.args.get("status", "").strip()
    keyword = request.args.get("keyword", "").strip()

    query = PasswordResetRequest.query

    if status:
        query = query.filter(PasswordResetRequest.status == status)

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            db.or_(
                PasswordResetRequest.username.like(like),
                PasswordResetRequest.email.like(like),
            )
        )

    total = query.count()
    items = (
        query.order_by(PasswordResetRequest.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return success(
        {"list": [r.to_dict() for r in items], "total": total},
        "查询成功",
    )


@admin_password_reset_bp.post("/reset/<int:request_id>")
@admin_required
def reset_password(request_id):
    req = db.session.get(PasswordResetRequest, request_id)
    if not req:
        return fail("请求不存在", 404)
    if req.status != "待处理":
        return fail("该请求已被处理")

    user = db.session.get(User, req.user_id)
    if not user:
        return fail("用户不存在", 404)

    temp_plain = _generate_temp_password()
    user.password_hash = generate_password_hash(temp_plain)
    user.must_change_password = True

    req.status = "已处理"
    req.temp_password_plain = temp_plain
    req.handled_by = int(get_jwt_identity())
    req.handled_at = datetime.now()

    db.session.commit()

    return success({"tempPassword": temp_plain}, "密码重置成功")


@admin_password_reset_bp.put("/ignore/<int:request_id>")
@admin_required
def ignore_request(request_id):
    req = db.session.get(PasswordResetRequest, request_id)
    if not req:
        return fail("请求不存在", 404)
    if req.status != "待处理":
        return fail("该请求已被处理")

    req.status = "已忽略"
    req.handled_by = int(get_jwt_identity())
    req.handled_at = datetime.now()

    db.session.commit()
    return success(None, "已忽略")
