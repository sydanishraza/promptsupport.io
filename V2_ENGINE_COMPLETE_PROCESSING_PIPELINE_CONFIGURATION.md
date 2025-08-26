# V2 ENGINE COMPLETE PROCESSING PIPELINE CONFIGURATION
## Comprehensive Configuration for All Formats - Audit Document

**Generated:** December 2024  
**Engine Version:** V2.0  
**Architecture:** Multi-Dimensional Content Processing with Evidence-Based Fidelity

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

### Core Principles
- **Single Source of Truth:** V2-only publishing with complete coverage verification
- **Evidence-Based Fidelity:** All content tagged with source block IDs (≥95% target)
- **Multi-Dimensional Analysis:** Audience, granularity, and content type detection
- **Strict Format Compliance:** Woolf-aligned technical writing standards
- **No Media Embedding:** Media stored separately with reference-only approach

### Processing Formats Supported
1. **Text Content** (`process_text_content_v2`)
2. **File Uploads** (via `/api/v2/upload-file` endpoint)
3. **URL Processing** (via `/api/v2/process-url` endpoint)

---

## 📋 V2 PROCESSING PIPELINE - COMPLETE STEP SEQUENCE

### STEP 1: Input Validation & Format Detection
**Entry Points:**
- Text: `process_text_content_v2(content: str, metadata: Dict[str, Any])`
- Files: Upload endpoint with format detection
- URLs: Scraping endpoint with content extraction

**Configuration:**
```python
metadata_required = {
    'title': str,
    'content_type': str,  # 'text', 'file', 'url'
    'original_filename': str,
    'processing_options': dict
}
```

### STEP 2: Content Extraction & Normalization
**Processor:** `V2ContentExtractor`
**Function:** `extract_raw_text(content, title)`

**Configuration:**
```python
v2_extractor = V2ContentExtractor()

extraction_config = {
    'block_types': [
        'text', 'code', 'list', 'table', 'quote', 
        'heading', 'media_reference', 'link'
    ],
    'media_handling': 'reference_only',  # No embedding
    'normalization': 'structured_blocks',
    'preserve_formatting': True
}
```

**Output:** `NormalizedDocument` with blocks and media references

### STEP 3: Document Storage
**Database:** `normalized_documents` collection
**Function:** `store_normalized_document(normalized_doc)`

### STEP 4: Multi-Dimensional Analysis
**Processor:** `V2MultiDimensionalAnalyzer`
**Function:** `analyze_normalized_document(normalized_doc, run_id)`

**Configuration:**
```python
v2_analyzer = V2MultiDimensionalAnalyzer()

analysis_dimensions = {
    'audience_detection': {
        'types': ['end_user', 'developer', 'admin', 'business'],
        'confidence_threshold': 0.7
    },
    'granularity_analysis': {
        'levels': ['shallow', 'moderate', 'deep'],
        'content_complexity_factors': ['technical_depth', 'procedural_steps', 'code_examples']
    },
    'content_type_classification': {
        'types': ['tutorial', 'reference', 'troubleshooting', 'integration_guide'],
        'feature_extraction': True
    }
}
```

### STEP 5: Global Outline Planning
**Processor:** `V2GlobalOutlinePlanner`
**Function:** `create_global_outline(normalized_doc, analysis, run_id)`

**Configuration:**
```python
v2_global_planner = V2GlobalOutlinePlanner()

outline_config = {
    'block_assignment': '100_percent_coverage',  # All blocks must be assigned
    'article_splitting_strategy': 'functional_coherence',
    'max_articles_per_document': 10,
    'min_blocks_per_article': 3,
    'discarded_blocks_handling': 'explicit_reasoning'
}
```

### STEP 6: Per-Article Outline Creation
**Processor:** `V2PerArticleOutlinePlanner`
**Function:** `create_per_article_outlines(normalized_doc, outline, analysis, run_id)`

**Configuration:**
```python
v2_per_article_outline_planner = V2PerArticleOutlinePlanner()

per_article_config = {
    'outline_depth': 'hierarchical',
    'section_planning': 'audience_aware',
    'block_to_section_mapping': 'explicit',
    'faq_integration': 'automatic',
    'related_links_planning': 'context_aware'
}
```

### STEP 6.5: Section-Grounded Prewrite Pass
**Processor:** `V2PrewriteSystem`
**Function:** `execute_prewrite_pass(content, content_type, article_outlines, per_article_outlines, analysis, run_id)`

**Configuration:**
```python
v2_prewrite_system = V2PrewriteSystem()

prewrite_config = {
    'fact_to_claim_transformation': True,
    'section_grounding': 'block_id_mapping',
    'evidence_preparation': {
        'target_coverage': 0.95,  # ≥95% paragraphs tagged
        'source_attribution': 'block_id_references'
    },
    'claim_validation': 'source_backed_only'
}
```

**Storage:** `v2_prewrite_results` collection

### STEP 7: Final Article Generation
**Processor:** `V2ArticleGenerator`
**Function:** `generate_final_articles(normalized_doc, per_article_outlines, analysis, run_id)`

**Configuration:**
```python
v2_article_generator = V2ArticleGenerator()

generation_config = {
    'format_compliance': 'strict_woolf_standards',
    'article_structure': {
        'no_h1_in_content': True,  # Title handled by frontend
        'required_sections': ['intro', 'mini_toc', 'main_body', 'faqs', 'related_links'],
        'mini_toc_format': 'simple_bullets',  # Links added by style processor
        'heading_hierarchy': 'h2_h3_only'
    },
    'audience_styling': {
        'end_user': {'tone': 'friendly', 'focus': 'practical_guidance'},
        'developer': {'tone': 'technical', 'focus': 'implementation_details'},
        'admin': {'tone': 'authoritative', 'focus': 'configuration_management'},
        'business': {'tone': 'professional', 'focus': 'business_value'}
    },
    'llm_integration': {
        'primary_method': 'llm_generation',
        'fallback_method': 'rule_based_generation',
        'content_validation': 'required_fields_check'
    }
}
```

**LLM System Message Configuration:**
```python
llm_instructions = {
    'format_requirements': [
        'NO H1 tags in content body',
        'Simple bullet list for Mini-TOC',
        'Use <ol> for procedural steps',
        'Consolidate code blocks',
        'No id attributes on headings'  # Added by style processor
    ],
    'content_requirements': [
        '100% source block coverage',
        'Insert [MISSING] for insufficient info',
        'No media embedding',
        'Audience-appropriate styling'
    ]
}
```

### STEP 7.6: Evidence Tagging
**Processor:** `V2EvidenceTaggingSystem`
**Function:** `tag_content_with_evidence(articles, blocks, prewrite_result, run_id)`

**Configuration:**
```python
v2_evidence_tagging_system = V2EvidenceTaggingSystem()

evidence_config = {
    'tagging_target': 0.95,  # ≥95% paragraphs must be tagged
    'evidence_attributes': {
        'data_evidence': 'block_id_list',
        'data_confidence': 'high|medium|low',
        'data_source_type': 'direct|inferred|synthesized'
    },
    'excluded_content': ['faqs', 'related_links', 'navigation'],
    'validation': 'fidelity_enforcement'
}
```

**Storage:** `v2_evidence_tagging_results` collection

### STEP 7.5: Woolf-Aligned Style Processing + Structural Lint
**Processor:** `V2StyleProcessor`
**Function:** `apply_style_formatting(content, content_type, articles, prewrite_data, analysis, run_id)`

**Configuration:**
```python
v2_style_processor = V2StyleProcessor()

style_config = {
    'woolf_terminology': {
        'api key': 'API key',
        'integration id': 'Integration ID',
        'sandbox api token': 'Sandbox API token'
    },
    'structural_requirements': {
        'intro_sentences': {'min': 2, 'max': 3},
        'paragraph_lines': {'max': 4},
        'table_rows': {'max': 10},
        'faq_sentence_limit': {'max': 2}
    },
    'comprehensive_post_processing': {
        'h1_removal': 'convert_to_h2',
        'list_type_detection': 'procedural_to_ordered',
        'code_consolidation': 'merge_consecutive_blocks',
        'toc_anchor_processing': 'html_links_with_ids'
    },
    'anchor_processing': {
        'method': 'sequential_assignment_to_existing_ids',
        'id_coordination': 'prioritize_section_style_ids',
        'toc_detection': 'beautifulsoup_ul_analysis',
        'broken_link_tracking': True
    }
}
```

**Post-Processing Methods:**
1. `_apply_comprehensive_post_processing()` - Master coordinator
2. `_remove_h1_from_content()` - H1 to H2 conversion
3. `_fix_list_types_comprehensive()` - UL to OL for procedural content
4. `_fix_code_consolidation_comprehensive()` - Merge fragmented code blocks
5. `_process_clickable_anchors()` - TOC to HTML anchor links

**Critical Content Update:**
```python
# Apply formatted content as main article content
for article in articles:
    if style_result.success and formatted_content:
        article['content'] = formatted_content  # Frontend uses this field
```

**Storage:** `v2_style_results` collection

### STEP 7.7: Related Links Generation
**Processor:** `V2RelatedLinksSystem`
**Function:** `generate_related_links(article, content, blocks, run_id)`

**Configuration:**
```python
v2_related_links_system = V2RelatedLinksSystem()

related_links_config = {
    'content_library_indexing': {
        'index_type': 'keyword_and_semantic',
        'update_frequency': '5_minutes',
        'similarity_threshold': 0.7
    },
    'internal_links': {
        'max_links': 5,
        'source': 'content_library',
        'deduplication': 'same_topic_filtering'
    },
    'external_links': {
        'source': 'source_content_and_blocks_only',
        'validation': 'broken_link_prevention',
        'max_links': 3
    },
    'merge_strategy': '3_to_6_total_links'
}
```

**Storage:** `v2_related_links_results` collection

### STEP 7.8: Intelligent Gap Filling
**Processor:** `V2GapFillingSystem`
**Function:** `fill_content_gaps(articles, content, blocks, run_id, enrich_mode)`

**Configuration:**
```python
v2_gap_filling_system = V2GapFillingSystem()

gap_filling_config = {
    'gap_patterns': ['[MISSING]', '[PLACEHOLDER]', '[TBD]', '[TODO]', '[FILL]'],
    'gap_type_inference': [
        'api_detail', 'code_example', 'configuration', 
        'authentication', 'procedure_step', 'generic_content'
    ],
    'enrich_modes': {
        'internal': 'in_corpus_retrieval_only',  # Default
        'external': 'standard_patterns_allowed'   # Opt-in
    },
    'in_corpus_retrieval': {
        'source_blocks_search': True,
        'content_library_search': True,
        'max_relevant_blocks': 10,
        'relevance_threshold': 0.6
    },
    'llm_patching': {
        'confidence_levels': ['high', 'low'],
        'support_block_tracking': 'evidence_attribution',
        'patch_length': '1_to_2_sentences',
        'fidelity_maintenance': '>=0.90'
    }
}
```

**Storage:** `v2_gap_filling_results` collection

### STEP 7.9: Code Block Normalization & Beautification
**Processor:** `V2CodeNormalizationSystem`
**Function:** `normalize_code_blocks(articles, blocks, prewrite_result, run_id)`

**Configuration:**
```python
v2_code_normalization_system = V2CodeNormalizationSystem()

code_config = {
    'prism_formatting': {
        'classes': ['line-numbers'],
        'language_detection': 'automatic',
        'attributes': ['data-lang', 'data-start']
    },
    'consolidation': {
        'merge_consecutive': True,
        'remove_figure_tags': True,
        'remove_code_toolbar_classes': True
    },
    'html_escaping': 'proper_character_encoding',
    'mobile_responsiveness': 'css_optimization'
}
```

**Storage:** `v2_code_normalization_results` collection

### STEP 8: Comprehensive Validation
**Processor:** `V2ValidationSystem`
**Function:** `validate_generated_articles(normalized_doc, generated_articles_result, analysis, run_id)`

**Configuration:**
```python
v2_validation_system = V2ValidationSystem()

validation_config = {
    'fidelity_validation': {
        'evidence_tagging_rate': '>=0.95',
        'source_fidelity_score': '>=0.90',
        'block_coverage': '100_percent'
    },
    'coverage_validation': {
        'all_blocks_assigned': True,
        'no_orphaned_content': True,
        'explicit_discard_reasoning': True
    },
    'placeholder_validation': {
        'missing_content_acceptable': '[MISSING] with justification',
        'no_lorem_ipsum': True,
        'no_placeholder_urls': True
    },
    'style_validation': {
        'woolf_compliance': True,
        'structural_requirements': True,
        'terminology_consistency': True
    }
}
```

**Storage:** `v2_validation_results` collection

### STEP 9: Cross-Article QA
**Processor:** `V2CrossArticleQASystem`
**Function:** `perform_cross_article_qa(generated_articles_result, run_id)`

**Configuration:**
```python
v2_cross_article_qa_system = V2CrossArticleQASystem()

qa_config = {
    'deduplication': {
        'content_similarity_threshold': 0.85,
        'merge_similar_sections': True
    },
    'link_validation': {
        'internal_links_check': True,
        'external_links_validation': True,
        'broken_link_detection': True
    },
    'faq_consolidation': {
        'merge_duplicate_questions': True,
        'consistency_check': True
    },
    'terminology_consistency': {
        'woolf_standards_enforcement': True,
        'cross_article_term_alignment': True
    }
}
```

**Storage:** `v2_qa_results` collection

### STEP 10: Adaptive Adjustment
**Processor:** `V2AdaptiveAdjustmentSystem`
**Function:** `perform_adaptive_adjustment(generated_articles_result, analysis, run_id)`

**Configuration:**
```python
v2_adaptive_adjustment_system = V2AdaptiveAdjustmentSystem()

adjustment_config = {
    'length_optimization': {
        'target_ranges': {
            'tutorial': '1500-3000_words',
            'reference': '800-1500_words',
            'troubleshooting': '600-1200_words'
        },
        'split_strategy': 'functional_coherence'
    },
    'readability_optimization': {
        'target_score': '>=0.7',
        'factors': ['sentence_length', 'paragraph_structure', 'technical_density']
    },
    'balance_optimization': {
        'code_to_text_ratio': 'content_type_appropriate',
        'section_length_variance': 'minimize'
    }
}
```

**Storage:** `v2_adjustment_results` collection

### STEP 11: V2-Only Publishing Flow
**Processor:** `V2PublishingSystem`
**Function:** `publish_v2_content(articles, generated_articles_result, validation_result, qa_result, adjustment_result, run_id)`

**Configuration:**
```python
v2_publishing_system = V2PublishingSystem()

publishing_config = {
    'eligibility_requirements': {
        'validation_status': 'passed',
        'coverage_achieved': '100_percent',
        'evidence_tagging_rate': '>=0.95'
    },
    'content_library_structure': {
        'fields': [
            'html', 'markdown', 'toc', 'faq', 'related_links',
            'provenance_map', 'metrics', 'media_references'
        ],
        'media_handling': 'reference_only_with_alt_text'
    },
    'single_source_of_truth': {
        'v2_content_only': True,
        'no_v1_contamination': True,
        'complete_metadata_preservation': True
    }
}
```

**Storage:** `content_library` collection, `v2_publishing_results` collection

### STEP 12: Versioning & Diff Management
**Processor:** `V2VersioningSystem`
**Function:** `manage_versioning(content, content_type, articles, generated_articles_result, publishing_result, run_id)`

**Configuration:**
```python
v2_versioning_system = V2VersioningSystem()

versioning_config = {
    'version_detection': {
        'content_hashing': 'first_5000_chars',
        'similarity_threshold': 0.9,
        'update_determination': 'automatic'
    },
    'diff_management': {
        'change_tracking': 'detailed',
        'reprocessing_support': True,
        'version_history': 'complete'
    },
    'metadata_versioning': {
        'version_number': 'incremental',
        'supersedes_tracking': True,
        'change_summary': 'automatic'
    }
}
```

**Storage:** `v2_versioning_results` collection

---

## 🔧 SYSTEM COMPONENTS CONFIGURATION

### Global Processor Instances
```python
# Core Processing Systems
v2_extractor = V2ContentExtractor()
v2_analyzer = V2MultiDimensionalAnalyzer()
v2_global_planner = V2GlobalOutlinePlanner()
v2_per_article_outline_planner = V2PerArticleOutlinePlanner()

# Article Generation & Enhancement
v2_prewrite_system = V2PrewriteSystem()
v2_article_generator = V2ArticleGenerator()
v2_evidence_tagging_system = V2EvidenceTaggingSystem()

# Style & Content Enhancement
v2_style_processor = V2StyleProcessor()
v2_related_links_system = V2RelatedLinksSystem()
v2_gap_filling_system = V2GapFillingSystem()
v2_code_normalization_system = V2CodeNormalizationSystem()

# Quality Assurance & Publishing
v2_validation_system = V2ValidationSystem()
v2_cross_article_qa_system = V2CrossArticleQASystem()
v2_adaptive_adjustment_system = V2AdaptiveAdjustmentSystem()
v2_publishing_system = V2PublishingSystem()
v2_versioning_system = V2VersioningSystem()
```

### Database Collections
```python
database_collections = {
    # Processing Data
    'normalized_documents': 'Source content blocks and media',
    'v2_analysis_results': 'Multi-dimensional analysis data',
    'v2_outline_results': 'Global and per-article outlines',
    'v2_prewrite_results': 'Section-grounded prewrite data',
    'v2_generated_articles': 'Raw article generation results',
    
    # Enhancement Results
    'v2_evidence_tagging_results': 'Evidence attribution data',
    'v2_style_results': 'Style processing and formatting',
    'v2_related_links_results': 'Related links generation',
    'v2_gap_filling_results': 'Gap filling and content enhancement',
    'v2_code_normalization_results': 'Code beautification data',
    
    # Quality & Publishing
    'v2_validation_results': 'Comprehensive validation outcomes',
    'v2_qa_results': 'Cross-article quality assurance',
    'v2_adjustment_results': 'Adaptive adjustment data',
    'v2_publishing_results': 'Publishing flow outcomes',
    'v2_versioning_results': 'Version management data',
    
    # Final Output
    'content_library': 'Published articles with complete metadata'
}
```

### API Endpoints Configuration
```python
api_endpoints = {
    # Processing Entry Points
    '/api/content/process': 'Text content processing',
    '/api/v2/upload-file': 'File upload processing',
    '/api/v2/process-url': 'URL content processing',
    
    # Diagnostic Endpoints
    '/api/engine': 'V2 engine status and capabilities',
    '/api/style/diagnostics': 'Style processing diagnostics',
    '/api/style/diagnostics/{style_id}': 'Specific style result analysis',
    '/api/related-links/diagnostics': 'Related links system status',
    '/api/gap-filling/diagnostics': 'Gap filling system status',
    
    # Content Management
    '/api/content-library': 'Published articles access',
    '/api/style/process-toc-links': 'TOC processing trigger',
    '/api/fix-formatting-defects': 'Targeted formatting fixes'
}
```

---

## 🎯 CRITICAL CONFIGURATION NOTES

### Content Format Transformation Issue
**IDENTIFIED ISSUE:** V2 engine transforms HTML to markdown during processing, occurring before TOC processing. This affects:
- Mini-TOC link generation (HTML `<ul><li>` → markdown format)
- Style processor anchor link coordination
- BeautifulSoup HTML processing capabilities

**MITIGATION STRATEGIES:**
1. **Preserve HTML Structures:** Maintain HTML format for TOC processing
2. **Enhanced Markdown Processing:** Extend TOC processor for markdown format
3. **Pipeline Timing Adjustment:** Apply TOC processing before HTML→markdown transformation

### Success Rate Targets
- **Evidence Tagging:** ≥95% paragraph coverage
- **Block Coverage:** 100% source block assignment
- **Fidelity Score:** ≥0.90 source fidelity maintenance
- **Style Compliance:** Woolf standards enforcement
- **Gap Filling:** Internal corpus retrieval prioritization

### Error Handling & Fallbacks
```python
error_handling = {
    'llm_generation_failure': 'rule_based_fallback',
    'style_processing_failure': 'basic_formatting_fallback',
    'validation_failure': 'diagnostic_reporting_with_partial_publish',
    'complete_pipeline_failure': 'legacy_processing_fallback'
}
```

---

## 📊 MONITORING & DIAGNOSTICS

### Key Metrics Tracked
- Processing success rates per step
- Content quality scores
- Evidence tagging coverage
- Style compliance percentages
- TOC link coordination rates
- Code normalization effectiveness

### Diagnostic Capabilities
- Real-time processing status
- Step-by-step result analysis
- Error tracking and resolution
- Performance optimization insights
- Content quality assessments

---

**END OF CONFIGURATION DOCUMENT**

*This document represents the complete V2 Engine processing pipeline configuration as implemented in December 2024. All components are operational with diagnostic capabilities for monitoring and optimization.*