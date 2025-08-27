"""
KE-PR5: V2 Style Processor - Complete Implementation
Extracted from server.py - Woolf-aligned style processing with structural linting
"""

from typing import Dict, Any, List
from ..llm.client import get_llm_client
from ..llm.prompts import STYLE_IMPROVEMENT_PROMPT

class V2StyleProcessor:
    """V2 Engine: Woolf-aligned style processing with structural linting, technical writing standards"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.woolf_guidelines = [
            'clear_scannable_headings', 'actionable_language', 'logical_flow',
            'technical_accuracy', 'accessibility_focus', 'smooth_transitions'
        ]
        self.style_rules = [
            'active_voice_preferred', 'concise_sentences', 'consistent_terminology',
            'proper_heading_hierarchy', 'clear_code_formatting'
        ]
    
    async def process_style(self, generated_content: dict, **kwargs) -> dict:
        """Process style and formatting according to Woolf guidelines"""
        try:
            print(f"🎨 V2 STYLE: Processing style with Woolf guidelines - engine=v2")
            
            articles = generated_content.get('articles', [])
            styled_articles = []
            
            for article in articles:
                styled_article = await self._process_article_style(article)
                styled_articles.append(styled_article)
            
            result = {
                'articles': styled_articles,
                'style_metadata': {
                    'articles_processed': len(styled_articles),
                    'style_guidelines_applied': len(self.woolf_guidelines),
                    'engine': 'v2'
                }
            }
            
            print(f"✅ V2 STYLE: Styled {len(styled_articles)} articles")
            return result
            
        except Exception as e:
            print(f"❌ V2 STYLE: Error processing style - {e}")
            return {
                'articles': generated_content.get('articles', []),
                'error': str(e)
            }
    
    async def _process_article_style(self, article: dict) -> dict:
        """Process style for a single article"""
        try:
            title = article.get('title', 'Article')
            content = article.get('content', '')
            
            # Apply Woolf-aligned style processing
            styled_content = await self._apply_woolf_styling(content, title)
            
            # Apply structural linting
            linted_content = self._apply_structural_linting(styled_content)
            
            # Apply technical writing standards
            final_content = self._apply_technical_standards(linted_content)
            
            # Create styled article
            styled_article = article.copy()
            styled_article['content'] = final_content
            styled_article['style_metadata'] = {
                'woolf_guidelines_applied': True,
                'structural_linting': True,
                'technical_standards': True,
                'style_score': self._calculate_style_score(final_content)
            }
            
            return styled_article
            
        except Exception as e:
            print(f"❌ V2 STYLE: Error styling article - {e}")
            return article
    
    async def _apply_woolf_styling(self, content: str, title: str) -> str:
        """Apply Woolf editorial guidelines using LLM"""
        try:
            system_message = """You are a style editor specializing in technical documentation following Woolf editorial guidelines.

WOOLF STYLE GUIDELINES:
1. Clear, scannable headings with proper hierarchy (H2, H3, H4)
2. Use active voice and actionable language
3. Ensure logical flow with smooth transitions
4. Maintain technical accuracy while being accessible
5. Create concise, direct sentences
6. Use consistent terminology throughout
7. Optimize content for readability and scanning

Apply these guidelines to improve the content while preserving all technical information."""

            user_message = f"Apply Woolf style guidelines to this article:\n\nTitle: {title}\n\nContent:\n{content}"

            # Use centralized LLM client
            styled_content = await self.llm_client.complete(
                system_message=system_message,
                user_message=user_message,
                temperature=0.3,
                max_tokens=6000
            )
            
            return styled_content if styled_content else content
            
        except Exception as e:
            print(f"⚠️ V2 STYLE: LLM styling failed, using rule-based fallback - {e}")
            return self._apply_rule_based_styling(content)
    
    def _apply_rule_based_styling(self, content: str) -> str:
        """Apply rule-based style improvements as fallback"""
        styled_content = content
        
        # Fix heading hierarchy
        styled_content = self._fix_heading_hierarchy(styled_content)
        
        # Improve sentence structure
        styled_content = self._improve_sentences(styled_content)
        
        # Fix common style issues
        styled_content = self._fix_common_issues(styled_content)
        
        return styled_content
    
    def _apply_structural_linting(self, content: str) -> str:
        """Apply structural linting rules"""
        linted_content = content
        
        # Ensure proper heading structure
        linted_content = self._ensure_heading_structure(linted_content)
        
        # Fix list formatting
        linted_content = self._fix_list_formatting(linted_content)
        
        # Improve code block formatting
        linted_content = self._improve_code_blocks(linted_content)
        
        # Add proper paragraph breaks
        linted_content = self._add_paragraph_breaks(linted_content)
        
        return linted_content
    
    def _apply_technical_standards(self, content: str) -> str:
        """Apply technical writing standards"""
        standardized_content = content
        
        # Ensure consistent technical terminology
        standardized_content = self._standardize_terminology(standardized_content)
        
        # Improve technical explanations
        standardized_content = self._improve_technical_explanations(standardized_content)
        
        # Add technical precision
        standardized_content = self._add_technical_precision(standardized_content)
        
        return standardized_content
    
    def _fix_heading_hierarchy(self, content: str) -> str:
        """Fix heading hierarchy to follow proper structure"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                # Count heading level
                level = len(stripped) - len(stripped.lstrip('#'))
                title = stripped.lstrip('# ').strip()
                
                # Ensure proper heading hierarchy (limit to H1-H4)
                level = min(level, 4)
                level = max(level, 1)
                
                fixed_line = '#' * level + ' ' + title
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _improve_sentences(self, content: str) -> str:
        """Improve sentence structure for clarity"""
        # Simple improvements
        improved = content.replace(' very ', ' ')  # Remove unnecessary intensifiers
        improved = improved.replace(' really ', ' ')
        improved = improved.replace(' quite ', ' ')
        
        # Fix common passive voice patterns
        improved = improved.replace(' is used by ', ' uses ')
        improved = improved.replace(' can be done by ', ' can do ')
        
        return improved
    
    def _fix_common_issues(self, content: str) -> str:
        """Fix common style issues"""
        fixed = content
        
        # Fix double spaces
        fixed = ' '.join(fixed.split())
        
        # Ensure proper line breaks
        fixed = fixed.replace('\n\n\n', '\n\n')
        
        # Fix punctuation spacing
        fixed = fixed.replace(' .', '.')
        fixed = fixed.replace(' ,', ',')
        
        return fixed
    
    def _ensure_heading_structure(self, content: str) -> str:
        """Ensure proper heading structure"""
        lines = content.split('\n')
        structured_lines = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                # Add spacing around headings
                if i > 0 and lines[i-1].strip():
                    structured_lines.append('')
                structured_lines.append(line)
                if i < len(lines) - 1 and lines[i+1].strip():
                    structured_lines.append('')
            else:
                structured_lines.append(line)
        
        return '\n'.join(structured_lines)
    
    def _fix_list_formatting(self, content: str) -> str:
        """Fix list formatting for consistency"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('*') or stripped.startswith('-'):
                # Standardize list markers
                list_content = stripped[1:].strip()
                fixed_lines.append(f"- {list_content}")
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _improve_code_blocks(self, content: str) -> str:
        """Improve code block formatting"""
        # Add language hints to code blocks where missing
        improved = content.replace('```\n', '```text\n')
        
        # Ensure proper code block spacing
        improved = improved.replace('```', '\n```')
        improved = improved.replace('\n\n```', '\n```')
        
        return improved
    
    def _add_paragraph_breaks(self, content: str) -> str:
        """Add proper paragraph breaks for readability"""
        # Split into paragraphs and ensure proper spacing
        paragraphs = content.split('\n\n')
        cleaned_paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return '\n\n'.join(cleaned_paragraphs)
    
    def _standardize_terminology(self, content: str) -> str:
        """Standardize technical terminology"""
        # Common technical term standardizations
        standardizations = {
            'API': 'API',  # Ensure consistent capitalization
            'url': 'URL',
            'http': 'HTTP',
            'json': 'JSON',
            'html': 'HTML',
            'css': 'CSS',
            'javascript': 'JavaScript'
        }
        
        standardized = content
        for old_term, new_term in standardizations.items():
            # Case-insensitive replacement with word boundaries
            import re
            pattern = r'\b' + re.escape(old_term) + r'\b'
            standardized = re.sub(pattern, new_term, standardized, flags=re.IGNORECASE)
        
        return standardized
    
    def _improve_technical_explanations(self, content: str) -> str:
        """Improve technical explanations for clarity"""
        # Add context to common technical terms
        improvements = {
            'endpoint': 'API endpoint',
            'parameter': 'API parameter',
            'response': 'API response'
        }
        
        improved = content
        for term, replacement in improvements.items():
            # Only replace if not already contextualized
            if term in improved and replacement not in improved:
                improved = improved.replace(f' {term} ', f' {replacement} ')
        
        return improved
    
    def _add_technical_precision(self, content: str) -> str:
        """Add technical precision to content"""
        # Ensure technical accuracy in common patterns
        precise = content
        
        # Add precision to common technical statements
        precise = precise.replace('send a request', 'send an HTTP request')
        precise = precise.replace('get data', 'retrieve data')
        precise = precise.replace('return data', 'return response data')
        
        return precise
    
    def _calculate_style_score(self, content: str) -> float:
        """Calculate style quality score"""
        score = 0.0
        total_checks = 6
        
        # Check heading structure
        if '#' in content:
            score += 1
        
        # Check paragraph structure
        if '\n\n' in content:
            score += 1
        
        # Check for code blocks
        if '```' in content:
            score += 1
        
        # Check for lists
        if '- ' in content or '* ' in content:
            score += 1
        
        # Check content length (reasonable length)
        if 100 < len(content) < 10000:
            score += 1
        
        # Check for technical terms
        technical_terms = ['API', 'HTTP', 'JSON', 'URL']
        if any(term in content for term in technical_terms):
            score += 1
        
        return round((score / total_checks) * 100, 1)