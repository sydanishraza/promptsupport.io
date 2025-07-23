import React, { useState, useEffect } from 'react';
import { marked } from 'marked';
import { 
  Edit, 
  Eye, 
  Save, 
  X, 
  FileText,
  Image,
  Sparkles,
  Brain
} from 'lucide-react';

const MediaArticleViewer = ({ 
  article, 
  isEditing, 
  onEdit, 
  onSave, 
  onCancel,
  backendUrl 
}) => {
  const [content, setContent] = useState(article?.content || '');
  const [processing, setProcessing] = useState(false);
  const [processedWithAI, setProcessedWithAI] = useState(false);

  useEffect(() => {
    if (article?.content) {
      setContent(article.content);
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

  const renderHTML = (htmlContent) => {
    // Convert markdown to HTML if needed
    let html = htmlContent;
    
    if (htmlContent.includes('![') && htmlContent.includes('data:image')) {
      // Enhanced markdown to HTML conversion with proper image handling
      html = marked(htmlContent);
      
      // Add enhanced styling to images
      html = html.replace(
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
    }
    
    return { __html: html };
  };

  if (isEditing) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {/* Editor Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Edit className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Edit Article</h3>
            {processedWithAI && (
              <div className="flex items-center space-x-1 text-green-600 text-sm">
                <Sparkles className="h-4 w-4" />
                <span>AI Enhanced</span>
              </div>
            )}
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
                  Processing...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  AI Enhance
                </>
              )}
            </button>
            <button
              onClick={() => onSave(content)}
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

        {/* Editor Content */}
        <div className="p-4">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content (Markdown with embedded images supported)
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full h-96 p-4 border border-gray-300 rounded-lg font-mono text-sm resize-vertical"
              placeholder="Enter your article content in Markdown format..."
            />
          </div>
          
          {/* Preview */}
          <div className="border-t border-gray-200 pt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Live Preview:</h4>
            <div 
              className="prose prose-gray max-w-none p-4 bg-gray-50 rounded-lg border min-h-32"
              dangerouslySetInnerHTML={renderHTML(content)}
            />
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
          <Eye className="h-5 w-5 text-green-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{article?.title}</h3>
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
        <div 
          className="prose prose-gray prose-lg max-w-none"
          dangerouslySetInnerHTML={renderHTML(content)}
          style={{
            lineHeight: '1.7',
            fontSize: '16px',
          }}
        />
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

export default MediaArticleViewer;