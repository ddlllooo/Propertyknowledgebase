from sqlalchemy import func

from extensions.db import db
from models.category import Category
from models.qa import QaKnowledge


AUTO_CATEGORY_DESCRIPTION = "由知识库问答自动生成的分类，可在分类管理中完善描述。"


def normalize_category_name(name):
    return (name or "").strip()


def count_category_questions(category_name):
    category_name = normalize_category_name(category_name)
    if not category_name:
        return 0

    return QaKnowledge.query.filter(
        QaKnowledge.category == category_name,
        QaKnowledge.status != "已停用",
    ).count()


def get_next_sort_order():
    max_sort_order = db.session.query(func.max(Category.sort_order)).scalar() or 0
    return int(max_sort_order) + 1


def ensure_category(category_name, description=""):
    category_name = normalize_category_name(category_name)
    if not category_name:
        return None

    description = (description or "").strip()
    category = Category.query.filter_by(name=category_name).first()

    if not category:
        category = Category(
            name=category_name,
            description=description or AUTO_CATEGORY_DESCRIPTION,
            question_count=0,
            sort_order=get_next_sort_order(),
            status="启用",
        )
        db.session.add(category)
    elif description and category.description != description:
        category.description = description

    category.question_count = count_category_questions(category_name)
    return category


def refresh_category_question_count(category_name):
    category = ensure_category(category_name)
    if category:
        category.question_count = count_category_questions(category.name)


def sync_categories_from_qa():
    records = (
        QaKnowledge.query.with_entities(QaKnowledge.category.label("name"))
        .filter(QaKnowledge.category != "")
        .group_by(QaKnowledge.category)
        .order_by(QaKnowledge.category.asc())
        .all()
    )

    for (category_name,) in records:
        ensure_category(category_name)

    for category in Category.query.all():
        category.question_count = count_category_questions(category.name)
