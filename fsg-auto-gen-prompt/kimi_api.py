import requests
import json
import logging

def get_kimi_api_key():
    """
    获取KIMI API密钥
    :return: API密钥
    """
    # 尝试从配置文件读取
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('kimi_api_key', '')
            if not api_key:
                logging.warning("配置文件中未找到API密钥")
            return api_key
    except FileNotFoundError:
        logging.info("配置文件不存在，将提示用户输入API密钥")
        return ''
    except json.JSONDecodeError:
        logging.error("配置文件格式不正确，将提示用户输入API密钥")
        return ''
    except Exception as e:
        logging.error(f"读取配置文件失败: {e}")
        return ''

def call_kimi_api(prompt, api_key):
    """
    调用KIMI大模型API
    :param prompt: 提示词
    :param api_key: API密钥
    :return: 模型返回的分类结果
    """
    if not api_key:
        logging.error("API密钥为空，无法调用KIMI API")
        return ""
    
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "moonshot-v1-8k",  # 使用KIMI的模型
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,  # 降低随机性，提高一致性
        "max_tokens": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # 检查响应状态
        result = response.json()
        # 提取模型返回的内容
        if result.get('choices') and len(result['choices']) > 0:
            return result['choices'][0]['message']['content'].strip()
        else:
            logging.warning("API返回结果格式不正确")
            return ""
    except requests.exceptions.Timeout:
        logging.error("API调用超时")
        return ""
    except requests.exceptions.HTTPError as e:
        logging.error(f"API调用失败，HTTP错误: {e}")
        return ""
    except json.JSONDecodeError:
        logging.error("API返回结果解析失败")
        return ""
    except Exception as e:
        logging.error(f"调用KIMI API失败: {e}")
        return ""