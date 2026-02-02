# 新闻订阅系统

一个基于 Flask 的新闻订阅和推送系统，支持用户订阅新闻、定时发送新闻邮件、查看最新新闻等功能。

## 功能特点

- ✅ **新闻爬取**：自动爬取新浪新闻的国内新闻
- ✅ **国际新闻**：通过 NewsAPI 获取国际新闻
- ✅ **邮件订阅**：用户可以通过邮箱订阅新闻
- ✅ **定时推送**：每天早上9:00自动发送新闻邮件
- ✅ **手动发送**：支持手动触发发送新闻邮件
- ✅ **实时查看**：前端页面可以实时查看新闻内容
- ✅ **分类展示**：新闻按分类（国内新闻、国际新闻）展示
- ✅ **详细日志**：完整的操作和错误日志记录

## 技术栈

- **后端**：Python 3.13, Flask
- **前端**：HTML5, CSS3, JavaScript
- **定时任务**：APScheduler
- **网络请求**：Requests
- **HTML解析**：BeautifulSoup4
- **邮件发送**：SMTP
- **数据存储**：JSON文件
- **部署**：Gunicorn (生产环境)

## 项目结构

```
news-subscription-system/
├── __pycache__/         # Python 编译缓存
├── templates/           # 前端模板
│   └── index.html       # 主页面
├── app.py               # 主应用文件
├── app.log              # 应用日志
├── config.json          # 配置文件
├── news.json            # 新闻数据存储
├── requirements.txt     # 依赖包列表
├── send_news.py         # 新闻发送脚本
├── subscribers.json     # 订阅用户存储
├── test.log             # 测试日志
├── test_email.py        # 邮件测试脚本
├── test_flask.py        # Flask 测试脚本
└── test_news_system.py  # 系统测试脚本
```

## 安装和运行

### 1. 克隆项目

```bash
git clone <repository-url>
cd news-subscription-system
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置修改

编辑 `config.json` 文件，修改以下配置：

```json
{
  "email": {
    "smtp_server": "smtp.qq.com",      # SMTP服务器地址
    "smtp_port": 465,                    # SMTP服务器端口
    "sender_email": "your-email@qq.com", # 发件人邮箱
    "sender_password": "your-password",  # 邮箱授权码
    "subject": "每日新闻"                 # 邮件主题
  },
  "news_api": {
    "api_key": "your-newsapi-key"        # NewsAPI API Key
  },
  "schedule": {
    "hour": 9,                           # 定时发送小时
    "minute": 0                           # 定时发送分钟
  }
}
```

> **注意**：
> - `sender_password` 不是邮箱登录密码，而是邮箱的授权码
> - `api_key` 是从 [NewsAPI](https://newsapi.org/) 获取的 API Key

### 4. 运行项目

#### 开发环境

```bash
python app.py
```

服务将在 `http://127.0.0.1:5000` 运行

#### 生产环境

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API 接口

### 1. 订阅接口

- **URL**: `/subscribe`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **响应**:
  ```json
  {
    "status": "success",
    "message": "订阅成功"
  }
  ```

### 2. 取消订阅接口

- **URL**: `/unsubscribe`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **响应**:
  ```json
  {
    "status": "success",
    "message": "取消订阅成功"
  }
  ```

### 3. 获取新闻列表接口

- **URL**: `/get-news`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "status": "success",
    "news": [
      {
        "id": 1,
        "title": "新闻标题",
        "content": "<a href='https://news-url'>查看详情</a>",
        "category": "国内新闻",
        "publish_date": "2026-02-02",
        "created_at": "2026-02-02T15:00:00"
      }
    ]
  }
  ```

### 4. 手动发送邮件接口

- **URL**: `/send-news`
- **方法**: `POST`
- **响应**:
  ```json
  {
    "status": "success",
    "message": "邮件发送成功！"
  }
  ```

## 前端功能

访问 `http://127.0.0.1:5000` 可以使用以下功能：

1. **订阅新闻**：输入邮箱地址，点击"订阅"按钮
2. **立即发送新闻**：点击"立即发送新闻"按钮，手动触发新闻发送
3. **查看新闻内容**：点击"查看新闻内容"按钮，在页面上查看最新新闻

## 定时任务

系统会在每天早上 **9:00** 自动执行以下任务：

1. 爬取最新的新浪新闻
2. 获取国际新闻（如果配置了 NewsAPI）
3. 生成新闻邮件内容
4. 向所有活跃订阅用户发送新闻邮件

## 数据存储

- **subscribers.json**：存储订阅用户信息
- **news.json**：存储爬取的新闻数据
- **app.log**：应用运行日志

## 测试

项目包含以下测试脚本：

- `test_email.py`：测试邮件发送功能
- `test_flask.py`：测试 Flask 应用接口
- `test_news_system.py`：测试整个新闻系统

运行测试：

```bash
python test_email.py
python test_flask.py
python test_news_system.py
```

## 部署指南

### Vercel 部署

#### 步骤 1: 准备工作

1. **创建 Vercel 账户**：访问 [Vercel](https://vercel.com/) 注册并登录
2. **安装 Vercel CLI**：
   ```bash
   npm install -g vercel
   ```
3. **创建 vercel.json 配置文件**：
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ],
     "env": {
       "FLASK_ENV": "production"
     }
   }
   ```

#### 步骤 2: 部署到 Vercel

```bash
# 登录 Vercel
vercel login

# 初始化项目
vercel init

# 部署项目
vercel --prod
```

#### Vercel 部署失败的常见原因及解决方案

| 失败原因 | 解决方案 |
|---------|----------|
| 缺少 Python 依赖 | 确保 `requirements.txt` 文件包含所有必需的依赖 |
| 端口配置问题 | Vercel 使用随机端口，确保 Flask 应用使用 `PORT` 环境变量 |
| 静态文件路径 | 确保 `templates` 目录正确配置 |
| 内存限制 | Vercel 免费版有内存限制，优化代码减少内存使用 |
| 运行时间限制 | Vercel 函数有运行时间限制，避免长时间运行的任务 |
| 环境变量配置 | 使用 Vercel 的环境变量功能配置敏感信息 |

#### 解决 Vercel 部署问题的具体措施

1. **修改 app.py 以支持 Vercel**：
   ```python
   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 5000))
       app.run(debug=False, host='0.0.0.0', port=port)
   ```

2. **添加 .vercelignore 文件**：
   ```
   __pycache__/
   *.pyc
   *.log
   ```

3. **使用环境变量存储敏感信息**：
   - 在 Vercel 控制台的项目设置中添加环境变量
   - 修改配置加载逻辑以支持环境变量

### 其他部署选项

#### 1. 云服务器部署

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py

# 或使用 Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 2. Docker 部署

创建 `Dockerfile`：
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

构建和运行：
```bash
docker build -t news-subscription-system .
docker run -p 5000:5000 news-subscription-system
```

### 部署后日志查看

#### 1. Vercel 日志

- **Web 控制台**：登录 Vercel → 选择项目 → 查看 "Logs" 标签页
- **CLI 命令**：
  ```bash
  vercel logs
  ```

#### 2. 本地服务器日志

- **应用日志**：查看 `app.log` 文件
  ```bash
  tail -f app.log
  ```
- **系统日志**：根据服务器类型查看相应的系统日志

#### 3. Docker 容器日志

```bash
docker logs <container-id>
```

### 部署最佳实践

1. **使用环境变量**：避免在代码中硬编码敏感信息
2. **配置 HTTPS**：生产环境必须使用 HTTPS
3. **设置合理的日志级别**：避免日志过大
4. **定期备份数据**：特别是订阅用户数据
5. **监控应用状态**：使用监控工具确保应用正常运行
6. **使用 CDN**：加速静态资源访问
7. **配置防火墙**：限制不必要的端口访问

## 注意事项

1. **邮箱配置**：
   - 请确保使用正确的 SMTP 服务器地址和端口
   - 发件人邮箱需要开启 SMTP 服务并获取授权码
   - QQ 邮箱的授权码获取方式：设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务 → 开启 SMTP 服务 → 获取授权码

2. **NewsAPI 配置**：
   - 国际新闻功能需要在 [NewsAPI](https://newsapi.org/) 注册并获取 API Key
   - 免费版 API Key 有请求次数限制

3. **生产环境部署**：
   - 使用 Gunicorn 作为 WSGI 服务器
   - 建议使用 Nginx 作为反向代理
   - 配置适当的日志轮转

4. **数据安全**：
   - 配置文件中的邮箱密码和 API Key 属于敏感信息
   - 生产环境建议使用环境变量或密钥管理服务

## 常见问题

### Q: 邮件发送失败怎么办？

A: 检查以下几点：
- SMTP 服务器地址和端口是否正确
- 发件人邮箱和授权码是否正确
- 网络连接是否正常
- 查看 app.log 中的错误信息

### Q: 国际新闻不显示怎么办？

A: 检查以下几点：
- NewsAPI API Key 是否正确配置
- API Key 是否过期
- 网络连接是否正常

### Q: 定时任务不执行怎么办？

A: 检查以下几点：
- 应用是否正常运行
- 服务器时间是否正确
- 查看 app.log 中的定时任务执行日志

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，欢迎联系项目维护者。