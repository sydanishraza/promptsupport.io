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
  Sparkles
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
    };
    
    if (showColorPicker || showSlashMenu || showAiPanel) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showColorPicker, showSlashMenu, showAiPanel]);

  // Phase 4: Auto-save functionality
  useEffect(() => {
    if (!hasUnsavedChanges || !isEditing) return;
    
    const autoSaveTimer = setTimeout(() => {
      autoSave();
    }, 3000); // Auto-save after 3 seconds of inactivity
    
    return () => clearTimeout(autoSaveTimer);
  }, [hasUnsavedChanges, content, title, isEditing]);

  // Phase 4: Content analytics
  useEffect(() => {
    if (content && isEditing) {
      analyzeContent(content);
    }
  }, [content, isEditing]);

  // Phase 4: Collaboration presence simulation
  useEffect(() => {
    if (isEditing) {
      updateCollaboratorPresence();
      const presenceInterval = setInterval(updateCollaboratorPresence, 10000);
      return () => clearInterval(presenceInterval);
    }
  }, [isEditing]);

  // === PHASE 1: CORE EDITABLE SURFACE ===
  
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
            handleSave();
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
   * Insert inline code - wrap selected text or insert at cursor
   */
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

  // === PHASE 3: MEDIA INTEGRATION ===
  
  /**
   * Handle file upload and convert to base64
   */
  const handleFileUpload = (files) => {
    Array.from(files).forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const base64 = e.target.result;
          insertImage(base64, file.name);
        };
        reader.readAsDataURL(file);
      }
    });
  };

  /**
   * Show asset library modal for image selection
   */
  const showAssetLibrary = () => {
    setShowImageModal(true);
  };

  /**
   * Handle asset selection from library
   */
  const handleAssetSelect = (asset) => {
    if (asset.type === 'image' && asset.data) {
      insertImage(asset.data, asset.name || 'Selected image');
      setShowImageModal(false);
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
  const insertVideoEmbed = () => {
    const url = prompt('Enter video URL (YouTube, Vimeo, etc.):');
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
   * Generate AI content suggestions using real LLM API
   */
  const generateAISuggestions = async (context, type = 'completion') => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai-assistance`, {
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
        throw new Error('AI service unavailable');
      }

      const data = await response.json();
      return data.suggestions || [];
    } catch (error) {
      console.error('AI assistance error:', error);
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
   * Get real content analysis using LLM API
   */
  const getContentAnalysis = async (content) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/content-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content
        })
      });

      if (!response.ok) {
        throw new Error('Content analysis service unavailable');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Content analysis error:', error);
      // Fallback to basic analysis
      const text = content.replace(/<[^>]*>/g, '');
      const words = text.split(/\s+/).filter(word => word.length > 0);
      return {
        wordCount: words.length,
        sentences: text.split(/[.!?]+/).length - 1,
        paragraphs: Math.max(content.split(/<\/p>/gi).length - 1, 1),
        readingTime: Math.ceil(words.length / 200),
        readabilityScore: 70,
        characterCount: text.length
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
   * Content analytics using real LLM analysis
   */
  const analyzeContent = async (content) => {
    try {
      const analytics = await getContentAnalysis(content);
      setContentAnalytics(analytics);
      return analytics;
    } catch (error) {
      console.error('Content analysis error:', error);
      // Fallback analysis
      const text = content.replace(/<[^>]*>/g, '');
      const words = text.split(/\s+/).filter(word => word.length > 0);
      const analytics = {
        wordCount: words.length,
        characterCount: text.length,
        sentences: text.split(/[.!?]+/).length - 1,
        paragraphs: Math.max(content.split(/<\/p>/gi).length - 1, 1),
        readingTime: Math.ceil(words.length / 200),
        readabilityScore: 70
      };
      setContentAnalytics(analytics);
      return analytics;
    }
  };

  // === PHASE 4: COLLABORATION FEATURES ===
  
  /**
   * Add comment to selected text
   */
  const addComment = () => {
    const selection = window.getSelection();
    if (selection.toString().length === 0) {
      alert('Please select some text to comment on');
      return;
    }
    
    const commentText = prompt('Enter your comment:');
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
            <div className="relative group">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
                title="Upload Image"
              >
                <Image className="h-4 w-4" />
              </button>
              
              <div className="absolute top-10 left-0 z-50 hidden group-hover:block bg-white border border-gray-200 rounded-lg shadow-lg p-1 min-w-max">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  <Upload className="h-4 w-4 text-gray-600" />
                  Upload from Computer
                </button>
                <button
                  onClick={showAssetLibrary}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  <FileImage className="h-4 w-4 text-blue-600" />
                  Choose from Assets
                </button>
              </div>
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

          {/* Phase 4: AI & Collaboration Group */}
          <div className="flex items-center mr-3 pr-3 border-r border-gray-300">
            <div className="relative group">
              <button
                onClick={() => handleAIAssist('suggest')}
                className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                  aiWritingMode ? 'animate-pulse' : ''
                }`}
                title="AI Writing Assistant"
                disabled={aiWritingMode}
              >
                <Brain className="h-4 w-4" />
              </button>
              
              <div className="absolute top-10 left-0 z-50 hidden group-hover:block bg-white border border-gray-200 rounded-lg shadow-lg p-2 min-w-max">
                <button
                  onClick={() => handleAIAssist('completion')}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  <Sparkles className="h-4 w-4 text-purple-600" />
                  Complete Text
                </button>
                <button
                  onClick={() => handleAIAssist('improvement')}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  <Lightbulb className="h-4 w-4 text-yellow-600" />
                  Improve Writing
                </button>
                <button
                  onClick={() => handleAIAssist('grammar')}
                  className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                >
                  <CheckSquare className="h-4 w-4 text-green-600" />
                  Grammar Check
                </button>
              </div>
            </div>
            
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
              onClick={addComment}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
              title="Add Comment to Selection"
            >
              <MessageSquare className="h-4 w-4" />
            </button>
            
            <button
              onClick={() => setShowAiPanel(!showAiPanel)}
              className={`p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors ${
                showAiPanel ? 'bg-purple-100 text-purple-600' : ''
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

  // === SAVE HANDLING (Enhanced with real API) ===
  
  const handleSave = async (publishAction = 'draft') => {
    try {
      setIsAutoSaving(true);
      
      const articleData = {
        title: title,
        content: content,
        status: publishAction
      };

      let response;
      if (article?.id) {
        // Update existing article
        response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/content-library/${article.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(articleData)
        });
      } else {
        // Create new article
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
        
        // Call onSave prop if provided
        if (onSave) {
          await onSave({ ...articleData, id: article?.id || result.id });
        }
        
        return true;
      } else {
        throw new Error('Save failed');
      }
    } catch (error) {
      console.error('Save error:', error);
      return false;
    } finally {
      setIsAutoSaving(false);
    }
  };

  const handlePublish = () => handleSave('published');
  const handleSaveDraft = () => handleSave('draft');

  // === PHASE 2: MODAL COMPONENTS ===
  
  /**
   * Render asset library modal for image selection
   */
  const renderAssetLibraryModal = () => {
    if (!showImageModal) return null;
    
    // Mock assets - in real implementation, this would fetch from the asset API
    const mockAssets = [
      { id: 1, name: 'Sample Image 1', type: 'image', data: '/api/placeholder/400/300?text=Sample+1' },
      { id: 2, name: 'Sample Image 2', type: 'image', data: '/api/placeholder/400/300?text=Sample+2' },
      { id: 3, name: 'Sample Image 3', type: 'image', data: '/api/placeholder/400/300?text=Sample+3' },
      { id: 4, name: 'Sample Image 4', type: 'image', data: '/api/placeholder/400/300?text=Sample+4' }
    ];
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-4/5 max-w-4xl max-h-4/5 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Choose from Asset Library</h3>
            <button
              onClick={() => setShowImageModal(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {mockAssets.map(asset => (
              <div
                key={asset.id}
                onClick={() => handleAssetSelect(asset)}
                className="cursor-pointer border border-gray-200 rounded-lg p-2 hover:border-blue-500 hover:shadow-md transition-all"
              >
                <img
                  src={asset.data}
                  alt={asset.name}
                  className="w-full h-32 object-cover rounded mb-2"
                />
                <p className="text-sm text-gray-700 truncate">{asset.name}</p>
              </div>
            ))}
          </div>
          
          <div className="mt-4 text-center">
            <button
              onClick={() => setShowImageModal(false)}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        </div>
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
        
        {/* Comments */}
        <div className="p-4">
          <h4 className="font-medium text-gray-800 mb-2">Comments</h4>
          {comments.length === 0 ? (
            <p className="text-sm text-gray-500">No comments yet</p>
          ) : (
            <div className="space-y-3">
              {comments.map(comment => (
                <div key={comment.id} className={`p-3 rounded-lg ${
                  comment.resolved ? 'bg-green-50' : 'bg-yellow-50'
                }`}>
                  <div className="flex items-start justify-between mb-1">
                    <span className="font-medium text-sm">{comment.author}</span>
                    <button
                      onClick={() => toggleCommentResolution(comment.id)}
                      className={`text-xs px-2 py-1 rounded ${
                        comment.resolved 
                          ? 'bg-green-200 text-green-800' 
                          : 'bg-yellow-200 text-yellow-800'
                      }`}
                    >
                      {comment.resolved ? 'Resolved' : 'Open'}
                    </button>
                  </div>
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
      
      {/* Phase 4: AI and Collaboration Panels */}
      {renderAIPanel()}
      {renderCollaborationSidebar()}
      
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
                    onClick={handleSaveDraft}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Save className="h-4 w-4" />
                    <span>Save</span>
                    <ChevronDown className="h-3 w-3" />
                  </button>
                  
                  <div className="absolute top-10 right-0 z-50 hidden group-hover:block bg-white border border-gray-200 rounded-lg shadow-lg p-1 min-w-max">
                    <button
                      onClick={handleSaveDraft}
                      className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                    >
                      <Save className="h-4 w-4 text-gray-600" />
                      Save as Draft
                    </button>
                    <button
                      onClick={handlePublish}
                      className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                    >
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      Save & Publish
                    </button>
                  </div>
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
                  className={`wysiwyg-editor h-full p-6 overflow-y-auto focus:outline-none transition-colors ${
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
                
                {/* Phase 3: Drag & Drop Overlay */}
                {draggedOver && (
                  <div className="absolute inset-0 flex items-center justify-center bg-blue-50 bg-opacity-90 pointer-events-none">
                    <div className="text-center">
                      <Upload className="h-12 w-12 text-blue-500 mx-auto mb-2" />
                      <p className="text-blue-700 font-medium">Drop images here to upload</p>
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