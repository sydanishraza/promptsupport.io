"""
KE-M12: V2 Adaptive Adjustment System - Complete Implementation Migration
Migrated from server.py - Adaptive adjustment for balancing article lengths
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..llm.client import get_llm_client
from ._utils import create_processing_metadata

class V2AdaptiveAdjustmentSystem:
    """V2 Engine: Adaptive adjustment system for balancing article lengths and splits"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        
        self.word_count_thresholds = {
            "min_article_length": 300,  # Articles below this should be merged
            "max_section_length": 1200,  # Sections above this should be split
            "optimal_article_range": (500, 2000),  # Optimal article length range
            "optimal_section_range": (200, 800)   # Optimal section length range
        }
        
        self.granularity_expectations = {
            "shallow": {"min_articles": 1, "max_articles": 3, "target_length_per_article": 1500},
            "moderate": {"min_articles": 2, "max_articles": 8, "target_length_per_article": 1000},
            "deep": {"min_articles": 5, "max_articles": 20, "target_length_per_article": 800}
        }
    
    async def run(self, generated_articles_result: dict, **kwargs) -> dict:
        """Run adaptive adjustment on generated articles (new interface)"""
        try:
            print(f"⚖️ V2 ADAPTIVE ADJUSTMENT: Processing generated articles - engine=v2")
            
            analysis = kwargs.get('analysis', {})
            run_id = kwargs.get('run_id', 'unknown')
            
            return await self.perform_adaptive_adjustment(generated_articles_result, analysis, run_id)
            
        except Exception as e:
            print(f"❌ V2 ADAPTIVE ADJUSTMENT: Error processing content - {e}")
            return {
                'generated_articles': generated_articles_result.get('generated_articles', []),
                'error': str(e)
            }
    
    async def perform_adaptive_adjustment(self, generated_articles_result: dict, analysis: dict, run_id: str) -> dict:
        """V2 Engine: Perform adaptive adjustment for optimal article balance (legacy interface)"""
        try:
            print(f"⚖️ V2 ADAPTIVE ADJUSTMENT: Starting length and split balancing - run {run_id} - engine=v2")
            
            generated_articles = generated_articles_result.get('generated_articles', [])
            if not generated_articles:
                print(f"⚠️ V2 ADAPTIVE ADJUSTMENT: No articles to adjust - run {run_id} - engine=v2")
                return self._create_adjustment_result("no_articles", run_id, {"article_count": 0})
            
            # Step 1: Analyze current word counts and structure
            word_count_analysis = await self._analyze_word_counts(generated_articles, run_id)
            
            # Step 2: LLM-based balancing analysis
            llm_adjustment_result = await self._perform_llm_balancing_analysis(
                word_count_analysis, analysis, run_id
            )
            
            # Step 3: Programmatic adjustment validation
            programmatic_adjustment_result = await self._perform_programmatic_adjustment_analysis(
                word_count_analysis, analysis, run_id
            )
            
            # Step 4: Consolidate adjustment recommendations
            consolidated_adjustments = self._consolidate_adjustment_recommendations(
                llm_adjustment_result, programmatic_adjustment_result, run_id
            )
            
            # Step 5: Apply adaptive adjustments
            adjustment_application_result = await self._apply_adaptive_adjustments(
                generated_articles, consolidated_adjustments, run_id
            )
            
            # Step 6: Create final adjustment result
            final_adjustment_result = {
                **consolidated_adjustments,
                "adjustment_application": adjustment_application_result,
                "adjustment_id": f"adjustment_{run_id}_{int(datetime.utcnow().timestamp())}",
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
            
            adjustments_applied = adjustment_application_result.get('total_adjustments', 0)
            granularity_status = consolidated_adjustments.get('granularity_check', 'unknown')
            
            print(f"✅ V2 ADAPTIVE ADJUSTMENT: Applied {adjustments_applied} adjustments - {granularity_status} granularity - run {run_id} - engine=v2")
            return final_adjustment_result
            
        except Exception as e:
            print(f"❌ V2 ADAPTIVE ADJUSTMENT: Error performing adjustment - {e} - run {run_id} - engine=v2")
            return self._create_adjustment_result("error", run_id, {"error_message": str(e)})
    
    async def _analyze_word_counts(self, generated_articles: list, run_id: str) -> dict:
        """Analyze word counts and structure of generated articles"""
        try:
            print(f"📊 V2 ADAPTIVE ADJUSTMENT: Analyzing word counts - run {run_id}")
            
            articles_analysis = []
            
            for i, article_result in enumerate(generated_articles):
                article_data = article_result.get('article_data', {})
                html_content = article_data.get('html', '')
                
                # Count words (simple approximation)
                word_count = len(html_content.split()) if html_content else 0
                
                # Extract sections (simplified)
                sections = self._extract_sections_from_html(html_content)
                
                articles_analysis.append({
                    'article_index': i,
                    'article_id': article_data.get('id', f'article_{i}'),
                    'title': article_data.get('title', f'Article {i+1}'),
                    'word_count': word_count,
                    'sections': sections,
                    'sections_count': len(sections)
                })
            
            return {
                'articles': articles_analysis,
                'total_articles': len(articles_analysis),
                'total_word_count': sum(a['word_count'] for a in articles_analysis),
                'average_article_length': sum(a['word_count'] for a in articles_analysis) / len(articles_analysis) if articles_analysis else 0,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ V2 ADAPTIVE ADJUSTMENT: Error analyzing word counts - {e}")
            return {'articles': [], 'total_articles': 0, 'total_word_count': 0}
    
    def _extract_sections_from_html(self, html_content: str) -> list:
        """Extract sections from HTML content"""
        import re
        
        sections = []
        
        # Find headings
        heading_pattern = r'<h([1-6])[^>]*>(.*?)</h\1>'
        headings = re.findall(heading_pattern, html_content, re.IGNORECASE)
        
        # Split content by headings and count words in each section
        if headings:
            parts = re.split(heading_pattern, html_content, flags=re.IGNORECASE)
            
            for i, (level, heading_text) in enumerate(headings):
                # Get content after this heading (approximation)
                section_content = parts[i*3 + 3] if i*3 + 3 < len(parts) else ''
                word_count = len(section_content.split()) if section_content else 0
                
                sections.append({
                    'level': int(level),
                    'heading': heading_text,
                    'word_count': word_count
                })
        
        return sections
    
    async def _perform_llm_balancing_analysis(self, word_count_analysis: dict, analysis: dict, run_id: str) -> dict:
        """Use LLM to analyze article balance and suggest adjustments"""
        try:
            print(f"🤖 V2 ADAPTIVE ADJUSTMENT: LLM balancing analysis - run {run_id}")
            
            articles = word_count_analysis.get('articles', [])
            granularity = analysis.get('granularity', 'moderate')
            
            # Create analysis prompt
            articles_summary = []
            for article in articles:
                articles_summary.append(f"- {article['title']}: {article['word_count']} words, {article['sections_count']} sections")
            
            system_message = """You are a content balancing expert. Analyze article lengths and suggest improvements.

Your task is to evaluate if articles are well-balanced for readability and suggest adjustments.

Evaluation criteria:
- Articles should be 500-2000 words for optimal readability
- Sections should be 200-800 words
- Overall content should match the specified granularity level

Return suggestions for merging short articles, splitting long ones, or rebalancing sections."""

            user_message = f"""Analyze this content structure for granularity: {granularity}

Current articles:
{chr(10).join(articles_summary)}

Total articles: {len(articles)}
Average length: {word_count_analysis.get('average_article_length', 0):.0f} words

Granularity expectations for {granularity}:
{self.granularity_expectations.get(granularity, {})}

Provide analysis and specific recommendations for improvement."""

            # Use LLM for analysis
            llm_response = await self.llm_client.complete(
                system_message=system_message,
                user_message=user_message,
                temperature=0.3,
                max_tokens=1000
            )
            
            if llm_response:
                return {
                    'analysis_method': 'llm_based',
                    'llm_response': llm_response,
                    'recommendation_confidence': 'high',
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            else:
                return self._get_fallback_llm_analysis(articles, granularity)
                
        except Exception as e:
            print(f"❌ V2 ADAPTIVE ADJUSTMENT: Error in LLM analysis - {e}")
            return self._get_fallback_llm_analysis(word_count_analysis.get('articles', []), analysis.get('granularity', 'moderate'))
    
    def _get_fallback_llm_analysis(self, articles: list, granularity: str) -> dict:
        """Fallback analysis when LLM is unavailable"""
        return {
            'analysis_method': 'rule_based_fallback',
            'recommendation': f"Review {len(articles)} articles for {granularity} granularity balance",
            'recommendation_confidence': 'medium',
            'fallback_reason': 'LLM unavailable'
        }
    
    async def _perform_programmatic_adjustment_analysis(self, word_count_analysis: dict, analysis: dict, run_id: str) -> dict:
        """Perform programmatic analysis of adjustment needs"""
        try:
            print(f"🔢 V2 ADAPTIVE ADJUSTMENT: Programmatic analysis - run {run_id}")
            
            articles = word_count_analysis.get('articles', [])
            granularity = analysis.get('granularity', 'moderate')
            
            # Validate article count against granularity
            current_article_count = len(articles)
            expectations = self.granularity_expectations.get(granularity, {"min_articles": 1, "max_articles": 10})
            
            granularity_validation = {
                "current_count": current_article_count,
                "expected_range": f"{expectations['min_articles']}-{expectations['max_articles']}",
                "alignment": "aligned" if expectations['min_articles'] <= current_article_count <= expectations['max_articles'] else "out_of_range",
                "target_length_per_article": expectations.get('target_length_per_article', 1000)
            }
            
            # Calculate length distribution
            word_counts = [article['word_count'] for article in articles]
            length_distribution = {
                "min_length": min(word_counts) if word_counts else 0,
                "max_length": max(word_counts) if word_counts else 0,
                "average_length": sum(word_counts) / len(word_counts) if word_counts else 0,
                "median_length": sorted(word_counts)[len(word_counts)//2] if word_counts else 0,
                "total_length": sum(word_counts)
            }
            
            # Readability analysis
            readability_analysis = {
                "articles_too_short": len([a for a in articles if a['word_count'] < self.word_count_thresholds['min_article_length']]),
                "articles_too_long": len([a for a in articles if a['word_count'] > self.word_count_thresholds['optimal_article_range'][1]]),
                "articles_optimal": len([a for a in articles if self.word_count_thresholds['optimal_article_range'][0] <= a['word_count'] <= self.word_count_thresholds['optimal_article_range'][1]]),
                "sections_too_long": sum(len([s for s in article.get('sections', []) if s['word_count'] > self.word_count_thresholds['max_section_length']]) for article in articles),
                "readability_score": self._calculate_readability_score(articles)
            }
            
            programmatic_result = {
                "granularity_validation": granularity_validation,
                "length_distribution": length_distribution,
                "readability_analysis": readability_analysis,
                "adjustment_priority": self._determine_adjustment_priority(granularity_validation, readability_analysis),
                "analysis_method": "programmatic_validation"
            }
            
            print(f"🔍 V2 ADAPTIVE ADJUSTMENT: Programmatic validation complete - Readability score: {readability_analysis['readability_score']:.2f} - run {run_id} - engine=v2")
            return programmatic_result
            
        except Exception as e:
            print(f"❌ V2 ADAPTIVE ADJUSTMENT: Error in programmatic adjustment analysis - {e} - run {run_id} - engine=v2")
            return {
                "granularity_validation": {"alignment": "unknown"},
                "length_distribution": {},
                "readability_analysis": {"readability_score": 0.5},
                "adjustment_priority": "medium",
                "analysis_method": "error"
            }
    
    def _calculate_readability_score(self, articles: list) -> float:
        """Calculate readability score based on length distribution"""
        try:
            if not articles:
                return 0.0
            
            optimal_count = 0
            total_articles = len(articles)
            
            for article in articles:
                word_count = article['word_count']
                
                # Score based on article length
                if self.word_count_thresholds['optimal_article_range'][0] <= word_count <= self.word_count_thresholds['optimal_article_range'][1]:
                    optimal_count += 1
                
                # Penalty for sections that are too long
                long_sections = len([s for s in article.get('sections', []) if s['word_count'] > self.word_count_thresholds['max_section_length']])
                if long_sections > 0:
                    optimal_count -= 0.2 * long_sections  # Penalty for long sections
            
            # Calculate score (0.0 to 1.0)
            readability_score = max(0.0, min(1.0, optimal_count / total_articles))
            return readability_score
            
        except Exception as e:
            return 0.5  # Default moderate readability
    
    def _determine_adjustment_priority(self, granularity_validation: dict, readability_analysis: dict) -> str:
        """Determine adjustment priority based on analysis"""
        try:
            granularity_aligned = granularity_validation.get('alignment') == 'aligned'
            readability_score = readability_analysis.get('readability_score', 0.5)
            articles_too_short = readability_analysis.get('articles_too_short', 0)
            sections_too_long = readability_analysis.get('sections_too_long', 0)
            
            # High priority: Major readability issues or granularity misalignment
            if not granularity_aligned or readability_score < 0.3 or articles_too_short > 2 or sections_too_long > 3:
                return "high"
            
            # Medium priority: Moderate issues
            elif readability_score < 0.7 or articles_too_short > 0 or sections_too_long > 0:
                return "medium"
            
            # Low priority: Minor optimizations
            else:
                return "low"
                
        except Exception as e:
            return "medium"  # Default priority
    
    def _consolidate_adjustment_recommendations(self, llm_result: dict, programmatic_result: dict, run_id: str) -> dict:
        """Consolidate LLM and programmatic adjustment recommendations"""
        try:
            adjustment_priority = programmatic_result.get('adjustment_priority', 'medium')
            granularity_check = programmatic_result.get('granularity_validation', {}).get('alignment', 'unknown')
            readability_score = programmatic_result.get('readability_analysis', {}).get('readability_score', 0.5)
            
            return {
                'llm_analysis': llm_result,
                'programmatic_analysis': programmatic_result,
                'consolidated_priority': adjustment_priority,
                'granularity_check': granularity_check,
                'readability_score': readability_score,
                'recommendation': f"Priority: {adjustment_priority}, Granularity: {granularity_check}, Readability: {readability_score:.2f}",
                'consolidation_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ V2 ADAPTIVE ADJUSTMENT: Error consolidating recommendations - {e}")
            return {'consolidated_priority': 'medium', 'granularity_check': 'unknown'}
    
    async def _apply_adaptive_adjustments(self, generated_articles: list, consolidated_adjustments: dict, run_id: str) -> dict:
        """Apply adaptive adjustments to articles"""
        try:
            print(f"🔧 V2 ADAPTIVE ADJUSTMENT: Applying adjustments - run {run_id}")
            
            priority = consolidated_adjustments.get('consolidated_priority', 'medium')
            
            # For now, return the articles without modification
            # In a full implementation, this would apply actual adjustments
            
            return {
                'adjusted_articles': generated_articles,  # No modifications for now
                'total_adjustments': 0,
                'adjustment_types': [],
                'adjustment_summary': f"Analysis completed with {priority} priority. No automatic adjustments applied.",
                'application_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ V2 ADAPTIVE ADJUSTMENT: Error applying adjustments - {e}")
            return {
                'adjusted_articles': generated_articles,
                'total_adjustments': 0,
                'error': str(e)
            }
    
    def _create_adjustment_result(self, status: str, run_id: str, additional_data: dict = None) -> dict:
        """Create standardized adjustment result"""
        result = {
            "adjustment_id": f"adjustment_{run_id}_{int(datetime.utcnow().timestamp())}",
            "run_id": run_id,
            "adjustment_status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "engine": "v2"
        }
        
        if additional_data:
            result.update(additional_data)
        
        return result


print("✅ KE-M12: V2 Adaptive Adjustment System migrated from server.py")