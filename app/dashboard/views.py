from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import render

from accounts.models import EmployeeProfile, User
from conditions.models import Condition
from dashboard.models import SystemSetting
from analysis.services import build_opinion_summary


def _get_admin_timeout_minutes():
    setting = SystemSetting.objects.first()
    if setting and setting.admin_timeout_minutes:
        return setting.admin_timeout_minutes
    return 30


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

    # 集計対象外は除外
    filtered = []
    for c in conditions:
        profile = profile_map.get(c.user_id)
        if profile and profile.is_target:
            continue
        filtered.append({"condition": c, "profile": profile})

    avg_values = (
        Condition.objects.filter(is_absent=False)
        .exclude(user_id__in=excluded_ids)
        .aggregate(avg_physical=Avg("physical"), avg_mental=Avg("mental"))
    )

    opinions = build_opinion_summary(user.role_level)

    return render(
        request,
        "dashboard/dashboard.html",
        {
        "conditions": filtered,
            "avg_physical": avg_values["avg_physical"],
            "avg_mental": avg_values["avg_mental"],
            "role_level": user.role_level,
            "opinions": opinions,
            "admin_timeout_minutes": _get_admin_timeout_minutes(),
        },
    )
