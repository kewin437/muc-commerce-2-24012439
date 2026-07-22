# 第9天学生项目：机器学习零基础数据准备

## 运行方法

```bash
python -m pip install -r requirements.txt
python validate_day09_environment.py
jupyter lab
```

打开`notebooks/day09_ml_preparation_student.ipynb`。Notebook已经提供完整处理骨架，你只需完成少量关键填空、运行检查点并撰写解释。

## 学生信息

- 姓名：陈健德
- 学号：24012439
- 班级：2班

## 用自己的话回答

- 什么是特征，什么是标签：特征是模型用于判断的输入信息（如Tenure、Complain）；标签是希望预测的结果（此处为Churn，0=未流失，1=流失）。
- 为什么要保留测试集：测试集模拟模型未见过的新用户，用来检验模型是否真正学到了规律，而不是只记住了训练集。
- 为什么83%准确率仍可能没有用：最低参照线始终预测人数最多的“未流失”，由于未流失用户占约83%，准确率自然达到83%，但流失召回率为0，一个流失用户都没找到，没有业务价值。
