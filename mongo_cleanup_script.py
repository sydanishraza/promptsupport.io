#!/usr/bin/env python3
"""
KE-PR9.3: Complete MongoDB cleanup script
Systematically replaces all direct MongoDB calls with repository pattern
"""

import re

def cleanup_mongodb_calls(file_content):
    """Replace all direct MongoDB calls with repository patterns"""
    
    # 1. Content Library Operations - Most Critical
    
    # Insert operations
    file_content = re.sub(
        r'await db\.content_library\.insert_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use repository pattern
                from engine.stores.mongo import RepositoryFactory
                content_repo = RepositoryFactory.get_content_library()
                await content_repo.insert_article(\1)''',
        file_content
    )
    
    # Find by ID operations  
    file_content = re.sub(
        r'await db\.content_library\.find_one\(\{"id": ([^}]+)\}\)',
        r'''# KE-PR9.3: Use repository pattern
                from engine.stores.mongo import RepositoryFactory
                content_repo = RepositoryFactory.get_content_library()
                article = await content_repo.collection.find_one({"id": \1})''',
        file_content
    )
    
    # Find by doc_uid operations (already have repository method)
    file_content = re.sub(
        r'await db\.content_library\.find_one\(\{"doc_uid": ([^}]+)\}\)',
        r'''# KE-PR9.3: Use repository pattern
                from engine.stores.mongo import RepositoryFactory
                content_repo = RepositoryFactory.get_content_library()
                doc = await content_repo.find_by_doc_uid(\1)''',
        file_content
    )
    
    # 2. V2 Processing Results - Use existing repositories
    
    # V2 Analysis
    file_content = re.sub(
        r'await db\.v2_analysis\.insert_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use V2 analysis repository
                from engine.stores.mongo import RepositoryFactory
                analysis_repo = RepositoryFactory.get_v2_analysis()
                await analysis_repo.store_analysis(\1)''',
        file_content
    )
    
    file_content = re.sub(
        r'await db\.v2_analysis\.find_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use V2 analysis repository
                from engine.stores.mongo import RepositoryFactory
                analysis_repo = RepositoryFactory.get_v2_analysis()
                analysis_record = await analysis_repo.get_analysis(\1)''',
        file_content
    )
    
    # V2 Global Outlines
    file_content = re.sub(
        r'await db\.v2_global_outlines\.insert_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use V2 outlines repository
                from engine.stores.mongo import RepositoryFactory
                outline_repo = RepositoryFactory.get_v2_outlines()
                await outline_repo.store_global_outline(\1)''',
        file_content
    )
    
    file_content = re.sub(
        r'await db\.v2_global_outlines\.find_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use V2 outlines repository
                from engine.stores.mongo import RepositoryFactory
                outline_repo = RepositoryFactory.get_v2_outlines()
                outline_record = await outline_repo.get_global_outline(\1)''',
        file_content
    )
    
    # V2 Per Article Outlines
    file_content = re.sub(
        r'await db\.v2_per_article_outlines\.insert_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use V2 outlines repository
                from engine.stores.mongo import RepositoryFactory
                outline_repo = RepositoryFactory.get_v2_outlines()
                await outline_repo.store_per_article_outlines(\1)''',
        file_content
    )
    
    # V2 Validation Results
    file_content = re.sub(
        r'await db\.v2_validation_results\.insert_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use V2 validation repository
                from engine.stores.mongo import RepositoryFactory
                validation_repo = RepositoryFactory.get_v2_validation()
                await validation_repo.store_validation(\1)''',
        file_content
    )
    
    file_content = re.sub(
        r'await db\.v2_validation_results\.find\(\)',
        r'''# KE-PR9.3: Use V2 validation repository
                from engine.stores.mongo import RepositoryFactory
                validation_repo = RepositoryFactory.get_v2_validation()
                validation_results = await validation_repo.find_validations()''',
        file_content
    )
    
    # Assets operations
    file_content = re.sub(
        r'await db\.assets\.insert_many\(([^)]+)\)',
        r'''# KE-PR9.3: Use assets repository
                from engine.stores.mongo import RepositoryFactory
                assets_repo = RepositoryFactory.get_assets()
                result = await assets_repo.insert_assets(\1)''',
        file_content
    )
    
    # QA Results
    file_content = re.sub(
        r'await db\.qa_results\.insert_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use QA results repository
                from engine.stores.mongo import RepositoryFactory
                qa_repo = RepositoryFactory.get_qa_results()
                await qa_repo.insert_qa_report(\1)''',
        file_content
    )
    
    # 3. Clean up excessive repository imports - consolidate them
    # Remove duplicate repository imports and consolidate at function start
    
    return file_content

def add_repository_import_at_top(file_content):
    """Add repository import at the top of the file"""
    
    # Find the imports section and add repository import
    import_pattern = r'(from engine\.stores\.mongo import RepositoryFactory.*?\n)'
    if not re.search(import_pattern, file_content):
        # Add after the existing engine imports
        engine_import_pattern = r'(# New Engine Package Imports.*?\n)'
        if re.search(engine_import_pattern, file_content):
            file_content = re.sub(
                engine_import_pattern,
                r'\1# KE-PR9.3: Repository pattern imports\nfrom engine.stores.mongo import RepositoryFactory\n',
                file_content
            )
    
    return file_content

def main():
    """Main cleanup function"""
    print("🧹 KE-PR9.3: Starting complete MongoDB cleanup...")
    
    # Read the current server file
    with open('/app/backend/server.py', 'r') as f:
        content = f.read()
    
    print(f"📄 Original file size: {len(content)} characters")
    
    # Add repository import at top
    content = add_repository_import_at_top(content)
    
    # Apply all MongoDB call replacements
    content = cleanup_mongodb_calls(content)
    
    print(f"📄 Processed file size: {len(content)} characters")
    
    # Write the cleaned up version
    with open('/app/backend/server_cleaned.py', 'w') as f:
        f.write(content)
    
    print("✅ KE-PR9.3: MongoDB cleanup completed!")
    print("📁 Cleaned file saved as: /app/backend/server_cleaned.py")
    print("🔍 Review the changes and replace the original file when ready")

if __name__ == "__main__":
    main()