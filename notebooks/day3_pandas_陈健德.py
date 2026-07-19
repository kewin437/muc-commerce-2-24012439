# 导入所需库
from pathlib import Path
import pandas as pd
import numpy as np

# ====================== 环境与文件配置 ======================
# 定义数据文件夹路径
DATA_DIR = Path('F:/Desktop/training/data')
CSV_PATH = DATA_DIR / '淘宝全品类全国数据.csv'

# 校验工作目录与文件是否存在
print("===== 环境校验 =====")
print("当前工作目录：", Path.cwd())
print("数据文件是否存在：", CSV_PATH.exists())

# 读取csv数据
df = pd.read_csv(CSV_PATH)
print("数据读取完成\n")

# ====================== 任务1：读取数据并初步观察 ======================
print("===== 任务1：数据初步观察 =====")
# 数据行列规模
print("数据规模(行,列)：", df.shape)
# 所有字段名称
print("全部字段名：", df.columns.tolist())
# 前5行样本数据
print("前5行数据：")
print(df.head(5))
# 数据整体信息（字段类型、非空值数量）
print("数据基础信息：")
print(df.info())
# 文字回答：一行代表一条淘宝商品记录，共25000行，15列
print("结论：本数据一行代表一条商品记录，数据集共25000行、15列\n")

# ====================== 任务2：字段类型与缺失值统计 ======================
print("===== 任务2：字段类型 & 缺失值分析 =====")
# 输出所有字段数据类型
print("各字段数据类型：")
print(df.dtypes)

# 缺失值数量（降序排序）
missing_count = df.isna().sum().sort_values(ascending=False)
print("\n各字段缺失值数量：")
print(missing_count)

# 缺失率百分比
missing_rate = (df.isna().mean() * 100).round(1).sort_values(ascending=False)
print("\n各字段缺失占比(%)：")
print(missing_rate)

# 字段分析说明
print("""
字段分析：
1. 可直接数值统计字段：商品价格，该字段为float浮点数值类型，无文本混杂，可直接计算均值、中位数；
2. 暂不宜精确数值统计字段：商品销量，该字段为字符串object类型，包含"100+人付款""1万+人付款"文字，无法直接数学运算。
""")

# ====================== 任务3：选择列、loc/iloc行列选取 ======================
print("===== 任务3：数据行列选取 =====")
# 1. 单列选取：Series类型
price_series = df['商品价格']
print("df['商品价格'] 数据类型：", type(price_series))

# 2. 多列选取：DataFrame类型
product_view = df[['商品id', '一级品类', '商品价格', '省份', '商品销量']]
print("\n多列选取product_view类型：", type(product_view))
print("product_view前5行：")
print(product_view.head())

# 3. loc：按标签选取前5行，指定三列
print("\nloc选取0~4行、指定字段：")
print(df.loc[0:4, ['一级品类', '商品价格', '省份']])

# 4. iloc：按位置选取前5行、前4列
print("\niloc选取前5行、前4列：")
print(df.iloc[0:5, 0:4])

# 区别解释
print("""
df["商品价格"] 与 df[["商品价格"]]区别：
1. df["商品价格"] 单中括号，返回Series一维序列，只有一列无列名；
2. df[["商品价格"]] 双中括号，返回DataFrame二维表格，保留表头结构，支持多列扩展。
""")

# ====================== 任务4：条件筛选 + 排序 ======================
print("===== 任务4：条件筛选与排序 =====")
# 单条件：筛选广东全部商品
guangdong = df[df['省份'] == '广东']
print("广东商品总条数：", guangdong.shape[0])

# 多条件：广东 且 商品价格≥1000元，指定输出字段
condition = (df['省份'] == '广东') & (df['商品价格'] >= 1000)
selected = df.loc[condition, ['商品id', '一级品类', '二级品类', '商品价格', '省份', '商品销量']]
# 价格降序排序
selected = selected.sort_values(by='商品价格', ascending=False)
print("\n广东价格≥1000元商品，价格从高到低前10条：")
print(selected.head(10))

# 或条件：浙江、江苏商品统计
zj_js = df[(df['省份'] == '浙江') | (df['省份'] == '江苏')]
print(f"\n浙江或江苏商品总数量：{zj_js.shape[0]}")

# ====================== 任务5：描述统计 & 分组聚合 ======================
print("===== 任务5：价格统计 + 一级品类分组分析 =====")
# 商品价格描述性统计
price_desc = df['商品价格'].describe().round(2)
print("商品价格描述统计：")
print(price_desc)

# 一级品类商品数量统计
print("\n各一级品类商品数量：")
print(df['一级品类'].value_counts())

# 分组聚合：商品数量、均价、中位价，按均价降序
category_summary = (
    df.groupby('一级品类')
    .agg(
        商品数=('商品id', 'size'),
        平均价格=('商品价格', 'mean'),
        中位价格=('商品价格', 'median')
    )
    .sort_values('平均价格', ascending=False)
    .round(2)
)
print("\n一级品类价格汇总表：")
print(category_summary)

# 规范分析结论（范围—字段方法—结论—边界）
print("""
分析结论：
数据范围：本数据集25000条淘宝全国商品记录；
字段与方法：使用一级品类、商品价格字段，groupby分组聚合计算各品类均价；
结论：数码家电类商品平均标价显著高于宠物用品等日用品类；
边界说明：该统计仅基于商品上架标价，不代表实际成交金额、用户真实消费偏好。
""")

# ====================== 挑战任务：省份-类别对比（广东VS江苏） ======================
print("===== 挑战任务：广东、江苏商品数据对比 =====")
# 筛选指定两省数据
target_provinces = ['广东', '江苏']
province_subset = df[df['省份'].isin(target_provinces)]

# 按省份分组统计商品数、均价、中位价
province_summary = (
    province_subset.groupby('省份')
    .agg(
        商品数=('商品id', 'size'),
        平均价格=('商品价格', 'mean'),
        中位价格=('商品价格', 'median')
    )
    .round(2)
)
print("两省商品汇总表：")
print(province_summary)

# 分别输出两省销量最高的一级品类
for p in target_provinces:
    top_cat = province_subset.loc[province_subset['省份'] == p, '一级品类'].value_counts().head(1)
    print(f"\n{p} 数量最多的一级品类：")
    print(top_cat)

# 两条规范对比结论
print("""
对比结论1（差异描述）：在数据集内，广东省商品总量高于江苏省，且商品平均标价更高；
对比结论2（边界说明）：该差异仅反映采集到的上架商品分布，不能代表两省电商真实成交额与市场规模。
""")