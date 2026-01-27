import pandas as pd

# 创建测试数据
test_data = [
    {"question": "如何更改密码？", "intent": "账户管理"},
    {"question": "我的订单什么时候发货？", "intent": "物流查询"},
    {"question": "如何退换货？", "intent": "售后服务"},
    {"question": "产品有哪些颜色可选？", "intent": "产品信息"},
    {"question": "如何联系客服？", "intent": "客户支持"}
]

# 创建DataFrame
df = pd.DataFrame(test_data)

# 保存为Excel文件
df.to_excel("test_data.xlsx", index=False, header=False)
print("测试Excel文件已创建: test_data.xlsx")
print("包含5条测试数据，用于验证功能完整性")