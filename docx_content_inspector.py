#!/usr/bin/env python3
"""
DOCX Content Inspector
Inspect the actual contents of DOCX files to understand why no images are found
"""

import zipfile
import os

def inspect_docx_file(file_path):
    """Inspect the contents of a DOCX file"""
    print(f"\n🔍 Inspecting DOCX file: {os.path.basename(file_path)}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"📁 ZIP contains {len(file_list)} files")
            
            # Categorize files
            categories = {
                'word/media/': [],
                'word/embeddings/': [],
                'word/': [],
                'docProps/': [],
                '_rels/': [],
                'other': []
            }
            
            for file in file_list:
                categorized = False
                for category in categories:
                    if file.startswith(category):
                        categories[category].append(file)
                        categorized = True
                        break
                if not categorized:
                    categories['other'].append(file)
            
            # Print categorized files
            for category, files in categories.items():
                if files:
                    print(f"\n📂 {category} ({len(files)} files):")
                    for file in files[:10]:  # Show first 10
                        print(f"  - {file}")
                    if len(files) > 10:
                        print(f"  ... and {len(files) - 10} more files")
            
            # Check specifically for image files
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.tiff', '.emf', '.wmf']
            all_image_files = []
            
            for file in file_list:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    all_image_files.append(file)
            
            print(f"\n🖼️ IMAGE FILES FOUND ({len(all_image_files)}):")
            if all_image_files:
                for img_file in all_image_files:
                    file_info = zip_ref.getinfo(img_file)
                    print(f"  ✅ {img_file} ({file_info.file_size} bytes)")
            else:
                print("  ❌ No image files found in this DOCX")
            
            # Check for relationships that might reference images
            try:
                if 'word/_rels/document.xml.rels' in file_list:
                    rels_content = zip_ref.read('word/_rels/document.xml.rels').decode('utf-8')
                    image_refs = rels_content.count('image')
                    print(f"\n🔗 RELATIONSHIPS:")
                    print(f"  📋 Image references in relationships: {image_refs}")
                    
                    if image_refs > 0:
                        print("  ✅ Document has image relationships")
                    else:
                        print("  ❌ No image relationships found")
                else:
                    print(f"\n🔗 RELATIONSHIPS:")
                    print("  ❌ No document relationships file found")
            except Exception as rel_error:
                print(f"  ⚠️ Could not read relationships: {rel_error}")
            
            # Check document.xml for image references
            try:
                if 'word/document.xml' in file_list:
                    doc_content = zip_ref.read('word/document.xml').decode('utf-8')
                    drawing_refs = doc_content.count('<w:drawing>')
                    pic_refs = doc_content.count('<pic:')
                    blip_refs = doc_content.count('<a:blip')
                    
                    print(f"\n📄 DOCUMENT XML:")
                    print(f"  📋 Drawing elements: {drawing_refs}")
                    print(f"  📋 Picture elements: {pic_refs}")
                    print(f"  📋 Blip elements: {blip_refs}")
                    
                    if drawing_refs > 0 or pic_refs > 0 or blip_refs > 0:
                        print("  ✅ Document XML contains image references")
                    else:
                        print("  ❌ No image references in document XML")
                else:
                    print(f"\n📄 DOCUMENT XML:")
                    print("  ❌ No document.xml file found")
            except Exception as doc_error:
                print(f"  ⚠️ Could not read document.xml: {doc_error}")
            
            # Summary
            print(f"\n🎯 SUMMARY FOR {os.path.basename(file_path)}:")
            if all_image_files:
                print(f"  ✅ Contains {len(all_image_files)} image files")
                print(f"  ✅ Should be processable by image extraction pipeline")
            else:
                print(f"  ❌ Contains NO image files")
                print(f"  ❌ This explains why images_processed = 0")
                print(f"  ❌ This DOCX file has no embedded images to extract")
            
    except zipfile.BadZipFile:
        print(f"❌ File is not a valid ZIP/DOCX file")
    except Exception as e:
        print(f"❌ Inspection failed: {e}")

def main():
    """Inspect all available DOCX files"""
    print("🔍 DOCX CONTENT INSPECTION")
    print("=" * 80)
    
    # List of DOCX files to inspect
    docx_files = [
        '/app/simple_test.docx',
        '/app/test_billing.docx',
        '/app/test_promotions.docx',
        '/app/large_performance_test.docx',
        '/app/frontend_test.docx'
    ]
    
    for docx_file in docx_files:
        if os.path.exists(docx_file):
            inspect_docx_file(docx_file)
        else:
            print(f"\n⚠️ File not found: {docx_file}")
    
    print(f"\n" + "=" * 80)
    print("🎯 CONCLUSION:")
    print("If all DOCX files show 'Contains NO image files', then the issue is that")
    print("the test DOCX files don't actually contain embedded images.")
    print("The image processing pipeline may be working correctly, but there are")
    print("simply no images to extract from these particular DOCX files.")
    print("=" * 80)

if __name__ == "__main__":
    main()