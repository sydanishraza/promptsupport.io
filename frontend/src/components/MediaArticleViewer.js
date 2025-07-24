import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { marked } from 'marked';
import TurndownService from 'turndown';
import { 
  Eye, 
  Edit, 
  Save, 
  X, 
  FileText,
  Code,
  Settings,
  Trash2,
  Brain,
  Sparkles,
  RefreshCw,
  Download,
  Copy,
  Share,
  Tag,
  User,
  Clock,
  Hash,
  Bold,
  Italic,
  List,
  Link,
  Image,
  Quote,
  Code2,
  Heading1,
  Heading2,
  Heading3,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Underline,
  Strikethrough
} from 'lucide-react';

const MediaArticleViewer = ({ 
  article, 
  isEditing, 
  onEdit, 
  onSave, 
  onCancel, 
  onDelete,
  backendUrl 
}) => {
  const [content, setContent] = useState('');
  const [htmlContent, setHtmlContent] = useState('');
  const [markdownContent, setMarkdownContent] = useState('');
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState([]);
  const [status, setStatus] = useState('draft');
  const [viewMode, setViewMode] = useState('wysiwyg'); // 'wysiwyg', 'markdown', 'html'
  const [isProcessing, setIsProcessing] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);
  const [metadata, setMetadata] = useState({});
  
  const editorRef = useRef(null);
  const htmlEditorRef = useRef(null);
  const markdownEditorRef = useRef(null);
  const turndownService = new TurndownService();

  // Configure marked for better rendering
  marked.setOptions({
    gfm: true,
    breaks: false,
    sanitize: false,
    smartLists: true,
    smartypants: true,
  });

  // Custom renderer for images to preserve base64 data URLs
  const renderer = new marked.Renderer();
  renderer.image = function(href, title, text) {
    return `<img src="${href}" alt="${text}" title="${title || ''}" class="max-w-full h-auto rounded-lg shadow-md my-4" />`;
  };

  marked.use({ renderer });

  // Initialize content when article changes
  useEffect(() => {
    if (article) {
      setTitle(article.title || '');
      const articleContent = article.content || '';
      
      // Detect if content is HTML or Markdown
      if (articleContent.includes('<') && articleContent.includes('>')) {
        // Content is HTML
        setHtmlContent(articleContent);
        setMarkdownContent(htmlToMarkdown(articleContent));
        setContent(articleContent);
      } else {
        // Content is Markdown
        setMarkdownContent(articleContent);
        setHtmlContent(markdownToHtml(articleContent));
        setContent(markdownToHtml(articleContent));
      }
      
      setTags(article.tags || []);
      setStatus(article.status || 'draft');
      setMetadata(article.metadata || {});
    }
  }, [article]);

  // Convert markdown to HTML with beautification
  const markdownToHtml = (markdown) => {
    try {
      const html = marked(markdown);
      // Add internal CSS styling
      return `<div class="article-content">${html}</div>`;
    } catch (error) {
      console.error('Markdown conversion error:', error);
      return `<div class="article-content">${markdown}</div>`;
    }
  };

  // Convert HTML to markdown with beautification
  const htmlToMarkdown = (html) => {
    try {
      // Remove the wrapper div if present
      const cleanHtml = html.replace(/<div class="article-content">(.*?)<\/div>/s, '$1');
      return turndownService.turndown(cleanHtml);
    } catch (error) {
      console.error('HTML to markdown conversion error:', error);
      return html;
    }
  };

  // Beautify HTML
  const beautifyHtml = (html) => {
    try {
      // Simple HTML beautification
      return html
        .replace(/></g, '>\n<')
        .replace(/^\s*\n/gm, '')
        .split('\n')
        .map((line, index) => {
          const depth = (line.match(/^(\s*)/)[1].length || 0) / 2;
          return '  '.repeat(depth) + line.trim();
        })
        .join('\n');
    } catch (error) {
      return html;
    }
  };

  // Beautify Markdown
  const beautifyMarkdown = (markdown) => {
    try {
      return markdown
        .replace(/^\s+|\s+$/g, '') // Trim
        .replace(/\n{3,}/g, '\n\n') // No more than 2 consecutive newlines
        .replace(/^(#{1,6})\s+/gm, '$1 ') // Ensure space after headings
        .replace(/^(\*|-|\+)\s+/gm, '- ') // Standardize list bullets
        .replace(/^(\d+\.)\s+/gm, '$1 '); // Ensure space after numbered lists
    } catch (error) {
      return markdown;
    }
  };

  // Handle view mode change with proper synchronization
  const handleViewModeChange = (mode) => {
    try {
      if (mode === 'markdown') {
        // Convert current content to markdown
        const newMarkdown = viewMode === 'html' ? htmlToMarkdown(htmlContent) : 
                           viewMode === 'wysiwyg' ? htmlToMarkdown(content) : markdownContent;
        setMarkdownContent(beautifyMarkdown(newMarkdown));
      } else if (mode === 'html') {
        // Convert current content to HTML
        const newHtml = viewMode === 'markdown' ? markdownToHtml(markdownContent) : 
                       viewMode === 'wysiwyg' ? content : htmlContent;
        setHtmlContent(beautifyHtml(newHtml));
      } else if (mode === 'wysiwyg') {
        // Convert current content to WYSIWYG HTML
        const newContent = viewMode === 'markdown' ? markdownToHtml(markdownContent) : 
                          viewMode === 'html' ? htmlContent : content;
        setContent(newContent);
      }
      
      setViewMode(mode);
    } catch (error) {
      console.error('View mode change error:', error);
      setViewMode(mode);
    }
  };

  // AI Enhancement
  const handleAIEnhancement = async () => {
    if (!article?.id) return;

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('content', content);
      formData.append('article_id', article.id);

      const response = await fetch(`${backendUrl}/api/media/process-article`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setContent(result.processed_content);
          console.log(`AI enhanced content with ${result.media_count} media items`);
        }
      }
    } catch (error) {
      console.error('AI enhancement error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle content changes with synchronization
  const handleContentChange = (newContent, sourceMode) => {
    if (sourceMode === 'markdown') {
      setMarkdownContent(newContent);
      setHtmlContent(markdownToHtml(newContent));
      setContent(markdownToHtml(newContent));
    } else if (sourceMode === 'html') {
      setHtmlContent(newContent);
      setMarkdownContent(htmlToMarkdown(newContent));
      setContent(newContent);
    } else if (sourceMode === 'wysiwyg') {
      setContent(newContent);
      setHtmlContent(newContent);
      setMarkdownContent(htmlToMarkdown(newContent));
    }
  };

  // Handle save with current content
  const handleSave = async () => {
    try {
      let finalContent = content;
      
      // Use the content from the current view mode
      if (viewMode === 'markdown') {
        finalContent = markdownToHtml(markdownContent);
      } else if (viewMode === 'html') {
        finalContent = htmlContent;
      } else {
        finalContent = content;
      }

      const articleData = {
        id: article.id,
        title: title,
        content: finalContent,
        status: status,
        tags: tags,
        metadata: metadata
      };

      const success = await onSave(articleData);
      if (success) {
        console.log('Article saved successfully');
      }
    } catch (error) {
      console.error('Save error:', error);
    }
  };

  // Handle tag management
  const addTag = (tagText) => {
    if (tagText.trim() && !tags.includes(tagText.trim())) {
      setTags([...tags, tagText.trim()]);
    }
  };

  const removeTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  // Enhanced toolbar for full formatting
  const insertFormatting = (before, after = '', targetMode = 'markdown') => {
    const targetRef = targetMode === 'markdown' ? markdownEditorRef : htmlEditorRef;
    if (!targetRef.current) return;
    
    const textarea = targetRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    const newText = before + selectedText + after;
    const newContent = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
    
    if (targetMode === 'markdown') {
      handleContentChange(newContent, 'markdown');
    } else {
      handleContentChange(newContent, 'html');
    }
    
    // Reset cursor position
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + before.length, start + before.length + selectedText.length);
    }, 0);
  };

  // Insert special components
  const insertComponent = (component, targetMode = 'markdown') => {
    const components = {
      tip: {
        markdown: '\n> 💡 **Tip:** Your tip content here\n\n',
        html: '\n<div class="tip">\n  <strong>💡 Tip:</strong> Your tip content here\n</div>\n\n'
      },
      warning: {
        markdown: '\n> ⚠️ **Warning:** Your warning content here\n\n',
        html: '\n<div class="warning">\n  <strong>⚠️ Warning:</strong> Your warning content here\n</div>\n\n'
      },
      note: {
        markdown: '\n> 📝 **Note:** Your note content here\n\n',
        html: '\n<div class="note">\n  <strong>📝 Note:</strong> Your note content here\n</div>\n\n'
      },
      code_block: {
        markdown: '\n```javascript\n// Your code here\nconsole.log("Hello, world!");\n```\n\n',
        html: '\n<pre><code class="language-javascript">\n// Your code here\nconsole.log("Hello, world!");\n</code></pre>\n\n'
      },
      table: {
        markdown: '\n| Header 1 | Header 2 | Header 3 |\n|----------|----------|----------|\n| Cell 1   | Cell 2   | Cell 3   |\n| Cell 4   | Cell 5   | Cell 6   |\n\n',
        html: '\n<table>\n  <thead>\n    <tr>\n      <th>Header 1</th>\n      <th>Header 2</th>\n      <th>Header 3</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <td>Cell 1</td>\n      <td>Cell 2</td>\n      <td>Cell 3</td>\n    </tr>\n    <tr>\n      <td>Cell 4</td>\n      <td>Cell 5</td>\n      <td>Cell 6</td>\n    </tr>\n  </tbody>\n</table>\n\n'
      }
    };

    const targetRef = targetMode === 'markdown' ? markdownEditorRef : htmlEditorRef;
    if (!targetRef.current) return;
    
    const textarea = targetRef.current;
    const start = textarea.selectionStart;
    const componentText = components[component][targetMode];
    
    const newContent = textarea.value.substring(0, start) + componentText + textarea.value.substring(start);
    
    if (targetMode === 'markdown') {
      handleContentChange(newContent, 'markdown');
    } else {
      handleContentChange(newContent, 'html');
    }
    
    // Reset cursor position
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + componentText.length, start + componentText.length);
    }, 0);
  };

  // Render metadata panel
  const renderMetadataPanel = () => (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      className="border-t border-gray-200 p-4 bg-gray-50"
    >
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <label className="block text-gray-600 mb-1">Created By</label>
          <div className="flex items-center space-x-2">
            <User className="h-4 w-4 text-gray-400" />
            <span>{metadata.created_by || 'System'}</span>
          </div>
        </div>
        <div>
          <label className="block text-gray-600 mb-1">Created At</label>
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4 text-gray-400" />
            <span>{article?.created_at ? new Date(article.created_at).toLocaleString() : 'Unknown'}</span>
          </div>
        </div>
        <div>
          <label className="block text-gray-600 mb-1">Version</label>
          <div className="flex items-center space-x-2">
            <Hash className="h-4 w-4 text-gray-400" />
            <span>v{article?.version || 1}</span>
          </div>
        </div>
        <div>
          <label className="block text-gray-600 mb-1">Word Count</label>
          <span>{content.replace(/<[^>]*>/g, '').split(/\s+/).filter(Boolean).length}</span>
        </div>
      </div>
    </motion.div>
  );

  // Enhanced toolbar for editing
  const renderEnhancedToolbar = () => {
    const currentMode = viewMode;
    
    return (
      <div className="border-b border-gray-200 p-3 bg-gray-50">
        <div className="flex flex-wrap gap-2">
          {/* Basic Formatting */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => insertFormatting('**', '**', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Bold"
            >
              <Bold className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertFormatting('*', '*', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Italic"
            >
              <Italic className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertFormatting(currentMode === 'markdown' ? '~~' : '<del>', currentMode === 'markdown' ? '~~' : '</del>', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Strikethrough"
            >
              <Strikethrough className="h-4 w-4" />
            </button>
          </div>

          {/* Headings */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => insertFormatting(currentMode === 'markdown' ? '# ' : '<h1>', currentMode === 'markdown' ? '\n' : '</h1>\n', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Heading 1"
            >
              <Heading1 className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertFormatting(currentMode === 'markdown' ? '## ' : '<h2>', currentMode === 'markdown' ? '\n' : '</h2>\n', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Heading 2"
            >
              <Heading2 className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertFormatting(currentMode === 'markdown' ? '### ' : '<h3>', currentMode === 'markdown' ? '\n' : '</h3>\n', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Heading 3"
            >
              <Heading3 className="h-4 w-4" />
            </button>
          </div>

          {/* Lists and Quotes */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => insertFormatting(currentMode === 'markdown' ? '- ' : '<ul>\n  <li>', currentMode === 'markdown' ? '\n' : '</li>\n</ul>\n', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Bullet List"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertFormatting(currentMode === 'markdown' ? '> ' : '<blockquote>', currentMode === 'markdown' ? '\n' : '</blockquote>\n', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Quote"
            >
              <Quote className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertFormatting(currentMode === 'markdown' ? '`' : '<code>', currentMode === 'markdown' ? '`' : '</code>', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Inline Code"
            >
              <Code2 className="h-4 w-4" />
            </button>
          </div>

          {/* Links and Images */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => insertFormatting(currentMode === 'markdown' ? '[' : '<a href="url">', currentMode === 'markdown' ? '](url)' : '</a>', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Link"
            >
              <Link className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertFormatting(currentMode === 'markdown' ? '![alt text](' : '<img src="', currentMode === 'markdown' ? 'url)' : '" alt="alt text" />', currentMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Image"
            >
              <Image className="h-4 w-4" />
            </button>
          </div>

          {/* Components */}
          <div className="flex items-center space-x-1">
            <button
              onClick={() => insertComponent('tip', currentMode)}
              className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
              title="Insert Tip"
            >
              💡 Tip
            </button>
            <button
              onClick={() => insertComponent('warning', currentMode)}
              className="px-3 py-1 text-xs bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200"
              title="Insert Warning"
            >
              ⚠️ Warning
            </button>
            <button
              onClick={() => insertComponent('note', currentMode)}
              className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
              title="Insert Note"
            >
              📝 Note
            </button>
            <button
              onClick={() => insertComponent('code_block', currentMode)}
              className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              title="Insert Code Block"
            >
              Code Block
            </button>
            <button
              onClick={() => insertComponent('table', currentMode)}
              className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
              title="Insert Table"
            >
              Table
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            {isEditing ? (
              <Edit className="h-5 w-5 text-blue-600" />
            ) : (
              <Eye className="h-5 w-5 text-green-600" />
            )}
            <h2 className="text-lg font-semibold text-gray-900">
              {isEditing ? 'Edit Article' : 'View Article'}
            </h2>
          </div>
          
          {/* View Mode Toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            {[
              { mode: 'wysiwyg', label: 'WYSIWYG', icon: Eye },
              { mode: 'markdown', label: 'Markdown', icon: FileText },
              { mode: 'html', label: 'HTML', icon: Code }
            ].map(({ mode, label, icon: Icon }) => (
              <button
                key={mode}
                onClick={() => handleViewModeChange(mode)}
                className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  viewMode === mode
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowMetadata(!showMetadata)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
            title="Toggle Metadata"
          >
            <Settings className="h-4 w-4" />
          </button>
          
          {article?.id && (
            <button
              onClick={handleAIEnhancement}
              disabled={isProcessing}
              className="flex items-center px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 text-sm"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  AI Enhance
                </>
              )}
            </button>
          )}
          
          {isEditing ? (
            <div className="flex items-center space-x-2">
              <button
                onClick={handleSave}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Save className="h-4 w-4 mr-2" />
                Save
              </button>
              <button
                onClick={onCancel}
                className="flex items-center px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <button
                onClick={onEdit}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </button>
              {article?.id && (
                <button
                  onClick={onDelete}
                  className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Metadata Panel */}
      {showMetadata && renderMetadataPanel()}

      {/* Article Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1">
            {isEditing ? (
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Article title..."
                className="w-full text-2xl font-bold text-gray-900 bg-transparent border-none focus:outline-none focus:ring-0"
              />
            ) : (
              <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              disabled={!isEditing}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="review">Under Review</option>
            </select>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {tags.map((tag, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
            >
              {tag}
              {isEditing && (
                <button
                  onClick={() => removeTag(tag)}
                  className="ml-1 text-blue-600 hover:text-blue-800"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </span>
          ))}
          {isEditing && (
            <input
              type="text"
              placeholder="Add tag..."
              className="px-2 py-1 text-sm border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  addTag(e.target.value);
                  e.target.value = '';
                }
              }}
            />
          )}
        </div>
      </div>

      {/* Toolbar for editing */}
      {isEditing && (viewMode === 'markdown' || viewMode === 'html') && renderToolbar()}

      {/* Content Area */}
      <div className="p-4 flex-1 overflow-y-auto">
        {viewMode === 'wysiwyg' ? (
          <div className="prose prose-lg max-w-none">
            <div 
              dangerouslySetInnerHTML={{ 
                __html: content.includes('<') ? content : markdownToHtml(content)
              }}
              className="wysiwyg-content"
              style={{
                color: '#333',
                lineHeight: '1.6',
                fontSize: '16px'
              }}
            />
          </div>
        ) : (
          <div className="space-y-4">
            {isEditing ? (
              <textarea
                ref={editorRef}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full h-96 p-4 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-vertical"
                placeholder={`Enter your content in ${viewMode.toUpperCase()} format...`}
              />
            ) : (
              <div className="prose prose-lg max-w-none">
                <div 
                  dangerouslySetInnerHTML={{ 
                    __html: viewMode === 'markdown' ? markdownToHtml(content) : content 
                  }}
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* CSS for enhanced styling */}
      <style jsx>{`
        .wysiwyg-content img {
          max-width: 100%;
          height: auto;
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          margin: 1rem 0;
        }
        .wysiwyg-content blockquote {
          border-left: 4px solid #3b82f6;
          padding-left: 1rem;
          margin: 1rem 0;
          background: #f8fafc;
          padding: 1rem;
          border-radius: 0 8px 8px 0;
        }
        .wysiwyg-content pre {
          background: #f1f5f9;
          padding: 1rem;
          border-radius: 8px;
          overflow-x: auto;
        }
        .wysiwyg-content table {
          border-collapse: collapse;
          width: 100%;
          margin: 1rem 0;
        }
        .wysiwyg-content th,
        .wysiwyg-content td {
          border: 1px solid #e2e8f0;
          padding: 0.5rem;
          text-align: left;
        }
        .wysiwyg-content th {
          background: #f8fafc;
          font-weight: 600;
        }
        .wysiwyg-content h1,
        .wysiwyg-content h2,
        .wysiwyg-content h3,
        .wysiwyg-content h4,
        .wysiwyg-content h5,
        .wysiwyg-content h6 {
          color: #1f2937;
          margin-top: 1.5rem;
          margin-bottom: 1rem;
        }
        .wysiwyg-content p {
          margin-bottom: 1rem;
        }
        .wysiwyg-content ul,
        .wysiwyg-content ol {
          margin-bottom: 1rem;
          padding-left: 1.5rem;
        }
        .wysiwyg-content li {
          margin-bottom: 0.5rem;
        }
      `}</style>
    </div>
  );
};

export default MediaArticleViewer;