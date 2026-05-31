"""管理端 / 面向运营的中文字段展示：将内部枚举码转为可读文案。"""

from __future__ import annotations


def label_content_type(code: str | None) -> str:
    if not code:
        return "—"
    return {
        "external": "外链",
        "original": "原创",
    }.get(str(code).strip(), str(code))


def label_admin_action(action: str | None) -> str:
    if not action:
        return "—"
    a = str(action).strip()
    return _ADMIN_ACTION_LABELS.get(a, a)


def label_resource_type(rt: str | None) -> str:
    if not rt:
        return "—"
    k = str(rt).strip()
    return _RESOURCE_TYPE_LABELS.get(k, k)


_ADMIN_ACTION_LABELS: dict[str, str] = {
    "login": "登录",
    "password_change": "修改密码",
    "article_create": "创建文章",
    "article_update": "更新文章",
    "article_delete": "删除文章",
    "article_category_create": "创建文章分类",
    "article_category_update": "更新文章分类",
    "article_category_delete": "删除文章分类",
    "site_create": "创建网站",
    "site_update": "更新网站",
    "site_delete": "删除网站",
    "site_refetch": "重新抓取网站信息",
    "site_check": "校验网站",
    "site_check_batch": "批量校验网站",
    "site_category_create": "创建网址分类",
    "site_category_update": "更新网址分类",
    "site_category_delete": "删除网址分类",
    "settings_update": "更新平台设置",
    "settings_logo": "更新平台 Logo",
    "maintenance_cleanup_visit_stats": "清理访问统计",
    "maintenance_cleanup_admin_logs": "清理操作日志",
    "maintenance_cleanup_captcha": "清理验证码",
    "upload_prune": "清理未引用上传",
}


def admin_action_options() -> list[dict[str, str]]:
    """供后台操作日志筛选下拉使用。"""
    return [{"value": k, "label": v} for k, v in sorted(_ADMIN_ACTION_LABELS.items(), key=lambda x: x[1])]


_RESOURCE_TYPE_LABELS: dict[str, str] = {
    "site": "网站",
    "article": "文章",
    "article_category": "文章分类",
    "site_category": "网址分类",
    "platform": "平台设置",
    "system": "系统",
}
