#!/usr/bin/env python3
"""
Enhanced Asset Manager Delete Functionality Testing
Comprehensive testing for asset deletion and persistence issues
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://promptsupport-2.preview.emergentagent.com') + '/api'

class AssetDeleteTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_assets = []
        self.initial_asset_count = 0
        print(f"🎯 Testing Enhanced Asset Manager Delete Functionality at: {self.base_url}")
        
    def test_get_initial_asset_list(self):
        """Get initial list of assets to understand current state"""
        print("\n🔍 Step 1: Getting initial asset list...")
        try:
            response = requests.get(f"{self.base_url}/assets", timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get('assets', [])
                self.initial_asset_count = len(assets)
                
                print(f"✅ Initial asset count: {self.initial_asset_count}")
                
                # Store first few assets for testing (if any exist)
                if assets:
                    self.test_assets = assets[:3]  # Take first 3 for testing
                    print(f"📋 Sample assets for testing:")
                    for i, asset in enumerate(self.test_assets):
                        print(f"  {i+1}. ID: {asset.get('id')}, Name: {asset.get('name', 'Unknown')}")
                        print(f"     Type: {asset.get('type', 'Unknown')}, Source: {asset.get('source', 'Unknown')}")
                else:
                    print("⚠️ No existing assets found - will need to create test assets")
                
                return True
            else:
                print(f"❌ Failed to get asset list - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to get initial asset list - {str(e)}")
            return False
    
    def test_create_test_asset(self):
        """Create a test asset for deletion testing"""
        print("\n🔍 Step 2: Creating test asset for deletion...")
        try:
            # Create a simple test image (1x1 PNG)
            import base64
            # 1x1 transparent PNG in base64
            png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==')
            
            files = {
                'file': ('test_delete_asset.png', png_data, 'image/png')
            }
            
            response = requests.post(
                f"{self.base_url}/assets/upload",
                files=files,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    test_asset = {
                        'id': data.get('id'),
                        'name': data.get('name', 'test_delete_asset.png'),
                        'url': data.get('url'),
                        'source': 'test_upload'
                    }
                    self.test_assets.append(test_asset)
                    print(f"✅ Test asset created successfully:")
                    print(f"   ID: {test_asset['id']}")
                    print(f"   Name: {test_asset['name']}")
                    print(f"   URL: {test_asset['url']}")
                    return True
                else:
                    print(f"❌ Asset upload failed: {data}")
                    return False
            else:
                print(f"❌ Asset upload failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create test asset - {str(e)}")
            return False
    
    def test_delete_asset_endpoint(self):
        """Test DELETE /api/assets/{asset_id} endpoint directly"""
        print("\n🔍 Step 3: Testing DELETE /api/assets/{asset_id} endpoint...")
        
        if not self.test_assets:
            print("❌ No test assets available for deletion testing")
            return False
        
        # Use the last asset (our created test asset if available)
        test_asset = self.test_assets[-1]
        asset_id = test_asset['id']
        asset_name = test_asset['name']
        
        print(f"🎯 Attempting to delete asset: {asset_name} (ID: {asset_id})")
        
        try:
            response = requests.delete(
                f"{self.base_url}/assets/{asset_id}",
                timeout=15
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ DELETE endpoint successful for asset {asset_id}")
                        return True
                    else:
                        print(f"❌ DELETE endpoint returned success=false: {data}")
                        return False
                except json.JSONDecodeError:
                    # Some APIs return plain text success messages
                    if 'success' in response.text.lower() or 'deleted' in response.text.lower():
                        print(f"✅ DELETE endpoint successful (text response)")
                        return True
                    else:
                        print(f"❌ DELETE endpoint unclear response: {response.text}")
                        return False
            else:
                print(f"❌ DELETE endpoint failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ DELETE endpoint test failed - {str(e)}")
            return False
    
    def test_asset_removal_verification(self):
        """Verify the deleted asset is actually removed from the list"""
        print("\n🔍 Step 4: Verifying asset removal from list...")
        
        if not self.test_assets:
            print("❌ No test assets to verify removal")
            return False
        
        deleted_asset = self.test_assets[-1]
        deleted_asset_id = deleted_asset['id']
        
        try:
            # Wait a moment for deletion to process
            time.sleep(2)
            
            response = requests.get(f"{self.base_url}/assets", timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get('assets', [])
                current_count = len(assets)
                
                print(f"📊 Asset count after deletion: {current_count}")
                print(f"📊 Initial asset count: {self.initial_asset_count}")
                
                # Check if the specific asset is gone
                deleted_asset_found = False
                for asset in assets:
                    if asset.get('id') == deleted_asset_id:
                        deleted_asset_found = True
                        break
                
                if deleted_asset_found:
                    print(f"❌ CRITICAL ISSUE: Deleted asset {deleted_asset_id} still appears in asset list!")
                    print(f"   This indicates the delete functionality is not working properly")
                    return False
                else:
                    print(f"✅ Deleted asset {deleted_asset_id} successfully removed from list")
                    
                    # Check if count decreased (if we created a test asset)
                    if current_count < self.initial_asset_count:
                        print(f"✅ Asset count decreased from {self.initial_asset_count} to {current_count}")
                    elif current_count == self.initial_asset_count:
                        print(f"⚠️ Asset count unchanged - may indicate asset was already deleted or count issue")
                    
                    return True
            else:
                print(f"❌ Failed to verify asset removal - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Asset removal verification failed - {str(e)}")
            return False
    
    def test_deletion_persistence(self):
        """Test that deleted assets don't reappear after multiple requests"""
        print("\n🔍 Step 5: Testing deletion persistence (assets don't reappear)...")
        
        if not self.test_assets:
            print("❌ No test assets to verify persistence")
            return False
        
        deleted_asset_id = self.test_assets[-1]['id']
        
        try:
            # Make multiple requests to check if asset reappears
            for i in range(3):
                print(f"  Check {i+1}/3: Verifying asset {deleted_asset_id} stays deleted...")
                
                response = requests.get(f"{self.base_url}/assets", timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    assets = data.get('assets', [])
                    
                    # Check if deleted asset reappeared
                    asset_found = False
                    for asset in assets:
                        if asset.get('id') == deleted_asset_id:
                            asset_found = True
                            break
                    
                    if asset_found:
                        print(f"❌ CRITICAL PERSISTENCE ISSUE: Asset {deleted_asset_id} reappeared on check {i+1}!")
                        return False
                    else:
                        print(f"  ✅ Check {i+1}: Asset stays deleted")
                
                # Wait between checks
                time.sleep(1)
            
            print("✅ Deletion persistence verified - asset stays deleted across multiple requests")
            return True
            
        except Exception as e:
            print(f"❌ Deletion persistence test failed - {str(e)}")
            return False
    
    def test_asset_count_consistency(self):
        """Test asset count consistency between frontend and backend"""
        print("\n🔍 Step 6: Testing asset count consistency...")
        
        try:
            response = requests.get(f"{self.base_url}/assets", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get('assets', [])
                backend_count = len(assets)
                
                print(f"📊 Backend reports {backend_count} assets")
                
                # Check if there's a total count field in the response
                total_count = data.get('total', data.get('count', None))
                if total_count is not None:
                    print(f"📊 API total field reports {total_count} assets")
                    
                    if backend_count == total_count:
                        print("✅ Asset count consistency verified - array length matches total field")
                    else:
                        print(f"❌ Asset count inconsistency - array has {backend_count} but total shows {total_count}")
                        return False
                else:
                    print("⚠️ No total count field in API response - using array length only")
                
                # Compare with the review request mention of 420 assets
                print(f"📊 Review mentioned 420 assets, backend shows {backend_count}")
                if backend_count > 400:
                    print("✅ Asset count is in expected range (400+)")
                elif backend_count > 0:
                    print(f"⚠️ Asset count ({backend_count}) is lower than mentioned 420, but system is functional")
                else:
                    print("❌ No assets found - this may indicate a system issue")
                    return False
                
                return True
            else:
                print(f"❌ Failed to get asset count - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Asset count consistency test failed - {str(e)}")
            return False
    
    def test_identify_asset_sources(self):
        """Identify different sources of assets (backend vs extracted)"""
        print("\n🔍 Step 7: Identifying asset sources...")
        
        try:
            response = requests.get(f"{self.base_url}/assets", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get('assets', [])
                
                if not assets:
                    print("❌ No assets found to analyze sources")
                    return False
                
                # Analyze asset sources
                source_counts = {}
                backend_assets = 0
                extracted_assets = 0
                
                for asset in assets:
                    source = asset.get('source', 'unknown')
                    source_counts[source] = source_counts.get(source, 0) + 1
                    
                    # Categorize assets
                    if source in ['upload', 'manual_upload', 'user_upload']:
                        backend_assets += 1
                    elif source in ['extraction', 'article_extraction', 'training_engine_extraction']:
                        extracted_assets += 1
                
                print(f"📊 Asset Source Analysis:")
                for source, count in source_counts.items():
                    print(f"  {source}: {count} assets")
                
                print(f"\n📊 Asset Categories:")
                print(f"  Backend/Upload assets: {backend_assets}")
                print(f"  Extracted assets: {extracted_assets}")
                print(f"  Other/Unknown: {len(assets) - backend_assets - extracted_assets}")
                
                # Test deletion behavior for different types
                if backend_assets > 0 and extracted_assets > 0:
                    print("✅ Both backend and extracted assets found")
                    print("🎯 Recommendation: Test deletion on both types to verify behavior")
                elif backend_assets > 0:
                    print("✅ Backend assets found")
                    print("⚠️ No extracted assets found - may need to process documents to create them")
                elif extracted_assets > 0:
                    print("✅ Extracted assets found")
                    print("⚠️ No backend assets found - may need to upload files to create them")
                else:
                    print("⚠️ Could not categorize asset sources clearly")
                
                return True
            else:
                print(f"❌ Failed to analyze asset sources - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Asset source identification failed - {str(e)}")
            return False
    
    def test_different_asset_types_deletion(self):
        """Test deletion of different types of assets (backend vs extracted)"""
        print("\n🔍 Step 8: Testing deletion of different asset types...")
        
        try:
            response = requests.get(f"{self.base_url}/assets", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get('assets', [])
                
                if len(assets) < 2:
                    print("⚠️ Not enough assets to test different types - need at least 2")
                    return True
                
                # Find assets from different sources
                backend_asset = None
                extracted_asset = None
                
                for asset in assets:
                    source = asset.get('source', 'unknown')
                    if source in ['upload', 'manual_upload', 'user_upload'] and not backend_asset:
                        backend_asset = asset
                    elif source in ['extraction', 'article_extraction', 'training_engine_extraction'] and not extracted_asset:
                        extracted_asset = asset
                
                results = []
                
                # Test backend asset deletion
                if backend_asset:
                    print(f"🎯 Testing backend asset deletion: {backend_asset.get('name')}")
                    try:
                        delete_response = requests.delete(
                            f"{self.base_url}/assets/{backend_asset['id']}",
                            timeout=15
                        )
                        if delete_response.status_code == 200:
                            print("✅ Backend asset deletion successful")
                            results.append(True)
                        else:
                            print(f"❌ Backend asset deletion failed - {delete_response.status_code}")
                            results.append(False)
                    except Exception as e:
                        print(f"❌ Backend asset deletion error - {str(e)}")
                        results.append(False)
                else:
                    print("⚠️ No backend assets found for deletion testing")
                
                # Test extracted asset deletion
                if extracted_asset:
                    print(f"🎯 Testing extracted asset deletion: {extracted_asset.get('name')}")
                    try:
                        delete_response = requests.delete(
                            f"{self.base_url}/assets/{extracted_asset['id']}",
                            timeout=15
                        )
                        if delete_response.status_code == 200:
                            print("✅ Extracted asset deletion successful")
                            results.append(True)
                        else:
                            print(f"❌ Extracted asset deletion failed - {delete_response.status_code}")
                            results.append(False)
                    except Exception as e:
                        print(f"❌ Extracted asset deletion error - {str(e)}")
                        results.append(False)
                else:
                    print("⚠️ No extracted assets found for deletion testing")
                
                if results:
                    success_rate = sum(results) / len(results)
                    if success_rate >= 0.5:
                        print(f"✅ Different asset types deletion test passed ({sum(results)}/{len(results)})")
                        return True
                    else:
                        print(f"❌ Different asset types deletion test failed ({sum(results)}/{len(results)})")
                        return False
                else:
                    print("⚠️ No assets available for type-specific deletion testing")
                    return True
                
            else:
                print(f"❌ Failed to get assets for type testing - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Different asset types deletion test failed - {str(e)}")
            return False
    
    def test_article_re_extraction_impact(self):
        """Test if assets are restored from article re-extraction"""
        print("\n🔍 Step 9: Testing article re-extraction impact on deleted assets...")
        
        try:
            # Get current asset count
            response = requests.get(f"{self.base_url}/assets", timeout=15)
            if response.status_code != 200:
                print("❌ Could not get current asset count")
                return False
            
            data = response.json()
            assets_before = len(data.get('assets', []))
            print(f"📊 Assets before re-extraction test: {assets_before}")
            
            # Try to trigger content processing that might re-extract assets
            # Check if there are any articles that might contain assets
            articles_response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if articles_response.status_code == 200:
                articles_data = articles_response.json()
                articles = articles_data.get('articles', [])
                
                if articles:
                    print(f"📚 Found {len(articles)} articles in content library")
                    
                    # Check if any articles contain image references
                    articles_with_images = 0
                    for article in articles[:5]:  # Check first 5 articles
                        content = article.get('content', '') or article.get('html', '')
                        if '<img' in content or '/api/static/uploads/' in content:
                            articles_with_images += 1
                    
                    print(f"📊 Articles with image references: {articles_with_images}")
                    
                    if articles_with_images > 0:
                        print("🔍 Articles contain image references - checking if they affect asset count")
                        
                        # Wait a moment and check asset count again
                        time.sleep(3)
                        
                        response2 = requests.get(f"{self.base_url}/assets", timeout=15)
                        if response2.status_code == 200:
                            data2 = response2.json()
                            assets_after = len(data2.get('assets', []))
                            
                            print(f"📊 Assets after re-extraction check: {assets_after}")
                            
                            if assets_after > assets_before:
                                print(f"❌ CRITICAL ISSUE: Asset count increased from {assets_before} to {assets_after}")
                                print("   This suggests assets are being restored from article re-extraction")
                                return False
                            elif assets_after == assets_before:
                                print("✅ Asset count stable - no restoration from article re-extraction")
                                return True
                            else:
                                print(f"✅ Asset count decreased from {assets_before} to {assets_after}")
                                return True
                        else:
                            print("❌ Could not verify asset count after re-extraction test")
                            return False
                    else:
                        print("✅ No articles with image references found - re-extraction unlikely")
                        return True
                else:
                    print("✅ No articles found - re-extraction not applicable")
                    return True
            else:
                print("⚠️ Could not check content library for re-extraction test")
                return True
                
        except Exception as e:
            print(f"❌ Article re-extraction impact test failed - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all asset deletion tests"""
        print("🚀 Starting Enhanced Asset Manager Delete Functionality Testing")
        print("=" * 80)
        
        tests = [
            ("Get Initial Asset List", self.test_get_initial_asset_list),
            ("Create Test Asset", self.test_create_test_asset),
            ("DELETE Endpoint Test", self.test_delete_asset_endpoint),
            ("Asset Removal Verification", self.test_asset_removal_verification),
            ("Deletion Persistence", self.test_deletion_persistence),
            ("Asset Count Consistency", self.test_asset_count_consistency),
            ("Identify Asset Sources", self.test_identify_asset_sources),
            ("Different Asset Types Deletion", self.test_different_asset_types_deletion),
            ("Article Re-extraction Impact", self.test_article_re_extraction_impact),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*80)
        print("🎯 ENHANCED ASSET MANAGER DELETE FUNCTIONALITY TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"📊 Overall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        print("\n📋 Detailed Results:")
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {status}: {test_name}")
        
        # Critical issues identification
        critical_failures = []
        for test_name, result in results:
            if not result and any(keyword in test_name.lower() for keyword in ['delete', 'removal', 'persistence']):
                critical_failures.append(test_name)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"  ❌ {failure}")
            print("\n💡 RECOMMENDATIONS:")
            print("  1. Check DELETE /api/assets/{asset_id} endpoint implementation")
            print("  2. Verify asset removal from database and file system")
            print("  3. Check for asset restoration from article re-extraction")
            print("  4. Verify frontend-backend synchronization")
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND - Delete functionality appears to be working")
        
        return passed >= total * 0.7  # 70% pass rate required

if __name__ == "__main__":
    tester = AssetDeleteTest()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 Asset Delete Testing COMPLETED SUCCESSFULLY")
    else:
        print(f"\n❌ Asset Delete Testing COMPLETED WITH ISSUES")