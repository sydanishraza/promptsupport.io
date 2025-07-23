import React, { useEffect, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import { Table } from '@tiptap/extension-table';
import { TableRow } from '@tiptap/extension-table-row';
import { TableHeader } from '@tiptap/extension-table-header';
import { TableCell } from '@tiptap/extension-table-cell';
import { Typography } from '@tiptap/extension-typography';
import { TextStyle } from '@tiptap/extension-text-style';
import { Color } from '@tiptap/extension-color';
import { Highlight } from '@tiptap/extension-highlight';
import { Blockquote } from '@tiptap/extension-blockquote';
import { HorizontalRule } from '@tiptap/extension-horizontal-rule';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { createLowlight } from 'lowlight';
import { marked } from 'marked';
import TurndownService from 'turndown';
import { 
  Bold, 
  Italic, 
  Strikethrough, 
  Code, 
  Heading1, 
  Heading2, 
  Heading3,
  List,
  ListOrdered,
  Quote,
  Link as LinkIcon,
  Image as ImageIcon,
  Minus,
  Undo,
  Redo,
  Eye,
  Edit,
  FileText,
  Save,
  Type,
  Code2,
  Table as TableIcon,
  Highlighter,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  Palette
} from 'lucide-react';

const AdvancedEditor = ({ content, onChange, onSave, isReadOnly = false, height = '400px' }) => {
  const [mode, setMode] = useState('wysiwyg'); // wysiwyg, markdown, html
  const [markdownContent, setMarkdownContent] = useState('');

  // Initialize lowlight
  const lowlight = createLowlight();

  // Initialize markdown parser
  const turndownService = new TurndownService({
    headingStyle: 'atx',
    bulletListMarker: '-',
    codeBlockStyle: 'fenced'
  });

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        codeBlock: false, // We'll use CodeBlockLowlight instead
      }),
      Typography,
      TextStyle,
      Color,
      Highlight.configure({
        multicolor: true,
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-600 underline hover:text-blue-800',
        },
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'rounded-lg max-w-full h-auto',
        },
      }),
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
      Table.configure({
        resizable: true,
      }),
      TableRow,
      TableHeader,
      TableCell,
      Blockquote.configure({
        HTMLAttributes: {
          class: 'border-l-4 border-gray-300 pl-4 italic my-4',
        },
      }),
      HorizontalRule,
      CodeBlockLowlight.configure({
        lowlight,
        HTMLAttributes: {
          class: 'bg-gray-100 rounded p-4 my-4 overflow-x-auto',
        },
      }),
    ],
    content: '',
    editable: !isReadOnly,
    onUpdate: ({ editor }) => {
      if (onChange && mode === 'wysiwyg') {
        onChange(editor.getHTML());
      }
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none min-h-[200px] p-4',
        style: 'line-height: 1.6;'
      },
    },
    parseOptions: {
      preserveWhitespace: 'full',
    },
  });

  // Convert markdown to HTML with better parsing
  const markdownToHtml = (markdown) => {
    try {
      // Configure marked for better rendering
      marked.setOptions({
        gfm: true,
        breaks: false,
        sanitize: false,
        smartLists: true,
        smartypants: true,
      });
      
      return marked(markdown);
    } catch (error) {
      console.error('Error converting markdown to HTML:', error);
      return `<p>${markdown}</p>`;
    }
  };

  // Convert HTML to markdown with better parsing
  const htmlToMarkdown = (html) => {
    try {
      return turndownService.turndown(html);
    } catch (error) {
      console.error('Error converting HTML to markdown:', error);
      return html;
    }
  };

  // Initialize content based on format with better detection
  useEffect(() => {
    if (editor && content !== undefined) {
      let htmlContent = content;
      
      // Better markdown detection
      const hasMarkdownSyntax = content.includes('#') || 
                                content.includes('**') || 
                                content.includes('- ') || 
                                content.includes('1. ') ||
                                content.includes('```') ||
                                content.includes('> ');
      
      const hasHtmlTags = content.includes('<') && content.includes('>');
      
      if (hasMarkdownSyntax && !hasHtmlTags) {
        // Convert markdown to HTML for editor
        htmlContent = markdownToHtml(content);
        setMarkdownContent(content);
      } else {
        // Content is HTML, convert to markdown for storage
        setMarkdownContent(htmlToMarkdown(content));
      }
      
      if (editor.getHTML() !== htmlContent) {
        editor.commands.setContent(htmlContent);
      }
    }
  }, [editor, content]);

  // Handle mode switching
  const handleModeSwitch = (newMode) => {
    if (mode === newMode || !editor) return;

    const currentContent = getCurrentContent();
    
    setMode(newMode);
    
    // Convert content based on new mode
    if (newMode === 'wysiwyg') {
      const htmlContent = mode === 'markdown' ? markdownToHtml(currentContent) : currentContent;
      editor.commands.setContent(htmlContent);
    } else if (newMode === 'markdown') {
      const markdownConvert = mode === 'html' ? htmlToMarkdown(currentContent) : htmlToMarkdown(editor.getHTML());
      setMarkdownContent(markdownConvert);
    }
  };

  // Get current content based on mode
  const getCurrentContent = () => {
    if (mode === 'wysiwyg') {
      return editor.getHTML();
    } else if (mode === 'markdown') {
      return markdownContent;
    } else {
      return editor.getHTML();
    }
  };

  // Handle content changes in different modes
  const handleContentChange = (newContent) => {
    if (mode === 'markdown') {
      setMarkdownContent(newContent);
      if (onChange) {
        onChange(markdownToHtml(newContent));
      }
    } else if (mode === 'html') {
      editor.commands.setContent(newContent);
      if (onChange) {
        onChange(newContent);
      }
    }
  };

  if (!editor) {
    return (
      <div className="border border-gray-300 rounded-lg p-4" style={{ height }}>
        <div className="flex items-center justify-center h-full">
          <div className="text-gray-500">Loading advanced editor...</div>
        </div>
      </div>
    );
  }

  const ToolbarButton = ({ onClick, active = false, disabled = false, children, title }) => (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`p-2 rounded hover:bg-gray-100 transition-colors ${
        active ? 'bg-blue-100 text-blue-600' : 'text-gray-600'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {children}
    </button>
  );

  const renderToolbar = () => (
    <div className="border-b border-gray-300 p-2 flex flex-wrap gap-1 bg-gray-50">
      {/* Text Formatting - Only show when not read-only */}
      {!isReadOnly && (
        <div className="flex border-r border-gray-200 pr-2 mr-2">
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleBold().run()}
            active={editor.isActive('bold')}
            title="Bold"
          >
            <Bold size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleItalic().run()}
            active={editor.isActive('italic')}
            title="Italic"
          >
            <Italic size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleStrike().run()}
            active={editor.isActive('strike')}
            title="Strikethrough"
          >
            <Strikethrough size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleCode().run()}
            active={editor.isActive('code')}
            title="Inline Code"
          >
            <Code size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleHighlight().run()}
            active={editor.isActive('highlight')}
            title="Highlight"
          >
            <Highlighter size={16} />
          </ToolbarButton>
        </div>
      )}

      {/* Headings - Only show when not read-only */}
      {!isReadOnly && (
        <div className="flex border-r border-gray-200 pr-2 mr-2">
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            active={editor.isActive('heading', { level: 1 })}
            title="Heading 1"
          >
            <Heading1 size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            active={editor.isActive('heading', { level: 2 })}
            title="Heading 2"
          >
            <Heading2 size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
            active={editor.isActive('heading', { level: 3 })}
            title="Heading 3"
          >
            <Heading3 size={16} />
          </ToolbarButton>
        </div>
      )}

      {/* Lists - Only show when not read-only */}
      {!isReadOnly && (
        <div className="flex border-r border-gray-200 pr-2 mr-2">
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            active={editor.isActive('bulletList')}
            title="Bullet List"
          >
            <List size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            active={editor.isActive('orderedList')}
            title="Numbered List"
          >
            <ListOrdered size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleTaskList().run()}
            active={editor.isActive('taskList')}
            title="Task List"
          >
            <FileText size={16} />
          </ToolbarButton>
        </div>
      )}

      {/* Other - Only show when not read-only */}
      {!isReadOnly && (
        <div className="flex border-r border-gray-200 pr-2 mr-2">
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            active={editor.isActive('blockquote')}
            title="Quote"
          >
            <Quote size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleCodeBlock().run()}
            active={editor.isActive('codeBlock')}
            title="Code Block"
          >
            <Code2 size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().setHorizontalRule().run()}
            title="Horizontal Line"
          >
            <Minus size={16} />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()}
            title="Insert Table"
          >
            <TableIcon size={16} />
          </ToolbarButton>
        </div>
      )}

      {/* Mode Toggle Buttons - Always visible */}
      <div className="flex border-r border-gray-200 pr-2 mr-2">
        <ToolbarButton
          onClick={() => handleModeSwitch('wysiwyg')}
          active={mode === 'wysiwyg'}
          title="WYSIWYG Editor"
        >
          <Edit size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => handleModeSwitch('markdown')}
          active={mode === 'markdown'}
          title="Markdown Editor"
        >
          <Type size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => handleModeSwitch('html')}
          active={mode === 'html'}
          title="HTML Editor"
        >
          <Code2 size={16} />
        </ToolbarButton>
      </div>

      {/* Save Button - Only show when not read-only and onSave is provided */}
      {!isReadOnly && onSave && (
        <div className="flex ml-auto">
          <button
            type="button"
            onClick={onSave}
            className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm flex items-center gap-1"
          >
            <Save size={14} />
            Save
          </button>
        </div>
      )}

      {/* View Mode Indicator - Show when read-only */}
      {isReadOnly && (
        <div className="flex items-center ml-auto text-sm text-gray-500">
          <Eye size={14} className="mr-1" />
          Read Only
        </div>
      )}
    </div>
  );

  const renderEditor = () => {
    if (mode === 'markdown') {
      return (
        <div className="p-4" style={{ height: `calc(${height} - 60px)` }}>
          <textarea
            className="w-full h-full font-mono text-sm border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={markdownContent}
            onChange={(e) => handleContentChange(e.target.value)}
            placeholder="Enter Markdown content..."
            readOnly={isReadOnly}
          />
        </div>
      );
    }

    if (mode === 'html') {
      return (
        <div className="p-4" style={{ height: `calc(${height} - 60px)` }}>
          <textarea
            className="w-full h-full font-mono text-sm border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={editor.getHTML()}
            onChange={(e) => handleContentChange(e.target.value)}
            placeholder="Enter HTML content..."
            readOnly={isReadOnly}
          />
        </div>
      );
    }

    return (
      <div className="overflow-auto" style={{ height: `calc(${height} - 60px)` }}>
        <EditorContent 
          editor={editor} 
          className="h-full"
        />
      </div>
    );
  };

  return (
    <div className="border border-gray-300 rounded-lg overflow-hidden bg-white" style={{ height }}>
      {renderToolbar()}
      <style jsx>{`
        .ProseMirror {
          outline: none;
          padding: 1rem;
          line-height: 1.6;
        }
        
        .ProseMirror h1 {
          font-size: 2.25rem !important;
          font-weight: 700 !important;
          line-height: 1.2 !important;
          margin: 2rem 0 1rem 0 !important;
          color: #1f2937 !important;
          border-bottom: 2px solid #e5e7eb !important;
          padding-bottom: 0.5rem !important;
        }
        
        .ProseMirror h2 {
          font-size: 1.875rem !important;
          font-weight: 600 !important;
          line-height: 1.3 !important;
          margin: 1.75rem 0 0.75rem 0 !important;
          color: #374151 !important;
        }
        
        .ProseMirror h3 {
          font-size: 1.5rem !important;
          font-weight: 600 !important;
          line-height: 1.4 !important;
          margin: 1.5rem 0 0.5rem 0 !important;
          color: #4b5563 !important;
        }
        
        .ProseMirror h4 {
          font-size: 1.25rem;
          font-weight: 600;
          line-height: 1.4;
          margin: 1.25rem 0 0.5rem 0;
          color: #6b7280;
        }
        
        .ProseMirror p {
          margin: 1rem 0;
          line-height: 1.7;
          color: #374151;
        }
        
        .ProseMirror ul {
          list-style-type: disc !important;
          margin: 1rem 0 !important;
          padding-left: 2rem !important;
        }
        
        .ProseMirror ol {
          list-style-type: decimal !important;
          margin: 1rem 0 !important;
          padding-left: 2rem !important;
        }
        
        .ProseMirror li {
          margin: 0.5rem 0 !important;
          line-height: 1.6 !important;
          color: #374151 !important;
          display: list-item !important;
        }
        
        .ProseMirror li p {
          margin: 0.25rem 0;
        }
        
        .ProseMirror blockquote {
          border-left: 4px solid #3b82f6;
          padding-left: 1rem;
          margin: 1.5rem 0;
          font-style: italic;
          color: #6b7280;
          background-color: #f8fafc;
          padding: 1rem;
          border-radius: 0.375rem;
        }
        
        .ProseMirror code {
          background-color: #f1f5f9;
          padding: 0.125rem 0.25rem;
          border-radius: 0.25rem;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 0.875rem;
          color: #dc2626;
        }
        
        .ProseMirror pre {
          background-color: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 0.5rem;
          padding: 1rem;
          margin: 1.5rem 0;
          overflow-x: auto;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 0.875rem;
          line-height: 1.5;
        }
        
        .ProseMirror table {
          border-collapse: collapse;
          margin: 1.5rem 0;
          width: 100%;
          border: 1px solid #d1d5db;
        }
        
        .ProseMirror th,
        .ProseMirror td {
          border: 1px solid #d1d5db;
          padding: 0.75rem;
          text-align: left;
          vertical-align: top;
        }
        
        .ProseMirror th {
          background-color: #f9fafb;
          font-weight: 600;
          color: #374151;
        }
        
        .ProseMirror td {
          color: #4b5563;
        }
        
        .ProseMirror hr {
          margin: 2rem 0;
          border: none;
          border-top: 2px solid #e5e7eb;
        }
        
        .ProseMirror strong {
          font-weight: 600;
          color: #1f2937;
        }
        
        .ProseMirror em {
          font-style: italic;
          color: #4b5563;
        }
        
        .ProseMirror mark {
          background-color: #fef3c7;
          padding: 0.125rem 0.25rem;
          border-radius: 0.25rem;
        }
        
        .ProseMirror a {
          color: #3b82f6;
          text-decoration: underline;
        }
        
        .ProseMirror a:hover {
          color: #1d4ed8;
        }
        
        .ProseMirror img {
          max-width: 100%;
          height: auto;
          border-radius: 0.5rem;
          margin: 1rem 0;
        }
        
        .ProseMirror ul[data-type="taskList"] {
          list-style: none;
          padding-left: 0;
        }
        
        .ProseMirror li[data-type="taskItem"] {
          display: flex;
          align-items: flex-start;
        }
        
        .ProseMirror li[data-type="taskItem"] > label {
          margin-right: 0.5rem;
          margin-top: 0.125rem;
        }
        
        .ProseMirror li[data-type="taskItem"] > div {
          flex: 1;
        }
      `}</style>
      {renderEditor()}
    </div>
  );
};

export default AdvancedEditor;