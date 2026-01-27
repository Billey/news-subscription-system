from kimi_api import call_kimi_api

def compare_classification(result, expected_intent):
    """
    比较分类结果与预期意图是否匹配
    :param result: 模型返回的分类结果
    :param expected_intent: 预期意图
    :return: 是否匹配
    """
    # 去除首尾空格，转换为小写进行比较
    return result.strip().lower() == expected_intent.strip().lower()

def analyze_error(result, expected_intent):
    """
    分析错误原因
    :param result: 模型返回的分类结果
    :param expected_intent: 预期意图
    :return: 错误分析
    """
    error_analysis = f"""
模型分类结果与预期意图不匹配:
- 模型返回: "{result}"
- 预期意图: "{expected_intent}"
"""
    return error_analysis

def optimize_prompt(question, intent, previous_prompt, result, api_key):
    """
    使用大模型优化提示词
    :param question: 问题
    :param intent: 意图
    :param previous_prompt: 之前的提示词
    :param result: 模型返回的分类结果
    :param api_key: KIMI API密钥
    :return: 优化后的提示词
    """
    error_analysis = analyze_error(result, intent)
    
    # 创建一个提示词，让大模型帮助优化分类提示词
    optimization_prompt = f"""
你是一个专业的提示词优化专家，擅长创建和优化用于意图分类的提示词。

请基于以下信息，优化一个用于最低工资问题分类的提示词：

当前问题: "{question}"
预期意图: "{intent}"
当前提示词:
{previous_prompt}

错误分析:
{error_analysis}

优化要求:
1. 保持提示词的核心结构，但改进其表述方式
2. 增强提示词对意图分类的引导能力
3. 确保优化后的提示词能够让模型正确分类该问题
4. 提示词应该清晰、明确，包含必要的分类规则
5. 不要改变意图类型的定义
6. 保持提示词的长度适中，不要过长

请输出优化后的完整提示词：
"""
    
    # 调用KIMI API获取优化后的提示词
    optimized_prompt = call_kimi_api(optimization_prompt, api_key)
    
    # 如果API调用失败，返回基于规则的优化提示词
    if not optimized_prompt:
        # 基于规则的备用优化
        optimized_prompt = f"""
你是一个专业的意图分类器，擅长处理最低工资相关的问题分类。

请仔细分析以下问题，判断其意图类型，并确保分类结果与预期完全一致。

问题: "{question}"
预期意图: "{intent}"

意图类型定义:
- 标准查询: 明确询问某个地区或城市的最低工资具体金额的问题
- 其他: 除标准查询外的其他所有最低工资相关问题

分类规则:
1. 首先识别问题中是否包含地区名称（如城市、省份、县区等）
2. 然后判断问题是否明确要求获知该地区最低工资的具体数值
3. 如果同时满足上述两个条件，则分类为"标准查询"
4. 否则，分类为"其他"
5. 只输出分类结果，不添加任何额外说明
6. 分类结果只能是"标准查询"或"其他"

请严格按照上述规则进行分类，确保结果与预期意图完全一致。

分类结果:
"""
    
    return optimized_prompt