from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from accounts.models import EmployeeProfile
from django.conf import settings


@dataclass
class OpinionItem:
    mode: str
    mode_label: str
    tag: str
    content: str


@dataclass
class OpinionSummary:
    tag_counts: dict
    items: list


def _mode_label(mode):
    return {"anonymous": "匿名", "semi": "準匿名", "signed": "署名"}.get(mode, mode)


def _safe_escape_csv(value: str) -> str:
    if not value:
        return value
    if value[0] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def _age_range(age: int) -> str:
    if age is None:
        return "-"
    start = (age // 10) * 10
    end = start + 9
    return f"{start}-{end}"


def _build_analysis_df():
    # app/ が BASE_DIR のため、1つ上のプロジェクトルートを基準に読む
    project_root = Path(settings.BASE_DIR).parent
    csv_path = project_root / "php_opinion_box" / "opinions" / "opinion_box.csv"
    if not csv_path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return pd.DataFrame()

    required_cols = {"timestamp", "employee_id", "mode", "content", "tag"}
    if not required_cols.issubset(set(df.columns)):
        return pd.DataFrame()

    df = df.dropna(subset=["mode", "content", "tag"])
    df["content"] = df["content"].astype(str)
    df["tag"] = df["tag"].astype(str)
    df["mode"] = df["mode"].astype(str)
    df["employee_id"] = df["employee_id"].astype(str)

    profiles = EmployeeProfile.objects.select_related("user").all()
    profile_map = {str(p.user_id): p for p in profiles}

    def map_profile(row):
        profile = profile_map.get(str(row["employee_id"]))
        if not profile:
            return {"gender": "-", "age_range": "-", "department": "-", "name": "-"}
        return {
            "gender": profile.gender,
            "age_range": _age_range(profile.age),
            "department": profile.department,
            "name": profile.full_name,
        }

    enriched = df.apply(map_profile, axis=1, result_type="expand")
    df = pd.concat([df, enriched], axis=1)

    def apply_mode(row):
        if row["mode"] == "anonymous":
            row["gender"] = "-"
            row["age_range"] = "-"
            row["department"] = "-"
            row["name"] = "-"
        elif row["mode"] == "semi":
            row["department"] = "-"
            row["name"] = "-"
        return row

    df = df.apply(apply_mode, axis=1)
    return df


def build_opinion_summary(role_level: int) -> OpinionSummary:
    df = _build_analysis_df()
    if df.empty:
        return OpinionSummary(tag_counts={}, items=[])

    # タグ件数は全投稿を集計。管理者レベル1は内容のみ非表示。
    tag_counts = df["tag"].value_counts().to_dict()

    items = []
    if role_level == 2:
        for _, row in df.iterrows():
            content = _safe_escape_csv(row["content"])
            tag = _safe_escape_csv(row["tag"])
            items.append(
                OpinionItem(
                    mode=row["mode"],
                    mode_label=_mode_label(row["mode"]),
                    tag=tag,
                    content=content,
                )
            )

    return OpinionSummary(tag_counts=tag_counts, items=items)
