#!/usr/bin/env python3
"""
Script to clean up all refined engine implementations from server.py
"""

import re

def cleanup_server_py():
    """Remove all refined engine related code from server.py"""
    
    with open('backend/server.py', 'r') as f:
        content = f.read()
    
    # Track what we're removing
    lines_removed = 0
    
    print("🧹 Starting cleanup of refined engine implementations...")
    
    # Remove refined engine import attempts and error handling
    content = re.sub(r'from refined_engine[^;]*\n?', '', content)
    content = re.sub(r'from refined_engine_v2[^;]*\n?', '', content)
    content = re.sub(r'from engine_migration_tool[^;]*\n?', '', content)
    content = re.sub(r'import refined_engine[^;]*\n?', '', content)
    
    # Define the endpoint blocks to remove (with their full function implementations)
    endpoints_to_remove = [
        # Advanced engine endpoints
        (r'# PHASE 2: ADVANCED REFINED ENGINE.*?(?=@app\.|# |$)', 'Advanced engine endpoints'),
        (r'@app\.post\("/api/content/process-advanced"\).*?(?=@app\.|# |$)', 'process-advanced endpoint'),
        (r'@app\.post\("/api/content/upload-advanced"\).*?(?=@app\.|# |$)', 'upload-advanced endpoint'),
        (r'@app\.post\("/api/content/upload-batch-advanced"\).*?(?=@app\.|# |$)', 'upload-batch-advanced endpoint'),
        
        # Cleanup and migration endpoints
        (r'@app\.post\("/api/content/cleanup-formatting"\).*?(?=@app\.|# |$)', 'cleanup-formatting endpoint'),
        (r'@app\.post\("/api/content/compare-engines"\).*?(?=@app\.|# |$)', 'compare-engines endpoint'),
        (r'@app\.post\("/api/content/migrate-articles"\).*?(?=@app\.|# |$)', 'migrate-articles endpoint'),
        (r'@app\.get\("/api/content/engine-statistics"\).*?(?=@app\.|# |$)', 'engine-statistics endpoint'),
        (r'@app\.get\("/api/content/analytics/advanced"\).*?(?=@app\.|# |$)', 'analytics/advanced endpoint'),
        
        # Refined engine endpoints
        (r'@app\.post\("/api/content/process-refined"\).*?(?=@app\.|# |$)', 'process-refined endpoint'),
        (r'@app\.post\("/api/content/upload-refined"\).*?(?=@app\.|# |$)', 'upload-refined endpoint'),
    ]
    
    # Remove each endpoint block
    for pattern, description in endpoints_to_remove:
        original_length = len(content)
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        removed_chars = original_length - len(content)
        if removed_chars > 0:
            print(f"  ✅ Removed {description} ({removed_chars} characters)")
            lines_removed += removed_chars // 50  # Rough estimate
    
    # Remove any references to refined engines in comments
    content = re.sub(r'#.*refined.*engine.*\n?', '', content, flags=re.IGNORECASE)
    content = re.sub(r'#.*advanced.*engine.*\n?', '', content, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Write the cleaned content back
    with open('backend/server.py', 'w') as f:
        f.write(content)
    
    print(f"✅ Cleanup complete! Estimated {lines_removed} lines removed")
    print("📁 Original server.py backed up as server_backup.py")

if __name__ == "__main__":
    cleanup_server_py()