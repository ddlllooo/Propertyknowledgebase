from flask import Blueprint, request

from extensions.db import db
from models.category import Category
from models.qa import QaKnowledge
from utils.auth import admin_required
from utils.response import fail, success


admin_category_bp = Blueprint("admin_category", __name__)


def get_sort_order(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def refresh_question_count(category):
    category.question_count = QaKnowledge.query.filter(
        QaKnowledge.category == category.name,
        QaKnowledge.status != "已停用",
    ).count()


@admin_category_bp.get("/list")
@admin_required
def list_categories():
    records = Category.query.order_by(Category.sort_order.asc(), Category.id.asc()).all()
    return success([item.to_dict() for item in records], "查询成功")


@admin_category_bp.post("/create")
@admin_required
def create_category():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    description = (payload.get("description") or "").strip()
    sort_order = get_sort_order(payload.get("sortOrder"))
    status = (payload.get("status") or "启用").strip()

    if not name:
        return fail("分类名称不能为空")
    if Category.query.filter_by(name=name).first():
        return fail("分类名称已存在")

    category = Category(
        name=name,
        description=description,
        sort_order=sort_order,
        status=status,
    )
    db.session.add(category)
    db.session.commit()

    return success(category.to_dict(), "新增成功")


@admin_category_bp.put("/update/<int:category_id>")
@admin_required
def update_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return fail("分类不存在", 404)

    payload = request.get_json(silent=True) or {}

    if "name" in payload:
        name = (payload.get("name") or "").strip()
        if not name:
            return fail("分类名称不能为空")

        exists = Category.query.filter(
            Category.name == name,
            Category.id != category_id,
        ).first()
        if exists:
            return fail("分类名称已存在")

        category.name = name

    if "description" in payload:
        category.description = (payload.get("description") or "").strip()

    if "sortOrder" in payload:
        category.sort_order = get_sort_order(payload.get("sortOrder"))

    if "status" in payload:
        category.status = (payload.get("status") or "").strip()

    refresh_question_count(category)
    db.session.commit()

    return success(category.to_dict(), "修改成功")


@admin_category_bp.delete("/delete/<int:category_id>")
@admin_required
def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return fail("分类不存在", 404)

    category.status = "停用"
    db.session.commit()

    return success(category.to_dict(), "删除成功")
