"""
Token cleanup utility for removing expired tokens from the database
"""
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def cleanup_expired_tokens(db):
    """Clean up expired refresh tokens and password reset tokens"""
    try:
        current_time = datetime.utcnow()
        
        # Remove expired refresh tokens
        refresh_result = db.refresh_tokens.delete_many({
            'expires_at': {'$lt': current_time}
        })
        
        # Remove expired password reset tokens
        reset_result = db.password_resets.delete_many({
            'expires_at': {'$lt': current_time}
        })
        
        print(f"Cleaned up {refresh_result.deleted_count} expired refresh tokens")
        print(f"Cleaned up {reset_result.deleted_count} expired password reset tokens")
        
        return {
            'refresh_tokens_cleaned': refresh_result.deleted_count,
            'reset_tokens_cleaned': reset_result.deleted_count
        }
        
    except Exception as e:
        print(f"Error during token cleanup: {e}")
        return None

def main():
    """Main function to run token cleanup"""
    print("="*60)
    print("  Token Cleanup Utility")
    print("="*60)
    
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/lms')
    client = MongoClient(mongo_uri)
    db = client.get_database()
    
    print(f"\nConnected to database: {db.name}")
    
    # Run cleanup
    result = cleanup_expired_tokens(db)
    
    if result:
        print("\n✅ Token cleanup completed successfully!")
        print(f"   - Refresh tokens removed: {result['refresh_tokens_cleaned']}")
        print(f"   - Reset tokens removed: {result['reset_tokens_cleaned']}")
    else:
        print("\n❌ Token cleanup failed")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
