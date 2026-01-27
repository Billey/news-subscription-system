import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import send_daily_news

def main():
    print("开始发送新闻邮件...")
    try:
        send_daily_news()
        print("✅ 新闻邮件发送成功！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    main()
