"""
KE-PR6: Centralized Prompt Templates
All LLM prompt templates for the V2 Engine
"""

# Content Analysis Prompts
CONTENT_ANALYSIS_PROMPT = """
You are an expert content analyzer. Analyze the provided content for {analysis_type} insights.

Provide a structured analysis covering:
1. Content structure and organization
2. Key topics and themes  
3. Technical depth and complexity
4. Target audience assessment
5. Content quality indicators
6. Improvement recommendations

Content to analyze:
{content}

Provide your analysis in a clear, structured format.
"""

# Article Generation Prompts
ARTICLE_SECTION_PROMPT = """
You are a senior technical writer specializing in clear, comprehensive documentation. 

INSTRUCTIONS:
- Rewrite the section faithfully to the source material
- Preserve all facts, code examples, and tables exactly
- Apply Woolf/PromptSupport style guidelines:
  * Clear, scannable headings
  * Concise, action-oriented language
  * Logical flow with smooth transitions
  * Technical accuracy with accessibility
- Add appropriate alt text and captions where media is referenced
- Maintain the original intent and technical depth
- Use active voice where appropriate
- Include concrete examples when relevant

Source section to rewrite:
{section_text}

Rewritten section:
"""

ARTICLE_OUTLINE_PROMPT = """
You are a documentation architect. Create a comprehensive, well-structured outline for the given content.

REQUIREMENTS:
1. Analyze the content thoroughly to identify main topics
2. Create a hierarchical structure with clear headings
3. Ensure logical flow from introduction to conclusion
4. Include subsections for complex topics
5. Maintain technical accuracy and completeness
6. Consider the target audience's knowledge level

Content to outline:
{content}

Create a detailed outline with:
- Main sections (H1)
- Subsections (H2, H3)
- Key points under each section
- Estimated content length for each section

Outline:
"""

# Style and Formatting Prompts
STYLE_IMPROVEMENT_PROMPT = """
You are a style editor specializing in technical documentation. Improve the writing style while preserving all technical content.

STYLE GUIDELINES:
1. Use clear, concise language
2. Employ active voice where appropriate
3. Create smooth transitions between ideas
4. Ensure consistent terminology
5. Optimize for readability and scanning
6. Maintain technical precision
7. Follow Woolf editorial standards

Original content:
{content}

Provide the improved version with better style and flow:
"""

# Validation and QA Prompts
CONTENT_VALIDATION_PROMPT = """
You are a technical reviewer conducting quality assurance on documentation.

VALIDATION CHECKLIST:
1. Technical accuracy verification
2. Completeness assessment
3. Clarity and readability check
4. Consistency review
5. Error identification
6. Improvement recommendations

Content to validate:
{content}

Provide a structured validation report with:
- Overall quality score (1-10)
- Issues found (if any)
- Technical accuracy assessment
- Readability evaluation
- Specific improvement suggestions
- Approval recommendation

Validation Report:
"""

# Gap Filling Prompts
GAP_FILLING_PROMPT = """
You are a technical writer specializing in comprehensive documentation. Fill in missing content while maintaining consistency with the existing material.

GUIDELINES:
1. Identify content gaps marked with [MISSING] or incomplete sections
2. Generate contextually appropriate content
3. Match the existing writing style and technical level
4. Ensure factual accuracy and avoid speculation
5. Maintain consistency with surrounding content
6. Use appropriate technical terminology

Context and content with gaps:
{content}

Fill the identified gaps with appropriate, well-written content:
"""

# Evidence and Fact-Checking Prompts
EVIDENCE_TAGGING_PROMPT = """
You are a fact-checker and evidence specialist. Tag content sections with evidence levels and source attribution.

EVIDENCE LEVELS:
- HIGH: Verifiable facts, code examples, official documentation references
- MEDIUM: Best practices, widely accepted principles, expert consensus
- LOW: Opinions, recommendations, subjective assessments
- SPECULATION: Unverified claims, future predictions, assumptions

Content to analyze:
{content}

Tag each significant claim or statement with:
- Evidence level (HIGH/MEDIUM/LOW/SPECULATION)
- Source type when identifiable
- Confidence assessment
- Recommendations for fact verification

Evidence Analysis:
"""

# Code Processing Prompts
CODE_NORMALIZATION_PROMPT = """
You are a code formatting specialist. Normalize and improve code blocks for documentation.

REQUIREMENTS:
1. Detect programming language automatically
2. Apply consistent formatting and indentation
3. Add syntax highlighting markers for Prism.js
4. Include copy-to-clipboard functionality markers
5. Add comments for clarity where appropriate
6. Ensure code is functional and follows best practices
7. Escape HTML entities properly

Code to normalize:
{code}

Provide normalized code with:
- Language identification
- Proper formatting
- Prism.js compatible syntax highlighting
- HTML-safe escaping
- Improved readability

Normalized Code:
"""

# Cross-Article QA Prompts
CROSS_ARTICLE_QA_PROMPT = """
You are a documentation consistency analyst. Identify potential conflicts or inconsistencies across multiple articles.

ANALYSIS FOCUS:
1. Terminology consistency
2. Technical approach alignment
3. Information conflicts or contradictions
4. Complementary content opportunities
5. Cross-referencing potential
6. Duplicate content identification

Articles to analyze:
{articles}

Provide a consistency analysis report with:
- Identified inconsistencies
- Terminology conflicts
- Recommended harmonizations
- Cross-linking opportunities
- Quality assessment

Cross-Article Analysis:
"""

# Media Processing Prompts
MEDIA_DESCRIPTION_PROMPT = """
You are a digital accessibility specialist. Create comprehensive descriptions for media content.

REQUIREMENTS:
1. Generate accurate alt text for images
2. Create detailed captions for complex visuals
3. Describe charts, diagrams, and infographics clearly
4. Ensure accessibility compliance
5. Maintain technical accuracy
6. Consider context within the document

Media information:
{media_info}

Provide accessibility-compliant descriptions:
- Concise alt text (125 characters max)
- Detailed description for complex content
- Context-appropriate captions
- Technical accuracy verification

Media Descriptions:
"""

# Publishing and Versioning Prompts
PUBLISHING_VALIDATION_PROMPT = """
You are a publishing quality controller. Perform final validation before content publication.

FINAL CHECKS:
1. Content completeness verification
2. Format and structure validation
3. Link and reference verification
4. Metadata accuracy check
5. SEO optimization assessment
6. Publication readiness evaluation

Content for publication validation:
{content}

Provide final validation report:
- Publication readiness score
- Critical issues (if any)
- Format compliance check
- Link validation results
- SEO recommendations
- Final approval status

Publishing Validation:
"""

# Review System Prompts
HUMAN_REVIEW_PROMPT = """
You are a content review coordinator. Prepare content for human review with quality indicators and focus areas.

REVIEW PREPARATION:
1. Identify sections requiring expert review
2. Highlight technical accuracy concerns
3. Flag potential quality issues
4. Suggest review priorities
5. Estimate review complexity
6. Provide reviewer guidance

Content for review preparation:
{content}

Generate review guidance with:
- Priority areas for expert attention
- Technical sections requiring verification
- Quality concerns and flags
- Estimated review time
- Specific reviewer expertise needed

Review Preparation Report:
"""

# Adaptive System Prompts
ADAPTIVE_ADJUSTMENT_PROMPT = """
You are an adaptive content optimizer. Analyze content performance and suggest improvements.

OPTIMIZATION AREAS:
1. Content length balancing
2. Section organization optimization
3. Readability improvements
4. Technical depth adjustments
5. Audience alignment
6. Engagement optimization

Content and metrics:
{content}
{metrics}

Provide optimization recommendations:
- Content restructuring suggestions
- Length adjustment recommendations
- Readability improvements
- Technical level adjustments
- Engagement enhancement ideas

Adaptive Optimization Report:
"""

# Template Variables Helper
PROMPT_VARIABLES = {
    "CONTENT_ANALYSIS": ["analysis_type", "content"],
    "ARTICLE_SECTION": ["section_text"],
    "ARTICLE_OUTLINE": ["content"],
    "STYLE_IMPROVEMENT": ["content"],
    "CONTENT_VALIDATION": ["content"],
    "GAP_FILLING": ["content"],
    "EVIDENCE_TAGGING": ["content"],
    "CODE_NORMALIZATION": ["code"],
    "CROSS_ARTICLE_QA": ["articles"],
    "MEDIA_DESCRIPTION": ["media_info"],
    "PUBLISHING_VALIDATION": ["content"],
    "HUMAN_REVIEW": ["content"],
    "ADAPTIVE_ADJUSTMENT": ["content", "metrics"]
}

def get_prompt_template(template_name: str) -> str:
    """Get prompt template by name"""
    templates = {
        "CONTENT_ANALYSIS": CONTENT_ANALYSIS_PROMPT,
        "ARTICLE_SECTION": ARTICLE_SECTION_PROMPT,
        "ARTICLE_OUTLINE": ARTICLE_OUTLINE_PROMPT,
        "STYLE_IMPROVEMENT": STYLE_IMPROVEMENT_PROMPT,
        "CONTENT_VALIDATION": CONTENT_VALIDATION_PROMPT,
        "GAP_FILLING": GAP_FILLING_PROMPT,
        "EVIDENCE_TAGGING": EVIDENCE_TAGGING_PROMPT,
        "CODE_NORMALIZATION": CODE_NORMALIZATION_PROMPT,
        "CROSS_ARTICLE_QA": CROSS_ARTICLE_QA_PROMPT,
        "MEDIA_DESCRIPTION": MEDIA_DESCRIPTION_PROMPT,
        "PUBLISHING_VALIDATION": PUBLISHING_VALIDATION_PROMPT,
        "HUMAN_REVIEW": HUMAN_REVIEW_PROMPT,
        "ADAPTIVE_ADJUSTMENT": ADAPTIVE_ADJUSTMENT_PROMPT
    }
    
    return templates.get(template_name.upper(), "")

def get_template_variables(template_name: str) -> list:
    """Get required variables for a prompt template"""
    return PROMPT_VARIABLES.get(template_name.upper(), [])