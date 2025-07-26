#!/usr/bin/env python3
"""
Content Library Cleanup Script
Deletes all articles and assets to start fresh with testing
"""

import asyncio
import motor.motor_asyncio
import os
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def cleanup_content_library():
    """Clean up all articles and assets from the content library"""
    
    # Connect to MongoDB
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.environ.get('DATABASE_NAME', 'promptsupport_db')
    
    print(f"🔗 Connecting to MongoDB: {MONGO_URL}")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Delete all articles from content_library collection
        print("🗑️ Deleting all articles from content_library...")
        articles_result = await db.content_library.delete_many({})
        print(f"✅ Deleted {articles_result.deleted_count} articles")
        
        # Delete all assets from assets collection
        print("🗑️ Deleting all assets from assets collection...")
        assets_result = await db.assets.delete_many({})
        print(f"✅ Deleted {assets_result.deleted_count} assets")
        
        # Delete all document chunks if they exist
        print("🗑️ Deleting all document chunks...")
        try:
            chunks_result = await db.document_chunks.delete_many({})
            print(f"✅ Deleted {chunks_result.deleted_count} document chunks")
        except Exception as e:
            print(f"⚠️ No document chunks to delete or error: {e}")
        
        # Delete all conversations if they exist
        print("🗑️ Deleting all conversations...")
        try:
            conv_result = await db.conversations.delete_many({})
            print(f"✅ Deleted {conv_result.deleted_count} conversations")
        except Exception as e:
            print(f"⚠️ No conversations to delete or error: {e}")
        
        # Clean up uploaded files directory
        uploads_dir = "/app/backend/static/uploads"
        if os.path.exists(uploads_dir):
            print(f"🗑️ Cleaning up uploaded files in {uploads_dir}...")
            
            # Count files before deletion
            file_count = 0
            for root, dirs, files in os.walk(uploads_dir):
                file_count += len(files)
            
            if file_count > 0:
                # Remove all files in uploads directory
                for filename in os.listdir(uploads_dir):
                    file_path = os.path.join(uploads_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f"⚠️ Error deleting {file_path}: {e}")
                
                print(f"✅ Cleaned up {file_count} uploaded files")
            else:
                print("✅ No uploaded files to clean up")
        else:
            print(f"⚠️ Uploads directory {uploads_dir} does not exist")
        
        # Verify cleanup
        print("\n📊 Verifying cleanup...")
        articles_count = await db.content_library.count_documents({})
        assets_count = await db.assets.count_documents({})
        
        print(f"📄 Articles remaining: {articles_count}")
        print(f"🖼️ Assets remaining: {assets_count}")
        
        if articles_count == 0 and assets_count == 0:
            print("\n🎉 Content Library cleanup completed successfully!")
            print("✅ Ready for fresh Knowledge Engine testing")
        else:
            print("\n⚠️ Some items may still remain - check manually if needed")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        raise
    
    finally:
        client.close()

if __name__ == "__main__":
    print("🧹 CONTENT LIBRARY CLEANUP")
    print("=" * 50)
    print("This will DELETE ALL articles and assets from the Content Library!")
    
    confirm = input("Are you sure you want to proceed? (type 'yes' to confirm): ")
    
    if confirm.lower() == 'yes':
        print("\n🚀 Starting cleanup...")
        asyncio.run(cleanup_content_library())
    else:
        print("❌ Cleanup cancelled")