from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
def setup_database():
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE,
                  subscribed_at TIMESTAMP)''')
    conn.commit()
    conn.close()

# Email configuration
EMAIL_HOST = "smtp.yourserver.com"
EMAIL_PORT = 587
EMAIL_USER = "your-email@domain.com"
EMAIL_PASSWORD = "your-email-password"

def send_confirmation_email(subscriber_email):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = subscriber_email
    msg['Subject'] = "Welcome to Maze Quiz Corp Magazine!"

    body = """
    Thank you for subscribing to Maze Quiz Corp Magazine!
    
    You're now part of our community of curious minds. You'll receive our latest stories,
    features, and in-depth analysis straight to your inbox.
    
    Your first magazine edition will arrive shortly.
    
    Best regards,
    The Maze Quiz Corp Team
    """
    
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        # Store in database
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute("INSERT INTO subscribers (email, subscribed_at) VALUES (?, ?)",
                 (email, datetime.now()))
        conn.commit()
        conn.close()
        
        # Send confirmation email
        if send_confirmation_email(email):
            return jsonify({
                'success': True,
                'message': 'Successfully subscribed!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Subscription successful but confirmation email failed to send.'
            }), 500
            
    except sqlite3.IntegrityError:
        return jsonify({
            'success': False,
            'message': 'This email is already subscribed.'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)