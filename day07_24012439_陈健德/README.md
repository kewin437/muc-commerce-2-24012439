# 第7天学生项目：电商用户分析Web系统

## 运行方法

```bash
python -m pip install -r requirements.txt
python app.py
```

浏览器访问 `http://127.0.0.1:5000`。

- 用户名：`student`
- 密码：`day07`

## 项目结构

```
day07_web_student/
├── app.py                          # 路由、Session、登录闭环
├── requirements.txt
├── data/                           # 课程提供：overall/category/segment 三个 CSV
├── services/
│   ├── data_service.py             # 4 张指标卡 + 筛选 + 数据观察 + 生命周期详情
│   └── qa_service.py               # 5 类问答：总用户/流失/品类/生命周期/订单
├── static/
│   ├── css/style.css
│   ├── images/01_category_bar.png  # 检查点 2 图表 1
│   ├── images/03_ordered_line.png  # 检查点 2 图表 2
│   └── js/assistant.js             # 智能问答前端
├── templates/
│   ├── base.html                   # 顶部导航 + flash
│   ├── login.html                  # 登录页
│   ├── dashboard.html              # 数据看板
│   ├── assistant.html              # 智能问答
│   ├── segments.html               # 拓展 B 生命周期详情
│   └── 404.html
└── screenshots/                    # 5 张验收截图
```

## 核心功能

- **检查点 1：登录闭环**：`app.py` 的 `login_required` 装饰器 + `flash` 提示
- **检查点 2：数据看板**：4 张指标卡（总用户/流失用户/总体流失率/平均订单数）+ 2 张图（品类柱状图、生命周期折线图）+ 真实数据表 + 数据观察
- **检查点 3：品类筛选**：下拉框选择 `Fashion` 等具体品类，URL `?category=Fashion`，表格只显示该品类一行；选"全部"显示全部 5 个品类
- **检查点 4：离线问答**：5 类问题均从 CSV 读取数值（不支持问题有友好提示）

## 必选拓展：B 生命周期详情页

- 路由：`/segments`（顶部导航已添加入口）
- 数据来源：`data/segment_analysis.csv`
- 页面展示：4 张指标卡（覆盖用户/累计流失/总体流失率/最高风险阶段）+ 5 行生命周期阶段对比表 + 一条带数值证据的数据观察
- 证据：`screenshots/05_extension.png`

## 学生信息

- 姓名：陈健德
- 学号：24012439
- 专题方向：电商用户行为与生命周期分析
- 已完成功能：检查点 1-4 + 拓展 B
- 选择的拓展任务：B 生命周期详情页
- 拓展访问或运行方法：登录后访问 `http://127.0.0.1:5000/segments`
- 拓展证据文件：`screenshots/05_extension.png`
- 尚未解决的问题：无

## 验收测试

启动服务后，按课程要求打开浏览器保存 5 张截图到 `screenshots/`：

- `01_login.png`：登录页
- `02_dashboard.png`：登录后看板
- `03_interaction.png`：选择 `Fashion` 后
- `04_assistant.png`：智能问答提问后
- `05_extension.png`：`/segments` 详情页
