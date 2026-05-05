from flask import Blueprint

from services.dashboard_service import (
    get_category_ratio,
    get_daily_trend,
    get_feedback_status,
    get_hit_rate_trend,
    get_hot_questions,
    get_overview,
    get_unmatched_questions,
)
from utils.auth import admin_required
from utils.response import success


admin_dashboard_bp = Blueprint("admin_dashboard", __name__)


@admin_dashboard_bp.get("/overview")
@admin_required
def overview():
    return success(get_overview(), "查询成功")


@admin_dashboard_bp.get("/daily-trend")
@admin_required
def daily_trend():
    return success(get_daily_trend(), "查询成功")


@admin_dashboard_bp.get("/hot-questions")
@admin_required
def hot_questions():
    return success(get_hot_questions(), "查询成功")


@admin_dashboard_bp.get("/hit-rate-trend")
@admin_required
def hit_rate_trend():
    return success(get_hit_rate_trend(), "查询成功")


@admin_dashboard_bp.get("/category-ratio")
@admin_required
def category_ratio():
    return success(get_category_ratio(), "查询成功")


@admin_dashboard_bp.get("/feedback-status")
@admin_required
def feedback_status():
    return success(get_feedback_status(), "查询成功")


@admin_dashboard_bp.get("/unmatched")
@admin_required
def unmatched():
    return success(get_unmatched_questions(), "查询成功")
