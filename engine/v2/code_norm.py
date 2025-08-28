"""
KE-M8: V2 Code Normalization System - Complete Implementation Migration
Migrated from server.py - Code normalization and beautification for Prism
"""

import re
from typing import Dict, Any, List, Optional
from ._utils import create_processing_metadata

class V2CodeNormalizationSystem:
    """V2 Engine: Code normalization and beautification system for Prism-ready code blocks"""
    
    def __init__(self):
        self.language_mappings = {
            # Shell/Curl mappings
            'bash': 'language-bash',
            'sh': 'language-bash', 
            'shell': 'language-bash',
            'curl': 'language-bash',
            
            # HTTP mappings
            'http': 'language-http',
            'https': 'language-http',
            'request': 'language-http',
            'response': 'language-http',
            
            # Programming language mappings
            'python': 'language-python',
            'py': 'language-python',
            'javascript': 'language-javascript',
            'js': 'language-javascript',
            'typescript': 'language-typescript',
            'ts': 'language-typescript',
            'java': 'language-java',
            'c': 'language-c',
            'cpp': 'language-cpp',
            'c++': 'language-cpp',
            'csharp': 'language-csharp',
            'c#': 'language-csharp',
            'php': 'language-php',
            'ruby': 'language-ruby',
            'rb': 'language-ruby',
            'go': 'language-go',
            'golang': 'language-go',
            'rust': 'language-rust',
            'rs': 'language-rust',
            'swift': 'language-swift',
            'kotlin': 'language-kotlin',
            'kt': 'language-kotlin',
            'scala': 'language-scala',
            
            # Markup languages
            'html': 'language-html',
            'htm': 'language-html',
            'xml': 'language-xml',
            'css': 'language-css',
            'scss': 'language-scss',
            'sass': 'language-sass',
            'less': 'language-less',
            
            # Data formats
            'json': 'language-json',
            'yaml': 'language-yaml',
            'yml': 'language-yaml',
            'toml': 'language-toml',
            'ini': 'language-ini',
            'conf': 'language-ini',
            'config': 'language-ini',
            
            # Database
            'sql': 'language-sql',
            'mysql': 'language-sql',
            'postgresql': 'language-sql',
            'sqlite': 'language-sql',
            
            # Shell scripts
            'powershell': 'language-powershell',
            'ps1': 'language-powershell',
            'batch': 'language-batch',
            'bat': 'language-batch',
            'cmd': 'language-batch',
            
            # Others
            'markdown': 'language-markdown',
            'md': 'language-markdown',
            'dockerfile': 'language-dockerfile',
            'docker': 'language-dockerfile',
            'makefile': 'language-makefile',
            'make': 'language-makefile',
            'tex': 'language-latex',
            'latex': 'language-latex'
        }
        
        self.prism_supported = {
            'bash', 'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 
            'csharp', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala',
            'html', 'css', 'xml', 'json', 'yaml', 'sql', 'markdown'
        }
    
    async def run(self, evidence_tagged_content: dict, **kwargs) -> dict:
        """Run code normalization on evidence-tagged content (new interface)"""
        try:
            print(f"💻 V2 CODE NORM: Processing evidence-tagged content - engine=v2")
            
            articles = evidence_tagged_content.get('articles', [])
            normalized_articles = []
            
            for article in articles:
                # Normalize code blocks in article
                normalized_article = await self.normalize_code_blocks(article)
                normalized_articles.append(normalized_article)
            
            return {
                'articles': normalized_articles,
                'code_normalization_metadata': create_processing_metadata('code_normalization',
                    articles_processed=len(normalized_articles),
                    total_code_blocks_normalized=sum(
                        article.get('code_normalization_metadata', {}).get('blocks_normalized', 0) 
                        for article in normalized_articles
                    )
                )
            }
            
        except Exception as e:
            print(f"❌ V2 CODE NORM: Error processing content - {e}")
            return {
                'articles': evidence_tagged_content.get('articles', []),
                'error': str(e)
            }
    
    async def normalize_code_blocks(self, article: dict) -> dict:
        """Normalize code blocks in a single article (legacy interface)"""
        try:
            article_title = article.get('title', 'Untitled')
            print(f"💻 V2 CODE NORM: Normalizing code blocks for '{article_title}' - engine=v2")
            
            content = article.get('content', '')
            normalized_content = await self._normalize_content_code_blocks(content)
            
            # Count code blocks processed
            original_blocks = self._count_code_blocks(content)
            normalized_blocks = self._count_code_blocks(normalized_content)
            
            # Update article
            normalized_article = article.copy()
            normalized_article['content'] = normalized_content
            normalized_article['html'] = normalized_content  # For compatibility
            
            # Add normalization metadata
            normalized_article['code_normalization_metadata'] = {
                'blocks_found': original_blocks,
                'blocks_normalized': normalized_blocks,
                'normalization_status': 'success',
                'timestamp': create_processing_metadata('code_normalization')['timestamp']
            }
            
            print(f"✅ V2 CODE NORM: Normalized {normalized_blocks} code blocks for '{article_title}' - engine=v2")
            return normalized_article
            
        except Exception as e:
            print(f"❌ V2 CODE NORM: Error normalizing code blocks - {e}")
            return article
    
    async def _normalize_content_code_blocks(self, content: str) -> str:
        """Normalize all code blocks in content for Prism compatibility"""
        try:
            # Handle fenced code blocks (```language)
            fenced_pattern = r'```(\w+)?\n?(.*?)\n?```'
            
            def replace_fenced(match):
                language = match.group(1) or ''
                code = match.group(2) or ''
                return self._create_prism_code_block(code.strip(), language)
            
            normalized_content = re.sub(fenced_pattern, replace_fenced, content, flags=re.DOTALL)
            
            # Handle inline code (`code`)
            inline_pattern = r'`([^`\n]+)`'
            
            def replace_inline(match):
                code = match.group(1)
                return f'<code class="language-text">{self._escape_html(code)}</code>'
            
            normalized_content = re.sub(inline_pattern, replace_inline, normalized_content)
            
            # Handle indented code blocks (4+ spaces)
            indented_pattern = r'^( {4,}|\t+)(.+)$'
            lines = normalized_content.split('\n')
            normalized_lines = []
            in_code_block = False
            code_buffer = []
            
            for line in lines:
                if re.match(indented_pattern, line):
                    if not in_code_block:
                        in_code_block = True
                        code_buffer = []
                    
                    # Remove indentation and add to buffer
                    code_line = re.sub(r'^( {4,}|\t+)', '', line)
                    code_buffer.append(code_line)
                    
                else:
                    if in_code_block:
                        # End of code block
                        code_content = '\n'.join(code_buffer)
                        normalized_lines.append(self._create_prism_code_block(code_content, ''))
                        in_code_block = False
                        code_buffer = []
                    
                    normalized_lines.append(line)
            
            # Handle any remaining code block
            if in_code_block and code_buffer:
                code_content = '\n'.join(code_buffer)
                normalized_lines.append(self._create_prism_code_block(code_content, ''))
            
            return '\n'.join(normalized_lines)
            
        except Exception as e:
            print(f"❌ V2 CODE NORM: Error normalizing content - {e}")
            return content
    
    def _create_prism_code_block(self, code: str, language: str = '') -> str:
        """Create Prism-compatible code block HTML"""
        try:
            # Normalize language
            normalized_lang = self._normalize_language(language)
            
            # Escape HTML entities
            escaped_code = self._escape_html(code)
            
            # Create Prism-compatible HTML
            if normalized_lang:
                return f'<pre><code class="{normalized_lang}">{escaped_code}</code></pre>'
            else:
                return f'<pre><code class="language-text">{escaped_code}</code></pre>'
                
        except Exception as e:
            print(f"❌ V2 CODE NORM: Error creating code block - {e}")
            return f'<pre><code>{self._escape_html(code)}</code></pre>'
    
    def _normalize_language(self, language: str) -> str:
        """Normalize language identifier for Prism compatibility"""
        if not language:
            return 'language-text'
        
        language_lower = language.lower().strip()
        
        # Direct mapping
        if language_lower in self.language_mappings:
            return self.language_mappings[language_lower]
        
        # Try common variations
        variations = {
            'js': 'javascript',
            'py': 'python',
            'rb': 'ruby',
            'ts': 'typescript',
            'sh': 'bash',
            'yml': 'yaml'
        }
        
        if language_lower in variations:
            return f"language-{variations[language_lower]}"
        
        # Check if it's a supported Prism language
        if language_lower in self.prism_supported:
            return f"language-{language_lower}"
        
        # Default to text
        return 'language-text'
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML entities in code"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
    
    def _count_code_blocks(self, content: str) -> int:
        """Count code blocks in content"""
        try:
            # Count fenced code blocks
            fenced_count = len(re.findall(r'```.*?```', content, re.DOTALL))
            
            # Count inline code
            inline_count = len(re.findall(r'`[^`\n]+`', content))
            
            # Count indented code blocks (simplified)
            lines = content.split('\n')
            indented_count = 0
            in_block = False
            
            for line in lines:
                if re.match(r'^( {4,}|\t+)', line):
                    if not in_block:
                        indented_count += 1
                        in_block = True
                else:
                    in_block = False
            
            return fenced_count + inline_count + indented_count
            
        except Exception as e:
            print(f"❌ V2 CODE NORM: Error counting code blocks - {e}")
            return 0


print("✅ KE-M8: V2 Code Normalization System migrated from server.py")