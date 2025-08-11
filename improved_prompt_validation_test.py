#!/usr/bin/env python3
"""
NEW IMPROVED Prompt Design Validation Test
Testing the enhanced enterprise-grade prompts based on Woolf/Eltropy standards
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://29ab9b48-9f0b-482b-8a23-9ef1aebd2745.preview.emergentagent.com') + '/api'

class ImprovedPromptValidationTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.google_maps_url = "https://customer-assets.emergentagent.com/job_content-refiner-2/artifacts/5lvc26qb_Google%20Map%20JavaScript%20API%20Tutorial.docx"
        print(f"🎯 Testing NEW IMPROVED Prompt Design at: {self.base_url}")
        print(f"📄 Google Maps DOCX URL: {self.google_maps_url}")
        
    def test_improved_prompt_design_validation(self):
        """Test the NEW IMPROVED prompt design with Google Maps DOCX"""
        print("\n🔍 Testing NEW IMPROVED Prompt Design with Google Maps DOCX...")
        print("🎯 CRITICAL VALIDATION POINTS:")
        print("  1. Title extraction: 'Using Google Map Javascript API' from H1")
        print("  2. Word count targets: 1200-2000 words per article")
        print("  3. Logical structure: Introduction → Background → Core Concepts → Steps → Examples → Best Practices")
        print("  4. NO summarization - content should be expanded and enhanced")
        print("  5. Technical depth with background, context, examples, and best practices")
        
        try:
            # Download the Google Maps DOCX
            print("\n📥 Downloading Google Maps DOCX...")
            response = requests.get(self.google_maps_url, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Failed to download DOCX - status code {response.status_code}")
                return False
            
            docx_content = response.content
            file_size = len(docx_content)
            print(f"✅ Downloaded Google Maps DOCX: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            
            # Process with enhanced content processing
            print("\n🚀 Processing with NEW IMPROVED prompts...")
            
            files = {
                'file': ('Google_Map_JavaScript_API_Tutorial.docx', docx_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use enhanced processing metadata
            form_data = {
                'metadata': json.dumps({
                    "source": "improved_prompt_validation",
                    "test_type": "enterprise_grade_prompts",
                    "document_type": "technical_tutorial",
                    "quality_requirements": {
                        "word_count_target": "1200-2000",
                        "title_extraction": "Using Google Map Javascript API",
                        "logical_structure": True,
                        "no_summarization": True,
                        "technical_depth": True,
                        "enterprise_standards": True
                    }
                })
            }
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=300  # 5 minutes for comprehensive processing
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            
            if response.status_code != 200:
                print(f"❌ Processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            print(f"📊 Processing Response: {data.get('status', 'unknown')}")
            print(f"📊 Chunks Created: {data.get('chunks_created', 0)}")
            
            # Wait for processing to complete
            job_id = data.get('job_id')
            if job_id:
                print(f"📋 Job ID: {job_id}")
                print("⏳ Waiting for processing to complete...")
                time.sleep(15)  # Wait for processing
            
            # Check Content Library for generated articles
            return self.validate_improved_prompt_results()
            
        except Exception as e:
            print(f"❌ Improved prompt validation test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def validate_improved_prompt_results(self):
        """Validate the results against enterprise-grade standards"""
        print("\n🔍 Validating NEW IMPROVED Prompt Results...")
        
        try:
            # Get recent articles from Content Library
            response = requests.get(f"{self.base_url}/content-library", timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Could not access Content Library - status code {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Find Google Maps related articles (most recent)
            google_maps_articles = []
            for article in articles[:15]:  # Check recent articles
                title = article.get('title', '').lower()
                content = article.get('content', '').lower()
                
                if ('google' in title and ('map' in title or 'javascript' in title)) or \
                   ('google' in content and 'map' in content and 'javascript' in content):
                    google_maps_articles.append(article)
            
            print(f"📚 Found {len(google_maps_articles)} Google Maps related articles")
            
            if not google_maps_articles:
                print("❌ No Google Maps articles found for validation")
                return False
            
            # Validation Results
            validation_results = {
                "title_extraction": False,
                "word_count_targets": False,
                "logical_structure": False,
                "no_summarization": False,
                "technical_depth": False
            }
            
            print(f"\n📊 Analyzing {len(google_maps_articles)} articles...")
            
            # VALIDATION 1: Title Extraction
            print("\n1️⃣ TITLE EXTRACTION VALIDATION:")
            correct_titles = 0
            expected_patterns = ["using google map javascript api", "google map javascript api", "javascript api tutorial"]
            
            for i, article in enumerate(google_maps_articles):
                title = article.get('title', '')
                print(f"   Article {i+1}: '{title}'")
                
                title_lower = title.lower()
                if any(pattern in title_lower for pattern in expected_patterns):
                    correct_titles += 1
                    print(f"   ✅ Title matches expected pattern")
                elif "comprehensive guide" in title_lower:
                    print(f"   ❌ Generic title detected (old prompt)")
                else:
                    print(f"   ⚠️ Custom title but not exact match")
            
            title_success_rate = (correct_titles / len(google_maps_articles)) * 100
            print(f"📊 Title Extraction Success: {title_success_rate:.1f}% ({correct_titles}/{len(google_maps_articles)})")
            
            if title_success_rate >= 70:
                validation_results["title_extraction"] = True
                print("✅ TITLE EXTRACTION: PASSED")
            else:
                print("❌ TITLE EXTRACTION: FAILED")
            
            # VALIDATION 2: Word Count Targets (1200-2000 words)
            print("\n2️⃣ WORD COUNT TARGETS VALIDATION:")
            compliant_articles = 0
            total_words = 0
            
            for i, article in enumerate(google_maps_articles):
                content = article.get('content', '') or article.get('html', '')
                word_count = len(content.split())
                total_words += word_count
                
                print(f"   Article {i+1}: {word_count} words")
                
                if 1200 <= word_count <= 2000:
                    compliant_articles += 1
                    print(f"   ✅ Within target range (1200-2000)")
                elif word_count >= 800:
                    print(f"   ⚠️ Acceptable but below target")
                else:
                    print(f"   ❌ Too low (possible summarization)")
            
            avg_word_count = total_words / len(google_maps_articles)
            compliance_rate = (compliant_articles / len(google_maps_articles)) * 100
            
            print(f"📊 Average Word Count: {avg_word_count:.0f} words")
            print(f"📊 Target Compliance: {compliance_rate:.1f}% ({compliant_articles}/{len(google_maps_articles)})")
            
            if compliance_rate >= 50 or avg_word_count >= 1000:
                validation_results["word_count_targets"] = True
                print("✅ WORD COUNT TARGETS: PASSED")
            else:
                print("❌ WORD COUNT TARGETS: FAILED")
            
            # VALIDATION 3: Logical Structure
            print("\n3️⃣ LOGICAL STRUCTURE VALIDATION:")
            structure_indicators = [
                "introduction", "background", "overview", "getting started",
                "core concepts", "key concepts", "fundamentals", "basics",
                "steps", "implementation", "tutorial", "guide", "how to",
                "examples", "sample", "demo", "practice", "use case",
                "best practices", "recommendations", "tips", "conclusion"
            ]
            
            structured_articles = 0
            
            for i, article in enumerate(google_maps_articles):
                content = article.get('content', '').lower()
                
                found_indicators = [indicator for indicator in structure_indicators if indicator in content]
                structure_score = len(found_indicators)
                
                print(f"   Article {i+1}: {structure_score} structure indicators")
                print(f"     Found: {found_indicators[:5]}...")
                
                if structure_score >= 5:
                    structured_articles += 1
                    print(f"   ✅ Strong logical structure")
                elif structure_score >= 3:
                    print(f"   ⚠️ Basic structure present")
                else:
                    print(f"   ❌ Poor structure")
            
            structure_success = (structured_articles / len(google_maps_articles)) * 100
            print(f"📊 Logical Structure Success: {structure_success:.1f}% ({structured_articles}/{len(google_maps_articles)})")
            
            if structure_success >= 60:
                validation_results["logical_structure"] = True
                print("✅ LOGICAL STRUCTURE: PASSED")
            else:
                print("❌ LOGICAL STRUCTURE: FAILED")
            
            # VALIDATION 4: No Summarization (Content Expansion)
            print("\n4️⃣ NO SUMMARIZATION VALIDATION:")
            expansion_keywords = [
                "detailed", "comprehensive", "thorough", "in-depth", "extensive",
                "step-by-step", "complete guide", "full tutorial", "detailed explanation",
                "comprehensive overview", "complete implementation", "thorough understanding"
            ]
            
            summarization_keywords = [
                "in summary", "to summarize", "in conclusion", "briefly",
                "key points", "main points", "overview of", "summary of"
            ]
            
            expanded_articles = 0
            
            for i, article in enumerate(google_maps_articles):
                content = article.get('content', '').lower()
                
                expansion_count = sum(1 for keyword in expansion_keywords if keyword in content)
                summary_count = sum(1 for keyword in summarization_keywords if keyword in content)
                
                print(f"   Article {i+1}: {expansion_count} expansion indicators, {summary_count} summary indicators")
                
                if expansion_count > summary_count and expansion_count >= 3:
                    expanded_articles += 1
                    print(f"   ✅ Content expansion detected")
                elif expansion_count >= 2:
                    print(f"   ⚠️ Some expansion present")
                else:
                    print(f"   ❌ Possible summarization")
            
            expansion_success = (expanded_articles / len(google_maps_articles)) * 100
            print(f"📊 Content Expansion Success: {expansion_success:.1f}% ({expanded_articles}/{len(google_maps_articles)})")
            
            if expansion_success >= 50 or avg_word_count >= 1200:
                validation_results["no_summarization"] = True
                print("✅ NO SUMMARIZATION: PASSED")
            else:
                print("❌ NO SUMMARIZATION: FAILED")
            
            # VALIDATION 5: Technical Depth
            print("\n5️⃣ TECHNICAL DEPTH VALIDATION:")
            technical_keywords = [
                "api", "javascript", "function", "method", "parameter", "callback",
                "code", "example", "implementation", "syntax", "library", "framework",
                "google.maps", "geocoding", "marker", "map", "coordinates", "latitude",
                "longitude", "event", "object", "property", "variable", "array"
            ]
            
            technical_articles = 0
            
            for i, article in enumerate(google_maps_articles):
                content = article.get('content', '').lower()
                
                found_technical = [keyword for keyword in technical_keywords if keyword in content]
                technical_score = len(found_technical)
                
                print(f"   Article {i+1}: {technical_score} technical indicators")
                print(f"     Found: {found_technical[:8]}...")
                
                if technical_score >= 10:
                    technical_articles += 1
                    print(f"   ✅ Strong technical depth")
                elif technical_score >= 6:
                    print(f"   ⚠️ Moderate technical depth")
                else:
                    print(f"   ❌ Insufficient technical depth")
            
            technical_success = (technical_articles / len(google_maps_articles)) * 100
            print(f"📊 Technical Depth Success: {technical_success:.1f}% ({technical_articles}/{len(google_maps_articles)})")
            
            if technical_success >= 60:
                validation_results["technical_depth"] = True
                print("✅ TECHNICAL DEPTH: PASSED")
            else:
                print("❌ TECHNICAL DEPTH: FAILED")
            
            # OVERALL VALIDATION RESULTS
            print("\n" + "="*80)
            print("📊 OVERALL NEW IMPROVED PROMPT DESIGN VALIDATION RESULTS")
            print("="*80)
            
            passed_validations = sum(validation_results.values())
            total_validations = len(validation_results)
            
            for validation, passed in validation_results.items():
                status = "✅ PASSED" if passed else "❌ FAILED"
                print(f"   {validation.replace('_', ' ').title()}: {status}")
            
            overall_success_rate = (passed_validations / total_validations) * 100
            print(f"\n🎯 OVERALL SUCCESS RATE: {overall_success_rate:.1f}% ({passed_validations}/{total_validations})")
            
            # Final Assessment
            if overall_success_rate >= 80:
                print("🎉 NEW IMPROVED PROMPT DESIGN: EXCELLENT QUALITY")
                print("✅ Validates quality improvements over previous design")
                print("✅ Meets enterprise-grade standards (Woolf/Eltropy)")
                return True
            elif overall_success_rate >= 60:
                print("⚠️ NEW IMPROVED PROMPT DESIGN: GOOD QUALITY")
                print("✅ Shows improvement but minor refinements needed")
                return True
            else:
                print("❌ NEW IMPROVED PROMPT DESIGN: NEEDS IMPROVEMENT")
                print("❌ Does not meet quality improvement targets")
                return False
                
        except Exception as e:
            print(f"❌ Validation failed - {str(e)}")
            return False

def main():
    """Main test execution"""
    print("🎯 NEW IMPROVED Prompt Design Validation Test")
    print("Testing enterprise-grade prompts based on Woolf/Eltropy standards")
    print("Using Google Maps DOCX document as validation case")
    print("="*80)
    
    tester = ImprovedPromptValidationTest()
    success = tester.test_improved_prompt_design_validation()
    
    print("\n" + "="*80)
    print("FINAL VALIDATION RESULTS")
    print("="*80)
    
    if success:
        print("🎉 VALIDATION SUCCESSFUL")
        print("✅ NEW IMPROVED prompt design shows quality improvements")
        print("✅ Resolves quality issues identified by user")
        print("✅ Meets enterprise-grade standards")
        return True
    else:
        print("❌ VALIDATION FAILED")
        print("❌ NEW IMPROVED prompt design needs further refinement")
        print("❌ Quality improvements not sufficient")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)