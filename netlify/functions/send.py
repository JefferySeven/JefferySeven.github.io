import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json
import os

def handler(event, context):
    """
    Vercel 或 Serverless 环境下的云函数
    接收来自简历网站的留言并发送到 QQ 邮箱
    """

    # 允许跨域请求 (CORS)
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    # 处理 OPTIONS 预检请求
    if event.get("httpMethod") == "OPTIONS" or event.get("method") == "OPTIONS":
        return {
            "statusCode": 204,
            "headers": headers,
            "body": ""
        }

    try:
        # 1. 解析前端发来的 JSON 数据
        body_str = event.get('body', '{}')
        if not body_str:
            body_str = '{}'

        body = json.loads(body_str)

        name = body.get('name', '访客')
        visitor_email = body.get('email', '未提供')
        message_content = body.get('message', '无内容')

        # 2. 邮箱配置 (从环境变量读取，安全)
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.qq.com")
        sender_email = os.environ.get("SENDER_EMAIL", "")  # 必须在 Netlify 环境变量配置
        auth_code = os.environ.get("SMTP_AUTH_CODE", "")   # 必须在 Netlify 环境变量配置
        receiver_email = os.environ.get("RECEIVER_EMAIL", sender_email)

        if not sender_email or not auth_code:
             raise Exception("服务端未配置邮箱环境变量 (SMTP_AUTH_CODE 或 SENDER_EMAIL)，请在 Netlify 后台配置。")

        # 3. 构造邮件
        mail_text = f"""
        简历网站收到新留言：
        --------------------------------
        姓名：{name}
        对方邮箱：{visitor_email}
        消息内容：{message_content}
        --------------------------------
        发送时间：自动生成
        """

        msg = MIMEText(mail_text, 'plain', 'utf-8')
        msg['From'] = Header(f"网站访客 <{sender_email}>", 'utf-8')
        msg['To'] = Header("宋亦涵", 'utf-8')
        msg['Subject'] = Header(f"📩 简历网站新留言: {name}", 'utf-8')

        # 4. 执行发送
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(sender_email, auth_code)
        server.sendmail(sender_email, [receiver_email], msg.as_string())
        server.quit()

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"status": "success", "message": "已发送到邮箱"})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"status": "error", "message": str(e)})
        }
