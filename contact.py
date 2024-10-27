from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from dotenv import load_dotenv # type: ignore
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Email configuration
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
FROM_EMAIL = os.getenv('FROM_EMAIL')
TO_EMAIL = os.getenv('TO_EMAIL')

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_email(name, email, message):
    """Send email using SMTP"""
    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'New Contact Form Message from {name}'
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL

    # Create HTML version of message
    html = f"""
    <html>
        <body>
            <h2>New Contact Form Submission</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Message:</strong></p>
            <p>{message.replace(chr(10), '<br>')}</p>
        </body>
    </html>
    """

    # Create plain text version of message
    text = f"""
    New Contact Form Submission

    Name: {name}
    Email: {email}
    Message:
    {message}
    """

    # Attach parts
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # Send email
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        name = data['name']
        email = data['email']
        message = data['message']

        # Validate email format
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Validate message length
        if len(message) < 10:
            return jsonify({'error': 'Message must be at least 10 characters long'}), 400

        # Send email
        send_email(name, email, message)

        return jsonify({'message': 'Message sent successfully'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Log error (replace with proper logging)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False)