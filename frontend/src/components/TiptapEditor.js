import React, { useEffect, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
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
  Save
} from 'lucide-react';

const TiptapEditor = ({ content, onChange, onSave, isReadOnly = false, height = '400px' }) => {
  const [mode, setMode] = useState('wysiwyg'); // wysiwyg, markdown, html

  const editor = useEditor({
    extensions: [
      StarterKit,
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
    ],
    content: content || '<p>Start writing...</p>',
    editable: !isReadOnly,
    onUpdate: ({ editor }) => {
      if (onChange) {
        onChange(editor.getHTML());
      }
    },
  });

  // Update editor content when prop changes
  useEffect(() => {
    if (editor && content !== undefined && editor.getHTML() !== content) {
      editor.commands.setContent(content);
    }
  }, [editor, content]);

  if (!editor) {
    return (
      <div className="border border-gray-300 rounded-lg p-4" style={{ height }}>
        <div className="flex items-center justify-center h-full">
          <div className="text-gray-500">Loading editor...</div>
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
    <div className="border-b border-gray-300 p-2 flex flex-wrap gap-1">
      {/* Text Formatting */}
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
      </div>

      {/* Headings */}
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

      {/* Lists */}
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
          <Code size={16} />
        </ToolbarButton>
      </div>

      {/* Other */}
      <div className="flex border-r border-gray-200 pr-2 mr-2">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          active={editor.isActive('blockquote')}
          title="Quote"
        >
          <Quote size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          title="Horizontal Line"
        >
          <Minus size={16} />
        </ToolbarButton>
      </div>

      {/* Undo/Redo */}
      <div className="flex border-r border-gray-200 pr-2 mr-2">
        <ToolbarButton
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          title="Undo"
        >
          <Undo size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          title="Redo"
        >
          <Redo size={16} />
        </ToolbarButton>
      </div>

      {/* Mode Toggle */}
      <div className="flex border-r border-gray-200 pr-2 mr-2">
        <ToolbarButton
          onClick={() => setMode(mode === 'wysiwyg' ? 'html' : 'wysiwyg')}
          active={mode === 'html'}
          title="Toggle HTML/WYSIWYG"
        >
          {mode === 'wysiwyg' ? <Code size={16} /> : <Eye size={16} />}
        </ToolbarButton>
      </div>

      {/* Save Button */}
      {onSave && (
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
    </div>
  );

  const renderEditor = () => {
    if (mode === 'html') {
      return (
        <div className="p-4" style={{ height: `calc(${height} - 60px)` }}>
          <textarea
            className="w-full h-full font-mono text-sm border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={editor.getHTML()}
            onChange={(e) => {
              editor.commands.setContent(e.target.value);
              if (onChange) {
                onChange(e.target.value);
              }
            }}
            placeholder="Enter HTML content..."
            readOnly={isReadOnly}
          />
        </div>
      );
    }

    return (
      <div className="p-4 prose prose-sm max-w-none" style={{ height: `calc(${height} - 60px)` }}>
        <EditorContent 
          editor={editor} 
          className="h-full overflow-y-auto focus:outline-none"
        />
      </div>
    );
  };

  return (
    <div className="border border-gray-300 rounded-lg overflow-hidden bg-white" style={{ height }}>
      {!isReadOnly && renderToolbar()}
      {renderEditor()}
    </div>
  );
};

export default TiptapEditor;
  const [markdownContent, setMarkdownContent] = useState('');
  const [htmlContent, setHtmlContent] = useState('');

  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-600 underline hover:text-blue-800',
        },
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full h-auto rounded-lg',
        },
      }),
      Table.configure({
        resizable: true,
        HTMLAttributes: {
          class: 'border-collapse table-auto w-full',
        },
      }),
      CodeBlockLowlight.configure({
        lowlight,
        HTMLAttributes: {
          class: 'bg-gray-100 rounded-lg p-4 font-mono text-sm',
        },
      }),
      TaskList.configure({
        HTMLAttributes: {
          class: 'task-list',
        },
      }),
      TaskItem.configure({
        nested: true,
        HTMLAttributes: {
          class: 'task-item',
        },
      }),
    ],
    content: content || '<p>Start writing your article...</p>',
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none',
        style: `min-height: ${height}`,
      },
    },
    onUpdate: ({ editor }) => {
      if (onChange) {
        onChange(editor.getHTML());
      }
    },
    editable: !isReadOnly,
  });

  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content || '<p>Start writing your article...</p>');
    }
  }, [content, editor]);

  useEffect(() => {
    if (editor) {
      // Convert to markdown when switching modes
      if (mode === 'markdown') {
        // Simple HTML to Markdown conversion (in production, use a proper converter)
        const html = editor.getHTML();
        const markdown = convertHtmlToMarkdown(html);
        setMarkdownContent(markdown);
      } else if (mode === 'html') {
        setHtmlContent(editor.getHTML());
      }
    }
  }, [mode, editor]);

  const convertHtmlToMarkdown = (html) => {
    // Simple conversion - in production use a proper HTML to Markdown converter
    return html
      .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1')
      .replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1')
      .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1')
      .replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**')
      .replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*')
      .replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<[^>]*>/g, '');
  };

  const ToolbarButton = ({ onClick, isActive, disabled, children, title }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`p-2 rounded-lg transition-colors ${
        isActive 
          ? 'bg-blue-100 text-blue-600' 
          : disabled
          ? 'text-gray-300 cursor-not-allowed'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
      }`}
    >
      {children}
    </button>
  );

  if (!editor) {
    return (
      <div className="border border-gray-300 rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      </div>
    );
  }

  return (
    <div className="border border-gray-300 rounded-lg overflow-hidden">
      {/* Mode Tabs */}
      <div className="border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between px-4 py-2">
          <div className="flex space-x-1">
            <button
              onClick={() => setMode('wysiwyg')}
              className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                mode === 'wysiwyg'
                  ? 'bg-white text-gray-900 border border-gray-300'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center space-x-1">
                <Edit size={14} />
                <span>WYSIWYG</span>
              </div>
            </button>
            <button
              onClick={() => setMode('markdown')}
              className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                mode === 'markdown'
                  ? 'bg-white text-gray-900 border border-gray-300'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center space-x-1">
                <FileText size={14} />
                <span>Markdown</span>
              </div>
            </button>
            <button
              onClick={() => setMode('html')}
              className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                mode === 'html'
                  ? 'bg-white text-gray-900 border border-gray-300'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center space-x-1">
                <Code size={14} />
                <span>HTML</span>
              </div>
            </button>
          </div>
          
          {onSave && (
            <button
              onClick={onSave}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-sm"
            >
              <Save size={14} />
              <span>Save</span>
            </button>
          )}
        </div>
      </div>

      {/* Toolbar */}
      {mode === 'wysiwyg' && !isReadOnly && (
        <div className="border-b border-gray-200 p-3 bg-white">
          <div className="flex flex-wrap items-center gap-1">
            {/* History */}
            <div className="flex items-center space-x-1 mr-3">
              <ToolbarButton
                onClick={() => editor.chain().focus().undo().run()}
                disabled={!editor.can().chain().focus().undo().run()}
                title="Undo"
              >
                <Undo size={16} />
              </ToolbarButton>
              <ToolbarButton
                onClick={() => editor.chain().focus().redo().run()}
                disabled={!editor.can().chain().focus().redo().run()}
                title="Redo"
              >
                <Redo size={16} />
              </ToolbarButton>
            </div>

            <div className="h-6 w-px bg-gray-300 mr-3" />

            {/* Text Formatting */}
            <div className="flex items-center space-x-1 mr-3">
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleBold().run()}
                isActive={editor.isActive('bold')}
                title="Bold"
              >
                <Bold size={16} />
              </ToolbarButton>
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleItalic().run()}
                isActive={editor.isActive('italic')}
                title="Italic"
              >
                <Italic size={16} />
              </ToolbarButton>
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleStrike().run()}
                isActive={editor.isActive('strike')}
                title="Strikethrough"
              >
                <Strikethrough size={16} />
              </ToolbarButton>
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleCode().run()}
                isActive={editor.isActive('code')}
                title="Inline Code"
              >
                <Code size={16} />
              </ToolbarButton>
            </div>

            <div className="h-6 w-px bg-gray-300 mr-3" />

            {/* Headings */}
            <div className="flex items-center space-x-1 mr-3">
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                isActive={editor.isActive('heading', { level: 1 })}
                title="Heading 1"
              >
                <Heading1 size={16} />
              </ToolbarButton>
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                isActive={editor.isActive('heading', { level: 2 })}
                title="Heading 2"
              >
                <Heading2 size={16} />
              </ToolbarButton>
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
                isActive={editor.isActive('heading', { level: 3 })}
                title="Heading 3"
              >
                <Heading3 size={16} />
              </ToolbarButton>
            </div>

            <div className="h-6 w-px bg-gray-300 mr-3" />

            {/* Lists */}
            <div className="flex items-center space-x-1 mr-3">
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleBulletList().run()}
                isActive={editor.isActive('bulletList')}
                title="Bullet List"
              >
                <List size={16} />
              </ToolbarButton>
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleOrderedList().run()}
                isActive={editor.isActive('orderedList')}
                title="Numbered List"
              >
                <ListOrdered size={16} />
              </ToolbarButton>
            </div>

            <div className="h-6 w-px bg-gray-300 mr-3" />

            {/* Other Elements */}
            <div className="flex items-center space-x-1">
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleBlockquote().run()}
                isActive={editor.isActive('blockquote')}
                title="Quote"
              >
                <Quote size={16} />
              </ToolbarButton>
              <ToolbarButton
                onClick={() => editor.chain().focus().setHorizontalRule().run()}
                title="Horizontal Rule"
              >
                <Minus size={16} />
              </ToolbarButton>
            </div>
          </div>
        </div>
      )}

      {/* Editor Content */}
      <div className="relative bg-white">
        {mode === 'wysiwyg' && (
          <>
            <EditorContent 
              editor={editor} 
              className="p-4 min-h-64 focus-within:outline-none"
              style={{ minHeight: height }}
            />
            
            {!isReadOnly && (
              <>
                <BubbleMenu editor={editor} tippyOptions={{ duration: 100 }}>
                  <div className="flex items-center space-x-1 bg-gray-900 rounded-lg p-2 shadow-lg">
                    <button
                      onClick={() => editor.chain().focus().toggleBold().run()}
                      className={`p-1 rounded text-white hover:bg-gray-700 ${
                        editor.isActive('bold') ? 'bg-gray-700' : ''
                      }`}
                    >
                      <Bold size={14} />
                    </button>
                    <button
                      onClick={() => editor.chain().focus().toggleItalic().run()}
                      className={`p-1 rounded text-white hover:bg-gray-700 ${
                        editor.isActive('italic') ? 'bg-gray-700' : ''
                      }`}
                    >
                      <Italic size={14} />
                    </button>
                    <button
                      onClick={() => {
                        const url = window.prompt('Enter URL:');
                        if (url) {
                          editor.chain().focus().setLink({ href: url }).run();
                        }
                      }}
                      className="p-1 rounded text-white hover:bg-gray-700"
                    >
                      <LinkIcon size={14} />
                    </button>
                  </div>
                </BubbleMenu>

                <FloatingMenu editor={editor} tippyOptions={{ duration: 100 }}>
                  <div className="flex items-center space-x-1 bg-white border border-gray-300 rounded-lg p-2 shadow-lg">
                    <button
                      onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                      className="p-2 rounded hover:bg-gray-100"
                    >
                      <Heading1 size={16} />
                    </button>
                    <button
                      onClick={() => editor.chain().focus().toggleBulletList().run()}
                      className="p-2 rounded hover:bg-gray-100"
                    >
                      <List size={16} />
                    </button>
                    <button
                      onClick={() => editor.chain().focus().toggleBlockquote().run()}
                      className="p-2 rounded hover:bg-gray-100"
                    >
                      <Quote size={16} />
                    </button>
                  </div>
                </FloatingMenu>
              </>
            )}
          </>
        )}

        {mode === 'markdown' && (
          <textarea
            value={markdownContent}
            onChange={(e) => {
              setMarkdownContent(e.target.value);
              // Convert markdown back to HTML and update editor
              const html = convertMarkdownToHtml(e.target.value);
              editor.commands.setContent(html);
            }}
            className="w-full p-4 border-0 focus:outline-none font-mono text-sm resize-none"
            style={{ minHeight: height }}
            placeholder="Write in Markdown..."
          />
        )}

        {mode === 'html' && (
          <textarea
            value={htmlContent}
            onChange={(e) => {
              setHtmlContent(e.target.value);
              editor.commands.setContent(e.target.value);
            }}
            className="w-full p-4 border-0 focus:outline-none font-mono text-sm resize-none"
            style={{ minHeight: height }}
            placeholder="Write in HTML..."
          />
        )}
      </div>
    </div>
  );
};

// Simple Markdown to HTML conversion (use proper library in production)
const convertMarkdownToHtml = (markdown) => {
  return markdown
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(.*)$/gm, '<p>$1</p>')
    .replace(/<p><\/p>/g, '');
};

export default TiptapEditor;