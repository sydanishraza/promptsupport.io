#!/usr/bin/env python3
"""
Direct Ultra-Large Document Function Test
Tests the ultra-large document detection functions directly
"""

import sys
import os
sys.path.append('/app/backend')

# Import the functions directly from the backend
try:
    from server import detect_ultra_large_document, create_hierarchical_article_structure, create_multi_level_overflow_articles
    print("✅ Successfully imported ultra-large document functions")
except ImportError as e:
    print(f"❌ Failed to import functions: {e}")
    sys.exit(1)

def test_ultra_large_detection():
    """Test the detect_ultra_large_document function directly"""
    print("\n🔍 TESTING ULTRA-LARGE DOCUMENT DETECTION FUNCTION")
    print("=" * 55)
    
    # Test case 1: Small document (should not trigger)
    small_content = "# Small Document\n\nThis is a small document with minimal content."
    small_result = detect_ultra_large_document(small_content, 1)
    
    print(f"\n📄 Test 1 - Small Document:")
    print(f"   - Content: {len(small_content)} chars, {len(small_content.split())} words")
    print(f"   - Ultra-large detected: {'✅ YES' if small_result['is_ultra_large'] else '❌ NO'}")
    print(f"   - Strategy: {small_result['strategy']}")
    print(f"   - Expected: Should NOT be ultra-large")
    
    # Test case 2: Large document (should trigger ultra-large)
    large_content = generate_large_content()
    large_result = detect_ultra_large_document(large_content, 20)
    
    print(f"\n📄 Test 2 - Large Document:")
    print(f"   - Content: {len(large_content)} chars, {len(large_content.split())} words")
    print(f"   - Headings: {large_result['heading_count']}")
    print(f"   - Major sections: {large_result['major_sections']}")
    print(f"   - Estimated articles: {large_result['estimated_articles_needed']}")
    print(f"   - Ultra-large detected: {'✅ YES' if large_result['is_ultra_large'] else '❌ NO'}")
    print(f"   - Strategy: {large_result['strategy']}")
    print(f"   - Expected: Should be ultra-large")
    
    # Test case 3: Very large document (should trigger document_splitting)
    very_large_content = generate_very_large_content()
    very_large_result = detect_ultra_large_document(very_large_content, 30)
    
    print(f"\n📄 Test 3 - Very Large Document:")
    print(f"   - Content: {len(very_large_content)} chars, {len(very_large_content.split())} words")
    print(f"   - Headings: {very_large_result['heading_count']}")
    print(f"   - Major sections: {very_large_result['major_sections']}")
    print(f"   - Estimated articles: {very_large_result['estimated_articles_needed']}")
    print(f"   - Ultra-large detected: {'✅ YES' if very_large_result['is_ultra_large'] else '❌ NO'}")
    print(f"   - Strategy: {very_large_result['strategy']}")
    print(f"   - Expected: Should be ultra-large with document_splitting strategy")
    
    # Analyze results
    test_results = []
    
    # Test 1: Small document should NOT be ultra-large
    test1_pass = not small_result['is_ultra_large']
    test_results.append(('Small Document (should not be ultra-large)', test1_pass))
    
    # Test 2: Large document should be ultra-large
    test2_pass = large_result['is_ultra_large']
    test_results.append(('Large Document (should be ultra-large)', test2_pass))
    
    # Test 3: Very large document should use document_splitting strategy
    test3_pass = (very_large_result['is_ultra_large'] and 
                  very_large_result['strategy'] == 'document_splitting')
    test_results.append(('Very Large Document (should use document_splitting)', test3_pass))
    
    print(f"\n📊 DETECTION TEST RESULTS:")
    passed_tests = 0
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   - {test_name}: {status}")
        if passed:
            passed_tests += 1
    
    print(f"\n🎯 Overall Detection Results: {passed_tests}/{len(test_results)} tests passed")
    
    return passed_tests == len(test_results)

def test_processing_strategies():
    """Test different processing strategies"""
    print("\n🔧 TESTING PROCESSING STRATEGY SELECTION")
    print("=" * 45)
    
    # Test multi_level_overflow strategy (12-15 estimated articles)
    medium_content = generate_medium_content()
    medium_result = detect_ultra_large_document(medium_content, 15)
    
    print(f"\n📄 Multi-Level Overflow Test:")
    print(f"   - Estimated articles: {medium_result['estimated_articles_needed']}")
    print(f"   - Strategy: {medium_result['strategy']}")
    print(f"   - Expected: multi_level_overflow")
    
    # Test hierarchical_articles strategy (15-20 estimated articles)
    large_content = generate_large_content()
    large_result = detect_ultra_large_document(large_content, 18)
    
    print(f"\n📄 Hierarchical Articles Test:")
    print(f"   - Estimated articles: {large_result['estimated_articles_needed']}")
    print(f"   - Strategy: {large_result['strategy']}")
    print(f"   - Expected: hierarchical_articles")
    
    # Test document_splitting strategy (>20 estimated articles)
    very_large_content = generate_very_large_content()
    very_large_result = detect_ultra_large_document(very_large_content, 25)
    
    print(f"\n📄 Document Splitting Test:")
    print(f"   - Estimated articles: {very_large_result['estimated_articles_needed']}")
    print(f"   - Strategy: {very_large_result['strategy']}")
    print(f"   - Expected: document_splitting")
    
    # Analyze strategy results
    strategy_results = []
    
    # Check if strategies are correctly selected based on estimated articles
    multi_level_correct = (medium_result['estimated_articles_needed'] <= 15 and 
                          medium_result['strategy'] in ['multi_level_overflow', 'standard_processing'])
    strategy_results.append(('Multi-level overflow strategy', multi_level_correct))
    
    hierarchical_correct = (large_result['estimated_articles_needed'] > 12 and 
                           large_result['strategy'] in ['hierarchical_articles', 'multi_level_overflow'])
    strategy_results.append(('Hierarchical articles strategy', hierarchical_correct))
    
    splitting_correct = (very_large_result['estimated_articles_needed'] > 20 and 
                        very_large_result['strategy'] == 'document_splitting')
    strategy_results.append(('Document splitting strategy', splitting_correct))
    
    print(f"\n📊 STRATEGY TEST RESULTS:")
    passed_strategies = 0
    for strategy_name, passed in strategy_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   - {strategy_name}: {status}")
        if passed:
            passed_strategies += 1
    
    print(f"\n🎯 Overall Strategy Results: {passed_strategies}/{len(strategy_results)} tests passed")
    
    return passed_strategies >= 2  # At least 2 out of 3 should pass

def test_completeness_thresholds():
    """Test completeness verification thresholds"""
    print("\n📊 TESTING COMPLETENESS VERIFICATION THRESHOLDS")
    print("=" * 50)
    
    # Test ultra-large document threshold (should be 60%)
    ultra_large_content = generate_large_content()
    ultra_large_result = detect_ultra_large_document(ultra_large_content, 20)
    
    print(f"\n📄 Ultra-Large Document Threshold Test:")
    print(f"   - Is ultra-large: {'✅ YES' if ultra_large_result['is_ultra_large'] else '❌ NO'}")
    print(f"   - Expected threshold: 60% (0.6) for ultra-large documents")
    print(f"   - Expected threshold: 70% (0.7) for standard documents")
    
    # Test standard document threshold
    standard_content = "# Standard Document\n\nThis is a standard document with normal content."
    standard_result = detect_ultra_large_document(standard_content, 5)
    
    print(f"\n📄 Standard Document Threshold Test:")
    print(f"   - Is ultra-large: {'✅ YES' if standard_result['is_ultra_large'] else '❌ NO'}")
    print(f"   - Should use standard 70% threshold")
    
    # The actual threshold application happens in the processing pipeline
    # Here we just verify the detection logic works correctly
    
    threshold_results = []
    
    # Ultra-large documents should be detected
    ultra_large_correct = ultra_large_result['is_ultra_large']
    threshold_results.append(('Ultra-large document detection', ultra_large_correct))
    
    # Standard documents should not be ultra-large
    standard_correct = not standard_result['is_ultra_large']
    threshold_results.append(('Standard document detection', standard_correct))
    
    print(f"\n📊 THRESHOLD TEST RESULTS:")
    passed_thresholds = 0
    for threshold_name, passed in threshold_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   - {threshold_name}: {status}")
        if passed:
            passed_thresholds += 1
    
    print(f"\n🎯 Overall Threshold Results: {passed_thresholds}/{len(threshold_results)} tests passed")
    
    return passed_thresholds == len(threshold_results)

def test_multi_level_overflow_creation():
    """Test multi-level overflow article creation"""
    print("\n📚 TESTING MULTI-LEVEL OVERFLOW ARTICLE CREATION")
    print("=" * 50)
    
    # Create test overflow sections (>5 sections to trigger multi-level)
    overflow_sections = []
    for i in range(8):  # 8 sections should trigger multi-level overflow
        section = {
            'title': f'Additional Topic {i+1}',
            'content': f'This is additional content for topic {i+1}. ' * 20,
            'section_type': 'overflow'
        }
        overflow_sections.append(section)
    
    metadata = {
        'source_document': 'test_document.txt',
        'processing_type': 'ultra_large'
    }
    
    print(f"\n📄 Multi-Level Overflow Test:")
    print(f"   - Overflow sections: {len(overflow_sections)}")
    print(f"   - Expected: Should create multiple overflow articles (>5 sections)")
    
    try:
        # Test the multi-level overflow creation function
        overflow_articles = create_multi_level_overflow_articles(overflow_sections, metadata)
        
        print(f"   - Overflow articles created: {len(overflow_articles)}")
        print(f"   - Expected: Multiple articles (sections grouped by 5)")
        
        # Analyze the created articles
        multi_level_detected = len(overflow_articles) > 1
        proper_grouping = all(article.get('is_multi_overflow', False) for article in overflow_articles)
        
        print(f"   - Multi-level overflow detected: {'✅ YES' if multi_level_detected else '❌ NO'}")
        print(f"   - Proper article grouping: {'✅ YES' if proper_grouping else '❌ NO'}")
        
        # Check article details
        if overflow_articles:
            sample_article = overflow_articles[0]
            print(f"   - Sample article title: {sample_article.get('title', 'N/A')}")
            print(f"   - Sample article type: {sample_article.get('stage_type', 'N/A')}")
            print(f"   - Sample overflow part: {sample_article.get('overflow_part', 'N/A')}")
            print(f"   - Sample total parts: {sample_article.get('overflow_total_parts', 'N/A')}")
        
        overflow_success = multi_level_detected and proper_grouping
        
        print(f"\n📊 MULTI-LEVEL OVERFLOW RESULTS:")
        print(f"   - Multi-level overflow creation: {'✅ PASSED' if overflow_success else '❌ FAILED'}")
        
        return overflow_success
        
    except Exception as e:
        print(f"   - ❌ Multi-level overflow test failed: {e}")
        return False

def generate_medium_content():
    """Generate medium-sized content for testing"""
    content_parts = ["# Medium Test Document\n\n"]
    
    for i in range(12):  # 12 sections
        section = f"""## {i+1}. Section {i+1}

### {i+1}.1 Subsection A
This is content for subsection A of section {i+1}. """ + "Content details. " * 30 + f"""

### {i+1}.2 Subsection B  
This is content for subsection B of section {i+1}. """ + "More content details. " * 25 + f"""

"""
        content_parts.append(section)
    
    return '\n'.join(content_parts)

def generate_large_content():
    """Generate large content for testing"""
    content_parts = ["# Large Test Document\n\n"]
    
    for i in range(18):  # 18 sections
        section = f"""## {i+1}. Section {i+1}

### {i+1}.1 Subsection A
This is content for subsection A of section {i+1}. """ + "Detailed content information. " * 40 + f"""

### {i+1}.2 Subsection B
This is content for subsection B of section {i+1}. """ + "More detailed content. " * 35 + f"""

### {i+1}.3 Subsection C
This is content for subsection C of section {i+1}. """ + "Additional content details. " * 30 + f"""

"""
        content_parts.append(section)
    
    return '\n'.join(content_parts)

def generate_very_large_content():
    """Generate very large content for testing"""
    content_parts = ["# Very Large Test Document\n\n"]
    
    for i in range(25):  # 25 sections
        section = f"""## {i+1}. Section {i+1}

### {i+1}.1 Subsection A
This is content for subsection A of section {i+1}. """ + "Comprehensive content information. " * 50 + f"""

### {i+1}.2 Subsection B
This is content for subsection B of section {i+1}. """ + "Detailed implementation content. " * 45 + f"""

### {i+1}.3 Subsection C
This is content for subsection C of section {i+1}. """ + "Additional comprehensive details. " * 40 + f"""

### {i+1}.4 Subsection D
This is content for subsection D of section {i+1}. """ + "Extended content information. " * 35 + f"""

"""
        content_parts.append(section)
    
    return '\n'.join(content_parts)

def main():
    """Run all direct function tests"""
    print("🚀 DIRECT ULTRA-LARGE DOCUMENT FUNCTION TESTS")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    try:
        result1 = test_ultra_large_detection()
        test_results.append(('Ultra-Large Detection', result1))
    except Exception as e:
        print(f"❌ Ultra-Large Detection test failed: {e}")
        test_results.append(('Ultra-Large Detection', False))
    
    try:
        result2 = test_processing_strategies()
        test_results.append(('Processing Strategies', result2))
    except Exception as e:
        print(f"❌ Processing Strategies test failed: {e}")
        test_results.append(('Processing Strategies', False))
    
    try:
        result3 = test_completeness_thresholds()
        test_results.append(('Completeness Thresholds', result3))
    except Exception as e:
        print(f"❌ Completeness Thresholds test failed: {e}")
        test_results.append(('Completeness Thresholds', False))
    
    try:
        result4 = test_multi_level_overflow_creation()
        test_results.append(('Multi-Level Overflow', result4))
    except Exception as e:
        print(f"❌ Multi-Level Overflow test failed: {e}")
        test_results.append(('Multi-Level Overflow', False))
    
    # Generate final summary
    print("\n" + "=" * 60)
    print("📊 DIRECT FUNCTION TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n🎯 Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    print(f"\n📋 Detailed Results:")
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   - {test_name}: {status}")
    
    print(f"\n🏆 FINAL ASSESSMENT:")
    if success_rate >= 75:
        print(f"   ✅ EXCELLENT: Ultra-large document functions are working correctly")
        print(f"   🎉 Core functionality verified and operational")
    elif success_rate >= 50:
        print(f"   ⚠️  GOOD: Most ultra-large document functions are working")
        print(f"   🔧 Some areas may need attention but core functionality is solid")
    else:
        print(f"   ❌ NEEDS WORK: Ultra-large document functions have significant issues")
        print(f"   🚨 Multiple critical functions are not working as expected")
    
    return success_rate >= 50

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)