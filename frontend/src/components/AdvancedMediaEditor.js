import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import TurndownService from 'turndown';
import { 
  Edit, 
  Eye, 
  Save, 
  X, 
  ArrowLeft,
  FileText,
  Image,
  Sparkles,
  Brain,
  Code,
  Type,
  Palette,
  Bold,
  Italic,
  Underline,
  List,
  ListOrdered,
  Quote,
  Link,
  Table,
  Heading1,
  Heading2,
  Heading3,
  Undo,
  Redo,
  AlignLeft,
  AlignCenter,
  AlignRight
} from 'lucide-react';

const AdvancedMediaEditor = ({ 
  article, 
  isEditing, 
  onEdit, 
  onSave, 
  onCancel,
  onBack,
  backendUrl 
}) => {
  const [content, setContent] = useState(article?.content || '');
  const [title, setTitle] = useState(article?.title || '');
  const [mode, setMode] = useState('wysiwyg'); // 'wysiwyg', 'markdown', 'html'
  const [processing, setProcessing] = useState(false);
  const [processedWithAI, setProcessedWithAI] = useState(false);
  const [showToolbar, setShowToolbar] = useState(true);
  const editorRef = useRef(null);
  const turndownService = new TurndownService();

  useEffect(() => {
    if (article?.content) {
      setContent(article.content);
      setTitle(article.title || '');
    }
  }, [article]);

  // Configure marked for better rendering
  marked.setOptions({
    gfm: true,
    breaks: false,
    sanitize: false,
    smartLists: true,
    smartypants: true,
  });

  const processWithAI = async () => {
    if (!article?.id || !content) return;

    setProcessing(true);
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
          setProcessedWithAI(true);
          console.log(`🎉 AI processed ${result.media_count} media items`);
        } else {
          console.error('AI processing failed:', result.error);
        }
      }
    } catch (error) {
      console.error('Error processing with AI:', error);
    } finally {
      setProcessing(false);
    }
  };

  const convertContent = (fromMode, toMode, contentToConvert) => {
    if (fromMode === toMode) return contentToConvert;

    try {
      if (fromMode === 'markdown' && toMode === 'html') {
        return marked(contentToConvert);
      } else if (fromMode === 'html' && toMode === 'markdown') {
        return turndownService.turndown(contentToConvert);
      } else if (fromMode === 'wysiwyg' && toMode === 'html') {
        return contentToConvert; // WYSIWYG stores HTML
      } else if (fromMode === 'html' && toMode === 'wysiwyg') {
        return contentToConvert; // WYSIWYG displays HTML
      } else if (fromMode === 'wysiwyg' && toMode === 'markdown') {
        return turndownService.turndown(contentToConvert);
      } else if (fromMode === 'markdown' && toMode === 'wysiwyg') {
        return marked(contentToConvert);
      }
    } catch (error) {
      console.error('Content conversion error:', error);
    }
    return contentToConvert;
  };

  const handleModeChange = (newMode) => {
    const convertedContent = convertContent(mode, newMode, content);
    setContent(convertedContent);
    setMode(newMode);
  };

  const insertFormatting = (tag, content = '') => {
    if (mode === 'wysiwyg' && editorRef.current) {
      document.execCommand('insertHTML', false, `<${tag}>${content}</${tag}>`);
    } else if (mode === 'markdown') {
      // Add markdown formatting logic
      let markdownTag = '';
      switch(tag) {
        case 'strong': markdownTag = '**'; break;
        case 'em': markdownTag = '*'; break;
        case 'h1': markdownTag = '# '; break;
        case 'h2': markdownTag = '## '; break;
        case 'h3': markdownTag = '### '; break;
        default: markdownTag = '';
      }
      if (markdownTag) {
        setContent(prev => prev + markdownTag + content + markdownTag);
      }
    }
  };

  const renderToolbar = () => (
    <div className="border-b border-gray-200 p-2 flex items-center space-x-1 flex-wrap bg-gray-50">
      {/* Mode Toggle */}
      <div className="flex items-center space-x-1 mr-4 border-r border-gray-300 pr-4">
        <button
          onClick={() => handleModeChange('wysiwyg')}
          className={`px-3 py-1 text-sm rounded ${
            mode === 'wysiwyg' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
          }`}
          title="WYSIWYG Editor"
        >
          <Type className="h-4 w-4 inline mr-1" />
          WYSIWYG
        </button>
        <button
          onClick={() => handleModeChange('markdown')}
          className={`px-3 py-1 text-sm rounded ${
            mode === 'markdown' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
          }`}
          title="Markdown Editor"
        >
          <FileText className="h-4 w-4 inline mr-1" />
          Markdown
        </button>
        <button
          onClick={() => handleModeChange('html')}
          className={`px-3 py-1 text-sm rounded ${
            mode === 'html' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
          }`}
          title="HTML Editor"
        >
          <Code className="h-4 w-4 inline mr-1" />
          HTML
        </button>
      </div>

      {/* Formatting Tools */}
      {mode === 'wysiwyg' && (
        <>
          <button
            onClick={() => document.execCommand('bold')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Bold"
          >
            <Bold className="h-4 w-4" />
          </button>
          <button
            onClick={() => document.execCommand('italic')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Italic"
          >
            <Italic className="h-4 w-4" />
          </button>
          <button
            onClick={() => document.execCommand('underline')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Underline"
          >
            <Underline className="h-4 w-4" />
          </button>
          
          <div className="border-l border-gray-300 h-6 mx-2"></div>
          
          <button
            onClick={() => document.execCommand('formatBlock', false, 'h1')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Heading 1"
          >
            <Heading1 className="h-4 w-4" />
          </button>
          <button
            onClick={() => document.execCommand('formatBlock', false, 'h2')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Heading 2"
          >
            <Heading2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => document.execCommand('formatBlock', false, 'h3')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Heading 3"
          >
            <Heading3 className="h-4 w-4" />
          </button>

          <div className="border-l border-gray-300 h-6 mx-2"></div>

          <button
            onClick={() => document.execCommand('insertUnorderedList')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Bullet List"
          >
            <List className="h-4 w-4" />
          </button>
          <button
            onClick={() => document.execCommand('insertOrderedList')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Numbered List"
          >
            <ListOrdered className="h-4 w-4" />
          </button>
          <button
            onClick={() => document.execCommand('formatBlock', false, 'blockquote')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Quote"
          >
            <Quote className="h-4 w-4" />
          </button>

          <div className="border-l border-gray-300 h-6 mx-2"></div>

          <button
            onClick={() => {
              const url = prompt('Enter URL:');
              if (url) document.execCommand('createLink', false, url);
            }}
            className="p-2 hover:bg-gray-200 rounded"
            title="Insert Link"
          >
            <Link className="h-4 w-4" />
          </button>
          <button
            onClick={() => {
              const src = prompt('Enter image URL:');
              if (src) document.execCommand('insertImage', false, src);
            }}
            className="p-2 hover:bg-gray-200 rounded"
            title="Insert Image"
          >
            <Image className="h-4 w-4" />
          </button>

          <div className="border-l border-gray-300 h-6 mx-2"></div>

          <button
            onClick={() => document.execCommand('justifyLeft')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Align Left"
          >
            <AlignLeft className="h-4 w-4" />
          </button>
          <button
            onClick={() => document.execCommand('justifyCenter')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Align Center"
          >
            <AlignCenter className="h-4 w-4" />
          </button>
          <button
            onClick={() => document.execCommand('justifyRight')}
            className="p-2 hover:bg-gray-200 rounded"
            title="Align Right"
          >
            <AlignRight className="h-4 w-4" />
          </button>
        </>
      )}

      {/* AI Enhancement */}
      <div className="ml-auto flex items-center space-x-2">
        <button
          onClick={processWithAI}
          disabled={processing}
          className="flex items-center px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 text-sm"
        >
          {processing ? (
            <>
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-2"></div>
              Processing...
            </>
          ) : (
            <>
              <Sparkles className="h-3 w-3 mr-1" />
              AI Enhance
            </>
          )}
        </button>
      </div>
    </div>
  );

  const renderEditor = () => {
    if (mode === 'wysiwyg') {
      return (
        <div
          ref={editorRef}
          contentEditable={isEditing}
          className="w-full min-h-96 p-4 border-0 outline-none prose prose-gray max-w-none"
          style={{
            minHeight: '400px',
            maxHeight: '600px',
            overflowY: 'auto'
          }}
          dangerouslySetInnerHTML={{ __html: content }}
          onInput={(e) => setContent(e.target.innerHTML)}
        />
      );
    } else {
      return (
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full h-96 p-4 border-0 outline-none font-mono text-sm resize-none"
          style={{ minHeight: '400px' }}
          readOnly={!isEditing}
          placeholder={
            mode === 'markdown'
              ? 'Enter your article content in Markdown format...'
              : 'Enter your article content in HTML format...'
          }
        />
      );
    }
  };

  const renderPreview = () => {
    let previewContent = content;
    
    if (mode === 'markdown') {
      previewContent = marked(content);
    }
    
    // Enhanced image rendering
    previewContent = previewContent.replace(
      /<img([^>]*?)src="(data:image[^"]*)"([^>]*?)>/g,
      (match, before, src, after) => {
        const altMatch = match.match(/alt="([^"]*)"/);
        const alt = altMatch ? altMatch[1] : 'Media content';
        
        return `
          <div class="media-container" style="margin: 2rem 0; text-align: center;">
            <figure style="margin: 0; padding: 1rem; background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
              <img 
                src="${src}" 
                alt="${alt}"
                style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.1);"
              />
              <figcaption style="margin-top: 1rem; font-size: 0.875rem; color: #475569; font-weight: 500;">
                ${alt}
              </figcaption>
            </figure>
          </div>
        `;
      }
    );

    return (
      <div 
        className="prose prose-gray max-w-none p-4"
        dangerouslySetInnerHTML={{ __html: previewContent }}
        style={{ minHeight: '400px' }}
      />
    );
  };

  if (isEditing) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {/* Editor Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <button
              onClick={onBack}
              className="flex items-center p-2 hover:bg-gray-100 rounded-lg"
              title="Back to Content Library"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600" />
            </button>
            <Edit className="h-5 w-5 text-blue-600" />
            <div>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="text-lg font-semibold text-gray-900 border-none bg-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2"
                placeholder="Article title..."
              />
              {processedWithAI && (
                <div className="flex items-center space-x-1 text-green-600 text-sm">
                  <Sparkles className="h-4 w-4" />
                  <span>AI Enhanced</span>
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onSave({ ...article, content, title })}
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
        </div>

        {/* Toolbar */}
        {showToolbar && renderToolbar()}

        {/* Editor Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-0 border-t border-gray-200">
          {/* Editor */}
          <div className="border-r border-gray-200">
            <div className="p-2 bg-gray-50 border-b border-gray-200 text-sm font-medium text-gray-700">
              Editor ({mode.toUpperCase()})
            </div>
            {renderEditor()}
          </div>
          
          {/* Preview */}
          <div>
            <div className="p-2 bg-gray-50 border-b border-gray-200 text-sm font-medium text-gray-700">
              Live Preview
            </div>
            {renderPreview()}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Viewer Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="flex items-center p-2 hover:bg-gray-100 rounded-lg"
            title="Back to Content Library"
          >
            <ArrowLeft className="h-5 w-5 text-gray-600" />
          </button>
          <Eye className="h-5 w-5 text-green-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Updated: {new Date(article?.updated_at || Date.now()).toLocaleDateString()}</span>
              {article?.media_processed && (
                <div className="flex items-center space-x-1 text-purple-600">
                  <Brain className="h-3 w-3" />
                  <span>AI Enhanced</span>
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={processWithAI}
            disabled={processing}
            className="flex items-center px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 text-sm"
          >
            {processing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Enhancing...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                AI Enhance
              </>
            )}
          </button>
          <button
            onClick={onEdit}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </button>
        </div>
      </div>

      {/* Article Content */}
      <div className="p-6">
        {renderPreview()}
      </div>

      {/* Media Statistics */}
      {article?.media_count > 0 && (
        <div className="px-6 pb-4">
          <div className="flex items-center space-x-4 text-sm text-gray-600 bg-blue-50 rounded-lg p-3">
            <div className="flex items-center space-x-1">
              <Image className="h-4 w-4 text-blue-600" />
              <span>{article.media_count} media items</span>
            </div>
            {article.media_processed && (
              <div className="flex items-center space-x-1">
                <Brain className="h-4 w-4 text-purple-600" />
                <span>AI processed</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedMediaEditor;