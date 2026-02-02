from flask import Flask, request, jsonify, render_template
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import requests
from bs4 import BeautifulSoup
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 加载配置
def load_config():
    config_path = os.path.join(PROJECT_ROOT, 'config.json')
    logger.info(f"加载配置文件: {config_path}")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info("配置文件加载成功")
        return config
    except Exception as e:
        logger.error(f"配置文件加载失败: {e}")
        raise

# 加载订阅用户
def load_subscribers():
    subscribers_path = os.path.join(PROJECT_ROOT, 'subscribers.json')
    logger.info(f"加载订阅用户文件: {subscribers_path}")
    try:
        with open(subscribers_path, 'r', encoding='utf-8') as f:
            subscribers = json.load(f)
        logger.info(f"订阅用户加载成功，共 {len(subscribers.get('subscribers', []))} 个用户")
        return subscribers
    except Exception as e:
        logger.warning(f"订阅用户文件加载失败: {e}，返回空列表")
        return {"subscribers": []}

# 保存订阅用户
def save_subscribers(data):
    subscribers_path = os.path.join(PROJECT_ROOT, 'subscribers.json')
    logger.info(f"保存订阅用户到文件: {subscribers_path}")
    try:
        with open(subscribers_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"订阅用户保存成功，共 {len(data.get('subscribers', []))} 个用户")
    except Exception as e:
        logger.error(f"订阅用户保存失败: {e}")
        raise

# 保存新闻内容
def save_news(news_data):
    news_path = os.path.join(PROJECT_ROOT, 'news.json')
    logger.info(f"保存新闻内容到文件: {news_path}")
    try:
        with open(news_path, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        logger.info(f"新闻内容保存成功，共 {len(news_data.get('news', []))} 条新闻")
    except Exception as e:
        logger.error(f"新闻内容保存失败: {e}")
        raise

# 发送邮件
def send_email(to_email, subject, content):
    logger.info(f"准备发送邮件到: {to_email}，主题: {subject}")
    config = load_config()    
    smtp_server = config['email']['smtp_server']
    smtp_port = config['email']['smtp_port']
    sender_email = config['email']['sender_email']
    sender_password = config['email']['sender_password']
    
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    html_part = MIMEText(content, 'html', 'utf-8')
    msg.attach(html_part)
    
    try:
        logger.info(f"正在连接SMTP服务器: {smtp_server}:{smtp_port}")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
        logger.info("连接SMTP服务器成功")
        
        logger.info("正在登录SMTP服务器...")
        server.login(sender_email, sender_password)
        logger.info("登录SMTP服务器成功")
        
        logger.info("正在发送邮件...")
        server.send_message(msg)
        logger.info(f"邮件发送成功到: {to_email}")
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("邮件发送失败: 认证错误，请检查邮箱账号和密码")
        return False
    except smtplib.SMTPConnectError:
        logger.error("邮件发送失败: 连接错误，请检查SMTP服务器地址和端口")
        return False
    except Exception as e:
        logger.error(f"邮件发送失败: {e}")
        return False

# 爬取新浪新闻
def crawl_sina_news():
    logger.info("开始爬取新浪新闻...")
    try:
        url = "https://news.sina.com.cn/china/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        logger.info(f"请求URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        logger.info(f"响应状态码: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        # 解析新闻
        logger.info("开始解析新闻...")
        for item in soup.select('.news-item'):
            title_elem = item.select_one('h2 a') or item.select_one('a')
            time_elem = item.select_one('.time')
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href')
                time = time_elem.get_text(strip=True) if time_elem else datetime.datetime.now().strftime('%Y-%m-%d')
                
                news_list.append({
                    "id": len(news_list) + 1,
                    "title": title,
                    "content": f"<a href='{link}'>查看详情</a>",
                    "category": "国内新闻",
                    "publish_date": time,
                    "created_at": datetime.datetime.now().isoformat()
                })
                
                if len(news_list) >= 10:  # 限制新闻数量
                    break
        
        logger.info(f"新浪新闻爬取完成，共获取 {len(news_list)} 条新闻")
        return news_list
    except Exception as e:
        logger.error(f"新浪新闻爬取失败: {e}")
        return []

# 使用NewsAPI获取国际新闻
def get_international_news():
    logger.info("开始获取国际新闻...")
    try:
        config = load_config()
        api_key = config.get('news_api', {}).get('api_key')
        
        if not api_key:
            logger.warning("NewsAPI API Key 未配置，跳过国际新闻获取")
            return []
        
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "apiKey": api_key,
            "pageSize": 5
        }
        
        logger.info(f"请求NewsAPI URL: {url}")
        logger.info(f"请求参数: country=us, pageSize=5")
        response = requests.get(url, params=params, timeout=10)
        logger.info(f"响应状态码: {response.status_code}")
        
        data = response.json()
        logger.info(f"NewsAPI响应: {data.get('status')}, 共 {data.get('totalResults', 0)} 条新闻")
        
        news_list = []
        for article in data.get('articles', []):
            news_list.append({
                "id": len(news_list) + 100,  # 避免ID冲突
                "title": article['title'],
                "content": article['description'] or f"<a href='{article['url']}'>查看详情</a>",
                "category": "国际新闻",
                "publish_date": article['publishedAt'].split('T')[0],
                "created_at": datetime.datetime.now().isoformat()
            })
        
        logger.info(f"国际新闻获取完成，共获取 {len(news_list)} 条新闻")
        return news_list
    except Exception as e:
        logger.error(f"国际新闻获取失败: {e}")
        return []

# 获取实时新闻
def get_real_time_news():
    logger.info("开始获取实时新闻...")
    
    # 获取国内新闻
    logger.info("获取国内新闻...")
    sina_news = crawl_sina_news()
    
    # 获取国际新闻
    logger.info("获取国际新闻...")
    international_news = get_international_news()
    
    # 合并新闻
    all_news = sina_news + international_news
    logger.info(f"新闻合并完成，共 {len(all_news)} 条新闻")
    
    # 保存新闻
    news_data = {
        "news": all_news,
        "last_updated": datetime.datetime.now().isoformat()
    }
    save_news(news_data)
    
    logger.info("实时新闻获取完成")
    return all_news

# 生成新闻邮件内容
def generate_news_content():
    logger.info("开始生成新闻邮件内容...")
    
    # 先获取最新新闻
    logger.info("获取最新新闻数据...")
    news_list = get_real_time_news()
    logger.info(f"获取到 {len(news_list)} 条新闻")
    
    content = f"""
    <html>
    <body>
        <h2>今日新闻 ({datetime.datetime.now().strftime('%Y-%m-%d')})</h2>
        <hr>
    """
    
    # 按分类组织新闻
    categories = {}
    for news in news_list:
        category = news['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(news)
    
    logger.info(f"新闻分类完成，共 {len(categories)} 个分类")
    
    # 生成分类新闻内容
    for category, news_items in categories.items():
        logger.info(f"生成 {category} 分类内容，共 {len(news_items)} 条新闻")
        content += f"<h3>{category}</h3>"
        
        for news in news_items:
            content += f"""
            <div style="margin: 10px 0; padding: 10px; border-left: 3px solid #4CAF50;">
                <h4>{news['title']}</h4>
                <p>{news['content']}</p>
                <p><small>发布日期: {news['publish_date']}</small></p>
            </div>
            """
        
        content += "<hr>"
    
    content += """
        <p> unsubscribe: <a href="http://your-domain.com/unsubscribe">取消订阅</a></p>
    </body>
    </html>
    """
    
    logger.info("新闻邮件内容生成完成")
    return content

# 定时发送新闻
def send_daily_news():
    logger.info("开始执行定时发送新闻任务...")
    
    subscribers = load_subscribers()
    config = load_config()
    
    active_subscribers = [s for s in subscribers.get('subscribers', []) if s['status'] == 'active']
    logger.info(f"找到 {len(active_subscribers)} 个活跃订阅用户")
    
    for subscriber in active_subscribers:
        email = subscriber['email']
        logger.info(f"准备发送新闻到: {email}")
        
        try:
            content = generate_news_content()
            subject = f"{config['email']['subject']} - {datetime.datetime.now().strftime('%Y-%m-%d')}"
            logger.info(f"生成邮件主题: {subject}")
            
            success = send_email(email, subject, content)
            if success:
                logger.info(f"新闻邮件发送成功到: {email}")
            else:
                logger.warning(f"新闻邮件发送失败到: {email}")
        except Exception as e:
            logger.error(f"发送邮件到 {email} 时发生错误: {e}")
    
    logger.info("定时发送新闻任务执行完成")

# 订阅接口
@app.route('/subscribe', methods=['POST'])
def subscribe():
    logger.info("收到订阅请求")
    
    try:
        data = request.json
        logger.info(f"请求数据: {data}")
        
        email = data.get('email')
        logger.info(f"订阅邮箱: {email}")
        
        if not email:
            logger.warning("订阅失败: 邮箱不能为空")
            return jsonify({"status": "error", "message": "邮箱不能为空"}), 400
        
        subscribers = load_subscribers()
        
        # 检查是否已订阅
        for subscriber in subscribers['subscribers']:
            if subscriber['email'] == email:
                logger.warning(f"订阅失败: 邮箱 {email} 已订阅")
                return jsonify({"status": "error", "message": "该邮箱已订阅"}), 400
        
        # 添加新订阅
        new_subscriber = {
            "email": email,
            "status": "active",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        subscribers['subscribers'].append(new_subscriber)
        save_subscribers(subscribers)
        logger.info(f"订阅成功: 添加新用户 {email}")
        
        # 发送确认邮件
        content = """
        <html>
        <body>
            <h2>订阅成功</h2>
            <p>感谢您订阅我们的新闻服务，您将在每天早上收到最新的新闻资讯。</p>
            <p> unsubscribe: <a href="http://your-domain.com/unsubscribe">取消订阅</a></p>
        </body>
        </html>
        """
        logger.info(f"发送订阅确认邮件到: {email}")
        send_email(email, "订阅确认", content)
        
        logger.info(f"订阅流程完成: {email}")
        return jsonify({"status": "success", "message": "订阅成功"}), 200
    except Exception as e:
        logger.error(f"订阅接口错误: {e}")
        return jsonify({"status": "error", "message": f"订阅失败: {str(e)}"}), 500

# 取消订阅接口
@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    logger.info("收到取消订阅请求")
    
    try:
        data = request.json
        logger.info(f"请求数据: {data}")
        
        email = data.get('email')
        logger.info(f"取消订阅邮箱: {email}")
        
        if not email:
            logger.warning("取消订阅失败: 邮箱不能为空")
            return jsonify({"status": "error", "message": "邮箱不能为空"}), 400
        
        subscribers = load_subscribers()
        found = False
        
        for subscriber in subscribers['subscribers']:
            if subscriber['email'] == email:
                subscriber['status'] = 'inactive'
                subscriber['updated_at'] = datetime.datetime.now().isoformat()
                found = True
                break
        
        if not found:
            logger.warning(f"取消订阅失败: 邮箱 {email} 未订阅")
            return jsonify({"status": "error", "message": "该邮箱未订阅"}), 400
        
        save_subscribers(subscribers)
        logger.info(f"取消订阅成功: {email}")
        return jsonify({"status": "success", "message": "取消订阅成功"}), 200
    except Exception as e:
        logger.error(f"取消订阅接口错误: {e}")
        return jsonify({"status": "error", "message": f"取消订阅失败: {str(e)}"}), 500

# 获取新闻列表接口
@app.route('/get-news', methods=['GET'])
def get_news():
    logger.info("收到获取新闻列表请求")
    
    try:
        logger.info("开始获取新闻列表...")
        news_list = get_real_time_news()
        logger.info(f"获取新闻列表成功，共 {len(news_list)} 条新闻")
        return jsonify({"status": "success", "news": news_list}), 200
    except Exception as e:
        logger.error(f"获取新闻列表失败: {e}")
        return jsonify({"status": "error", "message": f"获取新闻失败: {str(e)}"}), 500

# 手动发送邮件接口
@app.route('/send-news', methods=['POST'])
def send_news_manual():
    logger.info("收到手动发送邮件请求")
    
    try:
        logger.info("开始执行手动发送邮件任务...")
        send_daily_news()
        logger.info("手动发送邮件任务执行完成")
        return jsonify({"status": "success", "message": "邮件发送成功！"}), 200
    except Exception as e:
        logger.error(f"手动发送邮件失败: {e}")
        return jsonify({"status": "error", "message": f"邮件发送失败: {str(e)}"}), 500

# 前端页面
@app.route('/')
def index():
    logger.info("收到前端页面访问请求")
    return render_template('index.html')

# 启动定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_news, 'cron', hour=9, minute=0)  # 每天早上9:00发送
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)