import pandas as pd
import os

# 读取CSV文件
csv_file = r"d:\PyCharmProject\fsg-auto-gen-prompt\最低工资问题Q&A_数据表 (1)(1)(1).csv"

try:
    # 读取CSV文件，使用第一行作为表头
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    # 提取问题和回答列
    # 假设CSV文件的列名为：问题,回答,类型
    questions = df['问题']
    answers = df['回答']
    
    # 创建新的DataFrame，只包含问题和回答两列
    new_df = pd.DataFrame({
        '问题': questions,
        '回答': answers
    })
    
    # 保存为Excel文件，不包含表头
    output_file = r"d:\PyCharmProject\fsg-auto-gen-prompt\test_data.xlsx"
    new_df.to_excel(output_file, index=False, header=False)
    
    print(f"成功生成test_data.xlsx文件，包含 {len(new_df)} 条数据")
    print(f"文件路径: {output_file}")
    print("文件格式:")
    print("- A列: 问题")
    print("- B列: 回答（作为意图）")
    
except FileNotFoundError:
    print(f"CSV文件不存在: {csv_file}")
except Exception as e:
    print(f"生成Excel文件时出错: {e}")