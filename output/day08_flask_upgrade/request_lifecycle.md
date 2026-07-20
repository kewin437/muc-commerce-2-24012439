# 请求流程与代码讲解

> 本文档解释 day08 Flask 数据看板项目的完整请求处理流程，对应评分标准第 8 项"请求流程与代码解释"。

---

## 一、整体架构

```
浏览器/客户端
    │
    ▼
┌──────────────────────────────────────┐
│              app.py                  │
│  ┌──────────┐  ┌──────────────────┐ │
│  │ 路由层    │  │ 错误处理器       │ │
│  │ /login   │  │ @errorhandler(400)│ │
│  │ /dashboard│  │ @errorhandler(404)│ │
│  │ /health  │  └──────────────────┘ │
│  │ /api/*   │                       │
│  └────┬─────┘                       │
│       │ 调用                        │
│  ┌────▼──────────────────────────┐  │
│  │        services/              │  │
│  │  data_service.py  ── 读取CSV  │  │
│  │  qa_service.py    ── 问答匹配  │  │
│  └───────────────┬───────────────┘  │
└──────────────────┼──────────────────┘
                   │
              ┌────▼────┐
              │  data/  │
              │  *.csv  │
              └─────────┘
```

## 二、Flask 请求生命周期

### 2.1 Flask 应用创建

```python
# app.py 第 14-17 行
BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["SECRET_KEY"] = "day07-classroom-demo-key"
```

- `BASE_DIR` 指向项目根目录（通过 `__file__` 动态计算，不依赖当前工作目录）
- `SECRET_KEY` 用于加密 session cookie，没有它 `session` 对象无法工作

### 2.2 请求到来时发生了什么

```
1. HTTP 请求到达 Flask
       │
2. Flask 解析 URL，匹配路由（@app.route）
       │
3. 路由上如有 @login_required 装饰器 → 检查 session
       │   ├── 无 session → 302 重定向到 /login
       │   └── 有 session → 继续执行视图函数
       │
4. 视图函数执行
       │   ├── 调用 services 层读取数据
       │   ├── 调用 render_template() 或 jsonify()
       │   └── 返回 Response 对象
       │
5. Flask 将 Response 发送回客户端
```

## 三、核心路由逐一分析

### 3.1 `/health` —— 健康检查

```python
@app.route("/health")
def health():
    return jsonify({"ok": True, "service": "day08-flask-upgrade"})
```

- **无登录限制**，外部监控工具可直接调用
- 返回固定 JSON，仅用于确认进程存活
- 流程：客户端 `GET /health` → Flask 匹配路由 → `health()` 执行 → `jsonify()` 生成 JSON → 响应

### 3.2 `/login` —— 用户登录

```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "student" and password == "day07":
            session["username"] = username
            return redirect(url_for("dashboard"))
        flash("账号或密码错误。", "danger")
    return render_template("login.html")
```

- **GET**：渲染登录页面
- **POST**：校验凭据 → 写入 `session["username"]` → 302 跳转到 `/dashboard`
- session 数据存储在客户端的加密 cookie 中（由 `SECRET_KEY` 签名）

### 3.3 `/dashboard` —— 数据看板（需登录）

```python
@app.route("/dashboard")
@login_required
def dashboard():
    category = request.args.get("category", "全部")
    dashboard_data = load_dashboard_data(BASE_DIR, category)
    return render_template("dashboard.html", ..., **dashboard_data)
```

- `@login_required` 装饰器先执行：检查 `session["username"]` 是否存在
- 通过 `request.args` 读取 URL 查询参数 `?category=...`
- `load_dashboard_data()` 从 3 个 CSV 加载数据并做品类筛选
- `**dashboard_data` 将字典解包为模板变量

### 3.4 `/api/metrics` —— 指标 JSON API（需登录）

```python
@app.route("/api/metrics")
@login_required
def metrics_api():
    return jsonify({"ok": True, "metrics": load_metric_api_data(BASE_DIR)})
```

- 返回 4 条指标卡（总用户数、流失用户、流失率、平均订单数）
- `load_metric_api_data()` 内部调用 `load_dashboard_data()` 后只提取 `metrics` 字段
- 返回结构：`{"ok": true, "metrics": [{"label":..., "value":..., "note":...}, ...]}`

### 3.5 `/api/categories` —— 品类筛选 API（需登录）

```python
@app.route("/api/categories")
@login_required
def categories_api():
    category = request.args.get("category", "全部")
    return jsonify({"ok": True, "category": category,
                    "rows": load_category_api_data(BASE_DIR, category)})
```

- `?category=Fashion` → 返回 1 行 Fashion 数据
- 不传参数 → 默认 `"全部"` → 返回所有 5 行
- `load_category_api_data()` 内部在 DataFrame 上做行筛选：`table_df[table_df["PreferedOrderCat"] == selected_category]`

### 3.6 `/api/ask` —— 问答 API（需登录，含 400 触发）

```python
@app.route("/api/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"ok": False, "answer": "请输入一个与项目数据有关的问题。"}), 400
    return jsonify({"ok": True, "answer": answer_question(BASE_DIR, question)})
```

- 空 question 触发 `abort(400)` → 被 `@errorhandler(400)` 捕获 → 返回统一 JSON
- 非空 question → `qa_service.answer_question()` 做关键词匹配 → 返回对应数据回答

## 四、`@login_required` 装饰器机制

```python
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("请先登录后再访问数据看板。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view
```

- `@wraps(view)` 保留原函数名和 docstring
- 未登录 → `flash()` 存入一条消息（下次渲染页面时显示）+ 302 跳转
- 已登录 → 原样调用被装饰的函数

## 五、统一错误处理

```python
@app.errorhandler(400)
def bad_request(_error):
    return jsonify({"ok": False, "error": "请求格式不正确。"}), 400

@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404
```

- `@errorhandler(400)` 捕获所有 `abort(400)` 和 Flask 自动触发的 400 错误
- 返回 JSON 而非默认的 HTML 错误页，方便 API 客户端解析
- 404 仍然渲染 HTML 模板（面向浏览器用户）

## 六、data_service 数据流

```
csv 文件 (data/overall_metrics.csv / category_analysis.csv / segment_analysis.csv)
      │
      ▼ _read_csv() 用 utf-8-sig 编码读取（处理 BOM 头）
      │
      ▼ load_dashboard_data()
      │   ├── 指标卡：从 metrics_df 构造 list[dict]
      │   ├── 品类列表：category_df["PreferedOrderCat"].tolist()
      │   ├── 品类表格：按 selected_category 筛选后 to_dict("records")
      │   └── 流失洞察：segment_df 中流失率最高的行
      │
      ▼ load_metric_api_data() —— 只返回 metrics 字段
      ▼ load_category_api_data() —— 只返回 category_rows 字段
```

- **TODO 8-4 要点**：`to_dict("records")` 返回 `list[dict]`，且 dict 值都是 `str`（因为做了 `f"{value:.1%}"` 格式化），天然可被 `jsonify` 序列化，无需额外处理。

## 七、测试覆盖

| 测试文件 | 覆盖内容 |
|---|---|
| `tests/test_health.py` | /health 返回 200 + ok:true；无需登录 |
| `tests/test_api_metrics.py` | 未登录 → 302；登录后 → 200 + 4 条指标 |
| `tests/test_api_categories.py` | 未登录 → 302；默认全部(>=5行)；Fashion 过滤(1行)；Grocery 过滤(1行) |
| `tests/test_error_handling.py` | 空 question → 400 JSON；/health 不受影响 |
