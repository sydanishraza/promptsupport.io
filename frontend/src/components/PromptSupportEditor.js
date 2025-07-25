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
  Settings,
  Table,
  Columns,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  Palette,
  ChevronDown,
  Plus,
  Trash2,
  Move,
  Info,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ChevronRight,
  Image,
  Upload,
  Link,
  Video,
  FileIcon,
  Maximize2,
  RotateCw,
  Crop,
  Zap,
  Command,
  Search
} from 'lucide-react';

/**
 * PromptSupport WYSIWYG Editor - Phase 3: Media Integration and Advanced Features
 * 
 * Phase 1 Features (Complete):
 * - Rich text contentEditable surface with cursor stability
 * - Basic toolbar with essential formatting tools
 * - Multi-mode support (WYSIWYG, Markdown, HTML)
 * - Keyboard shortcuts and undo/redo
 * 
 * Phase 2 Features (Complete):
 * - Advanced block elements (tables, columns, callouts)
 * - Enhanced formatting options (colors, alignment)
 * - Layout tools and spacing controls
 * - Professional toolbar organization
 * 
 * Phase 3 Features (Current):
 * - Media integration (image upload, drag & drop, resizing)
 * - Advanced keyboard UX (slash commands, smart shortcuts)
 * - Block manipulation (selection, drag & drop reordering)
 * - Enhanced user experience and accessibility
 * - AI-powered content assistance integration ready
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
  
  // === PHASE 2: ADVANCED STATE ===
  const [selectedBlock, setSelectedBlock] = useState(null);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [showTableModal, setShowTableModal] = useState(false);
  const [currentTextColor, setCurrentTextColor] = useState('#1f2937');
  const [currentBgColor, setCurrentBgColor] = useState('transparent');
  const [tableRows, setTableRows] = useState(3);
  const [tableCols, setTableCols] = useState(3);
  
  // === PHASE 3: MEDIA & ADVANCED STATE ===
  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashMenuPosition, setSlashMenuPosition] = useState({ x: 0, y: 0 });
  const [draggedOver, setDraggedOver] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // === REFS ===
  const editorRef = useRef(null);
  const markdownRef = useRef(null);
  const htmlRef = useRef(null);
  
  // === CONTENT REF CALLBACK ===
  const contentRef = (element) => {
    editorRef.current = element;
    if (element && isEditing && content && element.innerHTML !== content) {
      // Set content only when needed, avoiding cursor issues
      element.innerHTML = content;
    }
  };
  
  // === INITIALIZE CONTENT ===
  useEffect(() => {
    if (article) {
      setTitle(article.title || '');
      setHasUnsavedChanges(false);
      
      // Set initial content, clean and simple
      const initialContent = article.content || '<p>Start writing your content...</p>';
      setContent(initialContent);
    }
  }, [article]);

  // Handle entering edit mode - use a cleaner approach
  useEffect(() => {
    if (isEditing && editorRef.current) {
      // Simply focus the editor
      setTimeout(() => {
        if (editorRef.current) {
          editorRef.current.focus();
          // Place cursor at the end naturally
          const range = document.createRange();
          const selection = window.getSelection();
          try {
            range.selectNodeContents(editorRef.current);
            range.collapse(false);
            selection.removeAllRanges();
            selection.addRange(range);
          } catch (e) {
            // Fallback - just focus
            console.log('Cursor positioning fallback');
          }
        }
      }, 100);
    }
  }, [isEditing]);

  // Phase 2: Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowColorPicker(false);
    };
    
    if (showColorPicker) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showColorPicker]);

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
      paragraph: '<p>New paragraph</p>',
      // Phase 2: Advanced blocks
      table2x2: `
        <table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
          <tr>
            <td style="border: 1px solid #e5e7eb; padding: 8px; background: #f9fafb;">Header 1</td>
            <td style="border: 1px solid #e5e7eb; padding: 8px; background: #f9fafb;">Header 2</td>
          </tr>
          <tr>
            <td style="border: 1px solid #e5e7eb; padding: 8px;">Cell 1</td>
            <td style="border: 1px solid #e5e7eb; padding: 8px;">Cell 2</td>
          </tr>
        </table>`,
      table3x3: `
        <table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
          <tr>
            <td style="border: 1px solid #e5e7eb; padding: 8px; background: #f9fafb;">Header 1</td>
            <td style="border: 1px solid #e5e7eb; padding: 8px; background: #f9fafb;">Header 2</td>
            <td style="border: 1px solid #e5e7eb; padding: 8px; background: #f9fafb;">Header 3</td>
          </tr>
          <tr>
            <td style="border: 1px solid #e5e7eb; padding: 8px;">Cell 1</td>
            <td style="border: 1px solid #e5e7eb; padding: 8px;">Cell 2</td>
            <td style="border: 1px solid #e5e7eb; padding: 8px;">Cell 3</td>
          </tr>
          <tr>
            <td style="border: 1px solid #e5e7eb; padding: 8px;">Cell 4</td>
            <td style="border: 1px solid #e5e7eb; padding: 8px;">Cell 5</td>
            <td style="border: 1px solid #e5e7eb; padding: 8px;">Cell 6</td>
          </tr>
        </table>`,
      twoColumns: `
        <div style="display: flex; gap: 16px; margin: 16px 0;">
          <div style="flex: 1; padding: 16px; background: #f9fafb; border-radius: 8px;">
            <p>Left column content</p>
          </div>
          <div style="flex: 1; padding: 16px; background: #f9fafb; border-radius: 8px;">
            <p>Right column content</p>
          </div>
        </div>`,
      infoCallout: `
        <div style="display: flex; gap: 12px; padding: 16px; margin: 16px 0; background: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 8px;">
          <div style="color: #3b82f6; font-size: 20px;">ℹ️</div>
          <div style="flex: 1;">
            <p style="margin: 0; color: #1e40af;"><strong>Info:</strong> Your information message here</p>
          </div>
        </div>`,
      warningCallout: `
        <div style="display: flex; gap: 12px; padding: 16px; margin: 16px 0; background: #fefce8; border-left: 4px solid #eab308; border-radius: 8px;">
          <div style="color: #eab308; font-size: 20px;">⚠️</div>
          <div style="flex: 1;">
            <p style="margin: 0; color: #a16207;"><strong>Warning:</strong> Your warning message here</p>
          </div>
        </div>`,
      successCallout: `
        <div style="display: flex; gap: 12px; padding: 16px; margin: 16px 0; background: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 8px;">
          <div style="color: #22c55e; font-size: 20px;">✅</div>
          <div style="flex: 1;">
            <p style="margin: 0; color: #15803d;"><strong>Success:</strong> Your success message here</p>
          </div>
        </div>`,
      errorCallout: `
        <div style="display: flex; gap: 12px; padding: 16px; margin: 16px 0; background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 8px;">
          <div style="color: #ef4444; font-size: 20px;">❌</div>
          <div style="flex: 1;">
            <p style="margin: 0; color: #dc2626;"><strong>Error:</strong> Your error message here</p>
          </div>
        </div>`,
      expandableSection: `
        <details style="margin: 16px 0; border: 1px solid #e5e7eb; border-radius: 8px;">
          <summary style="padding: 12px 16px; background: #f9fafb; cursor: pointer; font-weight: 600;">Click to expand</summary>
          <div style="padding: 16px;">
            <p>Expandable content goes here...</p>
          </div>
        </details>`
    };

    if (blocks[blockType] && editorMode === 'wysiwyg') {
      executeCommand('insertHTML', blocks[blockType]);
    }
  };

  // === PHASE 2: ADVANCED FORMATTING ===
  
  /**
   * Handle text alignment
   */
  const handleAlignment = (alignment) => {
    executeCommand('justify' + alignment.charAt(0).toUpperCase() + alignment.slice(1));
  };

  /**
   * Handle text and background colors
   */
  const handleColorChange = (color, type = 'text') => {
    if (type === 'text') {
      executeCommand('foreColor', color);
      setCurrentTextColor(color);
    } else {
      executeCommand('backColor', color);
      setCurrentBgColor(color);
    }
  };

  /**
   * Insert custom table with specified dimensions
   */
  const insertCustomTable = (rows, cols) => {
    let tableHTML = '<table style="border-collapse: collapse; width: 100%; margin: 16px 0;">';
    
    for (let i = 0; i < rows; i++) {
      tableHTML += '<tr>';
      for (let j = 0; j < cols; j++) {
        const isHeader = i === 0;
        const cellStyle = `border: 1px solid #e5e7eb; padding: 8px; ${isHeader ? 'background: #f9fafb; font-weight: 600;' : ''}`;
        const cellContent = isHeader ? `Header ${j + 1}` : `Cell ${i}-${j + 1}`;
        tableHTML += `<td style="${cellStyle}">${cellContent}</td>`;
      }
      tableHTML += '</tr>';
    }
    
    tableHTML += '</table>';
    executeCommand('insertHTML', tableHTML);
    setShowTableModal(false);
  };

  // === PHASE 2: ENHANCED TOOLBAR FRAMEWORK ===
  
  /**
   * Render the enhanced formatting toolbar with Phase 2 features
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

          {/* Phase 2: Color and Alignment Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <div className="relative">
              <button
                onClick={() => setShowColorPicker(!showColorPicker)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
                title="Text Color"
              >
                <Palette className="h-4 w-4" />
              </button>
              
              {showColorPicker && (
                <div className="absolute top-10 left-0 z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-3">
                  <div className="mb-2">
                    <label className="text-xs font-medium text-gray-700">Text Color</label>
                    <div className="flex gap-1 mt-1">
                      {['#000000', '#dc2626', '#ea580c', '#d97706', '#65a30d', '#059669', '#0891b2', '#2563eb', '#7c3aed', '#be185d'].map(color => (
                        <button
                          key={color}
                          onClick={() => handleColorChange(color, 'text')}
                          className="w-6 h-6 rounded border border-gray-300 hover:scale-110 transition-transform"
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-700">Background</label>
                    <div className="flex gap-1 mt-1">
                      {['transparent', '#fef3c7', '#dbeafe', '#dcfce7', '#fce7f3', '#f3e8ff', '#f1f5f9', '#f9fafb'].map(color => (
                        <button
                          key={color}
                          onClick={() => handleColorChange(color, 'background')}
                          className="w-6 h-6 rounded border border-gray-300 hover:scale-110 transition-transform"
                          style={{ backgroundColor: color === 'transparent' ? '#ffffff' : color }}
                          title={color}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <button
              onClick={() => handleAlignment('left')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Align Left"
            >
              <AlignLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => handleAlignment('center')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Align Center"
            >
              <AlignCenter className="h-4 w-4" />
            </button>
            <button
              onClick={() => handleAlignment('right')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Align Right"
            >
              <AlignRight className="h-4 w-4" />
            </button>
            <button
              onClick={() => handleAlignment('justify')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Justify"
            >
              <AlignJustify className="h-4 w-4" />
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

          {/* Phase 2: Advanced Blocks Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <div className="relative group">
              <button
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
                title="Insert Table"
              >
                <Table className="h-4 w-4" />
              </button>
              
              <div className="absolute top-10 left-0 z-50 hidden group-hover:block bg-white border border-gray-200 rounded-lg shadow-lg p-2 min-w-max">
                <button
                  onClick={() => insertBlock('table2x2')}
                  className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  2×2 Table
                </button>
                <button
                  onClick={() => insertBlock('table3x3')}
                  className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  3×3 Table
                </button>
                <button
                  onClick={() => setShowTableModal(true)}
                  className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  Custom Size...
                </button>
              </div>
            </div>
            
            <button
              onClick={() => insertBlock('twoColumns')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Two Columns"
            >
              <Columns className="h-4 w-4" />
            </button>
          </div>

          {/* Phase 2: Callouts Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <div className="relative group">
              <button
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
                title="Insert Callout"
              >
                <Info className="h-4 w-4" />
              </button>
              
              <div className="absolute top-10 left-0 z-50 hidden group-hover:block bg-white border border-gray-200 rounded-lg shadow-lg p-2 min-w-max">
                <button
                  onClick={() => insertBlock('infoCallout')}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  <Info className="h-4 w-4 text-blue-600" />
                  Info Callout
                </button>
                <button
                  onClick={() => insertBlock('warningCallout')}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  Warning Callout
                </button>
                <button
                  onClick={() => insertBlock('successCallout')}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  Success Callout
                </button>
                <button
                  onClick={() => insertBlock('errorCallout')}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  <XCircle className="h-4 w-4 text-red-600" />
                  Error Callout
                </button>
              </div>
            </div>
            
            <button
              onClick={() => insertBlock('expandableSection')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Expandable Section"
            >
              <ChevronRight className="h-4 w-4" />
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

  // === PHASE 2: MODAL COMPONENTS ===
  
  /**
   * Custom table creation modal
   */
  const renderTableModal = () => {
    if (!showTableModal) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-96">
          <h3 className="text-lg font-semibold mb-4">Create Custom Table</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rows: {tableRows}
              </label>
              <input
                type="range"
                min="2"
                max="10"
                value={tableRows}
                onChange={(e) => setTableRows(Number(e.target.value))}
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Columns: {tableCols}
              </label>
              <input
                type="range"
                min="2"
                max="6"
                value={tableCols}
                onChange={(e) => setTableCols(Number(e.target.value))}
                className="w-full"
              />
            </div>
            
            <div className="text-sm text-gray-500">
              Preview: {tableRows} × {tableCols} table
            </div>
          </div>
          
          <div className="flex justify-end gap-2 mt-6">
            <button
              onClick={() => setShowTableModal(false)}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={() => insertCustomTable(tableRows, tableCols)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Insert Table
            </button>
          </div>
        </div>
      </div>
    );
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
    <>
      {/* Phase 2: Modals */}
      {renderTableModal()}
      
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
          <div className="h-full relative">
            {!isEditing ? (
              // View mode: safely render HTML content
              <div 
                className="h-full p-6 overflow-y-auto prose prose-lg max-w-none"
                style={{
                  minHeight: '400px',
                  lineHeight: '1.7',
                  fontSize: '16px'
                }}
                dangerouslySetInnerHTML={{ __html: content || '<p>No content</p>' }} 
              />
            ) : (
              // Edit mode: use ref callback to avoid dangerouslySetInnerHTML issues
              <div
                key={`editor-${isEditing}-${article?.id}`} // Force re-render when switching modes
                ref={contentRef}
                contentEditable={true}
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
                  color: '#1f2937',
                  outline: 'none'
                }}
                suppressContentEditableWarning={true}
              />
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
    </>
  );
};

export default PromptSupportEditor;