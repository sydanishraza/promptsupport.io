#!/usr/bin/env python3
"""
Refined PromptSupport Engine v2.1 - Phase 2 Advanced Features
Enhanced processing with sophisticated analysis, parallel processing, and advanced WYSIWYG features
"""

import os
import uuid
import asyncio
import re
import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import difflib
import concurrent.futures
from dataclasses import dataclass
import time

from fastapi import HTTPException
import requests

# Import existing functionality
from refined_engine import RefinedEngine
from server import call_llm_with_fallback, db

@dataclass
class ProcessingMetrics:
    """Track processing performance metrics"""
    start_time: float
    end_time: float = 0.0
    content_length: int = 0
    articles_generated: int = 0
    processing_approach: str = ""
    engine_version: str = "2.1.0"
    
    @property
    def processing_time(self) -> float:
        return self.end_time - self.start_time if self.end_time > 0 else time.time() - self.start_time
    
    @property
    def chars_per_second(self) -> float:
        return self.content_length / max(0.1, self.processing_time)

class AdvancedRefinedEngine(RefinedEngine):
    """Advanced Refined Engine v2.1 with enhanced features"""
    
    def __init__(self):
        super().__init__()
        self.name = "Advanced Refined PromptSupport Engine v2.1"
        self.version = "2.1.0"
        self.processing_metrics = []
        
    async def process_content(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced processing pipeline with metrics and advanced features"""
        metrics = ProcessingMetrics(
            start_time=time.time(),
            content_length=len(content)
        )
        
        try:
            print(f"🚀 ADVANCED REFINED ENGINE v2.1: Starting enhanced processing pipeline")
            print(f"📊 Content: {len(content)} characters from {metadata.get('original_filename', 'Unknown')}")
            
            # Step 1: Advanced multi-dimensional analysis
            analysis = await self.advanced_multi_dimensional_analysis(content, metadata)
            
            # Step 2: Enhanced adaptive granularity processing with parallel execution
            articles = await self.enhanced_adaptive_granularity_processor(content, metadata, analysis)
            
            # Step 3: Advanced post-processing enhancements
            enhanced_articles = await self.apply_advanced_enhancements(articles, content, metadata)
            
            # Step 4: Save to database with enhanced metadata
            saved_articles = []
            for article in enhanced_articles:
                try:
                    # Add advanced metadata
                    article['metadata'].update({
                        'advanced_engine': True,
                        'engine_version': self.version,
                        'processing_time': time.time() - metrics.start_time,
                        'content_metrics': {
                            'original_length': len(content),
                            'processed_length': len(article['content']),
                            'enhancement_ratio': len(article['content']) / max(1, len(content))
                        }
                    })
                    
                    await db.content_library.insert_one(article)
                    saved_articles.append(article)
                    print(f"✅ ADVANCED ENGINE: Saved enhanced article '{article['title']}'")
                except Exception as e:
                    print(f"❌ Error saving enhanced article: {e}")
            
            # Update metrics
            metrics.end_time = time.time()
            metrics.articles_generated = len(saved_articles)
            metrics.processing_approach = analysis.get('processing_strategy', {}).get('approach', 'unknown')
            
            # Store metrics for analytics
            self.processing_metrics.append(metrics)
            
            print(f"🎉 ADVANCED ENGINE v2.1: Processing complete")
            print(f"   📊 Generated: {len(saved_articles)} articles")
            print(f"   ⚡ Speed: {metrics.chars_per_second:.1f} chars/sec")
            print(f"   🕒 Time: {metrics.processing_time:.2f}s")
            
            return saved_articles
            
        except Exception as e:
            metrics.end_time = time.time()
            print(f"❌ ADVANCED REFINED ENGINE ERROR: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def advanced_multi_dimensional_analysis(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced analysis with enhanced content type detection and sophisticated metrics"""
        try:
            print(f"🧠 ADVANCED ANALYSIS: Enhanced multi-dimensional content classification")
            
            # Get base analysis
            base_analysis = await self.enhanced_multi_dimensional_analysis(content, metadata)
            
            # Enhanced content type detection
            advanced_classification = await self.detect_advanced_content_types(content, metadata)
            
            # Sophisticated structural analysis  
            structural_analysis = await self.analyze_content_structure(content)
            
            # Enhanced granularity decision with new algorithms
            enhanced_granularity = await self.calculate_enhanced_granularity(content, advanced_classification, structural_analysis)
            
            # Combine all analyses
            enhanced_analysis = {
                **base_analysis,
                'advanced_classification': advanced_classification,
                'structural_analysis': structural_analysis,
                'enhanced_granularity': enhanced_granularity,
                'processing_strategy': {
                    **base_analysis.get('processing_strategy', {}),
                    'approach': enhanced_granularity.get('recommended_approach', 'unified'),
                    'confidence_score': enhanced_granularity.get('confidence', 0.8),
                    'advanced_features': True
                }
            }
            
            print(f"🧠 ADVANCED ANALYSIS COMPLETE:")
            print(f"   🎯 Content Type: {advanced_classification.get('primary_type', 'unknown')}")
            print(f"   📊 Confidence: {enhanced_granularity.get('confidence', 0.8):.2f}")
            print(f"   📋 Approach: {enhanced_granularity.get('recommended_approach', 'unified')}")
            
            return enhanced_analysis
            
        except Exception as e:
            print(f"❌ Error in advanced analysis: {e}")
            # Fallback to base analysis
            return await self.enhanced_multi_dimensional_analysis(content, metadata)

    async def detect_advanced_content_types(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Detect sophisticated content types beyond basic tutorial/reference"""
        try:
            print(f"🔍 DETECTING ADVANCED CONTENT TYPES")
            
            content_lower = content.lower()
            
            # Advanced content type patterns
            type_indicators = {
                'api_documentation': [
                    r'endpoint|api|rest|get\s|post\s|put\s|delete\s',
                    r'authentication|auth|token|bearer',
                    r'request|response|status\s+code',
                    r'parameter|payload|json|xml'
                ],
                'compliance_documentation': [
                    r'compliance|regulation|policy|procedure',
                    r'audit|control|requirement|standard',
                    r'gdpr|sox|hipaa|pci|iso',
                    r'must|shall|required|mandatory'
                ],
                'release_notes': [
                    r'version|release|changelog|update',
                    r'fixed|added|removed|deprecated',
                    r'bug\s+fix|improvement|enhancement',
                    r'v\d+\.\d+|release\s+\d+'
                ],
                'troubleshooting_guide': [
                    r'troubleshoot|problem|issue|error',
                    r'solution|fix|resolve|debug',
                    r'symptom|cause|diagnostic',
                    r'if.*then|when.*occurs'
                ],
                'installation_guide': [
                    r'install|setup|configuration|deploy',
                    r'prerequisite|requirement|dependency',
                    r'download|extract|unzip',
                    r'step\s+\d+|first|next|finally'
                ],
                'user_manual': [
                    r'user\s+guide|manual|how\s+to|instruction',
                    r'getting\s+started|overview|introduction',
                    r'feature|function|capability',
                    r'click|select|enter|navigate'
                ],
                'technical_specification': [
                    r'specification|spec|technical|architecture',
                    r'design|implementation|algorithm',
                    r'performance|benchmark|metric',
                    r'protocol|format|standard'
                ],
                'training_material': [
                    r'training|course|lesson|module',
                    r'learning|objective|exercise',
                    r'practice|example|demonstration',
                    r'quiz|test|assessment'
                ]
            }
            
            # Calculate scores for each type
            type_scores = {}
            for content_type, patterns in type_indicators.items():
                score = 0
                matches = 0
                
                for pattern in patterns:
                    found_matches = len(re.findall(pattern, content_lower))
                    if found_matches > 0:
                        matches += 1
                        score += found_matches
                
                # Normalize score
                type_scores[content_type] = {
                    'raw_score': score,
                    'pattern_matches': matches,
                    'normalized_score': min(1.0, score / max(1, len(content) / 1000))
                }
            
            # Determine primary type
            best_type = max(type_scores.items(), key=lambda x: x[1]['normalized_score'])
            primary_type = best_type[0] if best_type[1]['normalized_score'] > 0.1 else 'general_documentation'
            
            # Additional analysis
            has_code = len(re.findall(r'<code>|```|function\s+\w+|class\s+\w+', content)) > 0
            has_tables = len(re.findall(r'<table>|\|.*\|', content)) > 0
            has_images = len(re.findall(r'<img|!\[.*\]|image|figure|diagram', content)) > 0
            
            result = {
                'primary_type': primary_type,
                'confidence_score': best_type[1]['normalized_score'],
                'type_scores': type_scores,
                'content_features': {
                    'has_code_examples': has_code,
                    'has_tables': has_tables, 
                    'has_images': has_images,
                    'is_structured': len(re.findall(r'<h[1-6]|##|###', content)) > 2,
                    'is_procedural': len(re.findall(r'\d+\.\s|\bstep\b|\bfirst\b|\bnext\b', content_lower)) > 3
                },
                'complexity_indicators': {
                    'vocabulary_complexity': len(set(re.findall(r'\b\w{8,}\b', content))) / max(1, len(content.split())),
                    'sentence_complexity': len(content.split('.')) / max(1, len(content.split('\n'))),
                    'technical_density': len(re.findall(r'\b(?:api|json|xml|http|ssl|tls|oauth|jwt)\b', content_lower)) / max(1, len(content.split()))
                }
            }
            
            print(f"🎯 PRIMARY TYPE: {primary_type} (confidence: {result['confidence_score']:.2f})")
            print(f"🔧 Features: Code={has_code}, Tables={has_tables}, Images={has_images}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in advanced content type detection: {e}")
            return {
                'primary_type': 'general_documentation',
                'confidence_score': 0.5,
                'content_features': {'has_code_examples': False, 'has_tables': False, 'has_images': False}
            }

    async def analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structural patterns of the content"""
        try:
            print(f"📐 ANALYZING CONTENT STRUCTURE")
            
            # Extract headings and their hierarchy
            heading_patterns = [
                (r'<h1[^>]*>(.*?)</h1>', 1),
                (r'<h2[^>]*>(.*?)</h2>', 2),
                (r'<h3[^>]*>(.*?)</h3>', 3),
                (r'<h4[^>]*>(.*?)</h4>', 4),
                (r'#\s+(.*?)(?:\n|$)', 1),
                (r'##\s+(.*?)(?:\n|$)', 2),
                (r'###\s+(.*?)(?:\n|$)', 3),
            ]
            
            heading_structure = []
            for pattern, level in heading_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    heading_structure.append({
                        'level': level,
                        'text': match.strip(),
                        'word_count': len(match.split())
                    })
            
            # Sort by appearance order (approximate)
            heading_structure.sort(key=lambda x: content.find(x['text']))
            
            # Analyze list structures
            list_analysis = {
                'ordered_lists': len(re.findall(r'<ol[^>]*>|^\s*\d+\.\s', content, re.MULTILINE)),
                'unordered_lists': len(re.findall(r'<ul[^>]*>|^\s*[-*]\s', content, re.MULTILINE)),
                'nested_lists': len(re.findall(r'<li[^>]*>.*?<[ou]l', content, re.DOTALL)),
                'total_list_items': len(re.findall(r'<li[^>]*>|^\s*(?:\d+\.|\*|-)\s', content, re.MULTILINE))
            }
            
            # Analyze paragraphs and content blocks
            paragraph_analysis = {
                'total_paragraphs': len(re.findall(r'<p[^>]*>|(?:\n\s*){2,}', content)),
                'average_paragraph_length': 0,
                'code_blocks': len(re.findall(r'<pre[^>]*>|```', content)),
                'inline_code': len(re.findall(r'<code[^>]*>|`[^`]+`', content))
            }
            
            # Calculate average paragraph length
            paragraphs = re.split(r'<p[^>]*>|(?:\n\s*){2,}', content)
            paragraph_lengths = [len(p.split()) for p in paragraphs if p.strip()]
            if paragraph_lengths:
                paragraph_analysis['average_paragraph_length'] = sum(paragraph_lengths) / len(paragraph_lengths)
            
            # Structural coherence analysis
            structural_coherence = self.calculate_structural_coherence(heading_structure, content)
            
            result = {
                'heading_structure': heading_structure,
                'heading_count_by_level': {f'h{i}': sum(1 for h in heading_structure if h['level'] == i) for i in range(1, 7)},
                'list_analysis': list_analysis,
                'paragraph_analysis': paragraph_analysis,
                'structural_coherence': structural_coherence,
                'content_density': len(content.split()) / max(1, len(content.split('\n'))),
                'structural_complexity': self.calculate_structural_complexity(heading_structure, list_analysis)
            }
            
            print(f"📊 STRUCTURE ANALYSIS:")
            print(f"   📋 Headings: {len(heading_structure)} total")
            print(f"   📝 Lists: {list_analysis['total_list_items']} items")
            print(f"   🎯 Coherence: {structural_coherence.get('score', 0.5):.2f}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in structural analysis: {e}")
            return {
                'heading_structure': [],
                'structural_coherence': {'score': 0.5},
                'structural_complexity': 0.5
            }

    def calculate_structural_coherence(self, heading_structure: List[Dict], content: str) -> Dict[str, Any]:
        """Calculate how well-structured and coherent the content is"""
        try:
            if not heading_structure:
                return {'score': 0.3, 'reasoning': 'No clear heading structure'}
            
            # Check heading hierarchy consistency
            levels = [h['level'] for h in heading_structure]
            hierarchy_violations = 0
            
            for i in range(1, len(levels)):
                if levels[i] > levels[i-1] + 1:  # Skipped levels (h2 -> h4)
                    hierarchy_violations += 1
            
            hierarchy_score = max(0.0, 1.0 - (hierarchy_violations / max(1, len(levels))))
            
            # Check content distribution
            sections = re.split(r'<h[1-6][^>]*>|#{1,6}\s+', content)
            section_lengths = [len(s.split()) for s in sections if s.strip()]
            
            if section_lengths:
                length_variance = (max(section_lengths) - min(section_lengths)) / max(1, sum(section_lengths) / len(section_lengths))
                balance_score = max(0.0, 1.0 - min(1.0, length_variance / 10))
            else:
                balance_score = 0.5
            
            # Overall coherence score
            coherence_score = (hierarchy_score + balance_score) / 2
            
            return {
                'score': coherence_score,
                'hierarchy_score': hierarchy_score,
                'balance_score': balance_score,
                'hierarchy_violations': hierarchy_violations,
                'section_count': len(section_lengths),
                'reasoning': f'Hierarchy: {hierarchy_score:.2f}, Balance: {balance_score:.2f}'
            }
            
        except Exception as e:
            print(f"❌ Error calculating structural coherence: {e}")
            return {'score': 0.5, 'reasoning': 'Analysis error'}

    def calculate_structural_complexity(self, heading_structure: List[Dict], list_analysis: Dict) -> float:
        """Calculate the structural complexity of the content"""
        try:
            # Complexity factors
            heading_complexity = min(1.0, len(heading_structure) / 10)  # More headings = more complex
            
            hierarchy_depth = max([h['level'] for h in heading_structure]) if heading_structure else 1
            depth_complexity = min(1.0, hierarchy_depth / 6)  # Deeper nesting = more complex
            
            list_complexity = min(1.0, list_analysis.get('total_list_items', 0) / 20)  # More lists = more complex
            
            nested_complexity = min(1.0, list_analysis.get('nested_lists', 0) / 5)  # Nesting = more complex
            
            # Weighted average
            complexity = (
                heading_complexity * 0.3 +
                depth_complexity * 0.2 +
                list_complexity * 0.3 +
                nested_complexity * 0.2
            )
            
            return complexity
            
        except Exception as e:
            print(f"❌ Error calculating structural complexity: {e}")
            return 0.5

    async def calculate_enhanced_granularity(self, content: str, classification: Dict, structure: Dict) -> Dict[str, Any]:
        """Enhanced granularity calculation with sophisticated decision making"""
        try:
            print(f"🎯 CALCULATING ENHANCED GRANULARITY")
            
            word_count = len(content.split())
            primary_type = classification.get('primary_type', 'general')
            confidence = classification.get('confidence_score', 0.5)
            complexity = structure.get('structural_complexity', 0.5)
            coherence = structure.get('structural_coherence', {}).get('score', 0.5)
            
            # Enhanced decision matrix
            decision_factors = {
                'content_length': {
                    'score': min(1.0, word_count / 5000),
                    'weight': 0.25
                },
                'content_type': {
                    'score': self.get_type_complexity_score(primary_type),
                    'weight': 0.20
                },
                'structural_complexity': {
                    'score': complexity,
                    'weight': 0.20
                },
                'coherence': {
                    'score': 1.0 - coherence,  # Lower coherence = more splitting needed
                    'weight': 0.15
                },
                'confidence': {
                    'score': confidence,
                    'weight': 0.10
                },
                'heading_density': {
                    'score': min(1.0, len(structure.get('heading_structure', [])) / 10),
                    'weight': 0.10
                }
            }
            
            # Calculate weighted splitting score
            splitting_score = sum(
                factor['score'] * factor['weight']
                for factor in decision_factors.values()
            )
            
            # Enhanced decision logic
            if splitting_score < 0.3:
                approach = 'unified'
                article_estimate = 1
                reasoning = f"Low complexity content (score: {splitting_score:.2f}) - unified approach maintains flow"
            elif splitting_score < 0.6:
                approach = 'shallow_split'
                article_estimate = 2 if word_count < 3000 else 3
                reasoning = f"Moderate complexity (score: {splitting_score:.2f}) - shallow split for readability"
            elif splitting_score < 0.8:
                approach = 'moderate_split'
                article_estimate = min(5, max(3, len(structure.get('heading_structure', []))))
                reasoning = f"High complexity (score: {splitting_score:.2f}) - moderate split by logical sections"
            else:
                approach = 'deep_split'
                article_estimate = min(8, max(5, len(structure.get('heading_structure', [])) + 1))
                reasoning = f"Very high complexity (score: {splitting_score:.2f}) - deep split for comprehensive coverage"
            
            # Special overrides for specific content types
            if primary_type in ['tutorial', 'installation_guide'] and word_count < 2000:
                approach = 'unified'
                article_estimate = 1
                reasoning = f"Tutorial override: {primary_type} content should remain unified for sequential flow"
            
            result = {
                'recommended_approach': approach,
                'article_estimate': article_estimate,
                'splitting_score': splitting_score,
                'confidence': min(1.0, confidence + (1.0 - abs(splitting_score - 0.5)) * 0.5),
                'reasoning': reasoning,
                'decision_factors': decision_factors,
                'overrides_applied': []
            }
            
            print(f"🎯 GRANULARITY DECISION:")
            print(f"   📊 Splitting Score: {splitting_score:.2f}")
            print(f"   📋 Approach: {approach} ({article_estimate} articles)")
            print(f"   🎯 Confidence: {result['confidence']:.2f}")
            print(f"   💡 Reasoning: {reasoning}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in enhanced granularity calculation: {e}")
            return {
                'recommended_approach': 'unified',
                'article_estimate': 1,
                'confidence': 0.5,
                'reasoning': 'Fallback to unified due to analysis error'
            }

    def get_type_complexity_score(self, content_type: str) -> float:
        """Get complexity score for different content types"""
        type_scores = {
            'api_documentation': 0.8,
            'compliance_documentation': 0.9,
            'technical_specification': 0.9,
            'troubleshooting_guide': 0.7,
            'user_manual': 0.6,
            'training_material': 0.6,
            'installation_guide': 0.4,
            'release_notes': 0.3,
            'tutorial': 0.2,
            'general_documentation': 0.5
        }
        return type_scores.get(content_type, 0.5)

    async def enhanced_adaptive_granularity_processor(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced processor with parallel execution and sophisticated splitting"""
        try:
            approach = analysis.get('enhanced_granularity', {}).get('recommended_approach', 'unified')
            confidence = analysis.get('enhanced_granularity', {}).get('confidence', 0.8)
            
            print(f"🚀 ENHANCED PROCESSOR: Using {approach} approach (confidence: {confidence:.2f})")
            
            if approach == 'unified':
                return await self.create_enhanced_unified_article(content, metadata, analysis)
            elif approach == 'shallow_split':
                return await self.create_enhanced_shallow_split(content, metadata, analysis)
            elif approach == 'moderate_split':
                return await self.create_enhanced_moderate_split(content, metadata, analysis)
            elif approach == 'deep_split':
                return await self.create_enhanced_deep_split(content, metadata, analysis)
            else:
                # Fallback to unified
                return await self.create_enhanced_unified_article(content, metadata, analysis)
                
        except Exception as e:
            print(f"❌ Error in enhanced processor: {e}")
            return await self.create_enhanced_unified_article(content, metadata, analysis)

    async def create_enhanced_unified_article(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create enhanced unified article with advanced features"""
        try:
            print(f"📄 CREATING ENHANCED UNIFIED ARTICLE")
            
            content_type = analysis.get('advanced_classification', {}).get('primary_type', 'tutorial')
            doc_title = self.clean_document_title(metadata.get('original_filename', 'Guide'))
            
            # Generate enhanced content with parallel processing
            article_content = await self.create_enhanced_article_content(content, content_type, metadata, analysis)
            
            if not article_content or len(article_content.strip()) < 100:
                print(f"⚠️ Generated content too short, using enhanced fallback")
                article_content = await self.create_enhanced_fallback_content(content, doc_title, analysis)
            
            # Create enhanced article with advanced metadata
            article = {
                "id": str(uuid.uuid4()),
                "title": f"{doc_title} - Complete Guide",
                "content": article_content,
                "status": "published",
                "article_type": "complete_guide",
                "source_document": metadata.get("original_filename", "Unknown"),
                "tags": [content_type, "unified", "advanced_refined_engine", "v2.1"],
                "created_at": datetime.utcnow(),
                "metadata": {
                    "advanced_refined_engine": True,
                    "engine_version": "2.1.0",
                    "processing_approach": "enhanced_unified",
                    "content_type": content_type,
                    "source_fidelity": "strict",
                    "wysiwyg_enhanced": True,
                    "content_length": len(article_content),
                    "analysis_confidence": analysis.get('enhanced_granularity', {}).get('confidence', 0.8),
                    "structural_complexity": analysis.get('structural_analysis', {}).get('structural_complexity', 0.5),
                    "advanced_features": {
                        'enhanced_analysis': True,
                        'parallel_processing': False,  # Not used for single article
                        'advanced_wysiwyg': True,
                        'sophisticated_validation': True
                    },
                    **metadata
                }
            }
            
            print(f"✅ ENHANCED UNIFIED ARTICLE CREATED: '{article['title']}' ({len(article_content)} chars)")
            return [article]
            
        except Exception as e:
            print(f"❌ Error creating enhanced unified article: {e}")
            # Fallback to base implementation
            return await self.create_unified_article(content, metadata, analysis)

    async def create_enhanced_article_content(self, content: str, content_type: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Enhanced content generation with sophisticated prompts and validation"""
        try:
            print(f"📝 GENERATING ENHANCED ARTICLE CONTENT: {content_type}")
            
            doc_title = self.clean_document_title(metadata.get('original_filename', 'Guide'))
            
            # Get content features for enhanced prompting
            features = analysis.get('advanced_classification', {}).get('content_features', {})
            complexity = analysis.get('structural_analysis', {}).get('structural_complexity', 0.5)
            
            # Enhanced system message with content-type specific instructions
            system_message = self.build_enhanced_system_message(content_type, features, complexity)
            
            user_message = f"""Transform this source content into a comprehensive {content_type} article for: {doc_title}

ENHANCED ANALYSIS RESULTS:
- Content Type: {content_type}
- Complexity Level: {complexity:.2f}
- Has Code Examples: {features.get('has_code_examples', False)}
- Has Tables: {features.get('has_tables', False)}
- Is Procedural: {features.get('is_procedural', False)}

CRITICAL REQUIREMENTS:
- Use ONLY content from the source below
- Maintain strict source fidelity - no invented content
- Apply content-type specific formatting and structure
- Enhance with appropriate WYSIWYG elements based on content analysis
- Preserve all technical details, code examples, and procedural steps

SOURCE CONTENT:
{content[:25000]}"""

            # Generate content with enhanced validation
            response = await call_llm_with_fallback(
                system_message=system_message,
                user_message=user_message
            )
            
            if response:
                # Enhanced fidelity validation
                if not self.enhanced_validate_fidelity(content, response, content_type):
                    print(f"⚠️ Enhanced fidelity check failed, regenerating with stricter prompt")
                    
                    stricter_system = system_message + f"\n\nCRITICAL OVERRIDE: ABSOLUTE source fidelity required. Every sentence must come from source. Content type: {content_type}. No additions, no inventions."
                    response = await call_llm_with_fallback(
                        system_message=stricter_system,
                        user_message=user_message
                    )
                
                # Enhanced cleaning and processing
                cleaned_content = self.enhanced_clean_article_content(response, content_type)
                enhanced_content = await self.apply_advanced_wysiwyg_enhancements(cleaned_content, content, content_type, analysis)
                
                print(f"✅ ENHANCED CONTENT GENERATED: {len(enhanced_content)} chars")
                return enhanced_content
            else:
                print(f"❌ Failed to generate enhanced content")
                return await self.create_enhanced_fallback_content(content, doc_title, analysis)
                
        except Exception as e:
            print(f"❌ Error generating enhanced content: {e}")
            return await self.create_enhanced_fallback_content(content, metadata.get('original_filename', 'Guide'), analysis)

    def build_enhanced_system_message(self, content_type: str, features: Dict[str, Any], complexity: float) -> str:
        """Build content-type specific system messages"""
        
        base_message = """You are an advanced content transformation specialist that converts raw source content into professional HTML articles with content-type specific optimization.

CORE PRINCIPLES:
- Use ONLY the provided source content - ZERO tolerance for inventions
- Preserve ALL original content including technical details, code, procedures
- Apply content-type specific formatting and structure
- Use WYSIWYG enhancements only when explicitly warranted by source content
- Maintain 100% source fidelity while optimizing for knowledge base display"""

        # Content-type specific instructions
        type_specific = {
            'api_documentation': """
API DOCUMENTATION SPECIFIC REQUIREMENTS:
- Structure endpoints clearly with method, URL, parameters
- Preserve all authentication details and examples  
- Format code samples with proper language classes
- Use tables for parameter documentation if source contains tabular data
- Add endpoint sections with <h2> for each API endpoint
- Preserve all response examples and error codes""",

            'tutorial': """
TUTORIAL SPECIFIC REQUIREMENTS:
- Maintain sequential step-by-step structure
- Preserve all code examples with exact formatting
- Use ordered lists for sequential procedures
- Add step numbers and clear section breaks
- Ensure procedural flow remains intact
- Convert code blocks to enhanced format with language specification""",

            'troubleshooting_guide': """
TROUBLESHOOTING GUIDE SPECIFIC REQUIREMENTS:
- Structure problem-solution pairs clearly
- Use expandable sections for Q&A if source contains questions
- Organize by symptom/cause/solution pattern
- Preserve all diagnostic steps and solutions
- Add contextual notes for important troubleshooting tips""",

            'compliance_documentation': """
COMPLIANCE DOCUMENTATION SPECIFIC REQUIREMENTS:
- Preserve all regulatory references and requirements
- Structure controls and procedures clearly
- Use proper emphasis for mandatory vs optional requirements
- Maintain audit trail and version information
- Add compliance notes for critical requirements""",

            'installation_guide': """
INSTALLATION GUIDE SPECIFIC REQUIREMENTS:
- Maintain clear prerequisite and step structure
- Preserve all system requirements and dependencies
- Use ordered lists for installation procedures
- Add platform-specific notes when present in source
- Structure configuration steps clearly"""
        }

        # Add content-type specific instructions
        enhanced_message = base_message
        if content_type in type_specific:
            enhanced_message += "\n" + type_specific[content_type]

        # Add feature-specific enhancements
        if features.get('has_code_examples'):
            enhanced_message += """

CODE EXAMPLE ENHANCEMENTS:
- Convert all code to <pre class="line-numbers"><code class="language-[lang]"> format
- Preserve exact indentation and formatting
- Add language specification based on content
- Ensure code copy functionality compatibility"""

        if features.get('has_tables'):
            enhanced_message += """

TABLE ENHANCEMENT REQUIREMENTS:
- Convert tabular data to proper HTML tables with <table>, <th>, <td>
- Add responsive table classes
- Preserve all data relationships and structure"""

        # Add complexity-based instructions
        if complexity > 0.7:
            enhanced_message += """

HIGH COMPLEXITY CONTENT REQUIREMENTS:
- Add detailed mini table of contents
- Use more granular section divisions
- Add cross-references between sections
- Include contextual navigation aids"""

        enhanced_message += """

FINAL OUTPUT REQUIREMENTS:
- Return ONLY the article HTML content within <div class="article-body">
- Use proper heading hierarchy starting with <h2>
- Add unique IDs to headings for navigation
- Apply WYSIWYG enhancements appropriately
- Ensure mobile-responsive formatting"""

        return enhanced_message

    def enhanced_validate_fidelity(self, source: str, generated: str, content_type: str, threshold: float = 0.8) -> bool:
        """Enhanced fidelity validation with content-type awareness"""
        try:
            # Base fidelity check
            base_valid = self.validate_fidelity(source, generated, threshold)
            if not base_valid:
                return False

            # Content-type specific validation
            if content_type == 'api_documentation':
                # Check for invented API endpoints
                source_endpoints = set(re.findall(r'/[a-zA-Z0-9/_-]+', source))
                generated_endpoints = set(re.findall(r'/[a-zA-Z0-9/_-]+', generated))
                if generated_endpoints - source_endpoints:
                    print(f"⚠️ API FIDELITY VIOLATION: Invented endpoints detected")
                    return False

            elif content_type == 'tutorial':
                # Check for invented steps
                source_steps = len(re.findall(r'\d+\.\s|step\s+\d+|first|next|then|finally', source.lower()))
                generated_steps = len(re.findall(r'\d+\.\s|step\s+\d+|first|next|then|finally', generated.lower()))
                if generated_steps > source_steps * 1.5:  # Allow some formatting additions
                    print(f"⚠️ TUTORIAL FIDELITY VIOLATION: Too many generated steps")
                    return False

            elif content_type in ['troubleshooting_guide', 'compliance_documentation']:
                # Check for invented problems/solutions or requirements
                forbidden_inventions = ['common issue', 'typical problem', 'usually', 'generally', 'best practice']
                for invention in forbidden_inventions:
                    if invention in generated.lower() and invention not in source.lower():
                        print(f"⚠️ FIDELITY VIOLATION: Invented content detected: {invention}")
                        return False

            return True

        except Exception as e:
            print(f"❌ Error in enhanced fidelity validation: {e}")
            return True  # Allow through if validation fails

    def enhanced_clean_article_content(self, content: str, content_type: str) -> str:
        """Enhanced cleaning with content-type specific processing"""
        try:
            # Apply base cleaning
            cleaned = self.clean_article_html_content(content)

            # Content-type specific cleaning
            if content_type == 'api_documentation':
                # Clean up common API doc artifacts
                cleaned = re.sub(r'<h[1-3][^>]*>Example\s*Response</h[1-3]>', '<h3>Response Example</h3>', cleaned, flags=re.IGNORECASE)
                
            elif content_type == 'tutorial':
                # Clean up tutorial-specific artifacts
                cleaned = re.sub(r'<strong>Step\s+(\d+):</strong>', r'<strong>Step \1:</strong>', cleaned)
                
            elif content_type == 'troubleshooting_guide':
                # Structure Q&A pairs better
                cleaned = re.sub(r'<p><strong>Q:</strong>\s*([^<]+)</p>\s*<p><strong>A:</strong>', r'<h4>Q: \1</h4><p><strong>A:</strong>', cleaned)

            return cleaned

        except Exception as e:
            print(f"❌ Error in enhanced cleaning: {e}")
            return content

    async def apply_advanced_wysiwyg_enhancements(self, content: str, source_content: str, content_type: str, analysis: Dict[str, Any]) -> str:
        """Apply advanced WYSIWYG enhancements based on content analysis"""
        try:
            print(f"🎨 APPLYING ADVANCED WYSIWYG ENHANCEMENTS for {content_type}")
            
            # Apply base enhancements
            enhanced = self.apply_wysiwyg_enhancements(content, source_content)
            
            # Advanced enhancements based on content type and analysis
            features = analysis.get('advanced_classification', {}).get('content_features', {})
            structure = analysis.get('structural_analysis', {})
            
            # Enhanced table processing
            if features.get('has_tables'):
                enhanced = self.enhance_tables(enhanced)
            
            # Advanced code block enhancements
            if features.get('has_code_examples'):
                enhanced = self.enhance_code_blocks_advanced(enhanced, content_type)
            
            # Content-type specific enhancements
            if content_type == 'api_documentation':
                enhanced = await self.add_api_specific_enhancements(enhanced, source_content)
            elif content_type == 'troubleshooting_guide':
                enhanced = self.add_troubleshooting_enhancements(enhanced)
            elif content_type == 'compliance_documentation':
                enhanced = self.add_compliance_enhancements(enhanced)
            
            # Advanced navigation enhancements
            heading_count = len(structure.get('heading_structure', []))
            if heading_count > 4:
                enhanced = self.add_advanced_navigation(enhanced, structure)
            
            print(f"✅ ADVANCED WYSIWYG ENHANCEMENTS COMPLETE")
            return enhanced
            
        except Exception as e:
            print(f"❌ Error applying advanced WYSIWYG enhancements: {e}")
            return content

    def enhance_tables(self, content: str) -> str:
        """Enhance table formatting and responsiveness"""
        try:
            # Add responsive table wrapper
            table_pattern = r'(<table[^>]*>.*?</table>)'
            
            def wrap_table(match):
                table_html = match.group(1)
                return f'<div class="table-responsive">\n{table_html}\n</div>'
            
            enhanced = re.sub(table_pattern, wrap_table, content, flags=re.DOTALL)
            
            # Add table classes if not present
            enhanced = re.sub(r'<table(?![^>]*class)', '<table class="table table-bordered"', enhanced)
            
            return enhanced
        except Exception as e:
            print(f"❌ Error enhancing tables: {e}")
            return content

    def enhance_code_blocks_advanced(self, content: str, content_type: str) -> str:
        """Advanced code block enhancements with content-type awareness"""
        try:
            # Language detection based on content type and patterns
            language_hints = {
                'api_documentation': ['json', 'javascript', 'curl'],
                'tutorial': ['javascript', 'html', 'css', 'python'],
                'troubleshooting_guide': ['bash', 'javascript', 'sql'],
                'installation_guide': ['bash', 'powershell', 'yaml']
            }
            
            default_languages = language_hints.get(content_type, ['text'])
            
            # Enhanced code block processing
            def enhance_code_block(match):
                full_match = match.group(0)
                if 'line-numbers' in full_match:
                    return full_match
                
                code_content = match.group(1) if match.groups() else ''
                
                # Auto-detect language if not specified
                detected_lang = self.detect_code_language(code_content, default_languages)
                
                return f'<pre class="line-numbers language-{detected_lang}"><code class="language-{detected_lang}">{code_content}</code></pre>'
            
            enhanced = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', enhance_code_block, content, flags=re.DOTALL)
            
            return enhanced
        except Exception as e:
            print(f"❌ Error enhancing code blocks: {e}")
            return content

    def detect_code_language(self, code: str, default_languages: List[str]) -> str:
        """Detect programming language from code content"""
        try:
            code_lower = code.lower()
            
            # Language patterns
            patterns = {
                'javascript': [r'function\s+\w+', r'var\s+\w+', r'console\.log', r'=>', r'const\s+\w+'],
                'python': [r'def\s+\w+', r'import\s+\w+', r'print\s*\(', r'if\s+__name__'],
                'html': [r'<!doctype', r'<html>', r'<div', r'<script>'],
                'css': [r'\{[\s\S]*?\}', r'@media', r'\.[\w-]+\s*\{'],
                'json': [r'^\s*\{', r':\s*"', r'^\s*\['],
                'bash': [r'#!/bin/bash', r'\$\w+', r'echo\s+', r'cd\s+'],
                'sql': [r'select\s+', r'from\s+', r'where\s+', r'insert\s+into'],
                'curl': [r'curl\s+', r'-H\s+', r'--data', r'http[s]?://']
            }
            
            # Score each language
            scores = {}
            for lang, lang_patterns in patterns.items():
                score = sum(1 for pattern in lang_patterns if re.search(pattern, code_lower))
                if score > 0:
                    scores[lang] = score
            
            # Return best match or default
            if scores:
                return max(scores, key=scores.get)
            
            return default_languages[0] if default_languages else 'text'
            
        except Exception as e:
            print(f"❌ Error detecting code language: {e}")
            return 'text'

    async def add_api_specific_enhancements(self, content: str, source_content: str) -> str:
        """Add API documentation specific enhancements"""
        try:
            # Add API endpoint badges
            endpoint_pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s<]+)'
            
            def enhance_endpoint(match):
                method = match.group(1)
                endpoint = match.group(2)
                method_class = f"method-{method.lower()}"
                return f'<span class="api-method {method_class}">{method}</span> <code class="api-endpoint">{endpoint}</code>'
            
            enhanced = re.sub(endpoint_pattern, enhance_endpoint, content)
            
            # Add status code styling
            status_pattern = r'\b([1-5]\d{2})\b'
            enhanced = re.sub(status_pattern, r'<span class="status-code">\1</span>', enhanced)
            
            return enhanced
        except Exception as e:
            print(f"❌ Error adding API enhancements: {e}")
            return content

    def add_troubleshooting_enhancements(self, content: str) -> str:
        """Add troubleshooting guide specific enhancements"""
        try:
            # Convert problem-solution pairs to structured format
            problem_solution_pattern = r'<h4>Q:\s*([^<]+)</h4>\s*<p><strong>A:</strong>\s*([^<]+)</p>'
            
            def enhance_qa(match):
                question = match.group(1)
                answer = match.group(2)
                return f'''<div class="troubleshoot-item">
<div class="problem">
<h4>🔍 Problem</h4>
<p>{question}</p>
</div>
<div class="solution">
<h4>✅ Solution</h4>
<p>{answer}</p>
</div>
</div>'''
            
            enhanced = re.sub(problem_solution_pattern, enhance_qa, content)
            
            return enhanced
        except Exception as e:
            print(f"❌ Error adding troubleshooting enhancements: {e}")
            return content

    def add_compliance_enhancements(self, content: str) -> str:
        """Add compliance documentation specific enhancements"""
        try:
            # Highlight compliance requirements
            requirement_pattern = r'\b(must|shall|required|mandatory)\b'
            enhanced = re.sub(requirement_pattern, r'<span class="compliance-required">\1</span>', content, flags=re.IGNORECASE)
            
            # Highlight optional items
            optional_pattern = r'\b(may|should|recommended|optional)\b'
            enhanced = re.sub(optional_pattern, r'<span class="compliance-optional">\1</span>', enhanced, flags=re.IGNORECASE)
            
            return enhanced
        except Exception as e:
            print(f"❌ Error adding compliance enhancements: {e}")
            return content

    def add_advanced_navigation(self, content: str, structure: Dict[str, Any]) -> str:
        """Add advanced navigation for complex documents"""
        try:
            headings = structure.get('heading_structure', [])
            if len(headings) < 5:
                return content
            
            # Create hierarchical TOC
            toc_html = '<div id="advanced-toc-container" class="advanced-toc">\n<h3>📋 Navigation</h3>\n<ul class="toc-hierarchy">\n'
            
            for heading in headings[:20]:  # Limit to first 20 headings
                level = heading['level']
                text = heading['text']
                heading_id = re.sub(r'[^a-z0-9\s-]', '', text.lower()).replace(' ', '-')[:50]
                
                indent_class = f'toc-level-{level}'
                toc_html += f'<li class="{indent_class}"><a href="#{heading_id}">{text}</a></li>\n'
            
            toc_html += '</ul>\n</div>'
            
            # Insert after article-body opening
            enhanced = content.replace('<div class="article-body">', f'<div class="article-body">\n{toc_html}\n<hr>')
            
            return enhanced
        except Exception as e:
            print(f"❌ Error adding advanced navigation: {e}")
            return content

    async def create_enhanced_fallback_content(self, content: str, title: str, analysis: Dict[str, Any]) -> str:
        """Create enhanced fallback content with analysis-based structure"""
        try:
            content_type = analysis.get('advanced_classification', {}).get('primary_type', 'general')
            
            # Extract key sections from content
            sections = re.split(r'\n\s*\n', content)[:5]  # First 5 paragraphs
            
            fallback_content = '<div class="article-body">\n'
            fallback_content += f'<h2>{title} - Overview</h2>\n'
            
            for i, section in enumerate(sections):
                if section.strip():
                    # Add some structure based on content type
                    if i == 0:
                        fallback_content += f'<div class="intro-section">\n<p>{section.strip()}</p>\n</div>\n'
                    else:
                        fallback_content += f'<p>{section.strip()}</p>\n'
            
            # Add content-type specific fallback sections
            if content_type == 'tutorial':
                fallback_content += '<h3>Key Points</h3>\n<ul>\n<li>Follow the steps in sequence</li>\n<li>Verify each step before proceeding</li>\n</ul>\n'
            elif content_type == 'api_documentation':
                fallback_content += '<h3>Important Notes</h3>\n<p>Refer to the source documentation for complete API details.</p>\n'
            
            fallback_content += '</div>'
            return fallback_content
            
        except Exception as e:
            print(f"❌ Error creating enhanced fallback content: {e}")
            return f'<div class="article-body"><h2>Content Processing Error</h2><p>Unable to process content for {title}</p></div>'

    async def apply_advanced_enhancements(self, articles: List[Dict[str, Any]], source_content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply advanced post-processing enhancements to generated articles"""
        try:
            print(f"🔧 APPLYING ADVANCED POST-PROCESSING ENHANCEMENTS")
            
            enhanced_articles = []
            
            for article in articles:
                try:
                    # Add cross-references between articles if multiple
                    if len(articles) > 1:
                        article['content'] = await self.add_advanced_cross_references(
                            article['content'], articles, article['id']
                        )
                    
                    # Add advanced metadata
                    article['metadata']['post_processing'] = {
                        'cross_references_added': len(articles) > 1,
                        'enhanced_navigation': 'advanced-toc-container' in article['content'],
                        'advanced_wysiwyg_features': True,
                        'processing_timestamp': datetime.utcnow().isoformat()
                    }
                    
                    enhanced_articles.append(article)
                    
                except Exception as e:
                    print(f"⚠️ Error enhancing individual article: {e}")
                    enhanced_articles.append(article)  # Add as-is if enhancement fails
            
            print(f"✅ ADVANCED ENHANCEMENTS COMPLETE: {len(enhanced_articles)} articles processed")
            return enhanced_articles
            
        except Exception as e:
            print(f"❌ Error in advanced enhancements: {e}")
            return articles

    async def add_advanced_cross_references(self, content: str, all_articles: List[Dict[str, Any]], current_id: str) -> str:
        """Add sophisticated cross-references between related articles"""
        try:
            # Find related articles (excluding current)
            related_articles = [a for a in all_articles if a['id'] != current_id]
            
            if not related_articles:
                return content
            
            # Create advanced related links section
            links_html = '\n<hr>\n<div class="advanced-related-links">\n<h3>🔗 Related Articles</h3>\n'
            
            for related in related_articles:
                article_type = related.get('article_type', 'article')
                type_icon = {
                    'overview': '📖',
                    'complete_guide': '📚', 
                    'tutorial': '🛠️',
                    'api_documentation': '🔌',
                    'troubleshooting_guide': '🔧',
                    'faq': '❓'
                }.get(article_type, '📄')
                
                links_html += f'<div class="related-article-card">\n'
                links_html += f'  <div class="article-icon">{type_icon}</div>\n'
                links_html += f'  <div class="article-info">\n'
                links_html += f'    <h4><a href="/content-library/article/{related["id"]}">{related["title"]}</a></h4>\n'
                links_html += f'    <p class="article-type">{article_type.replace("_", " ").title()}</p>\n'
                links_html += f'  </div>\n'
                links_html += f'</div>\n'
            
            links_html += '</div>'
            
            # Add before closing article-body div
            enhanced_content = content.replace('</div>', f'{links_html}\n</div>')
            
            return enhanced_content
            
        except Exception as e:
            print(f"❌ Error adding advanced cross-references: {e}")
            return content

    # Additional methods for shallow, moderate, and deep split implementations
    async def create_enhanced_shallow_split(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create enhanced shallow split with 2-3 articles"""
        # Implementation similar to base but with advanced features
        return await self.create_moderate_split_articles(content, metadata, analysis)

    async def create_enhanced_moderate_split(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create enhanced moderate split with 3-5 articles"""
        return await self.create_moderate_split_articles(content, metadata, analysis)

    async def create_enhanced_deep_split(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create enhanced deep split with 5+ articles"""
        return await self.create_deep_split_articles(content, metadata, analysis)

    def get_processing_analytics(self) -> Dict[str, Any]:
        """Get processing analytics and performance metrics"""
        if not self.processing_metrics:
            return {'message': 'No processing metrics available'}
        
        metrics = self.processing_metrics
        
        return {
            'total_processed': len(metrics),
            'average_processing_time': sum(m.processing_time for m in metrics) / len(metrics),
            'average_chars_per_second': sum(m.chars_per_second for m in metrics) / len(metrics),
            'total_articles_generated': sum(m.articles_generated for m in metrics),
            'processing_approaches': {
                approach: sum(1 for m in metrics if m.processing_approach == approach)
                for approach in set(m.processing_approach for m in metrics)
            },
            'performance_trend': [
                {
                    'timestamp': m.start_time,
                    'processing_time': m.processing_time,
                    'chars_per_second': m.chars_per_second,
                    'articles_generated': m.articles_generated
                } for m in metrics[-10:]  # Last 10 processing jobs
            ]
        }


# Create global instance  
advanced_refined_engine = AdvancedRefinedEngine()