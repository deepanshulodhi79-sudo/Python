import os
import smtplib
import time
from email.utils import make_msgid, formatdate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Inbox-Delivery Email Sender</title>
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
        button { width: 100%; background-color: #28a745; color: white; border: none; padding: 12px; font-size: 16px; border-radius: 4px; cursor: pointer; margin-top: 20px; font-weight: bold; }
        button:hover { background-color: #218838; }
        button:disabled { background-color: #6c757d; cursor: not-allowed; }
        .result { margin-top: 20px; padding: 15px; border-radius: 4px; display: none; font-weight: 500; text-align: center; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; display: block; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; display: block; }
    </style>
</head>
<body>

<div class="container">
    <h2>📧 Inbox-Delivery Email Sender</h2>
    <form id="emailForm">
        <label for="sender_email">Sender Email ID:</label>
        <input type="email" id="sender_email" name="sender_email" placeholder="example@gmail.com" required>

        <label for="app_password">App Password (16 digits):</label>
        <input type="password" id="app_password" name="app_password" placeholder="abcdefghijklmnop" required>
        <div class="hint">Gmail ka 16-digit App Password dalein (bina spaces ke).</div>

        <label for="receiver_emails">Receiver Emails (Line by Line):</label>
        <textarea id="receiver_emails" name="receiver_emails" rows="5" placeholder="user1@gmail.com&#10;user2@gmail.com" required></textarea>
        <div class="hint">Har ek email id ko nayi line me likhein.</div>

        <label for="subject">Subject Line:</label>
        <input type="text" id="subject" name="subject" placeholder="Enter clear, non-spammy subject" required>

        <label for="message">Message:</label>
        <textarea id="message" name="message" rows="5" placeholder="Write natural conversation style text..." required></textarea>

        <button type="submit" id="submitBtn">Send Emails Now 🚀</button>
    </form>

    <!-- Bina page refresh ke result dikhane ke liye dynamic box -->
    <div id="resultBox" class="result"></div>
</div>

<script>
document.getElementById('emailForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // Page refresh ko rokne ke liye
    
    const submitBtn = document.getElementById('submitBtn');
    const resultBox = document.getElementById('resultBox');
    
    // UI Update for sending state
    submitBtn.disabled = true;
    submitBtn.innerText = "Sending... Please wait ⏳";
    resultBox.style.display = 'none';
    resultBox.className = 'result';

    const formData = new FormData(this);

    try {
        const response = await fetch('/send-email', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        resultBox.style.display = 'block';
        if (data.status === 'success') {
            resultBox.classList.add('success');
            resultBox.innerText = data.message;
        } else {
            resultBox.classList.add('error');
            resultBox.innerText = data.message;
        }
    } catch (error) {
        resultBox.style.display = 'block';
        resultBox.classList.add('error');
        resultBox.innerText = "Network error! Server se connect nahi ho paya.";
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Send Emails Now 🚀";
    }
});
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send-email', methods=['POST'])
def send_email():
    sender_email = request.form.get("sender_email")
    app_password = request.form.get("app_password").replace(" ", "")
    receiver_emails_raw = request.form.get("receiver_emails")
    subject = request.form.get("subject")
    body = request.form.get("message")

    receiver_list = [email.strip() for email in receiver_emails_raw.split('\n') if email.strip()]

    success_count = 0
    failed_emails = []

    try:
        # SMTP Session open
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)

        for receiver in receiver_list:
            try:
                # Anti-Spam Headers Integration
                msg = MIMEMultipart('alternative')
                msg['From'] = sender_email
                msg['To'] = receiver
                msg['Subject'] = subject
                msg['Date'] = formatdate(localtime=True)
                msg['Message-ID'] = make_msgid(domain=sender_email.split('@')[-1])
                
                # Standard headers jo email filters ko real lagte hain
                msg['X-Mailer'] = 'Python-SMTPLib-Client'
                msg['MIME-Version'] = '1.0'

                # Attach Plain Text
                msg.attach(MIMEText(body, 'plain'))
                
                # Mail Sending
                server.sendmail(sender_email, receiver, msg.as_string())
                success_count += 1
                
                # 1-second ka pause taaki Gmail filters ko lagy ki koi human bhej raha hai (Anti-spam tactic)
                time.sleep(1)
                
            except Exception as e:
                failed_emails.append(receiver)

        server.quit()

        if len(failed_emails) == 0:
            return jsonify({"status": "success", "message": f"✅ Sabhi {success_count} emails kamyabi se bhej diye gaye!"})
        else:
            return jsonify({"status": "error", "message": f"⚠️ {success_count} bheje gaye, lekin inpar fail hua: {', '.join(failed_emails)}"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ Login Failed! Password ya Email galat hai. Error: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
