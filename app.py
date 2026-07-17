import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# HTML Interface (Form Design)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Bulk Email Sender</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .container { max-width: 600px; background: white; margin: 30px auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h2 { color: #333; text-align: center; margin-bottom: 20px; }
        label { font-weight: 600; color: #555; display: block; margin-top: 15px; margin-bottom: 5px; }
        input[type="email"], input[type="password"], input[type="text"], textarea { 
            width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px;
        }
        textarea { resize: vertical; }
        .hint { font-size: 12px; color: #777; margin-top: 2px; }
        button { width: 100%; background-color: #007bff; color: white; border: none; padding: 12px; font-size: 16px; border-radius: 4px; cursor: pointer; margin-top: 20px; font-weight: bold; }
        button:hover { background-color: #0056b3; }
        .result { margin-top: 20px; padding: 15px; border-radius: 4px; display: none; font-weight: 500; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>

<div class="container">
    <h2>📧 Bulk Email Sender</h2>
    <form action="/send-email" method="POST">
        <label for="sender_email">Sender Email ID:</label>
        <input type="email" id="sender_email" name="sender_email" placeholder="example@gmail.com" required>

        <label for="app_password">App Password (16 digits):</label>
        <input type="password" id="app_password" name="app_password" placeholder="abcdefghijklmnop" required>
        <div class="hint">Gmail ka 16-digit App Password dalein (bina spaces ke).</div>

        <label for="receiver_emails">Receiver Emails (Line by Line):</label>
        <textarea id="receiver_emails" name="receiver_emails" rows="5" placeholder="user1@gmail.com&#10;user2@gmail.com&#10;user3@gmail.com" required></textarea>
        <div class="hint">Har ek email id ko nayi line (Enter daba kar) me likhein.</div>

        <label for="subject">Subject Line:</label>
        <input type="text" id="subject" name="subject" placeholder="Enter email subject" required>

        <label for="message">Message:</label>
        <textarea id="message" name="message" rows="5" placeholder="Write your email content here..." required></textarea>

        <button type="submit">Send Emails Now 🚀</button>
    </form>
</div>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send-email', methods=['POST'])
def send_email():
    # Form se data nikalna
    sender_email = request.form.get("sender_email")
    app_password = request.form.get("app_password").replace(" ", "") # Agar user space daal de toh delete ho jaye
    receiver_emails_raw = request.form.get("receiver_emails")
    subject = request.form.get("subject")
    body = request.form.get("message")

    # Line by line emails ko list me convert karna aur khali lines hatana
    receiver_list = [email.strip() for email in receiver_emails_raw.split('\n') if email.strip()]

    success_count = 0
    failed_emails = []

    try:
        # SMTP Server setup
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)

        # Loop chala kar sabhi ko alag-alag mail bhejna
        for receiver in receiver_list:
            try:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = receiver
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                
                server.sendmail(sender_email, receiver, msg.as_string())
                success_count += 1
            except Exception as e:
                failed_emails.append(f"{receiver} (Error: {str(e)})")

        server.quit()

        # Final Response screen par dikhane ke liye
        if len(failed_emails) == 0:
            return f"<div style='text-align:center; margin-top:50px; font-family:sans-serif;'><h2>✅ Success! All {success_count} emails sent successfully.</h2><a href='/'>Go Back</a></div>"
        else:
            return f"<div style='text-align:center; margin-top:50px; font-family:sans-serif;'><h2>⚠️ Partial Success! {success_count} sent, but failed for:</h2><p>{', '.join(failed_emails)}</p><a href='/'>Go Back</a></div>"

    except Exception as e:
        return f"<div style='text-align:center; margin-top:50px; font-family:sans-serif; color:red;'><h2>❌ Login Failed!</h2><p>{str(e)}</p><p>Kripya check karein ki Email aur App Password sahi hai ya nahi.</p><a href='/'>Go Back</a></div>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
