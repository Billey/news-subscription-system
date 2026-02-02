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

app = Flask(__name__)

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 加载配置
def load_config():
    config_path = os.path.join(PROJECT_ROOT, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载订阅用户
def load_subscribers():
    try:
        subscribers_path = os.path.join(PROJECT_ROOT, 'subscribers.json')
        with open(subscribers_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"subscribers": []}

# 保存订阅用户
def save_subscribers(data):
    subscribers_path = os.path.join(PROJECT_ROOT, 'subscribers.json')
    with open(subscribers_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 保存新闻内容
def save_news(news_data):
    news_path = os.path.join(PROJECT_ROOT, 'news.json')
    with open(news_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)

# 发送邮件
def send_email(to_email, subject, content):
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
        print(f"正在连接SMTP服务器: {smtp_server}:{smtp_port}")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
        print("连接成功，正在登录...")
        server.login(sender_email, sender_password)
        print("登录成功，正在发送邮件...")
        server.send_message(msg)
        print("邮件发送成功")
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        print("邮件发送失败: 认证错误，请检查邮箱账号和密码")
        return False
    except smtplib.SMTPConnectError:
        print("邮件发送失败: 连接错误，请检查SMTP服务器地址和端口")
        return False
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

# 爬取新浪新闻
def crawl_sina_news():
    try:
        url = "https://news.sina.com.cn/china/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        # 解析新闻
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
        
        return news_list
    except Exception as e:
        print(f"新浪新闻爬取失败: {e}")
        return []

# 使用NewsAPI获取国际新闻
def get_international_news():
    try:
        config = load_config()
        api_key = config.get('news_api', {}).get('api_key')
        
        if not api_key:
            return []
        
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "apiKey": api_key,
            "pageSize": 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
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
        
        return news_list
    except Exception as e:
        print(f"国际新闻获取失败: {e}")
        return []

# 获取实时新闻
def get_real_time_news():
    # 获取国内新闻
    sina_news = crawl_sina_news()
    
    # 获取国际新闻
    international_news = get_international_news()
    
    # 合并新闻
    all_news = sina_news + international_news
    
    # 保存新闻
    news_data = {
        "news": all_news,
        "last_updated": datetime.datetime.now().isoformat()
    }
    save_news(news_data)
    
    return all_news

# 生成新闻邮件内容
def generate_news_content():
    # 先获取最新新闻
    news_list = get_real_time_news()
    
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
    
    # 生成分类新闻内容
    for category, news_items in categories.items():
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
    
    return content

# 定时发送新闻
def send_daily_news():
    subscribers = load_subscribers()
    config = load_config()
    
    for subscriber in subscribers.get('subscribers', []):
        if subscriber['status'] == 'active':
            content = generate_news_content()
            subject = f"{config['email']['subject']} - {datetime.datetime.now().strftime('%Y-%m-%d')}"
            send_email(subscriber['email'], subject, content)

# 订阅接口
@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({"status": "error", "message": "邮箱不能为空"}), 400
    
    subscribers = load_subscribers()
    
    # 检查是否已订阅
    for subscriber in subscribers['subscribers']:
        if subscriber['email'] == email:
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
    send_email(email, "订阅确认", content)
    
    return jsonify({"status": "success", "message": "订阅成功"}), 200

# 取消订阅接口
@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.json
    email = data.get('email')
    
    if not email:
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
        return jsonify({"status": "error", "message": "该邮箱未订阅"}), 400
    
    save_subscribers(subscribers)
    return jsonify({"status": "success", "message": "取消订阅成功"}), 200

# 手动发送邮件接口
@app.route('/send-news', methods=['POST'])
def send_news_manual():
    try:
        send_daily_news()
        return jsonify({"status": "success", "message": "邮件发送成功！"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"邮件发送失败: {str(e)}"}), 500

# 前端页面
@app.route('/')
def index():
    return render_template('index.html')

# 启动定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_news, 'cron', hour=9, minute=0)  # 每天早上9:00发送
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)