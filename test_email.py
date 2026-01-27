import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import send_email

def main():
    print("测试邮件发送功能...")
    
    # 简单的测试邮件内容
    test_content = """
    <html>
    <body>
        <h2>测试邮件</h2>
        <p>这是一封测试邮件，用于验证邮件发送功能是否正常。</p>
        <p>如果您收到了这封邮件，说明邮件发送功能工作正常。</p>
    </body>
    </html>
    """
    
    try:
        result = send_email('1093926117@qq.com', '测试邮件', test_content)
        if result:
            print("✅ 测试邮件发送成功！")
        else:
            print("❌ 测试邮件发送失败！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    main()
