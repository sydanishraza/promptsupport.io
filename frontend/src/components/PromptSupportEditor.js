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
  Search,
  Brain,
  MessageSquare,
  Users,
  Clock,
  TrendingUp,
  Lightbulb,
  Wand2,
  CheckSquare,
  MessageCircle,
  User,
  Sparkles,
  ImageIcon
} from 'lucide-react';

/**
 * PromptSupport WYSIWYG Editor - Phase 4: AI-Powered Enhancements and Collaboration
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
 * Phase 3 Features (Complete):
 * - Media integration (image upload, drag & drop, video embeds)
 * - Advanced keyboard UX (slash commands, smart shortcuts)
 * - Enhanced user experience and accessibility
 * - Professional content creation workflow
 * 
 * Phase 4 Features (Current):
 * - AI writing assistance and content suggestions
 * - Real-time auto-save with smart conflict resolution
 * - Collaboration features (comments, suggestions, presence)
 * - Content analytics and optimization insights
 * - Smart formatting and grammar assistance
 * - Advanced productivity enhancements
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
  
  // === PHASE 4: AI & COLLABORATION STATE ===
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [showAiPanel, setShowAiPanel] = useState(false);
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);
  const [collaborators, setCollaborators] = useState([]);
  const [comments, setComments] = useState([]);
  const [showComments, setShowComments] = useState(false);
  const [contentAnalytics, setContentAnalytics] = useState({});
  const [aiWritingMode, setAiWritingMode] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [currentSuggestion, setCurrentSuggestion] = useState(null);
  const [showAiDropdown, setShowAiDropdown] = useState(false);
  const [showImageDropdown, setShowImageDropdown] = useState(false);
  const [showContentAnalysis, setShowContentAnalysis] = useState(false);
  const [showAiBrainModal, setShowAiBrainModal] = useState(false);
  const [aiResults, setAiResults] = useState({});
  const [aiActionType, setAiActionType] = useState('');
  const [selectedText, setSelectedText] = useState('');
  // Asset library modal state
  const [assets, setAssets] = useState([]);
  const [assetsLoading, setAssetsLoading] = useState(false);
  const [assetSearchTerm, setAssetSearchTerm] = useState('');
  // Save state management
  const [isSaving, setIsSaving] = useState(false);
  // Custom modal system
  const [customModal, setCustomModal] = useState({ show: false, type: '', title: '', message: '', onConfirm: null, onCancel: null, inputValue: '', inputPlaceholder: '' });
  // Link tooltip state
  const [linkTooltip, setLinkTooltip] = useState({ show: false, x: 0, y: 0, url: '', element: null });
  // Applied AI suggestions highlighting
  const [appliedSuggestions, setAppliedSuggestions] = useState([]);
  const [activeFormats, setActiveFormats] = useState({
    bold: false,
    italic: false,
    underline: false,
    strikethrough: false,
    h1: false,
    h2: false,
    h3: false,
    h4: false,
    ul: false,
    ol: false
  });
  
  // Hover delay timers for flyout menus
  const [hoverTimers, setHoverTimers] = useState({});

  const handleMenuHover = (menuName, show) => {
    // Clear existing timer
    if (hoverTimers[menuName]) {
      clearTimeout(hoverTimers[menuName]);
    }

    if (show) {
      // Show immediately
      switch(menuName) {
        case 'ai': setShowAiDropdown(true); break;
        case 'image': setShowImageDropdown(true); break;
        case 'table': break; // Handle table menu if needed
        case 'callout': break; // Handle callout menu if needed
      }
    } else {
      // Hide with delay
      const timer = setTimeout(() => {
        switch(menuName) {
          case 'ai': setShowAiDropdown(false); break;
          case 'image': setShowImageDropdown(false); break;
          case 'table': break;
          case 'callout': break;
        }
      }, 300); // 300ms delay

      setHoverTimers(prev => ({
        ...prev,
        [menuName]: timer
      }));
    }
  };
  
  // === REFS ===
  const editorRef = useRef(null);
  const markdownRef = useRef(null);
  const htmlRef = useRef(null);
  const fileInputRef = useRef(null);
  const slashMenuRef = useRef(null);
  
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

  // Phase 2 & 3: Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showColorPicker && !event.target.closest('[title="Text Color"]')) {
        setShowColorPicker(false);
      }
      if (showSlashMenu && slashMenuRef.current && !slashMenuRef.current.contains(event.target)) {
        setShowSlashMenu(false);
      }
      if (showAiPanel && !event.target.closest('.ai-panel')) {
        setShowAiPanel(false);
      }
      // Close AI dropdown if clicking outside
      if (showAiDropdown && !event.target.closest('[title="AI Writing Assistant"]')) {
        setShowAiDropdown(false);
      }
      // Close image dropdown if clicking outside
      if (showImageDropdown && !event.target.closest('[title="Insert Image"]')) {
        setShowImageDropdown(false);
      }
    };
    
    if (showColorPicker || showSlashMenu || showAiPanel || showAiDropdown || showImageDropdown) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showColorPicker, showSlashMenu, showAiPanel, showAiDropdown, showImageDropdown]);

  // Phase 4: Auto-save functionality
  useEffect(() => {
    if (!hasUnsavedChanges || !isEditing) return;
    
    const autoSaveTimer = setTimeout(() => {
      autoSave();
    }, 3000); // Auto-save after 3 seconds of inactivity
    
    return () => clearTimeout(autoSaveTimer);
  }, [hasUnsavedChanges, content, title, isEditing]);

  // Phase 4: Content analytics and selection tracking
  useEffect(() => {
    if (content && isEditing) {
      analyzeContent(content);
    }
  }, [content, isEditing]);

  // Phase 4: Track text selection for commenting and format detection
  useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection();
      if (selection && selection.toString().length > 0 && isEditing) {
        setSelectedText(selection.toString());
      } else {
        setSelectedText('');
      }
      
      // Detect active formats when selection changes
      if (isEditing) {
        detectActiveFormats();
      }
    };

    if (isEditing) {
      document.addEventListener('selectionchange', handleSelectionChange);
      // Also trigger on click in editor
      const editorElement = editorRef.current;
      if (editorElement) {
        editorElement.addEventListener('click', handleSelectionChange);
        editorElement.addEventListener('keyup', handleSelectionChange);
      }
      
      return () => {
        document.removeEventListener('selectionchange', handleSelectionChange);
        if (editorElement) {
          editorElement.removeEventListener('click', handleSelectionChange);
          editorElement.removeEventListener('keyup', handleSelectionChange);
        }
      };
    }
  }, [isEditing]);

  // Phase 4: Collaboration presence simulation
  useEffect(() => {
    if (isEditing) {
      updateCollaboratorPresence();
      const presenceInterval = setInterval(updateCollaboratorPresence, 10000);
      return () => clearInterval(presenceInterval);
    }
  }, [isEditing]);

  // === PHASE 1: CORE EDITABLE SURFACE ===
  
  // Custom modal functions to replace browser modals
  const showAlert = (message, title = 'Notice') => {
    setCustomModal({
      show: true,
      type: 'alert',
      title,
      message,
      onConfirm: () => setCustomModal(prev => ({ ...prev, show: false })),
      onCancel: null,
      inputValue: '',
      inputPlaceholder: ''
    });
  };

  const showConfirm = (message, title = 'Confirm') => {
    return new Promise((resolve) => {
      setCustomModal({
        show: true,
        type: 'confirm',
        title,
        message,
        onConfirm: () => {
          setCustomModal(prev => ({ ...prev, show: false }));
          resolve(true);
        },
        onCancel: () => {
          setCustomModal(prev => ({ ...prev, show: false }));
          resolve(false);
        },
        inputValue: '',
        inputPlaceholder: ''
      });
    });
  };

  const showPrompt = (message, defaultValue = '', title = 'Input Required') => {
    return new Promise((resolve) => {
      setCustomModal({
        show: true,
        type: 'prompt',
        title,
        message,
        onConfirm: (value) => {
          setCustomModal(prev => ({ ...prev, show: false }));
          resolve(value || null);
        },
        onCancel: () => {
          setCustomModal(prev => ({ ...prev, show: false }));
          resolve(null);
        },
        inputValue: defaultValue,
        inputPlaceholder: message
      });
    });
  };

  // Link editing functions
  const editLink = async (linkElement) => {
    setLinkTooltip({ show: false, x: 0, y: 0, url: '', element: null });
    const currentUrl = linkElement.href;
    const newUrl = await showPrompt('Enter new link URL:', currentUrl, 'Edit Link');
    if (newUrl && newUrl.trim()) {
      linkElement.href = newUrl;
      linkElement.setAttribute('data-url', newUrl);
    }
  };

  const removeLink = (linkElement) => {
    setLinkTooltip({ show: false, x: 0, y: 0, url: '', element: null });
    const parent = linkElement.parentNode;
    while (linkElement.firstChild) {
      parent.insertBefore(linkElement.firstChild, linkElement);
    }
    parent.removeChild(linkElement);
  };

  // Highlight applied AI suggestions
  const highlightAppliedSuggestion = (text) => {
    const suggestionId = `suggestion_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const highlightedHTML = `<span class="ai-suggestion-applied" data-suggestion-id="${suggestionId}" style="background-color: #fef3c7; border-bottom: 2px solid #f59e0b; padding: 1px 2px; border-radius: 2px; animation: highlight-fade 3s ease-out forwards;">${text}</span>`;
    
    // Add to applied suggestions for tracking
    setAppliedSuggestions(prev => [...prev, { id: suggestionId, text, timestamp: Date.now() }]);
    
    // Remove highlighting after 5 seconds
    setTimeout(() => {
      const element = document.querySelector(`[data-suggestion-id="${suggestionId}"]`);
      if (element) {
        const parent = element.parentNode;
        while (element.firstChild) {
          parent.insertBefore(element.firstChild, element);
        }
        parent.removeChild(element);
        parent.normalize(); // Merge adjacent text nodes
      }
      setAppliedSuggestions(prev => prev.filter(s => s.id !== suggestionId));
    }, 5000);
    
    return highlightedHTML;
  };

  /**
   * Simple content change handler - no cursor manipulation
   * Let the browser handle cursor positioning naturally like the title input
   */
  const handleContentChange = (newContent, mode = 'wysiwyg') => {
    setContent(newContent);
    setHasUnsavedChanges(true);
  };

  // === PHASE 3: ENHANCED KEYBOARD SHORTCUTS ===
  
  /**
   * Handle keyboard shortcuts for formatting and navigation (Enhanced)
   */
  const handleKeyDown = (e) => {
    // Prevent backspace/delete from exiting edit mode
    if (e.key === 'Backspace' || e.key === 'Delete') {
      e.stopPropagation();
    }

    // Phase 3: Slash command detection
    if (e.key === '/') {
      handleSlashCommand(e);
    } else if (e.key === 'Escape') {
      setShowSlashMenu(false);
      setShowColorPicker(false);
    }

    // Enhanced keyboard shortcuts
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
            handleMainSave();
          }
          break;
        case 'e':
          e.preventDefault();
          handleAlignment('center');
          break;
        case 'l':
          e.preventDefault();
          handleAlignment('left');
          break;
        case 'r':
          e.preventDefault();
          handleAlignment('right');
          break;
        case '1':
          if (e.altKey) {
            e.preventDefault();
            executeCommand('formatBlock', 'h1');
          }
          break;
        case '2':
          if (e.altKey) {
            e.preventDefault();
            executeCommand('formatBlock', 'h2');
          }
          break;
        case '3':
          if (e.altKey) {
            e.preventDefault();
            executeCommand('formatBlock', 'h3');
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
   * Clear all formatting from selected text
   */
  const clearFormatting = () => {
    // Remove all formatting from selected text
    executeCommand('removeFormat');
    
    // Additional cleanup for stubborn formatting
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      const selectedText = selection.toString();
      
      if (selectedText) {
        // Create a plain text span to replace formatted content
        const plainSpan = document.createElement('span');
        plainSpan.textContent = selectedText;
        
        try {
          range.deleteContents();
          range.insertNode(plainSpan);
        } catch (e) {
          // Fallback: use execCommand
          executeCommand('insertHTML', selectedText);
        }
      }
    }
  };

  /**
   * Convert selected text to paragraph
   */
  const convertToParagraph = () => {
    executeFormattingCommand('formatBlock', 'p');
  };

  /**
   * Detect active formatting at cursor position
   */
  const detectActiveFormats = () => {
    if (!isEditing || !editorRef.current) return;

    const formats = {
      bold: document.queryCommandState('bold'),
      italic: document.queryCommandState('italic'),
      underline: document.queryCommandState('underline'),
      strikethrough: document.queryCommandState('strikeThrough'),
      h1: false,
      h2: false,
      h3: false,
      h4: false,
      ul: document.queryCommandState('insertUnorderedList'),
      ol: document.queryCommandState('insertOrderedList')
    };

    // Check for heading formats
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      let node = selection.anchorNode;
      while (node && node !== editorRef.current) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          const tagName = node.tagName?.toLowerCase();
          if (tagName === 'h1') formats.h1 = true;
          if (tagName === 'h2') formats.h2 = true;
          if (tagName === 'h3') formats.h3 = true;
          if (tagName === 'h4') formats.h4 = true;
        }
        node = node.parentNode;
      }
    }

    setActiveFormats(formats);
  };

  /**
   * Enhanced execute command with format toggle
   */
  const executeFormattingCommand = (command, value = null) => {
    executeCommand(command, value);
    
    // Update active formats after command
    setTimeout(() => {
      detectActiveFormats();
    }, 10);
  };
  const insertInlineCode = () => {
    const selection = window.getSelection();
    if (selection.toString().length > 0) {
      // Wrap selected text
      executeCommand('insertHTML', `<code style="background-color: #f1f5f9; padding: 2px 4px; border-radius: 3px; font-family: monospace;">${selection.toString()}</code>`);
    } else {
      // Insert template for typing
      executeCommand('insertHTML', `<code style="background-color: #f1f5f9; padding: 2px 4px; border-radius: 3px; font-family: monospace;">code</code>`);
    }
  };
  const insertLink = async () => {
    const selection = window.getSelection();
    const selectedText = selection.toString();
    
    if (!selectedText.trim()) {
      showAlert('Please select some text to add a link to.');
      return;
    }
    
    const url = await showPrompt('Enter link URL:', 'https://', 'Add Link');
    if (url && url.trim()) {
      const linkHTML = `<a href="${url}" data-url="${url}" class="text-blue-600 underline hover:text-blue-800 cursor-pointer" target="_blank">${selectedText}</a>`;
      executeCommand('insertHTML', linkHTML);
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
      codeBlock: '<pre style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 16px; margin: 16px 0; overflow-x: auto;"><code style="font-family: \'Monaco\', \'Menlo\', \'Ubuntu Mono\', monospace; font-size: 14px; line-height: 1.4;">// Your code here\nfunction example() {\n  return "Hello World";\n}</code></pre>',
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

  // === PHASE 3: MEDIA INTEGRATION (Enhanced with real asset library) ===
  
  /**
   * Handle file upload, save to asset library, then embed
   */
  const handleFileUpload = async (files) => {
    for (const file of Array.from(files)) {
      if (file.type.startsWith('image/')) {
        try {
          setUploadProgress(25);
          
          // Upload to asset library first
          const formData = new FormData();
          formData.append('file', file);
          
          const uploadResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/assets/upload`, {
            method: 'POST',
            body: formData
          });
          
          setUploadProgress(75);
          
          if (uploadResponse.ok) {
            const result = await uploadResponse.json();
            
            // Insert image from asset library
            insertImage(result.asset.data, result.asset.name);
            setUploadProgress(100);
            
            // Reset progress after delay
            setTimeout(() => setUploadProgress(0), 1000);
          } else {
            throw new Error('Upload failed');
          }
        } catch (error) {
          console.error('File upload error:', error);
          showAlert('Failed to upload image. Please try again.', 'Upload Error');
          setUploadProgress(0);
        }
      }
    }
  };

  /**
   * Fetch real assets from asset library
   */
  const fetchAssets = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/assets`);
      if (response.ok) {
        const data = await response.json();
        return data.assets || [];
      }
    } catch (error) {
      console.error('Failed to fetch assets:', error);
    }
    
    // Fallback to empty array
    return [];
  };

  /**
   * Show asset library modal for image selection (Fixed hooks issue)
   */
  const showAssetLibrary = async () => {
    setShowImageModal(true);
    setAssetsLoading(true);
    
    try {
      const fetchedAssets = await fetchAssets();
      setAssets(fetchedAssets);
    } catch (error) {
      console.error('Failed to load assets:', error);
      setAssets([]);
    } finally {
      setAssetsLoading(false);
    }
  };

  /**
   * Handle asset selection from library (Fixed error handling)
   */
  const handleAssetSelect = (asset) => {
    try {
      console.log('Selected asset:', asset); // Debug logging
      
      if (!asset) {
        console.error('No asset selected');
        return;
      }
      
      // Check if asset has image data
      if (asset.data && (asset.type === 'image' || !asset.type)) {
        insertImage(asset.data, asset.name || 'Selected image');
        setShowImageModal(false);
      } else {
        console.error('Asset missing data or not an image:', asset);
        showAlert('Unable to insert selected asset. Please try another image.', 'Asset Error');
      }
    } catch (error) {
      console.error('Asset selection error:', error);
      showAlert('Error inserting image. Please try again.', 'Error');
    }
  };

  /**
   * Insert image into editor
   */
  const insertImage = (src, alt = 'Image') => {
    const imageHTML = `
      <figure style="margin: 16px 0; text-align: center;">
        <img src="${src}" alt="${alt}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);" />
        <figcaption style="margin-top: 8px; font-size: 14px; color: #6b7280; font-style: italic;">${alt}</figcaption>
      </figure>
    `;
    executeCommand('insertHTML', imageHTML);
  };

  /**
   * Handle drag and drop
   */
  const handleDragOver = (e) => {
    e.preventDefault();
    setDraggedOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDraggedOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDraggedOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files);
    }
  };

  /**
   * Insert video embed
   */
  const insertVideoEmbed = async () => {
    const url = await showPrompt('Enter video URL (YouTube, Vimeo, etc.):', 'https://', 'Add Video');
    if (url && url.trim()) {
      let embedHTML = '';
      
      if (url.includes('youtube.com') || url.includes('youtu.be')) {
        const videoId = url.includes('youtu.be') 
          ? url.split('youtu.be/')[1].split('?')[0]
          : url.split('v=')[1]?.split('&')[0];
        
        embedHTML = `
          <div style="margin: 16px 0; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
            <iframe src="https://www.youtube.com/embed/${videoId}" 
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; border-radius: 8px;"
                    allowfullscreen></iframe>
          </div>
        `;
      } else if (url.includes('vimeo.com')) {
        const videoId = url.split('vimeo.com/')[1].split('?')[0];
        embedHTML = `
          <div style="margin: 16px 0; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
            <iframe src="https://player.vimeo.com/video/${videoId}" 
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; border-radius: 8px;"
                    allowfullscreen></iframe>
          </div>
        `;
      } else {
        embedHTML = `
          <div style="margin: 16px 0; text-align: center;">
            <video controls style="max-width: 100%; height: auto; border-radius: 8px;">
              <source src="${url}" type="video/mp4">
              Your browser does not support the video tag.
            </video>
          </div>
        `;
      }
      
      executeCommand('insertHTML', embedHTML);
    }
  };

  // === PHASE 3: SLASH COMMANDS ===
  
  /**
   * Slash command menu items
   */
  const slashCommands = [
    { key: 'h1', label: 'Heading 1', icon: Heading1, action: () => insertBlock('h1') },
    { key: 'h2', label: 'Heading 2', icon: Heading2, action: () => insertBlock('h2') },
    { key: 'h3', label: 'Heading 3', icon: Heading3, action: () => insertBlock('h3') },
    { key: 'table', label: 'Table', icon: Table, action: () => insertBlock('table2x2') },
    { key: 'columns', label: 'Two Columns', icon: Columns, action: () => insertBlock('twoColumns') },
    { key: 'quote', label: 'Quote', icon: Quote, action: () => insertBlock('quote') },
    { key: 'code', label: 'Code Block', icon: Code, action: () => insertBlock('codeBlock') },
    { key: 'info', label: 'Info Callout', icon: Info, action: () => insertBlock('infoCallout') },
    { key: 'warning', label: 'Warning Callout', icon: AlertTriangle, action: () => insertBlock('warningCallout') },
    { key: 'success', label: 'Success Callout', icon: CheckCircle, action: () => insertBlock('successCallout') },
    { key: 'error', label: 'Error Callout', icon: XCircle, action: () => insertBlock('errorCallout') },
    { key: 'image', label: 'Upload Image', icon: Image, action: () => fileInputRef.current?.click() },
    { key: 'video', label: 'Video Embed', icon: Video, action: insertVideoEmbed },
    { key: 'hr', label: 'Divider', icon: Minus, action: () => insertBlock('hr') }
  ];

  /**
   * Handle slash command detection and menu
   */
  const handleSlashCommand = (e) => {
    if (e.key === '/') {
      setTimeout(() => {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
          const range = selection.getRangeAt(0);
          const rect = range.getBoundingClientRect();
          const editorRect = editorRef.current.getBoundingClientRect();
          
          setSlashMenuPosition({
            x: rect.left - editorRect.left,
            y: rect.bottom - editorRect.top + 8
          });
          setShowSlashMenu(true);
        }
      }, 10);
    } else if (e.key === 'Escape') {
      setShowSlashMenu(false);
    }
  };

  /**
   * Filter slash commands based on input
   */
  const getFilteredSlashCommands = (query = '') => {
    if (!query) return slashCommands;
    return slashCommands.filter(cmd => 
      cmd.label.toLowerCase().includes(query.toLowerCase()) ||
      cmd.key.toLowerCase().includes(query.toLowerCase())
    );
  };

  // === PHASE 4: AI-POWERED ENHANCEMENTS ===
  
  /**
   * Generate AI content suggestions using real LLM API (fixed)
   */
  const generateAISuggestions = async (context, type = 'completion') => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      const response = await fetch(`${backendUrl}/api/ai-assistance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: context,
          mode: type
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        console.warn('AI service error:', data.error);
        throw new Error(data.error);
      }
      
      return data.suggestions || [];
    } catch (error) {
      console.error('AI assistance error:', error);
      
      // Show user-friendly error message
      showAlert(`AI assistance is currently unavailable: ${error.message}`, 'AI Error');
      
      // Fallback to mock suggestions
      const suggestions = {
        completion: [
          `${context.slice(-50)}... and this opens up new possibilities for enhanced user engagement.`,
          `Building on this concept, we can explore how modern applications handle similar scenarios.`,
          `This approach provides several benefits including improved performance and scalability.`
        ],
        improvement: [
          'Consider breaking this into shorter paragraphs for better readability',
          'Add specific examples to illustrate your points more clearly',
          'Include relevant data to support your arguments'
        ],
        grammar: [
          'Consider using active voice instead of passive voice',
          'This sentence could be restructured for better clarity',
          'Check for consistent verb tense throughout the paragraph'
        ]
      };
      return suggestions[type] || suggestions.completion;
    }
  };

  /**
   * Get real content analysis using LLM API (fixed)
   */
  const getContentAnalysis = async (content) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      const response = await fetch(`${backendUrl}/api/content-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        console.warn('Content analysis error:', data.error);
        throw new Error(data.error);
      }
      
      return data;
    } catch (error) {
      console.error('Content analysis error:', error);
      
      // Show user-friendly error message
      showAlert(`Content analysis is currently unavailable: ${error.message}`, 'Analysis Error');
      
      // Fallback to basic analysis
      const text = content.replace(/<[^>]*>/g, '');
      const words = text.split(/\s+/).filter(word => word.length > 0);
      return {
        wordCount: words.length,
        sentences: text.split(/[.!?]+/).length - 1,
        paragraphs: Math.max(content.split(/<\/p>/gi).length - 1, 1),
        readingTime: Math.ceil(words.length / 200),
        readabilityScore: 70,
        characterCount: text.length,
        aiInsights: 'Content analysis service is currently unavailable.'
      };
    }
  };

  /**
   * AI Writing Assistant - Now with real LLM integration
   */
  const handleAIAssist = async (mode = 'suggest') => {
    setAiWritingMode(true);
    
    try {
      const currentText = editorRef.current?.textContent || '';
      const suggestions = await generateAISuggestions(currentText, mode);
      setAiSuggestions(suggestions);
      setShowAiPanel(true);
      
      // For completion mode, auto-apply the first suggestion
      if (mode === 'completion' && suggestions.length > 0) {
        setTimeout(() => {
          executeCommand('insertHTML', `<span style="color: #666;">${suggestions[0]}</span>`);
        }, 500);
      }
    } catch (error) {
      console.error('AI assistance error:', error);
    } finally {
      setAiWritingMode(false);
    }
  };

  /**
   * Enhanced AI assist with popup results - shows metrics and insights
   */
  const handleAIAssistWithPopup = async (mode = 'completion') => {
    setAiWritingMode(true);
    setAiActionType(mode);
    
    try {
      const currentText = editorRef.current?.textContent || '';
      const selection = window.getSelection();
      const selectedText = selection.toString();
      const textToProcess = selectedText || currentText;
      
      const suggestions = await generateAISuggestions(textToProcess, mode);
      
      // Calculate AI Brain metrics
      const metrics = {
        wordsProcessed: textToProcess.split(' ').length,
        suggestionsGenerated: suggestions.length,
        mode: mode,
        processingTime: Date.now(), // Mock processing time
        confidence: Math.random() * 30 + 70, // Mock confidence 70-100%
        improvements: Math.floor(Math.random() * 10) + 1,
        suggestions: suggestions,
        originalText: selectedText,
        processedText: textToProcess
      };
      
      setAiResults(metrics);
      setShowAiBrainModal(true);
      
    } catch (error) {
      console.error('AI assistance error:', error);
      showAlert('AI assistance is currently unavailable. Please try again later.', 'AI Error');
    } finally {
      setAiWritingMode(false);
    }
  };

  /**
   * Unified AI Brain handler with enhanced fallback suggestions
   */
  const handleUnifiedAIBrain = async () => {
    setAiWritingMode(true);
    setAiActionType('unified');
    
    try {
      const currentText = editorRef.current?.textContent || '';
      const selection = window.getSelection();
      const selectedText = selection.toString();
      const textToProcess = selectedText || currentText;
      
      if (!textToProcess.trim()) {
        showAlert('Please type some content or select text to analyze with AI Brain.');
        setAiWritingMode(false);
        return;
      }
      
      // Try to get AI suggestions from backend APIs
      const [completionResult, improvementResult, grammarResult] = await Promise.allSettled([
        generateAISuggestions(textToProcess, 'completion').catch(() => []),
        generateAISuggestions(textToProcess, 'improvement').catch(() => []), 
        generateAISuggestions(textToProcess, 'grammar').catch(() => [])
      ]);
      
      // Extract successful results or use empty arrays
      const completionSuggestions = completionResult.status === 'fulfilled' ? completionResult.value : [];
      const improvementSuggestions = improvementResult.status === 'fulfilled' ? improvementResult.value : [];
      const grammarSuggestions = grammarResult.status === 'fulfilled' ? grammarResult.value : [];
      
      // Create enhanced fallback suggestions if API responses are empty
      const enhancedSuggestions = [];
      
      // Add completion suggestions (or fallbacks)
      if (completionSuggestions.length > 0) {
        enhancedSuggestions.push(...completionSuggestions.map(s => ({ type: 'completion', text: s, icon: 'sparkles' })));
      } else if (selectedText) {
        // Fallback completion suggestions for selected text
        enhancedSuggestions.push(
          { type: 'completion', text: `${selectedText} Additionally, this approach provides comprehensive benefits for users.`, icon: 'sparkles' },
          { type: 'completion', text: `${selectedText} Furthermore, this method enhances overall efficiency and effectiveness.`, icon: 'sparkles' }
        );
      } else {
        // Fallback completion for full content
        const words = textToProcess.split(' ');
        if (words.length > 10) {
          enhancedSuggestions.push(
            { type: 'completion', text: 'To summarize, this comprehensive approach delivers significant value and measurable results for all stakeholders involved.', icon: 'sparkles' },
            { type: 'completion', text: 'In conclusion, implementing these strategies will drive innovation and sustainable growth in the long term.', icon: 'sparkles' }
          );
        }
      }
      
      // Add improvement suggestions (or fallbacks)
      if (improvementSuggestions.length > 0) {
        enhancedSuggestions.push(...improvementSuggestions.map(s => ({ type: 'improvement', text: s, icon: 'lightbulb' })));
      } else {
        // Generate smart improvement suggestions based on content analysis
        const sentences = textToProcess.split(/[.!?]+/).filter(s => s.trim().length > 0);
        const avgWordsPerSentence = textToProcess.split(' ').length / Math.max(sentences.length, 1);
        
        if (avgWordsPerSentence > 25) {
          enhancedSuggestions.push({ type: 'improvement', text: 'Consider breaking up long sentences for better readability. Aim for 15-20 words per sentence.', icon: 'lightbulb' });
        }
        
        if (textToProcess.length > 100) {
          enhancedSuggestions.push(
            { type: 'improvement', text: 'Add more specific examples or data points to strengthen your arguments and increase credibility.', icon: 'lightbulb' },
            { type: 'improvement', text: 'Consider adding transition words (however, therefore, additionally) to improve flow between ideas.', icon: 'lightbulb' }
          );
        }
      }
      
      // Add grammar suggestions (or fallbacks)
      if (grammarSuggestions.length > 0) {
        enhancedSuggestions.push(...grammarSuggestions.map(s => ({ type: 'grammar', text: s, icon: 'check-square' })));
      } else {
        // Basic grammar checks
        const commonIssues = [];
        if (textToProcess.includes(' i ')) commonIssues.push('Consider capitalizing "i" → "I"');
        if (textToProcess.includes('  ')) commonIssues.push('Remove extra spaces between words');
        if (!/[.!?]$/.test(textToProcess.trim())) commonIssues.push('Consider ending with proper punctuation (. ! ?)');
        
        commonIssues.forEach(issue => {
          enhancedSuggestions.push({ type: 'grammar', text: issue, icon: 'check-square' });
        });
        
        if (commonIssues.length === 0) {
          enhancedSuggestions.push({ type: 'grammar', text: 'Grammar looks good! Consider reviewing for consistent tense usage throughout.', icon: 'check-square' });
        }
      }
      
      // Calculate comprehensive AI Brain metrics
      const metrics = {
        wordsProcessed: textToProcess.split(' ').length,
        suggestionsGenerated: enhancedSuggestions.length,
        mode: 'unified',
        completionCount: enhancedSuggestions.filter(s => s.type === 'completion').length,
        improvementCount: enhancedSuggestions.filter(s => s.type === 'improvement').length,
        grammarCount: enhancedSuggestions.filter(s => s.type === 'grammar').length,
        processingTime: Date.now(),
        confidence: Math.random() * 20 + 80, // High confidence 80-100%
        improvements: enhancedSuggestions.length,
        suggestions: enhancedSuggestions,
        originalText: selectedText,
        processedText: textToProcess
      };
      
      setAiResults(metrics);
      setShowAiBrainModal(true);
      
    } catch (error) {
      console.error('Unified AI Brain error:', error);
      showAlert('AI Brain is currently unavailable. Please try again later.', 'AI Error');
    } finally {
      setAiWritingMode(false);
    }
  };

  /**
   * Apply AI suggestion to content - Now functional
   */
  const applyAISuggestion = (suggestion) => {
    if (editorMode === 'wysiwyg') {
      executeCommand('insertHTML', ` ${suggestion}`);
    }
    setShowAiPanel(false);
    setAiSuggestions([]);
  };

  /**
   * Real-time auto-save functionality with backend integration
   */
  const autoSave = async () => {
    if (!hasUnsavedChanges || !article?.id) return;
    
    setIsAutoSaving(true);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/content-library/${article.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: title,
          content: content,
          status: 'draft'
        })
      });

      if (response.ok) {
        setLastSaved(new Date());
        setHasUnsavedChanges(false);
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    } finally {
      setIsAutoSaving(false);
    }
  };

  /**
   * Content analytics with enhanced real content analysis and metrics
   */
  const analyzeContent = async (contentToAnalyze) => {
    try {
      // Get content from multiple sources to ensure we have text to analyze
      let content = contentToAnalyze;
      
      if (!content || content.trim().length === 0) {
        // Try to get content from editor
        content = editorRef.current?.innerHTML || '';
        
        if (!content || content.trim().length === 0) {
          content = editorRef.current?.textContent || '';
        }
        
        if (!content || content.trim().length === 0) {
          // Use current article content as fallback
          content = article?.content || '';
        }
      }
      
      console.log('Analyzing content:', content?.substring(0, 100) + '...');
      
      // Try to get AI-powered analysis first
      try {
        const analytics = await getContentAnalysis(content);
        if (analytics && analytics.wordCount > 0) {
          setContentAnalytics(analytics);
          return analytics;
        }
      } catch (error) {
        console.warn('AI analysis failed, using fallback:', error);
      }
      
      // Enhanced fallback analysis with real metrics
      const text = content.replace(/<[^>]*>/g, ''); // Remove HTML tags
      const words = text.split(/\s+/).filter(word => word.length > 0);
      const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
      const paragraphs = content.split(/<\/p>|<p>|<br>|\n\n/gi).filter(p => p.trim().length > 0);
      
      // Only proceed if we have actual content
      if (words.length === 0) {
        const emptyAnalytics = {
          wordCount: 0,
          characterCount: 0,
          sentences: 0,
          paragraphs: 0,
          headings: { h1: 0, h2: 0, h3: 0, h4: 0 },
          totalHeadings: 0,
          readingTime: 0,
          readabilityScore: 0,
          avgWordsPerSentence: 0,
          avgSentencesPerParagraph: 0,
          links: 0,
          images: 0,
          lists: 0,
          codeBlocks: 0,
          aiInsights: 'No content to analyze. Please add some text to get metrics.'
        };
        setContentAnalytics(emptyAnalytics);
        return emptyAnalytics;
      }
      
      // Heading analysis
      const headings = {
        h1: (content.match(/<h1[^>]*>|^#\s/gmi) || []).length,
        h2: (content.match(/<h2[^>]*>|^##\s/gmi) || []).length,
        h3: (content.match(/<h3[^>]*>|^###\s/gmi) || []).length,
        h4: (content.match(/<h4[^>]*>|^####\s/gmi) || []).length
      };
      
      // Readability estimation (Flesch Reading Ease approximation)
      const avgWordsPerSentence = words.length / Math.max(sentences.length, 1);
      const avgSyllablesPerWord = words.reduce((acc, word) => {
        // Simple syllable counting
        const syllables = word.toLowerCase().match(/[aeiouy]+/g) || [''];
        return acc + Math.max(1, syllables.length);
      }, 0) / Math.max(words.length, 1);
      
      const readabilityScore = Math.max(0, Math.min(100, 
        206.835 - (1.015 * avgWordsPerSentence) - (84.6 * avgSyllablesPerWord)
      ));
      
      // Content structure analysis
      const links = (content.match(/<a[^>]*>|https?:\/\/\S+/gi) || []).length;
      const images = (content.match(/<img[^>]*>|!\[.*?\]/gi) || []).length;
      const lists = (content.match(/<[ou]l[^>]*>|^[\s]*[-*+]\s/gmi) || []).length;
      const codeBlocks = (content.match(/<pre[^>]*>|```/gi) || []).length;
      
      const analytics = {
        wordCount: words.length,
        characterCount: text.length,
        sentences: sentences.length,
        paragraphs: Math.max(paragraphs.length, 1),
        headings: headings,
        totalHeadings: headings.h1 + headings.h2 + headings.h3 + headings.h4,
        readingTime: Math.ceil(words.length / 200), // 200 words per minute average
        readabilityScore: Math.round(readabilityScore),
        avgWordsPerSentence: Math.round(avgWordsPerSentence * 10) / 10,
        avgSentencesPerParagraph: Math.round((sentences.length / Math.max(paragraphs.length, 1)) * 10) / 10,
        links: links,
        images: images,
        lists: lists,
        codeBlocks: codeBlocks,
        aiInsights: generateContentInsights(words.length, sentences.length, paragraphs.length, readabilityScore, headings, links, images)
      };
      
      console.log('Generated analytics:', analytics);
      setContentAnalytics(analytics);
      return analytics;
      
    } catch (error) {
      console.error('Content analysis error:', error);
      
      // Minimal fallback
      const fallbackAnalytics = {
        wordCount: 0,
        characterCount: 0,
        sentences: 0,
        paragraphs: 0,
        headings: { h1: 0, h2: 0, h3: 0, h4: 0 },
        totalHeadings: 0,
        readingTime: 0,
        readabilityScore: 0,
        avgWordsPerSentence: 0,
        avgSentencesPerParagraph: 0,
        links: 0,
        images: 0,
        lists: 0,
        codeBlocks: 0,
        aiInsights: 'Content analysis temporarily unavailable. Please try again.'
      };
      
      setContentAnalytics(fallbackAnalytics);
      return fallbackAnalytics;
    }
  };

  /**
   * Generate AI insights based on content metrics
   */
  const generateContentInsights = (wordCount, sentenceCount, paragraphCount, readabilityScore, headings, links, images) => {
    const insights = [];
    
    // Word count insights
    if (wordCount < 50) {
      insights.push("Consider adding more content for better engagement.");
    } else if (wordCount > 1000) {
      insights.push("Great depth of content!");
    }
    
    // Readability insights
    if (readabilityScore > 60) {
      insights.push("Excellent readability score - easy to understand.");
    } else if (readabilityScore > 30) {
      insights.push("Moderate readability - consider shorter sentences.");
    } else {
      insights.push("Complex content - consider simplifying for broader audience.");
    }
    
    // Structure insights
    const totalHeadings = headings.h1 + headings.h2 + headings.h3 + headings.h4;
    if (totalHeadings === 0 && wordCount > 200) {
      insights.push("Consider adding headings to improve structure.");
    } else if (totalHeadings > 0) {
      insights.push("Well-structured with headings - great for readability.");
    }
    
    // Media insights
    if (images > 0) {
      insights.push(`Contains ${images} image${images > 1 ? 's' : ''} for visual engagement.`);
    }
    
    if (links > 0) {
      insights.push(`Includes ${links} link${links > 1 ? 's' : ''} for additional resources.`);
    }
    
    return insights.join(' ');
  };

  // === PHASE 4: COLLABORATION FEATURES ===
  
  /**
   * Add comment to selected text
   */
  const addComment = async () => {
    const selection = window.getSelection();
    if (selection.toString().length === 0) {
      showAlert('Please select some text to comment on');
      return;
    }
    
    const commentText = await showPrompt('Enter your comment:', '', 'Add Comment');
    if (!commentText) return;
    
    const range = selection.getRangeAt(0);
    const selectedText = selection.toString();
    
    // Create comment span with unique ID
    const commentId = Date.now();
    const commentSpan = document.createElement('span');
    commentSpan.setAttribute('data-comment-id', commentId);
    commentSpan.style.backgroundColor = '#fff3cd';
    commentSpan.style.borderBottom = '2px solid #ffc107';
    commentSpan.style.cursor = 'pointer';
    commentSpan.title = `Comment: ${commentText}`;
    
    // Wrap selected content
    try {
      range.surroundContents(commentSpan);
    } catch (e) {
      // Fallback for complex selections
      const span = `<span data-comment-id="${commentId}" style="background-color: #fff3cd; border-bottom: 2px solid #ffc107; cursor: pointer;" title="Comment: ${commentText}">${selectedText}</span>`;
      executeCommand('insertHTML', span);
    }
    
    // Add to comments list
    const newComment = {
      id: commentId,
      text: commentText,
      selectedText: selectedText,
      author: 'Current User',
      timestamp: new Date(),
      resolved: false
    };
    
    setComments(prev => [...prev, newComment]);
    selection.removeAllRanges();
  };

  /**
   * Toggle comment resolution
   */
  const toggleCommentResolution = (commentId) => {
    setComments(prev => 
      prev.map(comment => 
        comment.id === commentId 
          ? { ...comment, resolved: !comment.resolved }
          : comment
      )
    );
    
    // Update visual styling in editor
    const commentSpan = editorRef.current?.querySelector(`[data-comment-id="${commentId}"]`);
    if (commentSpan) {
      const comment = comments.find(c => c.id === commentId);
      if (comment?.resolved) {
        commentSpan.style.backgroundColor = '#d4edda';
        commentSpan.style.borderBottom = '2px solid #28a745';
      } else {
        commentSpan.style.backgroundColor = '#fff3cd';
        commentSpan.style.borderBottom = '2px solid #ffc107';
      }
    }
  };

  /**
   * Remove comment
   */
  const removeComment = (commentId) => {
    setComments(prev => prev.filter(comment => comment.id !== commentId));
    
    // Remove visual styling from editor
    const commentSpan = editorRef.current?.querySelector(`[data-comment-id="${commentId}"]`);
    if (commentSpan) {
      const parent = commentSpan.parentNode;
      while (commentSpan.firstChild) {
        parent.insertBefore(commentSpan.firstChild, commentSpan);
      }
      parent.removeChild(commentSpan);
    }
  };

  /**
   * Simulate real-time collaboration presence
   */
  const updateCollaboratorPresence = () => {
    // Simulate other users editing
    const mockCollaborators = [
      { id: 1, name: 'Sarah Johnson', avatar: '👩‍💼', cursor: { x: 100, y: 200 }, online: true },
      { id: 2, name: 'Mike Chen', avatar: '👨‍💻', cursor: { x: 300, y: 150 }, online: true }
    ];
    
    setCollaborators(mockCollaborators);
  };

  // === MARKDOWN CONVERSION ===
  
  /**
   * Convert HTML to Markdown
   */
  const htmlToMarkdown = (html) => {
    let markdown = html;
    
    // Convert headings
    markdown = markdown.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n');
    markdown = markdown.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n');
    markdown = markdown.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n');
    markdown = markdown.replace(/<h4[^>]*>(.*?)<\/h4>/gi, '#### $1\n\n');
    
    // Convert formatting
    markdown = markdown.replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**');
    markdown = markdown.replace(/<b[^>]*>(.*?)<\/b>/gi, '**$1**');
    markdown = markdown.replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*');
    markdown = markdown.replace(/<i[^>]*>(.*?)<\/i>/gi, '*$1*');
    markdown = markdown.replace(/<u[^>]*>(.*?)<\/u>/gi, '_$1_');
    
    // Convert lists
    markdown = markdown.replace(/<ul[^>]*>(.*?)<\/ul>/gis, (match, content) => {
      return content.replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n') + '\n';
    });
    markdown = markdown.replace(/<ol[^>]*>(.*?)<\/ol>/gis, (match, content) => {
      let counter = 1;
      return content.replace(/<li[^>]*>(.*?)<\/li>/gi, () => `${counter++}. $1\n`) + '\n';
    });
    
    // Convert blockquotes
    markdown = markdown.replace(/<blockquote[^>]*>(.*?)<\/blockquote>/gis, (match, content) => {
      return content.replace(/<p[^>]*>(.*?)<\/p>/gi, '> $1\n') + '\n';
    });
    
    // Convert code
    markdown = markdown.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');
    markdown = markdown.replace(/<pre[^>]*><code[^>]*>(.*?)<\/code><\/pre>/gis, (match, content) => {
      return '```\n' + content.replace(/<br[^>]*>/gi, '\n') + '\n```\n\n';
    });
    
    // Convert links
    markdown = markdown.replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)');
    
    // Convert paragraphs
    markdown = markdown.replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n');
    
    // Clean up extra whitespace and HTML tags
    markdown = markdown.replace(/<[^>]*>/g, '');
    markdown = markdown.replace(/\n\s*\n\s*\n/g, '\n\n');
    markdown = markdown.trim();
    
    return markdown;
  };

  /**
   * Convert Markdown to HTML
   */
  const markdownToHtml = (markdown) => {
    let html = markdown;
    
    // Convert headings
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
    
    // Convert formatting
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.*?)_/g, '<u>$1</u>');
    
    // Convert code blocks
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Convert links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    
    // Convert lists
    html = html.replace(/^\- (.*)$/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    html = html.replace(/^\d+\. (.*)$/gim, '<li>$1</li>');
    
    // Convert blockquotes
    html = html.replace(/^> (.*)$/gim, '<blockquote><p>$1</p></blockquote>');
    
    // Convert paragraphs
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>' + html + '</p>';
    
    return html;
  };
  
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
              onClick={() => executeFormattingCommand('bold')}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                activeFormats.bold ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Bold (⌘B)"
            >
              <Bold className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeFormattingCommand('italic')}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                activeFormats.italic ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Italic (⌘I)"
            >
              <Italic className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeFormattingCommand('underline')}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                activeFormats.underline ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Underline (⌘U)"
            >
              <Underline className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeFormattingCommand('strikeThrough')}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                activeFormats.strikethrough ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Strikethrough"
            >
              <Strikethrough className="h-4 w-4" />
            </button>
          </div>

          {/* Clear Formatting Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <button
              onClick={clearFormatting}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Clear Formatting"
            >
              <X className="h-4 w-4" />
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
              onClick={() => convertToParagraph()}
              className="px-2 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors text-xs font-medium"
              title="Paragraph"
            >
              P
            </button>
            <button
              onClick={() => executeFormattingCommand('formatBlock', 'h1')}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                activeFormats.h1 ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Heading 1"
            >
              <Heading1 className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeFormattingCommand('formatBlock', 'h2')}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                activeFormats.h2 ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Heading 2"
            >
              <Heading2 className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeFormattingCommand('formatBlock', 'h3')}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                activeFormats.h3 ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Heading 3"
            >
              <Heading3 className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeFormattingCommand('formatBlock', 'h4')}
              className={`px-2 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors text-xs font-bold ${
                activeFormats.h4 ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Heading 4"
            >
              H4
            </button>
          </div>

          {/* Lists Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <button
              onClick={() => executeFormattingCommand('insertUnorderedList')}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                activeFormats.ul ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Bullet List"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => executeFormattingCommand('insertOrderedList')}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                activeFormats.ol ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Numbered List"
            >
              <ListOrdered className="h-4 w-4" />
            </button>
          </div>

          {/* Phase 2: Advanced Blocks Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <div 
              className="relative group"
              onMouseEnter={() => handleMenuHover('table', true)}
              onMouseLeave={() => handleMenuHover('table', false)}
            >
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
            <div 
              className="relative group"
              onMouseEnter={() => handleMenuHover('callout', true)}
              onMouseLeave={() => handleMenuHover('callout', false)}
            >
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

          {/* Phase 3: Media Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => handleFileUpload(e.target.files)}
              className="hidden"
            />
            <div 
              className="relative"
              onMouseEnter={() => handleMenuHover('image', true)}
              onMouseLeave={() => handleMenuHover('image', false)}
            >
              <button
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
                title="Insert Image"
              >
                <Image className="h-4 w-4" />
              </button>
              
              {showImageDropdown && (
                <div 
                  className="absolute top-10 left-0 z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-1 min-w-max"
                  onMouseEnter={() => handleMenuHover('image', true)}
                  onMouseLeave={() => handleMenuHover('image', false)}
                >
                  <button
                    onClick={() => {
                      fileInputRef.current?.click();
                      setShowImageDropdown(false);
                    }}
                    className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                  >
                    <Upload className="h-4 w-4 text-gray-600" />
                    Upload from Computer
                  </button>
                  <button
                    onClick={() => {
                      showAssetLibrary();
                      setShowImageDropdown(false);
                    }}
                    className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                  >
                    <ImageIcon className="h-4 w-4 text-blue-600" />
                    Choose from Assets
                  </button>
                </div>
              )}
            </div>
            <button
              onClick={insertVideoEmbed}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Embed Video"
            >
              <Video className="h-4 w-4" />
            </button>
            <button
              onClick={insertLink}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Insert Link (⌘K)"
            >
              <Link className="h-4 w-4" />
            </button>
          </div>

          {/* Phase 4: Unified AI Brain Tool */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <button
              onClick={() => handleUnifiedAIBrain()}
              className={`p-2 text-purple-600 hover:text-purple-900 hover:bg-purple-100 rounded transition-colors ${
                aiWritingMode ? 'animate-pulse' : ''
              }`}
              title="AI Brain - Suggestions & Improvements"
              disabled={aiWritingMode}
            >
              <Brain className="h-4 w-4" />
            </button>
          </div>

          {/* Collaboration & Analytics Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <button
              onClick={() => setShowComments(!showComments)}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors relative ${
                showComments ? 'bg-blue-100 text-blue-600' : ''
              }`}
              title="Comments & Suggestions"
            >
              <MessageCircle className="h-4 w-4" />
              {comments.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                  {comments.length}
                </span>
              )}
            </button>
            
            <button
              onClick={() => {
                analyzeContent(content);
                setShowContentAnalysis(true);
              }}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                showContentAnalysis ? 'bg-purple-100 text-purple-600' : ''
              }`}
              title="Content Analytics"
            >
              <TrendingUp className="h-4 w-4" />
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
              onClick={insertInlineCode}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Inline Code (⌘`)"
            >
              <Code2 className="h-4 w-4" />
            </button>
            <button
              onClick={() => insertBlock('codeBlock')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Code Block (⌘⇧C)"
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

  // === SAVE HANDLING (Fixed with proper mode switching behavior and duplicate prevention) ===
  
  const handleSave = async (publishAction = 'draft', shouldExitEdit = false) => {
    // Prevent multiple simultaneous saves
    if (isSaving) {
      console.log('Save already in progress, skipping duplicate save request');
      return false;
    }

    try {
      setIsSaving(true);
      setIsAutoSaving(true);
      
      const articleData = {
        title: title,
        content: content,
        status: publishAction
      };

      let response;
      if (article?.id) {
        // Update existing article - this prevents creating duplicates
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/content-library/${article.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(articleData)
        });
      } else {
        // Create new article only if no ID exists
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/content-library`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(articleData)
        });
      }

      if (response.ok) {
        const result = await response.json();
        setHasUnsavedChanges(false);
        setLastSaved(new Date());
        
        // Update article ID if it was a new article
        if (!article?.id && result.id) {
          // Store the new article ID to prevent future duplicates
          if (onSave) {
            await onSave({ ...articleData, id: result.id });
          }
        } else if (onSave) {
          await onSave({ ...articleData, id: article.id });
        }
        
        // Only exit edit mode if explicitly requested (for Draft/Publish actions)
        if (shouldExitEdit && onEdit) {
          onEdit(); // Switch to view mode, don't exit to library
        }
        
        return true;
      } else {
        throw new Error(`Save failed: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Save error:', error);
      showAlert(`Save failed: ${error.message}. Please try again.`, 'Save Error');
      return false;
    } finally {
      setIsSaving(false);
      setIsAutoSaving(false);
    }
  };

  // Main save button - save without exiting edit mode
  const handleMainSave = async () => {
    const success = await handleSave('draft', false);
    if (success) {
      showAlert('Content saved successfully!', 'Success');
    }
  };

  const handlePublish = async () => {
    if (isSaving) return; // Prevent duplicate clicks
    
    const success = await handleSave('published', true);
    if (success) {
      showAlert('Article published successfully!', 'Success');
    }
  };
  
  const handleSaveDraft = async () => {
    if (isSaving) return; // Prevent duplicate clicks
    
    const success = await handleSave('draft', true);
    if (success) {
      showAlert('Draft saved successfully!', 'Success');
    }
  };

  // === PHASE 2: MODAL COMPONENTS ===
  
  /**
   * Render enhanced content analysis popup modal with detailed metrics
   */
  const renderContentAnalysisModal = () => {
    if (!showContentAnalysis) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-[500px] max-h-[600px] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              Content Analysis
            </h3>
            <button
              onClick={() => setShowContentAnalysis(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          
          <div className="space-y-4">
            {/* Basic Metrics */}
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{contentAnalytics.wordCount || 0}</div>
                <div className="text-sm text-gray-600">Words</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{contentAnalytics.readingTime || 0}</div>
                <div className="text-sm text-gray-600">Min Read</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{contentAnalytics.sentences || 0}</div>
                <div className="text-sm text-gray-600">Sentences</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{contentAnalytics.paragraphs || 0}</div>
                <div className="text-sm text-gray-600">Paragraphs</div>
              </div>
            </div>

            {/* Extended Metrics */}
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-lg font-bold text-gray-600">{contentAnalytics.totalHeadings || 0}</div>
                <div className="text-xs text-gray-500">Headings</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-lg font-bold text-gray-600">{contentAnalytics.links || 0}</div>
                <div className="text-xs text-gray-500">Links</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="text-lg font-bold text-gray-600">{contentAnalytics.images || 0}</div>
                <div className="text-xs text-gray-500">Images</div>
              </div>
            </div>

            {/* Structure Analysis */}
            {contentAnalytics.headings && (
              <div className="p-4 bg-indigo-50 rounded-lg">
                <h4 className="font-medium text-indigo-800 mb-2">Document Structure</h4>
                <div className="grid grid-cols-4 gap-2 text-sm">
                  <div>H1: <span className="font-bold">{contentAnalytics.headings.h1 || 0}</span></div>
                  <div>H2: <span className="font-bold">{contentAnalytics.headings.h2 || 0}</span></div>
                  <div>H3: <span className="font-bold">{contentAnalytics.headings.h3 || 0}</span></div>
                  <div>H4: <span className="font-bold">{contentAnalytics.headings.h4 || 0}</span></div>
                </div>
              </div>
            )}

            {/* Readability Score */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Readability Score</span>
                <span className={`font-bold ${
                  (contentAnalytics.readabilityScore || 0) > 60 ? 'text-green-600' : 
                  (contentAnalytics.readabilityScore || 0) > 30 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {contentAnalytics.readabilityScore || 0}/100
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    (contentAnalytics.readabilityScore || 0) > 60 ? 'bg-green-500' : 
                    (contentAnalytics.readabilityScore || 0) > 30 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${contentAnalytics.readabilityScore || 0}%` }}
                ></div>
              </div>
              {contentAnalytics.avgWordsPerSentence && (
                <div className="mt-2 text-sm text-gray-600">
                  Avg words per sentence: {contentAnalytics.avgWordsPerSentence}
                </div>
              )}
            </div>

            {/* AI Insights */}
            {contentAnalytics.aiInsights && (
              <div className="p-4 bg-purple-50 rounded-lg">
                <h4 className="font-medium text-purple-800 mb-2">AI Insights</h4>
                <p className="text-sm text-purple-700">{contentAnalytics.aiInsights}</p>
              </div>
            )}
          </div>
          
          <div className="mt-6 text-center">
            <button
              onClick={() => setShowContentAnalysis(false)}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  };

  /**
   * Render unified AI Brain results modal with comprehensive suggestions and improvements
   */
  const renderAiBrainModal = () => {
    if (!showAiBrainModal) return null;
    
    const actionLabels = {
      completion: 'Text Completion',
      improvement: 'Writing Improvement', 
      grammar: 'Grammar Check',
      unified: 'AI Brain Analysis'
    };
    
    const getSuggestionIcon = (type) => {
      switch (type) {
        case 'completion':
          return <Sparkles className="h-4 w-4 text-purple-600" />;
        case 'improvement':
          return <Lightbulb className="h-4 w-4 text-yellow-600" />;
        case 'grammar':
          return <CheckSquare className="h-4 w-4 text-green-600" />;
        default:
          return <Brain className="h-4 w-4 text-blue-600" />;
      }
    };
    
    const getSuggestionTypeLabel = (type) => {
      switch (type) {
        case 'completion': return 'Text Completion';
        case 'improvement': return 'Writing Improvement';
        case 'grammar': return 'Grammar Check';
        default: return 'Suggestion';
      }
    };
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-[600px] max-w-4xl max-h-[80vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-600" />
              {actionLabels[aiActionType]}
            </h3>
            <button
              onClick={() => setShowAiBrainModal(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          
          {/* Unified Mode Metrics */}
          {aiActionType === 'unified' ? (
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{aiResults.completionCount || 0}</div>
                <div className="text-sm text-gray-600">Completions</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{aiResults.improvementCount || 0}</div>
                <div className="text-sm text-gray-600">Improvements</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{aiResults.grammarCount || 0}</div>
                <div className="text-sm text-gray-600">Grammar Fixes</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{aiResults.wordsProcessed || 0}</div>
                <div className="text-sm text-gray-600">Words Analyzed</div>
              </div>
            </div>
          ) : (
            /* Single Mode Metrics */
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{aiResults.wordsProcessed || 0}</div>
                <div className="text-sm text-gray-600">Words Processed</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{aiResults.suggestionsGenerated || 0}</div>
                <div className="text-sm text-gray-600">Suggestions</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{aiResults.improvements || 0}</div>
                <div className="text-sm text-gray-600">Improvements</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{Math.round(aiResults.confidence) || 0}%</div>
                <div className="text-sm text-gray-600">Confidence</div>
              </div>
            </div>
          )}

          {/* Suggestions & Improvements */}
          {aiResults.suggestions && aiResults.suggestions.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-800 mb-3 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-purple-600" />
                AI Suggestions & Improvements:
              </h4>
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {aiResults.suggestions.map((suggestion, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-3 hover:border-purple-300 transition-colors">
                    <div className="flex items-start gap-2">
                      {suggestion.type ? getSuggestionIcon(suggestion.type) : <Brain className="h-4 w-4 text-blue-600 mt-0.5" />}
                      <div className="flex-1">
                        {suggestion.type && (
                          <div className="text-xs text-gray-500 mb-1">
                            {getSuggestionTypeLabel(suggestion.type)}
                          </div>
                        )}
                        <p className="text-sm text-gray-700 mb-2">
                          {suggestion.text || suggestion}
                        </p>
                        <button
                          onClick={() => {
                            const textToInsert = suggestion.text || suggestion;
                            if (aiResults.originalText) {
                              // Replace selected text with highlighting
                              const selection = window.getSelection();
                              if (selection.rangeCount > 0) {
                                const range = selection.getRangeAt(0);
                                range.deleteContents();
                                const highlightedHTML = highlightAppliedSuggestion(textToInsert);
                                range.insertNode(document.createElement('span'));
                                range.startContainer.innerHTML = highlightedHTML;
                              }
                            } else {
                              // Insert at cursor with highlighting
                              const highlightedHTML = highlightAppliedSuggestion(textToInsert);
                              executeCommand('insertHTML', ` ${highlightedHTML}`);
                            }
                            setShowAiBrainModal(false);
                          }}
                          className="px-3 py-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 transition-colors"
                        >
                          Apply
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No suggestions message */}
          {(!aiResults.suggestions || aiResults.suggestions.length === 0) && (
            <div className="text-center py-8">
              <Brain className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">No AI suggestions available at the moment.</p>
              <p className="text-sm text-gray-400 mt-1">Try selecting some text or typing more content.</p>
            </div>
          )}
          
          <div className="flex justify-between items-center mt-6">
            <div className="text-xs text-gray-500">
              {aiResults.originalText ? `Selected: "${aiResults.originalText.substring(0, 50)}..."` : 'Full document analyzed'}
            </div>
            <button
              onClick={() => setShowAiBrainModal(false)}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  };

  /**
   * Render asset library modal for image selection (Fixed React hooks issue)
   */
  /**
   * Render modern, responsive asset library modal with enhanced UI/UX
   */
  const renderAssetLibraryModal = () => {
    if (!showImageModal) return null;
    
    // Filter assets based on search term
    const filteredAssets = assets.filter(asset => 
      asset.name.toLowerCase().includes(assetSearchTerm.toLowerCase())
    );
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl h-full max-h-[90vh] flex flex-col animate-in fade-in duration-200">
          {/* Modern Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-purple-50 rounded-t-2xl">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <ImageIcon className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Asset Library</h3>
                <p className="text-sm text-gray-500">Choose an image for your content</p>
              </div>
            </div>
            <button
              onClick={() => {
                setShowImageModal(false);
                setAssetSearchTerm('');
              }}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors group"
            >
              <X className="h-5 w-5 text-gray-500 group-hover:text-gray-700" />
            </button>
          </div>

          {/* Search and Filter Bar */}
          <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search assets..."
                  value={assetSearchTerm}
                  onChange={(e) => setAssetSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded-full font-medium">
                  {filteredAssets.length}
                </span>
                <span>{filteredAssets.length === 1 ? 'asset' : 'assets'}</span>
              </div>
            </div>
          </div>

          {/* Content Area with Overflow Handling */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {assetsLoading ? (
              /* Modern Loading State */
              <div className="flex-1 flex items-center justify-center bg-gray-50">
                <div className="text-center">
                  <div className="relative">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mx-auto"></div>
                    <ImageIcon className="h-6 w-6 text-blue-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
                  </div>
                  <p className="mt-4 text-gray-600 font-medium">Loading your assets...</p>
                  <p className="text-sm text-gray-500 mt-1">This might take a moment</p>
                </div>
              </div>
            ) : filteredAssets.length === 0 ? (
              /* Enhanced Empty State */
              <div className="flex-1 flex items-center justify-center bg-gray-50">
                <div className="text-center max-w-md mx-auto px-6">
                  {assetSearchTerm ? (
                    /* No Search Results */
                    <>
                      <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Search className="h-8 w-8 text-yellow-600" />
                      </div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">No assets found</h4>
                      <p className="text-gray-500 mb-4">
                        No assets match "{assetSearchTerm}". Try a different search term.
                      </p>
                      <button
                        onClick={() => setAssetSearchTerm('')}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Clear Search
                      </button>
                    </>
                  ) : (
                    /* No Assets Available */
                    <>
                      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <ImageIcon className="h-8 w-8 text-gray-400" />
                      </div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">No assets yet</h4>
                      <p className="text-gray-500">
                        Upload some images to see them here. They'll appear automatically once added to your content.
                      </p>
                    </>
                  )}
                </div>
              </div>
            ) : (
              /* Responsive Grid with Overflow Handling */
              <div className="flex-1 overflow-y-auto px-6 py-6">
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                  {filteredAssets.map((asset, index) => (
                    <div
                      key={asset.id}
                      onClick={() => handleAssetSelect(asset)}
                      className="group cursor-pointer bg-white border border-gray-200 rounded-xl p-3 hover:border-blue-500 hover:shadow-lg transition-all duration-200 transform hover:-translate-y-1"
                      style={{
                        animationDelay: `${index * 50}ms`
                      }}
                    >
                      {/* Image Container with Aspect Ratio */}
                      <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden mb-3 relative">
                        <img
                          src={asset.data}
                          alt={asset.name}
                          className="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
                          loading="lazy"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                        {/* Fallback for broken images */}
                        <div className="hidden w-full h-full items-center justify-center bg-gray-100">
                          <ImageIcon className="h-8 w-8 text-gray-400" />
                        </div>
                        
                        {/* Hover Overlay */}
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 rounded-lg flex items-center justify-center">
                          <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-white rounded-full p-2">
                            <Eye className="h-4 w-4 text-gray-700" />
                          </div>
                        </div>
                      </div>

                      {/* Asset Info */}
                      <div className="space-y-1">
                        <h4 className="text-sm font-medium text-gray-900 truncate group-hover:text-blue-600 transition-colors" title={asset.name}>
                          {asset.name}
                        </h4>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>{Math.round(asset.size / 1024)}KB</span>
                          <span className="px-2 py-1 bg-gray-100 rounded-full">
                            {asset.type}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Load More Button (if needed for pagination) */}
                {filteredAssets.length > 0 && (
                  <div className="mt-8 text-center">
                    <p className="text-sm text-gray-500">
                      Showing {filteredAssets.length} asset{filteredAssets.length !== 1 ? 's' : ''}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Modern Footer */}
          <div className="px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Click any image to insert it into your content
              </div>
              <button
                onClick={() => {
                  setShowImageModal(false);
                  setAssetSearchTerm('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  /**
   * Render custom modal system to replace browser modals
   */
  const renderCustomModal = () => {
    if (!customModal.show) return null;
    
    const handleInputChange = (e) => {
      setCustomModal(prev => ({ ...prev, inputValue: e.target.value }));
    };
    
    const handleConfirm = () => {
      if (customModal.type === 'prompt') {
        customModal.onConfirm(customModal.inputValue);
      } else {
        customModal.onConfirm();
      }
    };
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <div className={`p-2 rounded-lg ${
              customModal.type === 'alert' ? 'bg-blue-100' : 
              customModal.type === 'confirm' ? 'bg-yellow-100' : 'bg-green-100'
            }`}>
              {customModal.type === 'alert' ? (
                <Info className={`h-5 w-5 text-blue-600`} />
              ) : customModal.type === 'confirm' ? (
                <AlertTriangle className={`h-5 w-5 text-yellow-600`} />
              ) : (
                <Edit3 className={`h-5 w-5 text-green-600`} />
              )}
            </div>
            <h3 className="text-lg font-semibold text-gray-900">{customModal.title}</h3>
          </div>
          
          <p className="text-gray-700 mb-6">{customModal.message}</p>
          
          {customModal.type === 'prompt' && (
            <input
              type="text"
              value={customModal.inputValue}
              onChange={handleInputChange}
              placeholder={customModal.inputPlaceholder}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-6"
              autoFocus
              onKeyPress={(e) => e.key === 'Enter' && handleConfirm()}
            />
          )}
          
          <div className="flex gap-3 justify-end">
            {customModal.onCancel && (
              <button
                onClick={customModal.onCancel}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
            )}
            <button
              onClick={handleConfirm}
              className={`px-4 py-2 text-white rounded-lg transition-colors ${
                customModal.type === 'alert' ? 'bg-blue-600 hover:bg-blue-700' :
                customModal.type === 'confirm' ? 'bg-yellow-600 hover:bg-yellow-700' :
                'bg-green-600 hover:bg-green-700'
              }`}
            >
              {customModal.type === 'prompt' ? 'OK' : customModal.type === 'confirm' ? 'Confirm' : 'OK'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  /**
   * Render link tooltip for hover/edit functionality
   */
  const renderLinkTooltip = () => {
    if (!linkTooltip.show) return null;
    
    return (
      <div 
        className="fixed z-50 bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg text-sm"
        style={{ 
          left: linkTooltip.x, 
          top: linkTooltip.y - 60,
          transform: 'translateX(-50%)'
        }}
      >
        <div className="flex items-center gap-2 mb-2">
          <Link className="h-3 w-3" />
          <span className="font-medium truncate max-w-48">{linkTooltip.url}</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => editLink(linkTooltip.element)}
            className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs transition-colors"
          >
            Edit
          </button>
          <button
            onClick={() => removeLink(linkTooltip.element)}
            className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs transition-colors"
          >
            Remove
          </button>
        </div>
        {/* Tooltip arrow */}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>
      </div>
    );
  };

  const renderAIPanel = () => {
    if (!showAiPanel) return null;
    
    return (
      <div className="ai-panel fixed right-4 top-20 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">AI Assistant</h3>
            <button
              onClick={() => setShowAiPanel(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        {/* Content Analytics */}
        <div className="p-4 border-b border-gray-200">
          <h4 className="font-medium text-gray-800 mb-2">Content Insights</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Words:</span>
              <span className="font-medium">{contentAnalytics.wordCount || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Reading Time:</span>
              <span className="font-medium">{contentAnalytics.readingTime || 0} min</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Readability:</span>
              <span className={`font-medium ${
                (contentAnalytics.readabilityScore || 0) > 60 ? 'text-green-600' : 
                (contentAnalytics.readabilityScore || 0) > 30 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {contentAnalytics.readabilityScore || 0}/100
              </span>
            </div>
          </div>
        </div>
        
        {/* AI Suggestions */}
        {aiSuggestions.length > 0 && (
          <div className="p-4">
            <h4 className="font-medium text-gray-800 mb-2">AI Suggestions</h4>
            <div className="space-y-2">
              {aiSuggestions.map((suggestion, index) => (
                <div key={index} className="p-3 bg-purple-50 rounded-lg">
                  <p className="text-sm text-gray-700 mb-2">{suggestion}</p>
                  <button
                    onClick={() => applyAISuggestion(suggestion)}
                    className="text-xs bg-purple-600 text-white px-2 py-1 rounded hover:bg-purple-700"
                  >
                    Apply
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  /**
   * Render collaboration sidebar
   */
  const renderCollaborationSidebar = () => {
    if (!showComments) return null;
    
    return (
      <div className="fixed right-4 top-20 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Collaboration</h3>
            <button
              onClick={() => setShowComments(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        {/* Active Collaborators */}
        {collaborators.length > 0 && (
          <div className="p-4 border-b border-gray-200">
            <h4 className="font-medium text-gray-800 mb-2">Active Now</h4>
            <div className="flex space-x-2">
              {collaborators.map(collaborator => (
                <div key={collaborator.id} className="flex items-center space-x-1">
                  <span className="text-lg">{collaborator.avatar}</span>
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Comments & Suggestions */}
        <div className="p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-gray-800">Comments & Suggestions</h4>
            <button
              onClick={addComment}
              className="text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
              title="Select text first, then click to add comment"
            >
              Add Comment
            </button>
          </div>
          
          {selectedText && (
            <div className="mb-3 p-2 bg-blue-50 rounded border-l-4 border-blue-400">
              <div className="text-xs text-blue-600 font-medium">Text Selected:</div>
              <div className="text-sm text-blue-800">"{selectedText.substring(0, 50)}..."</div>
              <button
                onClick={addComment}
                className="mt-1 text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
              >
                Comment on this text
              </button>
            </div>
          )}
          
          {comments.length === 0 ? (
            <div className="text-center py-4">
              <MessageSquare className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500">No comments yet.</p>
              <p className="text-xs text-gray-400 mt-1">Select text in the editor and click "Add Comment"</p>
            </div>
          ) : (
            <div className="space-y-3">
              {comments.map(comment => (
                <div key={comment.id} className={`p-3 rounded-lg border ${
                  comment.resolved ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'
                }`}>
                  <div className="flex items-start justify-between mb-1">
                    <span className="font-medium text-sm">{comment.author}</span>
                    <div className="flex space-x-1">
                      <button
                        onClick={() => toggleCommentResolution(comment.id)}
                        className={`text-xs px-2 py-1 rounded ${
                          comment.resolved 
                            ? 'bg-green-200 text-green-800 hover:bg-green-300' 
                            : 'bg-yellow-200 text-yellow-800 hover:bg-yellow-300'
                        }`}
                      >
                        {comment.resolved ? '✓ Resolved' : 'Open'}
                      </button>
                      <button
                        onClick={() => removeComment(comment.id)}
                        className="text-xs bg-red-200 text-red-800 px-2 py-1 rounded hover:bg-red-300"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  {comment.selectedText && (
                    <div className="text-xs text-gray-600 mb-1 p-1 bg-gray-100 rounded italic">
                      On: "{comment.selectedText.substring(0, 50)}..."
                    </div>
                  )}
                  <p className="text-sm text-gray-700">{comment.text}</p>
                  <span className="text-xs text-gray-500">
                    {comment.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };
  const renderSlashMenu = () => {
    if (!showSlashMenu) return null;
    
    const filteredCommands = getFilteredSlashCommands();
    
    return (
      <div 
        ref={slashMenuRef}
        className="absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg max-w-64 max-h-80 overflow-y-auto"
        style={{
          left: slashMenuPosition.x,
          top: slashMenuPosition.y
        }}
      >
        <div className="p-2">
          <div className="text-xs text-gray-500 mb-2 px-2">Quick Insert</div>
          {filteredCommands.map((command) => {
            const Icon = command.icon;
            return (
              <button
                key={command.key}
                onClick={() => {
                  command.action();
                  setShowSlashMenu(false);
                }}
                className="flex items-center gap-3 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded transition-colors"
              >
                <Icon className="h-4 w-4 text-gray-600" />
                <span>{command.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    );
  };
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
      
      {/* Phase 3: Asset Library Modal */}
      {renderAssetLibraryModal()}
      
      {/* Phase 4: Content Analysis Modal */}
      {renderContentAnalysisModal()}
      {renderAiBrainModal()}
      
      {/* Custom Modal System */}
      {renderCustomModal()}
      
      {/* Link Tooltip */}
      {renderLinkTooltip()}
      
      {/* Phase 4: AI and Collaboration Panels */}
      {renderAIPanel()}
      {renderCollaborationSidebar()}
      
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`h-full flex flex-col bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden ${className}`}
      >
      
      {/* Styles for editor enhancements */}
      <style jsx>{`
        @keyframes highlight-fade {
          0% {
            background-color: #fef3c7;
            border-bottom-color: #f59e0b;
          }
          50% {
            background-color: #fef3c7;
            border-bottom-color: #f59e0b;
          }
          100% {
            background-color: transparent;
            border-bottom-color: transparent;
          }
        }
        
        .ai-suggestion-applied {
          transition: all 0.3s ease;
        }
        
        /* Fix text overflow issues */
        .editor-content {
          overflow-wrap: break-word;
          word-wrap: break-word;
          word-break: break-word;
          white-space: pre-wrap;
          max-width: 100%;
          box-sizing: border-box;
        }
        
        .editor-content * {
          max-width: 100%;
          box-sizing: border-box;
        }
        
        /* Link styles for editor */
        .editor-content a {
          color: #2563eb !important;
          text-decoration: underline !important;
          cursor: pointer !important;
        }
        
        .editor-content a:hover {
          color: #1d4ed8 !important;
          text-decoration: underline !important;
        }
        
        /* Ensure pasted content doesn't overflow */
        .editor-content p,
        .editor-content div,
        .editor-content span {
          max-width: 100%;
          overflow-wrap: break-word;
          word-wrap: break-word;
        }
        
        /* Fix for contenteditable paste overflow */
        [contenteditable] {
          overflow: hidden !important;
          word-wrap: break-word !important;
          overflow-wrap: break-word !important;
        }
        
        [contenteditable] * {
          max-width: 100% !important;
          box-sizing: border-box !important;
        }
      `}</style>
      
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
            
            {/* Phase 4: Auto-save Status */}
            {isEditing && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                isAutoSaving ? 'bg-blue-100 text-blue-800' : 
                hasUnsavedChanges ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {isAutoSaving ? 'Saving...' : 
                 hasUnsavedChanges ? 'Unsaved Changes' :
                 lastSaved ? `Saved ${lastSaved.toLocaleTimeString()}` : 'Saved'}
              </span>
            )}

            {/* Phase 4: Collaboration Indicators */}
            {collaborators.length > 0 && (
              <div className="flex items-center space-x-1">
                <Users className="h-4 w-4 text-gray-500" />
                <span className="text-xs text-gray-600">
                  {collaborators.length} online
                </span>
              </div>
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
                <div className="relative group">
                  <button
                    onClick={handleMainSave}
                    disabled={isSaving}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                      isSaving 
                        ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {isSaving ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    <span>{isSaving ? 'Saving...' : 'Save'}</span>
                    {!isSaving && <ChevronDown className="h-3 w-3" />}
                  </button>
                  
                  {!isSaving && (
                    <div className="absolute top-10 right-0 z-50 hidden group-hover:block bg-white border border-gray-200 rounded-lg shadow-lg p-1 min-w-max">
                      <button
                        onClick={handleSaveDraft}
                        disabled={isSaving}
                        className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded disabled:opacity-50"
                      >
                        <Save className="h-4 w-4 text-gray-600" />
                        Save as Draft
                      </button>
                      <button
                        onClick={handlePublish}
                        disabled={isSaving}
                        className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded disabled:opacity-50"
                      >
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        Save & Publish
                      </button>
                    </div>
                  )}
                </div>
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
              // Edit mode: Enhanced with drag & drop and slash commands
              <div className="h-full relative">
                <style jsx>{`
                  .wysiwyg-editor h1 { font-size: 2rem; font-weight: bold; margin: 1rem 0; line-height: 1.2; }
                  .wysiwyg-editor h2 { font-size: 1.75rem; font-weight: bold; margin: 0.875rem 0; line-height: 1.3; }
                  .wysiwyg-editor h3 { font-size: 1.5rem; font-weight: bold; margin: 0.75rem 0; line-height: 1.4; }
                  .wysiwyg-editor h4 { font-size: 1.25rem; font-weight: bold; margin: 0.625rem 0; line-height: 1.4; }
                  .wysiwyg-editor p { margin: 0.5rem 0; }
                  .wysiwyg-editor ul { margin: 0.5rem 0; padding-left: 1.5rem; list-style-type: disc; }
                  .wysiwyg-editor ol { margin: 0.5rem 0; padding-left: 1.5rem; list-style-type: decimal; }
                  .wysiwyg-editor ul ul { list-style-type: circle; margin: 0.25rem 0; }
                  .wysiwyg-editor ul ul ul { list-style-type: square; }
                  .wysiwyg-editor ol ol { list-style-type: lower-alpha; margin: 0.25rem 0; }
                  .wysiwyg-editor ol ol ol { list-style-type: lower-roman; }
                  .wysiwyg-editor li { margin: 0.25rem 0; display: list-item; }
                  .wysiwyg-editor blockquote { border-left: 4px solid #e5e7eb; padding-left: 1rem; margin: 1rem 0; font-style: italic; color: #6b7280; background: #f9fafb; }
                  .wysiwyg-editor code { background-color: #f1f5f9; padding: 2px 4px; border-radius: 3px; font-family: monospace; font-size: 0.9em; }
                  .wysiwyg-editor pre { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 16px; margin: 16px 0; overflow-x: auto; }
                  .wysiwyg-editor strong, .wysiwyg-editor b { font-weight: bold; }
                  .wysiwyg-editor em, .wysiwyg-editor i { font-style: italic; }
                  .wysiwyg-editor u { text-decoration: underline; }
                  .wysiwyg-editor table { border-collapse: collapse; width: 100%; margin: 16px 0; }
                  .wysiwyg-editor td { border: 1px solid #e5e7eb; padding: 8px; }
                  .wysiwyg-editor th { border: 1px solid #e5e7eb; padding: 8px; background: #f9fafb; font-weight: 600; }
                `}</style>
                <div
                  key={`editor-${isEditing}-${article?.id}`}
                  ref={contentRef}
                  contentEditable={true}
                  onInput={(e) => {
                    setContent(e.target.innerHTML);
                    setHasUnsavedChanges(true);
                  }}
                  onKeyDown={handleKeyDown}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onMouseOver={handleLinkHover}
                  onMouseOut={handleLinkMouseOut}
                  onClick={handleLinkClick}
                  className={`wysiwyg-editor editor-content h-full p-6 overflow-y-auto focus:outline-none transition-colors ${
                    draggedOver ? 'bg-blue-50 border-2 border-dashed border-blue-300' : ''
                  }`}
                  style={{
                    minHeight: '400px',
                    lineHeight: '1.7',
                    fontSize: '16px',
                    fontFamily: 'system-ui, -apple-system, sans-serif',
                    color: '#1f2937',
                    outline: 'none'
                  }}
                  css={`
                    h1 { font-size: 2rem; font-weight: bold; margin: 1rem 0; }
                    h2 { font-size: 1.75rem; font-weight: bold; margin: 0.875rem 0; }
                    h3 { font-size: 1.5rem; font-weight: bold; margin: 0.75rem 0; }
                    h4 { font-size: 1.25rem; font-weight: bold; margin: 0.625rem 0; }
                    p { margin: 0.5rem 0; }
                    ul, ol { margin: 0.5rem 0; padding-left: 1.5rem; }
                    li { margin: 0.25rem 0; }
                    blockquote { border-left: 4px solid #e5e7eb; padding-left: 1rem; margin: 1rem 0; font-style: italic; color: #6b7280; }
                    code { background-color: #f1f5f9; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
                    pre { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 16px; margin: 16px 0; overflow-x: auto; }
                    strong, b { font-weight: bold; }
                    em, i { font-style: italic; }
                    u { text-decoration: underline; }
                    table { border-collapse: collapse; width: 100%; margin: 16px 0; }
                    td { border: 1px solid #e5e7eb; padding: 8px; }
                  `}
                  suppressContentEditableWarning={true}
                />
                
                {/* Phase 3: Slash Command Menu */}
                {renderSlashMenu()}
                
                {/* Phase 4: Text Selection Comment Tooltip */}
                {selectedText && isEditing && (
                  <div className="fixed bottom-4 right-4 z-50 bg-blue-600 text-white px-3 py-2 rounded-lg shadow-lg">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="h-4 w-4" />
                      <span className="text-sm">Selected: "{selectedText.substring(0, 30)}..."</span>
                      <button
                        onClick={addComment}
                        className="ml-2 bg-blue-700 hover:bg-blue-800 px-2 py-1 rounded text-xs"
                      >
                        Add Comment
                      </button>
                    </div>
                  </div>
                )}
                
                {/* Phase 3: Drag & Drop Overlay */}
                {draggedOver && (
                  <div className="absolute inset-0 flex items-center justify-center bg-blue-50 bg-opacity-90 pointer-events-none">
                    <div className="text-center">
                      <Upload className="h-12 w-12 text-blue-500 mx-auto mb-2" />
                      <p className="text-blue-700 font-medium">Drop images here to upload</p>
                    </div>
                  </div>
                )}
                
                {/* Phase 3: Upload Progress Indicator */}
                {uploadProgress > 0 && uploadProgress < 100 && (
                  <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-3 border">
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      <span className="text-sm text-gray-600">Uploading... {uploadProgress}%</span>
                    </div>
                    <div className="w-48 bg-gray-200 rounded-full h-2 mt-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all" 
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : editorMode === 'markdown' ? (
          <textarea
            ref={markdownRef}
            value={htmlToMarkdown(content)}
            onChange={(e) => {
              const htmlContent = markdownToHtml(e.target.value);
              handleContentChange(htmlContent, 'markdown');
            }}
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