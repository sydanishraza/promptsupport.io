#!/usr/bin/env python3
"""
KE-PR9.3: Targeted MongoDB cleanup
More surgical replacement of remaining MongoDB calls
"""

import re

def replace_content_library_inserts(content):
    """Replace content library insert operations"""
    
    # Pattern 1: Simple insert_one
    pattern1 = r'await db\.content_library\.insert_one\(([^)]+)\)'
    replacement1 = r'''# KE-PR9.3: Use repository pattern for content_library operations
                from engine.stores.mongo import RepositoryFactory
                content_repo = RepositoryFactory.get_content_library()
                await content_repo.insert_article(\1)'''
    
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: Find operations by id
    pattern2 = r'await db\.content_library\.find_one\(\{"id": ([^}]+)\}\)'
    replacement2 = r'''# KE-PR9.3: Use repository pattern for find operations
                from engine.stores.mongo import RepositoryFactory
                content_repo = RepositoryFactory.get_content_library()
                result = await content_repo.collection.find_one({"id": \1})'''
    
    content = re.sub(pattern2, replacement2, content)
    
    return content

def replace_v2_operations(content):
    """Replace V2 processing operations with repository pattern"""
    
    # V2 Analysis operations
    content = re.sub(
        r'await db\.v2_analysis\.insert_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use V2 analysis repository
                from engine.stores.mongo import RepositoryFactory
                analysis_repo = RepositoryFactory.get_v2_analysis()
                await analysis_repo.store_analysis(\1)''',
        content
    )
    
    # V2 Validation results
    content = re.sub(
        r'await db\.v2_validation_results\.insert_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use V2 validation repository
                from engine.stores.mongo import RepositoryFactory
                validation_repo = RepositoryFactory.get_v2_validation()
                await validation_repo.store_validation(\1)''',
        content
    )
    
    # V2 QA results
    content = re.sub(
        r'await db\.v2_qa_results\.insert_one\(([^)]+)\)',
        r'''# KE-PR9.3: Use QA results repository
                from engine.stores.mongo import RepositoryFactory
                qa_repo = RepositoryFactory.get_qa_results()
                await qa_repo.insert_qa_report(\1)''',
        content
    )
    
    return content

def replace_assets_operations(content):
    """Replace assets operations"""
    content = re.sub(
        r'await db\.assets\.insert_many\(([^)]+)\)',
        r'''# KE-PR9.3: Use assets repository
                from engine.stores.mongo import RepositoryFactory
                assets_repo = RepositoryFactory.get_assets()
                result = await assets_repo.insert_assets(\1)''',
        content
    )
    
    return content

def main():
    print("🎯 KE-PR9.3: Running targeted MongoDB cleanup...")
    
    # Read current file
    with open('/app/backend/server.py', 'r') as f:
        content = f.read()
    
    original_size = len(content)
    
    # Apply targeted replacements
    content = replace_content_library_inserts(content)
    content = replace_v2_operations(content)
    content = replace_assets_operations(content)
    
    # Clean up any double imports that might have been created
    content = re.sub(
        r'(# KE-PR9\.3:.*?\n.*?from engine\.stores\.mongo import RepositoryFactory\n.*?){2,}',
        r'\1',
        content,
        flags=re.DOTALL
    )
    
    final_size = len(content)
    
    # Write back to file
    with open('/app/backend/server.py', 'w') as f:
        f.write(content)
    
    print(f"✅ File size: {original_size} → {final_size} ({final_size - original_size:+} chars)")
    print("✅ KE-PR9.3: Targeted cleanup completed!")

if __name__ == "__main__":
    main()