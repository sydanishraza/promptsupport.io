import React, { useState, useEffect, useRef } from 'react';
import { Editor } from '@tinymce/tinymce-react';
import { motion } from 'framer-motion';
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
  ToggleLeft,
  ToggleRight,
  RefreshCw,
  Download,
  Copy,
  Share,
  Tag,
  User,
  Clock,
  Hash
} from 'lucide-react';
import { marked } from 'marked';
import TurndownService from 'turndown';

const TinyMCEEditor = ({ 
  article, 
  isEditing, 
  onEdit, 
  onSave, 
  onCancel, 
  onDelete,
  backendUrl 
}) => {
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState([]);
  const [status, setStatus] = useState('draft');
  const [viewMode, setViewMode] = useState('wysiwyg'); // 'wysiwyg', 'markdown', 'html'
  const [isProcessing, setIsProcessing] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);
  const [metadata, setMetadata] = useState({});
  const [editorReady, setEditorReady] = useState(false);
  
  const editorRef = useRef(null);
  const turndownService = new TurndownService();

  // Initialize content when article changes
  useEffect(() => {
    if (article) {
      setTitle(article.title || '');
      setContent(article.content || '');
      setTags(article.tags || []);
      setStatus(article.status || 'draft');
      setMetadata(article.metadata || {});
    }
  }, [article]);

  // TinyMCE configuration
  const editorConfig = {
    height: 600,
    menubar: true,
    plugins: [
      'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
      'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
      'insertdatetime', 'media', 'table', 'help', 'wordcount', 'codesample',
      'emoticons', 'template', 'paste', 'textcolor', 'colorpicker', 'textpattern'
    ],
    toolbar: [
      'undo redo | blocks | bold italic backcolor | alignleft aligncenter alignright alignjustify',
      'bullist numlist outdent indent | removeformat | help',
      'link image media table | codesample | fullscreen preview',
      'forecolor backcolor emoticons | searchreplace | code'
    ].join(' | '),
    content_style: `
      body { 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
        font-size: 14px; 
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
      }
      img { 
        max-width: 100%; 
        height: auto; 
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
      }
      blockquote {
        border-left: 4px solid #3b82f6;
        padding-left: 1rem;
        margin: 1rem 0;
        background: #f8fafc;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
      }
      pre {
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
      }
      table {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
      }
      th, td {
        border: 1px solid #e2e8f0;
        padding: 0.5rem;
        text-align: left;
      }
      th {
        background: #f8fafc;
        font-weight: 600;
      }
    `,
    paste_data_images: true,
    images_upload_handler: (blobInfo, success, failure) => {
      // Handle image uploads - convert to base64
      const reader = new FileReader();
      reader.onload = () => {
        success(reader.result);
      };
      reader.onerror = () => {
        failure('Image upload failed');
      };
      reader.readAsDataURL(blobInfo.blob());
    },
    setup: (editor) => {
      editor.on('init', () => {
        setEditorReady(true);
        console.log('TinyMCE editor initialized');
      });
    },
    // Custom formats for better content structure
    formats: {
      callout_info: {
        block: 'div',
        classes: 'callout callout-info',
        wrapper: true
      },
      callout_warning: {
        block: 'div', 
        classes: 'callout callout-warning',
        wrapper: true
      },
      callout_success: {
        block: 'div',
        classes: 'callout callout-success', 
        wrapper: true
      }
    }
  };

  // Convert markdown to HTML
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
      console.error('Markdown conversion error:', error);
      return markdown;
    }
  };

  // Convert HTML to markdown
  const htmlToMarkdown = (html) => {
    try {
      return turndownService.turndown(html);
    } catch (error) {
      console.error('HTML to markdown conversion error:', error);
      return html;
    }
  };

  // Handle view mode change
  const handleViewModeChange = (mode) => {
    if (!editorReady) return;

    const currentContent = editorRef.current?.getContent() || content;
    
    if (mode === 'markdown') {
      const markdownContent = htmlToMarkdown(currentContent);
      setContent(markdownContent);
    } else if (mode === 'html') {
      // Keep as HTML
      setContent(currentContent);
    } else if (mode === 'wysiwyg') {
      if (viewMode === 'markdown') {
        const htmlContent = markdownToHtml(content);
        setContent(htmlContent);
      }
    }
    
    setViewMode(mode);
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

  // Handle save
  const handleSave = async () => {
    try {
      const finalContent = viewMode === 'wysiwyg' 
        ? (editorRef.current?.getContent() || content)
        : content;

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

      {/* Content Area */}
      <div className="p-4 flex-1">
        {viewMode === 'wysiwyg' ? (
          <Editor
            ref={editorRef}
            apiKey="x09gf1395vrl61n0hbp843ynqsdo0kddcd3m58bjrilesxfl"
            value={content}
            init={editorConfig}
            onEditorChange={setContent}
            disabled={!isEditing}
          />
        ) : (
          <div className="space-y-4">
            {isEditing ? (
              <textarea
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
    </div>
  );
};

export default TinyMCEEditor;