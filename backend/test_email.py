"""
Test Email Configuration
Run this to test if email sending is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get email configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))

print("=" * 60)
print("EMAIL CONFIGURATION TEST")
print("=" * 60)
print(f"SMTP Host: {SMTP_HOST}")
print(f"SMTP Port: {SMTP_PORT}")
print(f"Email Address: {EMAIL_ADDRESS}")
print(f"Password Set: {'Yes' if EMAIL_PASSWORD else 'No'}")
print(f"Password Length: {len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 0}")
print("=" * 60)

# Check if credentials are set
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    print("\n❌ ERROR: Email credentials not configured!")
    print("\nPlease set the following in .env file:")
    print("EMAIL_ADDRESS=your-email@gmail.com")
    print("EMAIL_PASSWORD=your-app-password")
    sys.exit(1)

# Check if email address looks valid
if "your-" in EMAIL_ADDRESS or "@" not in EMAIL_ADDRESS:
    print("\n⚠️  WARNING: Email address looks like a placeholder!")
    print(f"Current value: {EMAIL_ADDRESS}")
    print("\nPlease update EMAIL_ADDRESS in .env with your actual Gmail address")
    sys.exit(1)

# Test SMTP connection
print("\n🔄 Testing SMTP connection...")
try:
    import smtplib
    
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    
    print("✅ SMTP connection successful!")
    print("🔄 Testing authentication...")
    
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    print("✅ Authentication successful!")
    
    server.quit()
    
    print("\n" + "=" * 60)
    print("✅ EMAIL CONFIGURATION IS WORKING!")
    print("=" * 60)
    print("\nYou can now send emails from the application.")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentication failed: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Make sure 2-Step Verification is enabled on your Google account")
    print("2. Generate an App Password:")
    print("   - Go to: https://myaccount.google.com/apppasswords")
    print("   - Create a new app password for 'EduNexa LMS'")
    print("   - Copy the 16-character password")
    print("   - Update EMAIL_PASSWORD in .env file")
    sys.exit(1)
    
except smtplib.SMTPException as e:
    print(f"\n❌ SMTP error: {e}")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    sys.exit(1)
