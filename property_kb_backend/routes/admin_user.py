from flask import Blueprint, request
from sqlalchemy import or_
from werkzeug.security import generate_password_hash

from extensions.db import db
from models.user import User
from utils.auth import admin_required
from utils.response import fail, success


admin_user_bp = Blueprint("admin_user", __name__)


def get_positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


VALID_ROLES = {"user", "admin"}
VALID_STATUSES = {"启用", "停用"}


@admin_user_bp.get("/list")
@admin_required
def list_users():
    keyword = (request.args.get("keyword") or "").strip()
    role = (request.args.get("role") or "").strip()
    status = (request.args.get("status") or "").strip()
    page = get_positive_int(request.args.get("page"), 1)
    page_size = get_positive_int(request.args.get("pageSize"), 20)

    query = User.query

    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                User.username.like(pattern),
                User.nickname.like(pattern),
                User.email.like(pattern),
            )
        )

    if role:
        query = query.filter(User.role == role)

    if status:
        query = query.filter(User.status == status)

    total = query.count()
    records = (
        query.order_by(User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return success(
        {
            "list": [item.to_dict() for item in records],
            "total": total,
        },
        "查询成功",
    )


@admin_user_bp.post("/create")
@admin_required
def create_user():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    email = (payload.get("email") or "").strip()
    password = (payload.get("password") or "").strip()
    nickname = (payload.get("nickname") or "").strip() or username
    role = (payload.get("role") or "user").strip()

    if not username:
        return fail("用户名不能为空")
    if not email:
        return fail("邮箱不能为空")
    if not password or len(password) < 6:
        return fail("密码不能少于6位")
    if role not in VALID_ROLES:
        return fail("角色无效")

    if User.query.filter_by(username=username).first():
        return fail("用户名已存在")
    if User.query.filter_by(email=email).first():
        return fail("邮箱已被使用")

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        nickname=nickname,
        role=role,
        status="启用",
        must_change_password=bool(payload.get("mustChangePassword")),
    )
    db.session.add(user)
    db.session.commit()

    return success(user.to_dict(), "创建成功")


@admin_user_bp.put("/update/<int:user_id>")
@admin_required
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return fail("用户不存在", 404)

    payload = request.get_json(silent=True) or {}

    if "nickname" in payload:
        user.nickname = (payload.get("nickname") or "").strip() or user.nickname

    if "email" in payload:
        email = (payload.get("email") or "").strip()
        if not email:
            return fail("邮箱不能为空")
        existing = User.query.filter(User.email == email, User.id != user_id).first()
        if existing:
            return fail("邮箱已被使用")
        user.email = email

    if "role" in payload:
        role = (payload.get("role") or "").strip()
        if role not in VALID_ROLES:
            return fail("角色无效")
        user.role = role

    if "status" in payload:
        status = (payload.get("status") or "").strip()
        if status not in VALID_STATUSES:
            return fail("状态无效")
        user.status = status

    if "password" in payload:
        password = (payload.get("password") or "").strip()
        if password and len(password) < 6:
            return fail("密码不能少于6位")
        if password:
            user.password_hash = generate_password_hash(password)
            user.must_change_password = bool(payload.get("mustChangePassword", False))

    db.session.commit()
    return success(user.to_dict(), "修改成功")


@admin_user_bp.delete("/delete/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return fail("用户不存在", 404)

    db.session.delete(user)
    db.session.commit()
    return success(message="删除成功")


@admin_user_bp.put("/batch-status")
@admin_required
def batch_update_status():
    payload = request.get_json(silent=True) or {}
    ids = payload.get("ids")
    status = (payload.get("status") or "").strip()

    if not isinstance(ids, list) or not ids:
        return fail("请提供用户ID列表")
    if status not in VALID_STATUSES:
        return fail("状态无效")

    count = User.query.filter(User.id.in_(ids)).update(
        {User.status: status}, synchronize_session=False
    )
    db.session.commit()
    return success({"updatedCount": count}, f"已更新 {count} 个用户状态")
