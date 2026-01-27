from kimi_api import call_kimi_api

def generate_initial_prompt(question, intent, api_key):
    """
    使用大模型生成初始提示词
    :param question: 问题
    :param intent: 意图（标准答案）
    :param api_key: KIMI API密钥
    :return: 初始提示词
    """
    # 创建一个提示词，让大模型帮助生成初始分类提示词
    generation_prompt = f"""
你是一个专业的提示词生成专家，擅长创建用于意图分类的提示词。

请基于以下信息，生成一个用于最低工资问题分类的初始提示词：

问题: "{question}"
预期意图: "{intent}"

意图类型说明:
1. 标准查询: 查询某地区最低工资的具体金额
2. 其他: 其他最低工资相关的问题

生成要求:
1. 提示词应该清晰、明确，包含必要的分类规则
2. 引导模型正确理解问题并输出与预期意图匹配的分类结果
3. 提示词应该包含明确的分类要求和格式说明
4. 保持提示词的长度适中，不要过长
5. 确保提示词能够让模型只输出分类结果，不输出其他内容

请输出完整的提示词：
"""
    
    # 调用KIMI API获取初始提示词
    initial_prompt = call_kimi_api(generation_prompt, api_key)
    
    # 如果API调用失败，使用默认模板
    if not initial_prompt:
        initial_prompt = f"""
你是一个智能意图分类器，负责根据用户输入的问题，判断其属于哪种意图类型。

请分析以下问题的意图，并确保你的分类结果与给定的标准答案完全匹配。

问题: "{question}"
标准答案意图: "{intent}"

意图类型说明:
1. 标准查询: 查询某地区最低工资的具体金额
2. 其他: 其他最低工资相关的问题

请按照以下要求进行分类:
1. 仔细理解问题的核心内容
2. 判断问题是否属于查询某地区最低工资的具体金额
3. 确保你的分类结果与标准答案完全一致
4. 只输出分类结果，不要输出任何其他内容
5. 分类结果只能是"标准查询"或"其他"

分类结果:
"""
    return initial_prompt

def generate_optimized_prompt(question, intent, previous_prompt, error_analysis):
    """
    基于错误分析生成优化提示词模板
    :param question: 问题
    :param intent: 意图（标准答案）
    :param previous_prompt: 之前的提示词
    :param error_analysis: 错误分析
    :return: 优化提示词模板
    """
    optimized_prompt = f"""
你是一个智能意图分类器，负责根据用户输入的问题，判断其属于哪种意图类型。

请分析以下问题的意图，并确保你的分类结果与给定的标准答案完全匹配。

问题: "{question}"
标准答案意图: "{intent}"

错误分析: {error_analysis}

意图类型说明:
1. 标准查询: 查询某地区最低工资的具体金额
2. 其他: 其他最低工资相关的问题

请按照以下要求进行分类:
1. 仔细理解问题的核心内容
2. 判断问题是否属于查询某地区最低工资的具体金额
3. 确保你的分类结果与标准答案完全一致
4. 只输出分类结果，不要输出任何其他内容
5. 分类结果只能是"标准查询"或"其他"

分类结果:
"""
    return optimized_prompt