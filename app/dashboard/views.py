from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg
from django.shortcuts import render

from accounts.models import EmployeeProfile, User
from analysis.services import build_opinion_summary
from conditions.models import Condition
from dashboard.models import SystemSetting


def _get_admin_timeout_minutes():
    setting = SystemSetting.objects.first()
    if setting and setting.admin_timeout_minutes:
        return setting.admin_timeout_minutes
    return 5


def _build_graph_data(rows):
    date_bucket = defaultdict(lambda: {"physical_sum": 0.0, "mental_sum": 0.0, "count": 0})
    for row in rows:
        day = row["condition"].date
        date_bucket[day]["physical_sum"] += float(row["condition"].physical or 0)
        date_bucket[day]["mental_sum"] += float(row["condition"].mental or 0)
        date_bucket[day]["count"] += 1

    graph_data = []
    for day, data in sorted(date_bucket.items()):
        count = data["count"] or 1
        graph_data.append(
            {
                "date": day.strftime("%Y-%m-%d"),
                "physical_avg": round(data["physical_sum"] / count, 2),
                "mental_avg": round(data["mental_sum"] / count, 2),
            }
        )
    return graph_data


def _build_page_tokens(page_obj):
    total = page_obj.paginator.num_pages
    current = page_obj.number
    if total <= 7:
        return list(range(1, total + 1))

    tokens = []
    if current <= 3:
        tokens.extend([1, 2, 3, "...", total])
    elif current >= total - 2:
        tokens.extend([1, "...", total - 2, total - 1, total])
    else:
        tokens.extend([1, "...", current - 1, current, current + 1, "...", total])
    return tokens


@login_required
def dashboard_view(request):
    user = request.user
    if user.role_level not in (User.ROLE_ADMIN_L1, User.ROLE_ADMIN_L2):
        return render(request, "dashboard/not_allowed.html")

    conditions = (
        Condition.objects.select_related("user")
        .filter(is_absent=False)
        .order_by("-date", "-created_at")
    )

    profiles = EmployeeProfile.objects.select_related("user").all()
    profile_map = {p.user_id: p for p in profiles}
    excluded_ids = [p.user_id for p in profiles if p.is_target]

    filtered = []
    for c in conditions:
        profile = profile_map.get(c.user_id)
        if profile and profile.is_target:
            continue
        filtered.append({"condition": c, "profile": profile})

    paginator = Paginator(filtered, 5)
    page_number = request.GET.get("page")
    conditions_page = paginator.get_page(page_number)
    conditions_page_tokens = _build_page_tokens(conditions_page)

    graph_data = _build_graph_data(filtered)
    graph_data_dept_a = _build_graph_data(
        [row for row in filtered if row["profile"] and row["profile"].department == "部署A"]
    )
    graph_data_dept_b = _build_graph_data(
        [row for row in filtered if row["profile"] and row["profile"].department == "部署B"]
    )

    avg_values = (
        Condition.objects.filter(is_absent=False)
        .exclude(user_id__in=excluded_ids)
        .aggregate(avg_physical=Avg("physical"), avg_mental=Avg("mental"))
    )

    opinions = build_opinion_summary(user.role_level)
    opinions_paginator = Paginator(opinions.items, 5)
    opinions_page_number = request.GET.get("opinion_page")
    opinions_page = opinions_paginator.get_page(opinions_page_number)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "conditions_page": conditions_page,
            "conditions_page_tokens": conditions_page_tokens,
            "avg_physical": avg_values["avg_physical"],
            "avg_mental": avg_values["avg_mental"],
            "role_level": user.role_level,
            "opinions": opinions,
            "opinions_page": opinions_page,
            "admin_timeout_minutes": _get_admin_timeout_minutes(),
            "graph_data": graph_data,
            "graph_data_dept_a": graph_data_dept_a,
            "graph_data_dept_b": graph_data_dept_b,
        },
    )
