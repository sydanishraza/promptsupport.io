import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Bold, 
  Italic, 
  Underline, 
  Strikethrough,
  Type,
  Heading1,
  Heading2, 
  Heading3,
  List,
  ListOrdered,
  Quote,
  Code,
  Code2,
  Minus,
  Undo,
  Redo,
  Eye,
  Edit3,
  FileText,
  Save,
  X,
  Settings
} from 'lucide-react';

/**
 * PromptSupport WYSIWYG Editor - Phase 1: Core Foundation
 * 
 * Features implemented in Phase 1:
 * - Rich text contentEditable surface with cursor stability
 * - Basic toolbar with essential formatting tools
 * - Multi-mode support (WYSIWYG, Markdown, HTML)
 * - Autosizing and proper text insertion handling
 * - Initial keyboard shortcuts and undo/redo
 */
const PromptSupportEditor = ({ 
  article, 
  isEditing, 
  onEdit, 
  onSave, 
  onCancel, 
  onDelete,
  className = '' 
}) => {
  // === CORE STATE ===
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [editorMode, setEditorMode] = useState('wysiwyg'); // 'wysiwyg' | 'markdown' | 'html'
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  // === REFS ===
  const editorRef = useRef(null);
  const markdownRef = useRef(null);
  const htmlRef = useRef(null);
  
  // === INITIALIZE CONTENT ===
  useEffect(() => {
    if (article) {
      setTitle(article.title || '');
      setContent(article.content || '<p>Start writing your content...</p>');
      setHasUnsavedChanges(false);
    }
  }, [article]);

  // === PHASE 1: CORE EDITABLE SURFACE ===
  
  /**
   * Simple content change handler - no cursor manipulation
   * Let the browser handle cursor positioning naturally like the title input
   */
  const handleContentChange = (newContent, mode = 'wysiwyg') => {
    setContent(newContent);
    setHasUnsavedChanges(true);
  };

  // === PHASE 1: KEYBOARD SHORTCUTS ===
  
  /**
   * Handle keyboard shortcuts for formatting and navigation
   */
  const handleKeyDown = (e) => {
    // Prevent backspace/delete from exiting edit mode
    if (e.key === 'Backspace' || e.key === 'Delete') {
      e.stopPropagation();
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
          executeCommand('bold');
          break;
        case 'i':
          e.preventDefault();
          executeCommand('italic');
          break;
        case 'u':
          e.preventDefault();
          executeCommand('underline');
          break;
        case 'k':
          e.preventDefault();
          insertLink();
          break;
        case 's':
          e.preventDefault();
          if (e.shiftKey) {
            handleSave();
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
        executeCommand('outdent');
      } else {
        executeCommand('indent');
      }
    }
  };

  // === PHASE 1: FORMATTING COMMANDS ===
  
  /**
   * Execute formatting commands with natural cursor behavior
   */
  const executeCommand = (command, value = null) => {
    if (editorRef.current && editorMode === 'wysiwyg') {
      editorRef.current.focus();
      
      try {
        document.execCommand(command, false, value);
        // Let the browser handle the update naturally
        setHasUnsavedChanges(true);
      } catch (error) {
        console.error('Command execution failed:', error);
      }
    }
  };

  /**
   * Insert a link with user input
   */
  const insertLink = () => {
    const url = prompt('Enter link URL:');
    if (url && url.trim()) {
      executeCommand('createLink', url.trim());
    }
  };

  /**
   * Insert block-level elements
   */
  const insertBlock = (blockType) => {
    const blocks = {
      h1: '<h1>Heading 1</h1>',
      h2: '<h2>Heading 2</h2>', 
      h3: '<h3>Heading 3</h3>',
      h4: '<h4>Heading 4</h4>',
      quote: '<blockquote><p>Quote text here</p></blockquote>',
      codeBlock: '<pre><code>// Your code here</code></pre>',
      hr: '<hr>',
      paragraph: '<p>New paragraph</p>'
    };

    if (blocks[blockType] && editorMode === 'wysiwyg') {
      executeCommand('insertHTML', blocks[blockType]);
    }
  };

  // === PHASE 1: TOOLBAR FRAMEWORK ===
  
  /**
   * Render the main formatting toolbar
   */
  const renderToolbar = () => {
    if (!isEditing) return null;

    return (
      <div className="border-b border-gray-200 bg-gray-50 p-3">
        <div className="flex flex-wrap items-center gap-1">
          
          {/* Undo/Redo Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <button
              onClick={() => executeCommand('undo')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Undo (⌘Z)"
            >
              <Undo className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeCommand('redo')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Redo (⌘Y)"
            >
              <Redo className="h-4 w-4" />
            </button>
          </div>

          {/* Basic Formatting Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <button
              onClick={() => executeCommand('bold')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Bold (⌘B)"
            >
              <Bold className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeCommand('italic')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Italic (⌘I)"
            >
              <Italic className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeCommand('underline')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Underline (⌘U)"
            >
              <Underline className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeCommand('strikeThrough')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Strikethrough"
            >
              <Strikethrough className="h-4 w-4" />
            </button>
          </div>

          {/* Headings Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <button
              onClick={() => executeCommand('formatBlock', 'h1')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Heading 1"
            >
              <Heading1 className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeCommand('formatBlock', 'h2')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Heading 2"
            >
              <Heading2 className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeCommand('formatBlock', 'h3')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Heading 3"
            >
              <Heading3 className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeCommand('formatBlock', 'h4')}
              className="px-2 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors text-xs font-bold"
              title="Heading 4"
            >
              H4
            </button>
          </div>

          {/* Lists Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <button
              onClick={() => executeCommand('insertUnorderedList')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Bullet List"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeCommand('insertOrderedList')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Numbered List"
            >
              <ListOrdered className="h-4 w-4" />
            </button>
          </div>

          {/* Special Elements Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <button
              onClick={() => insertBlock('quote')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Quote Block"
            >
              <Quote className="h-4 w-4" />
            </button>
            <button
              onClick={() => {
                const code = prompt('Enter inline code:');
                if (code) {
                  executeCommand('insertHTML', `<code style="background-color: #f1f5f9; padding: 2px 4px; border-radius: 3px; font-family: monospace;">${code}</code>`);
                }
              }}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Inline Code"
            >
              <Code2 className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertBlock('codeBlock')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Code Block"
            >
              <Code className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertBlock('hr')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Horizontal Divider"
            >
              <Minus className="h-4 w-4" />
            </button>
          </div>

        </div>
      </div>
    );
  };

  // === PHASE 1: MULTI-MODE SUPPORT ===
  
  /**
   * Render mode selector tabs (only in edit mode)
   */
  const renderModeSelector = () => {
    if (!isEditing) return null;

    const modes = [
      { key: 'wysiwyg', label: 'Editor', icon: Edit3 },
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
              onClick={() => setEditorMode(mode.key)}
              className={`flex items-center space-x-2 px-3 py-2 text-sm transition-colors ${
                editorMode === mode.key
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
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

  // === SAVE HANDLING ===
  
  const handleSave = async () => {
    try {
      const articleData = {
        id: article.id,
        title: title,
        content: content,
        status: article.status || 'draft'
      };

      const success = await onSave(articleData);
      if (success) {
        setHasUnsavedChanges(false);
      }
    } catch (error) {
      console.error('Save error:', error);
    }
  };

  // === MAIN RENDER ===
  
  if (!article) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <Edit3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>Select an article to view or edit</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`h-full flex flex-col bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden ${className}`}
    >
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          
          {/* Status and Mode Selector */}
          <div className="flex items-center space-x-3">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              isEditing ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'
            }`}>
              {isEditing ? 'Editing' : 'Viewing'}
            </span>
            
            {hasUnsavedChanges && (
              <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                Unsaved Changes
              </span>
            )}

            {isEditing && renderModeSelector()}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            {!isEditing ? (
              <button
                onClick={onEdit}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Edit3 className="h-4 w-4" />
                <span>Edit</span>
              </button>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleSave}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Save className="h-4 w-4" />
                  <span>Save</span>
                </button>
                <button
                  onClick={onCancel}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  <X className="h-4 w-4" />
                  <span>Cancel</span>
                </button>
              </div>
            )}
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
            }}
            className="w-full text-2xl font-bold text-gray-900 border-none outline-none focus:ring-0 p-0 bg-transparent"
            placeholder="Article title..."
          />
        ) : (
          <h1 className="text-2xl font-bold text-gray-900">{title || 'Untitled Article'}</h1>
        )}
      </div>

      {/* Toolbar - Only show in WYSIWYG editing mode */}
      {isEditing && editorMode === 'wysiwyg' && renderToolbar()}

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {editorMode === 'wysiwyg' ? (
          <div
            ref={editorRef}
            contentEditable={isEditing}
            onInput={(e) => {
              setContent(e.target.innerHTML);
              setHasUnsavedChanges(true);
            }}
            onKeyDown={handleKeyDown}
            className="h-full p-6 overflow-y-auto focus:outline-none"
            style={{
              minHeight: '400px',
              lineHeight: '1.7',
              fontSize: '16px',
              fontFamily: 'system-ui, -apple-system, sans-serif',
              color: '#1f2937'
            }}
            suppressContentEditableWarning={true}
          >
            {!isEditing ? (
              <div dangerouslySetInnerHTML={{ __html: content || '<p>No content</p>' }} />
            ) : (
              content ? (
                <div dangerouslySetInnerHTML={{ __html: content }} />
              ) : (
                <p style={{ color: '#9ca3af', fontStyle: 'italic' }}>Start writing your content...</p>
              )
            )}
          </div>
        ) : editorMode === 'markdown' ? (
          <textarea
            ref={markdownRef}
            value={content}
            onChange={(e) => handleContentChange(e.target.value, 'markdown')}
            onKeyDown={handleKeyDown}
            className="w-full h-full p-6 border-none outline-none resize-none font-mono text-sm bg-gray-50"
            placeholder="Write your content in Markdown..."
            readOnly={!isEditing}
          />
        ) : (
          <textarea
            ref={htmlRef}
            value={content}
            onChange={(e) => handleContentChange(e.target.value, 'html')}
            onKeyDown={handleKeyDown}
            className="w-full h-full p-6 border-none outline-none resize-none font-mono text-sm bg-gray-50"
            placeholder="Write your content in HTML..."
            readOnly={!isEditing}
          />
        )}
      </div>

    </motion.div>
  );
};

export default PromptSupportEditor;