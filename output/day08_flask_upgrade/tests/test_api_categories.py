"""Test /api/categories 接口 —— 查询参数筛选。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app

VALID_USER = {"username": "student", "password": "day07"}


def test_categories_requires_login():
    """未登录访问 /api/categories 应被重定向到登录页。"""
    with app.test_client() as client:
        resp = client.get("/api/categories")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


def test_categories_default_all():
    """不传 category 参数时默认返回"全部"多行数据（>=5 行）。"""
    with app.test_client() as client:
        client.post("/login", data=VALID_USER)
        resp = client.get("/api/categories")
        assert resp.status_code == 200

        data = resp.get_json()
        assert data["ok"] is True
        assert data["category"] == "全部"
        assert len(data["rows"]) >= 5, f"期望 >=5 行，实际 {len(data['rows'])}"


def test_categories_filter_fashion():
    """category=Fashion 只返回 1 行 Fashion 数据。"""
    with app.test_client() as client:
        client.post("/login", data=VALID_USER)
        resp = client.get("/api/categories?category=Fashion")
        assert resp.status_code == 200

        data = resp.get_json()
        assert data["ok"] is True
        assert data["category"] == "Fashion"
        assert len(data["rows"]) == 1, f"Fashion 过滤后应 1 行，实际 {len(data['rows'])}"


def test_categories_filter_grocery():
    """category=Grocery 只返回 1 行 Grocery 数据。"""
    with app.test_client() as client:
        client.post("/login", data=VALID_USER)
        resp = client.get("/api/categories?category=Grocery")
        assert resp.status_code == 200

        data = resp.get_json()
        assert data["ok"] is True
        assert data["category"] == "Grocery"
        assert len(data["rows"]) == 1
