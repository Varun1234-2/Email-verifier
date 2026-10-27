# Email Verifier Web App

This is a lightweight web application that checks a list of email addresses to determine if they are likely to be delivered, bounce, or if their status is unknown. 

## How It Works
1. **Format Validation:** Uses Regular Expressions to ensure the string is a valid email format.
2. **Domain Validation:** Queries the DNS to check if the domain has a valid Mail Exchange (MX) record.
3. **Mailbox Validation:** Connects to the mail server via SMTP and sends an `RCPT TO` command. It reads the server's response code (250 for success, 550 for not found) and then quits the connection *without* actually sending an email payload.

## Important Note on "Unknown" Results and Hosting Limitations
Many modern mail servers are configured as "catch-all" servers or actively obfuscate mailbox existence to prevent spam harvesting. In these cases, the server will not give a definitive 250 or 550 response, resulting in an **"unknown"** status. 

Furthermore, when deploying this application to cloud platforms (like Render, Railway, or PythonAnywhere), the **SMTP connection might return "unknown" due to platform restrictions**. Most cloud hosting providers block outbound traffic on Port 25 by default to prevent spam abuse. If the application cannot reach the mail server due to these network blocks, it will gracefully catch the timeout exception and label the email as "unknown" rather than crashing.