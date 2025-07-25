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
  Strikethrough,
  Table,
  Plus,
  Type,
  Minus
} from 'lucide-react';

const ModernMediaArticleViewer = ({ 
  article, 
  isEditing, 
  onEdit, 
  onSave, 
  onCancel, 
  onDelete,
  backendUrl 
}) => {
  // Core state
  const [content, setContent] = useState('');
  const [htmlContent, setHtmlContent] = useState('');
  const [markdownContent, setMarkdownContent] = useState('');
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState([]);
  const [status, setStatus] = useState('draft');
  const [viewMode, setViewMode] = useState('wysiwyg'); // 'wysiwyg', 'markdown', 'html', 'preview'
  const [isProcessing, setIsProcessing] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);
  const [metadata, setMetadata] = useState({});
  
  // Auto-save and status
  const [saveStatus, setSaveStatus] = useState('saved'); // 'saved', 'saving', 'unsaved'
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [lastSaved, setLastSaved] = useState(new Date());
  
  // Enhanced UI state
  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashMenuPosition, setSlashMenuPosition] = useState({ x: 0, y: 0 });
  const [selectedText, setSelectedText] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  
  // Refs
  const editorRef = useRef(null);
  const htmlEditorRef = useRef(null);
  const markdownEditorRef = useRef(null);
  const autoSaveTimeoutRef = useRef(null);
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

  // Add support for callouts and custom blocks
  renderer.blockquote = function(quote) {
    // Check for callout patterns
    if (quote.includes('💡')) {
      return `<div class="callout callout-tip" style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 16px 0; border-radius: 4px;">${quote}</div>`;
    } else if (quote.includes('⚠️')) {
      return `<div class="callout callout-warning" style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; margin: 16px 0; border-radius: 4px;">${quote}</div>`;
    } else if (quote.includes('📝')) {
      return `<div class="callout callout-note" style="background-color: #f0fdf4; border-left: 4px solid #10b981; padding: 16px; margin: 16px 0; border-radius: 4px;">${quote}</div>`;
    }
    return `<blockquote style="border-left: 4px solid #d1d5db; padding-left: 16px; margin: 16px 0; color: #6b7280;">${quote}</blockquote>`;
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
      setSaveStatus('saved');
      setHasUnsavedChanges(false);
      setLastSaved(new Date(article.updated_at || Date.now()));
    }
  }, [article]);

  // Content conversion functions
  const markdownToHtml = (markdown) => {
    try {
      const html = marked(markdown);
      return `<div class="article-content">${html}</div>`;
    } catch (error) {
      console.error('Markdown conversion error:', error);
      return `<div class="article-content">${markdown}</div>`;
    }
  };

  const htmlToMarkdown = (html) => {
    try {
      const cleanHtml = html.replace(/<div class="article-content">(.*?)<\/div>/s, '$1');
      return turndownService.turndown(cleanHtml);
    } catch (error) {
      console.error('HTML to markdown conversion error:', error);
      return html;
    }
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

    // Slash commands for WYSIWYG mode
    if (e.key === '/' && viewMode === 'wysiwyg' && !e.ctrlKey && !e.metaKey && !e.altKey) {
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

  // Enhanced content change handler with auto-save
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
        setSaveStatus('saved');
        setHasUnsavedChanges(false);
        setLastSaved(new Date());
        
        if (!isAutoSave) {
          console.log('Manual save completed successfully');
        }
      } else {
        throw new Error('Failed to save article');
      }
    } catch (error) {
      console.error('Save error:', error);
      setSaveStatus('unsaved');
    }
  };

  // WYSIWYG formatting functions
  const formatWysiwyg = (command, value = null) => {
    if (editorRef.current) {
      editorRef.current.focus();
      
      try {
        document.execCommand(command, false, value);
        
        setTimeout(() => {
          const newContent = editorRef.current.innerHTML;
          handleContentChange(newContent, 'wysiwyg');
        }, 10);
      } catch (error) {
        console.error('Formatting command failed:', error);
      }
    }
  };

  // Insert HTML at cursor in WYSIWYG
  const insertWysiwygHTML = (html) => {
    if (editorRef.current) {
      editorRef.current.focus();
      
      try {
        const success = document.execCommand('insertHTML', false, html);
        
        if (!success) {
          // Fallback method
          const selection = window.getSelection();
          if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            range.deleteContents();
            
            const fragment = range.createContextualFragment(html);
            range.insertNode(fragment);
            
            range.collapse(false);
            selection.removeAllRanges();
            selection.addRange(range);
          }
        }
        
        setTimeout(() => {
          const newContent = editorRef.current.innerHTML;
          handleContentChange(newContent, 'wysiwyg');
        }, 10);
      } catch (error) {
        console.error('Insert HTML failed:', error);
      }
    }
  };

  // Content blocks for slash commands
  const insertContentBlock = (type) => {
    const blocks = {
      heading1: '<h1>Heading 1</h1>',
      heading2: '<h2>Heading 2</h2>',
      heading3: '<h3>Heading 3</h3>',
      heading4: '<h4>Heading 4</h4>',
      paragraph: '<p>New paragraph</p>',
      bulletList: '<ul><li>List item 1</li><li>List item 2</li></ul>',
      numberedList: '<ol><li>List item 1</li><li>List item 2</li></ol>',
      quote: '<blockquote><p>Quote text here</p></blockquote>',
      codeBlock: '<pre><code>// Your code here\nconsole.log("Hello, world!");</code></pre>',
      divider: '<hr>',
      table: `<table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
        <thead>
          <tr style="background-color: #f3f4f6;">
            <th style="border: 1px solid #d1d5db; padding: 12px;">Header 1</th>
            <th style="border: 1px solid #d1d5db; padding: 12px;">Header 2</th>
            <th style="border: 1px solid #d1d5db; padding: 12px;">Header 3</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="border: 1px solid #d1d5db; padding: 12px;">Cell 1</td>
            <td style="border: 1px solid #d1d5db; padding: 12px;">Cell 2</td>
            <td style="border: 1px solid #d1d5db; padding: 12px;">Cell 3</td>
          </tr>
        </tbody>
      </table>`,
      tip: '<div class="callout callout-tip" style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 16px 0; border-radius: 4px;"><strong>💡 Tip:</strong> Your tip content here</div>',
      warning: '<div class="callout callout-warning" style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; margin: 16px 0; border-radius: 4px;"><strong>⚠️ Warning:</strong> Your warning content here</div>',
      note: '<div class="callout callout-note" style="background-color: #f0fdf4; border-left: 4px solid #10b981; padding: 16px; margin: 16px 0; border-radius: 4px;"><strong>📝 Note:</strong> Your note content here</div>',
      expandable: '<details style="margin: 16px 0; border: 1px solid #d1d5db; border-radius: 4px; padding: 8px;"><summary style="cursor: pointer; font-weight: bold; padding: 8px;">Click to expand</summary><div style="padding: 8px;">Expandable content goes here</div></details>'
    };

    if (blocks[type]) {
      insertWysiwygHTML(blocks[type]);
    }
    
    setShowSlashMenu(false);
  };

  // Slash command menu
  const renderSlashMenu = () => {
    if (!showSlashMenu) return null;

    const commands = [
      { icon: '🔤', label: 'Heading 1', action: () => insertContentBlock('heading1') },
      { icon: '🔤', label: 'Heading 2', action: () => insertContentBlock('heading2') },
      { icon: '🔤', label: 'Heading 3', action: () => insertContentBlock('heading3') },
      { icon: '🔤', label: 'Heading 4', action: () => insertContentBlock('heading4') },
      { icon: '📝', label: 'Paragraph', action: () => insertContentBlock('paragraph') },
      { icon: '•', label: 'Bullet List', action: () => insertContentBlock('bulletList') },
      { icon: '1.', label: 'Numbered List', action: () => insertContentBlock('numberedList') },
      { icon: '❝', label: 'Quote', action: () => insertContentBlock('quote') },
      { icon: '💻', label: 'Code Block', action: () => insertContentBlock('codeBlock') },
      { icon: '📊', label: 'Table', action: () => insertContentBlock('table') },
      { icon: '💡', label: 'Tip', action: () => insertContentBlock('tip') },
      { icon: '⚠️', label: 'Warning', action: () => insertContentBlock('warning') },
      { icon: '📝', label: 'Note', action: () => insertContentBlock('note') },
      { icon: '📁', label: 'Expandable Section', action: () => insertContentBlock('expandable') },
      { icon: '➖', label: 'Divider', action: () => insertContentBlock('divider') },
    ];

    return (
      <div 
        className="absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-2 min-w-64"
        style={{ 
          left: `${slashMenuPosition.x}px`, 
          top: `${slashMenuPosition.y + 5}px`,
          maxHeight: '300px',
          overflowY: 'auto'
        }}
      >
        <div className="text-xs text-gray-500 mb-2 px-2">Choose a block to insert:</div>
        {commands.map((command, index) => (
          <button
            key={index}
            onClick={command.action}
            className="w-full flex items-center space-x-3 px-3 py-2 text-left hover:bg-gray-100 rounded text-sm"
          >
            <span className="text-lg">{command.icon}</span>
            <span>{command.label}</span>
          </button>
        ))}
      </div>
    );
  };

  // Enhanced toolbar with all modern features
  const renderModernToolbar = () => {
    return (
      <div className="border-b border-gray-200 p-3 bg-gray-50">
        <div className="flex flex-wrap gap-2">
          {/* Undo/Redo */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => document.execCommand('undo')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Undo (Ctrl+Z)"
            >
              <RefreshCw className="h-4 w-4 transform rotate-180" />
            </button>
            <button
              onClick={() => document.execCommand('redo')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Redo (Ctrl+Y)"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>

          {/* Basic Formatting */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => formatWysiwyg('bold')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Bold (Ctrl+B)"
            >
              <Bold className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('italic')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Italic (Ctrl+I)"
            >
              <Italic className="h-4 w-4" />
            </button>
            <button
              onClick={() => formatWysiwyg('underline')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Underline (Ctrl+U)"
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
            <button
              onClick={() => formatWysiwyg('formatBlock', 'h4')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded text-xs font-bold"
              title="Heading 4"
            >
              H4
            </button>
          </div>

          {/* Lists and Alignment */}
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
            <button
              onClick={() => formatWysiwyg('indent')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Indent (Tab)"
            >
              →
            </button>
            <button
              onClick={() => formatWysiwyg('outdent')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Outdent (Shift+Tab)"
            >
              ←
            </button>
          </div>

          {/* Insert Elements */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => {
                const url = prompt('Enter link URL:');
                if (url) {
                  formatWysiwyg('createLink', url);
                }
              }}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Insert Link (Ctrl+K)"
            >
              <Link className="h-4 w-4" />
            </button>
            <button
              onClick={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*';
                input.onchange = (e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      const img = `<img src="${event.target.result}" alt="${file.name}" style="max-width: 100%; height: auto; border-radius: 8px; margin: 16px 0;" />`;
                      insertWysiwygHTML(img);
                    };
                    reader.readAsDataURL(file);
                  }
                };
                input.click();
              }}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Insert Image"
            >
              <Image className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertContentBlock('table')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Insert Table"
            >
              <Table className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertWysiwygHTML('<hr style="margin: 20px 0; border: none; border-top: 2px solid #e5e7eb;" />')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Insert Horizontal Line"
            >
              <Minus className="h-4 w-4" />
            </button>
          </div>

          {/* Special Blocks */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => insertContentBlock('quote')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Quote Block"
            >
              <Quote className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertContentBlock('codeBlock')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Code Block"
            >
              <Code className="h-4 w-4" />
            </button>
            <button
              onClick={() => {
                const code = prompt('Enter inline code:');
                if (code) {
                  insertWysiwygHTML(`<code style="background-color: #f3f4f6; padding: 2px 4px; border-radius: 3px; font-family: monospace;">${code}</code>`);
                }
              }}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="Inline Code"
            >
              <Code2 className="h-4 w-4" />
            </button>
          </div>

          {/* Callouts */}
          <div className="flex items-center space-x-1 border-r border-gray-300 pr-3">
            <button
              onClick={() => insertContentBlock('tip')}
              className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
              title="Tip Callout"
            >
              💡 Tip
            </button>
            <button
              onClick={() => insertContentBlock('warning')}
              className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200"
              title="Warning Callout"
            >
              ⚠️ Warning
            </button>
            <button
              onClick={() => insertContentBlock('note')}
              className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200"
              title="Note Callout"
            >
              📝 Note
            </button>
            <button
              onClick={() => insertContentBlock('expandable')}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded hover:bg-gray-200"
              title="Expandable Section"
            >
              📁 Expand
            </button>
          </div>

          {/* AI Tools */}
          <div className="flex items-center space-x-1">
            <button
              onClick={() => {
                const selection = window.getSelection();
                if (selection.toString()) {
                  console.log('AI rewrite:', selection.toString());
                  // Implement AI rewrite functionality
                } else {
                  alert('Please select text to rewrite');
                }
              }}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="AI Rewrite Selected Text"
            >
              <Brain className="h-4 w-4" />
            </button>
            <button
              onClick={() => {
                // Implement AI enhancement
                console.log('AI enhance content');
              }}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded"
              title="AI Enhancement"
            >
              <Sparkles className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Slash Command Help */}
        <div className="mt-2 text-xs text-gray-500">
          💡 Type <kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs">/</kbd> for quick insert menu • Use keyboard shortcuts for faster editing
        </div>
      </div>
    );
  };

  // Auto-save status display
  const renderSaveStatus = () => {
    let statusText = '';
    let statusColor = '';
    
    switch (saveStatus) {
      case 'saving':
        statusText = 'Saving...';
        statusColor = 'text-yellow-600';
        break;
      case 'saved':
        statusText = `Saved ${lastSaved.toLocaleTimeString()}`;
        statusColor = 'text-green-600';
        break;
      case 'unsaved':
        statusText = 'Unsaved changes';
        statusColor = 'text-red-600';
        break;
      default:
        statusText = 'Ready';
        statusColor = 'text-gray-600';
    }

    return (
      <div className={`text-xs ${statusColor} flex items-center space-x-1`}>
        {saveStatus === 'saving' && <RefreshCw className="h-3 w-3 animate-spin" />}
        <span>{statusText}</span>
      </div>
    );
  };

  // Enhanced view mode selector
  const renderViewModeSelector = () => {
    const modes = [
      { key: 'wysiwyg', label: 'Editor', icon: Edit },
      { key: 'preview', label: 'Preview', icon: Eye },
      { key: 'markdown', label: 'Markdown', icon: FileText },
      { key: 'html', label: 'HTML', icon: Code }
    ];

    return (
      <div className="flex bg-gray-100 rounded-lg overflow-hidden">
        {modes.map((mode) => {
          const Icon = mode.icon;
          return (
            <button
              key={mode.key}
              onClick={() => setViewMode(mode.key)}
              className={`flex items-center space-x-1 px-3 py-1.5 text-sm transition-colors ${
                viewMode === mode.key
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{mode.label}</span>
            </button>
          );
        })}
      </div>
    );
  };

  // Main render function
  if (!article) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Select an article to view or edit
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-full flex flex-col bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden relative"
    >
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                isEditing ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'
              }`}>
                {isEditing ? 'Editing' : 'Viewing'}
              </span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                status === 'published' ? 'bg-green-100 text-green-800' : 
                status === 'draft' ? 'bg-gray-100 text-gray-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {status}
              </span>
            </div>
            {renderSaveStatus()}
          </div>

          <div className="flex items-center space-x-2">
            {isEditing && renderViewModeSelector()}
            
            <div className="flex items-center space-x-1 border-l border-gray-200 pl-3">
              {!isEditing ? (
                <button
                  onClick={onEdit}
                  className="flex items-center space-x-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  <Edit className="h-4 w-4" />
                  <span>Edit</span>
                </button>
              ) : (
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleSave(false)}
                    disabled={saveStatus === 'saving'}
                    className="flex items-center space-x-2 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors text-sm"
                  >
                    {saveStatus === 'saving' ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                    <span>Save</span>
                  </button>
                  <button
                    onClick={onCancel}
                    className="flex items-center space-x-2 px-3 py-1.5 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm"
                  >
                    <X className="h-4 w-4" />
                    <span>Cancel</span>
                  </button>
                </div>
              )}
              
              <button
                onClick={() => setShowMetadata(!showMetadata)}
                className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                title="Toggle Metadata"
              >
                <Settings className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Title Editor */}
        {isEditing ? (
          <input
            type="text"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              setHasUnsavedChanges(true);
              setSaveStatus('unsaved');
            }}
            className="w-full text-2xl font-bold text-gray-900 border-none outline-none focus:ring-0 p-0 bg-transparent"
            placeholder="Article title..."
          />
        ) : (
          <h1 className="text-2xl font-bold text-gray-900">{title || 'Untitled Article'}</h1>
        )}
      </div>

      {/* Toolbar - Only show in editing mode */}
      {isEditing && viewMode === 'wysiwyg' && renderModernToolbar()}

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {viewMode === 'wysiwyg' && isEditing ? (
          <div className="h-full relative">
            <div
              ref={editorRef}
              contentEditable
              onInput={(e) => handleContentChange(e.target.innerHTML, 'wysiwyg')}
              onKeyDown={handleKeyDown}
              className="h-full p-6 overflow-y-auto focus:outline-none prose prose-lg max-w-none"
              style={{
                minHeight: '400px',
                lineHeight: '1.6',
              }}
              dangerouslySetInnerHTML={{ __html: content }}
            />
            {renderSlashMenu()}
          </div>
        ) : viewMode === 'markdown' && isEditing ? (
          <textarea
            ref={markdownEditorRef}
            value={markdownContent}
            onChange={(e) => handleContentChange(e.target.value, 'markdown')}
            onKeyDown={handleKeyDown}
            className="w-full h-full p-6 border-none outline-none resize-none font-mono text-sm"
            placeholder="Write your content in Markdown..."
          />
        ) : viewMode === 'html' && isEditing ? (
          <textarea
            ref={htmlEditorRef}
            value={htmlContent}
            onChange={(e) => handleContentChange(e.target.value, 'html')}
            onKeyDown={handleKeyDown}
            className="w-full h-full p-6 border-none outline-none resize-none font-mono text-sm"
            placeholder="Write your content in HTML..."
          />
        ) : (
          <div className="h-full p-6 overflow-y-auto prose prose-lg max-w-none">
            <div dangerouslySetInnerHTML={{ __html: content }} />
          </div>
        )}
      </div>

      {/* Metadata Panel */}
      {showMetadata && (
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
      )}
    </motion.div>
  );
};

export default ModernMediaArticleViewer;