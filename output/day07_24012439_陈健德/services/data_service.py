from pathlib import Path

import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    metric_map = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    # TODO 2-1：在已有两张指标卡基础上，增加“总体流失率”和“平均订单数”。
    churn_rate = float(metric_map["流失率"])
    avg_orders = float(metric_map["平均订单数"])
    metrics = [
        {"label": "总用户数", "value": f"{int(metric_map['用户数']):,}", "note": "人"},
        {"label": "流失用户", "value": f"{int(metric_map['流失人数']):,}", "note": "人"},
        {"label": "总体流失率", "value": f"{churn_rate:.2%}", "note": f"流失 {int(metric_map['流失人数']):,} 人"},
        {"label": "平均订单数", "value": f"{avg_orders:.2f}", "note": "单 / 人"},
    ]

    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()
    # TODO 3-1：选择具体品类后筛选table_df。
    # 提示：教师参考项目中使用布尔条件筛选。
    if selected_category and selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]

    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]
    table_df["流失率"] = table_df["流失率"].map(lambda value: f"{value:.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].map(lambda value: f"{value:.2f}")

    # TODO 2-2：找出流失率最高的生命周期阶段，并生成一句数据观察。
    risk_row = segment_df.loc[segment_df["流失率"].idxmax()]
    insight = (
        f"流失率最高的生命周期阶段是『{risk_row['TenureGroup']}』，"
        f"流失率达 {risk_row['流失率']:.2%}（{int(risk_row['流失人数'])} / {int(risk_row['用户数'])} 人），"
        f"建议在用户首单 30 天内加强引导与召回。"
    )

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict("records"),
        "insight": insight,
    }


def load_segments_data(base_dir: Path) -> dict:
    """拓展 B：生命周期详情页数据"""
    data_dir = base_dir / "data"
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    risk_row = segment_df.loc[segment_df["流失率"].idxmax()]
    rows = []
    for _, row in segment_df.iterrows():
        rows.append({
            "stage": row["TenureGroup"],
            "user_count": int(row["用户数"]),
            "churn_count": int(row["流失人数"]),
            "churn_rate": f"{row['流失率']:.2%}",
            "avg_orders": f"{row['平均订单数']:.2f}",
            "avg_cashback": f"{row['平均返现']:.2f}",
            "avg_days": f"{row['平均距上次下单天数']:.2f}",
        })

    total_users = int(segment_df["用户数"].sum())
    total_churn = int(segment_df["流失人数"].sum())
    overall_rate = total_churn / total_users if total_users else 0.0

    return {
        "rows": rows,
        "total_users": f"{total_users:,}",
        "total_churn": f"{total_churn:,}",
        "overall_rate": f"{overall_rate:.2%}",
        "risk_stage": risk_row["TenureGroup"],
        "risk_rate": f"{risk_row['流失率']:.2%}",
        "risk_users": int(risk_row["用户数"]),
        "risk_churn": int(risk_row["流失人数"]),
    }
