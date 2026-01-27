import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import (
    load_config, load_subscribers, save_subscribers, 
    send_email, crawl_sina_news, get_international_news,
    get_real_time_news, generate_news_content
)

class TestNewsSystem(unittest.TestCase):
    """新闻订阅系统单元测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试配置文件
        self.test_config = {
            "email": {
                "smtp_server": "smtp.qq.com",
                "smtp_port": 465,
                "sender_email": "test@qq.com",
                "sender_password": "test_password",
                "subject": "测试新闻"
            },
            "news_api": {
                "api_key": "test_api_key"
            }
        }
        
        # 创建测试订阅文件
        self.test_subscribers = {
            "subscribers": [
                {
                    "email": "test1@qq.com",
                    "status": "active",
                    "created_at": "2026-01-01T00:00:00",
                    "updated_at": "2026-01-01T00:00:00"
                }
            ]
        }
        
        # 保存测试文件
        with open('test_config.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_config, f)
        
        with open('test_subscribers.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_subscribers, f)
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除测试文件
        test_files = ['test_config.json', 'test_subscribers.json', 'test_news.json']
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
    
    def test_load_config(self):
        """测试配置文件加载功能"""
        # 测试正常加载
        with patch('app.open', unittest.mock.mock_open(read_data=json.dumps(self.test_config))):
            config = load_config()
            self.assertIsInstance(config, dict)
            self.assertIn('email', config)
            self.assertIn('news_api', config)
    
    def test_load_subscribers(self):
        """测试订阅用户加载功能"""
        # 测试正常加载
        with patch('app.open', unittest.mock.mock_open(read_data=json.dumps(self.test_subscribers))):
            subscribers = load_subscribers()
            self.assertIsInstance(subscribers, dict)
            self.assertIn('subscribers', subscribers)
            self.assertEqual(len(subscribers['subscribers']), 1)
        
        # 测试文件不存在的情况
        with patch('app.open', side_effect=FileNotFoundError):
            subscribers = load_subscribers()
            self.assertEqual(subscribers, {"subscribers": []})
    
    @patch('app.smtplib.SMTP_SSL')
    def test_send_email(self, mock_smtp):
        """测试邮件发送功能"""
        # 模拟SMTP服务器
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # 测试邮件发送
        with patch('app.load_config', return_value=self.test_config):
            result = send_email('recipient@qq.com', '测试邮件', '测试内容')
            self.assertTrue(result)
            mock_server.login.assert_called_once_with('test@qq.com', 'test_password')
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()
    
    @patch('app.requests.get')
    def test_crawl_sina_news(self, mock_get):
        """测试新浪新闻爬取功能"""
        # 模拟新浪新闻响应
        mock_response = MagicMock()
        mock_response.encoding = 'utf-8'
        mock_response.text = '''
        <div class="news-item">
            <h2><a href="https://news.sina.com.cn/test1">测试新闻1</a></h2>
            <span class="time">2026-01-26</span>
        </div>
        <div class="news-item">
            <a href="https://news.sina.com.cn/test2">测试新闻2</a>
            <span class="time">2026-01-26</span>
        </div>
        '''
        mock_get.return_value = mock_response
        
        # 测试新闻爬取
        news_list = crawl_sina_news()
        self.assertIsInstance(news_list, list)
        self.assertGreater(len(news_list), 0)
        self.assertEqual(news_list[0]['category'], '国内新闻')
    
    @patch('app.requests.get')
    def test_get_international_news(self, mock_get):
        """测试国际新闻获取功能"""
        # 模拟NewsAPI响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Test News",
                    "description": "Test Description",
                    "url": "https://test.com/news",
                    "publishedAt": "2026-01-26T00:00:00Z"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # 测试国际新闻获取
        with patch('app.load_config', return_value=self.test_config):
            news_list = get_international_news()
            self.assertIsInstance(news_list, list)
            self.assertEqual(len(news_list), 1)
            self.assertEqual(news_list[0]['category'], '国际新闻')
    
    @patch('app.crawl_sina_news')
    @patch('app.get_international_news')
    def test_get_real_time_news(self, mock_int_news, mock_sina_news):
        """测试实时新闻获取功能"""
        # 模拟新闻数据
        mock_sina_news.return_value = [
            {
                "id": 1,
                "title": "国内测试新闻",
                "content": "测试内容",
                "category": "国内新闻",
                "publish_date": "2026-01-26",
                "created_at": "2026-01-26T00:00:00"
            }
        ]
        
        mock_int_news.return_value = [
            {
                "id": 101,
                "title": "国际测试新闻",
                "content": "测试内容",
                "category": "国际新闻",
                "publish_date": "2026-01-26",
                "created_at": "2026-01-26T00:00:00"
            }
        ]
        
        # 测试实时新闻获取
        news_list = get_real_time_news()
        self.assertIsInstance(news_list, list)
        self.assertEqual(len(news_list), 2)
        
        # 检查是否生成了新闻文件
        self.assertTrue(os.path.exists('news.json'))
    
    @patch('app.get_real_time_news')
    def test_generate_news_content(self, mock_get_news):
        """测试新闻邮件内容生成功能"""
        # 模拟新闻数据
        mock_get_news.return_value = [
            {
                "id": 1,
                "title": "测试新闻",
                "content": "测试内容",
                "category": "国内新闻",
                "publish_date": "2026-01-26",
                "created_at": "2026-01-26T00:00:00"
            }
        ]
        
        # 测试邮件内容生成
        content = generate_news_content()
        self.assertIsInstance(content, str)
        self.assertIn('今日新闻', content)
        self.assertIn('国内新闻', content)
        self.assertIn('测试新闻', content)

if __name__ == '__main__':
    unittest.main()
