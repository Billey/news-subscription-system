import pandas as pd
import logging

def read_excel_data(file_path):
    """
    读取Excel文件数据
    :param file_path: Excel文件路径
    :return: 包含问题和意图的列表
    """
    try:
        df = pd.read_excel(file_path)
        # 假设Excel的A列是问题，B列是意图
        data = []
        for index, row in df.iterrows():
            try:
                question = row.iloc[0]  # A列
                intent = row.iloc[1]     # B列
                data.append({
                    'question': str(question),
                    'intent': str(intent)
                })
            except IndexError:
                logging.warning(f"第{index+1}行数据格式不正确，跳过")
                continue
        return data
    except FileNotFoundError:
        logging.error(f"Excel文件不存在: {file_path}")
        return []
    except Exception as e:
        logging.error(f"读取Excel文件时出错: {e}")
        return []

if __name__ == "__main__":
    # 测试读取功能
    import os
    test_file = "test_data.xlsx"
    if os.path.exists(test_file):
        data = read_excel_data(test_file)
        print(f"读取到 {len(data)} 条数据")
        for i, item in enumerate(data[:5]):
            print(f"第{i+1}条: 问题='{item['question']}', 意图='{item['intent']}'")
    else:
        print(f"测试文件 {test_file} 不存在，请先运行 create_test_data.py 创建测试数据")