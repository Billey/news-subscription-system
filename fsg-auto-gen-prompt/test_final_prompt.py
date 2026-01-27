import json
from kimi_api import get_kimi_api_key, call_kimi_api

def test_final_prompt():
    """
    测试最终提示词的分类效果
    """
    # 获取API密钥
    api_key = get_kimi_api_key()
    if not api_key:
        print("请先运行main.py并输入API密钥")
        return
    
    # 读取最终提示词
    try:
        with open('final_prompt.txt', 'r', encoding='utf-8') as f:
            final_prompt_template = f.read()
    except FileNotFoundError:
        print("final_prompt.txt文件不存在，请先运行main.py生成")
        return
    
    # 测试问题列表
    test_questions = [
        # 标准查询类型
        "上海目前最低工资是多少？",
        "北京2025年最低工资标准是多少？",
        "广州月最低工资是多少？",
        "四川泸州2025年最低工资是多少？",
        "安徽定远县最低工资是多少？",
        
        # 其他类型
        "最低工资上调会带来哪些影响？",
        "病假工资可以低于最低工资吗？",
        "加班费的计算底线是多少？",
        "最低工资包含社保吗？",
        "国家关于最低工资的政策是什么？"
    ]
    
    print("测试最终提示词的分类效果...")
    print("="*60)
    
    for question in test_questions:
        # 替换问题模板
        prompt = final_prompt_template.replace("{question}", question)
        
        # 调用KIMI API
        result = call_kimi_api(prompt, api_key)
        
        print(f"问题: {question}")
        print(f"分类结果: {result}")
        print("-"*60)

if __name__ == "__main__":
    test_final_prompt()