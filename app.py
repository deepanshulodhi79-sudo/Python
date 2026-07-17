import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Email Sender API is running! Go to /send-email to send the mail."

@app.route('/send-email')
def send_email():
    # Render dashboard se secure details uthane ke liye
    sender_email = os.environ.get("SENDER_EMAIL")
    app_password = os.environ.get("APP_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    
    # Agar Render me details nahi dali toh error dikhayega
    if not sender_email or not app_password or not receiver_email:
        return jsonify({"status": "error", "message": "Environment variables missing on Render!"}), 400

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Hosted Python Test Mail"
    
    body = "Hello! Ye mail Render par host ki gayi Python script se bheja gaya hai."
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        return jsonify({"status": "success", "message": f"Mail successfully sent to {receiver_email}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Render ke liye port configure karna zaroori hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
