import json
import time
import logging
import os
from excel_reader import read_excel_data
from prompt_generator import generate_initial_prompt
from kimi_api import get_kimi_api_key, call_kimi_api
from prompt_optimizer import compare_classification, optimize_prompt

def setup_logging():
    """
    设置日志配置
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def generate_final_prompt(success_prompts, api_key):
    """
    使用大模型基于成功的提示词生成最终的通用提示词
    :param success_prompts: 成功的提示词列表
    :param api_key: KIMI API密钥
    :return: 最终的通用提示词
    """
    # 分析成功的提示词，提取共同特征
    # 使用大模型生成一个优化的通用提示词
    
    # 从成功的提示词中提取关键信息
    if success_prompts:
        # 提取一些成功的提示词示例
        sample_prompts = []
        for i, prompt_data in enumerate(success_prompts[:3]):  # 取前3个作为示例
            sample_prompts.append(f"""
示例 {i+1}:
问题: "{prompt_data['question']}"
意图: "{prompt_data['intent']}"
提示词:
{prompt_data['prompt']}
""")
        
        sample_prompts_text = "\n".join(sample_prompts)
        
        # 创建一个提示词，让大模型帮助生成最终的通用提示词
        final_generation_prompt = f"""
你是一个专业的提示词优化专家，擅长创建和优化用于意图分类的提示词。

请基于以下成功的提示词示例，生成一个最终的通用提示词，适用于所有最低工资相关问题的分类：

成功提示词示例:
{sample_prompts_text}

意图类型定义:
- 标准查询: 明确询问某个地区或城市的最低工资具体金额的问题
- 其他: 除标准查询外的其他所有最低工资相关问题

生成要求:
1. 提示词应该是通用的，能够处理各种最低工资相关的问题
2. 提示词应该清晰、明确，包含必要的分类规则
3. 引导模型正确理解问题并输出准确的分类结果
4. 提示词应该包含明确的分类要求和格式说明
5. 保持提示词的长度适中，不要过长
6. 确保提示词能够让模型只输出分类结果，不输出其他内容
7. 分类结果只能是"标准查询"或"其他"

请输出完整的通用提示词：
"""
        
        # 调用KIMI API获取最终通用提示词
        from kimi_api import call_kimi_api
        final_prompt = call_kimi_api(final_generation_prompt, api_key)
        
        # 如果API调用失败，使用优化的默认模板
        if not final_prompt:
            final_prompt = """
你是一个专业的意图分类器，擅长处理最低工资相关的问题分类。

请仔细分析以下问题，判断其意图类型，并确保分类结果准确无误。

问题: "{question}"

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

请严格按照上述规则进行分类，确保结果准确。

分类结果:
"""
    else:
        # 如果没有成功的提示词，使用默认模板
        final_prompt = """
你是一个智能意图分类器，负责根据用户输入的问题，判断其属于哪种意图类型。

请分析以下问题的意图，并输出正确的分类结果。

问题: "{question}"

意图类型说明:
1. 标准查询: 查询某地区最低工资的具体金额
2. 其他: 其他最低工资相关的问题

请按照以下要求进行分类:
1. 仔细理解问题的核心内容
2. 判断问题是否属于查询某地区最低工资的具体金额
3. 只输出分类结果，不要输出任何其他内容
4. 分类结果只能是"标准查询"或"其他"

分类结果:
"""
    return final_prompt

def main():
    """
    主流程控制逻辑
    """
    # 设置日志
    setup_logging()
    
    # 1. 读取Excel数据
    excel_file = input("请输入Excel文件路径: ")
    if not os.path.exists(excel_file):
        logging.error(f"Excel文件不存在: {excel_file}")
        print("文件不存在，请检查路径是否正确")
        return
    
    data = read_excel_data(excel_file)
    
    if not data:
        logging.error("未读取到数据，请检查Excel文件格式是否正确")
        print("未读取到数据，请检查Excel文件格式是否正确")
        return
    
    logging.info(f"成功读取 {len(data)} 条数据")
    print(f"成功读取 {len(data)} 条数据")
    
    # 2. 获取KIMI API密钥
    api_key = get_kimi_api_key()
    if not api_key:
        api_key = input("请输入KIMI API密钥: ")
        if not api_key:
            logging.error("API密钥为空，无法继续")
            print("API密钥为空，无法继续")
            return
        # 保存API密钥到配置文件
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump({'kimi_api_key': api_key}, f, ensure_ascii=False, indent=2)
            logging.info("API密钥已保存到config.json文件")
            print("API密钥已保存到config.json文件")
        except Exception as e:
            logging.error(f"保存API密钥失败: {e}")
            print(f"保存API密钥失败: {e}")
    
    # 3. 处理每条数据
    results = []
    max_attempts = 5  # 最大尝试次数
    
    for i, item in enumerate(data):
        question = item['question']
        intent = item['intent']
        logging.info(f"处理第 {i+1} 条数据: 问题='{question}', 意图='{intent}'")
        print(f"\n处理第 {i+1} 条数据:")
        print(f"问题: {question}")
        print(f"标注意图: {intent}")
        
        # 生成初始提示词
        prompt = generate_initial_prompt(question, intent, api_key)
        attempt = 1
        
        while attempt <= max_attempts:
            logging.info(f"第 {i+1} 条数据，尝试第 {attempt} 次")
            print(f"尝试第 {attempt} 次...")
            
            # 调用KIMI API
            result = call_kimi_api(prompt, api_key)
            
            if not result:
                logging.warning(f"API调用失败，重试中...")
                print("API调用失败，重试中...")
                time.sleep(2)  # 等待2秒后重试
                attempt += 1
                continue
            
            logging.info(f"模型返回: {result}")
            print(f"模型返回: {result}")
            
            # 比较分类结果
            if compare_classification(result, intent):
                logging.info(f"分类结果与标注意图匹配！")
                print("分类结果与标注意图匹配！")
                results.append({
                    'question': question,
                    'intent': intent,
                    'prompt': prompt,
                    'success': True,
                    'attempts': attempt
                })
                break
            else:
                logging.warning(f"分类结果与标注意图不匹配，优化提示词...")
                print("分类结果与标注意图不匹配，优化提示词...")
                # 优化提示词
                prompt = optimize_prompt(question, intent, prompt, result, api_key)
                attempt += 1
                time.sleep(1)  # 等待1秒后重试
        
        if attempt > max_attempts:
            logging.error(f"达到最大尝试次数，未能匹配标注意图")
            print("达到最大尝试次数，未能匹配标注意图")
            results.append({
                'question': question,
                'intent': intent,
                'prompt': prompt,
                'success': False,
                'attempts': attempt - 1
            })
    
    # 4. 输出结果
    print("\n" + "="*50)
    print("处理完成！")
    print("="*50)
    
    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    logging.info(f"处理完成，成功: {success_count}/{total_count}，成功率: {success_rate:.2f}%")
    print(f"成功匹配: {success_count}/{total_count}")
    print(f"成功率: {success_rate:.2f}%")
    
    # 保存成功的提示词
    success_prompts = [r for r in results if r['success']]
    if success_prompts:
        try:
            with open('success_prompts.json', 'w', encoding='utf-8') as f:
                json.dump(success_prompts, f, ensure_ascii=False, indent=2)
            logging.info(f"成功的提示词已保存到success_prompts.json文件，共 {len(success_prompts)} 条")
            print(f"成功的提示词已保存到success_prompts.json文件，共 {len(success_prompts)} 条")
        except Exception as e:
            logging.error(f"保存成功提示词失败: {e}")
            print(f"保存成功提示词失败: {e}")
    
    # 保存所有结果
    try:
        with open('all_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logging.info("所有结果已保存到all_results.json文件")
        print("所有结果已保存到all_results.json文件")
    except Exception as e:
        logging.error(f"保存所有结果失败: {e}")
        print(f"保存所有结果失败: {e}")
    
    # 生成最终的通用提示词
    if success_prompts:
        final_prompt = generate_final_prompt(success_prompts, api_key)
        try:
            with open('final_prompt.txt', 'w', encoding='utf-8') as f:
                f.write(final_prompt)
            logging.info("最终的通用提示词已保存到final_prompt.txt文件")
            print("\n最终的通用提示词已生成并保存到final_prompt.txt文件")
            print("\n通用提示词预览:")
            print(final_prompt)
        except Exception as e:
            logging.error(f"保存最终提示词失败: {e}")
            print(f"保存最终提示词失败: {e}")

if __name__ == "__main__":
    main()