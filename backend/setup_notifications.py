#!/usr/bin/env python3
"""
Notification System Setup Script
Helps configure the notification system and verify setup.

Usage:
    python backend/setup_notifications.py
"""

import os
import sys
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")


def check_env_file():
    """Check if .env file exists"""
    print_header("Step 1: Check .env File")
    
    env_path = Path("backend/.env")
    
    if not env_path.exists():
        print_error(".env file not found")
        print_info("Creating .env from .env.example...")
        
        example_path = Path("backend/.env.example")
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            print_success(".env file created")
            print_info("Please edit backend/.env and add your email credentials")
            return False
        else:
            print_error(".env.example not found")
            return False
    
    print_success(".env file exists")
    return True


def check_email_config():
    """Check email configuration"""
    print_header("Step 2: Check Email Configuration")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ENABLE_EMAIL = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "true")
    ENABLE_IN_APP = os.getenv("ENABLE_IN_APP_NOTIFICATIONS", "true")
    
    all_configured = True
    
    if not EMAIL_ADDRESS or EMAIL_ADDRESS == "your-email@gmail.com":
        print_error("EMAIL_ADDRESS not configured")
        print_info("Please set EMAIL_ADDRESS in backend/.env")
        all_configured = False
    else:
        print_success(f"EMAIL_ADDRESS: {EMAIL_ADDRESS}")
    
    if not EMAIL_PASSWORD or EMAIL_PASSWORD == "your-app-password-here":
        print_error("EMAIL_PASSWORD not configured")
        print_info("Please set EMAIL_PASSWORD in backend/.env")
        print_info("See: https://myaccount.google.com/apppasswords")
        all_configured = False
    else:
        print_success(f"EMAIL_PASSWORD: {'*' * len(EMAIL_PASSWORD)}")
    
    print_info(f"Email Notifications: {ENABLE_EMAIL}")
    print_info(f"In-App Notifications: {ENABLE_IN_APP}")
    
    return all_configured


def check_mongodb():
    """Check MongoDB connection"""
    print_header("Step 3: Check MongoDB Connection")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        from pymongo import MongoClient
        
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/edunexa_lms')
        
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        print_success(f"Connected to MongoDB: {MONGO_URI}")
        
        # Check collections
        db = client.edunexa_lms
        
        users_count = db.users.count_documents({})
        print_info(f"Users in database: {users_count}")
        
        if users_count == 0:
            print_error("No users found in database")
            print_info("Please run seed scripts to create test users")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        print_info("Please ensure MongoDB is running")
        return False


def check_dependencies():
    """Check required Python packages"""
    print_header("Step 4: Check Dependencies")
    
    required_packages = [
        'flask',
        'flask_jwt_extended',
        'pymongo',
        'python-dotenv',
        'werkzeug'
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            all_installed = False
    
    if not all_installed:
        print_info("\nInstall missing packages:")
        print_info("pip install -r backend/requirements.txt")
    
    return all_installed


def test_smtp_connection():
    """Test SMTP connection"""
    print_header("Step 5: Test SMTP Connection")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print_error("Email credentials not configured")
        return False
    
    try:
        import smtplib
        
        SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        
        print_info(f"Testing connection to {SMTP_HOST}:{SMTP_PORT}...")
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        print_success("SMTP connection successful!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print_error("SMTP authentication failed")
        print_info("Please check your EMAIL_PASSWORD")
        print_info("Make sure you're using a Gmail App Password, not your regular password")
        print_info("Generate one at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print_error(f"SMTP connection failed: {e}")
        return False


def show_next_steps():
    """Show next steps"""
    print_header("Next Steps")
    
    print("\n📚 Documentation:")
    print("   - backend/NOTIFICATION_QUICK_START.md - Quick start guide")
    print("   - backend/NOTIFICATION_SYSTEM_README.md - Complete documentation")
    print("   - backend/NOTIFICATION_API_EXAMPLES.md - API examples")
    
    print("\n🧪 Testing:")
    print("   - Run automated tests:")
    print("     python backend/scripts/test_notification_system.py")
    print("   - Use interactive CLI:")
    print("     python backend/scripts/notification_cli.py")
    
    print("\n🚀 Start Backend:")
    print("   cd backend")
    print("   python run.py")
    
    print("\n📧 Test Endpoints:")
    print("   - Login: POST /api/auth/login")
    print("   - Get settings: GET /api/notification-settings")
    print("   - Send test email: POST /api/notification-settings/test-email")
    print("   - View history: GET /api/notification-history")
    
    print("\n🎓 For Viva:")
    print("   - Review backend/NOTIFICATION_QUICK_START.md")
    print("   - Practice demo script (10 minutes)")
    print("   - Prepare to explain implementation")


def main():
    """Main setup function"""
    print("=" * 70)
    print("  📧 Notification System Setup")
    print("=" * 70)
    
    # Change to project root if needed
    if not Path("backend").exists():
        print_error("Please run this script from the project root directory")
        sys.exit(1)
    
    # Run checks
    results = {
        'env_file': check_env_file(),
        'email_config': check_email_config(),
        'mongodb': check_mongodb(),
        'dependencies': check_dependencies(),
        'smtp': test_smtp_connection()
    }
    
    # Summary
    print_header("Setup Summary")
    
    print(f"   {'✅' if results['env_file'] else '❌'} .env file exists")
    print(f"   {'✅' if results['email_config'] else '❌'} Email configured")
    print(f"   {'✅' if results['mongodb'] else '❌'} MongoDB connected")
    print(f"   {'✅' if results['dependencies'] else '❌'} Dependencies installed")
    print(f"   {'✅' if results['smtp'] else '❌'} SMTP connection working")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "=" * 70)
        print("  🎉 Setup Complete! All checks passed.")
        print("=" * 70)
        show_next_steps()
    else:
        print("\n" + "=" * 70)
        print("  ⚠️  Setup Incomplete. Please fix the issues above.")
        print("=" * 70)
        
        print("\n📝 Common Issues:")
        
        if not results['email_config']:
            print("\n1. Email Configuration:")
            print("   - Edit backend/.env")
            print("   - Set EMAIL_ADDRESS to your Gmail address")
            print("   - Set EMAIL_PASSWORD to your Gmail App Password")
            print("   - Generate App Password: https://myaccount.google.com/apppasswords")
        
        if not results['mongodb']:
            print("\n2. MongoDB:")
            print("   - Ensure MongoDB is running")
            print("   - Check MONGO_URI in backend/.env")
            print("   - Run seed scripts to create test users")
        
        if not results['dependencies']:
            print("\n3. Dependencies:")
            print("   - Run: pip install -r backend/requirements.txt")
        
        if not results['smtp']:
            print("\n4. SMTP Connection:")
            print("   - Verify EMAIL_PASSWORD is correct")
            print("   - Use Gmail App Password, not regular password")
            print("   - Enable 2-Step Verification first")
            print("   - Generate new App Password if needed")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
