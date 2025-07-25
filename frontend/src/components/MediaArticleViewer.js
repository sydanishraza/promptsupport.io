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
  const [saveStatus, setSaveStatus] = useState('saved'); // 'saved', 'saving', 'unsaved'
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
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

  // Enhanced content change handler with save status tracking
  const handleContentChange = (newContent, mode) => {
    if (mode === 'wysiwyg') {
      setContent(newContent);
      setMarkdownContent(htmlToMarkdown(newContent));
      setHtmlContent(newContent);
    } else if (mode === 'markdown') {
      setMarkdownContent(newContent);
      const htmlContent = markdownToHtml(newContent);
      setContent(htmlContent);
      setHtmlContent(htmlContent);
    } else if (mode === 'html') {
      setHtmlContent(newContent);
      setContent(newContent);
      setMarkdownContent(htmlToMarkdown(newContent));
    }
    
    // Track unsaved changes
    setHasUnsavedChanges(true);
    setSaveStatus('unsaved');
    
    // Auto-save after 2 seconds of inactivity
    clearTimeout(autoSaveTimeoutRef.current);
    autoSaveTimeoutRef.current = setTimeout(() => {
      if (isEditing) {
        handleSave(true); // true for auto-save
      }
    }, 2000);
  };
  
  // Auto-save timeout reference
  const autoSaveTimeoutRef = useRef(null);

  // Handle save with current content and status tracking
  const handleSave = async (isAutoSave = false) => {
    try {
      setSaveStatus('saving');
      
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
        
        // Update save status
        setSaveStatus('saved');
        setHasUnsavedChanges(false);
        
        // Show success message
        if (!isAutoSave) {
          // You can add a toast notification here
          console.log('Manual save completed successfully');
        }
      } else {
        throw new Error('Failed to save article');
      }
    } catch (error) {
      console.error('Save error:', error);
      setSaveStatus('unsaved');
      // You can add error notification here
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

  // Cursor position management for contentEditable
  const [cursorPosition, setCursorPosition] = useState(null);
  
  // Save cursor position before content changes
  const saveCursorPosition = () => {
    if (editorRef.current) {
      const selection = window.getSelection();
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        return {
          startContainer: range.startContainer,
          startOffset: range.startOffset,
          endContainer: range.endContainer,
          endOffset: range.endOffset
        };
      }
    }
    return null;
  };

  // Restore cursor position after content changes
  const restoreCursorPosition = (position) => {
    if (position && editorRef.current) {
      try {
        const selection = window.getSelection();
        const range = document.createRange();
        
        // Check if the containers still exist in the DOM
        if (editorRef.current.contains(position.startContainer) && 
            editorRef.current.contains(position.endContainer)) {
          range.setStart(position.startContainer, Math.min(position.startOffset, position.startContainer.textContent?.length || 0));
          range.setEnd(position.endContainer, Math.min(position.endOffset, position.endContainer.textContent?.length || 0));
          
          selection.removeAllRanges();
          selection.addRange(range);
        }
      } catch (error) {
        console.warn('Could not restore cursor position:', error);
      }
    }
  };

  // Auto-scroll to cursor functionality
  const scrollToCursor = () => {
    if (editorRef.current) {
      const selection = window.getSelection();
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        const editorRect = editorRef.current.getBoundingClientRect();
        
        // Check if cursor is near the bottom of the visible area
        if (rect.bottom > editorRect.bottom - 50) {
          // Scroll to keep cursor visible
          editorRef.current.scrollTop += rect.bottom - editorRect.bottom + 100;
        }
        
        // Check if cursor is near the top of the visible area
        if (rect.top < editorRect.top + 50) {
          editorRef.current.scrollTop -= editorRect.top - rect.top + 100;
        }
      }
    }
  };

  // Enhanced content change handler with cursor preservation and auto-scroll
  const handleContentChangeWithCursor = (newContent, mode) => {
    // Save cursor position before making changes
    const savedPosition = saveCursorPosition();
    
    // Update content
    handleContentChange(newContent, mode);
    
    // Restore cursor position and scroll after a brief delay
    setTimeout(() => {
      restoreCursorPosition(savedPosition);
      scrollToCursor();
    }, 10); // Increased delay for better stability
  };

  // Enhanced keyboard handler with proper event handling
  const handleKeyDown = (e) => {
    // Prevent backspace/delete from exiting edit mode
    if (e.key === 'Backspace' || e.key === 'Delete') {
      e.stopPropagation();
      return;
    }

    // Keyboard shortcuts
    if (e.ctrlKey || e.metaKey) {
      switch (e.key.toLowerCase()) {
        case 'z':
          e.preventDefault();
          if (e.shiftKey) {
            document.execCommand('redo');
          } else {
            document.execCommand('undo');
          }
          break;
        case 'y':
          e.preventDefault();
          document.execCommand('redo');
          break;
        case 'b':
          e.preventDefault();
          formatWysiwyg('bold');
          break;
        case 'i':
          e.preventDefault();
          formatWysiwyg('italic');
          break;
        case 'u':
          e.preventDefault();
          formatWysiwyg('underline');
          break;
        case 'k':
          e.preventDefault();
          const url = prompt('Enter URL:');
          if (url) {
            formatWysiwyg('createLink', url);
          }
          break;
        case 's':
          e.preventDefault();
          if (e.shiftKey) {
            handleSave(false);
          }
          break;
        default:
          break;
      }
    }

    // Tab handling for indentation
    if (e.key === 'Tab') {
      e.preventDefault();
      if (e.shiftKey) {
        formatWysiwyg('outdent');
      } else {
        formatWysiwyg('indent');
      }
    }

    // Slash commands
    if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      // Check if we're at the beginning of a line or after whitespace
      const selection = window.getSelection();
      if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const textBefore = range.startContainer.textContent?.substring(0, range.startOffset) || '';
        if (textBefore === '' || textBefore.endsWith('\n') || textBefore.endsWith(' ')) {
          e.preventDefault();
          setShowSlashMenu(true);
          setSlashMenuPosition(getCaretPosition());
        }
      }
    }

    // Hide slash menu on escape
    if (e.key === 'Escape') {
      setShowSlashMenu(false);
    }
  };

  // Get caret position for slash menu positioning
  const getCaretPosition = () => {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      const editorRect = editorRef.current?.getBoundingClientRect();
      
      if (editorRect) {
        return {
          x: rect.left - editorRect.left,
          y: rect.bottom - editorRect.top
        };
      }
    }
    return { x: 0, y: 0 };
  };

  // State for slash menu
  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashMenuPosition, setSlashMenuPosition] = useState({ x: 0, y: 0 });
  // WYSIWYG formatting functions with cursor preservation
  const formatWysiwyg = (command, value = null) => {
    if (editorRef.current) {
      editorRef.current.focus();
      
      // Save cursor position before formatting
      const savedPosition = saveCursorPosition();
      
      // Execute the formatting command
      document.execCommand(command, false, value);
      
      // Update content and restore cursor
      setTimeout(() => {
        handleContentChangeWithCursor(editorRef.current.innerHTML, 'wysiwyg');
      }, 0);
    }
  };

  // Insert HTML at cursor in WYSIWYG with improved cursor handling
  const insertWysiwygHTML = (html) => {
    if (editorRef.current) {
      editorRef.current.focus();
      
      // Use document.execCommand for better cursor handling
      document.execCommand('insertHTML', false, html);
      
      // Update content
      setTimeout(() => {
        handleContentChangeWithCursor(editorRef.current.innerHTML, 'wysiwyg');
      }, 0);
    }
  };

  // Enhanced toolbar for WYSIWYG editing
  const renderWysiwygToolbar = () => {
    return (
      <div className="border-b border-gray-200 p-3 bg-gray-50">
        <div className="flex flex-wrap gap-2">
          {/* Basic Formatting */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => formatWysiwyg('bold')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Bold"
            >
              <Bold className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('italic')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Italic"
            >
              <Italic className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('underline')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Underline"
            >
              <Underline className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('strikeThrough')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Strikethrough"
            >
              <Strikethrough className="h-4 w-4" />
            </button>
          </div>

          {/* Headings */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => formatWysiwyg('formatBlock', 'h1')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Heading 1"
            >
              <Heading1 className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('formatBlock', 'h2')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Heading 2"
            >
              <Heading2 className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('formatBlock', 'h3')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Heading 3"
            >
              <Heading3 className="h-4 w-4" />
            </button>
          </div>

          {/* Lists */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => formatWysiwyg('insertUnorderedList')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Bullet List"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('insertOrderedList')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Numbered List"
            >
              <span className="text-sm font-bold">1.</span>
            </button>
          </div>

          {/* Alignment */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => formatWysiwyg('justifyLeft')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Align Left"
            >
              <AlignLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('justifyCenter')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Align Center"
            >
              <AlignCenter className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('justifyRight')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Align Right"
            >
              <AlignRight className="h-4 w-4" />
            </button>
          </div>

          {/* Special Elements */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => insertWysiwygHTML('<blockquote style="border-left: 4px solid #3b82f6; padding-left: 1rem; margin: 1rem 0; background: #f8fafc; padding: 1rem; border-radius: 0 8px 8px 0;">Quote text here</blockquote>')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Quote"
            >
              <Quote className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertWysiwygHTML('<code style="background: #f1f5f9; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.9em; color: #d63384;">inline code</code>&nbsp;')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Inline Code"
            >
              <Code2 className="h-4 w-4" />
            </button>
            <button
              onClick={() => {
                const url = prompt('Enter link URL:');
                if (url) formatWysiwyg('insertHTML', `<a href="${url}" style="color: #3b82f6; text-decoration: underline;">Link text</a>&nbsp;`);
              }}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Link"
            >
              <Link className="h-4 w-4" />
            </button>
          </div>

          {/* Custom Components */}
          <div className="flex items-center space-x-1">
            <button
              onClick={() => insertWysiwygHTML('<div class="tip" style="background: #dbeafe; border: 1px solid #3b82f6; border-radius: 8px; padding: 1rem; margin: 1rem 0; border-left: 4px solid #3b82f6;"><strong>💡 Tip:</strong> Your tip content here</div>')}
              className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
              title="Insert Tip"
            >
              💡 Tip
            </button>
            <button
              onClick={() => insertWysiwygHTML('<div class="warning" style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 1rem; margin: 1rem 0; border-left: 4px solid #f59e0b;"><strong>⚠️ Warning:</strong> Your warning content here</div>')}
              className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200"
              title="Insert Warning"
            >
              ⚠️ Warning
            </button>
            <button
              onClick={() => insertWysiwygHTML('<div class="note" style="background: #d1fae5; border: 1px solid #10b981; border-radius: 8px; padding: 1rem; margin: 1rem 0; border-left: 4px solid #10b981;"><strong>📝 Note:</strong> Your note content here</div>')}
              className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200"
              title="Insert Note"
            >
              📝 Note
            </button>
          </div>
        </div>
      </div>
    );
  };
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
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-full flex flex-col max-h-[calc(100vh-100px)]">
      {/* Header with save status */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            {isEditing ? (
              <Edit className="h-5 w-5 text-blue-600" />
            ) : (
              <Eye className="h-5 w-5 text-green-600" />
            )}
            <div className="flex items-center space-x-3">
              <h2 className="text-lg font-semibold text-gray-900">
                {isEditing ? 'Edit Article' : 'View Article'}
              </h2>
              
              {/* Edit/View Mode Indicator */}
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                isEditing 
                  ? 'bg-blue-100 text-blue-800' 
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {isEditing ? '✏️ Editing' : '👁️ Viewing'}
              </div>
              
              {/* Save Status Indicator */}
              {isEditing && (
                <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
                  saveStatus === 'saved' 
                    ? 'bg-green-100 text-green-800'
                    : saveStatus === 'saving'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {saveStatus === 'saved' && (
                    <>
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      <span>Saved</span>
                    </>
                  )}
                  {saveStatus === 'saving' && (
                    <>
                      <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                      <span>Saving...</span>
                    </>
                  )}
                  {saveStatus === 'unsaved' && (
                    <>
                      <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                      <span>Unsaved</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
          
          {/* View Mode Toggle - Only show when editing */}
          {isEditing && (
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
          )}
        </div>
        
        {/* Status description */}
        <div className="px-4 pb-2">
          <p className="text-sm text-gray-600">
            {isEditing ? 'Edit mode active - Your changes are being auto-saved' : 'Article view mode - Click Edit to modify content'}
          </p>
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

      {/* Enhanced Toolbar for editing */}
      {isEditing && viewMode === 'wysiwyg' && (
        <div className="flex-shrink-0">
          {renderWysiwygToolbar()}
        </div>
      )}
      {isEditing && viewMode === 'markdown' && (
        <div className="flex-shrink-0">
          {renderEnhancedToolbar()}
        </div>
      )}

      {/* Content Area - Flex grow to fill available space */}
      <div className="p-4 flex-1 overflow-hidden flex flex-col min-h-0">
        {viewMode === 'wysiwyg' ? (
          <div className="flex-1 flex flex-col min-h-0">
            {isEditing ? (
              <div className="flex-1 flex flex-col space-y-4 min-h-0">
                {/* WYSIWYG Editor Area */}
                <div
                  ref={editorRef}
                  contentEditable={true}
                  className="flex-1 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white overflow-y-auto"
                  onInput={(e) => {
                    e.preventDefault();
                    handleContentChangeWithCursor(e.target.innerHTML, 'wysiwyg');
                  }}
                  onKeyDown={(e) => {
                    // Handle keyboard shortcuts
                    if (e.ctrlKey || e.metaKey) {
                      switch (e.key) {
                        case 'z':
                          e.preventDefault();
                          document.execCommand('undo');
                          break;
                        case 'y':
                          e.preventDefault();
                          document.execCommand('redo');
                          break;
                        case 'b':
                          e.preventDefault();
                          formatWysiwyg('bold');
                          break;
                        case 'i':
                          e.preventDefault();
                          formatWysiwyg('italic');
                          break;
                        case 'u':
                          e.preventDefault();
                          formatWysiwyg('underline');
                          break;
                        case 'k':
                          e.preventDefault();
                          const url = prompt('Enter link URL:');
                          if (url) formatWysiwyg('createLink', url);
                          break;
                      }
                    }
                  }}
                  style={{
                    color: '#333',
                    lineHeight: '1.6',
                    fontSize: '16px',
                    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    backgroundColor: '#fff',
                    scrollBehavior: 'smooth'
                  }}
                  suppressContentEditableWarning={true}
                  dangerouslySetInnerHTML={{ __html: content }}
                />
                
                {/* WYSIWYG Helper Text */}
                <div className="text-xs text-gray-500 px-2 flex-shrink-0">
                  💡 Use the toolbar above to format your text, or type directly in the editor. 
                  Images and rich content are fully supported.
                </div>
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto">
                <div className="prose prose-lg max-w-none">
                  <div 
                    dangerouslySetInnerHTML={{ __html: content }}
                    className="wysiwyg-content"
                    style={{
                      color: '#333',
                      lineHeight: '1.6',
                      fontSize: '16px'
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        ) : viewMode === 'markdown' ? (
          <div className="flex-1 flex flex-col min-h-0">
            {isEditing ? (
              <textarea
                ref={markdownEditorRef}
                value={markdownContent}
                onChange={(e) => handleContentChange(e.target.value, 'markdown')}
                className="flex-1 p-4 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none overflow-y-auto"
                placeholder="Enter your content in Markdown format..."
              />
            ) : (
              <div className="flex-1 overflow-y-auto">
                <div className="prose prose-lg max-w-none">
                  <div dangerouslySetInnerHTML={{ __html: markdownToHtml(markdownContent) }} />
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex-1 flex flex-col min-h-0">
            {isEditing ? (
              <textarea
                ref={htmlEditorRef}
                value={htmlContent}
                onChange={(e) => handleContentChange(e.target.value, 'html')}
                className="flex-1 p-4 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none overflow-y-auto"
                placeholder="Enter your content in HTML format..."
              />
            ) : (
              <div className="flex-1 overflow-y-auto">
                <div className="prose prose-lg max-w-none">
                  <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Enhanced CSS for beautiful styling */}
      <style jsx>{`
        .article-content,
        .wysiwyg-content {
          color: #333;
          line-height: 1.6;
          font-size: 16px;
        }
        
        .article-content img,
        .wysiwyg-content img {
          max-width: 100%;
          height: auto;
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          margin: 1rem 0;
        }
        
        .article-content blockquote,
        .wysiwyg-content blockquote {
          border-left: 4px solid #3b82f6;
          padding-left: 1rem;
          margin: 1rem 0;
          background: #f8fafc;
          padding: 1rem;
          border-radius: 0 8px 8px 0;
        }
        
        .article-content pre,
        .wysiwyg-content pre {
          background: #f1f5f9;
          padding: 1rem;
          border-radius: 8px;
          overflow-x: auto;
          border: 1px solid #e2e8f0;
        }
        
        .article-content code,
        .wysiwyg-content code {
          background: #f1f5f9;
          padding: 0.2rem 0.4rem;
          border-radius: 4px;
          font-size: 0.9em;
          color: #d63384;
        }
        
        .article-content pre code,
        .wysiwyg-content pre code {
          background: none;
          padding: 0;
          color: #333;
        }
        
        .article-content table,
        .wysiwyg-content table {
          border-collapse: collapse;
          width: 100%;
          margin: 1rem 0;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          overflow: hidden;
        }
        
        .article-content th,
        .wysiwyg-content th {
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          padding: 0.75rem;
          text-align: left;
          font-weight: 600;
          color: #374151;
        }
        
        .article-content td,
        .wysiwyg-content td {
          border: 1px solid #e2e8f0;
          padding: 0.75rem;
          text-align: left;
        }
        
        .article-content .tip,
        .wysiwyg-content .tip {
          background: #dbeafe;
          border: 1px solid #3b82f6;
          border-radius: 8px;
          padding: 1rem;
          margin: 1rem 0;
          border-left: 4px solid #3b82f6;
        }
        
        .article-content .warning,
        .wysiwyg-content .warning {
          background: #fef3c7;
          border: 1px solid #f59e0b;
          border-radius: 8px;
          padding: 1rem;
          margin: 1rem 0;
          border-left: 4px solid #f59e0b;
        }
        
        .article-content .note,
        .wysiwyg-content .note {
          background: #d1fae5;
          border: 1px solid #10b981;
          border-radius: 8px;
          padding: 1rem;
          margin: 1rem 0;
          border-left: 4px solid #10b981;
        }
        
        .article-content h1,
        .wysiwyg-content h1 {
          color: #1f2937;
          margin-top: 2rem;
          margin-bottom: 1rem;
          font-size: 2rem;
          font-weight: 700;
          border-bottom: 2px solid #e5e7eb;
          padding-bottom: 0.5rem;
        }
        
        .article-content h2,
        .wysiwyg-content h2 {
          color: #1f2937;
          margin-top: 1.5rem;
          margin-bottom: 1rem;
          font-size: 1.5rem;
          font-weight: 600;
        }
        
        .article-content h3,
        .wysiwyg-content h3 {
          color: #1f2937;
          margin-top: 1.5rem;
          margin-bottom: 1rem;
          font-size: 1.25rem;
          font-weight: 600;
        }
        
        .article-content h4,
        .wysiwyg-content h4 {
          color: #1f2937;
          margin-top: 1.5rem;
          margin-bottom: 1rem;
          font-size: 1.125rem;
          font-weight: 600;
        }
        
        .article-content p,
        .wysiwyg-content p {
          margin-bottom: 1rem;
          line-height: 1.7;
        }
        
        .article-content ul,
        .wysiwyg-content ul {
          margin-bottom: 1rem;
          padding-left: 1.5rem;
        }
        
        .article-content ol,
        .wysiwyg-content ol {
          margin-bottom: 1rem;
          padding-left: 1.5rem;
        }
        
        .article-content li,
        .wysiwyg-content li {
          margin-bottom: 0.5rem;
          line-height: 1.6;
        }
        
        .article-content strong,
        .wysiwyg-content strong {
          font-weight: 600;
          color: #1f2937;
        }
        
        .article-content em,
        .wysiwyg-content em {
          font-style: italic;
        }
        
        .article-content a,
        .wysiwyg-content a {
          color: #3b82f6;
          text-decoration: underline;
        }
        
        .article-content a:hover,
        .wysiwyg-content a:hover {
          color: #2563eb;
        }
        
        .article-content hr,
        .wysiwyg-content hr {
          border: none;
          height: 1px;
          background: #e5e7eb;
          margin: 2rem 0;
        }
        
        /* Enhanced content editable styles for stability */
        [contentEditable="true"] {
          outline: none;
          background-color: #ffffff !important;
          -webkit-backface-visibility: hidden;
          backface-visibility: hidden;
          transform: translateZ(0);
          will-change: contents;
        }
        
        [contentEditable="true"]:focus {
          border-color: #3b82f6;
          ring: 2px solid #3b82f6;
          background-color: #ffffff !important;
        }
        
        /* WYSIWYG Editor specific styles */
        [contentEditable="true"]:empty:before {
          content: attr(placeholder);
          color: #9ca3af;
          font-style: italic;
        }
        
        [contentEditable="true"] {
          cursor: text;
          position: relative;
          z-index: 1;
        }
        
        [contentEditable="true"] * {
          background-color: transparent !important;
        }
        
        [contentEditable="true"] p {
          margin-bottom: 1rem;
          background-color: transparent !important;
          position: relative;
        }
        
        [contentEditable="true"] h1,
        [contentEditable="true"] h2,
        [contentEditable="true"] h3 {
          margin-top: 1.5rem;
          margin-bottom: 1rem;
          font-weight: bold;
          background-color: transparent !important;
          position: relative;
        }
        
        [contentEditable="true"] h1 {
          font-size: 2rem;
        }
        
        [contentEditable="true"] h2 {
          font-size: 1.5rem;
        }
        
        [contentEditable="true"] h3 {
          font-size: 1.25rem;
        }
        
        [contentEditable="true"] ul,
        [contentEditable="true"] ol {
          margin-left: 1.5rem;
          margin-bottom: 1rem;
          background-color: transparent !important;
          position: relative;
        }
        
        [contentEditable="true"] li {
          margin-bottom: 0.5rem;
          background-color: transparent !important;
          position: relative;
        }
        
        [contentEditable="true"] blockquote {
          border-left: 4px solid #3b82f6;
          padding-left: 1rem;
          margin: 1rem 0;
          background: #f8fafc !important;
          padding: 1rem;
          border-radius: 0 8px 8px 0;
          position: relative;
        }
        
        /* Prevent background flickering during scroll */
        [contentEditable="true"]::-webkit-scrollbar {
          width: 8px;
        }
        
        [contentEditable="true"]::-webkit-scrollbar-track {
          background: #f1f1f1;
        }
        
        [contentEditable="true"]::-webkit-scrollbar-thumb {
          background: #c1c1c1;
          border-radius: 4px;
        }
        
        [contentEditable="true"]::-webkit-scrollbar-thumb:hover {
          background: #a1a1a1;
        }
      `}</style>
    </div>
  );
};

export default MediaArticleViewer;