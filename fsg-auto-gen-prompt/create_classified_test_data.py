import pandas as pd
import re

# 读取CSV文件
csv_file = r"d:\PyCharmProject\fsg-auto-gen-prompt\最低工资问题Q&A_数据表 (1)(1)(1).csv"

def classify_intent(question):
    """
    分类问题意图
    :param question: 问题
    :return: 分类结果（标准查询或其他）
    """
    # 标准查询模式：查询某地区最低工资的具体金额
    # 匹配包含地区名称+最低工资+金额查询的模式
    standard_query_patterns = [
        r".*[省市县区].*最低工资.*[多少|是多少|为多少]",
        r".*最低工资.*[标准|金额]",
        r".*[省市县区].*月最低工资.*[多少|是多少]",
        r".*[省市县区].*小时最低工资.*[多少|是多少]",
        r".*[省市县区].*现行最低工资.*[多少|是多少]",
        r".*[省市县区].*当前最低工资.*[多少|是多少]",
        r".*[省市县区].*最新最低工资.*[多少|是多少]",
        r".*[省市县区].*202[45].*最低工资.*[多少|是多少]",
        r".*一类.*最低工资.*[多少|是多少]",
        r".*二类.*最低工资.*[多少|是多少]",
        r".*三类.*最低工资.*[多少|是多少]",
        r".*四类.*最低工资.*[多少|是多少]"
    ]
    
    # 检查是否匹配标准查询模式
    for pattern in standard_query_patterns:
        if re.search(pattern, question, re.IGNORECASE):
            return "标准查询"
    
    # 其他情况归为"其他"
    return "其他"

try:
    # 读取CSV文件
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    # 处理每条数据
    data = []
    for index, row in df.iterrows():
        question = row['问题']
        intent = classify_intent(question)
        data.append({
            'question': question,
            'intent': intent
        })
    
    # 创建新的DataFrame
    new_df = pd.DataFrame(data)
    
    # 保存为Excel文件，不包含表头
    output_file = r"d:\PyCharmProject\fsg-auto-gen-prompt\classified_test_data.xlsx"
    new_df.to_excel(output_file, index=False, header=False)
    
    # 统计分类结果
    standard_count = new_df[new_df['intent'] == '标准查询'].shape[0]
    other_count = new_df[new_df['intent'] == '其他'].shape[0]
    
    print(f"成功生成test_data.xlsx文件，包含 {len(new_df)} 条数据")
    print(f"文件路径: {output_file}")
    print(f"分类统计:")
    print(f"- 标准查询: {standard_count} 条")
    print(f"- 其他: {other_count} 条")
    print("文件格式:")
    print("- A列: 问题")
    print("- B列: 分类结果（标准查询/其他）")
    
except FileNotFoundError:
    print(f"CSV文件不存在: {csv_file}")
except Exception as e:
    print(f"生成Excel文件时出错: {e}")