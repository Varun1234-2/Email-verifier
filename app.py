from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import re
import dns.resolver
import smtplib
import concurrent.futures # This allows us to do multiple things at once!

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    # Serves the HTML frontend
    return send_file('index.html')

def verify_email(email):
    # Step 1: Format check
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return {"email": email, "status": "likely to bounce"}

    domain = email.split('@')[1]

    # Step 2: Domain MX check
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
    except Exception:
        return {"email": email, "status": "likely to bounce"}

    # Step 3: Mailbox check
    try:
        server = smtplib.SMTP(mx_record, 25, timeout=3)
        server.helo(server.local_hostname) 
        server.mail('test@example.com') 
        
        code, message = server.rcpt(email) 
        server.quit()

        if code == 250:
            return {"email": email, "status": "likely to be delivered"}
        elif code == 550:
            return {"email": email, "status": "likely to bounce"}
        else:
            return {"email": email, "status": "unknown"}
            
    except Exception:
        return {"email": email, "status": "unknown"}

@app.route('/check-emails', methods=['POST'])
def check_emails():
    data = request.json
    # Get the list and filter out any empty lines
    email_list = [e.strip() for e in data.get('emails', []) if e.strip()]
    
    results = []
    
    # SPEED FIX: We create a "pool" of 10 workers. 
    # Instead of checking one by one, 10 emails are checked simultaneously.
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 'executor.map' runs the 'verify_email' function for every email in our list in parallel
        # and gathers all the results back into a list.
        results = list(executor.map(verify_email, email_list))
            
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)